import fitz  # PyMuPDF
import logging
import io
from PIL import Image
import pytesseract
from typing import Dict, List

logger = logging.getLogger(__name__)

# =====================================================================
# 1. RAW TEXT EXTRACTION (WITH OCR FALLBACK)
# =====================================================================
def extract_raw_pages(pdf_path: str) -> Dict[int, str]:
    """Extracts raw text from a PDF, maintaining strict page boundaries. Uses OCR if no text is found."""
    doc = fitz.open(pdf_path)
    pages_dict = {}
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        
        # 1. Attempt standard text extraction (Fastest)
        raw_text = page.get_text("text")
        
        # 🟢 THE FIX: Preserve newlines so tables keep their shape!
        # This removes empty lines but keeps actual line breaks intact.
        clean_text = "\n".join([line.strip() for line in raw_text.splitlines() if line.strip()])
        
        # 2. 🟢 OCR FALLBACK: If the page has no readable text layer (e.g., scanned image)
        if not clean_text.strip():
            print(f"🔄 No text layer detected on Page {page_num + 1}. Running PyTesseract OCR...")
            try:
                # Render the page to an image (dpi=150 is a good balance of speed/quality)
                pix = page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                # Extract text using Tesseract
                # Extract text using Tesseract
                ocr_text = pytesseract.image_to_string(img)
                # 🟢 THE FIX FOR OCR:
                clean_text = "\n".join([line.strip() for line in ocr_text.splitlines() if line.strip()])
            except Exception as e:
                print(f"⚠️ OCR failed on Page {page_num + 1}: {e}")
                clean_text = ""
        
        # 3. Save if we successfully got text (from either method)
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