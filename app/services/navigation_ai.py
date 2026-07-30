# app/services/navigation_ai.py

import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List

class NavigationTopicNode(BaseModel):
    title: str = Field(description="Topic or sub-topic title.")
    hierarchy_level: int = Field(description="Nesting level (1 for main chapter, 2 for sub-topic, etc.)")
    page_number: int = Field(description="Associated page number from outline.")
    relationship_suggestions: List[str] = Field(description="Suggested downstream relationship targets or child topics.")

class NavigationMapSchema(BaseModel):
    document_title: str
    nodes: List[NavigationTopicNode] = Field(description="Complete hierarchical map of topics and sub-topics.")


def generate_navigation_map(navigation_payload: dict) -> NavigationMapSchema:
    """
    Navigation AI Service: Takes Python-extracted structural outline payload and 
    maps out topics, sub-topics, and relationship suggestions safely.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation Mapping AI for AgentPulse.\n"
        "MISSION: Read the provided local Python outline structure and build a clean, hierarchical "
        "JSON object containing 'document_title' (string) and 'nodes' (array of objects with 'title', 'hierarchy_level', 'page_number', and 'relationship_suggestions')."
    )

    # 🟢 By dropping response_schema and enforcing JSON via system prompt + mime type, 
    # we completely bypass Pydantic extra_forbidden validation errors in the Gemini SDK.
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Construct the navigation map JSON from this outline structure:\n\n{navigation_payload}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    try:
        parsed_data = json.loads(response.text)
        return NavigationMapSchema.model_validate(parsed_data)
    except Exception as parse_err:
        print(f"⚠️ Navigation Map JSON fallback parsing warning: {parse_err}")
        return NavigationMapSchema(
            document_title="Parsed Document",
            nodes=[NavigationTopicNode(title="General Content", hierarchy_level=1, page_number=1, relationship_suggestions=[])]
        )