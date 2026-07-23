import re
from typing import List, Dict, Any

class ContextOptimizer:
    def __init__(self, token_budget: int = 2000):
        self.token_budget = token_budget

    def optimize_context(self, retrieved_sections: List[Dict[str, Any]]) -> str:
        """
        Orchestrates: Deduplication -> Overlap Removal -> Section Budget Fitting
        """
        max_chars = self.token_budget * 4
        current_chars = 0
        cleaned_sections = []

        for section in retrieved_sections:
            content = section.get("content", "")
            
            # 1. Clean overlapping boundaries and duplicate structural text blocks
            content = self._remove_overlap_and_boilerplate(content)
            
            section_formatted = f"### Section: {section.get('section_name', 'General')}\n{content}"
            section_len = len(section_formatted)

            # 2. Section-level budget safety check (don't chop sections mid-sentence)
            if current_chars + section_len <= max_chars:
                cleaned_sections.append(section_formatted)
                current_chars += section_len
            else:
                print(f"🗜️ ContextOptimizer: Safe budget reached ({current_chars} chars). Skipping further overflow sections.")
                break

        return "\n\n".join(cleaned_sections)

    def _remove_overlap_and_boilerplate(self, text: str) -> str:
        """Strips out accidental line repetitions caused by smart chunk sliders"""
        lines = text.split("\n")
        seen_lines = set()
        unique_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Drop pure duplicate paragraph blocks or redundant sliding overlaps
            if stripped and stripped not in seen_lines:
                seen_lines.add(stripped)
                unique_lines.append(line)
            elif not stripped:
                unique_lines.append(line)
                
        return "\n".join(unique_lines)