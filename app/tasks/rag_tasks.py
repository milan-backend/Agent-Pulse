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

# 🟢 IMPORT THE INTEL LAYER EXTRACTION PIPELINES
from app.services.extraction_service import (
    get_intelligence_client,
    run_phase_a_document_extraction,
    run_phase_b_chunk_extraction,
    calculate_document_authority,
    calculate_compound_importance
)

# Initialize Celery app matching your system's setup instance configuration
CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
if not CELERY_BROKER:
    raise ValueError("CRITICAL CONFIGURATION TIMEOUT: CELERY_BROKER_URL or REDIS_URL environment variable is missing on this worker node context.")

celery_app = Celery("rag_tasks", broker=CELERY_BROKER)


# =====================================================================
# ✅ LAZY INITIALIZATION HELPER (NO HARDCODED PAYLOAD LINKS)
# =====================================================================
def get_chroma_client():
    """
    Dynamically initializes the Chroma client securely using environment parameters.
    Bypasses technical noise and prevents global-import server freezing traps.
    """
    CHROMA_HOST = os.getenv("CHROMA_HOST")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    
    if not CHROMA_HOST:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: CHROMA_HOST environment variable mapping is missing on this container instance.")
        
    CHROMA_HOST = str(CHROMA_HOST).strip().rstrip("/")
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )


