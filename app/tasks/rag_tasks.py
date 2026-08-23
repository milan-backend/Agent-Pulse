import os
import uuid
import time
from celery import Celery
from sqlalchemy.orm import Session
import chromadb
from google import genai  

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string

# 🟢 NEW ARCHITECTURE IMPORTS
from app.services.navigation_service import build_and_save_navigation_map
from app.services.pdf_parser import extract_smart_pages
from app.services.chunk_engine import ChunkEngine
from app.models.new_arch import DocumentChunk

import re

def extract_chunk_keywords(text: str) -> str:
    """
    Extracts high-signal tokens instantly in Python without LLM API calls.
    Keeps ALL unique tokens instead of truncating them!
    """
    if not text:
        return ""
    
    # 1. Finds acronyms (e.g., IGNOU)
    # 2. Finds numbers/decimals (e.g., 12123.00)
    # 3. Finds capitalized nouns and proper names (e.g., Indira, Education)
    tokens = re.findall(r'\b[A-Z]{2,}\b|\b\d+(?:\.\d+)?\b|\b[A-Z][a-z]{3,}\b', text)
    
    unique_tokens = list(dict.fromkeys(tokens))
    return ", ".join(unique_tokens)  # 🟢 REMOVED THE [:15] LIMIT! Keep them all!

CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
if not CELERY_BROKER:
    raise ValueError("CRITICAL: CELERY_BROKER_URL missing.")

celery_app = Celery("rag_tasks", broker=CELERY_BROKER)

def get_chroma_client():
    CHROMA_HOST = str(os.getenv("CHROMA_HOST", "")).strip().rstrip("/")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    return chromadb.HttpClient(
        host=CHROMA_HOST,
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )

@celery_app.task(name="app.tasks.rag_tasks.process_document_embedding")
def process_document_embedding(document_id: str):
    db: Session = next(get_db())
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    
    if not doc:
        print(f"❌ Ingestion aborted: Document UUID '{document_id}' not found.")
        return False
        
    try:
        # 1. Decrypt File Bytes
        raw_file_bytes = decrypt_file_bytes(doc.encrypted_file_data, doc.encryption_iv, doc.workspace_id)
        temp_pdf_path = f"/tmp/{uuid.uuid4().hex}.pdf"
        with open(temp_pdf_path, "wb") as f:
            f.write(raw_file_bytes)

        print(f"🧠 Commencing Knowledge Ingestion for Document ID: {doc.id}")
        
        # =====================================================================
        # 🎯 STAGE 1: NAVIGATION & STATE MACHINE
        # =====================================================================
        smart_pages = extract_smart_pages(temp_pdf_path)
        if not smart_pages:
            raise ValueError("Zero content extracted from document.")

        # The State Machine automatically merges multi-page tables and saves to Postgres
        saved_sections = build_and_save_navigation_map(
            db=db, 
            document_id=doc.id, 
            workspace_id=doc.workspace_id,
            smart_pages=smart_pages
        )

        # =====================================================================
        # 🎯 STAGE 2: SYSTEM PREP
        # =====================================================================
        chroma_client = get_chroma_client()
        # 🟢 THE UNIFIED COLLECTION (We deleted nav_collection!)
        collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1", 
            metadata={"hnsw:space": "cosine"}
        )
        
        ai_client = genai.Client(api_key=os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY"))
        chunk_engine = ChunkEngine(table_row_limit=5, narrative_chunk_size=400, overlap=50)

        # =====================================================================
        # 🎯 STAGE 3: CHUNKING & DUAL-INSERT (Postgres + Chroma)
        # =====================================================================
        for section in saved_sections:
            # Grab the perfectly stitched text directly from the State Machine's memory
            section_text = getattr(section, "_temp_text", "")
            if not section_text.strip(): 
                continue

            # Python slices the text mathematically and assigns UUIDs/Relationships
            section_chunks = chunk_engine.execute_section_chunking(
                section_text=section_text,
                section_id=section.id,
                document_id=doc.id,
                workspace_id=doc.workspace_id,
                content_type=section.content_type,
                table_headers=section.table_headers
            )
            
            for chunk_payload in section_chunks:
                chunk_uuid = chunk_payload["id"]  # 🟢 The Master Pointer
                pt_content = chunk_payload["text"]
                
                # 🟢 Extract the specific needles for this chunk!
                chunk_specific_keywords = extract_chunk_keywords(pt_content)
                
                # A. Generate Vector
                vector_resp = ai_client.models.embed_content(
                    model="models/gemini-embedding-001", 
                    contents=pt_content
                )
                raw_vector = vector_resp.embeddings[0].values
                
                # B. Save to PostgreSQL (The Relational Brain)
                new_db_chunk = DocumentChunk(
                    id=chunk_uuid, 
                    document_id=doc.id, 
                    section_id=section.id, 
                    workspace_id=doc.workspace_id,
                    sequence_number=chunk_payload["sequence_number"],
                    chunk_keywords=chunk_specific_keywords, # 🟢 Save granular keywords to DB
                    prev_chunk_id=chunk_payload["prev_chunk_id"],  
                    next_chunk_id=chunk_payload["next_chunk_id"]   
                )
                db.add(new_db_chunk)
                
                # C. Save to ChromaDB (The Search Vault & Index of Indexes)
                encrypted_doc = encrypt_text_string(pt_content, doc.workspace_id)
                collection.add(
                    ids=[str(chunk_uuid)],               
                    embeddings=[raw_vector], 
                    documents=[encrypted_doc],
                    metadatas=[{
                        "chunk_id": str(chunk_uuid),
                        "section_id": str(section.id),
                        "parent_path": str(section.parent_path) if section.parent_path else str(section.title),
                        "type": str(section.content_type),
                        "parent_keywords": str(section.parent_keywords) if section.parent_keywords else "",
                        "chunk_keywords": chunk_specific_keywords, # 🟢 Inject granular keywords into metadata
                        "semantic_summary": str(section.semantic_summary) if section.semantic_summary else "",
                        "document_id": str(doc.id),
                        "workspace_id": str(doc.workspace_id)
                    }]
                )
                
        # Finalize Transactions
        db.commit()
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

        doc.status = "ready"
        db.commit()
        print(f"🚀 Success: Unified hierarchical ingestion complete for '{doc.filename}'.")
        return True
        
    except Exception as pipeline_err:
        db.rollback()
        if doc:
            doc.status = "failed"
            doc.error_message = str(pipeline_err)
            db.commit()
        print(f"❌ Background pipeline failure: {str(pipeline_err)}")
        return False