from app.services.parser_pdf import parse_pdf_text
from app.services.parser_ppt import parse_ppt_text


def parse_document_text(file_path: str, file_type: str) -> str:
    if file_type == "pdf":
        return parse_pdf_text(file_path)
    if file_type in {"ppt", "pptx"}:
        return parse_ppt_text(file_path)
    return ""
