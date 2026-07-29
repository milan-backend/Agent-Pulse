import logging
import re
from typing import List, Dict, Any
from app.core.enums.signals import SignalType

logger = logging.getLogger(__name__)

class RuleDefinitionDetector:
    """
    Detects formal policy rules, compliance constraints, definitions, 
    and exceptions deterministically from document text.
    """

    def __init__(self):
        self.detector_name = "rule_definition_detector"

    def extract(self, pages: List[str]) -> List[Dict[str, Any]]:
        """
        Scans pages for rule and definition patterns and returns structured signals.
        """
        signals = []
        
        # Regex heuristics for mandatory rules and definitions
        rule_keywords = ["must", "shall", "required to", "strictly prohibited", "mandatory"]
        definition_pattern = r"(?:means|refers to|shall mean|is defined as)\s+['\"].*?['\"]"

        for idx, page_text in enumerate(pages):
            page_num = idx + 1
            lines = page_text.split("\n")

            for line_idx, line in enumerate(lines):
                cleaned_line = line.strip()
                if not cleaned_line:
                    continue

                # Rule Detection
                lower_line = cleaned_line.lower()
                if any(keyword in lower_line for keyword in rule_keywords):
                    signals.append({
                        "signal_type": SignalType.RULE,
                        "page_number": page_num,
                        "confidence": 0.87,
                        "content": cleaned_line,
                        "metadata": {
                            "category": "policy_mandate",
                            "line_index": line_idx
                        }
                    })

                # Definition Detection
                defs = re.findall(definition_pattern, cleaned_line, re.IGNORECASE)
                for d_match in defs:
                    signals.append({
                        "signal_type": SignalType.DEFINITION,
                        "page_number": page_num,
                        "confidence": 0.91,
                        "content": d_match,
                        "metadata": {
                            "category": "term_definition",
                            "line_index": line_idx
                        }
                    })

        logger.info(f"RuleDefinitionDetector extracted {len(signals)} rules/definitions across {len(pages)} pages.")
        return signals