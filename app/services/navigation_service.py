import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schemas for AI Output (Universal Enterprise Structure)
# =====================================================================
class HierarchyItem(BaseModel):
    title: str = Field(description="The formal title of the section or division.")
    type: str = Field(description="Logical classification like 'container', 'course', 'table_section', 'policy', 'unit'.")
    parent: Optional[str] = Field(default=None, description="Exact title of the parent container, or null if top-level.")
    start_page: int = Field(description="Starting page number of this logical section.")
    end_page: int = Field(description="Ending page number of this logical section.")
    content_type: str = Field(default="narrative_paragraph", description="Type of content: 'master_scheme_table', 'narrative_paragraph', 'policy_rule', 'code_block'.")
    semantic_summary: str = Field(description="A dense 1-2 sentence description explaining what data or topics live inside this section.")
    key_entities: List[str] = Field(default=[], description="Important identifiers, course codes, policy names, or key terms found in this section.")

class ChunkSuggestion(BaseModel):
    section: str = Field(description="The section title this suggestion applies to.")
    strategy: str = Field(description="Splitting strategy, e.g., 'table_boundary_preservation', 'topic_based', 'semantic_paragraph_shift'.")
    reason: str = Field(description="Engineering reasoning for this strategy choice.")
    preserve_tables: bool = True
    preserve_lists: bool = True
    split_triggers: List[str] = Field(default_factory=list)

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = []
    chunk_suggestions: List[ChunkSuggestion] = []
    confidence: float = 1.0
    notes: str = ""

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
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Universal Navigation & Document Structure Intelligence Engine for AgentPulse.\n\n"
        "MISSION:\n"
        "Reconstruct the logical structure of any arbitrary document (academic syllabi, financial statements, "
        "corporate policies, technical manuals) exactly as an expert human analyst would.\n\n"
        "GENERAL PRINCIPLES:\n"
        "- Discover logical structure dynamically; do not assume specific industries.\n"
        "- A section represents one continuous logical topic, table block, or policy group.\n"
        "- Classify `content_type` strictly as one of: 'master_scheme_table' (for overview/syllabus tables), "
        "'narrative_paragraph' (for standard text), 'policy_rule' (for compliance/rules), or 'code_block'.\n"
        "- Provide a concise `semantic_summary` for every section so downstream AI engines understand its contents instantly.\n"
        "- Maintain hierarchy properly (Parents contain children; root parent = null).\n"
        "- Avoid over-segmentation; page breaks do not automatically create new sections.\n\n"
        "🧠 THE BATON (CURRENT ACTIVE STATE):\n"
        f"- Current Active Parent: {state.current_parent or 'None'}\n"
        f"- Current Active Section: {state.current_section or 'None'}\n"
        f"- Current Section Type: {state.current_type or 'None'}\n"
        f"- Last Scanned Page: {state.last_page}\n\n"
        "⚠️ OUTPUT REQUIREMENTS:\n"
        "Return ONLY a raw JSON object matching this exact schema format:\n"
        "{\n"
        '  "hierarchy": [\n'
        '    {\n'
        '      "title": "string",\n'
        '      "type": "string",\n'
        '      "parent": "string or null",\n'
        '      "start_page": 0,\n'
        '      "end_page": 0,\n'
        '      "content_type": "master_scheme_table | narrative_paragraph | policy_rule | code_block",\n'
        '      "semantic_summary": "string",\n'
        '      "key_entities": ["string"]\n'
        '    }\n'
        '  ],\n'
        '  "chunk_suggestions": [\n'
        '    {\n'
        '      "section": "string",\n'
        '      "strategy": "string",\n'
        '      "reason": "string",\n'
        '      "preserve_tables": true,\n'
        '      "preserve_lists": true,\n'
        '      "split_triggers": ["string"]\n'
        '    }\n'
        '  ],\n'
        '  "confidence": 0.95,\n'
        '  "notes": "string"\n'
        "}"
    )

    prompt = f"RAW PDF BATCH:\n\n{raw_text_batch}"

    # 🟢 FIX: Remove response_schema from config and enforce JSON via system instructions 
    # to avoid the Pydantic v2 $defs extra_forbidden crash in google-genai SDK.
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        print(f"📊 [NAVIGATION TOKEN USAGE]")
        print(f"   - Input Tokens  : {getattr(meta, 'prompt_token_count', 'N/A')}")
        print(f"   - Output Tokens : {getattr(meta, 'candidates_token_count', 'N/A')}")

    # Safely parse the text output using Pydantic validation
    return NavigationBatchResponse.model_validate_json(response.text)

