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
    section_code: str = Field(description="Hierarchical code e.g., '1.0', '1.1', '1.1.1', '2.0'.")
    title: str = Field(description="Title or header of the section.")
    parent_code: Optional[str] = Field(default=None, description="Section code of parent header if nested, else None.")
    start_page: int = Field(description="Starting page number (1-indexed).")
    end_page: int = Field(description="Ending page number (1-indexed).")


class AINavigationMapSchema(BaseModel):
    document_title: str = Field(description="Inferred or extracted title of the document.")
    sections: List[AISectionItem] = Field(default_factory=list, description="Ordered hierarchical list of sections.")


# =====================================================================
# 2. Navigation AI Function (Fallback when no TOC in PDF)
# =====================================================================

def run_navigation_ai(page_previews: List[Dict[str, Any]]) -> AINavigationMapSchema:
    """
    Navigation AI: Analyzes sample page headings/text previews to construct 
    a structured Table of Contents with hierarchical section codes.
    """
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Navigation AI is missing.")

    client = genai.Client(api_key=gemini_key)

    system_instruction = (
        "You are the Core Navigation & Outline AI for AgentPulse.\n\n"
        "🎯 MISSION:\n"
        "Analyze page-by-page text previews from a document and generate a structured Table of Contents.\n"
        "1. Assign logical section codes (e.g., '1.0', '1.1', '1.2', '2.0').\n"
        "2. Identify clear titles for each section or chapter.\n"
        "3. Specify parent_code for sub-sections (e.g., parent_code of '1.1' is '1.0').\n"
        "4. Set exact start_page and end_page boundaries.\n"
    )

    context_lines = []
    for page in page_previews[:30]:  # Inspect first 30 page previews
        context_lines.append(f"--- PAGE {page['page_num']} ---")
        context_lines.append(page['text_snippet'][:500])

    prompt = "DOCUMENT PAGE PREVIEWS:\n\n" + "\n".join(context_lines)

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": AINavigationMapSchema,
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
    page_text_samples: Optional[List[Dict[str, Any]]] = None
) -> List[DocumentSection]:
    """
    Builds the Navigation Map using PyMuPDF TOC if available, or Navigation AI as fallback.
    Saves section hierarchy to PostgreSQL `document_sections` table.
    """
    saved_sections: List[DocumentSection] = []
    code_to_db_id: Dict[str, uuid.UUID] = {}

    # MODE A: Embedded PyMuPDF Table of Contents exists
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
            db.flush()  # Flush to obtain UUID primary key
            
            saved_sections.append(db_section)

    # MODE B: Fallback to Navigation AI
    else:
        print("🤖 No embedded TOC found. Triggering Navigation AI...")
        if not page_text_samples:
            raise ValueError("Page text samples required for Navigation AI fallback.")

        ai_nav_map = run_navigation_ai(page_text_samples)

        # First pass: Insert sections without parent foreign keys
        for item in ai_nav_map.sections:
            db_section = DocumentSection(
                document_id=document_id,
                workspace_id=workspace_id,
                agent_id=agent_id,
                section_code=item.section_code,
                title=item.title,
                start_page=item.start_page,
                end_page=item.end_page
            )
            db.add(db_section)
            db.flush()
            
            code_to_db_id[item.section_code] = db_section.id
            saved_sections.append(db_section)

        # Second pass: Link parent_section_id trees
        for item in ai_nav_map.sections:
            if item.parent_code and item.parent_code in code_to_db_id:
                child_db_id = code_to_db_id[item.section_code]
                parent_db_id = code_to_db_id[item.parent_code]
                
                child_sec = db.query(DocumentSection).get(child_db_id)
                if child_sec:
                    child_sec.parent_section_id = parent_db_id

    db.commit()
    print(f"✅ Navigation Map created with {len(saved_sections)} sections.")
    return saved_sections