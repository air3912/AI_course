from pydantic import BaseModel

from app.schemas.graph import GraphEdge, GraphNode


class UploadResponse(BaseModel):
    filename: str
    saved_path: str
    status: str


class UploadProcessResponse(BaseModel):
    filename: str
    file_type: str
    saved_path: str
    upload_status: str
    parse_status: str
    graph_status: str
    text_length: int
    extracted_text_preview: str
    document_id: int
    graph_snapshot_id: int
    keywords: list[str]
    entities: list[str]
    nodes: list[GraphNode]
    edges: list[GraphEdge]
