from pathlib import Path

import fitz

def parse_pdf_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        return ""

    chunks: list[str] = []
    with fitz.open(path) as doc:
        for page in doc:
            text = page.get_text("text")
            if text:
                chunks.append(text.strip())
    return "\n".join(item for item in chunks if item)
