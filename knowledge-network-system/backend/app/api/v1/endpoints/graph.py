from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_graph_service
from app.db.session import SessionLocal
from app.models.graph import GraphSnapshot
from app.schemas.graph import GraphBuildRequest, GraphBuildResponse
from app.services.graph_service import GraphService

router = APIRouter()


@router.post("/build", response_model=GraphBuildResponse)
async def build_graph(
    payload: GraphBuildRequest,
    graph_service: GraphService = Depends(get_graph_service),
) -> GraphBuildResponse:
    graph = await graph_service.build_from_text(payload.text, prefer_llm=payload.prefer_llm)
    return GraphBuildResponse(**graph)


@router.get("/snapshot/{snapshot_id}", response_model=GraphBuildResponse)
def get_graph_snapshot(snapshot_id: int) -> GraphBuildResponse:
    with SessionLocal() as session:
        row = session.query(GraphSnapshot).filter(GraphSnapshot.id == snapshot_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Graph snapshot not found.")
        graph = row.data.get("graph")
        if not graph:
            raise HTTPException(status_code=404, detail="Graph data not found in snapshot.")
        return GraphBuildResponse(**graph)
