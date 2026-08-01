import fitz  # PyMuPDF
import pdfplumber
import json
import logging
import re
from typing import List, Dict, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# ==========================================
# 1. GRAPH NODE REPRESENTATION
# ==========================================
class BlockNode:
    """Internal Document Graph Node representing a logical text block."""
    def __init__(self, node_id: str, page_num: int, bbox: List[float], text: str, 
                 font_size: float, is_bold: bool, font_name: str):
        self.id = node_id
        self.page = page_num
        self.bbox = bbox  
        self.text = text.strip()
        self.font_size = font_size
        self.is_bold = is_bold
        self.font_name = font_name
        
        self.parent: Optional['BlockNode'] = None
        self.children: List['BlockNode'] = []
        
        # Probabilistic roles
        self.type_probs = {
            "heading": 0.0, 
            "paragraph": 0.0, 
            "list": 0.0, 
            "table_header": 0.0,
            "caption": 0.0
        }
        self.boundary_confidence = 0.0
        self.continuation_score = 0.0
        self.indent_level = round(bbox[0] / 10) * 10 

# ==========================================
# 2. OUTPUT CANDIDATE REPRESENTATION
# ==========================================
class SectionCandidate:
    """Compressed, high-level Section Candidate designed for Navigation AI."""
    def __init__(self, sec_id: str, page_start: int, page_end: int, title: str, 
                 layout: str, heading_confidence: float):
        self.sec_id = sec_id
        self.page_start = page_start
        self.page_end = page_end
        self.title = title
        self.layout = layout
        self.heading_confidence = heading_confidence
        self.section_confidence = max(0.50, min(0.98, heading_confidence + 0.10))
        
        self.raw_texts: List[str] = []
        self.word_count = 0  
        self.tables_count = 0
        self.lists_count = 0
        self.images_count = 0
        self.parent_id: Optional[str] = None
        
        # Tracks pages already scanned for tables to avoid double counting
        self.scanned_pages = set()

    def add_text(self, text: str):
        cleaned_text = text.strip()
        if cleaned_text:
            self.raw_texts.append(cleaned_text)
            self.word_count += len(cleaned_text.split())

    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extracts top non-stopword domain terms."""
        stop_words = {
            "the", "and", "to", "a", "of", "in", "for", "is", "on", "that", "by", 
            "this", "with", "i", "you", "it", "not", "or", "be", "are", "from",
            "at", "as", "an", "was", "we", "were", "been", "have", "has", "had"
        }
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered = [w for w in words if w not in stop_words]
        counts = Counter(filtered)
        return [word for word, freq in counts.most_common(top_n)]

    def _classify_content_type(self, title: str, text: str, tables: int, lists: int) -> str:
        """Rich Content Classification Taxonomy."""
        combined = (title + " " + text).lower()
        
        if "financial" in combined or "revenue" in combined or "expenditure" in combined or "budget" in combined or "cost" in combined or "crore" in combined:
            return "Financial"
        if tables > 1 or "statistics" in combined or "enrolment" in combined or "census" in combined or "percentage" in combined:
            return "Statistics / Data"
        if "fellowship" in combined or "scholarship" in combined or "scheme" in combined or "programme" in combined or "initiative" in combined:
            return "Program Description"
        if "policy" in combined or "guideline" in combined or "framework" in combined or "strategy" in combined or "vision" in combined:
            return "Policy & Governance"
        if "legal" in combined or "act" in combined or "statute" in combined or "regulation" in combined or "clause" in combined:
            return "Regulatory / Legal"
        if "research" in combined or "publication" in combined or "journal" in combined or "innovation" in combined or "study" in combined:
            return "Research & Academic"
        if "annual report" in combined or "overview" in combined or "performance" in combined or "achievement" in combined:
            return "Annual Report / Review"
        if "procedure" in combined or lists > 5:
            return "Procedure"
            
        return "Narrative"

    def _extract_lightweight_entities(self, text: str) -> List[str]:
        """Advanced Entity Pipeline: Extract -> Normalize -> Deduplicate -> Filter."""
        raw_matches = re.findall(r'\b[A-Z][a-zA-Z0-9&]*(?:\s+[A-Z][a-zA-Z0-9&]*)*\b', text)
        
        ignore_exact = {
            "The", "And", "For", "This", "That", "Table", "Figure", "Section", 
            "Total", "Source", "Note", "Annual Report", "Government", "India"
        }
        
        # Filter verbs that cause noisy fragment extraction (e.g., "Allocation Released")
        ignore_verbs = {"Released", "Allocated", "Provided", "Approved", "Sanctioned", "Increased", "Decreased"}
        
        cleaned_candidates = []
        for m in raw_matches:
            m_str = m.strip()
            if len(m_str) < 4 or m_str in ignore_exact or m_str.isdigit():
                continue
            
            # Reject if it contains action verbs
            if any(verb in m_str for verb in ignore_verbs):
                continue
                
            cleaned_candidates.append(m_str)
                
        # Deduplicate and sort by length descending to filter out strict substrings
        unique_candidates = sorted(list(set(cleaned_candidates)), key=len, reverse=True)
        final_entities = []
        
        for cand in unique_candidates:
            if not any(cand in accepted for accepted in final_entities):
                final_entities.append(cand)
                
        return final_entities[:8]

    def to_dict(self) -> Dict[str, Any]:
        full_text = " ".join(self.raw_texts)
        words = full_text.split()
        actual_word_count = len(words)
        
        preview_len = 30
        start_prev = " ".join(words[:preview_len]) + ("..." if actual_word_count > preview_len else "")
        mid_idx = actual_word_count // 2
        mid_prev = " ".join(words[max(0, mid_idx - 15):min(actual_word_count, mid_idx + 15)]) if actual_word_count > preview_len else ""
        end_prev = " ".join(words[-preview_len:]) if actual_word_count > preview_len else ""

        return {
            "id": self.sec_id,
            "page_start": self.page_start,
            "page_end": self.page_end,
            "title": self.title,
            "content_type": self._classify_content_type(self.title, full_text, self.tables_count, self.lists_count),
            "word_count": actual_word_count,
            "estimated_reading_time_mins": round(actual_word_count / 200.0, 2),
            "preview_start": start_prev or "Empty section",
            "preview_middle": mid_prev,
            "preview_end": end_prev,
            "keywords": self._extract_keywords(full_text, top_n=5),
            "contains_tables": self.tables_count > 0,
            "contains_lists": self.lists_count > 0,
            "contains_entities": self._extract_lightweight_entities(full_text),
            "layout": self.layout,
            "tables": self.tables_count,
            "lists": self.lists_count,
            "heading_confidence": round(self.heading_confidence, 2),
            "section_confidence": round(self.section_confidence, 2),
            "parent": self.parent_id
        }

# ==========================================
# 3. UNIVERSAL PDF PARSER ENGINE
# ==========================================
class AdvancedPDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.known_heading_x_coords: List[float] = []

    def _clean_ocr_artifacts(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        return re.sub(r'[ \t]+', ' ', text).strip()

    def _detect_layout(self, nodes: List[BlockNode], page_width: float) -> str:
        if not nodes: return "single_column"
        left = sum(1 for n in nodes if n.bbox[0] < (page_width / 2.0) - 20)
        right = sum(1 for n in nodes if n.bbox[0] > (page_width / 2.0) + 20)
        return "two_column" if left > 3 and right > 3 else "single_column"

    def _reading_order_engine(self, nodes: List[BlockNode]) -> List[BlockNode]:
        """Clustering-based Reading Order: Groups nodes visually by approximate Y-axis."""
        return sorted(nodes, key=lambda n: (round(n.bbox[1] / 15) * 15, n.bbox[0]))

    def _cross_page_continuation_engine(self, prev: Optional[BlockNode], curr: BlockNode) -> float:
        if not prev: return 0.0
        score = 0.0
        if not re.search(r'[.!?]$', prev.text): score += 0.4
        if curr.text and curr.text[0].islower(): score += 0.4
        if prev.page != curr.page and prev.font_size == curr.font_size: score += 0.13
        return score

    def _probability_block_classifier(self, node: BlockNode, page_nodes: List[BlockNode]):
        """Evaluates probabilistic roles (Table Header, List, Paragraph) within page context."""
        words = node.text.split()
        word_count = len(words)
        
        siblings_on_y = [n for n in page_nodes if abs(n.bbox[1] - node.bbox[1]) < 10 and n.id != node.id]
        if siblings_on_y and word_count < 6:
            node.type_probs["table_header"] += 0.50
            if re.match(r'^(S\.?No|Sr|Sl|Amount|Total|Date|Head|Particulars)$', node.text, re.IGNORECASE):
                node.type_probs["table_header"] += 0.40
                
        if re.match(r'^[•\-\*]|\d+[\.\)]\s+', node.text):
            node.type_probs["list"] = 0.90
        if word_count > 15 and not node.is_bold:
            node.type_probs["paragraph"] = 0.85

    def _topic_boundary_engine(self, node: BlockNode, prev: Optional[BlockNode], next_n: Optional[BlockNode], page_nodes: List[BlockNode], base_font: float):
        """Semantic Boundary Engine using multi-factor signal aggregation."""
        words = node.text.split()
        word_count = len(words)
        score = 0.0

        if node.type_probs["table_header"] > 0.70 or word_count > 25 or word_count < 2:
            node.boundary_confidence = 0.0
            return

        is_numbered = bool(re.match(r'^(?:[A-Z]\.|[IVX]+\.|\d{1,3}\.?)\s+[A-Z]', node.text))
        
        if is_numbered:
            score += 0.30
            similar_numbered_nodes = sum(1 for n in page_nodes if re.match(r'^(?:[A-Z]\.|[IVX]+\.|\d{1,3}\.?)\s+[A-Z]', n.text))
            if similar_numbered_nodes > 1:
                score += 0.15

        cap_words = sum(1 for w in words if w[0].isupper() and w.isalpha())
        if word_count > 0 and (cap_words / word_count) >= 0.5: score += 0.15
        if 2 <= word_count <= 14: score += 0.10
        if next_n and len(next_n.text.split()) > 12: score += 0.15

        if is_numbered and self.known_heading_x_coords and any(abs(node.bbox[0] - x) < 5 for x in self.known_heading_x_coords):
            score += 0.10

        if prev and prev.page == node.page:
            if (node.bbox[1] - prev.bbox[3]) > base_font * 0.5: score += 0.15
        else:
            score += 0.15 

        if node.continuation_score > 0.5: score -= 0.40
        if node.text.endswith('.') and not is_numbered: score -= 0.20

        node.boundary_confidence = min(max(score, 0.0), 1.0)
        node.type_probs["heading"] = node.boundary_confidence
        
        if node.boundary_confidence > 0.65:
            self.known_heading_x_coords.append(round(node.bbox[0]))

    def _select_best_title(self, start_idx: int, ordered_graph: List[BlockNode]) -> str:
        """
        Heading Ranking Engine: Evaluates nearby candidates at a boundary 
        to select the true heading, rejecting mid-sentence statistics.
        """
        candidates = ordered_graph[start_idx : min(start_idx + 6, len(ordered_graph))]
        best_title = None
        best_score = -1.0

        for cand in candidates:
            text = cand.text.strip()
            words = text.split()
            word_count = len(words)
            cand_score = 0.0

            if word_count < 2 or word_count > 16:
                continue

            # Heavy penalty for inline statistic fragments
            if re.match(r'^\d+\s+(?:UG|PG|State|Universities|Institutions|Colleges|Students|Percent|%|Lakh|Crore)', text, re.IGNORECASE):
                cand_score -= 0.80

            # Reward standard heading markers
            if re.match(r'^(?:[A-Z]\.|[IVX]+\.|\d{1,3}\.?)\s+[A-Z]', text):
                cand_score += 0.40
            if cand.boundary_confidence > 0.50:
                cand_score += 0.30
            if cand.is_bold:
                cand_score += 0.15
            if text.endswith(':'):
                cand_score += 0.15
            
            cap_words = sum(1 for w in words if w[0].isupper() and w.isalpha())
            if word_count > 0 and (cap_words / word_count) >= 0.5:
                cand_score += 0.25

            if text.endswith('.') and not re.match(r'^(?:[A-Z]\.|[IVX]+\.|\d{1,3}\.?)\s+[A-Z]', text):
                cand_score -= 0.30

            if cand_score > best_score:
                best_score = cand_score
                best_title = text

        if not best_title or best_score < 0.20:
            fallback = ordered_graph[start_idx].text.strip()
            if len(fallback.split()) > 12:
                fallback = " ".join(fallback.split()[:10]) + "..."
            return fallback

        return best_title

    def _determine_heading_level(self, node: BlockNode) -> int:
        """Determines structural level (1, 2, 3) using numbering depth and indentation."""
        text = node.text
        num_match = re.match(r'^(\d+(?:\.\d+)*)', text)
        if num_match:
            depth = len(num_match.group(1).split('.'))
            return min(depth, 4)
            
        if node.indent_level > 120:
            return 3
        elif node.indent_level > 80:
            return 2
            
        return 1

    def parse_document(self) -> Dict[str, Any]:
        doc = fitz.open(self.pdf_path)
        total_pages = doc.page_count
        raw_graph: List[BlockNode] = []
        global_id = 0
        
        # 1. GRAPH EXTRACTION PASS
        for page_num in range(total_pages):
            blocks = doc[page_num].get_text("dict", flags=fitz.TEXT_DEHYPHENATE).get("blocks", [])
            for b in blocks:
                if b.get("type") == 0:
                    for l in b.get("lines", []):
                        line_text = ""
                        x0, y0, x1, y1 = 9999, 9999, 0, 0
                        sz, is_bold = 10.0, False
                        for s in l.get("spans", []):
                            t = self._clean_ocr_artifacts(s.get("text", ""))
                            if not t: continue
                            line_text += t + " "
                            sb = s.get("bbox")
                            x0, y0, x1, y1 = min(x0, sb[0]), min(y0, sb[1]), max(x1, sb[2]), max(y1, sb[3])
                            sz = s.get("size", 10.0)
                        
                        if len(line_text.strip()) > 3:
                            global_id += 1
                            raw_graph.append(BlockNode(f"n_{global_id}", page_num + 1, [x0, y0, x1, y1], line_text, sz, is_bold, ""))

        # 2. ENGINES PASS
        pages = {p: [] for p in range(1, total_pages + 1)}
        for node in raw_graph: pages[node.page].append(node)
        
        ordered_graph: List[BlockNode] = []
        for p in sorted(pages.keys()):
            ordered_graph.extend(self._reading_order_engine(pages[p]))

        for i, node in enumerate(ordered_graph):
            prev = ordered_graph[i-1] if i > 0 else None
            nxt = ordered_graph[i+1] if i < len(ordered_graph) - 1 else None
            node.continuation_score = self._cross_page_continuation_engine(prev, node)
            self._probability_block_classifier(node, pages[node.page])
            self._topic_boundary_engine(node, prev, nxt, pages[node.page], 10.0)

        # 3. ADAPTIVE BOUNDARY GROWTH & HIERARCHY COMPOSITION
        sections: List[SectionCandidate] = []
        current_section: Optional[SectionCandidate] = None
        global_sec = 0
        hierarchy_stack = []

        with pdfplumber.open(self.pdf_path) as p_pdf:
            for idx, node in enumerate(ordered_graph):
                
                req_threshold = 0.65
                if current_section:
                    if current_section.word_count > 1200:
                        req_threshold = 0.35
                    elif current_section.word_count > 600:
                        req_threshold = 0.50

                is_boundary = node.boundary_confidence >= req_threshold
                if node.continuation_score > 0.70:
                    is_boundary = False

                if is_boundary or not current_section:
                    if current_section: 
                        sections.append(current_section)
                    
                    global_sec += 1
                    sec_title = self._select_best_title(idx, ordered_graph) if is_boundary else "Introduction"
                    
                    current_section = SectionCandidate(
                        sec_id=f"sec_{global_sec:03d}",
                        page_start=node.page,
                        page_end=node.page,
                        title=sec_title,
                        layout=self._detect_layout(pages[node.page], doc[node.page-1].rect.width),
                        heading_confidence=node.boundary_confidence
                    )

                    current_level = self._determine_heading_level(node)
                    while hierarchy_stack and hierarchy_stack[-1]['level'] >= current_level:
                        hierarchy_stack.pop()
                    if hierarchy_stack:
                        current_section.parent_id = hierarchy_stack[-1]['id']
                    
                    hierarchy_stack.append({'id': current_section.sec_id, 'level': current_level})

                if current_section:
                    current_section.page_end = node.page
                    current_section.add_text(node.text)
                    if node.type_probs["list"] > 0.5:
                        current_section.lists_count += 1
                        
                    if node.page not in current_section.scanned_pages:
                        try:
                            tables = p_pdf.pages[node.page - 1].find_tables()
                            if tables: 
                                current_section.tables_count += len(tables)
                        except Exception: 
                            pass
                        current_section.scanned_pages.add(node.page)

        if current_section and current_section not in sections: 
            sections.append(current_section)

        quality = round(min(1.0, 0.75 + (len(sections) * 0.005)), 2)
        
        structured_output = {
            "status": "success",
            "total_pages": total_pages,
            "overall_document_quality": quality,
            "section_candidates": [sec.to_dict() for sec in sections]
        }
        
        doc.close()
        return structured_output

def extract_document_structure(pdf_path: str) -> dict:
    """Main entry point for Navigation AI structure extraction."""
    parser = AdvancedPDFParser(pdf_path)
    result = parser.parse_document()
    
    payload_json = json.dumps(result, indent=2)
    print(f"📤 [NAVIGATION AI PAYLOAD] Fingerprint Map Length: {len(payload_json)} chars.")
    
    return {
        "status": result["status"],
        "toc": [],
        "ai_header_map": payload_json
    }