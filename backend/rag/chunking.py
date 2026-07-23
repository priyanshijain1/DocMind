from pypdf import PdfReader


def extract_text(pdf_path: str) -> list[dict]:
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({"page": i + 1, "text": text.strip()})
    return pages


def chunk_pages(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    chunks = []
    for page in pages:
        words = page["text"].split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
            if chunk_words:
                chunks.append(
                    {
                        "page": page["page"],
                        "text": " ".join(chunk_words),
                        "chunk_index": len(chunks),
                    }
                )
    return chunks
