from app.services.parse_service import clean_llm_json_output


def test_clean_llm_json_output_strips_json_fences() -> None:
    raw = """```json
{"nodes":[{"id":"A","label":"A"}],"relations":[{"source":"A","target":"A","type":"self"}]}
```"""
    cleaned = clean_llm_json_output(raw)
    assert cleaned.startswith("{")
    assert cleaned.endswith("}")
    assert "```" not in cleaned


def test_clean_llm_json_output_recovers_embedded_object() -> None:
    raw = "Here is the JSON:\n```\n{\n  \"nodes\": [], \"relations\": []\n}\n```\nThanks!"
    cleaned = clean_llm_json_output(raw)
    assert cleaned == '{\n  "nodes": [], "relations": []\n}'
