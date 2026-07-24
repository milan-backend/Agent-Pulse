import re
from typing import List, Dict, Any
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan

class ChunkEngine:
    def __init__(self, plan: KnowledgeIngestionPlan):
        """
        The Chunk Engine reads the validated KnowledgeIngestionPlan.
        """
        self.strategy = plan.chunk_strategy
        self.chunk_size = plan.chunk_size
        self.overlap = plan.overlap

    def execute_chunking(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        if self.strategy == "Heading Based":
            return self._chunk_by_headings(text, source_filename)
        elif self.strategy == "Question Answer":
            return self._chunk_by_qa(text, source_filename)
        elif self.strategy == "Page Based":
            return self._chunk_by_sliding_window(text, source_filename)
        else:
            return self._chunk_by_sliding_window(text, source_filename)

    def _chunk_by_sliding_window(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        words = text.split()
        chunks = []
        stride = self.chunk_size - self.overlap
        if stride <= 0:
            stride = self.chunk_size

        for i in range(0, len(words), stride):
            chunk_text = " ".join(words[i:i + self.chunk_size])
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "source_file": source_filename,
                    "strategy_used": self.strategy
                })
        return chunks

    def _chunk_by_headings(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        sections = re.split(r'\n(?=#+\s|\n[A-Z0-9\s]{4,}:?\n)', text)
        chunks = []

        for section in sections:
            section_str = section.strip()
            if not section_str:
                continue

            words = section_str.split()
            if len(words) > self.chunk_size:
                sub_chunks = self._chunk_by_sliding_window(section_str, source_filename)
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "text": section_str,
                    "source_file": source_filename,
                    "strategy_used": "Heading Based"
                })
        return chunks

    def _chunk_by_qa(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        qa_blocks = re.split(r'\n(?=(?:Q|Question|FAQ)\s*[:\-\?])', text, flags=re.IGNORECASE)
        chunks = []

        for block in qa_blocks:
            block_str = block.strip()
            if not block_str:
                continue

            words = block_str.split()
            if len(words) > self.chunk_size:
                sub_chunks = self._chunk_by_sliding_window(block_str, source_filename)
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "text": block_str,
                    "source_file": source_filename,
                    "strategy_used": "Question Answer"
                })
        return chunks