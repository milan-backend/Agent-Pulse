# app/services/document_parser.py

import io
import re
import logging
from typing import Dict, List, Any
import pypdf

logger = logging.getLogger(__name__)

class DocumentParserService:
    """
    Local Python-first parser that processes large documents (e.g., 300+ pages) 
    completely locally. It extracts structural signals, headings, outlines, and 
    clean text summaries without relying on LLMs, keeping token costs to zero.
    """

    def __init__(self, file_bytes: bytes, filename: str):
        self.file_bytes = file_bytes
        self.filename = filename

    def parse_document(self) -> Dict[str, Any]:
        """
        Executes the full local parsing pipeline: reads the file, 
        extracts text page-by-page, detects structural headings, and formats 
        payloads for the Navigation AI and Extraction AI.
        """
        logger.info(f"Starting local Python parsing for file: {self.filename}")
        
        pages_text = self._extract_pages_from_pdf()
        total_pages = len(pages_text)
        
        # Extract headings and structural signals locally
        headings_outline = self._extract_headings_and_outline(pages_text)
        
        # Build optimized summaries/snippets for Metadata Extraction AI
        abstract_summary = self._extract_summary_payload(pages_text)

        logger.info(f"Successfully parsed {total_pages} pages locally. Extracted {len(headings_outline)} structural nodes.")

        return {
            "filename": self.filename,
            "total_pages": total_pages,
            "navigation_payload": {
                "document_title": self.filename,
                "total_pages": total_pages,
                "outline_structure": headings_outline
            },
            "extraction_payload": {
                "summary_text": abstract_summary,
                "first_few_pages_text": "\n".join(pages_text[:3]) if total_pages >= 3 else "\n".join(pages_text)
            }
        }

    def _extract_pages_from_pdf(self) -> List[str]:
        """Reads PDF binary content and extracts text page-by-page safely."""
        pages = []
        try:
            reader = pypdf.PdfReader(io.BytesIO(self.file_bytes))
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages.append(text.strip())
        except Exception as e:
            logger.error(f"Error reading PDF bytes for {self.filename}: {e}")
            raise ValueError(f"Failed to parse PDF document: {e}")
        return pages

    def _extract_headings_and_outline(self, pages_text: List[str]) -> List[Dict[str, Any]]:
        """
        Scans pages locally using pattern matching (RegEx) to find headings, 
        chapters, and sections (e.g., '1. Introduction', 'Chapter II').
        """
        outline = []
        # Pattern to catch common headings like "1. Overview", "1.1 Architecture", "Chapter 1"
        heading_pattern = re.compile(r"^(\d+(\.\d+)*)\s+([A-Z][A-Za-z0-9\s\,\-\:]+)$", re.MULTILINE)

        for page_idx, text in enumerate(pages_text):
            page_num = page_idx + 1
            matches = heading_pattern.findall(text)
            
            for match in matches:
                full_prefix = match[0]
                heading_title = match[2].strip()
                hierarchy_level = len(full_prefix.split('.'))

                outline.append({
                    "level": hierarchy_level,
                    "prefix": full_prefix,
                    "title": heading_title,
                    "page": page_num
                })

        # Fallback if no strict numbered headings were matched
        if not outline and pages_text:
            outline.append({
                "level": 1,
                "prefix": "1",
                "title": "Document Main Body",
                "page": 1
            })

        return outline

    def _extract_summary_payload(self, pages_text: List[str]) -> str:
        """
        Extracts high-signal introductory text from the first few pages 
        to pass to the Extraction AI for role and department tagging.
        """
        intro_text = ""
        # Combine text from the first 3 pages maximum
        for i in range(min(3, len(pages_text))):
            intro_text += f"\n--- Page {i+1} ---\n" + pages_text[i]
        
        # Truncate to avoid oversized payloads while keeping core context
        return intro_text[:4000]