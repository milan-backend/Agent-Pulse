import os
from google import genai
from pydantic import BaseModel
from typing import List, Optional

class ExtractedEntitySchema(BaseModel):
    name: str
    category: str
    description: str

class EntityRelationshipSchema(BaseModel):
    source_entity: str
    target_entity: str
    relationship_type: str

class SectionKnowledgeExtractionSchema(BaseModel):
    telemetry_summary: str
    entities: List[ExtractedEntitySchema] = []
    relationships: List[EntityRelationshipSchema] = []

def get_intelligence_client() -> genai.Client:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: API keys are not configured.")
    return genai.Client(api_key=gemini_key)

def run_section_knowledge_extraction(
    section_title: str, 
    section_text: str, 
    client: Optional[genai.Client] = None
) -> SectionKnowledgeExtractionSchema:
    if client is None:
        client = get_intelligence_client()

    system_instruction = (
        "You are the Core Knowledge & Entity Extraction AI for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "Analyze the provided section text to extract:\n"
        "1. A concise 1-2 sentence telemetry_summary summarizing key topics inside.\n"
        "2. Key domain entities (concepts, systems, modules, rules) with categories and descriptions.\n"
        "3. Semantic relationships connecting extracted entities (e.g., 'JWT Auth' -> depends_on -> 'User Table').\n\n"
        "⚠️ STRICT OUTPUT FORMAT:\n"
        "You must return ONLY a raw JSON object matching this exact structure. Do not include markdown formatting.\n"
        "{\n"
        '  "telemetry_summary": "Summary string here",\n'
        '  "entities": [\n'
        '    {"name": "Entity Name", "category": "Category", "description": "Desc"}\n'
        '  ],\n'
        '  "relationships": [\n'
        '    {"source_entity": "Name", "target_entity": "Name", "relationship_type": "depends_on"}\n'
        '  ]\n'
        "}"
    )

    prompt = f"SECTION TITLE: {section_title}\n\nSECTION TEXT:\n{section_text[:4000]}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    )

    return SectionKnowledgeExtractionSchema.model_validate_json(response.text)