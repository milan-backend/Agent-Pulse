from typing import List, Dict, Any

class DocumentDNAGenerator:
    """
    Component 3: Document DNA Generator (Pure Python / Deterministic)
    Compresses topic boundary information and page signals into a lightweight DNA package.
    """
    def __init__(self):
        pass

    def generate_dna(self, analyzed_pages: List[Dict[str, Any]], detected_topics: List[Dict[str, Any]], source_filename: str) -> Dict[str, Any]:
        if not analyzed_pages or not detected_topics:
            return {"document_title": source_filename, "total_pages": len(analyzed_pages), "topics": []}

        compressed_topics = []

        for topic in detected_topics:
            page_range = topic.get("pages", [1, 1])
            start_p, end_p = page_range[0], page_range[1]
            
            # Gather representative text snippets from the start and end of the topic range
            rep_snippets = []
            for page in analyzed_pages:
                p_num = page.get("page_number") or page.get("page", 1)
                if start_p <= p_num <= end_p:
                    rep_snippets.append(page.get("first_paragraph", ""))

            compressed_topic = {
                "topic_id": topic.get("topic_id") or topic.get("id", "T001"),
                "page_range": page_range,
                # 🟢 Safely fallback to topic title or default list if 'headings' is missing
                "headings": topic.get("headings", [topic.get("title", "General Section")]),
                # 🟢 Safely fallback to empty list if 'keywords' is missing
                "keywords": topic.get("keywords", [])[:5],
                "representative_summary": " ".join(rep_snippets)[:400] + "..." if rep_snippets else ""
            }
            compressed_topics.append(compressed_topic)

        document_dna = {
            "document_title": source_filename,
            "total_pages": len(analyzed_pages),
            "topic_count": len(compressed_topics),
            "topics": compressed_topics
        }

        return document_dna