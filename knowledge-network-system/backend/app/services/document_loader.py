from __future__ import annotations

from pathlib import Path

from app.services.parser_pdf import parse_pdf_text
from app.services.parser_ppt import parse_ppt_text


def load_document_text(file_path: str, file_type: str) -> str:
    """
    Document loader abstraction.

    Uses the built-in parsers by default. If you later decide to adopt LangChain/LlamaIndex,
    you can swap the internals here without touching API endpoints.
    """

    path = Path(file_path)
    if not path.exists():
        return ""

    # Optional LangChain integration (kept behind a soft import so it doesn't add a hard dependency).
    # - PDF: langchain_community.document_loaders.PyMuPDFLoader
    # - PPT/PPTX: often requires unstructured; current repo defaults to python-pptx.
    try:
        if file_type == "pdf":
            from langchain_community.document_loaders import PyMuPDFLoader  # type: ignore

            docs = PyMuPDFLoader(str(path)).load()
            return "\n".join(d.page_content for d in docs if getattr(d, "page_content", None))
    except Exception:
        # Fall back to local parser.
        pass

    if file_type == "pdf":
        return parse_pdf_text(str(path))
    if file_type in {"ppt", "pptx"}:
        return parse_ppt_text(str(path))
    return ""

