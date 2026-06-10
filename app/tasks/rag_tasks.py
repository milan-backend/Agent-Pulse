import os
import io
import uuid
from datetime import datetime
import chromadb
from celery import Celery
from sqlalchemy.orm import Session
from pypdf import PdfReader
from google import genai  # 🎯 Added for the official Google GenAI SDK interface

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.models.user import User  
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string

# Initialize Celery app matching your system's setup instance configuration
CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL")
if not CELERY_BROKER:
    raise ValueError("CRITICAL CONFIGURATION TIMEOUT: CELERY_BROKER_URL or REDIS_URL environment variable is missing on this worker node context.")

celery_app = Celery("rag_tasks", broker=CELERY_BROKER)


# =====================================================================
# ✅ FIXED: LAZY INITIALIZATION HELPER (NO HARDCODED PAYLOAD LINKS)
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
    # Safeguard against short text blocks falling into an infinite execution trap
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
            
        # Resolve user explicit identifier metadata safely to provide "Uploaded By" telemetry logs
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
        
        # 3. Extract text content string based on target MIME Type extension variations, capturing local page coordinates
        processed_chunks_pool = []
        
        # SUPPORTED FILE TYPE 1: Plain Text (.txt) Ingestion Gateway Handler
        if doc.mime_type == "text/plain":
            extracted_text = raw_file_bytes.decode("utf-8", errors="ignore")
            processed_chunks_pool.extend(
                chunk_text_by_page(text=extracted_text, page_num=1, source_filename=doc.filename)
            )
            
        # SUPPORTED FILE TYPE 2: Multi-page Portable Documents (.pdf) Ingestion Gateway Handler
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

        # 4. Initialize Cloud-Native Vector Engine Connection Dynamic Link
        chroma_client = get_chroma_client()
        
        # =====================================================================
        # 🎯 ENFORCED: DISTANCE METRIC SPACE LOCK TO COSINE SIMILARITY MATH
        # =====================================================================
        collection = chroma_client.get_or_create_collection(
            name="rag_knowledge_vectors",
            metadata={"hnsw:space": "cosine"}
        )
        
        # 🎯 INITIALIZE OFFICIAL GEMINI CLIENT FOR PLAIN TEXT EMBEDDINGS
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("CRITICAL INITIALIZATION ERROR: GEMINI_API_KEY environment variable is missing on Celery worker node context.")
            
        ai_client = genai.Client(api_key=gemini_api_key)
        
        ids = []
        embeddings = []  # 🎯 FIXED: Explicit vector tracking store array
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
            # 🚀 STEP A: Generate high-fidelity vector embedding from PLAIN TEXT
            # -----------------------------------------------------------------
            vector_response = ai_client.models.embed_content(
                model="text-embedding-004",
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
            
            # Metadata indices remain plaintext for fast conditional scoping
            metadatas.append({
                "workspace_id": str(doc.workspace_id),
                "agent_id": str(doc.agent_id) if doc.agent_id else "None",
                "document_id": str(doc.id),
                "source_file": str(chunk_payload["source_file"]),          
                "page_number": int(chunk_payload["page_number"]),          
                "last_updated": current_timestamp_iso,                    
                "uploaded_by": uploader_email                              
            })
            
        # 6. Push custom embeddings along with masked documents over to ChromaDB
        if ids:
            collection.add(
                ids=ids,
                embeddings=embeddings,  # ✅ FIXED PERMANENTLY: Chroma uses real text vectors for search
                documents=documents,     # ✅ SECURE: The raw stored field strictly contains your encrypted string
                metadatas=metadatas
            )
            
        # 7. Mark processing execution transaction as ready inside PostgreSQL
        doc.status = "ready"
        db.commit()
        print(f"🚀 Success: Cloud server ingestion complete for '{doc.filename}'. Loaded {len(ids)} text embeddings with secure ciphertext records.")
        return True
        
    except Exception as error:
        db.rollback()
        if doc:
            doc.status = "failed"
            db.commit()
        print(f"❌ Background pipeline failure for file record verification: {str(error)}")
        return False