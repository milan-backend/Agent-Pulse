import os
import json
from google import genai
from pydantic import BaseModel, Field
from typing import List
from app.services.intent_service import IntentAnalysisSchema

# =====================================================================
# 📊 Pydantic Structural Blueprint For Routing Engine Output
# =====================================================================

class RetrievalBlueprintSchema(BaseModel):
    selected_document_ids: List[str] = Field(
        description="UUIDs of the selected documents."
    )
    selection_reasons: List[str] = Field(
        description="Reason corresponding to each selected document."
    )
    vector_search_terms: List[str] = Field(
        description="Search phrases and concept keywords to query in ChromaDB."
    )
    
    # 🎯 NEW DEPTH ROUTING BLUEPRINT FIELDS
    relationship_traversal_hops: int = Field(
        description="Number of concept chain relationship hops to retrieve (0 to 3)."
    )
    max_chunks: int = Field(
        description="Calculated max chunk budget based on query depth (e.g. 3 for Shallow, 6 for Medium, 12 for Deep)."
    )
    prefer_latest: bool = True
    prefer_approved: bool = True
    planner_notes: str = Field(
        description="Summary of planning rationale including depth and relationship traversal constraints."
    )


# =====================================================================
# 🧠 The Retrieval Planner AI Execution Service
# =====================================================================

def execute_retrieval_planning_triage(
    user_prompt: str,
    intent_strategy: IntentAnalysisSchema,
    lightweight_candidates: List[dict]
) -> RetrievalBlueprintSchema:
    """
    Component 4: Planner AI (High-Recall Architecture Optimization)
    Uses structured Intent Analysis (including Depth & Concept Chain constraints) alongside
    lightweight candidate profiles to produce a depth-controlled Retrieval Blueprint.
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

    gemini_key = os.getenv("INTENT_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Retrieval Planner is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    formatted_candidates = []
    for doc in lightweight_candidates:
        meta_blob = doc.get("knowledge_metadata", {}) if isinstance(doc.get("knowledge_metadata"), dict) else {}
        extracted_keywords = meta_blob.get("global_retrieval_keywords", doc.get("retrieval_keywords", []))
        concept_chains = meta_blob.get("relationships", [])
        
        formatted_candidates.append(
            f"📄 [DOCUMENT ID: {doc['id']}]\n"
            f" - Filename: {doc.get('filename', 'Unknown asset')}\n"
            f" - Type: {doc['document_type']} | Role: {doc['document_role']}\n"
            f" - Structure Traits: {meta_blob.get('document_structure', {})}\n"
            f" - Concept Chains Available: {concept_chains[:5]}\n"
            f" - Planner Summary: {doc['planner_summary']}\n"
            f" - Questions Answered: {doc.get('questions_this_document_can_answer', doc.get('questions', []))}\n"
            f"--------------------------------------------------"
        )
    candidates_context_block = "\n".join(formatted_candidates)
    
    system_instruction = (
        "You are the Core Director of the AgentPulse Retrieval Planner AI Layer.\n\n"
        "🎯 MISSION OBJECTIVE:\n"
        "Construct a high-precision Retrieval Blueprint using Intent Analysis and candidate profiles.\n\n"
        "📊 DEPTH & CHUNK BUDGET ALLOCATION:\n"
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
    
    print("========== PLANNER PROMPT PAYLOAD ==========")
    print(prompt_payload)
    print("============================================")

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

    try:
        parsed_blueprint = RetrievalBlueprintSchema.model_validate_json(response.text)

        # Enforce Grounded Search Terms Fallback
        existing_terms = set(str(t).lower().strip() for t in parsed_blueprint.vector_search_terms)
        enriched_terms = list(parsed_blueprint.vector_search_terms)
        
        for target_id in parsed_blueprint.selected_document_ids:
            matched_cand = next((c for c in lightweight_candidates if str(c["id"]) == str(target_id)), None)
            if matched_cand:
                m_blob = matched_cand.get("knowledge_metadata", {}) if isinstance(matched_cand.get("knowledge_metadata"), dict) else {}
                g_keywords = m_blob.get("global_retrieval_keywords", matched_cand.get("retrieval_keywords", []))
                
                count = 0
                for kw in g_keywords:
                    clean_kw = str(kw).lower().strip()
                    if clean_kw not in existing_terms and count < 3:
                        existing_terms.add(clean_kw)
                        enriched_terms.append(kw)
                        count += 1
                        
        parsed_blueprint.vector_search_terms = enriched_terms
        return parsed_blueprint

    except Exception as validation_err:
        print(f"❌ Blueprint Schema Mismatch Fallback: {str(validation_err)}")
        return RetrievalBlueprintSchema.model_validate_json(response.text)