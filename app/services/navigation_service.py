import os
import uuid
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schemas
# =====================================================================
class HierarchyItem(BaseModel):
    title: str = Field(description="Formal section or subsection title.")
    type: str = Field(description="'container', 'table_section', 'policy', 'institution_grant', 'notes'.")
    parent: Optional[str] = Field(default=None, description="Exact parent title, or null for root.")
    start_page: int
    end_page: int
    content_type: str = Field(default="master_scheme_table")
    semantic_summary: str = Field(description="1-sentence dense summary of specific contents.")
    key_entities: List[str] = Field(default=[])
    normalized_text: str = Field(default="", description="The text for this specific subsection, with table rows intact.")

class ChunkSuggestion(BaseModel):
    section: str
    strategy: str = "row_preserving"
    reason: str = "Table structure"
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
        "You are the Universal Navigation Engine. Map the granular logical structure of the raw text.\n"
        "RULES:\n"
        "1. DO NOT group an entire multi-page document into a single section. Identify individual major headings, institutions (e.g. IITs, NITs, IIMs, UGC), and distinct scheme tables as SEPARATE sections or subsections.\n"
        "2. For budget tables, set 'content_type': 'master_scheme_table'. In chunk_suggestions, set 'preserve_tables': true.\n"
        "3. Ensure the 'section' string in chunk_suggestions EXACTLY matches the 'title' in hierarchy.\n"
        "4. Write a 1-sentence dense 'semantic_summary' explaining what specific institutions or schemes are in this section.\n"
        "5. Extract 'key_entities' (e.g., 'IIT', 'HEFA', 'NIT', 'UGC', specific scheme codes).\n"
        "6. DATA CLEANING: Extract text into 'normalized_text'. Forward-fill implicit row groupings.\n\n"
        f"PREVIOUS BATCH STATE:\n"
        f"- Last Active Root: {state.current_parent or 'None'} | Last Subsection: {state.current_section or 'None'} | Last Page: {state.last_page}\n\n"
        "OUTPUT EXACT JSON ONLY conforming to NavigationBatchResponse schema."
    )

    prompt = f"RAW PDF BATCH:\n\n{raw_text_batch}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-lite", 
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "temperature": 0.0
                }
            )

            raw_text = response.text.strip()
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            raw_json_str = raw_text[start_idx:end_idx + 1] if start_idx != -1 and end_idx != -1 else raw_text
            parsed_data = json.loads(raw_json_str)
            
            if isinstance(parsed_data, list):
                parsed_data = {
                    "hierarchy": parsed_data,
                    "chunk_suggestions": [],
                    "confidence": 0.5,
                    "notes": "Recovered from raw list format"
                }
                
            return NavigationBatchResponse(**parsed_data)

        except Exception as e:
            if ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 3)
            elif attempt == max_retries - 1:
                raise e

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

    print(f"🤖 Processing {len(pdf_batches)} batches through Symmetric Navigation AI (Ingestion)...")

    for idx, batch_text in enumerate(pdf_batches):
        print(f"   -> Analyzing Batch {idx + 1}/{len(pdf_batches)}")
        try:
            batch_response = run_navigation_batch(batch_text, active_state)
            
            for item in batch_response.hierarchy:
                # Only stitch if it's genuinely the same continuous leaf section across a page cut
                if master_hierarchy and master_hierarchy[-1].title.strip().lower() == item.title.strip().lower() and master_hierarchy[-1].parent == item.parent:
                    master_hierarchy[-1].end_page = max(master_hierarchy[-1].end_page, item.end_page)
                    master_hierarchy[-1].normalized_text += "\n" + item.normalized_text
                else:
                    master_hierarchy.append(item)

            for chunk_strat in batch_response.chunk_suggestions:
                master_chunk_suggestions.append(chunk_strat)

            if master_hierarchy:
                last_item = master_hierarchy[-1]
                active_state.current_section = last_item.title
                active_state.current_parent = last_item.parent
                active_state.current_type = last_item.type
                active_state.last_page = last_item.end_page
                
        except Exception as e:
            print(f"⚠️ Failed to parse batch {idx + 1}: {e}")

    # Build fuzzy-tolerant chunk hint map
    chunk_hint_map = {}
    for c in master_chunk_suggestions:
        key = c.section.strip().lower()
        chunk_hint_map[key] = c.model_dump()

    saved_sections: List[DocumentSection] = []
    path_to_db_id: Dict[str, uuid.UUID] = {}
    title_to_full_path: Dict[str, str] = {}

    for item in master_hierarchy:
        if not item.parent:
            full_path = item.title
        else:
            parent_full_path = title_to_full_path.get(item.parent, item.parent)
            full_path = f"{parent_full_path} > {item.title}"
            
        title_to_full_path[item.title] = full_path

        # Match strategy hint by title or default to preserve_tables for tables
        matched_hint = chunk_hint_map.get(item.title.strip().lower(), {})
        if not matched_hint and item.content_type == "master_scheme_table":
            matched_hint = {"preserve_tables": True, "preserve_lists": True, "strategy": "row_preserving"}
            
        matched_hint["normalized_text"] = item.normalized_text

        db_section = DocumentSection(
            document_id=document_id, 
            workspace_id=workspace_id, 
            agent_id=agent_id,
            section_code=str(uuid.uuid4())[:8],
            title=item.title[:250], 
            parent_path=full_path[:500],
            start_page=item.start_page, 
            end_page=item.end_page,
            content_type=item.content_type,
            semantic_summary=item.semantic_summary,
            key_entities=item.key_entities,
            chunking_strategy_hint=matched_hint
        )
        db.add(db_section)
        db.flush()
        
        path_to_db_id[full_path] = db_section.id
        saved_sections.append(db_section)

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