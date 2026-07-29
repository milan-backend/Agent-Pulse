import logging
import re
from typing import List, Dict, Any
from app.core.enums.signals import SignalType

logger = logging.getLogger(__name__)

class EntityDetector:
    """
    Detects named entities (organizations, systems, dates, departments) 
    deterministically from document text.
    """

    def __init__(self):
        self.detector_name = "entity_detector"

    def extract(self, pages: List[str]) -> List[Dict[str, Any]]:
        """
        Scans pages for entity patterns and returns structured entity signals.
        """
        signals = []
        
        # Simple regex patterns for deterministic entity extraction (e.g., Dates, Emails, System Codes)
        date_pattern = r"\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4})|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b"
        id_pattern = r"\b[A-Z]{2,}-\d{3,}\b"  # e.g., SEC-001, DOC-1234

        for idx, page_text in enumerate(pages):
            page_num = idx + 1

            # Extract Dates
            dates = re.findall(date_pattern, page_text)
            for date_match in set(dates):
                signals.append({
                    "signal_type": SignalType.ENTITY,
                    "page_number": page_num,
                    "confidence": 0.92,
                    "content": date_match,
                    "metadata": {
                        "entity_type": "DATE",
                        "subtype": "calendar_date"
                    }
                })

            # Extract System IDs / Codes
            system_ids = re.findall(id_pattern, page_text)
            for id_match in set(system_ids):
                signals.append({
                    "signal_type": SignalType.ENTITY,
                    "page_number": page_num,
                    "confidence": 0.89,
                    "content": id_match,
                    "metadata": {
                        "entity_type": "SYSTEM_ID",
                        "subtype": "identifier_code"
                    }
                })

        logger.info(f"EntityDetector extracted {len(signals)} entities across {len(pages)} pages.")
        return signals