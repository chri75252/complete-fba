from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any

from control_plane.env_config import ensure_llm_env


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


def load_llm_config() -> LLMConfig:
    ensure_llm_env()

    provider = os.environ.get("CONTROL_PLANE_LLM_PROVIDER", "none").strip().lower()
    model = os.environ.get("CONTROL_PLANE_LLM_MODEL")

    if provider == "openai":
        return LLMConfig(
            provider=provider,
            model=model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    if provider == "anthropic":
        return LLMConfig(
            provider=provider,
            model=model or os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
        )

    if provider in {"ollama", "lmstudio"}:
        return LLMConfig(
            provider=provider,
            model=model or os.environ.get("LOCAL_LLM_MODEL", "llama3"),
            base_url=os.environ.get("CONTROL_PLANE_LLM_BASE_URL"),
        )

    if provider == "opencode":
        return LLMConfig(
            provider=provider,
            model=os.environ.get("OPENCODE_MODEL") or model or "minimax-m2.5-free",
            api_key=os.environ.get("OPENCODE_API_KEY"),
            base_url=os.environ.get("CONTROL_PLANE_LLM_BASE_URL", "https://opencode.ai/zen"),
        )

    return LLMConfig(provider="none")


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")

    request_headers = dict(headers)
    if not any(k.lower() == "user-agent" for k in request_headers):
        request_headers["User-Agent"] = "python-requests/2.32.3"

    req = urllib.request.Request(url, data=data, headers=request_headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


def _safe_json_loads(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    raw = raw.removeprefix("```json").removeprefix("```").strip()
    if raw.endswith("```"):
        raw = raw[:-3].strip()

    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


def generate_json(prompt: str) -> dict[str, Any]:
    cfg = load_llm_config()
    if cfg.provider == "none":
        raise RuntimeError("LLM provider disabled")

    if cfg.provider == "ollama":
        base = (cfg.base_url or "http://localhost:11434").rstrip("/")
        url = f"{base}/api/chat"
        payload = {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        out = _post_json(url, payload, headers={"Content-Type": "application/json"})
        text = (out.get("message") or {}).get("content")
        if not isinstance(text, str):
            raise RuntimeError("ollama_response_missing_message_content")
        return _safe_json_loads(text)

    if cfg.provider == "lmstudio":
        base = (cfg.base_url or "http://localhost:1234").rstrip("/")
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        out = _post_json(url, payload, headers={"Content-Type": "application/json"})
        text = out["choices"][0]["message"]["content"]
        return _safe_json_loads(text)

    if cfg.provider == "opencode":
        base = (cfg.base_url or "https://opencode.ai/zen").rstrip("/")
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {cfg.api_key}"}
        out = _post_json(url, payload, headers=headers)
        text = out["choices"][0]["message"]["content"]
        return _safe_json_loads(text)

    raise RuntimeError(f"Unsupported provider: {cfg.provider}")
