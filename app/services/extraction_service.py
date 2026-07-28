import os
import json
from google import genai
from typing import Dict, Any

def get_intelligence_client() -> genai.Client:
    """Initializes and returns the official Google GenAI Client using system environment keys."""
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Neither INTELLIGENCE_LAYER_API_KEY nor GEMINI_API_KEY environment variables are configured.")
    return genai.Client(api_key=gemini_key)

class ExtractionService:
    """
    Component 6: Knowledge Enrichment AI (Gemini Call #2)
    Receives pre-bounded navigation chunks and enriches them with semantic metadata,
    entities, search hints, and question patterns. Chunking is already finished.
    """
    def __init__(self):
        self.client = get_intelligence_client()

    def enrich_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        system_instruction = (
            "You are the Knowledge Enrichment AI for AgentPulse V2.\n"
            "Chunking and structural boundary mapping are already completed by Python code.\n"
            "Your ONLY responsibility is to analyze the provided chunk text along with its navigation context "
            "(Topic and Subtopic) and output rich semantic metadata including a summary, entities, keywords, "
            "question patterns, and search terms in clean JSON format."
        )

        prompt = (
            f"Enrich the following bounded chunk:\n\n"
            f"Topic: {chunk_data.get('topic')}\n"
            f"Subtopic: {chunk_data.get('subtopic')}\n"
            f"Chunk Text:\n{chunk_data.get('chunk_text')}"
        )

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )

        try:
            enrichment_metadata = json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Enrichment JSON parse warning: {e}")
            enrichment_metadata = {
                "summary": chunk_data.get('chunk_text')[:150],
                "entities": [],
                "keywords": [],
                "question_patterns": [],
                "search_terms": []
            }

        return {
            **chunk_data,
            "enrichment": enrichment_metadata
        }