def chunk_text_by_page(text: str, page_num: int, source_filename: str, chunk_size: int = 600, chunk_overlap: int = 120) -> list[dict]:
    """
    Splits plain text strings extracted from a specific page partition into overlapping paragraph blocks,
    mapping localized source page metadata tags dynamically for the checklist array requirements.
    """
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
    Celery Background Task Worker: Extracts, chunks, generates native vectors from plain text,
    encrypts payload text fragments, and loads semantic identifiers with metadata into ChromaDB.
    """
    db: Session = next(get_db())
    doc = None
    
    try:
        # 1. Fetch the target file tracking record from PostgreSQL
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
        if not doc:
            print(f"❌ Ingestion aborted: Document string UUID '{document_id}' not found inside Postgres context row.")
            return False
            
        uploader_email = "Unknown System Operator"
        if doc.uploaded_by:
            user_row = db.query(User).filter(User.id == doc.uploaded_by).first()
            if user_row and user_row.email:
                uploader_email = str(user_row.email).strip()

        # 2. Decrypt the raw binary bytes payload pulled from PostgreSQL (Tier 1 Protection)
        raw_file_bytes = decrypt_file_bytes(
            ciphertext=doc.encrypted_file_data,
            iv=doc.encryption_iv,
            workspace_id=doc.workspace_id
        )
        
        # 3. Extract text content string based on target MIME Type extension variations
        processed_chunks_pool = []
        
        if doc.mime_type == "text/plain":
            extracted_text = raw_file_bytes.decode("utf-8", errors="ignore")
            processed_chunks_pool.extend(
                chunk_text_by_page(text=extracted_text, page_num=1, source_filename=doc.filename)
            )
            
        elif doc.mime_type == "application/pdf":
            pdf_stream = io.BytesIO(raw_file_bytes)
            reader = PdfReader(pdf_stream)
            
            for page_index, page in enumerate(reader.pages):
                text_content = page.extract_text()
                if text_content and text_content.strip():
                    processed_chunks_pool.extend(
                        chunk_text_by_page(text=text_content, page_num=page_index + 1, source_filename=doc.filename)
                    )
            
        if not processed_chunks_pool:
            raise ValueError("Zero human-readable text contents could be extracted from this asset resource.")

        # =====================================================================
        # 🎯 ADVANCED ARCHITECTURE UPGRADE: DUAL-PHASE EXTRACT & COMPILATION
        # =====================================================================
        try:
            print(f"🧠 Commencing Enterprise Knowledge Extraction Pipeline for Document ID: {doc.id}")
            
            # Reconstruct an aggregate global window sample of the document text footprint
            full_raw_text_recon = " ".join([c["text"] for c in processed_chunks_pool])
            global_sample_window = full_raw_text_recon[:40000]
            
            # Initialize a single shared Gemini client context for optimal network efficiency
            intelligence_client = get_intelligence_client()
            
            # --- PHASE A: DOCUMENT LEVEL EXTRACTION (RUNS ONCE PER DOCUMENT) ---
            print(f"📡 Executing Phase A Global Metadata Extraction for: {doc.filename}")
            phase_a_meta = run_phase_a_document_extraction(global_sample_window, intelligence_client)
            
            # Save Phase A Primitives straight to first-class PostgreSQL columns
            doc.document_type = phase_a_meta.document_type
            doc.document_role = phase_a_meta.document_role
            doc.departments = phase_a_meta.departments
            doc.topics = phase_a_meta.topics
            doc.document_purpose = phase_a_meta.document_purpose
            doc.planner_summary = phase_a_meta.planner_summary
            doc.time_scope = phase_a_meta.time_scope
            doc.document_status = phase_a_meta.document_status
            doc.knowledge_schema_version = 1
            
            # Ensure sorting compatibility metrics have defaults mapped
            doc.version = "1.0.0"
            doc.approved = True
            
            # --- PHASE B: CHUNK LEVEL GRAPH EXTRACTION & PYTHON AGGREGATION ---
            print(f"🧬 Commencing Phase B Aggregation across {len(processed_chunks_pool)} localized segments...")
            
            aggregated_entities = []
            aggregated_relationships = []
            aggregated_facts = []
            aggregated_keywords = []
            aggregated_questions = []
            
            seen_entity_keys = set()
            seen_relationship_keys = set()
            
            for chunk_data in processed_chunks_pool:
                try:
                    chunk_meta = run_phase_b_chunk_extraction(chunk_data["text"], intelligence_client)
                    
                    for entity in chunk_meta.entities:
                        entity_key = f"{entity.name.lower().strip()}_{entity.entity_type.lower().strip()}"
                        if entity_key not in seen_entity_keys:
                            seen_entity_keys.add(entity_key)
                            aggregated_entities.append({"name": entity.name, "entity_type": entity.entity_type})
                            
                    for rel in chunk_meta.relationships:
                        rel_key = f"{rel.source.lower().strip()}_{rel.relation.lower().strip()}_{rel.target.lower().strip()}"
                        if rel_key not in seen_relationship_keys:
                            seen_relationship_keys.add(rel_key)
                            aggregated_relationships.append({
                                "source": rel.source,
                                "relation": rel.relation,
                                "target": rel.target,
                                "confidence": rel.confidence
                            })
                            
                    aggregated_facts.extend([f for f in chunk_meta.facts if f not in aggregated_facts])
                    aggregated_keywords.extend([k for k in chunk_meta.retrieval_keywords if k not in aggregated_keywords])
                    aggregated_questions.extend([q for q in chunk_meta.questions_this_document_can_answer if q not in aggregated_questions])
                    
                except Exception as chunk_err:
                    print(f"⚠️ Warning: Granular segment skipped due to extraction variance: {str(chunk_err)}")
                    continue

            # --- CALCULATE SYSTEM BALANCED PERFORMANCE WEIGHTS ---
            base_authority = calculate_document_authority(phase_a_meta.document_type)
            compound_importance = calculate_compound_importance(
                meta_a=phase_a_meta,
                answers_count=len(aggregated_questions),
                relationships_count=len(aggregated_relationships)
            )
            
            doc.authority_score = base_authority
            doc.importance_score = compound_importance
            
            # --- PACK DEEP INTELLIGENCE POOL INTO COMPACT KNOWLEDGE_METADATA COLUMN ---
            doc.knowledge_metadata = {
                "entities": aggregated_entities,
                "relationships": aggregated_relationships,
                "facts": aggregated_facts,
                "retrieval_keywords": aggregated_keywords,
                "questions_this_document_can_answer": aggregated_questions,
                "metrics": [],
                "confidence": {
                    "classification_confidence": phase_a_meta.classification_confidence
                }
            }
            
            db.commit()
            print(f"🟢 Knowledge Registry Pipeline Complete for '{doc.filename}'! Role: {doc.document_role} | Importance: {doc.importance_score}")
            
        except Exception as pipeline_err:
            db.rollback()
            error_str = f"Dual-Phase Extraction Error: {str(pipeline_err)}"
            print(f"❌ Critical architectural pipeline extraction rollback triggered: {error_str}")
            
            # 🎯 FORCE BREAK: Bubble the extraction crash directly to the main failure handler
            raise ValueError(error_str)
        # =====================================================================

        # 4. Initialize Cloud-Native Vector Engine Connection Dynamic Link
        chroma_client = get_chroma_client()
        
        # =====================================================================
        # 🎯 ENFORCED: DISTANCE METRIC SPACE LOCK TO COSINE SIMILARITY MATH
        # =====================================================================
        collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )
        
        # INITIALIZE OFFICIAL GEMINI CLIENT FOR PLAIN TEXT EMBEDDINGS
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("CRITICAL INITIALIZATION ERROR: GEMINI_API_KEY environment variable is missing on Celery worker node context.")
            
        ai_client = genai.Client(api_key=gemini_api_key)
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        current_timestamp_iso = datetime.utcnow().strftime("%Y-%m-%d")

        # 5. Process each plain text chunk: Generate true vectors first, then encrypt text data
        for index, chunk_payload in enumerate(processed_chunks_pool):
            plain_text_content = chunk_payload["text"]
            if not plain_text_content.strip():
                continue
                
            chunk_id = f"{doc.id}_chunk_{index}"
            
            # -----------------------------------------------------------------
            # 🚀 STEP A: Self-Healing Multi-Model Fallback Ingestion Loop
            # -----------------------------------------------------------------
            raw_vector_array = None
            
            try:
                vector_response = ai_client.models.embed_content(
                    model="gemini-embedding-2",
                    contents=plain_text_content
                )
                raw_vector_array = vector_response.embeddings[0].values
            except Exception as e1:
                print(f"⚠️ 'gemini-embedding-2' route failed, falling back to legacy paths: {str(e1)}")
                
                try:
                    vector_response = ai_client.models.embed_content(
                        model="text-embedding-004",
                        contents=plain_text_content
                    )
                    raw_vector_array = vector_response.embeddings[0].values
                except Exception as e2:
                    print(f"⚠️ 'text-embedding-004' route failed, attempting baseline recovery: {str(e2)}")
                    
                    vector_response = ai_client.models.embed_content(
                        model="text-embedding-005",
                        contents=plain_text_content
                    )
                    raw_vector_array = vector_response.embeddings[0].values

            embeddings.append(raw_vector_array)
            
            # -----------------------------------------------------------------
            # 🔒 STEP B: Run Tier 2 Security Cryptographic Masking Protection Layer
            # -----------------------------------------------------------------
            masked_payload_string = encrypt_text_string(
                plain_text=plain_text_content, 
                workspace_id=doc.workspace_id
            )
            
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
        print(f"🚀 Success: Cloud server ingestion complete for '{doc.filename}'. Loaded {len(ids)} text embeddings with secure ciphertext records.")
        return True
        
    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            doc.error_message = str(error)
            db.commit()
        print(f"❌ Background pipeline failure for file record verification: {str(error)}")
        return False