# =====================================================================
# 4. Master Navigation & Stitching Loop with Safe Database Persistence
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

    print(f"🤖 Processing {len(pdf_batches)} batches through Universal Navigation AI...")

    for idx, batch_text in enumerate(pdf_batches):
        print(f"   -> Analyzing Batch {idx + 1}/{len(pdf_batches)}")
        batch_response = run_navigation_batch(batch_text, active_state)
        
        # Stitcher logic across batch cuts
        for item in batch_response.hierarchy:
            if master_hierarchy and master_hierarchy[-1].title == item.title and master_hierarchy[-1].parent == item.parent:
                master_hierarchy[-1].end_page = max(master_hierarchy[-1].end_page, item.end_page)
            else:
                master_hierarchy.append(item)

        # Deduplicate chunk suggestions
        existing_chunk_sections = {c.section for c in master_chunk_suggestions}
        for chunk_strat in batch_response.chunk_suggestions:
            if chunk_strat.section not in existing_chunk_sections:
                master_chunk_suggestions.append(chunk_strat)
                existing_chunk_sections.add(chunk_strat.section)

        if master_hierarchy:
            last_item = master_hierarchy[-1]
            active_state.current_section = last_item.title
            active_state.current_parent = last_item.parent
            active_state.current_type = last_item.type
            active_state.last_page = last_item.end_page

    # --- SAVE TO DATABASE USING COMPOSITE PATHS TO PREVENT COLLISIONS ---
    saved_sections: List[DocumentSection] = []
    path_to_db_id: Dict[str, uuid.UUID] = {}

    print("💾 Saving Universal Stitched Hierarchy to Database...")
    
    # Map section titles to their chunking hints for fast lookup
    chunk_hint_map = {c.section: c.model_dump() for c in master_chunk_suggestions}

    for item in master_hierarchy:
        db_section = DocumentSection(
            document_id=document_id, 
            workspace_id=workspace_id, 
            agent_id=agent_id,
            section_code=str(uuid.uuid4())[:8],
            title=item.title[:250], 
            start_page=item.start_page, 
            end_page=item.end_page,
            # 🟢 Save the rich universal metadata fields
            content_type=item.content_type,
            semantic_summary=item.semantic_summary,
            key_entities=item.key_entities,
            chunking_strategy_hint=chunk_hint_map.get(item.title, {})
        )
        db.add(db_section)
        db.flush()
        
        # Create a unique composite key path string to prevent title collision bugs
        composite_path = f"{item.parent} > {item.title}" if item.parent else item.title
        path_to_db_id[composite_path] = db_section.id
        saved_sections.append(db_section)

    # Establish secure Parent-Child Links using composite paths
    for item in master_hierarchy:
        if item.parent:
            parent_path = item.parent
            matching_parent_id = None
            
            # Find the correct parent ID safely
            for k, v in path_to_db_id.items():
                if k.endswith(f"> {parent_path}") or k == parent_path:
                    matching_parent_id = v
                    break
            
            if matching_parent_id:
                child_path = f"{item.parent} > {item.title}"
                child_sec_id = path_to_db_id.get(child_path)
                if child_sec_id:
                    child_sec = db.query(DocumentSection).filter_by(id=child_sec_id).first()
                    if child_sec:
                        child_sec.parent_section_id = matching_parent_id

    db.commit()
    print(f"✅ Universal Navigation Map finalized with {len(saved_sections)} robust sections.")
    
    return saved_sections, master_chunk_suggestions