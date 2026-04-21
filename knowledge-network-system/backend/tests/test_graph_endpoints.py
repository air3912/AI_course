from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_graph_build_endpoint_returns_structured_graph() -> None:
    response = client.post(
        "/api/v1/graph/build",
        json={"text": "Machine Learning enables Knowledge Graph construction with NLP methods."},
    )
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload.get("nodes"), list)
    assert isinstance(payload.get("edges"), list)
    assert isinstance(payload.get("keywords"), list)
    assert isinstance(payload.get("entities"), list)
    assert isinstance(payload.get("stats"), dict)
