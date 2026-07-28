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

# 🟢 IMPORT NEW INGESTION PIPELINE COMPONENTS (Phase 1 & Phase 2)
from app.services.extraction_service import ExtractionService, get_intelligence_client
from app.services.chunk_engine import ChunkEngine
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
    questions at Document-Level (Phase A) for absolute retrieval planner matching.
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

            # 🟢 Attempt 4: Ultimate OCR Fallback using PyTesseract & pdf2image for image-based PDFs
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
        # 🎯 AGENTPULSE V2 HIERARCHICAL NAVIGATION INGESTION PIPELINE
        # =====================================================================
        try:
            print(f"🧠 Commencing V2 Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            
            intelligence_client = get_intelligence_client()
            source_filename = doc.filename

            # --- STEP 1: DOCUMENT ANALYZER (Pure Python - Component 1) ---
            print(f"📊 Analyzing document structure page-by-page for: {source_filename}")
            from app.services.document_analyzer import DocumentAnalyzer
            analyzer = DocumentAnalyzer()
            analyzed_pages = analyzer.analyze_document(extracted_text, source_filename)

            # --- STEP 2: TOPIC BOUNDARY DETECTOR (Pure Python - Component 2) ---
            from app.services.boundary_detector import TopicBoundaryDetector
            boundary_detector = TopicBoundaryDetector()
            detected_topics = boundary_detector.detect_boundaries(analyzed_pages)

            # --- STEP 3: DOCUMENT DNA GENERATOR (Pure Python - Component 3) ---
            from app.services.dna_generator import DocumentDNAGenerator
            dna_generator = DocumentDNAGenerator()
            document_dna = dna_generator.generate_dna(analyzed_pages, detected_topics, source_filename)

            # --- STEP 4: NAVIGATION AI (Gemini Call #1 - Component 4) ---
            print(f"🧭 Building hierarchical Navigation Map for: {source_filename}")
            from app.services.navigation_ai import NavigationAI
            nav_ai = NavigationAI()
            navigation_map = nav_ai.build_navigation_map(document_dna)

            # Save the permanent Navigation Map to PostgreSQL metadata
            doc.document_type = "Hierarchical Document"
            doc.document_purpose = navigation_map.get("document_title", source_filename)
            doc.planner_summary = f"Structured document containing {len(navigation_map.get('navigation', []))} navigation nodes."
            doc.knowledge_schema_version = 2
            doc.approved = True

            doc.knowledge_metadata = {
                "navigation_map": navigation_map,
                "strategy": "Hierarchical Navigation-Bounded RAG"
            }
            db.commit()

            # --- STEP 5: BOUNDED CHUNK ENGINE (Pure Python - Component 5) ---
            print(f"🧬 Executing Bounded Chunk Engine within Navigation Nodes...")
            from app.services.chunk_engine import ChunkEngine
            chunk_engine = ChunkEngine(navigation_map=navigation_map)
            bounded_chunks_pool = chunk_engine.execute_bounded_chunking(
                full_document_text=extracted_text, 
                source_filename=source_filename
            )
            
            # --- STEP 6: KNOWLEDGE ENRICHMENT AI (Batched Execution) ---
            print(f"✨ Enriching {len(bounded_chunks_pool)} bounded chunks in batches...")
            from app.services.extraction_service import ExtractionService
            import time
            
            enrichment_service = ExtractionService()
            processed_chunks_pool = []
            
            BATCH_SIZE = 5
            for i in range(0, len(bounded_chunks_pool), BATCH_SIZE):
                batch_slice = bounded_chunks_pool[i:i + BATCH_SIZE]
                enriched_batch = enrichment_service.enrich_chunks_batch(batch_slice)
                
                for enriched_chunk in enriched_batch:
                    processed_chunks_pool.append({
                        # 🟢 PROBLEM 5 FIX: Document Embedding uses PURE ORIGINAL TEXT ONLY.
                        # Summaries/Topics are decoupled into metadata below, NOT prepended to raw text.
                        "text": enriched_chunk.get('chunk_text'),
                        "source_file": enriched_chunk.get('source_file'),
                        "page_number": enriched_chunk.get('page_start', 1),
                        "page_end": enriched_chunk.get('page_end', 1),
                        "strategy_used": enriched_chunk.get('strategy_used'),
                        "navigation_node": enriched_chunk.get('navigation_node'),
                        "topic": enriched_chunk.get('topic'),
                        "subtopic": enriched_chunk.get('subtopic'),
                        # 🟢 PROBLEM 6 FIX: Carry over full structured enrichment metadata for vector filters & retrieval search terms
                        "enrichment": enriched_chunk.get('encryption', enriched_chunk.get('enrichment', {}))
                    })
                time.sleep(0.5)

            print(f"🟢 V2 Pipeline complete. Generated {len(processed_chunks_pool)} enriched bounded chunks safely.")

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

        # 5. Process each plain text chunk[cite: 5]
        for index, chunk_payload in enumerate(processed_chunks_pool):
            plain_text_content = chunk_payload["text"]
            if not plain_text_content.strip():
                continue
                
            chunk_id = f"{doc.id}_chunk_{index}"
            raw_vector_array = None
            
            for model_name in ["text-embedding-004", "gemini-embedding-001"]:
                try:
                    vector_response = ai_client.models.embed_content(
                        model=model_name,
                        contents=plain_text_content
                    )
                    candidate = vector_response.embeddings[0].values
                    # Validate vector is a proper list/array and contains no NaN values
                    import math
                    if candidate and isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                        if not any(math.isnan(x) for x in candidate if isinstance(x, (int, float))):
                            raw_vector_array = candidate
                            break
                except Exception:
                    continue

            # Skip chunk entirely if embedding generation failed or returned NaN
            if not raw_vector_array:
                print(f"⚠️ Warning: Skipping chunk {index} due to invalid or null embedding response.")
                continue

            embeddings.append(raw_vector_array)
            masked_payload_string = encrypt_text_string(plain_text=plain_text_content, workspace_id=doc.workspace_id)
            
            ids.append(chunk_id)
            documents.append(masked_payload_string) 
            
            for enriched_chunk in enriched_batch:
                    processed_chunks_pool.append({
                        "text": enriched_chunk.get('chunk_text'),
                        "source_file": enriched_chunk.get('source_file'),
                        "page_number": enriched_chunk.get('page_start', 1),
                        "page_end": enriched_chunk.get('page_end', 1),
                        "strategy_used": enriched_chunk.get('strategy_used'),
                        "navigation_node": enriched_chunk.get('navigation_node'),
                        "topic": enriched_chunk.get('topic'),
                        "subtopic": enriched_chunk.get('subtopic'),
                        # 🟢 Corrected key mapping
                        "enrichment": enriched_chunk.get('enrichment', {})
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