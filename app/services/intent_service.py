import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class IntentAnalysisSchema(BaseModel):
    intent_type: str = Field(
        description="Strategy classification e.g., 'Direct Lookup', 'Workflow Explanation', 'Compliance Check', 'Audit'."
    )
    main_topic: str = Field(
        description="The primary domain subject matter being asked about."
    )
    retrieval_depth: str = Field(
        description="Granularity/depth of information required. MUST be one of: ['Shallow', 'Medium', 'Deep']."
    )
    target_document_ids: List[str] = Field(
        description="List of document UUIDs selected from the candidate pool that are highly relevant to the query."
    )
    target_section_codes: List[str] = Field(
        description="List of section codes or titles from the selected documents that are likely relevant."
    )
    include_sibling_sections: bool = Field(
        description="True if query depth requires pulling neighboring sections/chunks."
    )
    max_relationship_hops: int = Field(
        description="Maximum relationship hops (0 for direct fact, 1 for immediate context, 2-3 for deep multi-step workflows)."
    )
    depth_reasoning: str = Field(
        description="Brief reasoning for why these specific documents, sections, and depths were selected."
    )


def analyze_user_query_intent(user_prompt: str, registry_candidates: List[Dict[str, Any]]) -> IntentAnalysisSchema:
    """
    Component 4 Intent Understanding AI (LLM-as-a-Judge): Evaluates the Registry Filter's top 
    document candidates (including their entities and sections) to determine exact targets.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: API key for Intent Intelligence is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    system_instruction = (
        "You are AgentPulse Intent Intelligence.\n\n"
        "Your responsibility is to understand the user's objective, not their wording.\n"
        "Ignore grammar, spelling, phrasing, and synonyms.\n"
        "Different questions with identical meaning must produce identical intent.\n\n"
        "Determine:\n"
        "• What information the user wants.\n"
        "• The scope of information required.\n"
        "• The minimum document scope capable of answering.\n\n"
        "Prefer logical parent sections over individual child sections whenever possible.\n\n"
        "Do not retrieve information.\n"
        "Do not answer the question.\n"
        "Do not infer facts.\n"
        "Only reason about user intent and document structure.\n\n"
        "Select only sections that directly satisfy the user's objective.\n"
        "Avoid over-selection.\n"
        "Avoid under-selection.\n\n"
        "Produce stable outputs.\n"
        "Equivalent questions should produce nearly identical intent regardless of wording."
    )
    
    # Convert the Python list of dicts to a formatted JSON string for the LLM prompt
    candidates_json = json.dumps(registry_candidates, indent=2)
    
    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"TOP REGISTRY CANDIDATES (WITH ENTITIES & SECTIONS):\n{candidates_json}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": IntentAnalysisSchema,
            "temperature": 0.0
        }
    )
    
    return IntentAnalysisSchema.model_validate_json(response.text)