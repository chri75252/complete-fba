from __future__ import annotations

from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.paths import get_paths


def list_status_runs() -> list[str]:
    paths = get_paths()
    if not paths.status_dir.exists():
        return []
    return [
        p.stem for p in sorted(paths.status_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    ]


def read_status(run_id: str) -> dict[str, Any] | None:
    paths = get_paths()
    path = paths.status_dir / f"{run_id}.json"
    if not path.exists():
        return None
    return read_json(path)
