# app/services/navigation_ai.py

import os
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
    maps out topics, sub-topics, and relationship suggestions without parsing raw pages.
    Flattens Pydantic schema references to prevent Gemini SDK $defs validation errors.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation Mapping AI for AgentPulse.\n"
        "MISSION: Read the provided local Python outline structure and build a clean, hierarchical "
        "NavigationMapSchema containing topics, sub-topics, hierarchy levels, and logical relationship suggestions "
        "to guide the chunk engine and planner AI."
    )

    # 🟢 Flatten schema definitions to ensure compatibility with Gemini structured outputs
    json_schema = NavigationMapSchema.model_json_schema(ref_template="{model}")
    if "$defs" in json_schema:
        defs = json_schema.pop("$defs", {})
        def inline_refs(schema_obj):
            if isinstance(schema_obj, dict):
                if "$ref" in schema_obj:
                    ref_name = schema_obj["$ref"].split("/")[-1]
                    if ref_name in defs:
                        resolved = defs[ref_name].copy()
                        schema_obj.clear()
                        schema_obj.update(resolved)
                for k, v in schema_obj.items():
                    inline_refs(v)
            elif isinstance(schema_obj, list):
                for item in schema_obj:
                    inline_refs(item)
        inline_refs(json_schema)

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Construct the navigation map from this outline structure:\n\n{navigation_payload}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": json_schema,
            "temperature": 0.0
        }
    )

    return NavigationMapSchema.model_validate_json(response.text)