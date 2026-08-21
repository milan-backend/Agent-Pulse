import fitz  # PyMuPDF
import pymupdf4llm
import logging
import re
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# =====================================================================
# 1. SMART TABLE ROUTER LOGIC
# =====================================================================
def replace_tables_with_markers(md_text: str) -> tuple[str, bool]:
    """
    Splits the Markdown text into paragraph blocks and replaces 
    any Markdown table block with our custom Vision AI routing marker.
    Returns the masked text and a boolean indicating if a table was found.
    """
    blocks = md_text.split('\n\n')
    processed_blocks = []
    has_table = False
    
    for block in blocks:
        # A standard Markdown table ALWAYS contains a separator row like "|---|---|"
        if re.search(r"\|[\-\s:]+\|", block):
            processed_blocks.append("[🚨 TABLE DETECTED - ROUTE THIS SECTION TO VISION AI 🚨]")
            has_table = True
        else:
            processed_blocks.append(block)
            
    return '\n\n'.join(processed_blocks), has_table

# =====================================================================
# 2. SMART PAYLOAD EXTRACTION (DUAL-ENGINE PREP)
# =====================================================================
def extract_smart_pages(pdf_path: str) -> List[Dict[str, Any]]:
    smart_pages = []
    print(f"📄 Capturing Dual-Payloads with Smart Table Routing for {pdf_path}...")
    
    try:
        # 1. Extract perfectly formatted Markdown page-by-page 
        md_chunks = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        
        # 2. Open document standardly to grab high-res images for the Vision routing
        doc = fitz.open(pdf_path)
        
        for i in range(len(doc)):
            real_page_num = i + 1
            page = doc[i]
            
            # High-res image (150 DPI) for the Triage/Vision AI
            pix = page.get_pixmap(dpi=150)
            
            raw_markdown = md_chunks[i]["text"] if i < len(md_chunks) else ""
            
            # 3. Mask the tables and detect if vision is needed natively!
            masked_text, page_has_table = replace_tables_with_markers(raw_markdown)
            
            smart_pages.append({
                "page_num": real_page_num,
                "type": "dual_payload",
                "content_image": pix.tobytes("png"),    
                "content_text": masked_text,           # 📝 Clean markdown with 🚨 markers
                "has_table": page_has_table            # 🟢 Tells the router what to do for $0!
            })
            
        doc.close()
        print(f"✅ Extracted {len(smart_pages)} pages with perfect layout formatting.")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        raise e
        
    return smart_pages