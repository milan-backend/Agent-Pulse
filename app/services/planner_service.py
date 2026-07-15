import os
from google import genai
from pydantic import BaseModel, Field
from typing import List
from app.services.intent_service import IntentAnalysisSchema

# =====================================================================
# 📊 Pydantic Structural Blueprint For Routing Engine Output
# =====================================================================

class DocumentRouteSelection(BaseModel):
    document_id: str = Field(description="The UUID string of the chosen document.")
    reason: str = Field(description="Why this specific file is chosen to answer the query.")

class RetrievalBlueprintSchema(BaseModel):
    selected_documents: List[DocumentRouteSelection] = Field(description="Target files to vector search. Empty if no match.")
    vector_search_terms: List[str] = Field(description="Search terms mapping to the investigation.")
    prefer_latest: bool = Field(default=True)
    prefer_approved: bool = Field(default=True)
    max_chunks: int = Field(default=10)
    planner_notes: str = Field(description="Strategic notes explaining the combined routing strategy.")


# =====================================================================
# 🚀 The Retrieval Planner AI Execution Service
# =====================================================================

def execute_retrieval_planning_triage(
    user_prompt: str,
    intent_strategy: IntentAnalysisSchema,
    lightweight_candidates: List[dict]
) -> RetrievalBlueprintSchema:
    """
    Component 4: Planner AI
    Uses rich structured Intent Analysis context alongside lightweight candidate profiles
    to make an optimal data routing decision. Never reads full text or answers the query.
    """
    if not lightweight_candidates:
        return RetrievalBlueprintSchema(
            selected_documents=[], 
            vector_search_terms=[], 
            max_chunks=10,
            planner_notes="No candidate profiles reached the planner tier."
        )

    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: INTELLIGENCE_LAYER_API_KEY environment variable is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    # Format lightweight candidates context block
    formatted_candidates = []
    for doc in lightweight_candidates:
        formatted_candidates.append(
            f"📄 [DOCUMENT ID: {doc['id']}]\n"
            f" - Type: {doc['document_type']} | Role: {doc['document_role']}\n"
            f" - Scores -> Authority: {doc['authority_score']} | Importance: {doc['importance_score']} | Freshness: {doc['freshness']}\n"
            f" - Planner Summary: {doc['planner_summary']}\n"
            f" - Questions This Document Can Answer: {doc['questions_this_document_can_answer']}\n"
            f"--------------------------------------------------"
        )
    candidates_context_block = "\n".join(formatted_candidates)
    
    system_instruction = (
        "You are the Core Director of the AgentPulse Retrieval Planner AI Layer.\n\n"
        "🎯 MISSION OBJECTIVE:\n"
        "Your task is to review the highly structured INTENT ANALYSIS and a small set of pre-filtered candidate document profiles "
        "to construct a high-precision Retrieval Blueprint. Do NOT re-do the intent analysis; use the provided strategy parameters.\n\n"
        "⚠️ PLANNING CONSTRAINTS:\n"
        "- Select only the exact document IDs that have the definitive capability to answer the user query.\n"
        "- Match your selection against the 'Preferred Role', 'Time Scope', and 'Questions This Document Can Answer' metrics.\n"
        "- Output a comprehensive set of vector search terms to guide the downstream retrieval engine."
    )
    
    # 🎯 CORRECTION: Full intentional injection of the complete Intent Analysis schema footprint
    prompt_payload = (
        f"USER QUESTION\n"
        f"\"{user_prompt}\"\n"
        f"---------------------------------\n\n"
        f"INTENT ANALYSIS\n"
        f" - Intent Type: {intent_strategy.intent_type}\n"
        f" - Main Topic: {intent_strategy.main_topic}\n"
        f" - Preferred Role: {intent_strategy.target_role_preference}\n"
        f" - Departments: {', '.join(intent_strategy.target_departments) if intent_strategy.target_departments else 'Universal'}\n"
        f" - Time Scope: {intent_strategy.implied_time_scope}\n"
        # Optional field check to prevent attribute failure bugs if naming maps dynamically
        f" - Expanded Keywords: {', '.join(getattr(intent_strategy, 'expanded_search_keywords', []))}\n"
        f"---------------------------------\n\n"
        f"CANDIDATE DOCUMENTS\n"
        f"==================================================\n"
        f"{candidates_context_block}\n"
        f"=================================================="
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_payload,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": RetrievalBlueprintSchema,
            "temperature": 0.0
        }
    )
    return RetrievalBlueprintSchema.model_validate_json(response.text)