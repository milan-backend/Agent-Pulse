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
        description="Brief reasoning for why this depth was selected, why lower is insufficient, and why higher is unnecessary."
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
    "You are the Core Strategic Intent & Document Selection Analyst for AgentPulse.\n\n"

    "🎯 MISSION:\n"
    "Analyze the user's question and determine the exact retrieval plan for the Planner AI.\n"
    "Your analysis directly affects retrieval quality, latency, and token usage.\n"
    "Your goal is to produce a CONSISTENT retrieval plan for semantically identical questions.\n\n"

    "These candidates include relevance scores, extracted domain entities, and a full_navigation_map (Table of Contents).\n\n"

    "Your responsibilities are:\n"
    "1. Select the exact `target_document_ids` that actually contain the required information.\n"
    "2. Select `target_section_codes` ONLY from the provided full_navigation_map. Never invent section names.\n"
)
    
    # Convert the Python list of dicts to a formatted JSON string for the LLM prompt
    candidates_json = json.dumps(registry_candidates, indent=2)
    
    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"TOP REGISTRY CANDIDATES (WITH ENTITIES & SECTIONS):\n{candidates_json}"
    )

    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": IntentAnalysisSchema,
            "temperature": 0.0
        }
    )
    
    return IntentAnalysisSchema.model_validate_json(response.text)