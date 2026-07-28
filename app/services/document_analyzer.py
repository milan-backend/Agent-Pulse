import re
from typing import List, Dict, Any

class DocumentAnalyzer:
    """
    Component 1: Document Analyzer (Pure Python / Deterministic)
    Extracts structural signals, text blocks, and layout metadata page by page.
    """
    def __init__(self):
        pass

    def analyze_document(self, extracted_text: str, source_filename: str) -> List[Dict[str, Any]]:
        if not extracted_text or not extracted_text.strip():
            return []

        # Split text into pages by form feed or fallback block segmentation
        pages_list = extracted_text.split("\f")
        if len(pages_list) <= 1:
            pages_list = [extracted_text[i:i+3000] for i in range(0, len(extracted_text), 3000)]

        analyzed_pages = []

        for idx, page_content in enumerate(pages_list, start=1):
            cleaned_text = page_content.strip()
            if not cleaned_text:
                continue

            # Extract structural signals deterministically
            headings = self._extract_headings(cleaned_text)
            keywords = self._extract_keywords(cleaned_text)
            has_table = bool(re.search(r'(\│|\│|\+|\-{3,}|\|)', cleaned_text))
            has_bullets = bool(re.search(r'^(\*|\-|\d+\.)\s+', cleaned_text, re.MULTILINE))

            page_metadata = {
                "page": idx,
                "text": cleaned_text,
                "word_count": len(cleaned_text.split()),
                "headings": headings,
                "keywords": keywords,
                "layout": {
                    "table": has_table,
                    "bullets": has_bullets
                },
                "first_paragraph": cleaned_text.split('\n')[0] if '\n' in cleaned_text else cleaned_text[:100],
                "last_paragraph": cleaned_text.split('\n')[-1] if '\n' in cleaned_text else cleaned_text[-100:]
            }
            analyzed_pages.append(page_metadata)

        return analyzed_pages

    def _extract_headings(self, text: str) -> List[str]:
        # Regex to detect line-based capitalized or numbered headings
        heading_candidates = re.findall(r'^(?:[A-Z0-9\.\s]{4,}|[0-9]+\.[0-9]*\s+[A-Z].+)$', text, re.MULTILINE)
        return [h.strip() for h in heading_candidates if len(h.strip()) > 3][:5]

    def _extract_keywords(self, text: str) -> List[str]:
        # Simple frequency-based keyword extraction avoiding stop words
        stop_words = {"the", "and", "to", "of", "a", "in", "for", "is", "on", "that", "by", "this", "with", "i", "you", "it"}
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in stop_words:
                freq[w] = freq.get(w, 0) + 1
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [kw[0] for kw in sorted_keywords[:8]]