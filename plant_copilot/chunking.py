from dataclasses import dataclass
import re

from .extract import ExtractedSection


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str
    page: int | None
    index: int


def _units(text: str) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    result: list[str] = []
    for paragraph in paragraphs:
        result.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", paragraph) if s.strip())
    return result


def chunk_sections(sections: list[ExtractedSection], source: str, size: int, overlap: int) -> list[Chunk]:
    if size < 100 or overlap < 0 or overlap >= size:
        raise ValueError("Chunk size must be >= 100 and overlap must be >= 0 and smaller than size")
    chunks: list[Chunk] = []
    for section in sections:
        current = ""
        for unit in _units(section.text):
            while len(unit) > size:
                head, unit = unit[:size], unit[max(1, size - overlap):]
                if current:
                    chunks.append(Chunk(current, source, section.page, len(chunks)))
                    current = ""
                chunks.append(Chunk(head, source, section.page, len(chunks)))
            candidate = f"{current} {unit}".strip()
            if current and len(candidate) > size:
                chunks.append(Chunk(current, source, section.page, len(chunks)))
                carry = current[-overlap:] if overlap else ""
                current = f"{carry} {unit}".strip()
            else:
                current = candidate
        if current:
            chunks.append(Chunk(current, source, section.page, len(chunks)))
    return chunks

