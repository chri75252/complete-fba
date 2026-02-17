from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from control_plane import job_types
from control_plane.config_merger import deep_merge
from control_plane.internal.file_io import read_json, write_json_atomic
from control_plane.internal.path_resolver import ensure_control_plane_dirs, get_control_plane_paths


@dataclass(frozen=True)
class JobPaths:
    run_id: str
    run_dir: Path
    merged_config_path: Path
    categories_subset_path: Path
    job_path: Path
    log_path: Path
    status_path: Path


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_job_paths(run_id: str, repo_root: Path | None = None) -> JobPaths:
    paths = get_control_plane_paths(repo_root)
    ensure_control_plane_dirs(paths)

    run_dir = paths.overrides_dir / run_id
    merged_config_path = run_dir / "system_config.merged.json"
    categories_subset_path = run_dir / "categories_subset.json"
    job_path = paths.jobs_pending / f"job_{run_id}.json"
    log_path = paths.logs_dir / f"{run_id}.log"
    status_path = paths.status_dir / f"{run_id}.json"

    run_dir.mkdir(parents=True, exist_ok=True)

    return JobPaths(
        run_id=run_id,
        run_dir=run_dir,
        merged_config_path=merged_config_path,
        categories_subset_path=categories_subset_path,
        job_path=job_path,
        log_path=log_path,
        status_path=status_path,
    )


def _update_workflow_categories_path(
    full_config: dict[str, Any], workflow_key: str, categories_path: str
) -> None:
    workflows = full_config.setdefault("workflows", {})
    workflow = workflows.setdefault(workflow_key, {})
    workflow["categories_config_path"] = categories_path


class JobManager:
    def __init__(self, repo_root: Path | None = None):
        self.repo_root = repo_root

    def create_run_workflow_job(
        self,
        *,
        supplier_domain: str,
        workflow_key: str,
        runner_script: str,
        category_urls: list[str],
        max_products: int | None = None,
        max_products_per_category: int | None = None,
    ) -> JobPaths:
        run_id = str(uuid.uuid4())
        jp = build_job_paths(run_id, self.repo_root)

        categories_payload: dict[str, Any] = {
            "schema_version": "1.0",
            "supplier_domain": supplier_domain,
            "category_urls": category_urls,
        }
        write_json_atomic(jp.categories_subset_path, categories_payload)

        base_config_path = (
            Path(self.repo_root or get_control_plane_paths().repo_root)
            / "config"
            / "system_config.json"
        )
        base_config = read_json(base_config_path)

        overrides: dict[str, Any] = {}
        system_overrides: dict[str, Any] = {}
        if max_products is not None:
            system_overrides["max_products"] = int(max_products)
        if max_products_per_category is not None:
            system_overrides["max_products_per_category"] = int(max_products_per_category)

        if system_overrides:
            overrides["system"] = system_overrides

        merged_config = deep_merge(base_config, overrides)
        _update_workflow_categories_path(
            merged_config, workflow_key, str(jp.categories_subset_path)
        )
        write_json_atomic(jp.merged_config_path, merged_config)

        job_payload: dict[str, Any] = {
            "schema_version": "1.0",
            "run_id": run_id,
            "created_at": _iso_now(),
            "job_type": job_types.JOB_TYPE_RUN_WORKFLOW,
            "supplier_domain": supplier_domain,
            "workflow_key": workflow_key,
            "runner_script": runner_script,
            "override": {
                "system_config_path": str(jp.merged_config_path),
                "categories_path": str(jp.categories_subset_path),
            },
            "runtime": {
                "max_products": max_products,
                "max_products_per_category": max_products_per_category,
            },
        }
        write_json_atomic(jp.job_path, job_payload)

        return jp

    def create_onboarding_job(
        self,
        *,
        input_session_path: str,
        output_session_path: str,
        supplier_domain: str,
        timeout_seconds: int = 4200,
    ) -> JobPaths:
        run_id = str(uuid.uuid4())
        jp = build_job_paths(run_id, self.repo_root)

        job_payload: dict[str, Any] = {
            "schema_version": "1.0",
            "run_id": run_id,
            "created_at": _iso_now(),
            "job_type": job_types.JOB_TYPE_RUN_ONBOARDING_WIZARD,
            "supplier_domain": supplier_domain,
            "wizard": {
                "input": input_session_path,
                "output": output_session_path,
                "timeout_seconds": int(timeout_seconds),
            },
        }
        write_json_atomic(jp.job_path, job_payload)
        return jp
