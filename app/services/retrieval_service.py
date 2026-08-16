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
        include_neighbor_chunks: bool = False,
        user_prompt: str = None,
        top_k: int = 10  # 🟢 THE FIX: Increase from 3 to 10
    ) -> List[Dict[str, Any]]:
        """
        Direct ID Retrieval Engine with Token-Saving Re-ranking:
        1. Constrains the search strictly to the Vector IDs provided by the Smart Router.
        2. Reranks those chunks using the user's query and returns only the top 3.
        """
        if not target_chroma_ids:
            return []

        # 1. Fetch exact documents from Chroma DB by vector IDs
        try:
            if user_prompt:
                print(f"🎯 Re-ranking {len(target_chroma_ids)} chunks down to Top {top_k}...")
                
                # 🟢 THE FIX: Convert the text to a vector using the exact same Gemini model
                gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not gemini_key:
                    raise ValueError("Missing Gemini API Key for Retrieval")
                
                ai_client = genai.Client(api_key=gemini_key)
                
                vector_response = ai_client.models.embed_content(
                    model="models/gemini-embedding-001",
                    contents=user_prompt
                )
                prompt_vector = vector_response.embeddings[0].values
                
                # 🟢 THE FIX: Pass query_embeddings instead of query_texts
                raw_results = self.collection.query(
                    query_embeddings=[prompt_vector],
                    n_results=top_k * 3, # Pull a slightly wider net initially 
                    where={"workspace_id": str(workspace_id)}
                )
                
                valid_ids = []
                valid_docs = []
                valid_metas = []
                
                # Intersect the semantic query results with the Router's approved section IDs
                if raw_results and raw_results.get("ids") and len(raw_results["ids"]) > 0:
                    for i, c_id in enumerate(raw_results["ids"][0]):
                        if c_id in target_chroma_ids and len(valid_ids) < top_k:
                            valid_ids.append(c_id)
                            valid_docs.append(raw_results["documents"][0][i])
                            valid_metas.append(raw_results["metadatas"][0][i])
                            
                    results = {
                        "ids": valid_ids,
                        "documents": valid_docs,
                        "metadatas": valid_metas
                    }
                else:
                    results = {}
            else:
                # Fallback: Blanket Get if no prompt is provided
                results = self.collection.get(
                    ids=target_chroma_ids,
                    where={"workspace_id": str(workspace_id)}
                )
                
        except Exception as e:
            print(f"⚠️ Chroma Fetch/Query error: {e}")
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