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
        try:
            res = self.ai_client.models.embed_content(
                model="gemini-embedding-2",
                contents=text
            )
            return res.embeddings[0].values
        except Exception:
            try:
                res = self.ai_client.models.embed_content(
                    model="text-embedding-004",
                    contents=text
                )
                return res.embeddings[0].values
            except Exception:
                res = self.ai_client.models.embed_content(
                    model="text-embedding-005",
                    contents=text
                )
                return res.embeddings[0].values

    def execute_hybrid_retrieval(
        self, 
        query_vector: List[float], 
        workspace_id: uuid.UUID, 
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        target_doc_ids = filters.get("document_ids", [])
        target_nav_nodes = filters.get("target_navigation_nodes", [])
        search_queries = filters.get("search_queries", [])

        if not target_doc_ids:
            return []

        queries_to_run = search_queries[:2] if search_queries else [""]

        # 🟢 Construct ChromaDB Where Filter supporting V2 Navigation Node constraints
        doc_filter = {"document_id": {"$in": [str(d) for d in target_doc_ids]}} if len(target_doc_ids) > 1 else {"document_id": str(target_doc_ids[0])}
        
        and_conditions = [
            {"workspace_id": str(workspace_id)},
            doc_filter
        ]

        if target_nav_nodes:
            and_conditions.append({"navigation_node": {"$in": [str(n) for n in target_nav_nodes]}})

        where_filter = {"$and": and_conditions}

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
                    where=where_filter # 🚀 ChromaDB now restricts search strictly inside the V2 Navigation Node!
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
                                "page_number": meta.get("page_number", 1),
                                "navigation_node": meta.get("navigation_node", "N_UNKNOWN")
                            })
            except Exception as e:
                print(f"⚠️ Fast vector query error: {e}")

        # Fallback if strict navigation node scoping yields nothing (optional safety net)
        if not all_recovered_chunks and target_nav_nodes:
            print("⚠️ V2 Node-scoped query returned zero chunks. Retrying without navigation node constraint...")
            filters["target_navigation_nodes"] = []
            return self.execute_hybrid_retrieval(query_vector, workspace_id, filters)

        # Rest of your section reconstruction and deduplication code...
        return self._deduplicate_and_rerank(all_recovered_chunks)

    def _deduplicate_and_rerank(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_chunks = set()
        unique_sections = []
        for sec in sections:
            content_key = sec["content"].strip()
            if content_key not in seen_chunks:
                seen_chunks.add(content_key)
                unique_sections.append(sec)
        return unique_sections