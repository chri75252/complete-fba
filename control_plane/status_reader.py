from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from control_plane.internal.file_io import read_json
from control_plane.internal.path_resolver import get_control_plane_paths


class StatusReader:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root

    def get_status(self, run_id: str) -> dict[str, Any] | None:
        paths = get_control_plane_paths(self.repo_root)
        status_path = paths.status_dir / f"{run_id}.json"
        if not status_path.exists():
            return None
        return read_json(status_path)

    def list_run_ids(self) -> list[str]:
        paths = get_control_plane_paths(self.repo_root)
        if not paths.status_dir.exists():
            return []
        run_ids = []
        for p in paths.status_dir.glob("*.json"):
            run_ids.append(p.stem)
        return sorted(run_ids)

    def tail_run_log(self, run_id: str, lines: int = 200) -> list[str]:
        paths = get_control_plane_paths(self.repo_root)
        log_path = paths.logs_dir / f"{run_id}.log"
        if not log_path.exists():
            return []

        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        return [ln.rstrip("\n\r") for ln in all_lines[-lines:]]
