from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re

from bs4 import BeautifulSoup
from docx import Document
from pypdf import PdfReader


class ExtractionError(ValueError):
    pass


@dataclass(frozen=True)
class ExtractedSection:
    text: str
    page: int | None = None


SUPPORTED = {".txt", ".md", ".pdf", ".docx", ".html", ".htm"}


def normalize(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def extract_document(filename: str, data: bytes) -> list[ExtractedSection]:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise ExtractionError(f"Unsupported file type '{suffix or 'none'}'. Use TXT, MD, PDF, DOCX, or HTML.")
    if not data:
        raise ExtractionError("The uploaded file is empty.")
    try:
        if suffix in {".txt", ".md"}:
            sections = [ExtractedSection(data.decode("utf-8-sig", errors="strict"))]
        elif suffix == ".pdf":
            reader = PdfReader(BytesIO(data))
            sections = [ExtractedSection(page.extract_text() or "", i) for i, page in enumerate(reader.pages, 1)]
        elif suffix == ".docx":
            doc = Document(BytesIO(data))
            sections = [ExtractedSection("\n\n".join(p.text for p in doc.paragraphs))]
        else:
            soup = BeautifulSoup(data, "lxml")
            for node in soup(["script", "style", "nav", "footer", "header", "noscript", "svg"]):
                node.decompose()
            sections = [ExtractedSection(soup.get_text("\n"))]
    except Exception as exc:
        raise ExtractionError(f"Could not read {filename}: {exc}") from exc
    cleaned = [ExtractedSection(normalize(s.text), s.page) for s in sections if normalize(s.text)]
    if not cleaned:
        message = "No readable text found. Scanned PDFs require OCR before upload." if suffix == ".pdf" else "No readable text found in the file."
        raise ExtractionError(message)
    return cleaned
