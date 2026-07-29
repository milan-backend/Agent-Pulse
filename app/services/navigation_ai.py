import os
import json
from google import genai
from typing import Dict, Any

def get_intelligence_client() -> genai.Client:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Missing Gemini API keys for Navigation AI.")
    return genai.Client(api_key=gemini_key)

class NavigationAI:
    """
    Component: Navigation AI 
    Takes document data/DNA and constructs the official hierarchical Navigation Map using Gemini[cite: 4].
    """
    def __init__(self):
        self.client = get_intelligence_client()

    def build_navigation_map(self, document_dna: Dict[str, Any]) -> Dict[str, Any]:
        system_instruction = (
            "You are the Core Navigation Architect for AgentPulse V2.\n"
            "Your ONLY responsibility is to analyze the provided Document DNA and output a clean, "
            "hierarchical navigation map consisting of major nodes, titles, exact page ranges, and subtopics in valid JSON format[cite: 4].\n"
            "Ensure the JSON structure contains a 'navigation' array where each object has 'node_id', 'title' (or 'topic'), 'pages' (or 'page_range'), and 'subtopics'."
        )

        prompt = f"Construct the hierarchical Navigation Map for this document DNA:\n\n{document_dna}"

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
            return json.loads(response.text)
        except Exception as e:
            print(f"⚠️ Navigation Map JSON parse warning: {e}")
            return {"document_title": document_dna.get("document_title", "Unknown"), "navigation": []}