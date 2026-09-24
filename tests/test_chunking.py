from plant_copilot.chunking import chunk_sections
from plant_copilot.extract import ExtractedSection


def test_chunking_preserves_source_page_and_boundaries():
    text = "First inspection completed. " * 12 + "\n\nSecond paragraph records vibration. " * 10
    chunks = chunk_sections([ExtractedSection(text, page=7)], "report.pdf", 180, 30)
    assert len(chunks) > 1
    assert all(c.source == "report.pdf" and c.page == 7 for c in chunks)
    assert all(len(c.text) <= 210 for c in chunks)


def test_invalid_chunk_settings_rejected():
    try:
        chunk_sections([ExtractedSection("text")], "x.txt", 50, 50)
        assert False
    except ValueError as exc:
        assert "Chunk size" in str(exc)

