from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane import job_types
from control_plane.env_config import ensure_llm_env
from control_plane.internal.file_io import read_json, write_json_atomic, write_text_atomic
from control_plane.internal.path_resolver import ensure_control_plane_dirs, get_control_plane_paths
from control_plane.paths import get_paths
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
        "refresh": {
            "last_updated": None,
            "paths": {
                "products_path": None,
                "overrides_run_dir": None,
                "amazon_cache_dir": None,
                "linking_map": None,
                "processing_state": None,
            },
            "counts": {
                "input_products": 0,
                "linking_map_entries": 0,
                "amazon_cache_files": 0,
                "matched_asins": 0,
            },
            "source_supplier_domain": None,
        },
    }


def _acquire_lock(lock_file: Path, run_id: str) -> bool:
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    if lock_file.exists():
        return False
    write_text_atomic(lock_file, run_id)
    return True


def _is_cancelled(run_id: str) -> bool:
    paths = get_paths()

    return (paths.status_dir / f"{run_id}.cancelled").exists() or (
        paths.lock_dir / f"cancel_{run_id}.flag"
    ).exists()


def _release_lock(lock_file: Path) -> None:
    try:
        lock_file.unlink(missing_ok=True)
    except Exception:
        return


def _move_job(src: Path, dst_dir: Path) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if dst.exists():
        suffix = int(time.time() * 1000)
        dst = dst_dir / f"{src.stem}__dup_{suffix}{src.suffix}"
    try:
        os.replace(src, dst)
    except FileNotFoundError:
        return dst
    return dst


def _tail_file(path: Path, lines: int) -> list[str]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", errors="replace") as f:
        all_lines = f.readlines()
    return [ln.rstrip("\n\r") for ln in all_lines[-lines:]]


def _has_run_scoped_financial_report(
    financial_dir: str | None, run_started_at: float | None
) -> bool:
    if not financial_dir:
        return False

    base = Path(financial_dir)
    if not base.exists():
        return False

    if run_started_at is None:
        return any(base.rglob("*.csv"))

    try:
        for csv_path in base.rglob("*.csv"):
            if csv_path.stat().st_mtime >= run_started_at:
                return True
    except Exception:
        return False

    return False


def _read_processing_progress(
    loader: MetricsLoader, supplier_domain: str, run_started_at: float | None = None
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
            _has_run_scoped_financial_report(paths.get("financial_dir"), run_started_at)
        ),
    }

    return resolved, {"progress": progress, "artifacts": artifacts}


def _count_linking_map_entries(path):
    if not path:
        return 0
    try:
        data = read_json(Path(path))
        if isinstance(data, list | dict):
            return len(data)
        return 0
    except Exception:
        return 0


def _count_amazon_cache_files(cache_dir):
    try:
        return len(list(Path(cache_dir).glob("amazon_*.json")))
    except Exception:
        return 0


def _count_matched_asins(path):
    if not path:
        return 0
    try:
        data = read_json(Path(path))
        rows = data if isinstance(data, list) else list(data.values())
        return sum(1 for r in rows if isinstance(r, dict) and r.get("amazon_asin"))
    except Exception:
        return 0


def _recompute_refresh_counts(status, job, paths, resolved, loader):
    """Recompute refresh.counts from authoritative sources at terminal status."""
    import time as time_module

    refresh = job.get("refresh", {})
    run_id = str(job.get("run_id", ""))
    overrides_dir = paths.repo_root / "OUTPUTS" / "CONTROL_PLANE" / "overrides" / run_id
    amazon_cache_dir = overrides_dir / "amazon_cache"

    status["refresh"]["last_updated"] = time_module.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time_module.gmtime()
    )
    status["refresh"]["paths"] = {
        "products_path": str(refresh.get("products_path", "")),
        "overrides_run_dir": str(overrides_dir),
        "amazon_cache_dir": str(amazon_cache_dir),
        "linking_map": resolved.get("linking_map"),
        "processing_state": resolved.get("processing_state"),
    }

    # Recompute input_products correctly (handle object-shaped JSON)
    products_path = refresh.get("products_path")
    input_products = 0
    if products_path:
        try:
            data = read_json(Path(products_path))
            if isinstance(data, dict) and "products" in data:
                input_products = len(data["products"])
            elif isinstance(data, list):
                input_products = len(data)
        except Exception:
            input_products = 0

    status["refresh"]["counts"] = {
        "input_products": input_products,
        "linking_map_entries": _count_linking_map_entries(resolved.get("linking_map")),
        "amazon_cache_files": _count_amazon_cache_files(amazon_cache_dir),
        "matched_asins": _count_matched_asins(resolved.get("linking_map")),
    }


