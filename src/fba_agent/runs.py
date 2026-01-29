from __future__ import annotations

from pathlib import Path


def list_runs(runs_dir: Path) -> list[str]:
    if not runs_dir.exists():
        return []
    runs = []
    for p in runs_dir.iterdir():
        if p.is_dir():
            runs.append(p.name)
    return sorted(runs)

