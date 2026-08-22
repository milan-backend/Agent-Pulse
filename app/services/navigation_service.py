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
    type: str = Field(default="narrative_paragraph", description="'container', 'table_section', etc.")
    parent: Optional[str] = Field(default=None, description="Exact parent title, or null.")
    start_page: int = Field(default=1)
    end_page: int = Field(default=1)
    content_type: str = Field(default="narrative_paragraph")
    semantic_summary: str = Field(default="No summary provided.")
    key_entities: List[str] = Field(default_factory=list)
    normalized_text: str = Field(default="", description="The fully cleaned text for this section.")

# 🟢 NEW: Schema for your Atomic Row Grouping concept!
class RowGroup(BaseModel):
    start_row: int = Field(description="Starting row number for this connected group (1-indexed, excluding headers).")
    end_row: int = Field(description="Ending row number for this connected group.")
    group_reason: str = Field(description="Why these rows must stay together.")

class ChunkSuggestion(BaseModel):
    section: str = Field(default="Untitled Section")
    strategy: str = Field(default="standard")
    preserve_tables: bool = Field(default=False)
    table_headers: Optional[str] = Field(default="")
    row_groupings: List[RowGroup] = Field(
        default_factory=list,
        description="If this is a table, provide the exact row index boundaries that must be grouped together into unbreakable chunks."
    )

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = Field(default_factory=list)
    chunk_suggestions: List[ChunkSuggestion] = Field(default_factory=list)
    handoff_notes: str = Field(default="")

class ActiveState:
    def __init__(self):
        self.handoff_notes: str = ""  
        self.trailing_memory: str = "" 

# =====================================================================
# 2. AI Execution Call (UNIFIED ROUTER)
# =====================================================================
def run_navigation_batch(smart_page: Dict[str, Any], state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)

    def call_ai_engine(model_name: str, sys_instruct: str, payload: Any) -> NavigationBatchResponse:
        for attempt in range(3):
            try:
                resp = client.models.generate_content(
                    model=model_name,
                    contents=payload,
                    config={
                        "system_instruction": sys_instruct,
                        "response_mime_type": "application/json",
                        "response_schema": NavigationBatchResponse,
                        "temperature": 0.0,
                    }
                )
                data = json.loads(resp.text.strip(), strict=False)
                if isinstance(data, list): data = {"hierarchy": data}
                return NavigationBatchResponse(**data)
            except Exception as e:
                if attempt == 2: raise e
                time.sleep((attempt + 1) * 3)

    print(f"   -> 🧠 Running Unified Navigation Engine on Page {smart_page.get('page_num')}...")
    
    system_instruction = (
        "You are the Unified Navigation Engine for a RAG pipeline. Parse pure Markdown text containing BOTH narrative paragraphs and data tables.\n"
        "RULES:\n"
        "1. HIERARCHICAL MAPPING (CRITICAL): You MUST build a strict parent-child map using the 'hierarchy' array. Use Markdown heading levels (# vs ## vs ###) to determine relationships. If a section is '##', its 'parent' is the exact title of the most recent '#' heading. This builds the exact Table of Contents.\n"
        "2. STRICT HEADING SPLITTING: Group text logically based on Markdown Headings. A single section MUST NEVER exceed 400 words.\n"
        "3. AGGRESSIVE ENTITY EXTRACTION: Extract EXACT proper nouns and acronyms (e.g., IIT, NIT, ABC, PM-USHA) from both paragraphs AND tables into 'key_entities'.\n"
        "4. TABLE HANDLING: If you see a Markdown table (rows starting with |), set 'content_type' to 'data_table' and 'preserve_tables' to true.\n"
        "5. TABLE ROW GROUPING (CRITICAL): If you detect a table, you MUST identify semantic relationships between rows. Output `row_groupings` to tell the Chunk Engine exactly which rows belong together. For example, if row 1 is standalone, output start_row: 1, end_row: 1. If rows 2 to 5 are connected sub-items, output start_row: 2, end_row: 5. The Chunk Engine will treat these groups as unbreakable blocks.\n"
        "6. HANDOFF STATE: If a paragraph or table is cut off, write the broken sentence or last 3 table rows in 'handoff_notes'.\n\n"
        f"🧠 CONTINUOUS MEMORY LEDGER:\n```text\n{state.handoff_notes or state.trailing_memory}\n```\n"
    )
    
    text_contents = f"RAW PDF MARKDOWN (Page {smart_page.get('page_num')}):\n\n{smart_page.get('content_text', '')}"
    return call_ai_engine("models/gemini-3.1-flash-lite", system_instruction, text_contents)

