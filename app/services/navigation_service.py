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
# 1. PYDANTIC SCHEMAS (Streamlined for the New State Machine)
# =====================================================================
class HierarchyItem(BaseModel):
    title: str = Field(default="Untitled Section", description="Formal section title.")
    parent: Optional[str] = Field(default=None, description="Exact parent title, or null.")
    start_page: int = Field(default=1)
    end_page: int = Field(default=1)
    
    # 🟢 Semantic Routing & Keyword Nets
    content_type: str = Field(default="narrative", description="'narrative' or 'data_table'")
    semantic_summary: str = Field(default="No summary provided.")
    parent_keywords: str = Field(default="", description="Broad BM25 search keywords (e.g., 'Ministry, Budget, Education').")
    
    # 🟢 Table Handoff & State Machine Flags
    table_headers: Optional[str] = Field(default=None, description="If data_table, provide the exact Markdown column headers.")
    continues_on_next_page: bool = Field(default=False, description="CRITICAL: Set True if the table or paragraph is cut off at the bottom of the page.")
    
    normalized_text: str = Field(default="", description="The fully cleaned text for this section. DO NOT SUMMARIZE DATA.")

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = Field(default_factory=list)
    handoff_notes: str = Field(default="", description="If continuing to next page, output the last 2 table rows or cut-off sentence here.")

class ActiveState:
    def __init__(self):
        self.handoff_notes: str = ""  

# =====================================================================
# 2. AI EXECUTION (With Strict Anti-Laziness Mandates)
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
                        "temperature": 0.0, # Zero hallucination
                    }
                )
                data = json.loads(resp.text.strip(), strict=False)
                if isinstance(data, list): data = {"hierarchy": data}
                return NavigationBatchResponse(**data)
            except Exception as e:
                if attempt == 2: raise e
                time.sleep((attempt + 1) * 3)

    print(f"   -> 🧠 Running Navigation Engine on Page {smart_page.get('page_num')}...")
    
    # 🟢 STRICT ENTERPRISE PROMPT
    system_instruction = (
        "You are a strict Enterprise Navigation Engine. You parse Markdown text into hierarchical data.\n"
        "CRITICAL RULES - FAILURE IS NOT AN OPTION:\n"
        "1. PARENT-CHILD MAPPING: Use Markdown headings (# vs ##) to map the 'parent' relationships exactly.\n"
        "2. ANTI-LAZINESS MANDATE: When extracting 'normalized_text', you MUST extract every single word and table row exactly as written. DO NOT summarize, paraphrase, or use '...omitted for brevity'. Missing data will cause critical system failure.\n"
        "3. TABLE HANDLING: If you detect a table, set content_type to 'data_table' and extract the exact '| Header |' row into 'table_headers'.\n"
        "4. STATE MACHINE (BOUNDARY BLINDNESS): If a table or paragraph is cut off at the end of the page, you MUST set 'continues_on_next_page' to true, and write the last 2 rows/sentences into 'handoff_notes' so the next page can connect them.\n"
        f"🧠 CONTEXT HANDOFF FROM PREVIOUS PAGE:\n```text\n{state.handoff_notes}\n```\n"
    )
    
    text_contents = f"RAW PDF MARKDOWN (Page {smart_page.get('page_num')}):\n\n{smart_page.get('content_text', '')}"
    return call_ai_engine("models/gemini-3.1-flash-lite", system_instruction, text_contents)

# =====================================================================
# 3. MASTER STITCHING LOOP (PostgreSQL Database Linker)
# =====================================================================
def build_and_save_navigation_map(db: Session, document_id: uuid.UUID, workspace_id: uuid.UUID, smart_pages: List[Dict[str, Any]]) -> List[DocumentSection]:
    master_hierarchy = []
    active_state = ActiveState()

    for idx, page_payload in enumerate(smart_pages):
        try:
            batch_response = run_navigation_batch(page_payload, active_state)
            
            for item in batch_response.hierarchy:
                # 🟢 THE STATE MACHINE MERGE
                # If this section continues from the previous page, append it!
                if master_hierarchy and master_hierarchy[-1].title.strip().lower() == item.title.strip().lower() and master_hierarchy[-1].parent == item.parent:
                    master_hierarchy[-1].end_page = max(master_hierarchy[-1].end_page, item.end_page)
                    master_hierarchy[-1].normalized_text += "\n" + item.normalized_text
                    # Update continuation flag based on the NEW page's status
                    master_hierarchy[-1].continues_on_next_page = item.continues_on_next_page 
                else:
                    master_hierarchy.append(item)

            active_state.handoff_notes = batch_response.handoff_notes
        except Exception as e:
            print(f"⚠️ Failed to parse page {page_payload.get('page_num')}: {e}")

    saved_sections, path_to_db_id, title_to_full_path = [], {}, {}

    # 🟢 SAVE TO POSTGRESQL (The Relational Brain)
    for item in master_hierarchy:
        parent_full_path = title_to_full_path.get(item.parent, item.parent) if item.parent else ""
        full_path = f"{parent_full_path} > {item.title}" if item.parent else item.title
        title_to_full_path[item.title] = full_path

        # Determine Database Status
        db_status = "OPEN" if item.continues_on_next_page else "CLOSED"

        db_section = DocumentSection(
            document_id=document_id, 
            workspace_id=workspace_id, 
            title=item.title[:250], 
            parent_path=full_path[:500],
            status=db_status,                   # 🟢 New Database Column
            start_page=item.start_page, 
            end_page=item.end_page, 
            content_type=item.content_type,
            semantic_summary=item.semantic_summary, 
            parent_keywords=item.parent_keywords, # 🟢 New Keyword Net
            table_headers=item.table_headers      # 🟢 Stored for the 5-Row Chunker
        )
        # Store temporary text so the ChunkEngine can grab it later
        db_section._temp_text = item.normalized_text 
        
        db.add(db_section)
        db.flush() # Get the UUID instantly
        path_to_db_id[full_path] = db_section.id
        saved_sections.append(db_section)

    # 🟢 LINK THE CHILDREN TO THE PARENTS
    for item in master_hierarchy:
        if item.parent:
            child_id = path_to_db_id.get(title_to_full_path.get(item.title))
            parent_id = path_to_db_id.get(title_to_full_path.get(item.parent))
            if child_id and parent_id:
                child_sec = db.query(DocumentSection).filter_by(id=child_id).first()
                if child_sec: 
                    child_sec.parent_section_id = parent_id

    db.commit()
    return saved_sections