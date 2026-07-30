import os
from google import genai
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan

def get_intelligence_client() -> genai.Client:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Neither INTELLIGENCE_LAYER_API_KEY nor GEMINI_API_KEY are configured.")
    return genai.Client(api_key=gemini_key)

def run_phase_1_knowledge_extraction(extraction_payload: dict, client: genai.Client) -> KnowledgeIngestionPlan:
    """
    Phase 1 Extraction AI: Receives clean Python-extracted summary snippets and 
    generates the KnowledgeIngestionPlan (entities, metadata, and chunking strategy).
    """
    summary_text = extraction_payload.get("summary_text", "")

    system_instruction = (
        "You are the Core Computational Extraction AI for the AgentPulse Ingestion Pipeline.\n\n"
        "RESPONSIBILITY:\n"
        "Analyze the provided Python-extracted document summary snippet to construct a complete KnowledgeIngestionPlan.\n"
        "Focus strictly on understanding structure, discovering dynamic key-value metadata, identifying concept "
        "relationships with strength scores (0.0 to 1.0), and recommending an optimal chunking strategy.\n\n"
        "CONSTRAINTS & ALLOWED VALUES:\n"
        "- Chunking strategy MUST be one of: ['Section Based', 'Heading Based', 'Paragraph Based', 'Question Answer', 'Page Based', 'Semantic']\n"
        "- Recommended chunk_size MUST be between 400 and 1000.\n"
        "- Recommended overlap MUST be between 100 and 200.\n"
        "- Limit dynamic metadata key-value pairs to a maximum of 10 highly relevant items."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Analyze the following pre-parsed document context and build the KnowledgeIngestionPlan:\n\n{summary_text}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": KnowledgeIngestionPlan,
            "temperature": 0.1
        }
    )
    
    return KnowledgeIngestionPlan.model_validate_json(response.text)