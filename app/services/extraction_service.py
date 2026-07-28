import os
import json
from google import genai
from typing import List, Dict, Any

def get_intelligence_client() -> genai.Client:
    """Initializes and returns the official Google GenAI Client using system environment keys."""
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Missing Gemini API keys for Enrichment AI.")
    return genai.Client(api_key=gemini_key)

class ExtractionService:
    """
    Component 6: Knowledge Enrichment AI (Gemini Call #2) - Batch Capable
    """
    def __init__(self):
        self.client = get_intelligence_client()

    def enrich_chunks_batch(self, chunks_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches a batch of bounded chunks simultaneously to minimize API connection overhead.
        """
        formatted_chunks_input = []
        for idx, chunk in enumerate(chunks_batch):
            formatted_chunks_input.append(
                f"--- CHUNK ID: {idx} ---\n"
                f"Topic: {chunk.get('topic')}\n"
                f"Subtopic: {chunk.get('subtopic')}\n"
                f"Text:\n{chunk.get('chunk_text')}\n"
            )

        system_instruction = (
            "You are the Knowledge Enrichment AI for AgentPulse V2.\n"
            "You are receiving a batch of pre-bounded navigation chunks.\n"
            "For EACH chunk provided, output a JSON array containing objects with keys: "
            "'summary', 'entities', 'keywords', 'question_patterns', and 'search_terms'.\n"
            "Ensure the output JSON array length matches the exact number of input chunks."
        )

        prompt = "Enrich the following batch of chunks:\n\n" + "\n".join(formatted_chunks_input)

        try:
            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            )
            enrichment_results = json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Batch enrichment JSON parse warning: {e}")
            enrichment_results = []

        # Fallback mapping if batch response alignment fails
        enriched_output_pool = []
        for idx, chunk_data in enumerate(chunks_batch):
            meta = enrichment_results[idx] if idx < len(enrichment_results) else {
                "summary": chunk_data.get('chunk_text')[:150],
                "entities": [],
                "keywords": [],
                "question_patterns": [],
                "search_terms": []
            }
            enriched_output_pool.append({
                **chunk_data,
                "enrichment": meta
            })

        return enriched_output_pool