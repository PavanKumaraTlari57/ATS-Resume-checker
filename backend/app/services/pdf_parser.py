import fitz  # this is PyMuPDF
 
 
def extract_text_from_pdf(file_path: str) -> str:
    """Read a PDF file and return all its text as one string."""
    pages_text = []
 
    with fitz.open(file_path) as pdf:
        for page in pdf:
            pages_text.append(page.get_text())
 
    return "\n".join(pages_text).strip()
 