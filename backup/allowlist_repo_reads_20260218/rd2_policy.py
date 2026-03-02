from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_TOP_K = 5
DEFAULT_MAX_CHARS_PER_CHUNK = 1200
DEFAULT_MAX_RAG_CONTEXT_CHARS = 6000


RAG_TRIGGER_WORDS = {
    "workflow",
    "config",
    "configuration",
    "state",
    "processing_state",
    "persistent_category_index",
    "outputs",
    "output",
    "file",
    "files",
    "path",
    "paths",
    "categories",
    "category",
    "linking_map",
    "amazon_cache",
    "runner",
    "script",
}


SECRET_PATTERNS = [
    re.compile(r"api[_-]?key", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"credentials?", re.IGNORECASE),
]


BLOCKED_BASENAMES = {
    ".env",
    ".env.local",
    "credentials.json",
    "credentials.yaml",
}


BLOCKED_SUBSTRINGS = [
    "\\.git\\",
    "/.git/",
]


ALLOWED_RAG_SOURCES = [
    ".qoder/repowiki/",
    "OUTPUTS/DIAGNOSTICS/trace_",
    "OUTPUTS/DIAGNOSTICS/system_touch_report.json",
]


def should_use_rag(user_text: str) -> bool:
    t = (user_text or "").lower()
    return any(w in t for w in RAG_TRIGGER_WORDS)


def contains_secrets(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in SECRET_PATTERNS)


def is_blocked_path(path: Path) -> bool:
    name = path.name.lower()
    if name in BLOCKED_BASENAMES:
        return True

    s = str(path).replace("\\", "/")
    if any(x in s for x in BLOCKED_SUBSTRINGS):
        return True

    if any(p.search(s) for p in SECRET_PATTERNS):
        return True

    return False


def redact_secrets(text: str) -> str:
    if not text:
        return text

    redacted = text
    for pat in SECRET_PATTERNS:
        redacted = pat.sub("[REDACTED]", redacted)
    return redacted


@dataclass(frozen=True)
class RagConfig:
    enabled: bool
    top_k: int = DEFAULT_TOP_K
    max_chars_per_chunk: int = DEFAULT_MAX_CHARS_PER_CHUNK
    max_total_chars: int = DEFAULT_MAX_RAG_CONTEXT_CHARS


def default_rag_config() -> RagConfig:
    return RagConfig(enabled=True)


def clamp_int(value: Any, default: int, *, lo: int, hi: int) -> int:
    try:
        n = int(value)
    except Exception:
        return default
    return max(lo, min(hi, n))
