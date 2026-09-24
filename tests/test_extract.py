from io import BytesIO

import pytest
from docx import Document

from plant_copilot.extract import ExtractionError, extract_document


def test_html_removes_irrelevant_elements_and_normalizes():
    data = b"<html><nav>menu</nav><main><h1>Pump A</h1><p>Seal pressure is 4 bar.</p></main><script>bad()</script></html>"
    text = extract_document("manual.html", data)[0].text
    assert "Pump A" in text and "4 bar" in text
    assert "menu" not in text and "bad" not in text


def test_docx_extracts_text():
    document = Document()
    document.add_paragraph("Bearing inspection every 500 hours.")
    output = BytesIO()
    document.save(output)
    assert "500 hours" in extract_document("record.docx", output.getvalue())[0].text


@pytest.mark.parametrize(
    ("name", "data"),
    [
        ("empty.txt", b""),
        ("image.pdf", b"not-a-pdf"),
        ("broken.docx", b"not-a-docx"),
        ("x.exe", b"abc"),
    ],
)
def test_bad_uploads_have_useful_errors(name, data):
    with pytest.raises(ExtractionError):
        extract_document(name, data)
