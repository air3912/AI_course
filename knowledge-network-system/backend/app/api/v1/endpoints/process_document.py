from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.deps import get_file_service
from app.schemas.process_document import ProcessDocumentResponse
from app.services.document_loader_service import load_document_chunks
from app.services.file_service import FileService
from app.services.llm_client import LLMError
from app.services.parse_service import extract_graph_data_from_chunks
from app.utils.file_types import detect_file_type, is_supported_upload

router = APIRouter()


@router.post("/process-document", response_model=ProcessDocumentResponse)
async def process_document(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
) -> ProcessDocumentResponse:
    if not is_supported_upload(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF/PPT/PPTX are supported.")

    saved_path = await file_service.save_upload(file)
    file_type = detect_file_type(file.filename)

    text_chunks = load_document_chunks(saved_path, file_type, chunk_size=1000)
    if not text_chunks:
        raise HTTPException(status_code=422, detail="Document text extraction returned empty content.")

    try:
        graph = await extract_graph_data_from_chunks(text_chunks)
    except LLMError as exc:
        # This endpoint is LLM-first by design; surface a clear error for client timeouts/retries.
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to process document.") from exc

    return ProcessDocumentResponse(
        filename=file.filename or "",
        file_type=file_type,
        chunk_count=len(text_chunks),
        nodes=graph.get("nodes") or [],
        relations=graph.get("relations") or [],
    )

