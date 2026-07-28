import re
from typing import List, Dict, Any

class DocumentAnalyzer:
    """
    Component 1: Advanced Document Analyzer
    Parses structural signals, numbering patterns, layout hierarchies, tables, and lists page-by-page.
    """
    def analyze_document(self, full_text: str, filename: str) -> List[Dict[str, Any]]:
        pages = full_text.split("\f")
        if len(pages) <= 1:
            pages = [full_text[i:i+3000] for i in range(0, len(full_text), 3000)]

        analyzed_pages = []
        for idx, page_content in enumerate(pages, 1):
            lines = [line.strip() for line in page_content.split("\n") if line.strip()]
            
            headings = []
            numbering_schemes = []
            
            # 🟢 Structural layout flags
            has_table = bool(re.search(r'(\t|\s{4,}\|)', page_content)) or page_content.count('|') > 3
            has_bullets = any(line.startswith(('-', '*', '•')) for line in lines)
            has_numbered_lists = any(re.match(r'^(\d+[\.\)]|[a-zA-Z][\.\)])\s+', line) for line in lines)

            for line in lines:
                if re.match(r'^(\d+(\.\d+)*)\s+[A-Z]', line) or re.match(r'^(CHAPTER|SECTION|PART)\s+\d+', line, re.IGNORECASE):
                    headings.append(line)
                    num_match = re.match(r'^(\d+(\.\d+)*)', line)
                    if num_match:
                        numbering_schemes.append(num_match.group(1))
                elif len(line) < 80 and line.isupper() and len(line.split()) < 10:
                    headings.append(line)

            first_para = lines[0] if lines else ""
            last_para = lines[-1] if lines else ""
            
            analyzed_pages.append({
                "page": idx,
                "page_number": idx,
                "line_count": len(lines),
                "headings": headings,
                "numbering_schemes": numbering_schemes,
                "layout": {
                    "has_table": has_table,
                    "has_bullets": has_bullets,
                    "has_numbered_lists": has_numbered_lists
                },
                "first_paragraph": first_para,
                "last_paragraph": last_para,
                "raw_snippet": page_content[:500]
            })

        return analyzed_pages