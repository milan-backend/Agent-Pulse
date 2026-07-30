import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schema for Navigation AI Output
# =====================================================================

class AISectionItem(BaseModel):
    section_code: str
    title: str
    parent_code: Optional[str] = None
    start_page: int
    end_page: int

class AINavigationMapSchema(BaseModel):
    document_title: str
    sections: List[AISectionItem] = []

# =====================================================================
# 2. Navigation AI Function (Now takes the condensed map string)
# =====================================================================
def run_navigation_ai(condensed_header_map: str) -> AINavigationMapSchema:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Navigation AI is missing.")

    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation & Outline AI for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "I am providing you with a condensed 'Header Map' extracted from a large document. It shows only the bold/large text and the page it was found on.\n"
        "Analyze this map and generate a structured Table of Contents.\n"
        "1. Assign logical section codes (e.g., '1.0', '1.1', '1.2', '2.0').\n"
        "2. Identify clear titles for each section or chapter.\n"
        "3. Specify parent_code for sub-sections (e.g., parent_code of '1.1' is '1.0').\n"
        "4. Set exact start_page and end_page boundaries based on when the next section begins.\n\n"
        "⚠️ STRICT OUTPUT FORMAT:\n"
        "You must return ONLY a raw JSON object matching this exact structure. Do not include markdown formatting.\n"
        "{\n"
        '  "document_title": "Title Here",\n'
        '  "sections": [\n'
        '    {"section_code": "1.0", "title": "Intro", "parent_code": null, "start_page": 1, "end_page": 4}\n'
        "  ]\n"
        "}"
    )

    prompt = f"CONDENSED HEADER MAP:\n\n{condensed_header_map}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

    return AINavigationMapSchema.model_validate_json(response.text)

# =====================================================================
# 3. Master Navigation Service Function
# =====================================================================
def build_and_save_navigation_map(
    db: Session,
    document_id: uuid.UUID,
    workspace_id: uuid.UUID,
    agent_id: Optional[uuid.UUID],
    pymupdf_toc: List[List[Any]],
    doc_page_count: int,
    ai_header_map: Optional[str] = None # 🟢 Changed to accept the string map
) -> List[DocumentSection]:
    saved_sections: List[DocumentSection] = []
    code_to_db_id: Dict[str, uuid.UUID] = {}

    if pymupdf_toc and len(pymupdf_toc) > 0:
        print("📌 Building Navigation Map using embedded PyMuPDF TOC...")
        for idx, item in enumerate(pymupdf_toc):
            level, title, start_page = item[0], item[1], item[2]
            end_page = pymupdf_toc[idx + 1][2] if idx + 1 < len(pymupdf_toc) else doc_page_count
            section_code = f"{level}.{idx + 1}"

            db_section = DocumentSection(
                document_id=document_id, workspace_id=workspace_id, agent_id=agent_id,
                section_code=section_code, title=title, start_page=start_page, end_page=end_page
            )
            db.add(db_section)
            db.flush()  
            saved_sections.append(db_section)
    else:
        print("🤖 No embedded TOC found. Triggering Navigation AI with Condensed Map...")
        if not ai_header_map:
            raise ValueError("Condensed Header Map required for Navigation AI fallback.")

        ai_nav_map = run_navigation_ai(ai_header_map)

        for item in ai_nav_map.sections:
            db_section = DocumentSection(
                document_id=document_id, workspace_id=workspace_id, agent_id=agent_id,
                section_code=item.section_code, title=item.title, start_page=item.start_page, end_page=item.end_page
            )
            db.add(db_section)
            db.flush()
            code_to_db_id[item.section_code] = db_section.id
            saved_sections.append(db_section)

        for item in ai_nav_map.sections:
            if item.parent_code and item.parent_code in code_to_db_id:
                child_sec = db.query(DocumentSection).get(code_to_db_id[item.section_code])
                if child_sec:
                    child_sec.parent_section_id = code_to_db_id[item.parent_code]

    db.commit()
    print(f"✅ Navigation Map created with {len(saved_sections)} sections.")
    return saved_sections