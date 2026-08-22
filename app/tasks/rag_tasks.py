import os
import io
import uuid
from datetime import datetime
import chromadb
import time
from celery import Celery
from sqlalchemy.orm import Session
from pypdf import PdfReader
from google import genai  
import fitz  # PyMuPDF
import pdfplumber

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.models.user import User  
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string

# 🟢 NEW ARCHITECTURE IMPORTS
from app.services.navigation_service import build_and_save_navigation_map
from app.services.pdf_parser import extract_smart_pages
from app.services.chunk_engine import ChunkEngine
from app.models.new_arch import DocumentChunk

# Initialize Celery app matching your system's setup instance configuration
CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
if not CELERY_BROKER:
    raise ValueError("CRITICAL CONFIGURATION TIMEOUT: CELERY_BROKER_URL or REDIS_URL environment variable is missing on this worker node context.")

celery_app = Celery("rag_tasks", broker=CELERY_BROKER)


def get_chroma_client():
    """Initializes the Chroma client securely using environment parameters."""
    CHROMA_HOST = os.getenv("CHROMA_HOST")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    if not CHROMA_HOST:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: CHROMA_HOST environment variable mapping is missing.")
    CHROMA_HOST = str(CHROMA_HOST).strip().rstrip("/")
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )

@celery_app.task(name="app.tasks.rag_tasks.process_document_embedding")
def process_document_embedding(document_id: str):
    """
    Celery Background Task Worker: Restructured for Hierarchical & Agentic RAG.
    Creates navigation maps, extracts domain entities, and creates section-bound chunks.
    """
    db: Session = next(get_db())
    doc = None
    
    try:
        # 1. Fetch the target file tracking record from PostgreSQL
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if not doc:
            print(f"❌ Ingestion aborted: Document UUID '{document_id}' not found.")
            return False
            
        uploader_email = "Unknown System Operator"
        if doc.uploaded_by:
            user_row = db.query(User).filter(User.id == doc.uploaded_by).first()
            if user_row and user_row.email:
                uploader_email = str(user_row.email).strip()

        # 2. Decrypt the raw binary bytes payload pulled from PostgreSQL
        raw_file_bytes = decrypt_file_bytes(
            ciphertext=doc.encrypted_file_data,
            iv=doc.encryption_iv,
            workspace_id=doc.workspace_id
        )

        # =====================================================================
        # 🎯 HIERARCHICAL KNOWLEDGE INGESTION PIPELINE (UNIFIED MARKDOWN)
        # =====================================================================
        try:
            print(f"🧠 Commencing Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # 1. Save temp file for PyMuPDF parser
            temp_pdf_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(raw_file_bytes)
            
            # 🟢 2. UNIFIED ENGINE: Extract Pure Markdown
            smart_pages = extract_smart_pages(temp_pdf_path)
            
            # 🟢 THE FIX: BRING BACK THE PAGES DICTIONARY! We need the RAW Markdown!
            pages_dict = {p["page_num"]: p.get("content_text", "") for p in smart_pages}

            if not smart_pages:
                raise ValueError("Zero content extracted from document.")

            # 🟢 3. Pass the Markdown Payloads to the Unified AI
            saved_sections, chunk_suggestions = build_and_save_navigation_map(
                db=db, 
                document_id=doc.id, 
                workspace_id=doc.workspace_id,
                agent_id=doc.agent_id, 
                smart_pages=smart_pages
            )
            
            # 4. Setup AI & Vector DB
            chroma_client = get_chroma_client()
            
            collection = chroma_client.get_or_create_collection(
                name="rag_enterprise_vectors_v1", 
                metadata={"hnsw:space": "cosine"}
            )
            
            nav_collection = chroma_client.get_or_create_collection(
                name="navigation_index_cards",
                metadata={"hnsw:space": "cosine"}
            )
            
            paid_api_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not paid_api_key:
                raise ValueError("CRITICAL: INTELLIGENCE_LAYER_API_KEY / GEMINI_API_KEY missing for embeddings.")
                
            ai_client = genai.Client(api_key=paid_api_key)
            chunk_engine = ChunkEngine(chunk_size=400, overlap=50)

            # 5. Process Sections (Extraction + Chunking)
            for section in saved_sections:
                
                # ==========================================================
                # 🟢 A. GET THE TEXT (The Fix: Use the RAW Markdown directly!)
                # ==========================================================
                hint = section.chunking_strategy_hint or {}
                
                # Rebuild the exact Markdown using the start and end pages
                section_text = ""
                for p in range(section.start_page, section.end_page + 1):
                    section_text += pages_dict.get(p, "") + "\n"
                
                if not section_text or not section_text.strip(): 
                    print(f"⚠️ Warning: Section '{section.title}' has no text. Skipping.")
                    continue

                # ==========================================================
                # 🟢 B. Save the Index Card to the Navigation Vector DB
                # ==========================================================
                if section.semantic_summary and section.semantic_summary.strip():
                    try:
                        import json
                        
                        # 🟢 THE FIX: The Smart Router expects strict JSON formatting!
                        index_card_dict = {
                            "section_id": str(section.id),
                            "path": str(section.parent_path) if section.parent_path else str(section.title),
                            "title": str(section.title),
                            "type": str(section.content_type),
                            "summary": str(section.semantic_summary),
                            "entities": section.key_entities if section.key_entities else [],
                            "data_preview": section_text[:3000]
                        }
                        
                        dense_search_card = json.dumps(index_card_dict)
                        
                        summary_vector_resp = ai_client.models.embed_content(
                            model="models/gemini-embedding-001", 
                            contents=dense_search_card
                        )
                        nav_collection.add(
                            ids=[str(section.id)],
                            embeddings=[summary_vector_resp.embeddings[0].values],
                            documents=[dense_search_card], 
                            metadatas=[{
                                "workspace_id": str(doc.workspace_id),
                                "document_id": str(doc.id)
                            }]
                        )
                    except Exception as e:
                        print(f"⚠️ Navigation vector generation failed for section {section.id}: {e}")
                
                # ==========================================================
                # 🟢 C. Section-Bound Chunking
                # ==========================================================
                section_chunks = chunk_engine.execute_section_chunking(
                    section_text=section_text, 
                    section_id=section.id, 
                    document_id=doc.id, 
                    workspace_id=doc.workspace_id, 
                    agent_id=doc.agent_id,
                    strategy_hint=hint
                )
                
                last_chunk_db_id = None
                for chunk_payload in section_chunks:
                    pt_content = chunk_payload["text"]
                    
                    try:
                        vector_response = ai_client.models.embed_content(
                            model="models/gemini-embedding-001", 
                            contents=pt_content
                        )
                        raw_vector = vector_response.embeddings[0].values
                    except Exception as e: 
                        print(f"⚠️ Vector generation failed for chunk: {e}")
                        continue
                        
                    chroma_id = f"vec_{uuid.uuid4().hex[:12]}"
                    encrypted_doc = encrypt_text_string(pt_content, doc.workspace_id)
                    
                    collection.add(
                        ids=[chroma_id], 
                        embeddings=[raw_vector], 
                        documents=[encrypted_doc],
                        metadatas=[{
                            "workspace_id": str(doc.workspace_id), 
                            "section_id": str(section.id), 
                            "document_id": str(doc.id)
                        }]
                    )
                    
                    new_db_chunk = DocumentChunk(
                        document_id=doc.id, 
                        section_id=section.id, 
                        workspace_id=doc.workspace_id,
                        agent_id=doc.agent_id,
                        chroma_vector_id=chroma_id, 
                        sequence_number=chunk_payload["sequence_number"],
                        telemetry_summary=chunk_payload.get("telemetry_summary", ""),
                        prev_chunk_id=last_chunk_db_id
                    )
                    
                    db.add(new_db_chunk)
                    db.flush()
                    
                    if last_chunk_db_id:
                        prev_chunk = db.query(DocumentChunk).filter(DocumentChunk.id == last_chunk_db_id).first()
                        if prev_chunk:
                            prev_chunk.next_chunk_id = new_db_chunk.id
                            
                    last_chunk_db_id = new_db_chunk.id

            # Cleanup
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            doc.status = "ready"
            db.commit()
            print(f"🚀 Success: Unified hierarchical ingestion complete for '{doc.filename}'.")
            return True
            
        except Exception as pipeline_err:
            db.rollback()
            raise ValueError(f"Knowledge Ingestion Pipeline Error: {str(pipeline_err)}")

    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            if hasattr(doc, 'error_message'):
                doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure: {str(error)}")
        return False