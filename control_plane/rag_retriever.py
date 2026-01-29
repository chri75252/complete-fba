from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.internal.file_io import read_json
from control_plane.rd2_policy import RagConfig, contains_secrets


@dataclass(frozen=True)
class RagChunk:
    source_path: str
    title: str
    content: str
    score: float


def _tokenize(text: str) -> set[str]:
    out: set[str] = set()
    for raw in (text or "").lower().replace("_", " ").replace("-", " ").split():
        w = "".join(ch for ch in raw if ch.isalnum())
        if len(w) >= 3:
            out.add(w)
    return out


def _score(query_tokens: set[str], doc_tokens: set[str]) -> float:
    if not query_tokens or not doc_tokens:
        return 0.0
    inter = len(query_tokens & doc_tokens)
    if inter == 0:
        return 0.0
    denom = math.sqrt(len(query_tokens) * len(doc_tokens))
    return float(inter) / denom if denom else 0.0


def load_rag_index(rag_index_path: Path) -> dict[str, Any] | None:
    if not rag_index_path.exists():
        return None
    try:
        data = read_json(rag_index_path)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("docs"), list):
        return None
    return data


def retrieve_rag(
    *,
    rag_index: dict[str, Any],
    query: str,
    config: RagConfig,
) -> dict[str, Any]:
    docs = rag_index.get("docs") or []
    if not isinstance(docs, list):
        return {"ok": True, "chunks": [], "sources": [], "scores": []}

    q_tokens = _tokenize(query)
    scored: list[RagChunk] = []

    for d in docs:
        if not isinstance(d, dict):
            continue
        src = str(d.get("source_path") or "")
        title = str(d.get("title") or "")
        content = str(d.get("content") or "")
        if not src or not content:
            continue
        if contains_secrets(content):
            continue
        d_tokens = _tokenize(title + "\n" + content)
        s = _score(q_tokens, d_tokens)
        if s <= 0.0:
            continue
        scored.append(RagChunk(source_path=src, title=title, content=content, score=s))

    scored.sort(key=lambda c: c.score, reverse=True)
    top = scored[: max(0, config.top_k)]

    chunks: list[dict[str, Any]] = []
    used_sources: list[str] = []
    scores: list[float] = []

    budget = max(0, config.max_total_chars)

    for c in top:
        if budget <= 0:
            break
        text = c.content
        if config.max_chars_per_chunk > 0 and len(text) > config.max_chars_per_chunk:
            text = text[: config.max_chars_per_chunk]
        if len(text) > budget:
            text = text[:budget]
        budget -= len(text)

        chunks.append({"source_path": c.source_path, "title": c.title, "content": text})
        used_sources.append(c.source_path)
        scores.append(float(c.score))

    return {"ok": True, "chunks": chunks, "sources": used_sources, "scores": scores}


def format_rag_context(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "RAG_CONTEXT: (disabled or no relevant chunks)\n"

    lines: list[str] = []
    lines.append("RAG_CONTEXT:")
    for c in chunks:
        lines.append("---")
        lines.append(f"source_path: {c.get('source_path')}")
        lines.append(f"title: {c.get('title')}")
        lines.append("content:")
        lines.append(str(c.get("content") or ""))
    lines.append("---")
    return "\n".join(lines) + "\n"