# =====================================================================
# 3. Master Navigation & Stitching Loop 
# =====================================================================
def build_and_save_navigation_map(db: Session, document_id: uuid.UUID, workspace_id: uuid.UUID, agent_id: Optional[uuid.UUID], smart_pages: List[Dict[str, Any]]) -> tuple[List[DocumentSection], List[ChunkSuggestion]]:
    master_hierarchy, master_chunk_suggestions = [], []
    active_state = ActiveState()

    for idx, page_payload in enumerate(smart_pages):
        try:
            batch_response = run_navigation_batch(page_payload, active_state)
            
            for item in batch_response.hierarchy:
                if master_hierarchy and master_hierarchy[-1].title.strip().lower() == item.title.strip().lower() and master_hierarchy[-1].parent == item.parent:
                    master_hierarchy[-1].end_page = max(master_hierarchy[-1].end_page, item.end_page)
                    master_hierarchy[-1].normalized_text += "\n" + item.normalized_text
                else:
                    master_hierarchy.append(item)

            for chunk_strat in batch_response.chunk_suggestions:
                master_chunk_suggestions.append(chunk_strat)

            if master_hierarchy and master_hierarchy[-1].normalized_text:
                active_state.trailing_memory = master_hierarchy[-1].normalized_text[-400:]
            active_state.handoff_notes = batch_response.handoff_notes
        except Exception as e:
            print(f"⚠️ Failed to parse page {page_payload.get('page_num')}: {e}")

    chunk_hint_map = {c.section.strip().lower(): c.model_dump() for c in master_chunk_suggestions}
    saved_sections, path_to_db_id, title_to_full_path = [], {}, {}

    for item in master_hierarchy:
        parent_full_path = title_to_full_path.get(item.parent, item.parent) if item.parent else ""
        full_path = f"{parent_full_path} > {item.title}" if item.parent else item.title
        title_to_full_path[item.title] = full_path

        matched_hint = chunk_hint_map.get(item.title.strip().lower(), {})
        if not matched_hint and item.content_type in ["master_scheme_table", "data_table"]:
            matched_hint = {"preserve_tables": True, "preserve_lists": True, "row_groupings": []}
            
        matched_hint["normalized_text"] = item.normalized_text
        matched_hint["section"] = item.title

        db_section = DocumentSection(
            document_id=document_id, workspace_id=workspace_id, agent_id=agent_id,
            section_code=str(uuid.uuid4())[:8], title=item.title[:250], parent_path=full_path[:500],
            start_page=item.start_page, end_page=item.end_page, content_type=item.content_type,
            semantic_summary=item.semantic_summary, key_entities=item.key_entities, chunking_strategy_hint=matched_hint
        )
        db.add(db_section)
        db.flush()
        path_to_db_id[full_path] = db_section.id
        saved_sections.append(db_section)

    for item in master_hierarchy:
        if item.parent:
            child_id = path_to_db_id.get(title_to_full_path.get(item.title))
            parent_id = path_to_db_id.get(title_to_full_path.get(item.parent))
            if child_id and parent_id:
                child_sec = db.query(DocumentSection).filter_by(id=child_id).first()
                if child_sec: child_sec.parent_section_id = parent_id

    db.commit()
    return saved_sections, master_chunk_suggestions