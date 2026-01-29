from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane import job_types
from control_plane.internal.file_io import read_json, write_json_atomic, write_text_atomic
from control_plane.internal.path_resolver import ensure_control_plane_dirs, get_control_plane_paths
from dashboard.metrics_core import MetricsLoader


@dataclass(frozen=True)
class WorkerConfig:
    poll_seconds: int = 1
    status_refresh_seconds: int = 2


def _status_template(run_id: str, supplier_domain: str) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "state": "queued",
        "supplier_domain": supplier_domain,
        "started_at": None,
        "ended_at": None,
        "pid": None,
        "resolved_paths": {},
        "progress": {},
        "artifacts": {},
        "error": {"summary": "", "last_log_lines": []},
    }


def _acquire_lock(lock_file: Path, run_id: str) -> bool:
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    if lock_file.exists():
        return False
    write_text_atomic(lock_file, run_id)
    return True


def _release_lock(lock_file: Path) -> None:
    try:
        lock_file.unlink(missing_ok=True)
    except Exception:
        return


def _move_job(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    os.replace(src, dst)
    return dst


def _tail_file(path: Path, lines: int) -> list[str]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()
    return [ln.rstrip("\n\r") for ln in all_lines[-lines:]]


def _read_processing_progress(
    loader: MetricsLoader, supplier_domain: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    paths = loader.resolve_paths(supplier_domain)

    resolved = {
        "processing_state": paths.get("state_file"),
        "linking_map": paths.get("linking_file"),
        "financial_dir": paths.get("financial_dir"),
        "logs_dir": paths.get("logs_dir"),
    }

    progress: dict[str, Any] = {}

    state_file = paths.get("state_file")
    if state_file and os.path.exists(state_file):
        try:
            state = read_json(Path(state_file))
            sp = state.get("system_progression") or {}
            progress = {
                "current_phase": sp.get("current_phase"),
                "persistent_category_index": sp.get("persistent_category_index"),
                "total_categories": sp.get("total_categories"),
                "current_category_url": sp.get("current_category_url"),
            }
            cp = (state.get("supplier_extraction_progress") or {}).get("category_progress") or {}
            if cp:
                progress.update(
                    {
                        "supplier_products_completed": cp.get("supplier_products_completed"),
                        "supplier_products_needing_extraction": cp.get(
                            "supplier_products_needing_extraction"
                        ),
                        "amazon_products_completed": cp.get("amazon_products_completed"),
                        "amazon_products_needing_analysis": cp.get(
                            "amazon_products_needing_analysis"
                        ),
                    }
                )
        except Exception:
            pass

    artifacts = {
        "cached_products_exists": bool(
            paths.get("cached_products_file") and os.path.exists(paths["cached_products_file"])
        ),
        "linking_map_exists": bool(
            paths.get("linking_file") and os.path.exists(paths["linking_file"])
        ),
        "financial_report_exists": bool(
            paths.get("financial_dir") and os.path.exists(paths["financial_dir"])
        ),
    }

    return resolved, {"progress": progress, "artifacts": artifacts}


class ControlPlaneWorker:
    def __init__(self, repo_root: Path | None = None, config: WorkerConfig | None = None):
        self.repo_root = repo_root
        self.config = config or WorkerConfig()

    def run_forever(self) -> None:
        paths = get_control_plane_paths(self.repo_root)
        ensure_control_plane_dirs(paths)

        loader = MetricsLoader(str(paths.repo_root))

        while True:
            job_files = sorted(
                paths.jobs_pending.glob("job_*.json"), key=lambda p: p.stat().st_mtime
            )
            if not job_files:
                time.sleep(self.config.poll_seconds)
                continue

            job_path = job_files[0]
            try:
                job = read_json(job_path)
            except Exception:
                _move_job(job_path, paths.jobs_failed)
                continue

            run_id = str(job.get("run_id") or "")
            supplier_domain = str(job.get("supplier_domain") or "")
            if not run_id or not supplier_domain:
                _move_job(job_path, paths.jobs_failed)
                continue

            if not _acquire_lock(paths.active_lock_file, run_id):
                time.sleep(self.config.poll_seconds)
                continue

            running_job_path = _move_job(job_path, paths.jobs_running)
            status_path = paths.status_dir / f"{run_id}.json"
            log_path = paths.logs_dir / f"{run_id}.log"

            status = _status_template(run_id, supplier_domain)
            status["state"] = "running"
            status["started_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            cmd: list[str]
            env = os.environ.copy()

            timeout_seconds: int | None = None

            if job.get("job_type") == job_types.JOB_TYPE_RUN_WORKFLOW:
                runner_script = str(job.get("runner_script") or "")
                sys_cfg_path = (job.get("override") or {}).get("system_config_path")
                if sys_cfg_path:
                    env["FBA_SYSTEM_CONFIG_PATH"] = str(sys_cfg_path)
                cmd = ["python", runner_script]
            elif job.get("job_type") == job_types.JOB_TYPE_RUN_ONBOARDING_WIZARD:
                wizard = job.get("wizard") or {}
                cmd = [
                    "python",
                    "utils/supplier_onboarding_wizard.py",
                    "--input",
                    str(wizard.get("input")),
                    "--output",
                    str(wizard.get("output")),
                ]
                timeout_seconds = int(wizard.get("timeout_seconds") or 4200)
            else:
                status["state"] = "failed"
                status["error"]["summary"] = "Unknown job_type"
                write_json_atomic(status_path, status)
                _move_job(running_job_path, paths.jobs_failed)
                _release_lock(paths.active_lock_file)
                continue

            write_json_atomic(status_path, status)

            with open(log_path, "w", encoding="utf-8") as log_file:
                try:
                    proc = subprocess.Popen(
                        cmd,
                        cwd=str(paths.repo_root),
                        env=env,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        text=True,
                    )
                except Exception as e:
                    status["state"] = "failed"
                    status["error"]["summary"] = f"Failed to start process: {e}"
                    write_json_atomic(status_path, status)
                    _move_job(running_job_path, paths.jobs_failed)
                    _release_lock(paths.active_lock_file)
                    continue

                status["pid"] = proc.pid
                write_json_atomic(status_path, status)

                last_status_refresh = 0.0
                start_ts = time.time()
                try:
                    while True:
                        ret = proc.poll()
                        now = time.time()
                        if now - last_status_refresh >= self.config.status_refresh_seconds:
                            resolved, snap = _read_processing_progress(loader, supplier_domain)
                            status["resolved_paths"] = {
                                **resolved,
                                "runner_log": str(log_path),
                            }
                            status["progress"] = snap.get("progress", {})
                            status["artifacts"] = snap.get("artifacts", {})
                            status["error"]["last_log_lines"] = _tail_file(log_path, 50)
                            write_json_atomic(status_path, status)
                            last_status_refresh = now

                        if ret is not None:
                            break

                        if timeout_seconds is not None and now - start_ts > timeout_seconds:
                            proc.terminate()
                            break

                        time.sleep(0.5)

                finally:
                    proc.wait(timeout=30)

            status["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            status["error"]["last_log_lines"] = _tail_file(log_path, 200)

            if proc.returncode == 0:
                status["state"] = "done"
                write_json_atomic(status_path, status)
                _move_job(running_job_path, paths.jobs_done)
            else:
                status["state"] = "failed"
                status["error"]["summary"] = f"Process exited with code {proc.returncode}"
                write_json_atomic(status_path, status)
                _move_job(running_job_path, paths.jobs_failed)

            _release_lock(paths.active_lock_file)

            time.sleep(self.config.poll_seconds)


def main() -> None:
    ControlPlaneWorker().run_forever()


if __name__ == "__main__":
    main()
