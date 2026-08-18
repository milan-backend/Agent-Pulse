import fitz  # PyMuPDF
import pdfplumber
import logging
import io
from PIL import Image
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# =====================================================================
# 1. SMART PAYLOAD EXTRACTION (COST-ROUTING ENGINE)
# =====================================================================
def extract_smart_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Scans a PDF and routes pages to either TEXT or VISION payloads 
    based on the structural presence of tables.
    """
    smart_pages = []
    
    print(f"📄 Analyzing document structure for {pdf_path}...")
    
    try:
        # We open the PDF with both libraries simultaneously: 
        # pdfplumber for structural math, fitz for high-res screenshots
        with pdfplumber.open(pdf_path) as pdf_struct:
            doc_visual = fitz.open(pdf_path)
            
            for page_num, struct_page in enumerate(pdf_struct.pages):
                real_page_num = page_num + 1
                
                # 1. 🟢 THE TRIGGER: Does this page have a grid/table?
                tables = struct_page.find_tables()
                
                if tables:
                    # 📸 TABLE DETECTED: Take a high-res screenshot for the Vision AI
                    print(f"   -> Page {real_page_num}: 📊 Table detected! Routing to Vision AI.")
                    visual_page = doc_visual[page_num]
                    
                    # DPI 200 ensures the Vision AI can perfectly read tiny numbers
                    pix = visual_page.get_pixmap(dpi=200) 
                    img_bytes = pix.tobytes("png")
                    
                    smart_pages.append({
                        "page_num": real_page_num,
                        "type": "table_image",
                        "content": img_bytes
                    })
                else:
                    # 📝 NO TABLE: Extract raw text for the faster/cheaper Text AI
                    print(f"   -> Page {real_page_num}: 📝 Plain text. Routing to Text AI.")
                    raw_text = struct_page.extract_text(layout=True)
                    
                    if raw_text and raw_text.strip():
                        smart_pages.append({
                            "page_num": real_page_num,
                            "type": "plain_text",
                            "content": raw_text
                        })
                        
            doc_visual.close()
            
    except Exception as e:
        print(f"❌ Smart extraction failed: {e}")
        
    return smart_pages

# =====================================================================
# 2. BATCH BUILDER (WITH MEMORY SUPPORT)
# =====================================================================
def build_smart_batches(smart_pages: List[Dict[str, Any]], pages_per_batch: int = 1) -> List[List[Dict[str, Any]]]:
    """
    Groups the smart payloads into batches. 
    We keep it at 1 page per batch to give the AI maximum focus, 
    relying on the Continuous Memory Ledger to link them together.
    """
    batches = []
    current_batch = []
    
    for page in smart_pages:
        current_batch.append(page)
        if len(current_batch) >= pages_per_batch:
            batches.append(current_batch)
            current_batch = []
            
    if current_batch:
        batches.append(current_batch)
        
    return batches

# =====================================================================
# 3. MAIN PROCESSOR
# =====================================================================
def process_pdf_for_navigation(pdf_path: str) -> List[List[Dict[str, Any]]]:
    """Main entry point: Converts a PDF into AI-ready Smart Payloads."""
    pages = extract_smart_pages(pdf_path)
    batches = build_smart_batches(pages, pages_per_batch=1)
    print(f"📦 Created {len(batches)} highly-focused batches for the Navigation Engine.")
    return batches