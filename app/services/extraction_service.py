import os
from google import genai

# 🟢 1. Import your smart sampler module
from app.services.smart_sampler import analyze_pdf_structure, select_intelligent_pages
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan


def get_intelligence_client() -> genai.Client:
    """Initializes and returns the official Google GenAI Client using system environment keys."""
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: Neither INTELLIGENCE_LAYER_API_KEY nor GEMINI_API_KEY environment variables are configured.")
    return genai.Client(api_key=gemini_key)


def run_phase_1_knowledge_extraction(extracted_text: str, client: genai.Client) -> KnowledgeIngestionPlan:
    """
    Phase 1 Extraction AI: Runs local deterministic page inspection, builds a smart 
    token-budgeted sample window, and queries Gemini for the KnowledgeIngestionPlan.
    """
    # 🟢 2. Split text into pages locally (zero LLM tokens)
    pages_list = extracted_text.split("\f")
    if len(pages_list) <= 1:
        pages_list = [extracted_text[i:i+3000] for i in range(0, len(extracted_text), 3000)]

    # 🟢 3. Run local code analysis on structural metrics
    doc_stats = analyze_pdf_structure(pages_list)
    print(f"📊 Deterministic PDF Inspector Stats: {doc_stats}")

    # 🟢 4. Build smart sample under strict token budget
    global_text_sample = select_intelligent_pages(pages_list, max_token_budget=8000)

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