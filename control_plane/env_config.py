from __future__ import annotations

import os
from typing import Optional


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _set_clean(key: str) -> str | None:
    raw = os.environ.get(key)
    cleaned = _clean(raw)
    if cleaned is None:
        if raw is not None:
            os.environ.pop(key, None)
        return None
    if raw != cleaned:
        os.environ[key] = cleaned
    return cleaned


def ensure_llm_env() -> None:
    provider_raw = os.environ.get("CONTROL_PLANE_LLM_PROVIDER")
    provider = (_clean(provider_raw) or "none").lower()
    os.environ["CONTROL_PLANE_LLM_PROVIDER"] = provider

    llm_base = _set_clean("CONTROL_PLANE_LLM_BASE_URL")
    llm_model = _set_clean("CONTROL_PLANE_LLM_MODEL")
    ollama_base = _set_clean("CONTROL_PLANE_OLLAMA_BASE_URL")
    ollama_model = _set_clean("CONTROL_PLANE_OLLAMA_MODEL")

    if provider in {"ollama", "lmstudio"}:
        if ollama_base and not llm_base:
            os.environ["CONTROL_PLANE_LLM_BASE_URL"] = ollama_base
        if llm_base and not ollama_base:
            os.environ["CONTROL_PLANE_OLLAMA_BASE_URL"] = llm_base
        if ollama_model and not llm_model:
            os.environ["CONTROL_PLANE_LLM_MODEL"] = ollama_model
        if llm_model and not ollama_model:
            os.environ["CONTROL_PLANE_OLLAMA_MODEL"] = llm_model
