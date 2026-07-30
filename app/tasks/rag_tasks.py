import os
import io
import uuid
from datetime import datetime
import chromadb
from celery import Celery
from sqlalchemy.orm import Session
from pypdf import PdfReader
from google import genai

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.models.user import User  
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string

# 🟢 IMPORT NEW V2 ARCHITECTURE COMPONENTS
from app.services.document_parser import DocumentParserService
from app.services.extraction_service import get_intelligence_client, run_phase_1_knowledge_extraction
from app.services.navigation_ai import generate_navigation_map
from app.services.plan_validator import validate_and_sanitize_ingestion_plan
from app.services.vector_sync import ChromaVectorSyncService
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


@celery_app.task(name="app.tasks.rag_tasks.process_document_embedding")
def process_document_embedding(document_id: str):
    """
    Celery Background Task Worker: Upgraded to V2 Architecture. Uses local Python 
    DocumentParserService for structural signals, Navigation AI for topic mapping, 
    Extraction AI for metadata, and ChromaVectorSyncService for secure indexing.
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
        
        # 3. Extract Full Raw Text Content String with Ultimate OCR Fallback (Retaining all robust extraction layers)
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
        # 🎯 V2 ARCHITECTURE INGESTION PIPELINE
        # =====================================================================
        try:
            print(f"🧠 Commencing V2 Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            # --- STEP A: LOCAL PYTHON DOCUMENT PARSER ---
            parser_service = DocumentParserService(file_bytes=raw_file_bytes, filename=doc.filename)
            parsed_bundle = parser_service.parse_document()
            
            navigation_payload = parsed_bundle["navigation_payload"]
            extraction_payload = parsed_bundle["extraction_payload"]

            intelligence_client = get_intelligence_client()
            
            # --- STEP B: EXTRACTION AI ---
            print(f"📡 Generating Knowledge Ingestion Plan for: {doc.filename}")
            raw_ingestion_plan = run_phase_1_knowledge_extraction(extraction_payload, intelligence_client)
            validated_plan = validate_and_sanitize_ingestion_plan(raw_ingestion_plan)

            # --- STEP C: NAVIGATION AI ---
            print(f"🧭 Generating Navigation Topic Map for: {doc.filename}")
            navigation_map = generate_navigation_map(navigation_payload)

            # Parse Metadata & Relationships securely (preserving old robust parsing logic)
            parsed_metadata = []
            for item in validated_plan.metadata:
                if ":" in item:
                    k, v = item.split(":", 1)
                    parsed_metadata.append({"key": k.strip(), "value": v.strip()})
                else:
                    parsed_metadata.append({"key": "Metadata", "value": item.strip()})

            parsed_relationships = []
            for item in validated_plan.relationships:
                parts = [p.strip() for p in item.split("|")]
                if len(parts) >= 4:
                    try:
                        strength_val = float(parts[3])
                    except ValueError:
                        strength_val = 0.9
                    parsed_relationships.append({
                        "chain": parts[0],
                        "relation": parts[1],
                        "target": parts[2],
                        "strength": strength_val
                    })
                elif len(parts) == 3:
                    parsed_relationships.append({
                        "chain": parts[0],
                        "relation": parts[1],
                        "target": parts[2],
                        "strength": 0.9
                    })
                else:
                    parsed_relationships.append({"chain": item.strip(), "relation": "relates_to", "target": "Context", "strength": 0.85})

            # Save plan metadata directly to PostgreSQL (keeping lean architecture table properties)
            doc.document_type = validated_plan.document_type
            doc.document_purpose = validated_plan.document_purpose
            doc.planner_summary = validated_plan.summary
            doc.knowledge_schema_version = 2
            doc.approved = True

            doc.knowledge_metadata = {
                "document_profile": {
                    "document_type": validated_plan.document_type,
                    "structure": validated_plan.structure,
                    "document_purpose": validated_plan.document_purpose,
                    "summary": validated_plan.summary
                },
                "document_structure": {
                    "has_tables": validated_plan.has_tables,
                    "has_headings": validated_plan.has_headings,
                    "is_hierarchical": validated_plan.is_hierarchical,
                    "contains_policies": validated_plan.contains_policies,
                    "contains_procedures": validated_plan.contains_procedures,
                    "contains_questions": validated_plan.contains_questions
                },
                "dynamic_metadata": parsed_metadata,
                "relationships": parsed_relationships,
                "chunking_plan": {
                    "strategy": validated_plan.chunk_strategy,
                    "chunk_size": validated_plan.chunk_size,
                    "overlap": validated_plan.overlap,
                    "reasoning": validated_plan.chunk_reasoning
                },
                "questions_this_document_can_answer": validated_plan.questions_this_document_can_answer,
                "confidence": {
                    "metadata_confidence": validated_plan.metadata_confidence,
                    "chunk_strategy_confidence": validated_plan.chunk_strategy_confidence
                }
            }
            db.commit()

            # --- STEP D: VECTOR SYNC SERVICE (Bridges ChunkEngine, Navigation AI, and ChromaDB securely) ---
            print(f"🧬 Executing ChromaVectorSyncService for {doc.filename}...")
            
            chroma_client = get_chroma_client()
            collection = chroma_client.get_or_create_collection(
                name="rag_enterprise_vectors_v1",
                metadata={"hnsw:space": "cosine"}
            )
            
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if not gemini_api_key:
                raise ValueError("CRITICAL INITIALIZATION ERROR: GEMINI_API_KEY is missing.")
            ai_client = genai.Client(api_key=gemini_api_key)

            vector_sync_service = ChromaVectorSyncService(
                chroma_collection=collection,
                embedding_client=ai_client
            )

            stored_chunk_ids = vector_sync_service.process_and_sync_chunks(
                document_id=str(doc.id),
                workspace_id=str(doc.workspace_id),
                filename=doc.filename,
                full_text=extracted_text,
                ingestion_plan=validated_plan,
                navigation_map=navigation_map
            )

            print(f"🚀 Success: Cloud server batched ingestion complete for '{doc.filename}'. Loaded {len(stored_chunk_ids)} chunks safely into ChromaDB.")

        except Exception as pipeline_err:
            db.rollback()
            error_str = f"Knowledge Ingestion Pipeline Error: {str(pipeline_err)}"
            print(f"❌ Pipeline rollback triggered: {error_str}")
            raise ValueError(error_str)
        # =====================================================================
            
        doc.status = "ready"
        db.commit()
        return True
        
    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure: {str(error)}")
        return False