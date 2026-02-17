from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str | None = None
    api_key: str | None = None
    base_url: str | None = None


def load_llm_config() -> LLMConfig:
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

    return LLMConfig(provider="none")


def _post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8")
    return json.loads(body)


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
        return json.loads(text)

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
        return json.loads(text)

    if cfg.provider == "openai":
        if not cfg.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        base = (cfg.base_url or "https://api.openai.com").rstrip("/")
        url = f"{base}/v1/chat/completions"
        payload = {
            "model": cfg.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        out = _post_json(
            url,
            payload,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg.api_key}"},
        )
        text = out["choices"][0]["message"]["content"]
        return json.loads(text)

    if cfg.provider == "anthropic":
        if not cfg.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        base = (cfg.base_url or "https://api.anthropic.com").rstrip("/")
        url = f"{base}/v1/messages"
        payload = {
            "model": cfg.model,
            "max_tokens": 512,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        out = _post_json(
            url,
            payload,
            headers={
                "Content-Type": "application/json",
                "x-api-key": cfg.api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        text = out["content"][0]["text"]
        return json.loads(text)

    raise RuntimeError(f"Unsupported provider: {cfg.provider}")
