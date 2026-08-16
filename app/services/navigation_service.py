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
# 1. Pydantic Schemas (Crash-Proof with Defaults)
# =====================================================================
class HierarchyItem(BaseModel):
    title: str = Field(default="Untitled Section", description="Formal section title.")
    type: str = Field(default="narrative_paragraph", description="'container', 'table_section', 'institution', etc.")
    parent: Optional[str] = Field(default=None, description="Exact parent title, or null.")
    start_page: int = Field(default=1)
    end_page: int = Field(default=1)
    content_type: str = Field(default="master_scheme_table")
    semantic_summary: str = Field(default="No summary provided.", description="1-sentence dense summary of contents.")
    key_entities: List[str] = Field(default_factory=list)
    normalized_text: str = Field(default="", description="The fully cleaned text for this section.")

class ChunkSuggestion(BaseModel):
    section: str = Field(default="Untitled Section")
    strategy: str = Field(default="row_preserving")
    reason: str = Field(default="Table extraction")
    preserve_tables: bool = Field(default=True)
    preserve_lists: bool = Field(default=True)
    split_triggers: List[str] = Field(default_factory=list)

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = Field(default_factory=list)
    chunk_suggestions: List[ChunkSuggestion] = Field(default_factory=list)
    confidence: float = Field(default=1.0)
    notes: str = Field(default="")
    # 🟢 THE NEW UNIVERSAL ROLLING SUMMARY FIELD
    handoff_notes: str = Field(default="", description="Machine-to-machine notes for the next batch. MUST include active table column headers if a table spans across the batch cutoff.")

class ActiveState:
    def __init__(self):
        self.current_parent: Optional[str] = None
        self.current_section: Optional[str] = None
        self.current_type: Optional[str] = None
        self.last_page: int = 0
        self.handoff_notes: str = ""  # 🟢 HOLDS THE PREVIOUS BATCH HEADERS

# =====================================================================
# 3. AI Execution Call 
# =====================================================================
def run_navigation_batch(raw_text_batch: str, state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # 🟢 THE UNIVERSAL SYSTEM PROMPT
    system_instruction = (
        "You are the Universal Navigation Engine. Map the granular logical structure of the raw text.\n"
        "RULES:\n"
        "1. GRANULARITY: DO NOT group multi-page documents into a single section. Identify individual major headings, sub-headings, distinct topical shifts, and standalone data tables as SEPARATE sections or subsections.\n"
        "2. CHUNKING STRATEGY: For any data tables, matrices, or financial data, set 'content_type' to 'data_table' and ensure 'preserve_tables' is true in chunk_suggestions.\n"
        "3. MATCHING: Ensure the 'section' string in chunk_suggestions EXACTLY matches the 'title' in hierarchy.\n"
        "4. SUMMARY: Write a 1-sentence dense 'semantic_summary' explaining the specific contents of this section.\n"
        "5. ENTITIES: Extract 'key_entities' (core topics, organizations, unique IDs, or locations).\n"
        "6. DATA CLEANING: Extract text into 'normalized_text'. Forward-fill implicit row groupings.\n"
        "7. 🟢 HANDOFF STATE (CRITICAL): If a table, list, or paragraph is cut off at the end of this text batch, write a summary in 'handoff_notes'. You MUST include the exact column headers of any active table so the next batch knows what the numbers mean.\n\n"
        f"PREVIOUS BATCH STATE:\n"
        f"- Last Active Root: {state.current_parent or 'None'} | Last Subsection: {state.current_section or 'None'} | Last Page: {state.last_page}\n"
        f"- 🟢 MACHINE HANDOFF NOTES: {state.handoff_notes or 'No active tables or context carried over.'}\n\n"
        "OUTPUT EXACT JSON ONLY MATCHING THIS EXACT STRUCTURE (Do not use Markdown formatting):\n"
        "{\"hierarchy\": [{\"title\": \"...\", \"type\": \"...\", \"parent\": null, \"start_page\": 1, \"end_page\": 1, \"content_type\": \"...\", \"semantic_summary\": \"...\", \"key_entities\": [\"...\"], \"normalized_text\": \"...\"}], \"chunk_suggestions\": [{\"section\": \"...\", \"strategy\": \"row_preserving\", \"reason\": \"...\", \"preserve_tables\": true, \"preserve_lists\": true, \"split_triggers\": [\"...\"]}], \"confidence\": 1.0, \"notes\": \"\", \"handoff_notes\": \"...\"}"
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
            
            if start_idx != -1 and end_idx != -1:
                raw_json_str = raw_text[start_idx:end_idx + 1]
            else:
                raw_json_str = raw_text
                
            parsed_data = json.loads(raw_json_str)
            
            if isinstance(parsed_data, list):
                parsed_data = {"hierarchy": parsed_data}
                
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
            
            # Stitcher logic: Strict case-insensitive title matching
            for item in batch_response.hierarchy:
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
                
            # 🟢 PASS THE ROLLING SUMMARY TO THE NEXT BATCH
            active_state.handoff_notes = batch_response.handoff_notes
                
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

    print("💾 Saving Universal Stitched Hierarchy & Index Cards to Database...")

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