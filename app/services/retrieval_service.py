import os
import uuid
import chromadb
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.uploaded_document import UploadedDocument
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

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("CRITICAL INITIALIZATION ERROR: GEMINI_API_KEY is missing.")
        self.ai_client = genai.Client(api_key=gemini_api_key)

    def _get_query_embedding(self, text: str) -> List[float]:
        """Generates query embedding matching the vector database model standard."""
        embedding_models = ["text-embedding-004", "gemini-embedding-001", "text-embedding-005"]
        
        for model_name in embedding_models:
            try:
                res = self.ai_client.models.embed_content(
                    model=model_name,
                    contents=text
                )
                if res and res.embeddings and res.embeddings[0].values:
                    return res.embeddings[0].values
            except Exception as e:
                continue
                
        raise ValueError(f"CRITICAL: Failed to generate query embedding for text using models: {embedding_models}")

    def execute_hybrid_retrieval(
        self, 
        query_vector: List[float], 
        workspace_id: uuid.UUID, 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        target_doc_ids = filters.get("document_ids", [])
        search_queries = filters.get("search_queries", [])

        if not target_doc_ids:
            return []

        queries_to_run = search_queries[:2] if search_queries else [""]

        where_filter = (
            {
                "$and": [
                    {"workspace_id": str(workspace_id)},
                    {"document_id": {"$in": [str(d) for d in target_doc_ids]}}
                ]
            } if len(target_doc_ids) > 1 else {
                "$and": [
                    {"workspace_id": str(workspace_id)},
                    {"document_id": str(target_doc_ids[0])}
                ]
            }
        )

        all_recovered_chunks = []
        seen_chunk_ids = set()

        for q_term in queries_to_run:
            if not q_term or not q_term.strip():
                continue
            try:
                q_emb = self._get_query_embedding(q_term)

                results = self.collection.query(
                    query_embeddings=[q_emb],
                    n_results=5,
                    where=where_filter
                )

                if results and results.get("ids") and results["ids"][0]:
                    for idx, c_id in enumerate(results["ids"][0]):
                        if c_id not in seen_chunk_ids:
                            seen_chunk_ids.add(c_id)
                            encrypted_doc = results["documents"][0][idx] if results.get("documents") else ""
                            meta = results["metadatas"][0][idx] if results.get("metadatas") else {}

                            decrypted_text = decrypt_text_string(
                                encrypted_doc,
                                workspace_id
                            )

                            all_recovered_chunks.append({
                                "chunk_id": c_id,
                                "document_id": meta.get("document_id"),
                                "text": decrypted_text,
                                "source_file": meta.get("source_file", "Unknown"),
                                "page_number": meta.get("page_number", 1)
                            })
            except Exception as e:
                print(f"⚠️ Fast vector query error: {e}")

        if not all_recovered_chunks:
            return []

        db: Session = SessionLocal()
        reconstructed_sections = []
        try:
            unique_doc_ids = list(set([c["document_id"] for c in all_recovered_chunks if c.get("document_id")]))
            doc_records = db.query(UploadedDocument).filter(UploadedDocument.id.in_(unique_doc_ids)).all()
            doc_map = {str(d.id): d.filename for d in doc_records}

            for chunk in all_recovered_chunks:
                d_id = chunk["document_id"]
                filename = doc_map.get(str(d_id), chunk["source_file"])
                reconstructed_sections.append({
                    "document_id": d_id,
                    "filename": filename,
                    "section_name": filename,  # 🟢 Essential: Guarantees ContextOptimizer won't throw KeyError
                    "content": chunk["text"],
                    "page_number": chunk["page_number"]
                })
        except Exception as sql_err:
            print(f"⚠️ Section stitching batch SQL warning: {sql_err}")
            for chunk in all_recovered_chunks:
                filename = chunk["source_file"]
                reconstructed_sections.append({
                    "document_id": chunk["document_id"],
                    "filename": filename,
                    "section_name": filename,  # 🟢 Essential fallback mapping
                    "content": chunk["text"],
                    "page_number": chunk["page_number"]
                })
        finally:
            db.close()

        return self._deduplicate_and_rerank(reconstructed_sections)

    def _deduplicate_and_rerank(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_chunks = set()
        unique_sections = []
        for sec in sections:
            content_key = sec["content"].strip()
            if content_key not in seen_chunks:
                seen_chunks.add(content_key)
                unique_sections.append(sec)
        return unique_sections