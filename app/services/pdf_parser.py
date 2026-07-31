import fitz
import json
from typing import List, Dict

def calculate_base_font_size(doc: fitz.Document, sample_pages: int = 10) -> float:
    """
    Scans the first few pages to determine the most common font size (body text).
    """
    font_sizes = []
    limit = min(sample_pages, doc.page_count)
    
    for page_num in range(limit):
        page = doc[page_num]
        blocks = page.get_text("dict").get("blocks", [])
        for block in blocks:
            if block.get("type") == 0:  # 0 means text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            font_sizes.append(round(span["size"], 1))
                            
    if font_sizes:
        return max(set(font_sizes), key=font_sizes.count)
    return 11.0

def generate_page_reasoning(doc: fitz.Document) -> str:
    """
    Scans ALL pages and generates a structured JSON array of observations
    and reasoning for the Navigation AI to read.
    """
    base_font = calculate_base_font_size(doc)
    header_threshold = base_font * 1.15  # 15% larger than body text
    
    ai_payload: List[Dict] = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        blocks = page.get_text("dict").get("blocks", [])
        
        page_headings = []
        has_body_text = False
        has_table_elements = False
        
        for block in blocks:
            if block.get("type") != 0:
                has_table_elements = True
                continue
                
            for line in block.get("lines", []):
                line_text = ""
                is_heading = False
                
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                        
                    size = span["size"]
                    is_bold = bool(span["flags"] & 16) or "Bold" in span["font"]
                    
                    if size >= header_threshold or is_bold:
                        is_heading = True
                        line_text += text + " "
                    elif size == base_font:
                        has_body_text = True
                
                if is_heading and len(line_text.strip()) > 3:
                    page_headings.append(line_text.strip())

        if page_headings:
            reasoning = f"HEADING_DETECTED: Found text larger than base font ({base_font}pt) or flagged as Bold."
            if has_table_elements:
                reasoning += " TABLE_OR_GRAPHICS_DETECTED: Non-text vector blocks present."
                
            ai_payload.append({
                "page": page_num + 1,
                "extracted_text": " | ".join(page_headings),
                "python_reasoning": reasoning
            })
            
        elif has_body_text:
            ai_payload.append({
                "page": page_num + 1,
                "extracted_text": "None",
                "python_reasoning": "CONTINUATION_PAGE: Only standard body text detected. No structural headings found."
            })
            
        else:
            ai_payload.append({
                "page": page_num + 1,
                "extracted_text": "None",
                "python_reasoning": "BLANK_OR_IMAGE_PAGE: No readable body text or headings detected."
            })
            
    return json.dumps(ai_payload, indent=2)

def extract_document_structure(pdf_path: str) -> dict:
    """
    Main entry point called by rag_tasks.py.
    Prioritizes embedded TOC, falls back to Advanced Sensor Reasoning.
    """
    doc = fitz.open(pdf_path) 
    toc = doc.get_toc(simple=True)
    
    # If the PDF has a native table of contents built-in, use it to save AI costs!
    if toc:
        doc.close()
        return {
            "status": "success",
            "toc": toc,
            "ai_header_map": None
        }
    
    # Otherwise, generate the reasoning payload for Gemini
    print("🤖 No embedded TOC found. Generating AI Sensor Payload...")
    ai_payload = generate_page_reasoning(doc)
    doc.close() 
    
    return {
        "status": "success",
        "toc": [],
        "ai_header_map": ai_payload
    }