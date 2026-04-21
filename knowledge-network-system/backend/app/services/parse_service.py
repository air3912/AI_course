from app.services.document_loader import load_document_text


def parse_document_text(file_path: str, file_type: str) -> str:
    return load_document_text(file_path=file_path, file_type=file_type)
