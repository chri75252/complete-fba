from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
