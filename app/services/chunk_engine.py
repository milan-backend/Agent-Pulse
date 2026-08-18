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

        # =====================================================================
        # 📊 1. ATOMIC SEMANTIC CHUNKING (For Tables & Grids)
        # =====================================================================
        if preserve_tables:
            table_headers = strategy_hint.get("table_headers", "")
            table_headers = table_headers.strip() if table_headers else ""
            section_title = strategy_hint.get("section", "Unknown Table").strip()
            
            # Always staple the headers to the top of EVERY chunk so context is never lost
            header_prefix = f"[TABLE CONTEXT: {section_title}]\n"
            if table_headers:
                header_prefix += f"[COLUMN HEADERS: {table_headers}]\n\n"
            
            # 🟢 THE FIX: Split by the Vision AI's invisible marker, NOT by random lines!
            semantic_blocks = section_text.split("<!-- SEMANTIC_BREAK -->")
            
            current_chunk_blocks = []
            current_word_count = 0
            
            print(f"\n🧠 [X-RAY CHUNKER] Processing Table: '{section_title}' ({len(semantic_blocks)} Semantic Blocks)")
            
            for block_idx, block in enumerate(semantic_blocks):
                block = block.strip()
                if not block:
                    continue
                    
                words_in_block = len(block.split())
                
                # 🟢 ATOMIC MATH: Does adding this unbreakable block push us over the limit?
                if current_word_count + words_in_block > self.chunk_size and current_chunk_blocks:
                    print(f"   ✂️ Block {block_idx + 1} ({words_in_block} words) exceeds limit. Sealing Chunk {sequence} early at {current_word_count} words.")
                    
                    # Seal and save the current chunk exactly as it is
                    final_text = header_prefix + "\n\n".join(current_chunk_blocks)
                    self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)
                    sequence += 1
                    
                    # Start a fresh chunk with the new block
                    current_chunk_blocks = [block]
                    current_word_count = words_in_block
                else:
                    # Safe to add to current chunk without breaking the limit
                    current_chunk_blocks.append(block)
                    current_word_count += words_in_block
                    print(f"   -> Added Block {block_idx + 1}: +{words_in_block} words (Running Total: {current_word_count}/{self.chunk_size})")
            
            # Catch the final remaining blocks
            if current_chunk_blocks:
                print(f"   📦 Finalizing last pieces into chunk {sequence}.")
                final_text = header_prefix + "\n\n".join(current_chunk_blocks)
                self._append_chunk(chunks, final_text, sequence, section_id, document_id, workspace_id, agent_id)

        # =====================================================================
        # 📝 2. NARRATIVE CHUNKING (For Paragraphs)
        # =====================================================================
        else:
            # Note: Because this function is called inside a loop for EACH section 
            # in rag_tasks.py, the "Hard Boundary" rule is automatically enforced! 
            # A 600-word Introduction will NEVER bleed into the Architecture section.
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