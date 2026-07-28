import os
from google import genai
from typing import Dict, Any

def get_intelligence_client() -> genai.Client:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Missing Gemini API keys for Navigation AI.")
    return genai.Client(api_key=gemini_key)

class NavigationAI:
    """
    Component 4: Navigation AI (Gemini Call #1)
    Takes the Document DNA and constructs the official hierarchical Navigation Map.
    """
    def __init__(self):
        self.client = get_intelligence_client()

    def build_navigation_map(self, document_dna: Dict[str, Any]) -> Dict[str, Any]:
        system_instruction = (
            "You are the Core Navigation Architect for AgentPulse V2.\n"
            "Your ONLY responsibility is to analyze the provided Document DNA and output a clean, "
            "hierarchical navigation map consisting of major nodes, titles, exact page ranges, and subtopics.\n"
            "Do NOT create chunks, extract entities, or summarize content. Build the structural roadmap only."
        )

        prompt = f"Construct the hierarchical Navigation Map for this document DNA:\n\n{document_dna}"

        # Using standard lightweight Gemini model for fast structured generation
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )

        import json
        try:
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Navigation Map JSON parse warning: {e}")
            return {"document_title": document_dna.get("document_title", "Unknown"), "navigation": []}