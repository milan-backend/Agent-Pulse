import os
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai
from google.genai import types  # 🟢 NEW: Official types for bulletproof schema

from app.models.new_arch import DocumentSection

# =====================================================================
# 1. Pydantic Schema for Internal Application Validation
# =====================================================================

class AISectionItem(BaseModel):
    section_code: str = Field(description="Logical code e.g., '1.0', '1.1', '2.0'")
    title: str = Field(description="Cleaned, meaningful section title.")
    parent_code: Optional[str] = Field(None, description="Parent section code if nested.")
    start_page: int
    end_page: int

class AINavigationMapSchema(BaseModel):
    document_title: str
    sections: List[AISectionItem] = []

# =====================================================================
# 2. Official GenAI Types Schema 
# (Guarantees zero INVALID_ARGUMENT errors from the API)
# =====================================================================

NAVIGATION_MAP_RESPONSE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "document_title": types.Schema(
            type=types.Type.STRING, 
            description="Title of the document"
        ),
        "sections": types.Schema(
            type=types.Type.ARRAY,
            items=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "section_code": types.Schema(type=types.Type.STRING, description="Logical code e.g. '1.0', '1.1'"),
                    "title": types.Schema(type=types.Type.STRING, description="Cleaned section title"),
                    "parent_code": types.Schema(type=types.Type.STRING, nullable=True, description="Parent section code if nested"),
                    "start_page": types.Schema(type=types.Type.INTEGER),
                    "end_page": types.Schema(type=types.Type.INTEGER)
                },
                required=["section_code", "title", "start_page", "end_page"]
            )
        )
    },
    required=["document_title", "sections"]
)

# =====================================================================
# 3. Navigation AI Function
# =====================================================================

def run_navigation_ai(condensed_header_map: str) -> AINavigationMapSchema:
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Navigation AI is missing.")

    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation & Outline AI for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "Analyze the provided 'Contextual Header Map' to generate a strictly structured Table of Contents.\n\n"
        "⚠️ CRITICAL RULES FOR REJECTION & FILTERING:\n"
        "- Do NOT treat table headers (e.g., 'S. No.', 'Marks', 'Credits') as sections.\n"
        "- Do NOT treat author names, publishers, or book references (e.g., 'G. Hadley', 'McGraw Hill') as sections.\n"
        "- Do NOT treat standalone numbers, bullet points, or page footers as sections.\n"
        "- Ignore fragments that are too short or lack semantic meaning.\n\n"
        "🧠 HIERARCHY & MERGING INSTRUCTIONS:\n"
        "- Detect repeating document patterns (e.g., Semester structure, Unit structure).\n"
        "- Merge broken or split headings if they logically belong together.\n"
        "- Assign logical hierarchical section codes (e.g., '1.0' for Semester III, '1.1' for Digital Electronics, '1.1.1' for Unit I).\n"
        "- Define exact start_page and end_page boundaries.\n\n"
        "⚠️ STRICT OUTPUT FORMAT:\n"
        "Return ONLY a raw JSON object matching the requested schema. No markdown."
    )

    prompt = f"CONTEXTUAL HEADER MAP:\n\n{condensed_header_map}"

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=NAVIGATION_MAP_RESPONSE_SCHEMA,
            temperature=0.0
        )
    )

    return AINavigationMapSchema.model_validate_json(response.text)

# =====================================================================
# 4. Master Navigation Service Function
# =====================================================================

def build_and_save_navigation_map(
    db: Session,
    document_id: uuid.UUID,
    workspace_id: uuid.UUID,
    agent_id: Optional[uuid.UUID],
    pymupdf_toc: List[List[Any]],
    doc_page_count: int,
    ai_header_map: Optional[str] = None
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
                document_id=document_id, 
                workspace_id=workspace_id, 
                agent_id=agent_id,
                section_code=section_code, 
                title=title, 
                start_page=start_page, 
                end_page=end_page
            )
            db.add(db_section)
            db.flush()  
            saved_sections.append(db_section)
    else:
        print("🤖 No embedded TOC found. Triggering Navigation AI with Contextual Map...")
        if not ai_header_map:
            raise ValueError("Contextual Header Map required for Navigation AI fallback.")

        # Truncate to safety threshold to prevent prompt overflow on massive files
        truncated_map = ai_header_map[:80000] if len(ai_header_map) > 80000 else ai_header_map
        
        ai_nav_map = run_navigation_ai(truncated_map)

        for item in ai_nav_map.sections:
            clean_title = item.title[:250].strip() if item.title else "Untitled Section"
            clean_code = item.section_code[:50].strip() if item.section_code else str(uuid.uuid4())[:8]
            
            db_section = DocumentSection(
                document_id=document_id, 
                workspace_id=workspace_id, 
                agent_id=agent_id,
                section_code=clean_code, 
                title=clean_title, 
                start_page=item.start_page, 
                end_page=item.end_page
            )
            db.add(db_section)
            db.flush()
            code_to_db_id[item.section_code] = db_section.id
            saved_sections.append(db_section)

        # Establish parent-child section relationships
        for item in ai_nav_map.sections:
            if item.parent_code and item.parent_code in code_to_db_id:
                child_sec = db.query(DocumentSection).get(code_to_db_id[item.section_code])
                if child_sec:
                    child_sec.parent_section_id = code_to_db_id[item.parent_code]

    db.commit()
    print(f"✅ Navigation Map created with {len(saved_sections)} valid sections.")
    return saved_sections