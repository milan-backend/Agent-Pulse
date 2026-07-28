from typing import List, Dict, Any

class TopicBoundaryDetector:
    """
    Component 2: Topic Boundary Detector (Pure Python / Deterministic)
    Groups adjacent analyzed pages into candidate topic blocks using weighted signals.
    """
    def __init__(self, heading_weight: float = 0.5, keyword_weight: float = 0.3, length_weight: float = 0.2):
        self.heading_weight = heading_weight
        self.keyword_weight = keyword_weight
        self.length_weight = length_weight

    def detect_boundaries(self, analyzed_pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not analyzed_pages:
            return []

        topics = []
        current_topic_pages = [analyzed_pages[0]["page"]]
        current_headings = set(analyzed_pages[0]["headings"])
        current_keywords = set(analyzed_pages[0]["keywords"])
        
        topic_counter = 1

        for i in range(1, len(analyzed_pages)):
            prev_page = analyzed_pages[i - 1]
            curr_page = analyzed_pages[i]

            # Compute similarity signals
            curr_headings = set(curr_page["headings"])
            curr_keywords = set(curr_page["keywords"])

            heading_overlap = len(current_headings.intersection(curr_headings)) / max(1, len(current_headings.union(curr_headings)))
            keyword_overlap = len(current_keywords.intersection(curr_keywords)) / max(1, len(current_keywords.union(curr_keywords)))
            
            # Weighted continuity score (0 to 1)
            continuity_score = (self.heading_weight * heading_overlap) + (self.keyword_weight * keyword_overlap)

            # Threshold for splitting a topic (e.g., sharp shift in headings or low keyword overlap)
            if continuity_score < 0.15 and curr_page["headings"]:
                # Finalize current topic block
                topics.append({
                    "topic_id": f"T{topic_counter:03d}",
                    "pages": [current_topic_pages[0], current_topic_pages[-1]],
                    "headings": list(current_headings),
                    "keywords": list(current_keywords)
                })
                topic_counter += 1
                current_topic_pages = [curr_page["page"]]
                current_headings = curr_headings
                current_keywords = curr_keywords
            else:
                current_topic_pages.append(curr_page["page"])
                current_headings.update(curr_headings)
                current_keywords.update(curr_keywords)

        # Append remaining pages as the final topic block
        if current_topic_pages:
            topics.append({
                "topic_id": f"T{topic_counter:03d}",
                "pages": [current_topic_pages[0], current_topic_pages[-1]],
                "headings": list(current_headings),
                "keywords": list(current_keywords)
            })

        return topics