from app.services.graph_service import GraphService


def test_graph_build() -> None:
    service = GraphService()
    graph = service.build_from_text("Knowledge Graph uses NLP and Machine Learning in AI systems.")
    assert "nodes" in graph
    assert "edges" in graph
    assert "keywords" in graph
    assert "entities" in graph
    assert "stats" in graph
