from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_plane.json_io import read_json, write_json_atomic
from control_plane.paths import get_paths


@dataclass(frozen=True)
class RunRequest:
    supplier_domain: str
    workflow_key: str
    runner_script: str
    category_urls: list[str]
    max_products: int
    max_products_per_category: int
    notes: str | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def create_run_workspace(run_id: str) -> Path:
    paths = get_paths()
    run_dir = paths.overrides_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_categories_subset(run_id: str, supplier_domain: str, category_urls: list[str]) -> Path:
    run_dir = create_run_workspace(run_id)
    subset_path = run_dir / "categories_subset.json"
    payload = {
        "schema_version": "1.0",
        "supplier_domain": supplier_domain,
        "category_urls": category_urls,
    }
    write_json_atomic(subset_path, payload)
    return subset_path


def write_merged_system_config(
    run_id: str, base_config: dict[str, Any], overrides: dict[str, Any]
) -> Path:
    # simple deep merge
    def merge(a: Any, b: Any) -> Any:
        if isinstance(a, dict) and isinstance(b, dict):
            out = dict(a)
            for k, v in b.items():
                out[k] = merge(out.get(k), v)
            return out
        return b if b is not None else a

    merged = merge(base_config, overrides)

    run_dir = create_run_workspace(run_id)
    path = run_dir / "system_config.merged.json"
    write_json_atomic(path, merged)
    return path


def enqueue_run_job(
    run_id: str,
    request: RunRequest,
    merged_config_path: Path,
    categories_path: Path,
    sandbox_supplier: str | None = None,
) -> Path:
    if not request.runner_script or not request.runner_script.strip():
        raise ValueError("Cannot enqueue job: runner_script is empty")

    paths = get_paths()
    paths.jobs_pending.mkdir(parents=True, exist_ok=True)

    job_path = paths.jobs_pending / f"job_{run_id}.json"
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": utc_now_iso(),
        "job_type": "run_workflow",
        "supplier_domain": request.supplier_domain,
        "sandbox_supplier": sandbox_supplier or request.supplier_domain,
        "workflow_key": request.workflow_key,
        "runner_script": request.runner_script,
        "override": {
            "system_config_path": str(merged_config_path),
            "categories_path": str(categories_path),
        },
        "runtime": {
            "max_products": request.max_products,
            "max_products_per_category": request.max_products_per_category,
        },
        "notes": request.notes,
    }
    write_json_atomic(job_path, payload)
    return job_path


def load_job(job_path: Path) -> dict[str, Any]:
    return read_json(job_path)


def set_env_for_run(config_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["FBA_SYSTEM_CONFIG_PATH"] = str(config_path)
    return env
