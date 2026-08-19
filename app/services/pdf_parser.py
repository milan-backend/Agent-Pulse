import fitz  # PyMuPDF
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# =====================================================================
# 1. SMART PAYLOAD EXTRACTION (DUAL-ENGINE PREP)
# =====================================================================
def extract_smart_pages(pdf_path: str) -> List[Dict[str, Any]]:
    smart_pages = []
    print(f"📄 Capturing Dual-Payloads (Text + Image) for {pdf_path}...")
    
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            real_page_num = page_num + 1
            page = doc[page_num]
            
            # DPI 150 gives clear images without wasting tokens
            pix = page.get_pixmap(dpi=150)
            
            smart_pages.append({
                "page_num": real_page_num,
                "type": "dual_payload",
                "content_image": pix.tobytes("png"),    # 📸 For the Vision/Triage AI
                "content_text": page.get_text("text") or "" # 📝 For the Text AI
            })
            
        doc.close()
        print(f"✅ Extracted {len(smart_pages)} pages.")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        raise e
        
    return smart_pages