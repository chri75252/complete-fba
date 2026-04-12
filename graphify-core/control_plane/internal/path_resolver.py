from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from control_plane import constants


@dataclass(frozen=True)
class ControlPlanePaths:
    repo_root: Path
    outputs_dir: Path
    control_plane_dir: Path

    jobs_pending: Path
    jobs_running: Path
    jobs_done: Path
    jobs_failed: Path

    status_dir: Path
    logs_dir: Path
    overrides_dir: Path
    index_dir: Path
    lock_dir: Path

    active_lock_file: Path


def find_repo_root(start: Path | None = None) -> Path:
    cursor = start or Path.cwd()
    cursor = cursor.resolve()

    for _ in range(20):
        if (cursor / constants.PROJECT_ROOT_MARKER).exists():
            return cursor
        if cursor.parent == cursor:
            break
        cursor = cursor.parent

    return (start or Path.cwd()).resolve()


def get_control_plane_paths(repo_root: Path | None = None) -> ControlPlanePaths:
    root = repo_root or find_repo_root()
    outputs_dir = root / "OUTPUTS"
    control_plane_dir = outputs_dir / constants.CONTROL_PLANE_DIRNAME

    jobs_dir = control_plane_dir / "jobs"
    jobs_pending = jobs_dir / "pending"
    jobs_running = jobs_dir / "running"
    jobs_done = jobs_dir / "done"
    jobs_failed = jobs_dir / "failed"

    status_dir = control_plane_dir / "status"
    logs_dir = control_plane_dir / "logs"
    overrides_dir = control_plane_dir / "overrides"
    index_dir = control_plane_dir / "index"
    lock_dir = control_plane_dir / "lock"

    active_lock_file = lock_dir / "active_run.lock"

    return ControlPlanePaths(
        repo_root=root,
        outputs_dir=outputs_dir,
        control_plane_dir=control_plane_dir,
        jobs_pending=jobs_pending,
        jobs_running=jobs_running,
        jobs_done=jobs_done,
        jobs_failed=jobs_failed,
        status_dir=status_dir,
        logs_dir=logs_dir,
        overrides_dir=overrides_dir,
        index_dir=index_dir,
        lock_dir=lock_dir,
        active_lock_file=active_lock_file,
    )


def ensure_control_plane_dirs(paths: ControlPlanePaths) -> None:
    for p in [
        paths.jobs_pending,
        paths.jobs_running,
        paths.jobs_done,
        paths.jobs_failed,
        paths.status_dir,
        paths.logs_dir,
        paths.overrides_dir,
        paths.index_dir,
        paths.lock_dir,
    ]:
        p.mkdir(parents=True, exist_ok=True)

    os.makedirs(paths.repo_root / "OUTPUTS" / "DIAGNOSTICS", exist_ok=True)
