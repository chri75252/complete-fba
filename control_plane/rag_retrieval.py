from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from control_plane.json_io import read_json
from control_plane.paths import get_paths


@dataclass(frozen=True)
class RagChunk:
    source_path: str
    title: str
    content: str
    score: int


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _tokenize(text: str) -> list[str]:
    norm = _normalize(text)
    if not norm:
        return []
    return [t for t in norm.split(" ") if len(t) > 2]


def _score_text(query_tokens: set[str], text: str) -> int:
    if not query_tokens:
        return 0
    hay_tokens = set(_tokenize(text))
    return sum(1 for t in query_tokens if t in hay_tokens)


def load_rag_index() -> dict[str, Any] | None:
    paths = get_paths()
    idx_path = paths.rag_index_path
    if not idx_path.exists():
        return None
    return read_json(idx_path)


def iter_rag_docs(index: dict[str, Any]) -> Iterable[dict[str, Any]]:
    docs = index.get("docs") if isinstance(index, dict) else None
    if not isinstance(docs, list):
        return []
    return [d for d in docs if isinstance(d, dict)]


def retrieve_rag_chunks(
    query: str,
    *,
    top_k: int = 4,
    max_chars_per_chunk: int = 1600,
) -> list[RagChunk]:
    index = load_rag_index()
    if not index:
        return []

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    ranked: list[RagChunk] = []
    for doc in iter_rag_docs(index):
        content = str(doc.get("content") or "")
        if not content:
            continue
        score = _score_text(query_tokens, content)
        if score <= 0:
            continue

        chunk = content[:max_chars_per_chunk]
        ranked.append(
            RagChunk(
                source_path=str(doc.get("source_path") or ""),
                title=str(doc.get("title") or ""),
                content=chunk,
                score=score,
            )
        )

    ranked.sort(key=lambda c: (c.score, len(c.content)), reverse=True)
    return ranked[: max(top_k, 1)]


def build_rag_context(chunks: list[RagChunk]) -> str:
    if not chunks:
        return ""

    lines: list[str] = []
    for idx, chunk in enumerate(chunks, start=1):
        lines.append(f"[{idx}] source_path: {chunk.source_path}")
        if chunk.title:
            lines.append(f"title: {chunk.title}")
        lines.append("content:")
        lines.append(chunk.content)
        lines.append("")

    return "\n".join(lines).strip()


def summarize_rag_index(index: dict[str, Any] | None) -> dict[str, Any]:
    if not index:
        return {"ok": False, "doc_count": 0, "generated_at": None}

    return {
        "ok": True,
        "doc_count": index.get("doc_count", 0),
        "generated_at": index.get("generated_at"),
    }
