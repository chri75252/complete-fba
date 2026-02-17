from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


JobType = Literal["run_workflow", "run_onboarding_wizard"]
StatusState = Literal["queued", "running", "done", "failed"]


@dataclass(frozen=True)
class JobManifest:
    schema_version: str
    run_id: str
    created_at: str
    job_type: JobType
    supplier_domain: str
    runner_script: str
    workflow_key: str | None
    override: dict[str, Any]
    runtime: dict[str, Any]
    notes: str | None


@dataclass(frozen=True)
class RunStatus:
    schema_version: str
    run_id: str
    state: StatusState
    supplier_domain: str
    started_at: str | None
    ended_at: str | None
    pid: int | None
    resolved_paths: dict[str, Any]
    progress: dict[str, Any]
    artifacts: dict[str, Any]
    error: dict[str, Any]
