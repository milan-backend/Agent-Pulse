import re
import uuid
from typing import List, Dict, Any, Optional


class ChunkEngine:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        """
        Section-Bound Chunk Engine.
        :param chunk_size: Target max word limit per chunk.
        :param overlap: Word overlap between consecutive chunks to prevent context loss.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def execute_section_chunking(
        self, 
        section_text: str, 
        section_id: Optional[uuid.UUID], 
        document_id: uuid.UUID, 
        workspace_id: uuid.UUID, 
        agent_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Slices section text into word/token-bounded chunks strictly within section boundaries.
        Generates sequence numbers for PostgreSQL linked-list building.
        """
        if not section_text or not section_text.strip():
            return []

        words = section_text.split()
        chunks = []
        stride = self.chunk_size - self.overlap
        if stride <= 0:
            stride = self.chunk_size

        sequence = 1
        for i in range(0, len(words), stride):
            chunk_words = words[i:i + self.chunk_size]
            chunk_str = " ".join(chunk_words)
            
            if chunk_str.strip():
                chunks.append({
                    "text": chunk_str,
                    "section_id": section_id,
                    "document_id": document_id,
                    "workspace_id": workspace_id,
                    "agent_id": agent_id,
                    "sequence_number": sequence,
                    "word_count": len(chunk_words)
                })
                sequence += 1

        return chunks