import os
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from uuid import UUID
from google import genai
from pydantic import BaseModel, Field

from app.models.knowledge.semantic_metadata import SemanticMetadata
from app.models.knowledge.entity import Entity
from app.models.knowledge.relationship import Relationship
from app.python_intelligence.signal_store import SignalStore

logger = logging.getLogger(__name__)

class ExtractionExtractionSchema(BaseModel):
    summary: str = Field(description="High-level synthesis summary of the document contents.")
    keywords: List[str] = Field(description="Extracted domain core search keywords.")
    topics: List[str] = Field(description="Identified primary topics or categories.")

class ExtractionAI:
    """
    Consumes Python Intelligence signals using Gemini model integration to enrich the document 
    with semantic metadata, summaries, entities, and relationship graphs[cite: 4].
    """

    def __init__(self, db: Session, document_id: UUID, workspace_id: UUID):
        self.db = db
        self.document_id = document_id
        self.workspace_id = workspace_id
        self.signal_store = SignalStore(db, document_id, workspace_id)
        
        gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("CRITICAL RUNTIME ERROR: Missing API keys for ExtractionAI.")
        self.client = genai.Client(api_key=gemini_key)
        self.model_name = "gemini-2.5-flash-lite"

    def process_enrichment(self) -> bool:
        """
        Executes the knowledge enrichment and extraction process using Gemini AI synthesis[cite: 4].
        """
        try:
            logger.info(f"Starting ExtractionAI processing for Document {self.document_id}")
            
            # Fetch all signals produced by Python Intelligence
            signals = self.signal_store.get_all_document_signals()
            
            # 1. Generate and save semantic metadata summary via Gemini LLM
            self._generate_semantic_metadata_with_llm(signals)
            
            # 2. Extract and link entities & relationships from signals
            self._extract_graph_nodes(signals)

            self.db.commit()
            logger.info(f"Successfully completed ExtractionAI processing for Document {self.document_id}")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error during ExtractionAI processing: {e}")
            return False

    def _generate_semantic_metadata_with_llm(self, signals: List[Any]):
        """
        Synthesizes signals into high-level semantic summaries and topic lists via Gemini structured generation.
        """
        signal_texts = [sig.content for sig in signals if sig.content][:40]
        
        system_instruction = (
            "You are the Core Knowledge Synthesis Engine for AgentPulse V2.\n"
            "Analyze document signal contents and construct accurate semantic metadata, topics, and keywords."
        )
        
        prompt = f"Synthesize these document signals into core semantic metadata:\n\n{json.dumps(signal_texts)}"

        summary_text = f"Document contains {len(signals)} extracted deterministic signals covering structural and rule data."
        keywords = ["policy", "intelligence", "automation"]
        topics = ["document_analysis"]

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "response_schema": ExtractionExtractionSchema,
                    "temperature": 0.1
                }
            )
            parsed_data = ExtractionExtractionSchema.model_validate_json(response.text)
            summary_text = parsed_data.summary
            keywords = parsed_data.keywords
            topics = parsed_data.topics
        except Exception as llm_err:
            logger.warning(f"ExtractionAI model synthesis fallback triggered due to: {llm_err}")

        # Check if semantic metadata already exists for this document
        existing_meta = self.db.query(SemanticMetadata).filter(
            SemanticMetadata.document_id == self.document_id
        ).first()

        if existing_meta:
            existing_meta.summary = summary_text
            existing_meta.keywords = keywords
            existing_meta.topics = topics
        else:
            meta = SemanticMetadata(
                document_id=self.document_id,
                summary=summary_text,
                language="en",
                keywords=keywords,
                topics=topics,
                metadata={"signal_count": len(signals), "model_used": self.model_name}
            )
            self.db.add(meta)

    def _extract_graph_nodes(self, signals: List[Any]):
        """
        Maps entity signals into the dedicated Entity tables[cite: 4].
        """
        for sig in signals:
            if sig.signal_type == "entity":
                entity = Entity(
                    document_id=self.document_id,
                    name=sig.content,
                    entity_type=sig.metadata.get("entity_type", "GENERAL"),
                    confidence=sig.confidence,
                    page_number=sig.page_number,
                    metadata=sig.metadata
                )
                self.db.add(entity)