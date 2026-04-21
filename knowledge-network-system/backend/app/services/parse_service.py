from __future__ import annotations

import json
import re

from app.core.config import settings
from app.services.document_loader import load_document_text
from app.services.llm_client import LLMConfig
from app.services.llm_client import LLMError, chat_completions_text


def parse_document_text(file_path: str, file_type: str) -> str:
    return load_document_text(file_path=file_path, file_type=file_type)


def build_ai_client_config() -> LLMConfig:
    """
    Central place to initialize AI client config from `.env` via app.core.config.settings.
    Never hardcode secrets here.
    """

    return LLMConfig(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
    )


def _chunk_text(text: str, *, chunk_size: int = 1000) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    if chunk_size <= 0:
        return [text]
    # Prefer paragraph-ish boundaries.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p and p.strip()]

    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0

    def flush() -> None:
        nonlocal buf, buf_len
        if not buf:
            return
        chunk = "\n\n".join(buf).strip()
        if chunk:
            chunks.append(chunk)
        buf = []
        buf_len = 0

    for p in paragraphs:
        if len(p) > chunk_size:
            flush()
            start = 0
            while start < len(p):
                part = p[start : start + chunk_size].strip()
                if part:
                    chunks.append(part)
                start += chunk_size
            continue

        extra = (2 if buf else 0) + len(p)
        if buf_len + extra > chunk_size:
            flush()
        buf.append(p)
        buf_len += extra

    flush()
    return chunks


def clean_llm_json_output(raw: str) -> str:
    """
    Remove common wrappers like ```json ... ``` and return a pure JSON string.
    """
    s = (raw or "").strip()
    if not s:
        return s

    # Strip fenced code blocks.
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*```$", "", s)
        s = s.strip()

    # If the model added leading "json" token on its own line.
    s = re.sub(r"^\s*json\s*\n", "", s, flags=re.IGNORECASE).strip()

    # Recover the first JSON object in the text.
    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        s = s[start : end + 1].strip()

    return s


def _merge_graph_payload(target: dict, payload: dict) -> None:
    nodes_by_id: dict[str, dict] = target.setdefault("_nodes_by_id", {})
    edges_set: set[tuple[str, str, str]] = target.setdefault("_edges_set", set())

    nodes = payload.get("nodes") or []
    for n in nodes:
        if not isinstance(n, dict):
            continue
        node_id = str(n.get("id") or "").strip()
        label = str(n.get("label") or node_id).strip()
        if not node_id:
            continue
        if node_id not in nodes_by_id:
            nodes_by_id[node_id] = {"id": node_id, "label": label or node_id}

    rels = payload.get("relations") or payload.get("edges") or []
    for e in rels:
        if not isinstance(e, dict):
            continue
        src = str(e.get("source") or "").strip()
        dst = str(e.get("target") or "").strip()
        typ = str(e.get("type") or e.get("relation") or "related_to").strip() or "related_to"
        if not src or not dst or src == dst:
            continue
        edges_set.add((src, dst, typ))


async def extract_graph_data(text: str) -> dict:
    """
    Send chunked text to the LLM and extract graph JSON.

    Output:
    {
      "nodes": [{"id": "...", "label": "..."}],
      "relations": [{"source": "...", "target": "...", "type": "..."}]
    }
    """
    if not settings.llm_enabled:
        raise LLMError("LLM is disabled (set LLM_ENABLED=true in .env)")

    cfg = build_ai_client_config()
    text_chunks = _chunk_text(text, chunk_size=1000)
    return await extract_graph_data_from_chunks(text_chunks, cfg=cfg)


async def extract_graph_data_from_chunks(text_chunks: list[str], *, cfg: LLMConfig | None = None) -> dict:
    """
    Same as extract_graph_data(), but expects pre-chunked text.
    This is useful when a dedicated document_loader already produced chunks.
    """
    if not settings.llm_enabled:
        raise LLMError("LLM is disabled (set LLM_ENABLED=true in .env)")

    cfg = cfg or build_ai_client_config()
    if not text_chunks:
        return {"nodes": [], "relations": []}

    system_prompt = (
        "You are a precise information extraction engine.\n"
        "Return ONLY a single JSON object. Do not add Markdown, code fences, or extra text.\n"
        "Schema:\n"
        "{\n"
        '  "nodes": [{"id": "string", "label": "string"}],\n'
        '  "relations": [{"source": "string", "target": "string", "type": "string"}]\n'
        "}\n"
        "Rules:\n"
        "- ids must be short, stable, and unique.\n"
        "- relations must reference node ids.\n"
        "- prefer fewer, higher-quality nodes/relations.\n"
    )

    merged: dict = {}
    for idx, text_chunk in enumerate(text_chunks, start=1):
        user_prompt = (
            f"Chunk {idx}/{len(text_chunks)}:\n{text_chunk}\n\n"
            "Extract key concepts and relations from this chunk.\n"
            "Return JSON only."
        )
        raw = await chat_completions_text(config=cfg, system_prompt=system_prompt, user_prompt=user_prompt)
        cleaned = clean_llm_json_output(raw)
        payload = json.loads(cleaned)
        if not isinstance(payload, dict):
            raise LLMError("LLM did not return a JSON object")
        _merge_graph_payload(merged, payload)

    nodes_by_id: dict[str, dict] = merged.get("_nodes_by_id", {})
    edges_set: set[tuple[str, str, str]] = merged.get("_edges_set", set())

    node_ids = set(nodes_by_id.keys())
    relations = [
        {"source": s, "target": t, "type": typ}
        for (s, t, typ) in sorted(edges_set)
        if s in node_ids and t in node_ids
    ]
    nodes = list(nodes_by_id.values())

    return {"nodes": nodes, "relations": relations}
