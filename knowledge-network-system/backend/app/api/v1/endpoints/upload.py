from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import desc

from app.api.deps import get_file_service
from app.db.session import SessionLocal
from app.models.document import Document
from app.models.graph import GraphSnapshot
from app.schemas.upload import UploadProcessResponse, UploadResponse
from app.services.file_service import FileService
from app.services.graph_service import GraphService
from app.services.parse_service import parse_document_text
from app.utils.file_types import detect_file_type, is_supported_upload

router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service),
) -> UploadResponse:
    if not is_supported_upload(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF/PPT/PPTX are supported.")
    saved_path = await file_service.save_upload(file)
    return UploadResponse(filename=file.filename, saved_path=saved_path, status="uploaded")


@router.post("/process", response_model=UploadProcessResponse)
async def upload_and_process(
    file: UploadFile = File(...),
    prefer_llm: bool = True,
    file_service: FileService = Depends(get_file_service),
) -> UploadProcessResponse:
    if not is_supported_upload(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF/PPT/PPTX are supported.")

    saved_path = await file_service.save_upload(file)
    file_type = detect_file_type(file.filename)
    text = parse_document_text(saved_path, file_type)
    if not text.strip():
        raise HTTPException(status_code=422, detail="Document text extraction returned empty content.")

    graph_service = GraphService()
    graph = await graph_service.build_from_text(text, prefer_llm=prefer_llm)

    with SessionLocal() as session:
        document = Document(filename=file.filename, file_type=file_type, path=saved_path)
        session.add(document)
        session.flush()

        snapshot = GraphSnapshot(
            data={
                "document_id": document.id,
                "filename": file.filename,
                "file_type": file_type,
                "text_length": len(text),
                "extracted_text_preview": graph_service.build_preview(text),
                "graph": graph,
                "graph_meta": graph.get("meta") or {},
            }
        )
        session.add(snapshot)
        session.commit()
        session.refresh(document)
        session.refresh(snapshot)

    return UploadProcessResponse(
        filename=file.filename,
        file_type=file_type,
        saved_path=saved_path,
        upload_status="completed",
        parse_status="completed",
        graph_status="completed",
        text_length=len(text),
        extracted_text_preview=graph_service.build_preview(text),
        document_id=document.id,
        graph_snapshot_id=snapshot.id,
        keywords=graph["keywords"],
        entities=graph["entities"],
        nodes=graph["nodes"],
        edges=graph["edges"],
    )


@router.get("/history")
def list_upload_history(limit: int = 10) -> list[dict]:
    with SessionLocal() as session:
        rows = (
            session.query(GraphSnapshot)
            .order_by(desc(GraphSnapshot.id))
            .limit(max(1, min(limit, 50)))
            .all()
        )
        return [
            {
                "graph_snapshot_id": row.id,
                "created_at": row.created_at.isoformat(),
                "document_id": row.data.get("document_id"),
                "filename": row.data.get("filename"),
                "file_type": row.data.get("file_type"),
                "text_length": row.data.get("text_length", 0),
                "node_count": len(row.data.get("graph", {}).get("nodes", [])),
                "edge_count": len(row.data.get("graph", {}).get("edges", [])),
            }
            for row in rows
        ]
