import re
from typing import List, Dict, Any

def analyze_pdf_structure(pages_text: List[str]) -> Dict[str, Any]:
    """Computes deterministic structural statistics across all pages with zero LLM tokens."""
    total_pages = len(pages_text)
    if total_pages == 0:
        return {"total_pages": 0, "strategy": "default"}

    page_word_counts = []
    heading_count = 0
    table_row_count = 0
    qa_indicators = 0

    for text in pages_text:
        words = text.split()
        page_word_counts.append(len(words))
        
        if re.search(r'^\s*(\d+(\.\d+)*)\s+[A-Z]', text, re.MULTILINE):
            heading_count += 1
            
        lines = text.split('\n')
        for line in lines:
            if '|' in line or len(re.findall(r'\b\d+\b', line)) >= 3:
                table_row_count += 1
                
        if 'Q:' in text or 'Question:' in text or 'FAQ' in text:
            qa_indicators += 1

    avg_words = sum(page_word_counts) / total_pages if total_pages > 0 else 0

    return {
        "total_pages": total_pages,
        "avg_words_per_page": avg_words,
        "has_headings": heading_count > (total_pages * 0.1),
        "has_tables": table_row_count > (total_pages * 2),
        "is_qa_heavy": qa_indicators > (total_pages * 0.2)
    }

def select_intelligent_pages(pages_text: List[str], max_token_budget: int = 8000) -> str:
    """Selects representative pages based on a strict token budget (~4 chars per token)."""
    total_pages = len(pages_text)
    if total_pages == 0:
        return ""

    max_chars = max_token_budget * 4
    selected_indices = set()

    # Always include the First page and the Last page
    selected_indices.add(0)
    if total_pages > 1:
        selected_indices.add(total_pages - 1)

    # Select evenly distributed representative checkpoints
    step = max(1, total_pages // 8)
    for i in range(0, total_pages, step):
        selected_indices.add(i)

    compiled_sample = []
    current_chars = 0

    for idx in sorted(list(selected_indices)):
        page_content = f"\n--- [PAGE {idx + 1} OF {total_pages}] ---\n{pages_text[idx]}"
        page_chars = len(page_content)
        
        if current_chars + page_chars > max_chars and len(compiled_sample) > 0:
            break
            
        compiled_sample.append(page_content)
        current_chars += page_chars

    return "".join(compiled_sample)