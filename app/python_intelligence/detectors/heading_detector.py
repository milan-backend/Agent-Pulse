import logging
from typing import List, Dict, Any
from app.core.enums.signals import SignalType

logger = logging.getLogger(__name__)

class HeadingDetector:
    """
    Detects section headers, titles, and hierarchical document divisions
    deterministically from page content.
    """

    def __init__(self):
        self.detector_name = "heading_detector"

    def extract(self, pages: List[str]) -> List[Dict[str, Any]]:
        """
        Scans pages for heading patterns and returns structured signal dictionaries.
        """
        signals = []
        
        for idx, page_text in enumerate(pages):
            page_num = idx + 1
            lines = page_text.split("\n")
            
            for line_idx, line in enumerate(lines):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue

                # Deterministic heuristic rules for headings
                is_heading = False
                level = 1

                # Rule 1: Short capitalized lines or standalone title-case lines
                if len(cleaned_line) < 80 and (cleaned_line.isupper() or cleaned_line.istitle()):
                    # Filter out likely running headers or single random words
                    if len(cleaned_line.split()) <= 10:
                        is_heading = True
                        # Simple heuristic for level based on length/casing
                        level = 1 if cleaned_line.isupper() else 2

                if is_heading:
                    signals.append({
                        "signal_type": SignalType.HEADING,
                        "page_number": page_num,
                        "confidence": 0.90,
                        "content": cleaned_line,
                        "metadata": {
                            "heading_level": level,
                            "line_index": line_idx
                        }
                    })

        logger.info(f"HeadingDetector extracted {len(signals)} headers across {len(pages)} pages.")
        return signals