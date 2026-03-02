from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.paths import get_paths


def get_run_outputs(repo_root: Path, run_id: str) -> dict[str, Any]:
    """Scan filesystem for all artifacts produced by a specific run_id.

    Checks: status JSON, log, job JSON (done/failed), overrides dir,
    processing state, linking map, cached products, financial reports.
    """
    if not run_id or not run_id.strip():
        return {"ok": False, "error": "missing_run_id"}

    run_id = run_id.strip()
    sandbox_id = run_id[:8]
    paths = get_paths()
    files: list[dict[str, Any]] = []

    def _add(label: str, p: Path) -> None:
        if p.exists():
            files.append(
                {
                    "label": label,
                    "path": str(p),
                    "rel_path": str(p.relative_to(repo_root))
                    if _is_under(p, repo_root)
                    else str(p),
                    "size": p.stat().st_size if p.is_file() else None,
                    "type": "dir" if p.is_dir() else "file",
                }
            )

    def _is_under(child: Path, parent: Path) -> bool:
        try:
            child.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False

    # Control plane artifacts
    _add("status", paths.status_dir / f"{run_id}.json")
    _add("log", paths.logs_dir / f"{run_id}.log")
    _add("overrides_dir", paths.overrides_dir / run_id)

    for d in [paths.jobs_done, paths.jobs_failed, paths.jobs_pending, paths.jobs_running]:
        job_path = d / f"job_{run_id}.json"
        _add(f"job ({d.name})", job_path)

    # Scan for sandbox artifacts matching this run's sandbox_id
    # Processing states
    states_dir = repo_root / "OUTPUTS" / "CACHE" / "processing_states"
    if states_dir.exists():
        for f in states_dir.iterdir():
            if sandbox_id in f.name and f.suffix == ".json":
                _add("processing_state", f)

    # Linking maps
    lm_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps"
    if lm_dir.exists():
        for d in lm_dir.iterdir():
            if sandbox_id in d.name and d.is_dir():
                lm_file = d / "linking_map.json"
                _add("linking_map", lm_file)

    # Cached products
    cp_dir = repo_root / "OUTPUTS" / "cached_products"
    if cp_dir.exists():
        for f in cp_dir.iterdir():
            if sandbox_id in f.name:
                _add("cached_products", f)

    # Financial reports
    fr_dir = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports"
    if fr_dir.exists():
        for d in fr_dir.iterdir():
            if sandbox_id in d.name and d.is_dir():
                for csv in d.glob("*.csv"):
                    _add("financial_report", csv)

    # Try to get supplier info from status
    supplier = None
    status_path = paths.status_dir / f"{run_id}.json"
    if status_path.exists():
        try:
            status = read_json(status_path)
            supplier = status.get("supplier_domain")
        except Exception:
            pass

    return {
        "ok": True,
        "run_id": run_id,
        "sandbox_id": sandbox_id,
        "supplier": supplier,
        "file_count": len(files),
        "files": files,
    }
