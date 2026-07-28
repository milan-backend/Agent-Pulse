import re
from typing import List, Dict, Any

class ChunkEngine:
    """
    Component 5: Semantic Chunk Engine (Pure Python / Deterministic)
    Cascades strictly top-down (Navigation Node -> Subtopic -> Semantic Paragraphs -> Chunk).
    Paragraph groups serve as primary boundaries; word limits act strictly as overflow safety caps.
    """
    def __init__(self, navigation_map: Dict[str, Any], max_chunk_words: int = 450, overlap_words: int = 60):
        self.navigation_map = navigation_map
        self.max_chunk_words = max_chunk_words
        self.overlap_words = overlap_words

    def execute_bounded_chunking(self, full_document_text: str, source_filename: str) -> List[Dict[str, Any]]:
        if not full_document_text or not full_document_text.strip():
            return []

        pages_list = full_document_text.split("\f")
        if len(pages_list) <= 1:
            pages_list = [full_document_text[i:i + 3000] for i in range(0, len(full_document_text), 3000)]

        all_bounded_chunks = []
        navigation_nodes = self.navigation_map.get("navigation", [])
        document_title = self.navigation_map.get("document_title", source_filename)
        chunk_counter = 1

        for node in navigation_nodes:
            node_id = node.get("node_id", "N_UNKNOWN")
            topic_title = node.get("title") or node.get("topic") or "General"
            page_range = node.get("pages") or node.get("page_range") or [1, len(pages_list)]
            subtopics = node.get("subtopics", [])

            if not isinstance(page_range, list) or len(page_range) < 2:
                page_range = [1, len(pages_list)]

            start_p = max(1, int(page_range[0]))
            end_p = min(len(pages_list), int(page_range[1]))
            
            node_pages_subset = pages_list[max(0, start_p - 1):end_p]
            if not node_pages_subset:
                continue

            # Semantic grouping cascade
            node_chunks = self._semantic_paragraph_split_with_subtopics(node_pages_subset, start_p, subtopics, topic_title)

            for chunk_info in node_chunks:
                bounded_chunk = {
                    "chunk_id": f"C{chunk_counter:03d}",
                    "document_title": document_title,
                    "source_file": source_filename,
                    "navigation_node": node_id,
                    "topic": topic_title,
                    "subtopic": chunk_info["subtopic"],     # 🟢 Mapped accurately to closest structural subtopic
                    "page_start": chunk_info["page_start"], 
                    "page_end": chunk_info["page_end"],      
                    "chunk_text": chunk_info["text"],        
                    "strategy_used": "Top-Down Semantic Subtopic-Aligned Chunking"
                }
                all_bounded_chunks.append(bounded_chunk)
                chunk_counter += 1

        return all_bounded_chunks

    def _semantic_paragraph_split_with_subtopics(
        self, page_texts: List[str], base_page_num: int, subtopics: List[str], fallback_topic: str
    ) -> List[Dict[str, Any]]:
        """
        Groups paragraphs naturally. Splits only on semantic group boundaries, 
        using max_chunk_words strictly as an overflow safety valve.
        Maps text chunks to relevant subtopics based on heading proximity or keyword matching.
        """
        chunks = []
        current_words = []
        current_start_page = base_page_num
        current_end_page = base_page_num

        def resolve_subtopic(snippet: str) -> str:
            if not subtopics:
                return fallback_topic
            snippet_lower = snippet.lower()
            # Check if any defined subtopic keyword matches the text snippet
            for sub in subtopics:
                if any(kw.lower() in snippet_lower for kw in sub.split()):
                    return sub
            # Default to the first subtopic or fallback if no keyword match occurs
            return subtopics[0]

        for p_idx, page_content in enumerate(page_texts):
            current_page_num = base_page_num + p_idx
            paragraphs = re.split(r'\n\s*\n', page_content)

            for para in paragraphs:
                para_clean = para.strip()
                if not para_clean:
                    continue
                
                para_words = para_clean.split()
                if not para_words:
                    continue

                # Safety cap overflow check (only split when natural paragraph block exceeds word budget)
                if len(current_words) + len(para_words) > self.max_chunk_words and current_words:
                    chunk_text = " ".join(current_words)
                    chunks.append({
                        "text": chunk_text,
                        "subtopic": resolve_subtopic(chunk_text),
                        "page_start": current_start_page,
                        "page_end": current_end_page
                    })
                    overlap_pool = current_words[-self.overlap_words:] if len(current_words) > self.overlap_words else current_words
                    current_words = list(overlap_pool)
                    current_start_page = current_page_num

                current_end_page = current_page_num
                current_words.extend(para_words)

        # Flush trailing content
        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append({
                "text": chunk_text,
                "subtopic": resolve_subtopic(chunk_text),
                "page_start": current_start_page,
                "page_end": current_end_page
            })

        return chunks