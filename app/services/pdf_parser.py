import fitz  # PyMuPDF

def calculate_base_font_size(doc: fitz.Document, pages_to_scan: int = 5) -> float:
    """
    Pass 1: Scans the first few pages to determine the most common font size (body text).
    """
    font_counts = {}
    limit = min(pages_to_scan, doc.page_count)
    
    for page_num in range(limit):
        page = doc[page_num]
        content = page.get_text("dict")
        for block in content.get("blocks", []):
            if block.get("type") != 0:  # 0 means text block
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    font_counts[size] = font_counts.get(size, 0) + len(span["text"].strip())
                    
    if not font_counts:
        return 11.0 # Safe default
        
    # Return the font size that has the most characters associated with it
    return max(font_counts, key=font_counts.get)


def extract_advanced_header_map(doc: fitz.Document) -> str:
    """
    Pass 2: Scans ALL pages. Extracts ONLY text that is significantly larger than 
    the base font OR is flagged as Bold. Returns a condensed text map.
    """
    base_size = calculate_base_font_size(doc)
    header_threshold = base_size * 1.15  # Text must be 15% larger than body text
    
    header_map_lines = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        content = page.get_text("dict")
        
        page_headers = []
        for block in content.get("blocks", []):
            if block.get("type") != 0:
                continue
                
            for line in block.get("lines", []):
                line_text = ""
                is_header = False
                
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                        
                    size = span["size"]
                    flags = span["flags"]
                    
                    # In PyMuPDF, bit 4 (16) often denotes bold. 
                    is_bold = bool(flags & 16) or "Bold" in span["font"]
                    
                    if size >= header_threshold or is_bold:
                        is_header = True
                        line_text += text + " "
                
                if is_header and len(line_text.strip()) > 3: # Ignore tiny artifacts
                    page_headers.append(line_text.strip())
                    
        if page_headers:
            header_map_lines.append(f"--- PAGE {page_num + 1} ---")
            for h in page_headers:
                header_map_lines.append(h)
                
    # Join into a single highly condensed string for the AI
    return "\n".join(header_map_lines)


def extract_document_structure(pdf_path: str) -> dict:
    """
    Prioritizes embedded TOC, falls back to Advanced Header Map.
    """
    doc = fitz.open(pdf_path) 
    toc = doc.get_toc(simple=True)
    
    condensed_map = None
    if not toc:
        print("No embedded TOC found. Executing Advanced PyMuPDF Header Extraction across all pages...")
        condensed_map = extract_advanced_header_map(doc)
        
    doc.close() 
    
    return {
        "status": "success",
        "toc": toc,
        "ai_header_map": condensed_map
    }