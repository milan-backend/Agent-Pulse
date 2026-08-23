import uuid
import re
from typing import List, Dict, Any, Optional

class ChunkEngine:
    def __init__(self, table_row_limit: int = 5, narrative_chunk_size: int = 400, overlap: int = 50):
        self.table_row_limit = table_row_limit  # 🟢 NEW: Fixed 5-row slicing
        self.narrative_chunk_size = narrative_chunk_size
        self.overlap = overlap

    def execute_section_chunking(
        self, 
        section_text: str,
        section_id: uuid.UUID, 
        document_id: uuid.UUID, 
        workspace_id: uuid.UUID, 
        content_type: str,            # "data_table" or "narrative"
        table_headers: Optional[str]  # Passed directly from the new Postgres schema
    ) -> List[Dict[str, Any]]:
        
        if not section_text or not section_text.strip():
            return []

        chunks = []
        sequence = 1

        # =====================================================================
        # 📊 1. MATHEMATICAL TABLE CHUNKING (The 5-Row Slicer)
        # =====================================================================
        if content_type == "data_table":
            print(f"\n🧠 [X-RAY CHUNKER] Slicing Table mathematically (Max {self.table_row_limit} rows per chunk)")
            
            # Extract clean rows from Markdown
            lines = section_text.strip().split("\n")
            data_rows = [
                line.strip() for line in lines 
                if line.strip().startswith("|") and not re.search(r"^\|[\-\s:|]+\|$", line.strip())
            ]
            
            if not data_rows:
                content_type = "narrative"
            else:
                # 🟢 1. Multi-Row Header Resolution
                if table_headers and table_headers.strip():
                    header_block = table_headers.strip()
                    header_lines = [h.strip() for h in header_block.split("\n") if h.strip()]
                    actual_data_rows = [r for r in data_rows if r not in header_lines]
                else:
                    # If top 2 rows are years + categories (e.g. Budget / Revenue), combine them
                    if len(data_rows) >= 2 and any(k in data_rows[1].lower() for k in ["revenue", "capital", "total", "actual", "budget"]):
                        header_block = f"{data_rows[0]}\n{data_rows[1]}"
                        actual_data_rows = data_rows[2:]
                    else:
                        header_block = data_rows[0]
                        actual_data_rows = data_rows[1:]

                # 🟢 2. Dynamic Separator Width (Matches the widest row)
                sample_rows = [header_block] + actual_data_rows[:5]
                max_cols = 1
                for r in sample_rows:
                    for line in r.split("\n"):
                        cols = line.count("|") - 1
                        if cols > max_cols:
                            max_cols = cols

                separator_row = "|" + "|".join(["---"] * max_cols) + "|"

                # 🟢 3. Guaranteed Header + Separator on Every Slice
                if not actual_data_rows:
                    actual_data_rows = [header_block]

                for i in range(0, len(actual_data_rows), self.table_row_limit):
                    row_slice = actual_data_rows[i : i + self.table_row_limit]
                    
                    final_text = f"{header_block}\n{separator_row}\n" + "\n".join(row_slice)
                    
                    self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id)
                    sequence += 1

        # =====================================================================
        # 📝 2. NARRATIVE CHUNKING (For Paragraphs)
        # =====================================================================
        if content_type == "narrative":
            print(f"\n📝 [X-RAY CHUNKER] Processing Narrative Paragraph")
            
            words = section_text.split()
            stride = self.narrative_chunk_size - self.overlap
            if stride <= 0: stride = self.narrative_chunk_size

            for i in range(0, len(words), stride):
                chunk_words = words[i:i + self.narrative_chunk_size]
                chunk_str = " ".join(chunk_words)
                
                if chunk_str.strip():
                    self._append_chunk(chunks, chunk_str, sequence, section_id, document_id, workspace_id)
                    sequence += 1

        # =====================================================================
        # 🔗 3. BUILD THE LINKED-LIST (The Retrieval Safety Net)
        # =====================================================================
        # Now that all chunks are created, we link them together using their UUIDs.
        for i in range(len(chunks)):
            if i > 0:
                chunks[i]["prev_chunk_id"] = chunks[i-1]["id"]
            if i < len(chunks) - 1:
                chunks[i]["next_chunk_id"] = chunks[i+1]["id"]

        return chunks

    def _append_chunk(self, chunks_list, text, sequence, section_id, document_id, workspace_id):
        text = text.strip()
        if not text:
            return
            
        # 🟢 GENERATE THE UUID HERE! 
        # This becomes the exact ID for both PostgreSQL and ChromaDB.
        chunk_id = uuid.uuid4()
        
        chunks_list.append({
            "id": chunk_id,
            "text": text,
            "section_id": section_id,
            "document_id": document_id,
            "workspace_id": workspace_id,
            "sequence_number": sequence,
            "prev_chunk_id": None, # Will be filled in Step 3
            "next_chunk_id": None  # Will be filled in Step 3
        })