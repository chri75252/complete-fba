from __future__ import annotations

import os
from pathlib import Path


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
    _load_dotenv_if_present()

    provider_raw = os.environ.get("CONTROL_PLANE_LLM_PROVIDER")
    provider = (_clean(provider_raw) or "none").lower()
    os.environ["CONTROL_PLANE_LLM_PROVIDER"] = provider

    llm_base = _set_clean("CONTROL_PLANE_LLM_BASE_URL")
    llm_model = _set_clean("CONTROL_PLANE_LLM_MODEL")
    opencode_model = _set_clean("OPENCODE_MODEL")
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

    if provider == "opencode" and opencode_model:
        os.environ["CONTROL_PLANE_LLM_MODEL"] = opencode_model


def _load_dotenv_if_present() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    try:
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip().removeprefix("export ").strip()
            if not key:
                continue

            value = value.strip()
            if len(value) >= 2 and (
                (value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))
            ):
                value = value[1:-1]

            if key not in os.environ:
                os.environ[key] = value
    except Exception:
        return
