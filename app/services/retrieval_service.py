import os
import uuid
import chromadb
from typing import List, Dict, Any
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from google import genai  # 🟢 NEW: Added for manual vector embedding

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
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )

    def execute_direct_id_retrieval(
        self, 
        target_chroma_ids: List[str], 
        workspace_id: uuid.UUID,
        include_neighbor_chunks: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Direct ID Retrieval Engine (Section Overwrite):
        1. Fully trusts the Smart Router's authorized Vector IDs.
        2. Unconditionally fetches every requested chunk (No top_k limits).
        3. Bypasses semantic re-ranking to prevent Shattered Tables.
        """
        if not target_chroma_ids:
            return []

        # 🟢 THE FIX: Unconditional Retrieval. Fetch all requested IDs!
        try:
            results = self.collection.get(
                ids=target_chroma_ids,
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
            for idx, chroma_id in enumerate(results["ids"]):
                encrypted_doc = results["documents"][idx] if results.get("documents") else ""
                meta = results["metadatas"][idx] if results.get("metadatas") else {}

                decrypted_text = decrypt_text_string(encrypted_doc, workspace_id)

                # Query SQL for chunk record & neighbor expansion
                chunk_record = db.query(DocumentChunk).filter(
                    DocumentChunk.chroma_vector_id == chroma_id,
                    DocumentChunk.workspace_id == workspace_id
                ).first()

                retrieved_chunks.append({
                    "chroma_id": chroma_id,
                    "document_id": meta.get("document_id"),
                    "section_id": meta.get("section_id"),
                    "text": decrypted_text,
                    "sequence_number": chunk_record.sequence_number if chunk_record else 1
                })

                # 2. Dynamic Depth Expansion via Relational Linked List
                if include_neighbor_chunks and chunk_record:
                    neighbor_ids = []
                    if chunk_record.prev_chunk_id:
                        neighbor_ids.append(chunk_record.prev_chunk_id)
                    if chunk_record.next_chunk_id:
                        neighbor_ids.append(chunk_record.next_chunk_id)

                    if neighbor_ids:
                        neighbors = db.query(DocumentChunk).filter(DocumentChunk.id.in_(neighbor_ids)).all()
                        neighbor_chroma_ids = [n.chroma_vector_id for n in neighbors if n.chroma_vector_id not in target_chroma_ids]
                        
                        if neighbor_chroma_ids:
                            n_results = self.collection.get(ids=neighbor_chroma_ids)
                            if n_results and n_results.get("ids"):
                                for n_idx, n_chroma_id in enumerate(n_results["ids"]):
                                    n_enc = n_results["documents"][n_idx]
                                    n_dec = decrypt_text_string(n_enc, workspace_id)
                                    retrieved_chunks.append({
                                        "chroma_id": n_chroma_id,
                                        "document_id": meta.get("document_id"),
                                        "section_id": meta.get("section_id"),
                                        "text": n_dec,
                                        "sequence_number": 0  # Neighbor context tag
                                    })

        finally:
            db.close()

        # Deduplicate retrieved chunks by content
        seen = set()
        unique_chunks = []
        for c in retrieved_chunks:
            if c["text"] not in seen:
                seen.add(c["text"])
                unique_chunks.append(c)

        return unique_chunks