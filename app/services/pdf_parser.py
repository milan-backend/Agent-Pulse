import fitz  # PyMuPDF

def extract_toc(doc: fitz.Document) -> list:
    """
    Extracts the Table of Contents from a PyMuPDF document.
    Returns a list of lists: [level, title, page_number].
    """
    return doc.get_toc(simple=True) # Extracts standard hierarchical outline

def build_heuristic_toc(doc: fitz.Document) -> list:
    """
    If no built-in TOC exists, scans the document for larger, bold fonts to build a 
    custom outline based on text formatting heuristics.
    """
    heuristic_toc = []
    
    # We will assume that text larger than the average on the page is a heading. 
    # This logic extracts font size and style from every line of text in the document.
    for page_num in range(doc.page_count): # Iterate through all pages
        page = doc[page_num] # Load the page
        
        # Extract a detailed dictionary of all text, including meta-information like font size
        content = page.get_text("dict") 
        
        for block in content.get("blocks", []): # Blocks are the top hierarchy of a page's text
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    # Check if the text might be a header.
                    # We are looking for large text (e.g., > 12pt) and bold fonts.
                    text = span["text"].strip()
                    font_size = span["size"]
                    font_flags = span["flags"]
                    
                    # 16 in PyMuPDF flags often indicates bold. You can adjust this threshold.
                    is_bold = bool(font_flags & 16) 
                    
                    if text and font_size >= 14 and is_bold:
                        # Add to our heuristic TOC list.
                        # We use level 1 for all found headers in this simple heuristic.
                        heuristic_toc.append([1, text, page_num + 1]) 
    return heuristic_toc


def extract_document_structure(pdf_path: str) -> dict:
    """
    Main function to parse the PDF. It prioritizes the embedded TOC,
    but falls back to visual heuristics if the TOC is missing.
    """
    # Open the PDF file
    doc = fitz.open(pdf_path) 
    
    # Attempt to grab the embedded Table of Contents first
    toc = extract_toc(doc)
    
    if not toc:
        print("No embedded TOC found. Building one using font size heuristics...")
        toc = build_heuristic_toc(doc)
        
    doc.close() # Close the document when finished processing
    
    return {
        "status": "success",
        "toc": toc
    }

# Example usage:
if __name__ == "__main__":
    result = extract_document_structure("test_document.pdf")
    print(result)