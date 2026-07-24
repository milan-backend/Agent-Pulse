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

# 🟢 IMPORT NEW INGESTION PIPELINE COMPONENTS (Phase 1 & Phase 2)
from app.services.extraction_service import (
    get_intelligence_client,
    run_phase_1_knowledge_extraction
)
from app.services.plan_validator import validate_and_sanitize_ingestion_plan
from app.services.chunk_engine import ChunkEngine

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
        
        # 3. Extract Full Raw Text Content String
        extracted_text = ""
        if doc.mime_type == "text/plain":
            extracted_text = raw_file_bytes.decode("utf-8", errors="ignore")
        elif doc.mime_type == "application/pdf":
            pdf_stream = io.BytesIO(raw_file_bytes)
            reader = PdfReader(pdf_stream)
            extracted_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
        if not extracted_text.strip():
            raise ValueError("Zero human-readable text contents could be extracted from this asset resource.")

        # =====================================================================
        # 🎯 NEW KNOWLEDGE INGESTION PIPELINE (PHASE 1 & PHASE 2)
        # =====================================================================
        try:
            print(f"🧠 Commencing Knowledge Ingestion Pipeline for Document ID: {doc.id}")
            global_sample_window = extracted_text[:40000]
            
            intelligence_client = get_intelligence_client()
            
            # --- STEP 1: EXTRACTION AI (Phase 1) ---
            print(f"📡 Generating Knowledge Ingestion Plan for: {doc.filename}")
            raw_ingestion_plan = run_phase_1_knowledge_extraction(global_sample_window, intelligence_client)
            
            # --- STEP 2: VALIDATION LAYER ---
            validated_plan = validate_and_sanitize_ingestion_plan(raw_ingestion_plan)
            print(f"✅ Ingestion Plan Validated. Strategy: {validated_plan.chunking.strategy} | Size: {validated_plan.chunking.chunk_size}")

            # Save plan metadata directly to PostgreSQL
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
                "dynamic_metadata": [m.model_dump() for m in validated_plan.metadata],
                "relationships": [r.model_dump() for r in validated_plan.relationships],
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

            # --- STEP 3: CHUNK ENGINE (Phase 2) ---
            print(f"🧬 Executing Chunk Engine for {doc.filename}...")
            chunk_engine = ChunkEngine(plan=validated_plan)
            processed_chunks_pool = chunk_engine.execute_chunking(
                text=extracted_text, 
                source_filename=doc.filename
            )
            
            print(f"🟢 Chunk Engine finished. Created {len(processed_chunks_pool)} chunks.")

        except Exception as pipeline_err:
            db.rollback()
            error_str = f"Knowledge Ingestion Pipeline Error: {str(pipeline_err)}"
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
            
            try:
                vector_response = ai_client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=plain_text_content
                )
                raw_vector_array = vector_response.embeddings[0].values
            except Exception:
                try:
                    vector_response = ai_client.models.embed_content(
                        model="text-embedding-004",
                        contents=plain_text_content
                    )
                    raw_vector_array = vector_response.embeddings[0].values
                except Exception:
                    vector_response = ai_client.models.embed_content(
                        model="text-embedding-005",
                        contents=plain_text_content
                    )
                    raw_vector_array = vector_response.embeddings[0].values

            embeddings.append(raw_vector_array)
            masked_payload_string = encrypt_text_string(plain_text=plain_text_content, workspace_id=doc.workspace_id)
            
            ids.append(chunk_id)
            documents.append(masked_payload_string) 
            
            metadatas.append({
                "workspace_id": str(doc.workspace_id),
                "agent_id": str(doc.agent_id) if doc.agent_id else "None",
                "document_id": str(doc.id),
                "source_file": str(chunk_payload["source_file"]),          
                "page_number": int(chunk_payload["page_number"]),          
                "last_updated": current_timestamp_iso,                    
                "uploaded_by": uploader_email                              
            })
            
        if ids:
            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
        doc.status = "ready"
        db.commit()
        print(f"🚀 Success: Cloud server ingestion complete for '{doc.filename}'. Loaded {len(ids)} chunks.")
        return True
        
    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure: {str(error)}")
        return False