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

from celery import shared_task

@shared_task(name="app.tasks.rag_tasks.process_document_embedding")
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
        # 🎯 HIERARCHICAL KNOWLEDGE INGESTION PIPELINE
        # =====================================================================
        try:
            print(f"🧠 Commencing Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # 1. Save temp file for PyMuPDF parser
            temp_pdf_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(raw_file_bytes)
            
            # 🟢 SAFE MEMORY FLUSH
            # Clear local byte variable without corrupting the DB object!
            import gc
            del raw_file_bytes
            gc.collect()
            
            # 🟢 2. THE FIX: Use the new Cost-Routing Smart Parser
            smart_pages = extract_smart_pages(temp_pdf_path)
            
            # 🟢 UPDATED: Reads directly from content_text in the dual-payload
            pages_dict = {p["page_num"]: p.get("content_text", "") for p in smart_pages}

            if not smart_pages:
                raise ValueError("Zero content extracted from document.")

            # 🟢 3. Pass the Smart Payloads (Images + Text) to the Dual-Engine AI
            saved_sections, chunk_suggestions = build_and_save_navigation_map(
                db=db, 
                document_id=doc.id, 
                workspace_id=doc.workspace_id,
                agent_id=doc.agent_id, 
                smart_pages=smart_pages  # 🟢 NEW: Passes the list of dicts directly
            )
            
            # 3. Setup AI & Vector DB
            chroma_client = get_chroma_client()
            
            # The original collection for raw text chunks
            collection = chroma_client.get_or_create_collection(
                name="rag_enterprise_vectors_v1", 
                metadata={"hnsw:space": "cosine"}
            )
            
            # 🟢 NEW: The lightweight collection for the Smart Router Index Cards
            nav_collection = chroma_client.get_or_create_collection(
                name="navigation_index_cards",
                metadata={"hnsw:space": "cosine"}
            )
            
            paid_api_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not paid_api_key:
                raise ValueError("CRITICAL: INTELLIGENCE_LAYER_API_KEY / GEMINI_API_KEY missing for embeddings.")
                
            ai_client = genai.Client(api_key=paid_api_key)
            chunk_engine = ChunkEngine(chunk_size=400, overlap=50)

            # 4. Process Sections (Extraction + Chunking)
            all_chunks_for_chroma = []
            
            for section in saved_sections:
                
                # ==========================================================
                # 🟢 1. EXTRACT TEXT FIRST
                # ==========================================================
                hint = section.chunking_strategy_hint or {}
                cleaned_text = hint.get("normalized_text")
                
                if cleaned_text and cleaned_text.strip():
                    section_text = cleaned_text
                else:
                    section_text = ""
                    for p in range(section.start_page, section.end_page + 1):
                        if p in pages_dict:
                            section_text += pages_dict[p] + "\n"
                            
                if not section_text.strip(): 
                    continue

                # ==========================================================
                # 🟢 2. Save the Index Card to the Navigation Vector DB
                # ==========================================================
                if section.semantic_summary and section.semantic_summary.strip():
                    try:
                        entities_str = ", ".join(section.key_entities) if section.key_entities else ""
                        dense_search_card = f"Title: {section.title} | Summary: {section.semantic_summary} | Keywords: {entities_str} | Data Snippet: {section_text[:500]}"
                        
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
                # 🟢 3. Section-Bound Chunking (Queueing for Bulk Processing)
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
                    chroma_id = f"vec_{uuid.uuid4().hex[:12]}"
                    encrypted_doc = encrypt_text_string(pt_content, doc.workspace_id)
                    
                    # Store in memory temporarily for the bulk API call
                    all_chunks_for_chroma.append({
                        "id": chroma_id,
                        "text": pt_content,
                        "encrypted_doc": encrypted_doc,
                        "metadata": {
                            "workspace_id": str(doc.workspace_id), 
                            "section_id": str(section.id), 
                            "document_id": str(doc.id)
                        }
                    })
                    
                    # Link Postgres hierarchy 
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
                    db.flush()  # 🟢 ADDED: Generates new_db_chunk.id required for the linked list pointer
                    
                    if last_chunk_db_id:
                        prev_chunk = db.query(DocumentChunk).filter(DocumentChunk.id == last_chunk_db_id).first()
                        if prev_chunk:
                            prev_chunk.next_chunk_id = new_db_chunk.id
                            
                    last_chunk_db_id = new_db_chunk.id

            # ==========================================================
            # 🟢 4. BULK VECTOR EMBEDDING & CHROMA INSERTION (10x FASTER)
            # ==========================================================
            BATCH_SIZE = 100
            for i in range(0, len(all_chunks_for_chroma), BATCH_SIZE):
                batch = all_chunks_for_chroma[i:i + BATCH_SIZE]
                
                batch_texts = [c["text"] for c in batch]
                batch_ids = [c["id"] for c in batch]
                batch_docs = [c["encrypted_doc"] for c in batch]
                batch_metas = [c["metadata"] for c in batch]
                
                try:
                    # ONE network call for 100 chunks!
                    vector_response = ai_client.models.embed_content(
                        model="models/gemini-embedding-001",
                        contents=batch_texts
                    )
                    
                    batch_embeddings = [emb.values for emb in vector_response.embeddings]
                    
                    collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        documents=batch_docs,
                        metadatas=batch_metas
                    )
                    
                    # 🟢 SAFE COMMIT: Commits the batch to Postgres securely
                    db.commit() 
                    
                    print(f"⚡ Batch processed and inserted {len(batch)} chunks lightning fast.")
                except Exception as e:
                    print(f"⚠️ Bulk vector generation/insertion failed for batch: {e}")

            # Cleanup
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)

            doc.status = "ready"
            db.commit()
            print(f"🚀 Success: Hierarchical ingestion complete for '{doc.filename}'.")
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