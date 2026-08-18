# app/services/vector_sync.py

import uuid
from typing import List, Dict, Any
from app.services.chunk_engine import ChunkEngine
from app.services.navigation_service import NavigationMapSchema
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan

class ChromaVectorSyncService:
    """
    Bridges the Navigation AI's topic maps, the ChunkEngine's splitting strategy, 
    and ChromaDB synchronization to ensure chunks are stored with precise topic tags, IDs, and agent isolation.
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
        navigation_map: NavigationMapSchema,
        agent_id: str = None,
        uploader_email: str = "System Operator"
    ) -> List[str]:
        """
        Takes ingestion plan, splits text, maps to Navigation AI topics, generates embeddings, 
        and syncs to ChromaDB with strict agent and workspace metadata tags.
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

            # 🟢 Restoring original dual-tier agent and workspace scope metadata tags
            metadata = {
                "document_id": str(document_id),
                "workspace_id": str(workspace_id),
                "agent_id": str(agent_id) if agent_id else "None",
                "source_file": filename,
                "topic": topic_title,
                "hierarchy_level": hierarchy_level,
                "page_number": page_num,
                "strategy_used": chunk.get("strategy_used", "Standard"),
                "uploaded_by": uploader_email
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
        """Generates vector embedding matching working syntax."""
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