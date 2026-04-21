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


def test_upload_endpoint_rejects_invalid_extension() -> None:
    response = client.post(
        "/api/v1/upload",
        files={"file": ("bad.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_endpoint_accepts_pdf() -> None:
    response = client.post(
        "/api/v1/upload",
        files={"file": ("ok.pdf", _build_pdf_bytes("upload test"), "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "uploaded"
    assert data["filename"] == "ok.pdf"
