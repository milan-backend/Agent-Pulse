import os
import io
import uuid
from datetime import datetime
import chromadb
from celery import Celery
from sqlalchemy.orm import Session
from pypdf import PdfReader
from google import genai  # 🎯 Official Google GenAI SDK interface

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.models.user import User  
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string
from app.services.smart_sampler import analyze_pdf_structure, select_intelligent_pages

# 🟢 UPDATED NEW INGESTION PIPELINE COMPONENTS
from app.services.navigation_service import NavigationService
from app.services.chunk_engine import ChunkEngineService
from app.services.extraction_service import ExtractionAI
import pdfplumber

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
    Celery Background Task Worker: Restructured to pull high-density operational 
    questions at Document-Level for absolute retrieval planner matching.
    """
    db: Session = next(get_db())
    doc = None
    
    try:
        # 1. Fetch the target file tracking record from PostgreSQL[cite: 5]
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if not doc:
            print(f"❌ Ingestion aborted: Document UUID '{document_id}' not found.")
            return False
            
        uploader_email = "Unknown System Operator"
        if doc.uploaded_by:
            user_row = db.query(User).filter(User.id == doc.uploaded_by).first()
            if user_row and user_row.email:
                uploader_email = str(user_row.email).strip()

        # 2. Decrypt the raw binary bytes payload pulled from PostgreSQL[cite: 5]
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
                    import pdfplumber
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
        # 🎯 AGENTPULSE V2 NEW ARCHITECTURE PIPELINE INTEGRATION
        # =====================================================================
        try:
            print(f"🧠 Commencing V2 Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # --- STEP 1: NAVIGATION SERVICE TREE BUILD ---
            print(f"🧭 Building hierarchical navigation tree for: {doc.filename}")
            nav_service = NavigationService(db, doc.id, doc.workspace_id)
            node_count = nav_service.build_navigation_tree()

            # --- STEP 2: CHUNK ENGINE SERVICE ---
            print(f"🧬 Executing Chunk Engine Service...")
            chunk_engine = ChunkEngineService(db, doc.id, doc.workspace_id)
            chunk_count = chunk_engine.process_document_chunks(extracted_text, page_number=1)

            # --- STEP 3: EXTRACTION AI KNOWLEDGE ENRICHMENT ---
            print(f"✨ Executing ExtractionAI Knowledge Enrichment...")
            extraction_ai = ExtractionAI(db, doc.id, doc.workspace_id)
            extraction_ai.process_enrichment()

            doc.status = "ready"
            doc.knowledge_schema_version = 2
            doc.approved = True
            db.commit()

            print(f"🟢 V2 Pipeline complete. Created {node_count} navigation nodes and {chunk_count} secure chunks.")

        except Exception as pipeline_err:
            db.rollback()
            error_str = f"AgentPulse V2 Pipeline Error: {str(pipeline_err)}"
            print(f"❌ Pipeline rollback triggered: {error_str}")
            raise ValueError(error_str)
        # =====================================================================

        # 4. Initialize Cloud-Native Vector Engine Connection Dynamic Link[cite: 5]
        chroma_client = get_chroma_client()
        collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("CRITICAL INITIALIZATION ERROR: GEMINI_API_KEY is missing.")
            
        ai_client = genai.Client(api_key=gemini_api_key)
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        current_timestamp_iso = datetime.utcnow().strftime("%Y-%m-%d")

        # Fetch stored chunks from database to sync with ChromaDB
        from app.models.chunks.chunk import Chunk
        stored_chunks = db.query(Chunk).filter(Chunk.document_id == doc.id).all()

        # 5. Process each stored chunk securely
        for index, chunk_record in enumerate(stored_chunks):
            raw_content = chunk_record.encrypted_content
            if isinstance(raw_content, bytes):
                plain_text_content = raw_content.decode("utf-8", errors="ignore")
            else:
                plain_text_content = str(raw_content)

            if not plain_text_content.strip():
                continue
                
            chunk_id = str(chunk_record.id)
            raw_vector_array = None
            
            for model_name in ["text-embedding-004", "gemini-embedding-001"]:
                try:
                    vector_response = ai_client.models.embed_content(
                        model=model_name,
                        contents=plain_text_content
                    )
                    candidate = vector_response.embeddings[0].values
                    import math
                    if candidate and isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                        if not any(math.isnan(x) for x in candidate if isinstance(x, (int, float))):
                            raw_vector_array = candidate
                            break
                except Exception:
                    continue

            if not raw_vector_array:
                print(f"⚠️ Warning: Skipping chunk {index} due to invalid or null embedding response.")
                continue

            embeddings.append(raw_vector_array)
            documents.append(chunk_record.encrypted_content) 
            
            ids.append(chunk_id)
            metadatas.append({
                "document_id": str(doc.id),
                "workspace_id": str(doc.workspace_id),
                "source_file": doc.filename,
                "page_number": 1
            })
            
        # 🚀 BATCHED INSERTION LOOP TO PREVENT DATABASE & VECTOR MEMORY OVERLOAD
        BATCH_SIZE = 50
        if ids:
            for i in range(0, len(ids), BATCH_SIZE):
                batch_ids = ids[i:i + BATCH_SIZE]
                batch_embeddings = embeddings[i:i + BATCH_SIZE]
                batch_documents = documents[i:i + BATCH_SIZE]
                batch_metadatas = metadatas[i:i + BATCH_SIZE]
                
                collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_documents,
                    metadatas=batch_metadatas
                )
                # Incremental commit to keep connection sessions healthy and light
                db.commit()
            
        doc.status = "ready"
        db.commit()
        print(f"🚀 Success: Cloud server batched ingestion complete for '{doc.filename}'. Loaded {len(ids)} chunks safely.")
        return True
        
    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure: {str(error)}")
        return False