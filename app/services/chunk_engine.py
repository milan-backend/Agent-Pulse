import uuid
import re
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
        section_title = strategy_hint.get("section", "Unknown Section").strip()

        # =====================================================================
        # 📊 1. SEMANTIC TABLE CHUNKING (With Smart Row Grouping)
        # =====================================================================
        if preserve_tables:
            row_groupings = strategy_hint.get("row_groupings", [])
            header_prefix = f"[TABLE CONTEXT: {section_title}]\n\n"
            
            # Extract rows from pure Markdown table (lines starting with |)
            lines = section_text.strip().split("\n")
            
            data_rows = []
            for line in lines:
                line = line.strip()
                if line.startswith("|"):
                    if re.search(r"\|[\-\s:]+\|", line):
                        continue # Skip markdown separator like |---|---|
                    data_rows.append(line)
            
            if not data_rows:
                # Fallback if the AI mistakenly flagged text as a table
                self._append_chunk(chunks, section_text, sequence, section_id, document_id, workspace_id, agent_id)
                return chunks
                
            markdown_header = data_rows[0]
            actual_data_rows = data_rows[1:]
            
            # Fallback: If AI fails to provide groups, treat each row as its own group
            if not row_groupings:
                row_groupings = [{"start_row": i+1, "end_row": i+1} for i in range(len(actual_data_rows))]
            
            current_chunk_rows = []
            current_word_count = len(markdown_header.split())
            
            print(f"\n🧠 [X-RAY CHUNKER] Processing Table: '{section_title}' ({len(actual_data_rows)} Rows, {len(row_groupings)} Groups)")
            
            for group in row_groupings:
                start = group.get("start_row", 1) if isinstance(group, dict) else getattr(group, "start_row", 1)
                end = group.get("end_row", start) if isinstance(group, dict) else getattr(group, "end_row", start)
                
                # Zero-indexed list slices (start-1 because AI returns 1-indexed rows)
                group_rows = actual_data_rows[start-1 : end]
                if not group_rows:
                    continue
                    
                group_text = "\n".join(group_rows)
                words_in_group = len(group_text.split())
                
                # 🟢 THE LOGIC YOU INVENTED: If group exceeds space, shift entire group to next chunk!
                if current_word_count + words_in_group > self.chunk_size and current_chunk_rows:
                    print(f"   ✂️ Group ({words_in_group} words) exceeds limit. Sealing Chunk {sequence} early.")
                    final_text = header_prefix + markdown_header + "\n" + "\n".join(current_chunk_rows)
                    self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)
                    sequence += 1
                    
                    # Start fresh chunk with the shifted group
                    current_chunk_rows = group_rows
                    current_word_count = len(markdown_header.split()) + words_in_group
                else:
                    current_chunk_rows.extend(group_rows)
                    current_word_count += words_in_group
                    print(f"   -> Added Group (Rows {start}-{end}): +{words_in_group} words (Running Total: {current_word_count}/{self.chunk_size})")
                    
            if current_chunk_rows:
                print(f"   📦 Finalizing last pieces into chunk {sequence}.")
                final_text = header_prefix + markdown_header + "\n" + "\n".join(current_chunk_rows)
                self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)

        # =====================================================================
        # 📝 2. NARRATIVE CHUNKING (For Paragraphs)
        # =====================================================================
        else:
            header_prefix = f"[DOCUMENT SECTION: {section_title}]\n\n"
            
            print(f"\n📝 [X-RAY CHUNKER] Processing Paragraph: '{section_title}'")
            
            words = section_text.split()
            stride = self.chunk_size - self.overlap
            if stride <= 0: stride = self.chunk_size

            for i in range(0, len(words), stride):
                chunk_words = words[i:i + self.chunk_size]
                chunk_str = " ".join(chunk_words)
                
                if chunk_str.strip():
                    final_chunk_text = header_prefix + chunk_str
                    self._append_chunk(chunks, final_chunk_text, sequence, section_id, document_id, workspace_id, agent_id)
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