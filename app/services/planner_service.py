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

    vector_search_terms: List[str]

    prefer_latest: bool = True

    prefer_approved: bool = True

    max_chunks: int = 10

    planner_notes: str

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
    Uses rich structured Intent Analysis context alongside lightweight candidate profiles
    to make an optimal data routing decision. Never reads full text or answers the query.
    """
    if not lightweight_candidates:
        return RetrievalBlueprintSchema(
            selected_document_ids=[],
            selection_reasons=[],
            vector_search_terms=[],
            max_chunks=10,
            planner_notes="..."
)

    gemini_key = os.getenv("INTENT_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: INTENT_API_KEY environment variable is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    # 🎯 FIX FOR PROBLEM 7: Format lightweight candidates context block to include keywords
    formatted_candidates = []
    for doc in lightweight_candidates:
        # Gracefully handle extraction variants if keywords exist inside nested JSONB blocks
        meta_blob = doc.get("knowledge_metadata", {}) if isinstance(doc.get("knowledge_metadata"), dict) else {}
        extracted_keywords = meta_blob.get("global_retrieval_keywords", doc.get("retrieval_keywords", []))
        
        formatted_candidates.append(
            f"📄 [DOCUMENT ID: {doc['id']}]\n"
            f" - Filename: {doc.get('filename', 'Unknown asset')}\n"
            f" - Type: {doc['document_type']} | Role: {doc['document_role']}\n"
            f" - Time Scope: {doc.get('time_scope', 'N/A')} | Status: {doc.get('document_status', 'N/A')}\n"
            f" - Scores -> Authority: {doc['authority_score']} | Importance: {doc['importance_score']} | Freshness: {doc['freshness']}\n"
            f" - Planner Summary: {doc['planner_summary']}\n"
            f" - Grounded Retrieval Keywords: {extracted_keywords}\n"
            f" - Questions This Document Can Answer: {doc.get('questions_this_document_can_answer', doc.get('questions', []))}\n"
            f"--------------------------------------------------"
        )
    candidates_context_block = "\n".join(formatted_candidates)
    
    # 🎯 FIX FOR PROBLEM 2 & 3: High-Recall prompt adjustment to evaluate metrics holistically
    system_instruction = (
        "You are the Core Director of the AgentPulse Retrieval Planner AI Layer.\n\n"
        "🎯 MISSION OBJECTIVE:\n"
        "Your task is to review the highly structured INTENT ANALYSIS and a small set of pre-filtered candidate document profiles "
        "to construct a high-precision Retrieval Blueprint. Do NOT re-do the intent analysis; use the provided strategy parameters.\n\n"
        "⚠️ BALANCED PLANNING CONSTRAINTS & HIGH-RECALL RULES:\n"
        "- **Select every candidate document that is reasonably relevant, shares structural tags, or temporal bounds with the request.**\n"
        "- Balance metrics holistically: rely on 'Planner Summary', authority scores, and bridge keywords alongside question arrays. Do not punish a file just because one field is thin.\n"
        "- Return an empty selection array ONLY if absolutely none of the candidate items share any functional relationship with the user question.\n"
        "- When in doubt, prefer INCLUSION over exclusion. High recall is critical to avoid downstream context starvation.\n"
        "- Output a comprehensive set of vector search terms to guide the downstream retrieval engine."
    )
    
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
        f" - Expanded Keywords: {', '.join(getattr(intent_strategy, 'expanded_search_keywords', []))}\n"
        f"---------------------------------\n\n"
        f"CANDIDATE DOCUMENTS\n"
        f"==================================================\n"
        f"{candidates_context_block}\n"
        f"=================================================="
    )
    
    # Debug telemetry validation logs
    print("========== PLANNER PROMPT PAYLOAD ==========")
    print(prompt_payload)
    print("============================================")

    response = client.models.generate_content(
        model="gemini-3.5-flash",  # 🎯 Current flagship production model
        contents=prompt_payload,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": RetrievalBlueprintSchema,
            "temperature": 0.0
        }
    )

    
    print("========== PLANNER RAW LLM RESPONSE ==========")
    print(response.text)
    print("==============================================")

    try:
        parsed_blueprint = RetrievalBlueprintSchema.model_validate_json(response.text)

        print("========== PARSED BLUEPRINT ==========")
        print(parsed_blueprint.model_dump())
        print("======================================")
        
        # 🎯 FIX FOR PROBLEM 5: Grounded Search Terms Extraction Integration Fallback
        # If the LLM generates weak generic keywords but selected highly focused documents, 
        # we dynamically enrich vector_search_terms with the grounded keywords pre-extracted during asset ingestion.
        existing_terms = set(str(t).lower().strip() for t in parsed_blueprint.vector_search_terms)
        enriched_terms = list(parsed_blueprint.vector_search_terms)
        
        for target_id in parsed_blueprint.selected_document_ids:
            matched_cand = next((c for c in lightweight_candidates if str(c["id"]) == str(target_id)), None)
            
            if matched_cand:
                m_blob = matched_cand.get("knowledge_metadata", {}) if isinstance(matched_cand.get("knowledge_metadata"), dict) else {}
                g_keywords = m_blob.get("global_retrieval_keywords", matched_cand.get("retrieval_keywords", []))
                
                # Blend the top 3 grounded terms that aren't duplicates to guarantee true vector indexing
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
        print(f"❌ Fallback triggered due to blueprint schema mismatch: {str(validation_err)}")
        # If schema verification hits parsing exceptions, attempt generic fallback parsing to save operations
        return RetrievalBlueprintSchema.model_validate_json(response.text)