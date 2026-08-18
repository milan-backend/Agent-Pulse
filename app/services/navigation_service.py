import os
import uuid
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai
from google.genai import types

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
    content_type: str = Field(default="data_table")
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
    table_headers: Optional[str] = Field(default="", description="If this section contains a table, extract the exact column headers here separated by a pipe '|'.")

class NavigationBatchResponse(BaseModel):
    hierarchy: List[HierarchyItem] = Field(default_factory=list)
    chunk_suggestions: List[ChunkSuggestion] = Field(default_factory=list)
    confidence: float = Field(default=1.0)
    notes: str = Field(default="")
    handoff_notes: str = Field(default="", description="Machine-to-machine notes for the next batch. MUST include active table column headers if a table spans across the batch cutoff.")

class ActiveState:
    def __init__(self):
        self.current_parent: Optional[str] = None
        self.current_section: Optional[str] = None
        self.current_type: Optional[str] = None
        self.last_page: int = 0
        self.handoff_notes: str = ""  
        self.trailing_memory: str = "" 


# =====================================================================
# 3. AI Execution Call (DUAL-ENGINE ROUTER WITH SPLIT PROMPTS)
# =====================================================================
def run_navigation_batch(smart_page: Dict[str, Any], state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # 🟢 DUAL-ENGINE ROUTING LOGIC
    is_vision = smart_page.get("type") == "table_image"
    target_model = "gemini-1.5-pro" if is_vision else "gemini-3.1-flash-lite"
    
    print(f"   -> 🧠 Activating {target_model} for {smart_page.get('type')} on Page {smart_page.get('page_num')}")

    # 🟢 SPLIT SYSTEM INSTRUCTIONS BASED ON PAYLOAD TYPE
    if is_vision:
        # 📊 INSTRUCTIONS ONLY FOR THE VISION MODEL (TABLES)
        system_instruction = (
            "You are the Vision Table Extraction Engine. Your ONLY job is to perfectly map visual grids and tables into structured data.\n"
            "RULES:\n"
            "1. UNIVERSAL MARKDOWN & MERGED CELLS: Format grids as strict Markdown tables. Markdown does NOT support merged cells. Explicitly fill in blank merged cells with their parent values.\n"
            "2. 🟢 ATOMIC SEMANTIC CHUNKING (CRITICAL): Whenever you see a logical semantic grouping end (e.g., all classes for Monday are finished, or a time block ends), you MUST insert the exact text `<!-- SEMANTIC_BREAK -->` on a new line before continuing to the next group.\n"
            "3. HEADER EXTRACTION: You MUST extract the column headers and place them in the 'table_headers' field.\n"
            "4. TABLE ISOLATION: Set 'content_type' to 'data_table' and 'preserve_tables' to true.\n"
            "5. HANDOFF STATE: Write a summary in 'handoff_notes'. You MUST include the exact column headers if a table spans off the bottom of the page.\n\n"
            f"🧠 CONTINUOUS MEMORY LEDGER (CRITICAL):\n"
            f"You are processing a new page. The text below is the EXACT MARKDOWN you generated at the very end of the previous page.\n"
            f"```markdown\n{state.trailing_memory or 'No previous memory. This is the start of the document.'}\n```\n"
            f"If the memory shows an incomplete table, you MUST continue generating the rest of the table using the exact same column structure!\n\n"
        )
    else:
        # 📝 INSTRUCTIONS ONLY FOR THE TEXT MODEL (PARAGRAPHS)
        system_instruction = (
            "You are the Text Navigation Engine. Your job is to map the granular logical structure of the narrative text.\n"
            "RULES:\n"
            "1. STRICT HEADING SPLITTING (CRITICAL): EVERY TIME you encounter a new major heading or a distinct shift in topic, you MUST start a new, completely separate section in the hierarchy.\n"
            "2. BOUNDED ENTITY EXTRACTION: Write a 1-sentence dense 'semantic_summary'. Extract key entities (MAX 15). Do NOT extract raw numbers.\n"
            "3. CONTENT TYPE: This is narrative text. Set 'content_type' to 'narrative_paragraph' and 'preserve_tables' to false.\n"
            "4. HANDOFF STATE: If a paragraph is cut off at the end of this text batch, write a brief summary in 'handoff_notes' so the next batch knows the context.\n\n"
            f"🧠 CONTINUOUS MEMORY LEDGER:\n"
            f"You are processing a new page. The text below is the last thing generated on the previous page.\n"
            f"```text\n{state.trailing_memory or 'No previous memory.'}\n```\n"
            f"PREVIOUS BATCH STATE:\n"
            f"- Last Active Root: {state.current_parent or 'None'} | Last Subsection: {state.current_section or 'None'}\n\n"
        )

    # 🟢 JSON SCHEMA ENFORCEMENT STRING (Appended to both)
    schema_enforcement = (
        "OUTPUT EXACT JSON ONLY MATCHING THIS EXACT STRUCTURE (Do not use Markdown formatting for the JSON wrapper):\n"
        "{\"hierarchy\": [{\"title\": \"...\", \"type\": \"...\", \"parent\": null, \"start_page\": 1, \"end_page\": 1, \"content_type\": \"...\", \"semantic_summary\": \"...\", \"key_entities\": [\"...\"], \"normalized_text\": \"...\"}], \"chunk_suggestions\": [{\"section\": \"...\", \"strategy\": \"row_preserving\", \"reason\": \"...\", \"preserve_tables\": true, \"preserve_lists\": true, \"split_triggers\": [\"...\"], \"table_headers\": \"...\"}], \"confidence\": 1.0, \"notes\": \"\", \"handoff_notes\": \"...\"}"
    )
    
    system_instruction += schema_enforcement

    # 🟢 PAYLOAD CONSTRUCTION
    if is_vision:
        contents = [
            types.Part.from_bytes(data=smart_page["content"], mime_type="image/png"),
            f"Analyze this document image (Page {smart_page.get('page_num')}) and build the JSON hierarchy."
        ]
    else:
        contents = f"RAW PDF TEXT (Page {smart_page.get('page_num')}):\n\n{smart_page['content']}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=target_model, 
                contents=contents,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "temperature": 0.0,
                    "max_output_tokens": 8192 
                }
            )

            raw_text = response.text.strip()
            
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                raw_json_str = raw_text[start_idx:end_idx + 1]
            else:
                raw_json_str = raw_text
                
            parsed_data = json.loads(raw_json_str, strict=False)
            if isinstance(parsed_data, list):
                parsed_data = {"hierarchy": parsed_data}
                
            return NavigationBatchResponse(**parsed_data)

        except Exception as e:
            if ("503" in str(e) or "UNAVAILABLE" in str(e) or "429" in str(e)) and attempt < max_retries - 1:
                print(f"⚠️ API Busy ({str(e)[:30]}). Retrying in {(attempt + 1) * 3}s...")
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
    smart_pages: List[Dict[str, Any]]  
) -> tuple[List[DocumentSection], List[ChunkSuggestion]]:
    
    master_hierarchy: List[HierarchyItem] = []
    master_chunk_suggestions: List[ChunkSuggestion] = []
    active_state = ActiveState()

    print(f"🤖 Processing {len(smart_pages)} pages through Dual-Engine Navigation AI...")

    for idx, page_payload in enumerate(smart_pages):
        try:
            batch_response = run_navigation_batch(page_payload, active_state)
            
            print(f"\n{'='*80}")
            print(f"🧠 [X-RAY] RAW OUTPUT (PAGE {page_payload.get('page_num')}):")
            print(f"📝 Handoff Notes Received: {active_state.handoff_notes or 'None'}")
            print(json.dumps(batch_response.model_dump(), indent=2))
            print(f"{'='*80}\n")
            
            # Stitcher logic: Connect pages seamlessly
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

                # 🟢 FORCEFUL MEMORY CAPTURE: Grab the last 400 characters of the stitched text!
                if last_item.normalized_text:
                    active_state.trailing_memory = last_item.normalized_text[-400:]
                    
            # 🟢 PASS THE ROLLING SUMMARY TO THE NEXT BATCH
            active_state.handoff_notes = batch_response.handoff_notes
                
        except Exception as e:
            print(f"⚠️ Failed to parse page {page_payload.get('page_num')}: {e}")

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

        matched_hint = chunk_hint_map.get(item.title.strip().lower(), {})
        if not matched_hint and item.content_type in ["master_scheme_table", "data_table"]:
            matched_hint = {"preserve_tables": True, "preserve_lists": True, "strategy": "row_preserving", "table_headers": ""}
            
        matched_hint["normalized_text"] = item.normalized_text
        matched_hint["table_headers"] = chunk_hint_map.get(item.title.strip().lower(), {}).get("table_headers", "")

        print(f"\n{'='*60}")
        print(f"🛠️ [TRANSPARENCY] NAVIGATION AI BUILT SECTION: {item.title}")
        print(f"🧩 TYPE RECOGNIZED: {item.content_type}")
        print(f"📊 CHUNKING STRATEGY ASSIGNED: {json.dumps(matched_hint, indent=2)}")
        print(f"📄 NORMALIZED TEXT (PREVIEW):\n{item.normalized_text[:200]}...")
        print(f"{'='*60}\n")

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

    # Re-link the Parent/Child hierarchy mapping
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