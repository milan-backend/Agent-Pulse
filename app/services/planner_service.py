import os
from google import genai
from pydantic import BaseModel, Field
from typing import List
from app.services.intent_service import IntentAnalysisSchema

class RetrievalBlueprintSchema(BaseModel):
    selected_document_ids: List[str] = Field(
        description="UUIDs of the selected documents."
    )
    selection_reasons: List[str] = Field(
        description="Reason corresponding to each selected document."
    )
    vector_search_terms: List[str] = Field(
        description="Search phrases and concept keywords to query in ChromaDB with topic/chunk mapping."
    )
    relationship_traversal_hops: int = Field(
        description="Number of concept chain relationship hops to retrieve (0 to 3)."
    )
    max_chunks: int = Field(
        description="Calculated max chunk budget based on query depth."
    )
    prefer_latest: bool = True
    prefer_approved: bool = True
    planner_notes: str = Field(
        description="Summary of planning rationale including depth and relationship traversal constraints."
    )

def execute_retrieval_planning_triage(
    user_prompt: str,
    intent_strategy: IntentAnalysisSchema,
    lightweight_candidates: List[dict]
) -> RetrievalBlueprintSchema:
    """
    Planner AI: Combines Intent Analysis and Navigation/Extraction metadata profiles 
    to produce a depth-controlled Retrieval Blueprint targeting ChromaDB topic indices and chunk IDs.
    """
    if not lightweight_candidates:
        return RetrievalBlueprintSchema(
            selected_document_ids=[],
            selection_reasons=[],
            vector_search_terms=[],
            relationship_traversal_hops=0,
            max_chunks=5,
            planner_notes="No candidate documents available."
        )

    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Retrieval Planner is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    formatted_candidates = []
    for doc in lightweight_candidates:
        meta_blob = doc.get("knowledge_metadata", {}) if isinstance(doc.get("knowledge_metadata"), dict) else {}
        extracted_keywords = meta_blob.get("global_retrieval_keywords", doc.get("retrieval_keywords", []))
        concept_chains = meta_blob.get("relationships", [])
        
        formatted_candidates.append(
            f"📌 [DOCUMENT ID: {doc['id']}]\n"
            f" - Filename: {doc.get('filename', 'Unknown asset')}\n"
            f" - Type: {doc.get('document_type', 'General')} | Role: {doc.get('document_role', 'Standard')}\n"
            f" - Concept Chains Available: {concept_chains[:5]}\n"
            f" - Planner Summary: {doc.get('planner_summary', '')}\n"
            f"--------------------------------------------------"
        )
    candidates_context_block = "\n".join(formatted_candidates)
    
    system_instruction = (
        "You are the Core Director of the AgentPulse Retrieval Planner AI Layer.\n\n"
        "MISSION OBJECTIVE:\n"
        "Construct a high-precision Retrieval Blueprint using Intent Analysis and candidate profiles.\n\n"
        "DEPTH & CHUNK BUDGET ALLOCATION:\n"
        "- If Intent Depth = 'Shallow': Limit relationship_traversal_hops = 0, max_chunks = 3 to 5.\n"
        "- If Intent Depth = 'Medium': Limit relationship_traversal_hops = 1, max_chunks = 6 to 8.\n"
        "- If Intent Depth = 'Deep': Set relationship_traversal_hops = 2 or 3, max_chunks = 10 to 15.\n"
        "- Traverse concept chains ONLY if intent_strategy.include_concept_chains is True."
    )
    
    prompt_payload = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"INTENT DIAGNOSTICS & DEPTH BOUNDARIES:\n"
        f" - Intent Type: {intent_strategy.intent_type}\n"
        f" - Main Topic: {intent_strategy.main_topic}\n"
        f" - Retrieval Depth Requested: {intent_strategy.retrieval_depth}\n"
        f" - Include Concept Chains: {intent_strategy.include_concept_chains}\n"
        f" - Recommended Max Hops: {intent_strategy.max_relationship_hops}\n"
        f" - Depth Rationale: {intent_strategy.depth_reasoning}\n"
        f"---------------------------------\n\n"
        f"CANDIDATE DOCUMENTS:\n"
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