import re
from typing import List, Dict, Any

class ContextOptimizer:
    def __init__(self, token_budget: int = 2000):
        self.token_budget = token_budget

    def optimize_context(self, retrieved_sections: List[Dict[str, Any]]) -> str:
        """
        Orchestrates: Deduplication -> Overlap Removal -> Context Ordering -> Budget Truncation
        """
        cleaned_contents = []
        
        for section in retrieved_sections:
            content = section.get("content", "")
            
            # 1. Clean overlapping boundaries and duplicate structural text blocks
            content = self._remove_overlap_and_boilerplate(content)
            
            # Safe section header fallback resolution
            header_name = section.get("section_name") or section.get("filename") or "Document Section"
            cleaned_contents.append(f"### Section: {header_name}\n{content}")
            
        # 2. Assemble Context with Priority Ordering
        raw_assembled_context = "\n\n".join(cleaned_contents)
        
        # 3. Enforce Token Budget via strict Character/Token Constraint Scaling
        final_prompt_context = self._enforce_budget(raw_assembled_context)
        
        return final_prompt_context

    def _remove_overlap_and_boilerplate(self, text: str) -> str:
        """Strips out accidental line repetitions caused by smart chunk sliders"""
        lines = text.split("\n")
        seen_lines = set()
        unique_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and stripped not in seen_lines:
                seen_lines.add(stripped)
                unique_lines.append(line)
            elif not stripped:
                unique_lines.append(line)
                
        return "\n".join(unique_lines)

    def _enforce_budget(self, full_text: str) -> str:
        """Ensures the text context doesn't spill over your ~2000 token budget baseline"""
        max_chars = self.token_budget * 4
        
        if len(full_text) <= max_chars:
            return full_text
            
        print(f"🗜️ ContextOptimizer: Budget exceeded. Truncating context to safe token window.")
        return full_text[:max_chars] + "\n\n[Context truncated due to system token budget configuration...]"