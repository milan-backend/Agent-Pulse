import os
import uuid
import json
from typing import List, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection, DocumentChunk

# =====================================================================
# 1. AI Output Schema (Strict & Simple)
# =====================================================================
class RoutingDecision(BaseModel):
    target_section_ids: List[str] = Field(
        description="The exact list of string UUIDs for the sections containing the answer."
    )
    routing_reasoning: str = Field(
        description="A brief explanation of why these specific sections were chosen based on their semantic summaries."
    )

# =====================================================================
# 2. The Smart Query Engine (Phase 2)
# =====================================================================
def execute_smart_routing(
    user_prompt: str, 
    workspace_id: uuid.UUID, 
    db: Session,
    document_ids: List[uuid.UUID] = None
) -> List[str]:
    """
    Symmetric AI Router: Reads the universal Document Map and outputs the exact
    Chroma Vector IDs to fetch, bypassing traditional SQL search limitations.
    """
    
    # 1. Fetch the "Index Cards" (The Navigation Map)
    query = db.query(DocumentSection).filter(DocumentSection.workspace_id == workspace_id)
    if document_ids:
        query = query.filter(DocumentSection.document_id.in_(document_ids))
        
    available_sections = query.all()
    
    if not available_sections:
        print("⚠️ No navigation map found for this workspace.")
        return []

    # 2. Build the Flat Semantic Index for the AI
    # This is highly token-efficient because the AI isn't reading the raw text, 
    # just the dense summaries and materialized paths.
    index_cards = []
    for sec in available_sections:
        index_cards.append({
            "section_id": str(sec.id),
            "path": sec.parent_path,
            "title": sec.title,
            "type": sec.content_type,
            "summary": sec.semantic_summary
        })

    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Smart Router AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Smart Query Router for AgentPulse.\n"
        "MISSION:\n"
        "Read the user's question and review the provided Document Index Catalog.\n"
        "Select ONLY the `section_id`s that semantically match the user's intent. "
        "Use the `path` and `summary` to determine relevance. If the user asks for a broad overview, prioritize sections with `type: master_scheme_table`.\n\n"
        "OUTPUT EXACT JSON matching this schema:\n"
        "{\"target_section_ids\": [\"uuid-string\"], \"routing_reasoning\": \"string\"}"
    )

    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"DOCUMENT INDEX CATALOG:\n"
        f"{json.dumps(index_cards, indent=2)}"
    )

    print("🧠 Routing Query through Smart Navigation AI...")
    
    # Using a capable model for reasoning accuracy
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    # 3. Print Token Usage Logs
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        print(f"📊 [SMART ROUTER TOKEN USAGE]")
        print(f"   - Prompt Tokens     : {getattr(meta, 'prompt_token_count', 0)}")
        print(f"   - Completion Tokens : {getattr(meta, 'candidates_token_count', 0)}")
        print(f"   - Total Tokens      : {getattr(meta, 'total_token_count', 0)}")

    # 4. Parse the Decision
    try:
        decision = RoutingDecision.model_validate_json(response.text)
        print(f"✅ Router AI Decision: {decision.routing_reasoning}")
        print(f"🎯 Selected Sections: {len(decision.target_section_ids)}")
    except Exception as e:
        print(f"❌ Failed to parse Router AI output: {e}")
        return []

    # 5. Resolve Sections to exact Chroma Vector IDs
    if not decision.target_section_ids:
        return []

    target_chunks = db.query(DocumentChunk).filter(
        DocumentChunk.section_id.in_(decision.target_section_ids),
        DocumentChunk.workspace_id == workspace_id
    ).all()

    vector_ids = [chunk.chroma_vector_id for chunk in target_chunks]
    print(f"📡 Resolved {len(decision.target_section_ids)} sections into {len(vector_ids)} exact vector targets.")
    
    return vector_ids