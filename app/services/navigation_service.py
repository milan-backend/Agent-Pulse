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
# 3. AI Execution Call (DYNAMIC CASCADING ROUTER)
# =====================================================================
def run_navigation_batch(smart_page: Dict[str, Any], state: ActiveState) -> NavigationBatchResponse:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Navigation AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # 🟢 STEP 1: INSTANT LOCAL TABLE ROUTING ($0 / 0ms Latency)
    has_table = smart_page.get("has_table", False)
        
    # 🟢 STEP 2: PARALLEL EXECUTION LOGIC (The "Parallel Brains" Architecture)
    
    combined_hierarchy = []
    combined_chunk_suggestions = []
    final_handoff_notes = ""

    # Reusable caller with retry logic
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
                        "max_output_tokens": 8192
                    }
                )
                data = json.loads(resp.text.strip(), strict=False)
                if isinstance(data, list):
                    data = {"hierarchy": data}
                return NavigationBatchResponse(**data)
            except Exception as e:
                if attempt == 2:
                    raise e
                time.sleep((attempt + 1) * 3)

    # =========================================================
    # 🧠 BRAIN 1: TEXT ENGINE (Runs on every page for paragraphs)
    # =========================================================
    print(f"   -> 📝 Running Text Engine (3.1) on Page {smart_page.get('page_num')}...")
    text_instruction = (
        "You are the Text Navigation Engine for a RAG pipeline. Your job is to parse narrative text and group it logically.\n"
        "CRITICAL DIRECTIVE: You must be absolutely perfect in your extraction. Your output feeds directly into ChromaDB. If you miss keywords or generate poor summaries, ChromaDB will fail to fetch this information when the user asks a question!\n"
        "RULES:\n"
        "1. STRICT HEADING SPLITTING & 400-WORD LIMIT: Group text logically based on Markdown Headings. A single section MUST NEVER exceed 400 words. If a topic is longer, split it, but you MUST write the exact same Markdown Heading at the beginning of EVERY split section.\n"
        "2. AGGRESSIVE ENTITY EXTRACTION: Write a dense 'semantic_summary'. You MUST extract the EXACT proper nouns and acronyms (e.g., IIT, NIT, ABC, PM-USHA) into the 'key_entities' array. Do not use generic terms.\n"
        "3. IGNORE TABLE MARKERS: If you see '[🚨 TABLE DETECTED - ROUTE THIS SECTION TO VISION AI 🚨]', completely ignore it and process only the surrounding narrative paragraphs.\n"
        "4. CONTENT TYPE: Set 'content_type' to 'narrative_paragraph' and 'preserve_tables' to false.\n"
        "5. HANDOFF STATE: If a paragraph is cut off, write the exact Markdown Heading and the broken sentence in 'handoff_notes' so the next page can stitch it seamlessly.\n\n"
        f"🧠 CONTINUOUS MEMORY LEDGER:\n"
        f"```text\n{state.handoff_notes or state.trailing_memory or 'No previous memory.'}\n```\n"
    )
    text_contents = f"RAW PDF TEXT (Page {smart_page.get('page_num')}):\n\n{smart_page['content_text']}"
    
    text_resp = call_ai_engine("models/gemini-3.1-flash-lite", text_instruction, text_contents)
    combined_hierarchy.extend(text_resp.hierarchy)
    combined_chunk_suggestions.extend(text_resp.chunk_suggestions)
    final_handoff_notes = text_resp.handoff_notes

    # =========================================================
    # 🧠 BRAIN 2: VISION ENGINE (Runs strictly for tables)
    # =========================================================
    if has_table:
        print(f"   -> 📊 Table Detected! Running Vision Engine (3.6) on Page {smart_page.get('page_num')} for tables...")
        vision_instruction = (
            "You are the Vision Table Extraction Engine for a RAG pipeline. Your ONLY job is to extract visual grids, matrices, and tables.\n"
            "CRITICAL DIRECTIVE: You must be absolutely perfect in your extraction. Your output feeds directly into ChromaDB. If you miss keywords, lose headers, or chunk poorly, ChromaDB will fail to fetch this table when the user asks a question!\n"
            "RULES:\n"
            "1. STRICT TABLE ONLY & 400-WORD LIMIT: ONLY extract structured visual tables. You MUST NEVER create a table chunk larger than 400 words. If a table is massive, split it into multiple smaller sections. Keep connected rows together. NEVER break a single row's data. EVERY split chunk MUST start with the exact Markdown Table Headers.\n"
            "2. AGGRESSIVE ENTITY EXTRACTION: Even though it's a table, you MUST extract exact acronyms (e.g., IIT, NIT, IIM) and proper nouns from the rows into the 'key_entities' array. Do not use generic terms.\n"
            "3. HEADER EXTRACTION: Extract column headers into the 'table_headers' field.\n"
            "4. TABLE ISOLATION: Set 'content_type' to 'data_table' and 'preserve_tables' to true.\n"
            "5. TABLE HANDOFF NOTES (LAST 3 ROWS): If a table spans off the bottom, your 'handoff_notes' MUST include: 1) The exact Table Headers, and 2) The EXACT LAST 3 ROWS of data. The next AI agent needs this to stitch the table without duplicating data.\n\n"
            f"🧠 CONTINUOUS MEMORY LEDGER (CRITICAL):\n"
            f"```markdown\n{state.handoff_notes or state.trailing_memory or 'No previous memory.'}\n```\n"
        )
        vision_contents = [
            types.Part.from_bytes(data=smart_page["content_image"], mime_type="image/png"),
            f"Analyze this document image (Page {smart_page.get('page_num')}) and extract ONLY the tables into structured JSON."
        ]
        
        vision_resp = call_ai_engine("models/gemini-3.6-flash", vision_instruction, vision_contents)
        combined_hierarchy.extend(vision_resp.hierarchy)
        combined_chunk_suggestions.extend(vision_resp.chunk_suggestions)
        
        if vision_resp.handoff_notes:
            final_handoff_notes += f"\n[Table Notes]: {vision_resp.handoff_notes}"

    # 🟢 STEP 3: UNIFY AND RETURN
    return NavigationBatchResponse(
        hierarchy=combined_hierarchy,
        chunk_suggestions=combined_chunk_suggestions,
        confidence=1.0,
        handoff_notes=final_handoff_notes
    )

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