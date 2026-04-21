from __future__ import annotations

from pathlib import Path

from app.services.document_loader_service import load_document_chunks


def load_document_text(file_path: str, file_type: str) -> str:
    """
    Document loader abstraction.

    Uses the built-in parsers by default. If you later decide to adopt LangChain/LlamaIndex,
    you can swap the internals here without touching API endpoints.
    """
    # Keep the existing API (string) by joining chunked output.
    chunks = load_document_chunks(file_path=file_path, file_type=file_type, chunk_size=1000)
    return "\n\n".join(chunks).strip()
