import fitz  # PyMuPDF
import pdfplumber
import json
import logging
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DocumentBlock:
    """Represents a structural block in the document hierarchy."""
    def __init__(self, block_id: str, page_number: int, bbox: List[float], text: str, 
                 font_size: float, font_name: str, is_bold: bool):
        self.block_id = block_id
        self.page_number = page_number
        self.bbox = bbox  # [x0, y0, x1, y1]
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.is_bold = is_bold
        self.parent_block: Optional['DocumentBlock'] = None
        self.child_blocks: List['DocumentBlock'] = []
        self.prev_block: Optional['DocumentBlock'] = None
        self.next_block: Optional['DocumentBlock'] = None
        self.block_type = "paragraph"  # heading, paragraph, list_item, table, image, caption

    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_id": self.block_id,
            "page_number": self.page_number,
            "bounding_box": self.bbox,
            "text": self.text,
            "font_size": self.font_size,
            "font_name": self.font_name,
            "is_bold": self.is_bold,
            "block_type": self.block_type,
            "parent_block_id": self.parent_block.block_id if self.parent_block else None,
            "child_block_ids": [c.block_id for c in self.child_blocks]
        }


class AdvancedPDFParser:
    """
    Enterprise-grade PDF Parser implementing multi-signal heading confidence, 
    reading-order reconstruction, header/footer stripping, OCR artifact cleaning, 
    and block-level hierarchical graphs with full logging visibility.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path

    def _clean_ocr_artifacts(self, text: str) -> str:
        """Removes broken line breaks, duplicate spaces, and OCR noise."""
        if not text:
            return ""
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()

    def _detect_and_strip_headers_footers(self, doc: fitz.Document) -> Dict[int, List[List[float]]]:
        """Identifies text blocks repeated across multiple pages to remove them."""
        line_counts = {}
        page_lines = {}

        for page_num in range(doc.page_count):
            page = doc[page_num]
            rect = page.rect
            page_lines[page_num] = []
            
            blocks = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE).get("blocks", [])
            for b in blocks:
                if b.get("type") == 0:
                    for l in b.get("lines", []):
                        line_text = "".join([s.get("text", "") for s in l.get("spans", [])]).strip()
                        if len(line_text) > 4:
                            bbox = l.get("bbox")
                            is_margin = bbox[1] < (rect.height * 0.08) or bbox[3] > (rect.height * 0.92)
                            if is_margin:
                                norm_text = re.sub(r'\d+', 'X', line_text)
                                page_lines[page_num].append((norm_text, bbox))
                                line_counts[norm_text] = line_counts.get(norm_text, 0) + 1

        threshold = max(2, doc.page_count * 0.4)
        repeated_signatures = {text for text, count in line_counts.items() if count >= threshold}
        
        excluded_boxes = {}
        for page_num, lines in page_lines.items():
            excluded_boxes[page_num] = [bbox for text, bbox in lines if text in repeated_signatures]
            
        print(f"🧹 [PARSER LOG] Detected {len(repeated_signatures)} recurring header/footer signatures to strip.")
        return excluded_boxes

    def _reconstruct_reading_order(self, spans: List[Dict]) -> List[Dict]:
        """Sorts bounding boxes into a logical multi-column reading order."""
        sorted_spans = sorted(spans, key=lambda s: (round(s['bbox'][0] / 50), s['bbox'][1]))
        return sorted_spans

    def _calculate_heading_confidence(self, line_text: str, span: Dict, base_font: float, page_width: float) -> float:
        """Calculates a multi-signal Heading Confidence Score (0.0 to 1.0)."""
        score = 0.0
        size = span.get("size", base_font)
        flags = span.get("flags", 0)
        font_name = span.get("font", "").lower()

        if size > base_font * 1.15:
            score += 0.3
        elif size > base_font * 1.05:
            score += 0.15

        is_bold = bool((flags & 2) or (flags & 16) or "bold" in font_name or "demi" in font_name)
        if is_bold:
            score += 0.25

        if re.match(r'^(\d+(\.\d+)*[\.\)]?|chapter|section|appendix)\s+[A-Z]', line_text, re.IGNORECASE):
            score += 0.25

        if line_text.isupper() and len(line_text) > 3:
            score += 0.1

        if len(line_text) < 60:
            score += 0.1

        return min(score, 1.0)

    def parse_document(self) -> Dict[str, Any]:
        """Main execution flow parsing the entire document into an intelligent structured representation."""
        print(f"📄 [PARSER LOG] Starting Advanced PDF Parsing for: {self.pdf_path}")
        doc = fitz.open(self.pdf_path)
        doc_page_count = doc.page_count
        
        font_sizes = []
        for p in range(min(15, doc_page_count)):
            for b in doc[p].get_text("dict").get("blocks", []):
                if b.get("type") == 0:
                    for l in b.get("lines", []):
                        for s in l.get("spans", []):
                            t = s.get("text", "").strip()
                            if len(t) > 1:
                                font_sizes.append(round(s.get("size", 11.0), 1))
        base_font = max(set(font_sizes), key=font_sizes.count) if font_sizes else 10.0
        print(f"📏 [PARSER LOG] Calculated Base Body Font Size: {base_font}pt")

        excluded_headers_footers = self._detect_and_strip_headers_footers(doc)
        
        structured_pages = []
        global_block_counter = 0

        with pdfplumber.open(self.pdf_path) as plumber_pdf:
            for page_num in range(doc_page_count):
                page = doc[page_num]
                plumber_page = plumber_pdf.pages[page_num]
                page_rect = page.rect

                text_len = len(page.get_text("text").strip())
                image_count = len(page.get_images())
                has_tables = len(plumber_page.extract_tables() or []) > 0
                
                quality_score = 0.95 if text_len > 200 else (0.5 if text_len > 50 else 0.2)
                layout_type = "two_column" if text_len > 1500 and image_count == 0 else "single_column"
                if has_tables:
                    layout_type = "table_page"

                page_blocks: List[DocumentBlock] = []
                page_tables = []

                try:
                    extracted_tables = plumber_page.extract_tables()
                    if extracted_tables:
                        for tbl in extracted_tables:
                            page_tables.append(tbl)
                except Exception as e:
                    logger.warning(f"Table extraction error on page {page_num + 1}: {e}")

                blocks = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE).get("blocks", [])
                page_spans = []

                for b in blocks:
                    if b.get("type") == 0:
                        for l in b.get("lines", []):
                            for s in l.get("spans", []):
                                s_text = self._clean_ocr_artifacts(s.get("text", ""))
                                if not s_text:
                                    continue
                                
                                bbox = s.get("bbox")
                                is_hf = any(
                                    bbox[0] >= h_box[0] - 5 and bbox[1] >= h_box[1] - 5 and 
                                    bbox[2] <= h_box[2] + 5 and bbox[3] <= h_box[3] + 5
                                    for h_box in excluded_headers_footers.get(page_num, [])
                                )
                                if not is_hf:
                                    page_spans.append(s)

                ordered_spans = self._reconstruct_reading_order(page_spans)
                
                for span in ordered_spans:
                    text = span.get("text", "")
                    size = span.get("size", base_font)
                    font_name = span.get("font", "")
                    is_bold = bool((span.get("flags", 0) & 2) or "bold" in font_name.lower())
                    
                    confidence = self._calculate_heading_confidence(text, span, base_font, page_rect.width)

                    global_block_counter += 1
                    block_id = f"blk_{global_block_counter:04d}"
                    
                    block = DocumentBlock(
                        block_id=block_id,
                        page_number=page_num + 1,
                        bbox=span.get("bbox"),
                        text=text,
                        font_size=size,
                        font_name=font_name,
                        is_bold=is_bold
                    )

                    if confidence >= 0.5:
                        block.block_type = "heading"
                        print(f"🎯 [HEADING FOUND] Page {page_num + 1} | Conf: {confidence} | Text: {text}")
                    elif re.match(r'^[•\-\*]|\d+[\.\)]\s+', text):
                        block.block_type = "list_item"
                    else:
                        block.block_type = "paragraph"

                    page_blocks.append(block)

                for i in range(len(page_blocks)):
                    if i > 0:
                        page_blocks[i].prev_block = page_blocks[i-1]
                        page_blocks[i-1].next_block = page_blocks[i]

                structured_pages.append({
                    "page": page_num + 1,
                    "layout": layout_type,
                    "quality_score": quality_score,
                    "section_start": any(b.block_type == "heading" for b in page_blocks),
                    "blocks": [b.to_dict() for b in page_blocks],
                    "tables": page_tables,
                    "images_count": image_count
                })

        doc.close()
        print(f"✅ [PARSER LOG] Successfully parsed {doc_page_count} pages into {global_block_counter} structured blocks.")
        return {
            "status": "success",
            "total_pages": doc_page_count,
            "document_structure": structured_pages
        }

def extract_document_structure(pdf_path: str) -> dict:
    """Main entry point called by rag_tasks.py with log verification prints."""
    try:
        parser = AdvancedPDFParser(pdf_path)
        result = parser.parse_document()
        
        # 🟢 PRINT THE EXACT PAYLOAD BEING SENT TO NAVIGATION AI
        payload_json = json.dumps(result["document_structure"], indent=2)
        print(f"📤 [NAVIGATION AI PAYLOAD] Handing over structured JSON map to Navigation AI. Length: {len(payload_json)} chars.")
        
        return {
            "status": result["status"],
            "toc": [],
            "ai_header_map": payload_json
        }
    except Exception as e:
        print(f"❌ [PARSER ERROR] Advanced parser execution failure: {e}")
        logger.error(f"Advanced parser execution failure: {e}")
        return {
            "status": "error",
            "toc": [],
            "ai_header_map": None
        }