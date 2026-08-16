import uuid
from typing import List, Dict, Any, Optional
import re

class ChunkEngine:
    def __init__(self, chunk_size: int = 400, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def execute_section_chunking(
        self, 
        section_text: str, 
        section_id: Optional[uuid.UUID], 
        document_id: uuid.UUID, 
        workspace_id: uuid.UUID, 
        agent_id: Optional[uuid.UUID] = None,
        strategy_hint: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        if not section_text or not section_text.strip():
            return []

        chunks = []
        sequence = 1
        
        strategy_hint = strategy_hint or {}
        preserve_tables = strategy_hint.get("preserve_tables", False)

        # 🟢 SMART SPLITTING: If it's a table/list, split by newline to preserve rows
        if preserve_tables:
            # Split by lines, keeping rows perfectly intact
            lines = section_text.split('\n')
            current_chunk_words = []
            current_chunk_text = ""
            
            for line in lines:
                line_words = line.split()
                # If adding this row exceeds the limit, save the chunk and start over
                if len(current_chunk_words) + len(line_words) > self.chunk_size and current_chunk_words:
                    self._append_chunk(chunks, current_chunk_text, sequence, section_id, document_id, workspace_id, agent_id)
                    sequence += 1
                    
                    # Keep overlap (last few rows)
                    overlap_text = "\n".join(current_chunk_text.split('\n')[-3:])
                    current_chunk_text = overlap_text + "\n" + line
                    current_chunk_words = current_chunk_text.split()
                else:
                    current_chunk_text += (line + "\n")
                    current_chunk_words.extend(line_words)
            
            # Catch the remaining text
            if current_chunk_text.strip():
                self._append_chunk(chunks, current_chunk_text, sequence, section_id, document_id, workspace_id, agent_id)

        # 🔴 NAIVE SPLITTING: Fallback for standard narrative paragraphs
        else:
            words = section_text.split()
            stride = self.chunk_size - self.overlap
            if stride <= 0:
                stride = self.chunk_size

            for i in range(0, len(words), stride):
                chunk_words = words[i:i + self.chunk_size]
                chunk_str = " ".join(chunk_words)
                if chunk_str.strip():
                    self._append_chunk(chunks, chunk_str, sequence, section_id, document_id, workspace_id, agent_id)
                    sequence += 1

        return chunks

    def _append_chunk(self, chunks_list, text, sequence, section_id, document_id, workspace_id, agent_id):
        text = text.strip()
        if not text:
            return
            
        extractive_summary = text[:150].strip() + "..." if len(text) > 150 else text
        
        chunks_list.append({
            "text": text,
            "section_id": section_id,
            "document_id": document_id,
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "sequence_number": sequence,
            "word_count": len(text.split()),
            "telemetry_summary": extractive_summary
        })