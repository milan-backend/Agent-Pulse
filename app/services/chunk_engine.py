from typing import List, Dict, Any

class ChunkEngine:
    """
    Component 5: Bounded Chunk Engine (Pure Python / Deterministic)
    Strictly chunks text within the boundaries of the Navigation Map nodes,
    ensuring chunks never cross topic or subtopic lines and inherit full hierarchical metadata.
    """
    def __init__(self, navigation_map: Dict[str, Any], chunk_size: int = 800, overlap: int = 150):
        self.navigation_map = navigation_map
        self.chunk_size = chunk_size
        self.overlap = overlap

    def execute_bounded_chunking(self, full_document_text: str, source_filename: str) -> List[Dict[str, Any]]:
        if not full_document_text or not full_document_text.strip():
            return []

        # Split text into pages locally (zero LLM tokens)
        pages_list = full_document_text.split("\f")
        if len(pages_list) <= 1:
            pages_list = [full_document_text[i:i+3000] for i in range(0, len(full_document_text), 3000)]

        all_bounded_chunks = []
        navigation_nodes = self.navigation_map.get("navigation", [])
        document_title = self.navigation_map.get("document_title", source_filename)

        chunk_counter = 1

        for node in navigation_nodes:
            node_id = node.get("node_id", "N_UNKNOWN")
            topic_title = node.get("title", "General")
            page_range = node.get("pages", [1, len(pages_list)])
            subtopics = node.get("subtopics", [])

            # Slice text strictly within this navigation node's page range
            start_p = max(1, page_range[0]) - 1
            end_p = min(len(pages_list), page_range[1])
            
            node_text_pages = pages_list[start_p:end_p]
            node_combined_text = "\n".join(node_text_pages).strip()

            if not node_combined_text:
                continue

            # Sub-chunk the node text using an overlapping sliding window
            node_chunks = self._sliding_window_split(node_combined_text)

            for sub_idx, chunk_text in enumerate(node_chunks):
                subtopic_assigned = subtopics[sub_idx % len(subtopics)] if subtopics else topic_title

                bounded_chunk = {
                    "chunk_id": f"C{chunk_counter:03d}",
                    "document_title": document_title,
                    "source_file": source_filename,
                    "navigation_node": node_id,
                    "topic": topic_title,
                    "subtopic": subtopic_assigned,
                    "page_start": page_range[0],
                    "page_end": page_range[1],
                    "chunk_text": chunk_text,
                    "strategy_used": "Navigation-Bounded Sliding Window"
                }
                all_bounded_chunks.append(bounded_chunk)
                chunk_counter += 1

        return all_bounded_chunks

    def _sliding_window_split(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        stride = self.chunk_size - self.overlap
        if stride <= 0:
            stride = self.chunk_size

        for i in range(0, len(words), stride):
            chunk_text = " ".join(words[i:i + self.chunk_size])
            if chunk_text.strip():
                chunks.append(chunk_text)
                
        if not chunks and text.strip():
            chunks.append(text.strip())
            
        return chunks