import os
from pypdf import PdfReader
import config


def split_text(text, chunk_size=None, overlap=None):
    """Split extracted text into overlapping character chunks."""
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap if overlap is not None else config.CHUNK_OVERLAP

    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def ingest_pdf(file_path):
    """Read a PDF, extract text page by page, and return chunks with metadata."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.lower().endswith(".pdf"):
        raise ValueError("Please select a PDF file.")

    reader = PdfReader(file_path)
    page_chunks = []
    all_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        all_text.append(page_text)
        for chunk_index, chunk in enumerate(split_text(page_text), start=1):
            page_chunks.append({
                "text": chunk,
                "page": page_number,
                "chunk": chunk_index,
                "source": os.path.basename(file_path)
            })

    if not page_chunks:
        raise ValueError(
            "No readable text was found in this PDF. If it is a scanned PDF, "
            "run OCR on it first and upload the searchable PDF."
        )

    return {
        "filename": os.path.basename(file_path),
        "path": os.path.abspath(file_path),
        "num_pages": len(reader.pages),
        "num_chunks": len(page_chunks),
        "chunks": page_chunks,
        "full_text": "\n".join(all_text)
    }
