import os
import io
import uuid
from datetime import datetime
import chromadb
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
from app.services.pdf_parser import extract_document_structure
from app.services.navigation_service import build_and_save_navigation_map
from app.services.extraction_ai import run_section_knowledge_extraction
from app.services.chunk_engine import ChunkEngine
from app.models.new_arch import DocumentChunk, ExtractedEntity

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
        
        # 3. Extract Full Raw Text Content String with Ultimate OCR Fallback
        extracted_text = ""
        if doc.mime_type == "text/plain":
            extracted_text = raw_file_bytes.decode("utf-8", errors="ignore")
        elif doc.mime_type == "application/pdf":
            pdf_stream = io.BytesIO(raw_file_bytes)
            
            # Attempt 1: Standard pypdf extraction
            try:
                reader = PdfReader(pdf_stream)
                extracted_text = " ".join([page.extract_text() for page in reader.pages if page and page.extract_text()])
            except Exception as e:
                print(f"⚠️ pypdf extraction warning: {e}")

            # Attempt 2: Fallback to layout-aware extraction mode
            if not extracted_text.strip():
                print("🔄 Standard extraction yielded empty text. Trying layout-aware extraction mode...")
                try:
                    pdf_stream.seek(0)
                    reader = PdfReader(pdf_stream)
                    extracted_text = " ".join([page.extract_text(extraction_mode="layout") for page in reader.pages if page])
                except Exception as layout_err:
                    print(f"⚠️ Layout extraction warning: {layout_err}")

            # Attempt 3: pdfplumber table/grid parser
            if not extracted_text.strip():
                print("🔄 Layout extraction yielded empty text. Executing pdfplumber table/grid parser...")
                try:
                    pdf_stream.seek(0)
                    with pdfplumber.open(pdf_stream) as pdf:
                        plumber_text_parts = []
                        for page in pdf.pages:
                            txt = page.extract_text(layout=True)
                            if txt:
                                plumber_text_parts.append(txt)
                        extracted_text = " ".join(plumber_text_parts)
                except Exception as plumber_err:
                    print(f"⚠️ pdfplumber fallback warning: {plumber_err}")

            # Attempt 4: Ultimate OCR Fallback using PyTesseract & pdf2image for image-based PDFs
            if not extracted_text.strip():
                print("🔄 Text layers missing. Initializing PyTesseract OCR optical engine...")
                try:
                    from pdf2image import convert_from_bytes
                    import pytesseract

                    images = convert_from_bytes(raw_file_bytes)
                    ocr_text_parts = []
                    for img in images:
                        text_page = pytesseract.image_to_string(img)
                        if text_page:
                            ocr_text_parts.append(text_page)
                    extracted_text = " ".join(ocr_text_parts)
                    print(f"✨ OCR Success: Extracted {len(extracted_text)} characters via optical scanning.")
                except Exception as ocr_err:
                    print(f"❌ OCR fallback error: {ocr_err}")
            
        if not extracted_text.strip():
            raise ValueError("Zero human-readable text contents could be extracted even after OCR processing.")
        
        # =====================================================================
        # 🎯 HIERARCHICAL KNOWLEDGE INGESTION PIPELINE
        # =====================================================================
        try:
            print(f"🧠 Commencing Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # 1. Save temp file for PyMuPDF parser
            temp_pdf_path = f"/tmp/{uuid.uuid4().hex}.pdf"
            with open(temp_pdf_path, "wb") as f:
                f.write(raw_file_bytes)
            
            doc_obj = fitz.open(temp_pdf_path)
            doc_page_count = doc_obj.page_count
            
            # 2. Extract Structure and Build DB Navigation Map
            struct_data = extract_document_structure(temp_pdf_path)
            saved_sections = build_and_save_navigation_map(
                db=db, 
                document_id=doc.id, 
                workspace_id=doc.workspace_id,
                agent_id=doc.agent_id, 
                pymupdf_toc=struct_data.get("toc", []),
                doc_page_count=doc_page_count, 
                page_text_samples=None
            )
            
            # 3. Setup AI & Vector DB
            chroma_client = get_chroma_client()
            collection = chroma_client.get_or_create_collection(
                name="rag_enterprise_vectors_v1", 
                metadata={"hnsw:space": "cosine"}
            )
            
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            ai_client = genai.Client(api_key=gemini_api_key)
            chunk_engine = ChunkEngine(chunk_size=400, overlap=50)

            # 4. Process Sections (Extraction + Chunking)
            for section in saved_sections:
                section_text = ""
                for p in range(section.start_page - 1, section.end_page):
                    if p < doc_page_count:
                        section_text += doc_obj.load_page(p).get_text("text") + "\n"
                        
                if not section_text.strip(): 
                    continue

                # A. Extraction AI (Telemetry & Entities)
                extraction_data = run_section_knowledge_extraction(section.title, section_text, ai_client)
                for ent in extraction_data.entities:
                    db.add(ExtractedEntity(
                        document_id=doc.id, 
                        workspace_id=doc.workspace_id, 
                        agent_id=doc.agent_id,
                        name=ent.name, 
                        category=ent.category, 
                        description=ent.description
                    ))
                
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
                        vector_response = ai_client.models.embed_content(
                            model="text-embedding-004", 
                            contents=pt_content
                        )
                        raw_vector = vector_response.embeddings[0].values
                    except Exception as e: 
                        print(f"⚠️ Vector generation failed for a chunk: {e}")
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
                        telemetry_summary=extraction_data.telemetry_summary, 
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
            doc_obj.close()
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
            # Some models have an error_message field, wrapping safely
            if hasattr(doc, 'error_message'):
                doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure: {str(error)}")
        return False