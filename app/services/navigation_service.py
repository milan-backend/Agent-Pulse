import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schemas for AI Output
# =====================================================================
class HierarchyItem(BaseModel):
    title: str
    type: str  # 'container', 'course', 'unit', etc.
    parent: Optional[str] = None
    start_page: int
    end_page: int

class ChunkSuggestion(BaseModel):
    section: str
    strategy: str
    reason: str
    preserve_tables: bool
    preserve_lists: bool
    split_triggers: List[str]

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = []
    chunk_suggestions: List[ChunkSuggestion] = []
    confidence: float
    notes: str

# =====================================================================
# 2. State "Baton" Object
# =====================================================================
class ActiveState:
    def __init__(self):
        self.current_parent: Optional[str] = None
        self.current_section: Optional[str] = None
        self.current_type: Optional[str] = None
        self.last_page: int = 0

# =====================================================================
# 3. AI Execution Call
# =====================================================================
def run_navigation_batch(raw_text_batch: str, state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation & Chunking Strategy AI.\n\n"
        "🎯 MISSION:\n"
        "Analyze the raw PDF pages provided. Output the Document Hierarchy and recommend a Chunking Strategy. "
        "Do NOT extract entities, summaries, or metadata.\n\n"
        "🧠 THE BATON (CURRENT ACTIVE STATE):\n"
        "You are receiving a batch of pages from a larger document. Use this state to maintain continuity:\n"
        f"- Current Active Parent: {state.current_parent or 'None'}\n"
        f"- Current Active Section: {state.current_section or 'None'}\n"
        f"- Current Section Type: {state.current_type or 'None'}\n"
        f"- Last Scanned Page: {state.last_page}\n\n"
        "If the text continues the 'Current Active Section', DO NOT create a new section. Only create a new section if a distinct new heading appears.\n\n"
        "✂️ CHUNKING STRATEGY RULES:\n"
        "- Do not count tokens or suggest numeric chunk sizes.\n"
        "- Recommend split triggers like: ['new heading', 'new topic', 'new procedure', 'new table'].\n\n"
        "⚠️ OUTPUT FORMAT:\n"
        "Return ONLY a raw JSON object exactly matching this structure. No markdown wrappers.\n"
        "{\n"
        '  "hierarchy": [\n'
        '    {"title": "III Semester", "type": "container", "parent": null, "start_page": 12, "end_page": 25},\n'
        '    {"title": "Digital Electronics", "type": "course", "parent": "III Semester", "start_page": 15, "end_page": 17}\n'
        '  ],\n'
        '  "chunk_suggestions": [\n'
        '    {"section": "Digital Electronics", "strategy": "topic_based", "reason": "Units discuss different concepts.", "preserve_tables": true, "preserve_lists": true, "split_triggers": ["new unit heading", "new table"]}\n'
        '  ],\n'
        '  "confidence": 0.95,\n'
        '  "notes": "Pages contained standard syllabus structures."\n'
        "}"
    )

    prompt = f"RAW PDF BATCH:\n\n{raw_text_batch}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    # 🟢 2. WRITE THIS LOG HERE TO TRACK TOKENS:
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        print(f"📊 [TOKEN USAGE METRICS]")
        print(f"   - Prompt (Input) Tokens : {getattr(meta, 'prompt_token_count', 'N/A')}")
        print(f"   - Completion (Output)   : {getattr(meta, 'candidates_token_count', 'N/A')}")
        print(f"   - Total Tokens Consumed : {getattr(meta, 'total_token_count', 'N/A')}")

    # 3. Parse json response as normal
    return NavigationBatchResponse.model_validate_json(response.text)

# =====================================================================
# 4. Master Navigation & Stitching Loop
# =====================================================================
def build_and_save_navigation_map(
    db: Session,
    document_id: uuid.UUID,
    workspace_id: uuid.UUID,
    agent_id: Optional[uuid.UUID],
    pdf_batches: List[str]
) -> tuple[List[DocumentSection], List[ChunkSuggestion]]:
    
    master_hierarchy: List[HierarchyItem] = []
    master_chunk_suggestions: List[ChunkSuggestion] = []
    active_state = ActiveState()

    print(f"🤖 Processing {len(pdf_batches)} batches through Navigation AI...")

    # --- THE BATCH LOOP ---
    for idx, batch_text in enumerate(pdf_batches):
        print(f"   -> Analyzing Batch {idx + 1}/{len(pdf_batches)}")
        
        batch_response = run_navigation_batch(batch_text, active_state)
        
        # --- THE STITCHER ---
        for item in batch_response.hierarchy:
            # If the current item is an exact match to the last item in the master list, STITCH them.
            if master_hierarchy and master_hierarchy[-1].title == item.title and master_hierarchy[-1].parent == item.parent:
                master_hierarchy[-1].end_page = max(master_hierarchy[-1].end_page, item.end_page)
            else:
                # New section found, append it to master
                master_hierarchy.append(item)

        # Append Chunking Strategies (Deduplicating by section name)
        existing_chunk_sections = {c.section for c in master_chunk_suggestions}
        for chunk_strat in batch_response.chunk_suggestions:
            if chunk_strat.section not in existing_chunk_sections:
                master_chunk_suggestions.append(chunk_strat)
                existing_chunk_sections.add(chunk_strat.section)

        # --- UPDATE THE BATON ---
        if master_hierarchy:
            last_item = master_hierarchy[-1]
            active_state.current_section = last_item.title
            active_state.current_parent = last_item.parent
            active_state.current_type = last_item.type
            active_state.last_page = last_item.end_page

    # --- SAVE TO DATABASE ---
    saved_sections: List[DocumentSection] = []
    title_to_db_id: Dict[str, uuid.UUID] = {}

    print("💾 Saving Stitched Hierarchy to Database...")
    for item in master_hierarchy:
        db_section = DocumentSection(
            document_id=document_id, 
            workspace_id=workspace_id, 
            agent_id=agent_id,
            section_code=str(uuid.uuid4())[:8], # Logical code can be generated via a separate numbering function if needed
            title=item.title[:250], 
            start_page=item.start_page, 
            end_page=item.end_page
        )
        db.add(db_section)
        db.flush()
        title_to_db_id[item.title] = db_section.id
        saved_sections.append(db_section)

    # Establish Parent-Child Links based on the stitched titles
    for item in master_hierarchy:
        if item.parent and item.parent in title_to_db_id:
            child_sec = db.query(DocumentSection).get(title_to_db_id[item.title])
            if child_sec:
                child_sec.parent_section_id = title_to_db_id[item.parent]

    db.commit()
    print(f"✅ Navigation Map finalized with {len(saved_sections)} stitched sections.")
    
    # Return both the Sections for saving, and the Chunk Suggestions to pass to your Chunk Engine
    return saved_sections, master_chunk_suggestions