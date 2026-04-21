from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from app.core.config import settings
from app.services.llm_client import LLMError, chat_completions_json
from app.services.parse_service import build_ai_client_config


@dataclass(frozen=True)
class LLMGraphResult:
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    keywords: list[str]
    entities: list[str]
    meta: dict[str, Any]


SYSTEM_PROMPT = """You are an expert at building knowledge graphs from documents.
Return ONLY a single JSON object. Do not wrap it in Markdown.

Goal:
- Extract important concepts and their relations from the given text.
- Output a compact knowledge network suitable for visualization.

Constraints:
- Nodes must be unique by id.
- Edge source/target must reference existing node ids.
- Prefer fewer high-quality nodes/edges over many noisy ones.
- If information is insufficient, return empty arrays.

Output JSON schema (strict):
{
  "nodes": [{"id": "string", "label": "string", "type": "keyword|entity|topic|method|dataset|paper|person|org|tool", "score": number}],
  "edges": [{"source": "string", "target": "string", "relation": "string", "weight": number}],
  "keywords": ["string"],
  "entities": ["string"]
}
"""


def _estimate_max_nodes(text: str, hard_cap: int = 40) -> int:
    # Roughly scale node count with text length, but keep it bounded.
    n = max(12, min(hard_cap, int(10 + math.log(max(2, len(text))) * 4)))
    return n


def build_user_prompt(text: str, max_nodes: int | None = None) -> str:
    limit = max_nodes or _estimate_max_nodes(text)
    # Keep prompt short; truncation is handled by caller if desired.
    return f"""Text:
{text}

Instructions:
- Extract up to {limit} nodes.
- Extract up to {max(0, limit * 2)} edges.
- Use short labels (<= 24 chars) when possible.
- Use relation verbs like: "defines", "uses", "improves", "part_of", "causes", "supports", "contrasts", "depends_on".
"""


def _normalize_graph_payload(payload: dict[str, Any]) -> LLMGraphResult:
    nodes_in = payload.get("nodes") or []
    edges_in = payload.get("edges") or []
    keywords = payload.get("keywords") or []
    entities = payload.get("entities") or []

    nodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in nodes_in:
        if not isinstance(item, dict):
            continue
        node_id = str(item.get("id") or "").strip()
        label = str(item.get("label") or node_id).strip()
        if not node_id:
            continue
        if node_id in seen:
            continue
        seen.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "label": label[:48] if label else node_id,
                "type": str(item.get("type") or "keyword"),
                "score": float(item.get("score") or 1.0),
            }
        )

    node_ids = {n["id"] for n in nodes}
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for item in edges_in:
        if not isinstance(item, dict):
            continue
        src = str(item.get("source") or "").strip()
        dst = str(item.get("target") or "").strip()
        rel = str(item.get("relation") or "related_to").strip() or "related_to"
        if not src or not dst or src == dst:
            continue
        if src not in node_ids or dst not in node_ids:
            continue
        key = (src, dst, rel)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        edges.append(
            {
                "source": src,
                "target": dst,
                "relation": rel[:64],
                "weight": float(item.get("weight") or 1.0),
            }
        )

    keywords_out = [str(x).strip() for x in keywords if str(x).strip()]
    entities_out = [str(x).strip() for x in entities if str(x).strip()]

    return LLMGraphResult(
        nodes=nodes,
        edges=edges,
        keywords=keywords_out[:30],
        entities=entities_out[:30],
        meta={},
    )


async def extract_graph_with_llm(text: str) -> LLMGraphResult:
    if not settings.llm_enabled:
        raise LLMError("LLM is disabled")

    cfg = build_ai_client_config()

    # Simple truncation guard to avoid huge requests.
    trimmed = text.strip()
    if len(trimmed) > 24000:
        trimmed = trimmed[:24000]

    user_prompt = build_user_prompt(trimmed)
    payload = await chat_completions_json(
        config=cfg,
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        json_schema_hint={"type": "object"},
    )
    result = _normalize_graph_payload(payload)
    result.meta.update(
        {
            "provider": settings.llm_provider,
            "base_url": cfg.base_url,
            "model": cfg.model,
        }
    )
    return result
