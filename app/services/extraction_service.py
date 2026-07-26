import os
from google import genai

# 🟢 SINGLE SOURCE OF TRUTH: Import Root Pydantic Schema for Ingestion Plan
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan


def get_intelligence_client() -> genai.Client:
    """Initializes and returns the official Google GenAI Client using system environment keys."""
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Neither INTELLIGENCE_LAYER_API_KEY nor GEMINI_API_KEY environment variables are configured.")
    return genai.Client(api_key=gemini_key)


def get_multi_zone_sample(full_text: str, max_chars: int = 40000) -> str:
    """
    Intelligently samples text across the entire document (Beginning, Middle, and End)
    to prevent blind spots in massive files while staying within token limits.
    """
    if not full_text or len(full_text) <= max_chars:
        return full_text
        
    third = max_chars // 3
    length = len(full_text)
    
    start_snippet = full_text[:third]
    mid_start = (length // 2) - (third // 2)
    mid_snippet = full_text[mid_start:mid_start + third]
    end_snippet = full_text[length - third:]
    
    return f"--- [DOCUMENT BEGINNING / TOC] ---\n{start_snippet}\n\n--- [DOCUMENT MIDDLE SECTION] ---\n{mid_snippet}\n\n--- [DOCUMENT ENDING / CONCLUSION] ---\n{end_snippet}"


def run_phase_1_knowledge_extraction(global_text_sample: str, client: genai.Client) -> KnowledgeIngestionPlan:
    """
    Phase 1 Extraction AI: Analyzes document structure, discovers dynamic metadata,
    extracts concept relationships with numeric strength scores (0.0 to 1.0), and 
    recommends an optimal chunking strategy to produce the KnowledgeIngestionPlan.
    """
    system_instruction = (
        "You are the Core Computational Extraction AI for the AgentPulse Ingestion Pipeline.\n\n"
        "🎯 RESPONSIBILITY:\n"
        "Analyze the provided document text sample to construct a complete KnowledgeIngestionPlan.\n"
        "Do NOT chunk the document. Do NOT create vector embeddings. Focus strictly on understanding structure, "
        "discovering dynamic key-value metadata, identifying concept relationships with strength scores (0.0 to 1.0), "
        "and recommending an optimal chunking strategy.\n\n"
        "⚠️ CONSTRAINTS & ALLOWED VALUES:\n"
        "- Chunking strategy MUST be one of: ['Section Based', 'Heading Based', 'Paragraph Based', 'Question Answer', 'Page Based', 'Semantic']\n"
        "- Recommended chunk_size MUST be between 500 and 1500.\n"
        "- Recommended overlap MUST be between 50 and 300.\n"
        "- Limit dynamic metadata key-value pairs to a maximum of 10 highly relevant items."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Analyze the following document context sample and build the KnowledgeIngestionPlan:\n\n{global_text_sample}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": KnowledgeIngestionPlan,
            "temperature": 0.1
        }
    )
    
    return KnowledgeIngestionPlan.model_validate_json(response.text)