class ControlPlaneWorker:
    def __init__(self, repo_root: Path | None = None, config: WorkerConfig | None = None):
        self.repo_root = repo_root
        self.config = config or WorkerConfig()

    def run_forever(self) -> None:
        ensure_llm_env()
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

            try:
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

                    # SAFETY CHECK
                    if not runner_script or not (paths.repo_root / runner_script).exists():
                        status["state"] = "failed"
                        status["error"]["summary"] = f"Runner script missing: {runner_script}"
                        write_json_atomic(status_path, status)
                        _move_job(running_job_path, paths.jobs_failed)
                        continue

                    sys_cfg_path = (job.get("override") or {}).get("system_config_path")
                    if sys_cfg_path:
                        env["FBA_SYSTEM_CONFIG_PATH"] = str(sys_cfg_path)
                    cmd = ["python", runner_script]
                elif job.get("job_type") == job_types.JOB_TYPE_RUN_PRODUCT_LIST_REFRESH:
                    refresh = job.get("refresh") or {}
                    env["CONTROL_PLANE_JOB_PATH"] = str(running_job_path)
                    cmd = ["python", "-m", "control_plane.run_product_list_refresh"]
                    timeout_seconds = int(refresh.get("timeout_seconds") or 7200)
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
                    continue

                write_json_atomic(status_path, status)

                with open(log_path, "w", encoding="utf-8") as log_file:
                    env["CONTROL_PLANE_LOG_PATH"] = str(log_path)
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
                        continue

                    status["pid"] = proc.pid
                    write_json_atomic(status_path, status)

                    last_status_refresh = 0.0
                    start_ts = time.time()
                    try:
                        while True:
                            ret = proc.poll()
                            now = time.time()

                            if _is_cancelled(run_id):
                                proc.terminate()
                                status["state"] = "cancelled"
                                status["ended_at"] = time.strftime(
                                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
                                )
                                status["error"]["summary"] = "Run cancelled"
                                status["error"]["last_log_lines"] = _tail_file(log_path, 200)
                                write_json_atomic(status_path, status)
                                _move_job(running_job_path, paths.jobs_failed)
                                break

                            if now - last_status_refresh >= self.config.status_refresh_seconds:
                                poll_supplier = job.get("sandbox_supplier", supplier_domain)
                                resolved, snap = _read_processing_progress(
                                    loader,
                                    poll_supplier,
                                    run_started_at=start_ts,
                                )
                                status["resolved_paths"] = {
                                    **resolved,
                                    "runner_log": str(log_path),
                                }
                                status["progress"] = snap.get("progress", {})
                                status["artifacts"] = snap.get("artifacts", {})
                                status["error"]["last_log_lines"] = _tail_file(log_path, 50)
                                write_json_atomic(status_path, status)

                                # E9: Detect refresh jobs and populate status["refresh"]
                                if (
                                    job.get("job_type")
                                    == job_types.JOB_TYPE_RUN_PRODUCT_LIST_REFRESH
                                ):
                                    import time as time_module

                                    refresh = job.get("refresh", {})
                                    overrides_dir = (
                                        paths.repo_root
                                        / "OUTPUTS"
                                        / "CONTROL_PLANE"
                                        / "overrides"
                                        / run_id
                                    )
                                    amazon_cache_dir = overrides_dir / "amazon_cache"
                                    status["refresh"]["last_updated"] = time_module.strftime(
                                        "%Y-%m-%dT%H:%M:%SZ", time_module.gmtime()
                                    )
                                    status["refresh"]["paths"] = {
                                        "products_path": str(refresh.get("products_path", "")),
                                        "overrides_run_dir": str(overrides_dir),
                                        "amazon_cache_dir": str(amazon_cache_dir),
                                        "linking_map": resolved.get("linking_map"),
                                        "processing_state": resolved.get("processing_state"),
                                    }
                                    products_path = refresh.get("products_path")
                                    input_products = 0
                                    if products_path:
                                        try:
                                            data = read_json(Path(products_path))
                                            if isinstance(data, dict) and "products" in data:
                                                input_products = len(data["products"])
                                            elif isinstance(data, list):
                                                input_products = len(data)
                                        except Exception:
                                            input_products = 0
                                    status["refresh"]["counts"] = {
                                        "input_products": input_products,
                                        "linking_map_entries": _count_linking_map_entries(
                                            resolved.get("linking_map")
                                        ),
                                        "amazon_cache_files": _count_amazon_cache_files(
                                            amazon_cache_dir
                                        ),
                                        "matched_asins": _count_matched_asins(
                                            resolved.get("linking_map")
                                        ),
                                    }
                                    status["refresh"]["source_supplier_domain"] = job.get(
                                        "source_supplier_domain"
                                    )

                                last_status_refresh = now

                            if ret is not None:
                                break

                            if timeout_seconds is not None and now - start_ts > timeout_seconds:
                                proc.terminate()
                                break

                            time.sleep(0.5)

                    finally:
                        try:
                            proc.wait(timeout=30)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            proc.wait(timeout=10)

                if status.get("state") != "cancelled":
                    status["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    status["error"]["last_log_lines"] = _tail_file(log_path, 200)

                    # Recompute refresh counts from disk before final status write (Issue #7 fix)
                    if job.get("job_type") == job_types.JOB_TYPE_RUN_PRODUCT_LIST_REFRESH:
                        poll_supplier = job.get("sandbox_supplier", supplier_domain)
                        resolved, _ = _read_processing_progress(
                            loader,
                            poll_supplier,
                            run_started_at=start_ts,
                        )
                        _recompute_refresh_counts(status, job, paths, resolved, loader)

                    if proc.returncode == 0:
                        # Check log tail for tracebacks that escaped without causing a non-zero exit
                        log_tail_text = "\n".join(status["error"]["last_log_lines"])
                        has_traceback = "Traceback (most recent call last):" in log_tail_text
                        has_index_error = "IndexError" in log_tail_text

                        # Known non-fatal artifacts to ignore if they appear alone
                        shutdown_artifacts = [
                            "Exception ignored in: <function BaseSubprocessTransport.__del__",
                            "RuntimeError: Event loop is closed",
                            "asyncio.base_subprocess",
                        ]

                        is_fatal_traceback = False
                        if has_traceback:
                            is_fatal_traceback = True
                            # If it's *only* a known shutdown artifact, we don't fail the run
                            if (
                                any(artifact in log_tail_text for artifact in shutdown_artifacts)
                                and not has_index_error
                                and "Exception in callback"
                                not in log_tail_text.split("Traceback")[0]
                            ):
                                is_fatal_traceback = False

                        if is_fatal_traceback:
                            status["state"] = "failed"
                            status["error"]["summary"] = (
                                "Process exited 0 but log contains fatal Traceback"
                            )
                            write_json_atomic(status_path, status)
                            _move_job(running_job_path, paths.jobs_failed)
                        else:
                            status["state"] = "done"
                            write_json_atomic(status_path, status)
                            _move_job(running_job_path, paths.jobs_done)
                    else:
                        status["state"] = "failed"
                        status["error"]["summary"] = f"Process exited with code {proc.returncode}"
                        write_json_atomic(status_path, status)
                        _move_job(running_job_path, paths.jobs_failed)
            finally:
                _release_lock(paths.active_lock_file)

            try:
                (get_paths().status_dir / f"{run_id}.cancelled").unlink(missing_ok=True)
                (get_paths().lock_dir / f"cancel_{run_id}.flag").unlink(missing_ok=True)
            except Exception:
                pass

            time.sleep(self.config.poll_seconds)


def main() -> None:
    ensure_llm_env()
    ControlPlaneWorker().run_forever()


if __name__ == "__main__":
    main()
