from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.paths import get_paths


@dataclass(frozen=True)
class TraceSummary:
    file: str
    entry_point: str | None
    timestamp: str | None
    summary: dict[str, Any]
    inputs_sample: list[str]
    outputs_sample: list[str]
    scripts_loaded_sample: list[str]


def list_trace_files(repo_root: Path) -> list[Path]:
    diag = repo_root / "OUTPUTS" / "DIAGNOSTICS"
    if not diag.exists():
        return []
    return sorted(diag.glob("trace_*.json"), key=lambda p: p.stat().st_mtime)


def read_trace_summary(repo_root: Path, limit: int = 5) -> dict[str, Any]:
    traces = list_trace_files(repo_root)
    traces = traces[-limit:] if limit > 0 else traces

    out: list[dict[str, Any]] = []

    for p in traces:
        try:
            data = read_json(p)
        except Exception:
            continue

        md = data.get("metadata", {})
        out.append(
            {
                "file": str(p),
                "entry_point": md.get("entry_point"),
                "timestamp": md.get("timestamp"),
                "summary": md.get("summary", {}),
                "inputs_sample": (data.get("inputs") or [])[:30],
                "outputs_sample": (data.get("outputs") or [])[:30],
                "scripts_loaded_sample": (data.get("scripts_loaded") or [])[:30],
            }
        )

    return {"ok": True, "count": len(out), "traces": out}
