import os 
import pdfplumber
from typing import List

DATA_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")
os.makedirs(DATA_DIR, exist_ok=True)

def extract_text_from_pdf(path: str) -> str:
    """Extrait le texte d’un PDF avec pdfplumber."""
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            text += txt + "\n"
    return text.strip()

def chunk_text(text: str, max_chars: int = 1000, overlap: int = 200) -> List[str]:
    """Découpe le texte en morceaux avec chevauchement."""
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + max_chars
        chunk = text[start:end]
        chunks.append(chunk)
        start += max_chars - overlap
    return chunks
