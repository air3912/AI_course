import fitz
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _build_pdf_bytes(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    payload = doc.tobytes()
    doc.close()
    return payload


def test_process_document_requires_supported_extension() -> None:
    response = client.post(
        "/api/v1/process-document",
        files={"file": ("bad.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_process_document_returns_400_when_llm_disabled() -> None:
    response = client.post(
        "/api/v1/process-document",
        files={"file": ("ok.pdf", _build_pdf_bytes("hello"), "application/pdf")},
    )
    # Default .env.example sets LLM_ENABLED=false in this repo.
    assert response.status_code == 400

