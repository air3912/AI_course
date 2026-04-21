from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class LLMConfig:
    base_url: str
    api_key: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 1400
    timeout_s: float = 45.0


class LLMError(RuntimeError):
    pass


def _join_url(base_url: str, path: str) -> str:
    base = base_url.rstrip("/")
    suffix = path if path.startswith("/") else f"/{path}"
    return f"{base}{suffix}"


async def chat_completions_json(
    *,
    config: LLMConfig,
    system_prompt: str,
    user_prompt: str,
    json_schema_hint: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Call an OpenAI-compatible Chat Completions endpoint and return a JSON object.

    This is intentionally lightweight (no langchain dependency) and works with
    providers that expose OpenAI-compatible APIs (including some Qwen endpoints).
    """

    url = _join_url(config.base_url, "/chat/completions")
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    payload: dict[str, Any] = {
        "model": config.model,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    # Newer OpenAI-compatible servers may support "response_format" forcing JSON.
    if json_schema_hint is not None:
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=config.timeout_s) as client:
            resp = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise LLMError(f"LLM error {resp.status_code}: {resp.text[:500]}")

    try:
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise LLMError("LLM response was not valid JSON") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        raise LLMError("LLM response missing choices/message/content") from exc

    # If provider didn't enforce JSON mode, try to recover JSON object from text.
    content_str = (content or "").strip()
    if not content_str:
        raise LLMError("LLM returned empty content")

    # Fast path: whole content is a JSON object.
    try:
        parsed = json.loads(content_str)
        if isinstance(parsed, dict):
            return parsed
    except Exception:  # noqa: BLE001
        pass

    # Recovery: find first {...} span and parse.
    start = content_str.find("{")
    end = content_str.rfind("}")
    if start >= 0 and end > start:
        snippet = content_str[start : end + 1]
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, dict):
                return parsed
        except Exception as exc:  # noqa: BLE001
            raise LLMError("Failed to parse JSON object from LLM response") from exc

    raise LLMError("LLM response did not contain a JSON object")


async def chat_completions_text(
    *,
    config: LLMConfig,
    system_prompt: str,
    user_prompt: str,
) -> str:
    """
    Call an OpenAI-compatible Chat Completions endpoint and return the assistant content as text.
    """

    url = _join_url(config.base_url, "/chat/completions")
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"

    payload: dict[str, Any] = {
        "model": config.model,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=config.timeout_s) as client:
            resp = await client.post(url, headers=headers, json=payload)
    except httpx.HTTPError as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    if resp.status_code >= 400:
        raise LLMError(f"LLM error {resp.status_code}: {resp.text[:500]}")

    try:
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        raise LLMError("LLM response was not valid JSON") from exc

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception as exc:  # noqa: BLE001
        raise LLMError("LLM response missing choices/message/content") from exc

    content_str = (content or "").strip()
    if not content_str:
        raise LLMError("LLM returned empty content")
    return content_str
