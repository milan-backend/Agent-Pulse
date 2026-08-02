import fitz  # PyMuPDF
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# =====================================================================
# 1. RAW TEXT EXTRACTION
# =====================================================================
def extract_raw_pages(pdf_path: str) -> Dict[int, str]:
    """Extracts raw text from a PDF, maintaining strict page boundaries."""
    doc = fitz.open(pdf_path)
    pages_dict = {}
    
    for page_num in range(doc.page_count):
        # We use simple text extraction since the AI handles semantics now
        raw_text = doc[page_num].get_text("text")
        
        # Clean up excessive newlines/spaces to save tokens
        clean_text = " ".join(raw_text.split())
        
        if clean_text.strip():
            pages_dict[page_num + 1] = clean_text.strip()
            
    doc.close()
    return pages_dict

# =====================================================================
# 2. BATCH BUILDER
# =====================================================================
def build_pdf_batches(pages_dict: Dict[int, str], pages_per_batch: int = 15) -> List[str]:
    """
    Groups raw pages into token-efficient batches formatted for the Navigation AI.
    Format:
    --- PAGE 1 ---
    text...
    --- PAGE 2 ---
    """
    batches = []
    current_batch = []
    current_count = 0
    
    for page_num, text in sorted(pages_dict.items()):
        current_batch.append(f"--- PAGE {page_num} ---\n{text}\n")
        current_count += 1
        
        if current_count >= pages_per_batch:
            batches.append("\n".join(current_batch))
            current_batch = []
            current_count = 0
            
    # Append any remaining pages
    if current_batch:
        batches.append("\n".join(current_batch))
        
    return batches

def process_pdf_for_navigation(pdf_path: str, batch_size: int = 15) -> List[str]:
    """Main entry point: Converts a PDF into AI-ready raw text batches."""
    print(f"📄 Extracting raw text from {pdf_path}...")
    pages = extract_raw_pages(pdf_path)
    batches = build_pdf_batches(pages, batch_size)
    print(f"📦 Created {len(batches)} batches for Navigation AI.")
    return batches