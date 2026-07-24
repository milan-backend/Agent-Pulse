import re
from typing import List, Dict, Any
from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan


class ChunkEngine:
    def __init__(self, plan: KnowledgeIngestionPlan):
        self.strategy = plan.chunk_strategy
        self.chunk_size = plan.chunk_size
        self.overlap = plan.overlap

    def execute_chunking(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        if not text or not text.strip():
            return []

        words = text.split()
        
        # Guardrail: If total text exceeds chunk_size but strategy produced 1 chunk, enforce sliding window
        if self.strategy == "Heading Based":
            chunks = self._chunk_by_headings(text, source_filename)
        elif self.strategy == "Question Answer":
            chunks = self._chunk_by_qa(text, source_filename)
        elif self.strategy == "Section Based":
            chunks = self._chunk_by_sections(text, source_filename)
        else:
            chunks = self._chunk_by_sliding_window(text, source_filename)

        # Fallback Safety Valve: If text has over chunk_size words but strategy yielded 1 chunk, split it
        if len(chunks) <= 1 and len(words) > (self.chunk_size * 1.2):
            print(f"⚠️ Chunk Engine Safety Triggered: Strategy '{self.strategy}' yielded 1 large chunk ({len(words)} words). Applying sliding window sub-chunking.")
            chunks = self._chunk_by_sliding_window(text, source_filename)

        return chunks

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
                    "strategy_used": "Sliding Window"
                })
        return chunks

    def _chunk_by_sections(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        sections = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk_words = []

        for sec in sections:
            sec_words = sec.strip().split()
            if not sec_words:
                continue

            if len(current_chunk_words) + len(sec_words) <= self.chunk_size:
                current_chunk_words.extend(sec_words)
            else:
                if current_chunk_words:
                    chunks.append({
                        "text": " ".join(current_chunk_words),
                        "source_file": source_filename,
                        "strategy_used": "Section Based"
                    })
                current_chunk_words = sec_words

        if current_chunk_words:
            chunks.append({
                "text": " ".join(current_chunk_words),
                "source_file": source_filename,
                "strategy_used": "Section Based"
            })
        return chunks

    def _chunk_by_headings(self, text: str, source_filename: str) -> List[Dict[str, Any]]:
        sections = re.split(r'\n(?=#+\s|\n[A-Z0-9\.\s]{4,}:?\n)', text)
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