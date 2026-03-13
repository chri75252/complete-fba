from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_plane.json_io import write_json_atomic
from control_plane.paths import ensure_dirs, get_paths


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def append_audit(event: dict[str, Any]) -> Path:
    ensure_dirs()
    paths = get_paths()
    out = paths.audit_dir / "chat_tool_calls.jsonl"

    event = {**event, "ts": _now_iso()}

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return out


def append_transcript(event: dict[str, Any]) -> Path:
    ensure_dirs()
    paths = get_paths()
    out = paths.audit_dir / "chat_transcript.jsonl"

    event = {**event, "ts": _now_iso()}

    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return out


def write_session_transcript(session_id: str, payload: dict[str, Any]) -> Path:
    ensure_dirs()
    paths = get_paths()
    out = paths.transcripts_dir / f"session_{session_id}.json"
    body = {**payload}
    body.setdefault("saved_at", _now_iso())
    write_json_atomic(out, body, indent=2)
    return out
