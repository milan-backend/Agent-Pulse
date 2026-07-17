import os
import chromadb
from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from app.models.uploaded_document import UploadedDocument

load_dotenv()

class RetrievalService:
    def __init__(self):
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        
        # 🟢 Initialize the HTTP Client connection to your Railway Chroma instance!
        chroma_host = str(os.getenv("CHROMA_HOST")).strip().rstrip("/")
        chroma_token = os.getenv("CHROMA_TOKEN")
        
        self.chroma_client = chromadb.HttpClient(
            host=chroma_host,
            headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
        )

    def execute_hybrid_retrieval(self, query_vector: List[float], workspace_id: UUID, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main orchestration: Vector Search -> Section Reconstruction -> Deduplicate
        """
        # 1. Pull core anchor chunks from ChromaDB[cite: 4]
        initial_chunks = self._vector_search(workspace_id, filters)
        
        # 2. Section Reconstruction Pipeline[cite: 4]
        reconstructed_sections = []
        for chunk in initial_chunks:
            # Reconstruct the section using the source file identifier
            section_data = self._reconstruct_section(chunk["document_id"], chunk["source_file"])
            if section_data:
                reconstructed_sections.append(section_data)
                
        # 3. Clean up duplicates[cite: 4]
        return self._deduplicate_and_rerank(reconstructed_sections)

    def _vector_search(self, workspace_id: UUID, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Queries your cloud-native ChromaDB collection to get text matches"""
        try:
            collection = self.chroma_client.get_collection(name="rag_enterprise_vectors_v1")
            target_ids = filters.get("document_ids", [])
            
            # Retrieve data fragments using collection lookup
            results = collection.get(
                where={
                    "$and": [
                        {"workspace_id": str(workspace_id)},
                        {"document_id": {"$in": target_ids}}
                    ]
                }
            )
            
            metadatas = results.get("metadatas", []) or []
            
            extracted_anchors = []
            for meta in metadatas:
                extracted_anchors.append({
                    "document_id": meta.get("document_id"),
                    "source_file": meta.get("source_file")
                })
            return extracted_anchors
        except Exception as e:
            print(f"⚠️ Chroma lookup variance: {e}")
            return []

    def _reconstruct_section(self, document_id: str, source_file: str) -> Dict[str, Any]:
        """
        🎯 SECTION RECONSTRUCTION FROM CHROMADB
        Gathers all chunks belonging to the document directly out of ChromaDB.
        """
        try:
            collection = self.chroma_client.get_collection(name="rag_enterprise_vectors_v1")
            
            # Pull all 3 chunks for this document out of ChromaDB at once!
            results = collection.get(
                where={
                    "$and": [
                        {"document_id": str(document_id)},
                        {"source_file": str(source_file)}
                    ]
                }
            )
            
            # Collect and decode the encrypted text segments from Chroma
            from app.core.rag_crypto import decrypt_text_string
            from app.db.session import get_db
            
            db = next(get_db())
            doc_record = db.query(UploadedDocument).filter(UploadedDocument.id == document_id).first()
            
            plain_texts = []
            for enc_doc in results.get("documents", []):
                decrypted = decrypt_text_string(enc_doc, doc_record.workspace_id)
                if decrypted:
                    plain_texts.append(decrypted)
            
            if not plain_texts:
                return None
                
            # Stitch all text fragments back together seamlessly!
            full_section_text = "\n".join(plain_texts)
            
            return {
                "document_id": document_id,
                "section_name": "Environment",  # Set fallback header context
                "content": full_section_text
            }
        except Exception as e:
            print(f"⚠️ Section stitching failed: {e}")
            return None

    def _deduplicate_and_rerank(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen_docs = set()
        unique_sections = []
        for sec in sections:
            if sec["document_id"] not in seen_docs:
                seen_docs.add(sec["document_id"])
                unique_sections.append(sec)
        return unique_sections