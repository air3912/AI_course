from fastapi import APIRouter

from app.schemas.parse import ParseRequest, ParseResponse
from app.services.parse_service import parse_document_text

router = APIRouter()


@router.post("", response_model=ParseResponse)
def parse_document(payload: ParseRequest) -> ParseResponse:
    text = parse_document_text(payload.file_path, payload.file_type)

    preview = text[:300] if text else ""
    return ParseResponse(
        file_path=payload.file_path,
        file_type=payload.file_type,
        extracted_text_preview=preview,
        text_length=len(text),
    )
