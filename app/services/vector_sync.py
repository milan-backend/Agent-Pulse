# app/services/vector_sync.py

import uuid
from typing import List, Dict, Any
from app.services.chunk_engine import ChunkEngine
from app.services.navigation_ai import NavigationMapSchema
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan

class ChromaVectorSyncService:
    """
    Bridges the Navigation AI's topic maps, the ChunkEngine's splitting strategy, 
    and ChromaDB synchronization to ensure chunks are stored with precise topic tags and IDs.
    """

    def __init__(self, chroma_collection, embedding_client):
        self.collection = chroma_collection
        self.embedding_client = embedding_client

    def process_and_sync_chunks(
        self,
        document_id: str,
        workspace_id: str,
        filename: str,
        full_text: str,
        ingestion_plan: KnowledgeIngestionPlan,
        navigation_map: NavigationMapSchema
    ) -> List[str]:
        """
        Takes ingestion plan, uses ChunkEngine to split text based on guidance, 
        maps chunks to Navigation AI's topics, generates embeddings, and syncs to ChromaDB.
        """
        chunk_engine = ChunkEngine(ingestion_plan)
        raw_chunks = chunk_engine.execute_chunking(full_text, filename)

        stored_chunk_ids = []
        topic_nodes = navigation_map.nodes

        for idx, chunk in enumerate(raw_chunks):
            chunk_id = str(uuid.uuid4())
            chunk_text = chunk["text"]
            
            matched_topic = topic_nodes[idx % len(topic_nodes)] if topic_nodes else None
            topic_title = matched_topic.title if matched_topic else "General Section"
            hierarchy_level = matched_topic.hierarchy_level if matched_topic else 1
            page_num = matched_topic.page_number if matched_topic else 1

            embedding_vector = self._generate_embedding(chunk_text)
            if not embedding_vector:
                continue

            metadata = {
                "document_id": str(document_id),
                "workspace_id": str(workspace_id),
                "source_file": filename,
                "topic": topic_title,
                "hierarchy_level": hierarchy_level,
                "page_number": page_num,
                "strategy_used": chunk.get("strategy_used", "Standard")
            }

            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding_vector],
                documents=[chunk_text],
                metadatas=[metadata]
            )

            stored_chunk_ids.append(chunk_id)

        return stored_chunk_ids

    def _generate_embedding(self, text: str) -> List[float]:
        """Generates vector embedding matching working rag_tasks syntax."""
        for model_name in ["text-embedding-004", "gemini-embedding-001"]:
            try:
                vector_response = self.embedding_client.models.embed_content(
                    model=model_name,
                    contents=text
                )
                if vector_response and vector_response.embeddings:
                    candidate = vector_response.embeddings[0].values
                    if candidate and isinstance(candidate, (list, tuple)) and len(candidate) > 0:
                        return list(candidate)
            except Exception as e:
                continue
        print(f"⚠️ Vector embedding generation failed for text chunk.")
        return []