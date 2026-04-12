from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

from control_plane.internal.file_io import read_json
from control_plane.json_io import write_json_atomic
from control_plane.paths import get_paths


@dataclass(frozen=True)
class RagDoc:
    source_path: str
    title: str
    content: str


def _extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip() or fallback
    return fallback


def _chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    chunks: list[str] = []
    buf: list[str] = []
    size = 0

    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if size + len(para) + 2 > max_chars and buf:
            chunks.append("\n\n".join(buf))
            buf = [para]
            size = len(para)
        else:
            buf.append(para)
            size += len(para) + 2

    if buf:
        chunks.append("\n\n".join(buf))

    return chunks


def build_repowiki_rag_docs(repo_root: Path) -> list[RagDoc]:
    wiki_root = repo_root / ".qoder" / "repowiki" / "en" / "content"
    if not wiki_root.exists():
        return []

    docs: list[RagDoc] = []

    for md_path in wiki_root.rglob("*.md"):
        try:
            text = md_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        title = _extract_title(text, md_path.stem)
        for idx, chunk in enumerate(_chunk_text(text, max_chars=2000)):
            docs.append(
                RagDoc(
                    source_path=str(md_path.relative_to(repo_root)),
                    title=f"{title} (chunk {idx+1})",
                    content=chunk,
                )
            )

    return docs


def build_trace_rag_docs(repo_root: Path) -> list[RagDoc]:
    diag_dir = repo_root / "OUTPUTS" / "DIAGNOSTICS"
    if not diag_dir.exists():
        return []

    docs: list[RagDoc] = []
    for trace_path in diag_dir.glob("trace_*.json"):
        try:
            data = read_json(trace_path)
        except Exception:
            continue

        md = data.get("metadata", {})
        summary = md.get("summary", {})
        entry = md.get("entry_point")
        title = f"Trace: {trace_path.name}"

        content = json.dumps(
            {
                "entry_point": entry,
                "timestamp": md.get("timestamp"),
                "summary": summary,
                "inputs_sample": (data.get("inputs") or [])[:40],
                "outputs_sample": (data.get("outputs") or [])[:40],
                "scripts_loaded_sample": (data.get("scripts_loaded") or [])[:40],
            },
            indent=2,
        )

        docs.append(
            RagDoc(source_path=str(trace_path.relative_to(repo_root)), title=title, content=content)
        )

    return docs


def build_system_touch_rag_docs(repo_root: Path) -> list[RagDoc]:
    p = repo_root / "OUTPUTS" / "DIAGNOSTICS" / "system_touch_report.json"
    if not p.exists():
        return []

    try:
        data = read_json(p)
    except Exception:
        return []

    content = json.dumps(
        {
            "metadata": data.get("metadata"),
            "scripts_loaded_sample": (data.get("scripts_loaded") or [])[:80],
            "files_read_sample": (data.get("files_read") or [])[:80],
            "files_written_sample": (data.get("files_written") or [])[:80],
        },
        indent=2,
    )

    return [
        RagDoc(
            source_path=str(p.relative_to(repo_root)), title="System Touch Report", content=content
        )
    ]


def build_rag_index() -> dict:
    paths = get_paths()
    repo_root = paths.repo_root

    docs: list[RagDoc] = []
    docs.extend(build_system_touch_rag_docs(repo_root))
    docs.extend(build_trace_rag_docs(repo_root))
    docs.extend(build_repowiki_rag_docs(repo_root))

    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    return {
        "schema_version": "1.0",
        "generated_at": now,
        "doc_count": len(docs),
        "docs": [
            {
                "source_path": d.source_path,
                "title": d.title,
                "content": d.content,
            }
            for d in docs
        ],
    }


def write_rag_index() -> Path:
    paths = get_paths()
    out_path = paths.index_dir / "rag_index.json"
    idx = build_rag_index()
    write_json_atomic(out_path, idx)
    return out_path
