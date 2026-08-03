import os
import uuid
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schemas (Universal Enterprise Structure)
# =====================================================================
class HierarchyItem(BaseModel):
    title: str = Field(description="Formal section title.")
    type: str = Field(description="'container', 'course', 'table_section', 'policy', 'unit'.")
    parent: Optional[str] = Field(default=None, description="Exact parent title, or null.")
    start_page: int
    end_page: int
    content_type: str = Field(default="narrative_paragraph")
    semantic_summary: str = Field(description="1-sentence dense summary of contents.")
    key_entities: List[str] = Field(default=[])

class ChunkSuggestion(BaseModel):
    section: str
    strategy: str
    reason: str
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
# 3. AI Execution Call (Optimized for Cost & Speed)
# =====================================================================
def run_navigation_batch(raw_text_batch: str, state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # 🟢 CONDENSED SYSTEM INSTRUCTION: Saves token cost per batch while enforcing strict rules.
    system_instruction = (
        "You are the Universal Navigation Engine. Map the logical structure of the raw document text.\n"
        "RULES:\n"
        "1. Group continuous topics into logical sections (do not split strictly by page breaks).\n"
        "2. Assign 'content_type': 'master_scheme_table', 'narrative_paragraph', 'policy_rule', or 'code_block'.\n"
        "3. Write a 1-sentence 'semantic_summary' for each section.\n"
        "4. Extract 'key_entities' (codes, IDs, core topics).\n"
        "5. Connect parents/children (Root parent = null).\n\n"
        f"BATON STATE (Continuity):\n"
        f"- Parent: {state.current_parent or 'None'} | Section: {state.current_section or 'None'} | Page: {state.last_page}\n\n"
        "OUTPUT EXACT JSON ONLY:\n"
        "{\"hierarchy\": [{\"title\": \"...\", \"type\": \"...\", \"parent\": \"...\", \"start_page\": 0, \"end_page\": 0, \"content_type\": \"...\", \"semantic_summary\": \"...\", \"key_entities\": [\"...\"]}], \"chunk_suggestions\": [{\"section\": \"...\", \"strategy\": \"...\", \"reason\": \"...\", \"preserve_tables\": true, \"preserve_lists\": true, \"split_triggers\": [\"...\"]}], \"confidence\": 1.0, \"notes\": \"\"}"
    )

    prompt = f"RAW PDF BATCH:\n\n{raw_text_batch}"

    # Using Flash Lite for Phase 1 cost efficiency
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    # 🟢 EXACT TOKEN LOGGING
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        prompt_tokens = getattr(meta, 'prompt_token_count', 0)
        completion_tokens = getattr(meta, 'candidates_token_count', 0)
        total_tokens = getattr(meta, 'total_token_count', 0)
        
        print(f"📊 [NAVIGATION AI TOKEN USAGE]")
        print(f"   - Prompt Tokens     : {prompt_tokens}")
        print(f"   - Completion Tokens : {completion_tokens}")
        print(f"   - Total Tokens      : {total_tokens}")

    return NavigationBatchResponse.model_validate_json(response.text)

# =====================================================================
# 4. Master Navigation & Stitching Loop (Phase 1 Ingestion)
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

    print(f"🤖 Processing {len(pdf_batches)} batches through Symmetric Navigation AI (Ingestion)...")

    for idx, batch_text in enumerate(pdf_batches):
        print(f"   -> Analyzing Batch {idx + 1}/{len(pdf_batches)}")
        try:
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
                
        except Exception as e:
            print(f"⚠️ Failed to parse batch {idx + 1}: {e}")

    # --- SAVE TO DATABASE WITH MATERIALIZED PATHS ---
    saved_sections: List[DocumentSection] = []
    path_to_db_id: Dict[str, uuid.UUID] = {}
    title_to_full_path: Dict[str, str] = {}

    print("💾 Saving Universal Stitched Hierarchy & Index Cards to Database...")
    
    chunk_hint_map = {c.section: c.model_dump() for c in master_chunk_suggestions}

    for item in master_hierarchy:
        # 🟢 Compute the Full Materialized Path (Breadcrumbs)
        if not item.parent:
            full_path = item.title
        else:
            parent_full_path = title_to_full_path.get(item.parent, item.parent)
            full_path = f"{parent_full_path} > {item.title}"
            
        title_to_full_path[item.title] = full_path

        db_section = DocumentSection(
            document_id=document_id, 
            workspace_id=workspace_id, 
            agent_id=agent_id,
            section_code=str(uuid.uuid4())[:8],
            title=item.title[:250], 
            parent_path=full_path[:500], # 🟢 Saved for Phase 2 Routing
            start_page=item.start_page, 
            end_page=item.end_page,
            content_type=item.content_type,
            semantic_summary=item.semantic_summary,
            key_entities=item.key_entities,
            chunking_strategy_hint=chunk_hint_map.get(item.title, {})
        )
        db.add(db_section)
        db.flush()
        
        path_to_db_id[full_path] = db_section.id
        saved_sections.append(db_section)

    # Establish Relational Parent-Child Links
    for item in master_hierarchy:
        if item.parent:
            child_full_path = title_to_full_path.get(item.title)
            parent_full_path = title_to_full_path.get(item.parent)
            
            child_id = path_to_db_id.get(child_full_path)
            parent_id = path_to_db_id.get(parent_full_path)
            
            if child_id and parent_id:
                child_sec = db.query(DocumentSection).filter_by(id=child_id).first()
                if child_sec:
                    child_sec.parent_section_id = parent_id

    db.commit()
    print(f"✅ Document Index Model finalized with {len(saved_sections)} sections.")
    
    return saved_sections, master_chunk_suggestions