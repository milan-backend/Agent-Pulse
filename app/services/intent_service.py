import os
from google import genai
from pydantic import BaseModel, Field
from typing import List

# =====================================================================
# 📊 Pydantic Structural Schema for Open-World Intent Intelligence
# =====================================================================

class IntentAnalysisSchema(BaseModel):
    intent_type: str = Field(
        description="The strategy classification of what the user is trying to achieve. Prefer labels like "
                    "'Business Health Assessment', 'Compliance Verification', 'Operational Audit', 'Direct Lookup'. "
                    "If the query is specialized, output a dynamic, descriptive tag summarizing the core objective."
    )
    main_topic: str = Field(
        description="The primary core subject, domain, or core asset identity the user is asking about, "
                    "e.g., 'Business Performance', 'Leave Policy', 'Cloud Infrastructure'."
    )
    target_role_preference: str = Field(
        description="The strategic document tier most likely to hold the substance of this query role. Prefer standard roles: "
                    "'Evidence', 'Decision Making', 'Compliance', 'Supporting Context'. "
                    "If a custom role fits better, provide that value."
    )
    implied_time_scope: str = Field(
        description="The target chronological frame requested by the user, e.g., 'Q2 2026', 'Annual', 'Historical', 'Future Plan'. "
                    "If the prompt does not target a specific date frame, return 'Unspecified'."
    )
    target_departments: List[str] = Field(
        description="List of organizational corporate divisions or areas most likely to hold this data scope, "
                    "e.g., ['Finance'], ['HR'], ['Engineering']. Returns empty array if universal."
    )
    search_rationale: str = Field(
        description="A brief explanation for the downstream Retrieval Planner explaining *why* this filtering strategy "
                    "was selected and what specific objective the user is trying to accomplish."
    )


# =====================================================================
# 🚀 Intent Understanding Service Function
# =====================================================================

def analyze_user_query_intent(user_prompt: str) -> IntentAnalysisSchema:
    """
    Component 4 Intent Understanding AI: Analyzes raw user strings and compiles a deep, 
    structured, domain-agnostic lookup framework for the upstream Planner.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME BREAKDOWN: INTELLIGENCE_LAYER_API_KEY environment variable is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    system_instruction = (
        "You are the Core Strategic Intent Analyst for the AgentPulse Retrieval Layer.\n\n"
        "🎯 MISSION OBJECTIVE:\n"
        "Your generated output will be consumed directly by an automated Retrieval Planner to determine the logical scope of "
        "the retrieval. Your only goal is to dissect human phrasing and translate it into a clear target objective. Do NOT attempt "
        "to expand keywords or guess related terms; the downstream knowledge graph handles conceptual connections.\n\n"
        "⚠️ BEHAVIORAL CONSTRAINTS:\n"
        "- Focus entirely on diagnosing WHAT the user is trying to achieve rather than trying to perform keyword generation.\n"
        "- Do NOT limit yourself to a rigid set of labels. If a user query requires specialized routing (e.g., medical diagnostics, "
        "software codebase debugging, architectural blueprints), output dynamic, descriptive categories for intent, roles, and departments."
    )
    
    response = client.models.generate_content(
        model="gemini-3.0-flash",
        contents=f"Analyze the following user question string and extract its target search intent schema:\n\n{user_prompt}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": IntentAnalysisSchema,
            "temperature": 0.0  # Absolute zero ensures deterministic query mapping structure
        }
    )
    
    return IntentAnalysisSchema.model_validate_json(response.text)