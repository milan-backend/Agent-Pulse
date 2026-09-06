import pymupdf4llm
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# =====================================================================
# 1. PURE MARKDOWN EXTRACTION (UNIFIED ENGINE PREP)
# =====================================================================
def extract_smart_pages(pdf_path: str) -> List[Dict[str, Any]]:
    smart_pages = []
    print(f"📄 Capturing Pure Markdown Payload for {pdf_path}...")
    
    try:
        # 1. Extract perfectly formatted Markdown page-by-page natively
        # 🟢 FIX: Added 'language="hin+eng"' so Tesseract can read Hindi (Devanagari)!
        md_chunks = pymupdf4llm.to_markdown(
            pdf_path, 
            page_chunks=True,
            language="hin+eng"  # 🟢 Tells the OCR engine to expect both Hindi and English
        )
        
        for i, page_data in enumerate(md_chunks):
            # Fallback to index + 1 if metadata is missing
            real_page_num = page_data.get("metadata", {}).get("page_number", i + 1)
            exact_markdown_text = page_data.get("text", "")
            
            smart_pages.append({
                "page_num": real_page_num,
                "type": "unified_payload",
                "content_text": exact_markdown_text     # 📝 Sends pure Markdown with tables!
            })
            
        print(f"✅ Extracted {len(smart_pages)} pages with perfect unified formatting.")
    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        raise e
        
    return smart_pages