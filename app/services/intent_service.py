import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

# =====================================================================
# Pydantic Structural Schema for Open-World Intent Intelligence
# =====================================================================

class IntentAnalysisSchema(BaseModel):
    intent_type: str = Field(
        description="The strategy classification of what the user is trying to achieve. Prefer labels like "
                    "'Business Health Assessment', 'Compliance Verification', 'Operational Audit', 'Direct Lookup', 'Process Explanation'."
    )
    main_topic: str = Field(
        description="The primary core subject or domain, e.g., 'Attendance Policy', 'Leave Policy', 'Examination Rules'."
    )
    target_topic: str = Field(
        description="The specific hierarchical document topic being targeted based on the query."
    )
    target_subtopic: str = Field(
        description="The specific subtopic or section within the document being targeted."
    )
    
    # DEPTH CONTROL FIELDS
    retrieval_depth: str = Field(
        description="Granularity/depth of information required. MUST be one of: ['Shallow', 'Medium', 'Deep']. "
                    "'Shallow': Direct 1-fact lookup. 'Medium': Fact + immediately related context. 'Deep': Multi-step process, policy chain, or full workflow."
    )
    include_concept_chains: bool = Field(
        description="Set to True if answering the question requires traversing relationship chains."
    )
    max_relationship_hops: int = Field(
        description="The maximum number of relationship hops required (0 for direct lookup, up to 3 for deep workflows)."
    )
    depth_reasoning: str = Field(
        description="Brief justification for why this depth and hop count were chosen."
    )

    target_role_preference: str = Field(
        description="The strategic document tier most likely to hold the substance of this query role."
    )
    implied_time_scope: str = Field(
        description="The target chronological frame, e.g., 'Q2 2026', 'Annual', 'Historical', 'Unspecified'."
    )
    target_departments: List[str] = Field(
        description="List of organizational corporate divisions. Returns empty array if universal."
    )
    search_rationale: str = Field(
        description="Explanation for downstream Retrieval Planner on why this filtering and depth strategy was selected."
    )


# =====================================================================
# Intent Understanding Service Function
# =====================================================================

def analyze_user_query_intent(user_prompt: str) -> IntentAnalysisSchema:
    """
    Component Intent Understanding AI: Analyzes user queries and outputs a structured lookup blueprint
    including V2 navigation topic targets and retrieval depth boundaries using Gemini models[cite: 5].
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: API key for Intent Intelligence is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    system_instruction = (
        "You are the Core Strategic Intent & Navigation Analyst for AgentPulse V2.\n\n"
        "MISSION OBJECTIVE:\n"
        "Dissect human user questions and determine target topics, subtopics, search context targets, "
        "and retrieval depth requirements for navigating structured document trees.\n\n"
        "DEPTH CONTROL RULES:\n"
        "1. Shallow (Hops = 0, Concept Chains = False): For direct single-fact questions.\n"
        "2. Medium (Hops = 1, Concept Chains = True/False): For queries needing a fact + immediate context.\n"
        "3. Deep (Hops = 2-3, Concept Chains = True): For end-to-end workflows or complex policies.\n"
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Analyze the following user question and extract its intent, V2 navigation targets, and depth control schema:\n\n{user_prompt}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": IntentAnalysisSchema,
            "temperature": 0.0
        }
    )
    
    return IntentAnalysisSchema.model_validate_json(response.text)