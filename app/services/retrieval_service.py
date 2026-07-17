import os
from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

class RetrievalService:
    def __init__(self):
        # Connect using your newly migrated Render DB URL
        self.engine = create_engine(os.getenv("DATABASE_URL"))

    def execute_hybrid_retrieval(self, query_vector: List[float], workspace_id: UUID, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Main orchestration: Vector Search -> Filter -> Section Reconstruction -> Rerank
        """
        # 1. Simulate/Execute Chroma Vector Search to get core chunk hits
        # (Replace placeholder with your actual Chroma/Vector DB call)
        initial_chunks = self._vector_search(query_vector, workspace_id, filters)
        
        # 2. Section Reconstruction Pipeline
        reconstructed_sections = []
        for chunk in initial_chunks:
            # Reconstruct the parent section around this specific chunk hit
            section_data = self._reconstruct_section(chunk["document_id"], chunk["section_name"])
            if section_data:
                reconstructed_sections.append(section_data)
                
        # 3. Apply Reranking / Duplicate Chunk Elimination at structural level
        final_retrieved_context = self._deduplicate_and_rerank(reconstructed_sections)
        
        return final_retrieved_context

    def _vector_search(self, query_vector: List[float], workspace_id: UUID, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Placeholder for your Chroma Vector DB Query matching chunks"""
        # Returns matched chunk anchors containing document_id, section_name, and indices
        return []

    def _reconstruct_section(self, document_id: str, section_name: str) -> Dict[str, Any]:
        """
        🎯 SECTION RECONSTRUCTION MECHANISM
        Queries PostgreSQL to gather ALL sister chunks belonging to the same heading section.
        """
        if not section_name:
            return None
            
        query = text("""
            SELECT chunk_index, content 
            FROM document_chunks 
            WHERE document_id = :doc_id AND section_name = :sec_name
            ORDER BY chunk_index ASC;
        """)
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, {"doc_id": document_id, "sec_name": section_name})
                rows = [dict(row._mapping) for row in result]
                
                if not rows:
                    return None
                
                # Stitch the sister chunks sequentially to reconstruct unbroken text
                full_section_text = "\n".join([row["content"] for row in rows])
                
                return {
                    "document_id": document_id,
                    "section_name": section_name,
                    "content": full_section_text
                }
        except Exception as e:
            print(f"⚠️ Section reconstruction failed: {e}")
            return None

    def _deduplicate_and_rerank(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Removes duplicate sections caught by multiple internal chunk hits"""
        seen_sections = set()
        unique_sections = []
        
        for sec in sections:
            identifier = f"{sec['document_id']}_{sec['section_name']}"
            if identifier not in seen_sections:
                seen_sections.add(identifier)
                unique_sections.append(sec)
                
        return unique_sections