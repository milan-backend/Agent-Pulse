import logging
from typing import List, Dict, Any
from app.core.enums.signals import SignalType

logger = logging.getLogger(__name__)

class TableDetector:
    """
    Detects and parses tabular structures, grids, and matrix data 
    from document pages prior to chunking or embedding.
    """

    def __init__(self):
        self.detector_name = "table_detector"

    def extract(self, pages: List[str]) -> List[Dict[str, Any]]:
        """
        Scans pages for table layouts and returns structured table signals.
        """
        signals = []
        
        for idx, page_text in enumerate(pages):
            page_num = idx + 1
            lines = page_text.split("\n")
            
            # Heuristic pattern matching for tabular data (e.g., lines containing multiple column delimiters like tabs or pipes)
            table_row_count = 0
            table_buffer = []

            for line_idx, line in enumerate(lines):
                stripped = line.strip()
                # Check for row delimiters (tabs, multiple spaces, or pipe characters common in structured text)
                if "\t" in line or (line.count("  ") >= 2 and len(stripped) > 0):
                    table_row_count += 1
                    table_buffer.append(stripped)
                else:
                    if table_row_count >= 2:
                        # We detected a contiguous block of table rows
                        signals.append({
                            "signal_type": SignalType.TABLE,
                            "page_number": page_num,
                            "confidence": 0.88,
                            "content": "\n".join(table_buffer),
                            "metadata": {
                                "row_count": table_row_count,
                                "structure_type": "delimited_grid"
                            }
                        })
                    table_row_count = 0
                    table_buffer = []

            # Catch trailing tables at the end of a page
            if table_row_count >= 2:
                signals.append({
                    "signal_type": SignalType.TABLE,
                    "page_number": page_num,
                    "confidence": 0.85,
                    "content": "\n".join(table_buffer),
                    "metadata": {
                        "row_count": table_row_count,
                        "structure_type": "delimited_grid"
                    }
                })

        logger.info(f"TableDetector extracted {len(signals)} tabular blocks across {len(pages)} pages.")
        return signals