import os
import uuid
import json
from typing import List, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection, DocumentChunk
from app.models.uploaded_document import UploadedDocument  # 🟢 ADDED: To fetch document names

# =====================================================================
# 1. AI Output Schemas (Strict & Simple)
# =====================================================================
# 🟢 NEW: Schema for Step 1 (Cabinet Check)
class DocumentTriageDecision(BaseModel):
    target_document_ids: List[str] = Field(
        description="The exact list of document string UUIDs likely to contain the answer."
    )
    reasoning: str = Field(
        description="Brief explanation of why these documents were selected based on their titles."
    )

# Schema for Step 2 (Folder Check)
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
    Includes Document-Level Pre-Triage to save token costs.
    """
    
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Smart Router AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # =====================================================================
    # 🟢 STEP 1: DOCUMENT PRE-TRIAGE (The "Cabinet Check")
    # =====================================================================
    target_doc_ids = []
    
    if document_ids:
        target_doc_ids = [str(d) for d in document_ids]
    else:
        # Fetch all available documents (cabinets) in the workspace
        workspace_docs = db.query(UploadedDocument).filter(
            UploadedDocument.workspace_id == workspace_id,
            UploadedDocument.status == "ready"
        ).all()

        if not workspace_docs:
            print("⚠️ No ready documents found in this workspace.")
            return []

        # If there is only 1 document, skip the triage to save time and money
        if len(workspace_docs) == 1:
            target_doc_ids = [str(workspace_docs[0].id)]
            print(f"📄 Only 1 document found ({workspace_docs[0].filename}). Skipping Triage.")
        else:
            # Build the lightweight Cabinet List
            cabinet_list = [{"document_id": str(d.id), "filename": d.filename} for d in workspace_docs]
            
            triage_instruction = (
                "You are the Document Triage AI. Read the user's question and review the list of available documents.\n"
                "Select ONLY the `document_id`s that are likely to contain the answer based on their filenames.\n\n"
                "OUTPUT EXACT JSON matching this schema:\n"
                "{\"target_document_ids\": [\"uuid-string\"], \"reasoning\": \"string\"}"
            )
            triage_prompt = (
                f"USER QUESTION: \"{user_prompt}\"\n\n"
                f"AVAILABLE DOCUMENTS:\n{json.dumps(cabinet_list, indent=2)}"
            )

            print(f"🗄️ Triaging {len(workspace_docs)} documents to find the correct context...")
            try:
                # Use a fast/cheap model for Step 1
                triage_resp = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=triage_prompt,
                    config={
                        "system_instruction": triage_instruction,
                        "response_mime_type": "application/json",
                        "temperature": 0.0
                    }
                )
                triage_decision = DocumentTriageDecision.model_validate_json(triage_resp.text)
                target_doc_ids = triage_decision.target_document_ids
                print(f"✅ Triage Decision: {triage_decision.reasoning}")
                print(f"🎯 Selected Cabinets: {len(target_doc_ids)}")
            except Exception as e:
                print(f"⚠️ Triage failed, falling back to scanning ALL documents. Error: {e}")
                target_doc_ids = [str(d.id) for d in workspace_docs]

    if not target_doc_ids:
        return []

    # =====================================================================
    # 🟢 STEP 2: THE SECTION ROUTER (The "Folder Check")
    # =====================================================================
    # Fetch the "Index Cards" ONLY for the documents the Triage AI selected
    available_sections = db.query(DocumentSection).filter(
        DocumentSection.workspace_id == workspace_id,
        DocumentSection.document_id.in_(target_doc_ids)
    ).all()
    
    if not available_sections:
        print("⚠️ No navigation sections found for the selected documents.")
        return []

    # Build the Flat Semantic Index (Folders)
    index_cards = []
    for sec in available_sections:
        index_cards.append({
            "section_id": str(sec.id),
            "path": sec.parent_path,
            "title": sec.title,
            "type": sec.content_type,
            "summary": sec.semantic_summary
        })

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

    print(f"🧠 Routing Query through Smart Navigation AI (Scanning {len(index_cards)} Index Cards)...")
    
    # Using the capable model for detailed section reasoning
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    # Print Token Usage Logs
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        print(f"📊 [SMART ROUTER TOKEN USAGE]")
        print(f"   - Prompt Tokens     : {getattr(meta, 'prompt_token_count', 0)}")
        print(f"   - Completion Tokens : {getattr(meta, 'candidates_token_count', 0)}")
        print(f"   - Total Tokens      : {getattr(meta, 'total_token_count', 0)}")

    # Parse the Decision
    try:
        decision = RoutingDecision.model_validate_json(response.text)
        print(f"✅ Router AI Decision: {decision.routing_reasoning}")
        print(f"🎯 Selected Sections: {len(decision.target_section_ids)}")
    except Exception as e:
        print(f"❌ Failed to parse Router AI output: {e}")
        return []

    # Resolve Sections to exact Chroma Vector IDs
    if not decision.target_section_ids:
        return []

    target_chunks = db.query(DocumentChunk).filter(
        DocumentChunk.section_id.in_(decision.target_section_ids),
        DocumentChunk.workspace_id == workspace_id
    ).all()

    vector_ids = [chunk.chroma_vector_id for chunk in target_chunks]
    print(f"📡 Resolved {len(decision.target_section_ids)} sections into {len(vector_ids)} exact vector targets.")
    
    return vector_ids