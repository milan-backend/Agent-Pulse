import uuid
from typing import List, Dict, Any, Optional

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

        # 🟢 SMART SPLITTING: Chop massive tables row-by-row and inject headers!
        if preserve_tables:
            table_headers = strategy_hint.get("table_headers", "").strip()
            header_prefix = f"[COLUMN HEADERS: {table_headers}]\n" if table_headers else ""
            
            lines = section_text.split('\n')
            current_chunk_lines = []
            current_word_count = 0
            
            for line in lines:
                current_chunk_lines.append(line)
                current_word_count += len(line.split())
                
                # If this chunk hits our limit, save it and start a new one
                if current_word_count >= self.chunk_size:
                    final_text = header_prefix + "\n".join(current_chunk_lines)
                    self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)
                    sequence += 1
                    
                    # Keep the last 3 rows for context overlap
                    current_chunk_lines = current_chunk_lines[-3:]
                    current_word_count = sum(len(l.split()) for l in current_chunk_lines)
            
            # Catch the last remaining piece of the table
            if len(current_chunk_lines) > 3 or (current_chunk_lines and sequence == 1):
                final_text = header_prefix + "\n".join(current_chunk_lines)
                self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)

        # 🔴 NAIVE SPLITTING: Standard stride fallback for regular paragraphs
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