"""Read and normalize source data."""
from pathlib import Path
from typing import Iterable
from pypdf import PdfReader
from .models import DocumentPage
from .normalize import clean_page


def load_pdf(path: Path, document_id: str, source: str,
             page_numbers: Iterable[int] | None = None) -> list[DocumentPage]:
    """Extract physical pages (1-based). Flags pages with little/no text."""
    reader = PdfReader(str(path))
    nums = list(page_numbers) if page_numbers is not None else range(1, len(reader.pages) + 1)
    pages = []
    for n in nums:
        text = reader.pages[n - 1].extract_text() or ""
        n_chars = len(text.strip())
        pages.append(DocumentPage(document_id, source, n, text,
                                  {"chars": n_chars, "empty": n_chars == 0, "low_text": n_chars < 300}))
    return pages


def normalize_text(text: str) -> str:
    """Remove header/footer/labels/footnote markers; keep structure:
    paragraphs separated by blank lines, headings as '## ...', bullets as '• ...'."""
    blocks, _ = clean_page(text)
    parts = []
    for b in blocks:
        if b["type"] == "heading":
            parts.append("## " + b["text"])
        elif b["type"] == "bullet":
            parts.append("• " + b["text"])
        else:
            parts.append(b["text"])
    return "\n\n".join(parts)