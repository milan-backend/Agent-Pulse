import os
import json
from google import genai
from typing import List, Dict, Any

class GenerationService:
    """
    Component: Generation AI / Response Synthesis
    Takes decrypted context chunks and user query to generate a grounded,
    verified final response.
    """
    def __init__(self):
        gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("CRITICAL RUNTIME ERROR: Missing Gemini API keys for GenerationService.")
        self.client = genai.Client(api_key=gemini_key)
        self.model_name = "gemini-2.5-flash-lite"

    def synthesize_response(
        self, 
        user_prompt: str, 
        intent_strategy: Any, 
        recovered_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Synthesizes a response using strictly the decrypted context chunks in memory.
        """
        if not recovered_chunks:
            return "I searched the authorized document repositories and navigation nodes matching your query, but no relevant content chunks were found."

        # Format context blocks from decrypted chunks
        context_blocks = []
        for idx, chunk in enumerate(recovered_chunks):
            context_blocks.append(
                f"[CONTEXT CHUNK {idx + 1} | Source: {chunk.get('source_file', 'Unknown')} | Page: {chunk.get('page_number', 1)}]\n"
                f"{chunk.get('text', '')}\n"
                f"--------------------------------------------------"
            )
        combined_context = "\n".join(context_blocks)

        system_instruction = (
            "You are the Core Response Synthesis AI for AgentPulse V2.\n\n"
            "MISSION OBJECTIVE:\n"
            "Answer the user's question accurately, concisely, and exclusively using the provided decrypted context chunks. "
            "Never hallucinate or bring in outside information not supported by the text. "
            "If the answer cannot be found in the provided context, state that clearly."
        )

        prompt_payload = (
            f"USER QUESTION: \"{user_prompt}\"\n\n"
            f"INTENT CONTEXT & TARGET TOPIC: {getattr(intent_strategy, 'target_topic', 'General')}\n\n"
            f"VERIFIED DECRYPTED CONTEXT CHUNKS:\n"
            f"{combined_context}\n\n"
            f"Provide a clear, professional, and well-structured response based strictly on the above chunks."
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_payload,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.2
            }
        )

        return response.text