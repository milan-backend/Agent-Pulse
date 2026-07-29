import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the schema from your actual intent service file
from app.services.intent_service import IntentAnalysisSchema

# =====================================================================
# Pydantic Structural Blueprint For Routing Engine Output
# =====================================================================

class RetrievalBlueprintSchema(BaseModel):
    selected_document_ids: List[str] = Field(
        description="UUIDs of the selected documents."
    )
    target_navigation_nodes: List[str] = Field(
        description="Specific V2 navigation node IDs to restrict search scope to (e.g. ['N1', 'N2']). Leave empty if global search across selected docs is required."
    )
    selection_reasons: List[str] = Field(
        description="Reason corresponding to each selected document."
    )
    vector_search_terms: List[str] = Field(
        description="Search phrases and concept keywords to query in ChromaDB."
    )
    
    # DEPTH ROUTING BLUEPRINT FIELDS
    relationship_traversal_hops: int = Field(
        description="Number of concept chain relationship hops to retrieve (0 to 3)."
    )
    max_chunks: int = Field(
        description="Calculated max chunk budget based on query depth."
    )
    prefer_latest: bool = True
    prefer_approved: bool = True
    planner_notes: str = Field(
        description="Summary of planning rationale including V2 navigation mapping and depth constraints."
    )


# =====================================================================
# The Retrieval Planner AI Execution Service
# =====================================================================

def execute_retrieval_planning_triage(
    user_prompt: str,
    intent_strategy: IntentAnalysisSchema,
    lightweight_candidates: List[dict]
) -> RetrievalBlueprintSchema:
    """
    Component Planner AI: Uses structured Intent Analysis alongside V2 document navigation maps
    to produce a precision-constrained Retrieval Blueprint[cite: 8].
    """
    if not lightweight_candidates:
        return RetrievalBlueprintSchema(
            selected_document_ids=[],
            target_navigation_nodes=[],
            selection_reasons=[],
            vector_search_terms=[],
            relationship_traversal_hops=0,
            max_chunks=5,
            planner_notes="No candidate documents available."
        )

    gemini_key = os.getenv("INTENT_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("INTELLIGENCE_LAYER_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Retrieval Planner is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    formatted_candidates = []
    for doc in lightweight_candidates:
        meta_blob = doc.get("knowledge_metadata", {}) if isinstance(doc.get("knowledge_metadata"), dict) else {}
        navigation_map = meta_blob.get("navigation_map", {})
        
        formatted_candidates.append(
            f"[DOCUMENT ID: {doc['id']}]\n"
            f" - Filename: {doc.get('filename', 'Unknown asset')}\n"
            f" - Type: {doc['document_type']} | Role: {doc['document_role']}\n"
            f" - V2 Navigation Map / Topics: {navigation_map.get('navigation', [])}\n"
            f" - Planner Summary: {doc['planner_summary']}\n"
            f"--------------------------------------------------"
        )
    candidates_context_block = "\n".join(formatted_candidates)
    
    system_instruction = (
        "You are the Core Director of the AgentPulse V2 Retrieval Planner AI Layer.\n\n"
        "MISSION OBJECTIVE:\n"
        "Construct a high-precision Retrieval Blueprint using Intent Analysis, target navigation topics, "
        "and document navigation maps. Map queries directly to exact navigation nodes when available.\n\n"
        "DEPTH & CHUNK BUDGET ALLOCATION:\n"
        "- If Intent Depth = 'Shallow': Limit relationship_traversal_hops = 0, max_chunks = 3 to 5.\n"
        "- If Intent Depth = 'Medium': Limit relationship_traversal_hops = 1, max_chunks = 6 to 8.\n"
        "- If Intent Depth = 'Deep': Set relationship_traversal_hops = 2 or 3, max_chunks = 10 to 15."
    )
    
    prompt_payload = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"INTENT DIAGNOSTICS & V2 TARGETS:\n"
        f" - Target Topic: {intent_strategy.target_topic}\n"
        f" - Target Subtopic: {intent_strategy.target_subtopic}\n"
        f" - Retrieval Depth Requested: {intent_strategy.retrieval_depth}\n"
        f" - Depth Rationale: {intent_strategy.depth_reasoning}\n"
        f"---------------------------------\n\n"
        f"CANDIDATE DOCUMENTS & NAVIGATION MAPS:\n"
        f"{candidates_context_block}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt_payload,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": RetrievalBlueprintSchema,
            "temperature": 0.0
        }
    )

    return RetrievalBlueprintSchema.model_validate_json(response.text)