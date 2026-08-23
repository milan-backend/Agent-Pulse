import os
import uuid
import chromadb
from typing import List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.new_arch import DocumentChunk
from app.core.rag_crypto import decrypt_text_string

load_dotenv()

class RetrievalService:
    def __init__(self):
        chroma_host = str(os.getenv("CHROMA_HOST")).strip().rstrip("/")
        chroma_token = os.getenv("CHROMA_TOKEN")
        
        if not chroma_host:
            raise ValueError("CRITICAL: CHROMA_HOST environment variable is missing.")

        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
        )
        
        # 🟢 We are strictly using the single Unified Collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )

    def execute_direct_id_retrieval(
        self, 
        target_chunk_ids: List[str],  # 🟢 Directly accepts the list of UUIDs (including neighbors) from the Smart Router
        workspace_id: uuid.UUID
    ) -> List[Dict[str, Any]]:
        """
        Direct ID Retrieval Engine:
        1. Fully trusts the authorized Chunk IDs from the Router.
        2. Unconditionally fetches every requested chunk (Bypasses semantic math entirely).
        3. Decrypts and sorts the text into perfect reading order.
        """
        if not target_chunk_ids:
            return []

        # =====================================================================
        # 🟢 STEP 1: INSTANT CHROMA FETCH (No Vector Math)
        # =====================================================================
        try:
            print(f"⚡ Fetching {len(target_chunk_ids)} exact chunks from ChromaDB...")
            results = self.collection.get(
                ids=target_chunk_ids,
                where={"workspace_id": str(workspace_id)}
            )
        except Exception as e:
            print(f"⚠️ Chroma Direct ID Fetch error: {e}")
            return []

        if not results or not results.get("ids"):
            return []

        retrieved_chunks = []
        db: Session = SessionLocal()
        
        try:
            # =====================================================================
            # 🟢 STEP 2: DECRYPT & FETCH SEQUENCE NUMBERS
            # =====================================================================
            for idx, chroma_id in enumerate(results["ids"]):
                encrypted_doc = results["documents"][idx] if results.get("documents") else ""
                meta = results["metadatas"][idx] if results.get("metadatas") else {}

                # 1. Decrypt the raw text
                decrypted_text = decrypt_text_string(encrypted_doc, workspace_id)

                # 2. Query Postgres ONLY to get the Sequence Number for sorting
                chunk_record = db.query(DocumentChunk).filter(
                    DocumentChunk.id == chroma_id,
                    DocumentChunk.workspace_id == workspace_id
                ).first()

                retrieved_chunks.append({
                    "chunk_id": chroma_id,
                    "document_id": meta.get("document_id"),
                    "section_id": meta.get("section_id"),
                    "text": decrypted_text,
                    "sequence_number": chunk_record.sequence_number if chunk_record else 0
                })

        finally:
            db.close()

        # =====================================================================
        # 🟢 STEP 3: DEDUPLICATE & SORT FOR THE LLM
        # =====================================================================
        # 1. Deduplicate by chunk_id just in case
        unique_chunks_map = {c["chunk_id"]: c for c in retrieved_chunks}
        unique_chunks = list(unique_chunks_map.values())
        
        # 2. Sort by sequence_number so the Final LLM reads the paragraphs in the exact correct order
        unique_chunks.sort(key=lambda x: x["sequence_number"])

        print(f"✅ Successfully retrieved, decrypted, and sorted {len(unique_chunks)} chunks for the Response AI.")
        return unique_chunks