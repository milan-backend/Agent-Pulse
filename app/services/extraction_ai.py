import os
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional


class ExtractedEntitySchema(BaseModel):
    name: str = Field(description="Name of the technical concept, module, rule, or system.")
    category: str = Field(description="Category e.g., 'API', 'Database', 'Policy', 'Security', 'Process'.")
    description: str = Field(description="Brief summary or definition of the entity.")


class EntityRelationshipSchema(BaseModel):
    source_entity: str = Field(description="Name of the source entity.")
    target_entity: str = Field(description="Name of the target entity.")
    relationship_type: str = Field(description="Relationship type e.g., 'depends_on', 'part_of', 'triggers', 'extends'.")


class SectionKnowledgeExtractionSchema(BaseModel):
    telemetry_summary: str = Field(description="1 to 2 sentence data-dense summary of what main concepts this text block contains.")
    entities: List[ExtractedEntitySchema] = Field(default_factory=list)
    relationships: List[EntityRelationshipSchema] = Field(default_factory=list)


def get_intelligence_client() -> genai.Client:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Neither INTELLIGENCE_LAYER_API_KEY nor GEMINI_API_KEY environment variables are configured.")
    return genai.Client(api_key=gemini_key)


def run_section_knowledge_extraction(
    section_title: str, 
    section_text: str, 
    client: Optional[genai.Client] = None
) -> SectionKnowledgeExtractionSchema:
    """
    Extraction AI: Extracts telemetry summary, domain entities, and entity relationships 
    from section text blocks to populate PostgreSQL knowledge graph tables.
    """
    if client is None:
        client = get_intelligence_client()

    system_instruction = (
        "You are the Core Knowledge & Entity Extraction AI for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "Analyze the provided section text to extract:\n"
        "1. A concise 1-2 sentence telemetry_summary summarizing key topics inside.\n"
        "2. Key domain entities (concepts, systems, modules, rules) with categories and descriptions.\n"
        "3. Semantic relationships connecting extracted entities (e.g., 'JWT Auth' -> depends_on -> 'User Table').\n"
    )

    prompt = f"SECTION TITLE: {section_title}\n\nSECTION TEXT:\n{section_text[:4000]}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": SectionKnowledgeExtractionSchema,
            "temperature": 0.1
        }
    )

    return SectionKnowledgeExtractionSchema.model_validate_json(response.text)