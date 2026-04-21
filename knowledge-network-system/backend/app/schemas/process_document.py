from pydantic import BaseModel


class ProcessNode(BaseModel):
    id: str
    label: str


class ProcessRelation(BaseModel):
    source: str
    target: str
    type: str


class ProcessDocumentResponse(BaseModel):
    filename: str
    file_type: str
    chunk_count: int
    nodes: list[ProcessNode]
    relations: list[ProcessRelation]

