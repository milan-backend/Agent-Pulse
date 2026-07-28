from typing import List, Dict, Any

class TopicBoundaryDetector:
    """
    Component 2: Robust Topic Boundary Detector
    Uses safe .get() queries with default fallbacks to guarantee 100% crash immunity.
    """
    def detect_boundaries(self, analyzed_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not analyzed_pages:
            return [{
                "topic_id": "T001",
                "id": "T001",
                "title": "General Document",
                "section_number": "",
                "pages": [1, 1]
            }]

        detected_topics = []
        current_topic_pages = []
        
        first_page = analyzed_pages[0]
        initial_headings = first_page.get("headings", ["Document Introduction"])
        current_title = initial_headings[0] if initial_headings else "Document Introduction"
        
        initial_numberings = first_page.get("numbering_schemes") or first_page.get("numberings", [])
        current_numbering = initial_numberings[0] if initial_numberings else ""
        
        topic_counter = 1
        prev_page_words = set(str(first_page.get("raw_snippet", "")).lower().split())

        for page in analyzed_pages:
            # Safely fetch properties using fallback dictionaries
            page_num = page.get("page_number") or page.get("page", 1)
            headings = page.get("headings", ["Section"])
            numberings = page.get("numbering_schemes") or page.get("numberings", [])
            snippet = str(page.get("raw_snippet", ""))
            current_page_words = set(snippet.lower().split())

            has_explicit_heading = bool(headings)
            numbering_changed = bool(numberings and numberings[0] != current_numbering)
            
            intersection = len(prev_page_words.intersection(current_page_words))
            union = len(prev_page_words.union(current_page_words))
            keyword_similarity = intersection / union if union > 0 else 0.0

            continuity_score = 1.0
            if has_explicit_heading:
                continuity_score -= 0.4
            if numbering_changed:
                continuity_score -= 0.4
            if keyword_similarity < 0.15:
                continuity_score -= 0.3

            if continuity_score < 0.5 and current_topic_pages:
                t_id = f"T{topic_counter:03d}"
                detected_topics.append({
                    "topic_id": t_id,
                    "id": t_id,
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