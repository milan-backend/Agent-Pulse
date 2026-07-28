from typing import List, Dict, Any

class TopicBoundaryDetector:
    """
    Component 2: Robust Topic Boundary Detector
    Computes a multi-signal continuity score across pages combining numbering,
    heading similarity, paragraph flow, and keyword overlap.
    """
    def detect_boundaries(self, analyzed_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not analyzed_pages:
            return []

        detected_topics = []
        current_topic_pages = []
        current_title = analyzed_pages[0].get("headings", ["Document Introduction"])[0]
        current_numbering = analyzed_pages[0].get("numbering_schemes", [""])[0]
        topic_counter = 1

        prev_page_words = set(analyzed_pages[0].get("raw_snippet", "").lower().split())

        for page in analyzed_pages:
            page_num = page["page_number"]
            headings = page.get("headings", [])
            numberings = page.get("numbering_schemes", [])
            snippet = page.get("raw_snippet", "")
            current_page_words = set(snippet.lower().split())

            # Compute multi-signal continuity metrics
            has_explicit_heading = bool(headings)
            numbering_changed = bool(numberings and numberings[0] != current_numbering)
            
            # Calculate Jaccard keyword overlap similarity with previous page
            intersection = len(prev_page_words.intersection(current_page_words))
            union = len(prev_page_words.union(current_page_words))
            keyword_similarity = intersection / union if union > 0 else 0.0

            # Continuity score (0.0 to 1.0 scale where lower means a topic break is likely)
            continuity_score = 1.0
            if has_explicit_heading:
                continuity_score -= 0.4
            if numbering_changed:
                continuity_score -= 0.4
            if keyword_similarity < 0.15:
                continuity_score -= 0.3

            # Threshold decision: if continuity drops below 0.5, establish a new topic boundary
            if continuity_score < 0.5 and current_topic_pages:
                t_id = f"T{topic_counter:03d}"
                detected_topics.append({
                    "topic_id": t_id,     # 🟢 Explicit primary key
                    "id": t_id,           # 🟢 Fallback key alias
                    "title": current_title,
                    "section_number": current_numbering,
                    "pages": [current_topic_pages[0], current_topic_pages[-1]]
                })
                topic_counter += 1
                current_topic_pages = []
                current_title = headings[0] if headings else f"Section on Page {page_num}"
                current_numbering = numberings[0] if numberings else ""

            current_topic_pages.append(page_num)
            prev_page_words = current_page_words

        # Flush final trailing topic block
        if current_topic_pages:
            t_id = f"T{topic_counter:03d}"
            detected_topics.append({
                "topic_id": t_id,
                "id": t_id,
                "title": current_title,
                "section_number": current_numbering,
                "pages": [current_topic_pages[0], current_topic_pages[-1]]
            })

        return detected_topics