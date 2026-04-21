from pydantic import BaseModel


class GraphBuildRequest(BaseModel):
    text: str
    prefer_llm: bool = True


class GraphNode(BaseModel):
    id: str
    label: str
    type: str = "keyword"
    score: float = 1.0


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float = 1.0
    relation: str = "co_occurs"


class GraphStats(BaseModel):
    node_count: int
    edge_count: int
    keyword_count: int
    entity_count: int


class GraphBuildResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    keywords: list[str] = []
    entities: list[str] = []
    stats: GraphStats
