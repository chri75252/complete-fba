from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ControlPlanePaths:
    repo_root: Path

    @property
    def diagnostics_dir(self) -> Path:
        return self.outputs_root / "DIAGNOSTICS"

    @property
    def audit_dir(self) -> Path:
        return self.control_plane_root / "audit"

    @property
    def transcripts_dir(self) -> Path:
        return self.control_plane_root / "transcripts"

    @property
    def rag_index_path(self) -> Path:
        return self.index_dir / "rag_index.json"

    @property
    def outputs_root(self) -> Path:
        return self.repo_root / "OUTPUTS"

    @property
    def control_plane_root(self) -> Path:
        return self.outputs_root / "CONTROL_PLANE"

    @property
    def jobs_pending(self) -> Path:
        return self.control_plane_root / "jobs" / "pending"

    @property
    def jobs_running(self) -> Path:
        return self.control_plane_root / "jobs" / "running"

    @property
    def jobs_done(self) -> Path:
        return self.control_plane_root / "jobs" / "done"

    @property
    def jobs_failed(self) -> Path:
        return self.control_plane_root / "jobs" / "failed"

    @property
    def status_dir(self) -> Path:
        return self.control_plane_root / "status"

    @property
    def logs_dir(self) -> Path:
        return self.control_plane_root / "logs"

    @property
    def overrides_dir(self) -> Path:
        return self.control_plane_root / "overrides"

    @property
    def lock_dir(self) -> Path:
        return self.control_plane_root / "lock"

    @property
    def active_run_lock(self) -> Path:
        return self.lock_dir / "active_run.lock"

    @property
    def index_dir(self) -> Path:
        return self.control_plane_root / "index"

    @property
    def system_index_path(self) -> Path:
        return self.index_dir / "system_index.json"

    @property
    def prompts_dir(self) -> Path:
        return self.repo_root / "control_plane" / "prompts"

    @property
    def system_instructions_path(self) -> Path:
        return self.prompts_dir / "SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md"


def get_repo_root() -> Path:
    # control_plane/paths.py => repo root is parent
    return Path(__file__).resolve().parent.parent


def get_paths() -> ControlPlanePaths:
    return ControlPlanePaths(repo_root=get_repo_root())


def ensure_dirs() -> None:
    p = get_paths()
    for d in [
        p.jobs_pending,
        p.jobs_running,
        p.jobs_done,
        p.jobs_failed,
        p.status_dir,
        p.logs_dir,
        p.overrides_dir,
        p.index_dir,
        p.lock_dir,
        p.audit_dir,
        p.transcripts_dir,
    ]:
        d.mkdir(parents=True, exist_ok=True)
