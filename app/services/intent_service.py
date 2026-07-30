import os
from google import genai
from pydantic import BaseModel, Field
from typing import List


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
    target_section_codes: List[str] = Field(
        description="List of section codes (e.g. ['1.1', '1.2']) from the Navigation Map that are likely relevant."
    )
    include_sibling_sections: bool = Field(
        description="True if query depth requires pulling neighboring sections/chunks."
    )
    max_relationship_hops: int = Field(
        description="Maximum relationship hops (0 for direct fact, 1 for immediate context, 2-3 for deep multi-step workflows)."
    )
    depth_reasoning: str = Field(
        description="Brief reasoning for why this depth and section target were selected."
    )


def analyze_user_query_intent(user_prompt: str, navigation_map_summary: str) -> IntentAnalysisSchema:
    """
    Component 4 Intent Understanding AI: Compares user prompt against the Document Navigation Map 
    to output target section codes and depth controls for downstream Planner AI.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: API key for Intent Intelligence is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    system_instruction = (
        "You are the Core Strategic Intent & Navigation Depth Analyst for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "Analyze human user questions against the provided Document Navigation Map (sections & codes).\n"
        "Identify target section codes (e.g., '1.1', '1.2') and determine retrieval depth:\n"
        "1. Shallow (Hops=0, include_sibling_sections=False): For direct single-fact lookups.\n"
        "2. Medium (Hops=1, include_sibling_sections=True): For fact + immediate surrounding context.\n"
        "3. Deep (Hops=2-3, include_sibling_sections=True): For end-to-end multi-section processes or policies.\n"
    )
    
    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"DOCUMENT NAVIGATION MAP:\n{navigation_map_summary}"
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