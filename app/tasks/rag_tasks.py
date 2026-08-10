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
from app.services.pdf_parser import process_pdf_for_navigation, extract_raw_pages, build_pdf_batches
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


def chunk_text_by_page(text: str, page_num: int, source_filename: str, chunk_size: int = 250, chunk_overlap: int = 40) -> list[dict]:
    """Splits plain text strings extracted from a specific page partition into overlapping paragraph blocks."""
    if not text or not str(text).strip():
        return []
    words = text.split()
    chunks_with_meta = []
    stride = chunk_size - chunk_overlap
    if stride <= 0:
        stride = chunk_size
    for i in range(0, len(words), stride):
        chunk_text_raw = " ".join(words[i:i + chunk_size])
        if chunk_text_raw.strip():
            chunks_with_meta.append({
                "text": chunk_text_raw,
                "page_number": page_num,
                "source_file": source_filename
            })
    return chunks_with_meta


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
        # 🎯 HIERARCHICAL KNOWLEDGE INGESTION PIPELINE
        # =====================================================================
        try:
            print(f"🧠 Commencing Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # 1. Save temp file for PyMuPDF parser
            temp_pdf_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(raw_file_bytes)
            
            # Use the parser to get both the raw text (with OCR) and the batches
            pages_dict = extract_raw_pages(temp_pdf_path)
            pdf_batches = build_pdf_batches(pages_dict, pages_per_batch=15)

            if not pdf_batches:
                raise ValueError("Zero human-readable text contents extracted.")

            saved_sections, chunk_suggestions = build_and_save_navigation_map(
            db=db, 
            document_id=doc.id, 
            workspace_id=doc.workspace_id,
            agent_id=doc.agent_id, 
            pdf_batches=pdf_batches
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
            for section in saved_sections:
                
                # ==========================================================
                # 🟢 OPTION 3: Save the Index Card to the Navigation Vector DB
                # ==========================================================
                if section.semantic_summary and section.semantic_summary.strip():
                    try:
                        summary_vector_resp = ai_client.models.embed_content(
                            model="models/gemini-embedding-001", 
                            contents=section.semantic_summary
                        )
                        nav_collection.add(
                            ids=[str(section.id)], # Map directly to the DocumentSection UUID
                            embeddings=[summary_vector_resp.embeddings[0].values],
                            documents=[section.semantic_summary],
                            metadatas=[{
                                "workspace_id": str(doc.workspace_id),
                                "document_id": str(doc.id)
                            }]
                        )
                    except Exception as e:
                        print(f"⚠️ Navigation vector generation failed for section {section.id}: {e}")
                # ==========================================================
                
                # 1. Pull raw OCR/extracted text natively for this section
                section_text = ""
                for p in range(section.start_page, section.end_page + 1):
                    if p in pages_dict:
                        section_text += pages_dict[p] + "\n"
                        
                if not section_text.strip(): 
                    continue

                # ==========================================================
                # 🟢 HYBRID UNIVERSAL DATA CLEANER (pdfplumber + Gemini AI)
                # ==========================================================
                if section.content_type in ["master_scheme_table", "table_section"]:
                    print(f"🧹 Table section detected: '{section.title}'")
                    
                    grid_text_extracted = ""
                    # 📐 Attempt physical grid detection via pdfplumber
                    try:
                        with pdfplumber.open(temp_pdf_path) as pdf:
                            for page_num in range(section.start_page, section.end_page + 1):
                                if 0 <= page_num - 1 < len(pdf.pages):
                                    page = pdf.pages[page_num - 1]
                                    tables = page.extract_tables()
                                    for tbl in tables:
                                        for row in tbl:
                                            clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                                            if any(clean_row):
                                                grid_text_extracted += " | ".join(clean_row) + "\n"
                    except Exception as plumber_err:
                        print(f"⚠️ pdfplumber grid extraction skipped: {plumber_err}")

                    # Use pdfplumber grid output if found; fallback to raw page text
                    raw_table_context = grid_text_extracted.strip() if grid_text_extracted.strip() else section_text.strip()

                    # 🤖 Pass table structure to Universal AI Normalizer
                    clean_prompt = f"""
                    You are an expert Data Structuring AI. Analyze this raw text extracted from a PDF table.
                    PDF tables often use visual groupings (e.g., merged cells) to apply one value (like a supervisor, category, or department) to multiple rows, leaving the surrounding cells blank.

                    Your task is to reconstruct the logical rows of this table universally:
                    1. DEDUCE THE LAYOUT: Look at the blank spaces and content sequence. Figure out if shared values are top-aligned, bottom-aligned, or center-aligned within their respective groups.
                    2. FILL THE BLANKS: Physically rewrite the text so EVERY SINGLE row explicitly includes all its assigned data (e.g., attach the supervisor name explicitly to every student row in that group).
                    3. IGNORE ARTIFACTS: Seamlessly bridge groups that are interrupted by page headers or footers.
                    4. NO FORMATTING: Do not add markdown table delimiters or explanations. Return only the explicit, clean text list.
                    5. STANDARD TABLES: If every row is already complete with no implied groupings, return the text as-is.

                    RAW TABLE CONTENT:
                    {raw_table_context}
                    """
                    try:
                        clean_resp = ai_client.models.generate_content(
                            model="gemini-3.1-flash-lite", 
                            contents=clean_prompt
                        )
                        if clean_resp and clean_resp.text:
                            section_text = clean_resp.text.strip()
                            print(f"✨ Universal table normalization successful for section '{section.title}'.")
                    except Exception as ai_err:
                        print(f"⚠️ AI Data Normalization failed, using default text: {ai_err}")
                else:
                    print(f"⏩ Standard narrative section detected ('{section.title}'). Skipping table normalizer.")
                # ==========================================================
                # ==========================================================
                # ==========================================================
                
                # B. Section-Bound Chunking
                section_chunks = chunk_engine.execute_section_chunking(
                    section_text=section_text, 
                    section_id=section.id, 
                    document_id=doc.id, 
                    workspace_id=doc.workspace_id, 
                    agent_id=doc.agent_id
                )
                
                last_chunk_db_id = None
                for chunk_payload in section_chunks:
                    pt_content = chunk_payload["text"]
                    
                    try:
                        # 🟢 Updated to standard text-embedding-004 model
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