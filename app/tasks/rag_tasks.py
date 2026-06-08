import os
import io
import uuid
import chromadb
from celery import Celery
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.db.session import get_db
from app.models.uploaded_document import UploadedDocument
from app.core.rag_crypto import decrypt_file_bytes, encrypt_text_string

# Initialize Celery app matching your system's setup instance configuration
CELERY_BROKER = os.getenv("CELERY_BROKER_URL") or os.getenv("REDIS_URL") or "redis://localhost:6379/0"
celery_app = Celery("rag_tasks", broker=CELERY_BROKER)

# DECENTRALIZED: Switch from local disk client to cloud server HTTP Client
CHROMA_HOST = os.getenv("CHROMA_HOST", "http://localhost:8000")
chroma_client = chromadb.HttpClient(host=CHROMA_HOST)


def chunk_text(text: str, chunk_size: int = 600, chunk_overlap: int = 120) -> list[str]:
    """
    Splits plain text strings into overlapping paragraph blocks for semantic chunking analysis.
    """
    if not text:
        return []
        
    words = text.split()
    chunks = []
    
    # Calculate word boundaries
    stride = chunk_size - chunk_overlap
    for i in range(0, len(words), stride):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
            
    return chunks


@celery_app.task(name="app.tasks.rag_tasks.process_document_embedding")
def process_document_embedding(document_id: str):
    """
    Celery Background Task Worker: Extracts, chunks, encrypts text fragments, 
    and loads semantic identifiers into the decentralized Railway ChromaDB server.
    """
    db: Session = next(get_db())
    
    # 1. Fetch the target file tracking record from PostgreSQL
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
    if not doc:
        print(f"❌ Ingestion aborted: Document string UUID '{document_id}' not found inside Postgres context row.")
        return False
        
    try:
        # 2. Decrypt the raw binary bytes payload pulled from PostgreSQL
        raw_file_bytes = decrypt_file_bytes(
            ciphertext=doc.encrypted_file_data,
            iv=doc.encryption_iv,
            workspace_id=doc.workspace_id
        )
        
        # 3. Extract text content string based on target MIME Type extension variations
        extracted_text = ""
        
        if doc.mime_type == "text/plain":
            extracted_text = raw_file_bytes.decode("utf-8", errors="ignore")
            
        elif doc.mime_type == "application/pdf":
            # Stream the file bytes seamlessly inside memory arrays
            pdf_stream = io.BytesIO(raw_file_bytes)
            reader = PdfReader(pdf_stream)
            
            pages_text = []
            for page in reader.pages:
                text_content = page.extract_text()
                if text_content:
                    pages_text.append(text_content)
            extracted_text = "\n".join(pages_text)
            
        if not extracted_text.strip():
            raise ValueError("Zero human-readable text contents could be extracted from this asset resource.")

        # 4. Generate overlapping semantic chunks arrays
        text_chunks = chunk_text(extracted_text)
        
        # 5. Handshake with the centralized ChromaDB cluster over HTTP
        collection = chroma_client.get_or_create_collection(name="rag_knowledge_base")
        
        ids = []
        documents = []
        metadatas = []
        
        # 6. Encrypt each chunk text explicitly before streaming into Chroma metadata vectors
        for index, text_chunk in enumerate(text_chunks):
            chunk_id = f"{doc.id}_chunk_{index}"
            
            # Run Tier 2 Security Cryptographic Masking
            masked_payload_string = encrypt_text_string(plain_text=text_chunk, workspace_id=doc.workspace_id)
            
            ids.append(chunk_id)
            # We save the unreadable cipher text into Chroma's documents column
            documents.append(masked_payload_string) 
            
            # Plain numbers and UUID markers stay in unencrypted indexing boundaries for fast searches
            metadatas.append({
                "workspace_id": str(doc.workspace_id),
                "agent_id": str(doc.agent_id) if doc.agent_id else "None",
                "document_id": str(doc.id)
            })
            
        # 7. Push vectors over HTTP to ChromaDB
        if ids:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
        # 8. Mark processing execution transaction as ready inside Postgres
        doc.status = "ready"
        db.commit()
        print(f"🚀 Success: Cloud server ingestion complete for '{doc.filename}'. Loaded {len(ids)} masked text vectors.")
        return True
        
    except Exception as error:
        db.rollback()
        # Explicit status tracking error management fallback loop configuration block
        doc.status = "failed"
        db.commit()
        print(f"❌ Background pipeline failure for file record ID '{document_id}': {str(error)}")
        return False