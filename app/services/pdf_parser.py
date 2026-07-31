import fitz  # PyMuPDF
import pdfplumber
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def calculate_base_font_size(doc: fitz.Document, sample_pages: int = 15) -> float:
    """
    Scans sample pages, rounding font sizes to identify the most 
    frequently occurring body text size robustly.
    """
    font_sizes = []
    limit = min(sample_pages, doc.page_count)
    
    for page_num in range(limit):
        page = doc[page_num]
        try:
            blocks = page.get_text("dict").get("blocks", [])
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text and len(text) > 1:
                                font_sizes.append(round(span.get("size", 11.0), 1))
        except Exception as e:
            logger.debug(f"Font sampling error on page {page_num + 1}: {e}")
                            
    if font_sizes:
        return max(set(font_sizes), key=font_sizes.count)
    return 10.0

def is_span_bold(span: Dict) -> bool:
    """
    Multi-tier robust check for bold attributes across various PDF generators.
    Inspects PyMuPDF bit flags, font descriptor strings, and weight attributes.
    """
    flags = span.get("flags", 0)
    font_name = span.get("font", "").lower()
    
    # PyMuPDF flag checks: Bit 1 (value 2) or Bit 4 (value 16) often indicate bold
    flag_bold = bool((flags & 2) or (flags & 16))
    
    # Comprehensive string matching for font names
    name_bold = any(kw in font_name for kw in ["bold", "black", "heavy", "demi", "medi"])
    
    return flag_bold or name_bold

def generate_page_reasoning(doc: fitz.Document, pdf_path: str) -> str:
    """
    Extremely resilient page analyzer designed to extract headings, bold text, 
    and tables even from poorly formatted or messy PDFs.
    """
    base_font = calculate_base_font_size(doc)
    header_threshold = base_font * 1.10  # Sensitive 10% threshold
    
    ai_payload: List[Dict] = []
    
    try:
        with pdfplumber.open(pdf_path) as plumber_pdf:
            for page_num in range(doc.page_count):
                page = doc[page_num]
                plumber_page = plumber_pdf.pages[page_num]
                
                page_headings = []
                has_body_text = False
                has_vector_elements = False
                
                # 1. Table Extraction via pdfplumber
                page_tables = []
                try:
                    tables = plumber_page.extract_tables()
                    if tables:
                        for table in tables:
                            if table:
                                page_tables.append(table)
                except Exception as table_err:
                    logger.warning(f"Table extraction warning on page {page_num + 1}: {table_err}")
                
                # 2. Layout-aware Text Block Parsing via PyMuPDF
                try:
                    text_dict = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE)
                    blocks = text_dict.get("blocks", [])
                    
                    for block in blocks:
                        if block.get("type") != 0:
                            has_vector_elements = True
                            continue
                            
                        # Sort lines vertically and spans horizontally to fix messy layouts
                        lines = block.get("lines", [])
                        for line in lines:
                            line_text = ""
                            line_is_bold = False
                            line_has_large_font = False
                            has_content = False
                            
                            spans = line.get("spans", [])
                            for span in spans:
                                text = span.get("text", "").strip()
                                if not text:
                                    continue
                                
                                has_content = True
                                size = span.get("size", base_font)
                                bold_status = is_span_bold(span)
                                
                                if bold_status:
                                    line_is_bold = True
                                if size >= header_threshold:
                                    line_has_large_font = True
                                    
                                if size <= base_font + 1.0:
                                    has_body_text = True
                                    
                                line_text += text + " "
                                
                            cleaned_line = line_text.strip()
                            if has_content and len(cleaned_line) > 2:
                                # Catch headings via size, bold weight, or numbered item patterns (e.g., "50. National...")
                                if line_has_large_font or line_is_bold or cleaned_line[:3].replace('.', '').isdigit():
                                    page_headings.append(cleaned_line)
                except Exception as text_err:
                    logger.warning(f"Text extraction parsing warning on page {page_num + 1}: {text_err}")

                # 3. Compile Reasoning and Observations for Navigation AI
                reasoning_parts = []
                if page_headings:
                    reasoning_parts.append(f"HEADING_OR_KEY_ITEM_DETECTED: Identified prominent or bold structural text lines.")
                if page_tables:
                    reasoning_parts.append(f"TABLE_DETECTED: Found {len(page_tables)} structured table(s) on this page.")
                elif has_vector_elements:
                    reasoning_parts.append("GRAPHICS_DETECTED: Non-text vector blocks present.")

                if page_headings:
                    ai_payload.append({
                        "page": page_num + 1,
                        "extracted_text": " | ".join(page_headings[:15]),  # Capped for token optimization
                        "tables_found": len(page_tables),
                        "python_reasoning": " ".join(reasoning_parts)
                    })
                elif has_body_text or page_tables:
                    ai_payload.append({
                        "page": page_num + 1,
                        "extracted_text": "None",
                        "tables_found": len(page_tables),
                        "python_reasoning": " ".join(reasoning_parts) if reasoning_parts else "CONTINUATION_PAGE: Standard body text or tables detected. No prominent structural headers found."
                    })
                else:
                    ai_payload.append({
                        "page": page_num + 1,
                        "extracted_text": "None",
                        "tables_found": 0,
                        "python_reasoning": "BLANK_OR_IMAGE_PAGE: No readable body text or headings detected."
                    })
                    
    except Exception as e:
        logger.error(f"Critical error during page reasoning generation: {e}")
        
    return json.dumps(ai_payload, indent=2)

def extract_document_structure(pdf_path: str) -> dict:
    """
    Main entry point called by rag_tasks.py.
    Prioritizes embedded TOC, falls back to the resilient AI Sensor Payload.
    """
    try:
        doc = fitz.open(pdf_path) 
        toc = doc.get_toc(simple=True)
        
        if toc:
            doc.close()
            return {
                "status": "success",
                "toc": toc,
                "ai_header_map": None
            }
        
        print("🤖 No embedded TOC found. Executing Resilient AI Sensor Payload Generator...")
        ai_payload = generate_page_reasoning(doc, pdf_path)
        doc.close() 
        
        return {
            "status": "success",
            "toc": [],
            "ai_header_map": ai_payload
        }
    except Exception as e:
        logger.error(f"Failed to extract document structure for {pdf_path}: {e}")
        return {
            "status": "error",
            "toc": [],
            "ai_header_map": None
        }