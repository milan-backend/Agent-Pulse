import fitz  # PyMuPDF
import pdfplumber
import logging
import io
from PIL import Image
import pytesseract
from typing import Dict, List

logger = logging.getLogger(__name__)

# =====================================================================
# 1. RAW TEXT EXTRACTION (WITH OCR FALLBACK & VISUAL LAYOUT)
# =====================================================================
def extract_raw_pages(pdf_path: str) -> Dict[int, str]:
    """Extracts raw text preserving EXACT visual layout for tables."""
    pages_dict = {}
    
    # 1. 🟢 THE FIX: Use pdfplumber to preserve the 2D visual grid
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # layout=True forces it to keep the physical spaces between columns
                raw_text = page.extract_text(layout=True)
                
                if raw_text and raw_text.strip():
                    # We do NOT use .strip() on the lines anymore, to protect the column spaces!
                    pages_dict[page_num + 1] = raw_text
    except Exception as e:
        print(f"⚠️ pdfplumber failed, falling back to PyMuPDF: {e}")
    
    # 2. OCR FALLBACK: If pdfplumber found nothing (e.g., scanned images)
    if not pages_dict:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc[page_num]
            print(f"🔄 No text layer detected on Page {page_num + 1}. Running PyTesseract OCR...")
            try:
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img)
                
                if ocr_text.strip():
                    pages_dict[page_num + 1] = ocr_text
            except Exception as e:
                print(f"⚠️ OCR failed on Page {page_num + 1}: {e}")
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

# =====================================================================
# 3. MAIN PROCESSOR
# =====================================================================
def process_pdf_for_navigation(pdf_path: str, batch_size: int = 15) -> List[str]:
    """Main entry point: Converts a PDF into AI-ready raw text batches."""
    print(f"📄 Extracting raw text from {pdf_path}...")
    pages = extract_raw_pages(pdf_path)
    batches = build_pdf_batches(pages, batch_size)
    print(f"📦 Created {len(batches)} batches for Navigation AI.")
    return batches