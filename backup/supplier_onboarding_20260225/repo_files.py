from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.internal.file_io import read_json
from control_plane.rd2_policy import is_blocked_path, redact_secrets


DEFAULT_MAX_BYTES = 1_000_000

_ALLOWED_READ_DIR_PREFIXES: tuple[str, ...] = (
    "OUTPUTS/CONTROL_PLANE/reports/",
    "OUTPUTS/CONTROL_PLANE/overrides/",
    "OUTPUTS/FBA_ANALYSIS/amazon_cache/",
    "OUTPUTS/cached_products/",
    "OUTPUTS/PRODUCTS_LISTS/",
    "tools/",
    "utils/",
    "control_plane/",
    "OUTPUTS/CONTROL_PLANE/status/",
    "OUTPUTS/CONTROL_PLANE/logs/",
    "OUTPUTS/CONTROL_PLANE/jobs/",
    "OUTPUTS/CONTROL_PLANE/diagnostics/",
    "OUTPUTS/CONTROL_PLANE/index/",
    "OUTPUTS/CACHE/processing_states/",
    "OUTPUTS/FBA_ANALYSIS/linking_maps/",
    "OUTPUTS/FBA_ANALYSIS/financial_reports/",
    "logs/",
)


_ALLOWED_LIST_DIRS: tuple[str, ...] = (
    "config",
    "config/supplier_configs",
    "OUTPUTS/CONTROL_PLANE",
    "OUTPUTS/CONTROL_PLANE/reports",
    "OUTPUTS/CONTROL_PLANE/overrides",
    "OUTPUTS/CONTROL_PLANE/status",
    "OUTPUTS/CONTROL_PLANE/logs",
    "OUTPUTS/CONTROL_PLANE/jobs",
    "OUTPUTS/CONTROL_PLANE/diagnostics",
    "OUTPUTS/CONTROL_PLANE/index",
    "OUTPUTS/CACHE/processing_states",
    "OUTPUTS/FBA_ANALYSIS/amazon_cache",
    "OUTPUTS/FBA_ANALYSIS/linking_maps",
    "OUTPUTS/FBA_ANALYSIS/financial_reports",
    "OUTPUTS/cached_products",
    "OUTPUTS/PRODUCTS_LISTS",
    "tools",
    "utils",
    "control_plane",
    "logs",
)


_ALLOWED_READ_DIR_PREFIXES_LOWER = tuple(p.lower() for p in _ALLOWED_READ_DIR_PREFIXES)
_ALLOWED_LIST_DIRS_LOWER = tuple(d.lower() for d in _ALLOWED_LIST_DIRS)


def _rel_posix_in_repo(repo_root: Path, p: Path) -> str | None:
    try:
        rel = p.relative_to(repo_root)
    except Exception:
        return None
    return rel.as_posix().lstrip("/")


def _is_allowed_config_json(rel_posix: str) -> bool:
    rp = (rel_posix or "").replace("\\", "/").lstrip("/")
    rpl = rp.lower()

    if rpl == "config/system_config.json":
        return True
    if rpl.startswith("config/supplier_configs/") and rpl.endswith(".json"):
        return True
    if rpl.startswith("config/") and rpl.endswith(".json"):
        base = rpl.rsplit("/", 1)[-1]
        if base.endswith("_categories.json") or base.endswith("_workflow_categories.json"):
            return True
        if base.endswith("_system_config_additions.json"):
            return True
        if base.startswith("test_"):
            return True
    if rpl.startswith("run_custom_") and rpl.endswith(".py"):
        return True
    return False


def _is_allowed_read_path(rel_posix: str) -> bool:
    rp = (rel_posix or "").replace("\\", "/").lstrip("/")
    rpl = rp.lower()

    if not rpl:
        return False

    if _is_allowed_config_json(rpl):
        return True

    rel_slash = rpl if rpl.endswith("/") else rpl + "/"
    return any(rel_slash.startswith(prefix) for prefix in _ALLOWED_READ_DIR_PREFIXES_LOWER)


def _is_allowed_list_dir(rel_posix_dir: str) -> bool:
    rp = (rel_posix_dir or "").replace("\\", "/").lstrip("/")
    rpl = rp.lower().rstrip("/")

    if not rpl:
        return False
    if rpl in _ALLOWED_LIST_DIRS_LOWER:
        return True
    rel_slash = rpl + "/"
    return any(d.startswith(rel_slash) for d in _ALLOWED_LIST_DIRS_LOWER)


def _not_allowed_error(*, tool: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": "path_not_allowed",
        "tool": tool,
        "allowed": [
            "OUTPUTS/CONTROL_PLANE/{status,logs,jobs,diagnostics,index}/...",
            "OUTPUTS/CACHE/processing_states/...",
            "OUTPUTS/FBA_ANALYSIS/{linking_maps,financial_reports}/...",
            "logs/...",
            "config/system_config.json",
            "config/*_categories.json",
            "config/*_workflow_categories.json",
            "config/*_system_config_additions.json",
            "config/test_*.json",
            "config/supplier_configs/*.json",
        ],
    }


def read_repo_file(
    repo_root: Path, rel_path: str, *, max_bytes: int = DEFAULT_MAX_BYTES
) -> dict[str, Any]:
    p = (repo_root / rel_path).resolve()
    repo_root = repo_root.resolve()

    rel_posix = _rel_posix_in_repo(repo_root, p)
    if rel_posix is None:
        return {"ok": False, "error": "path_outside_repo"}

    if is_blocked_path(p):
        return {"ok": False, "error": "blocked_path"}

    if not _is_allowed_read_path(rel_posix):
        return _not_allowed_error(tool="read_repo_file")

    if not p.exists() or not p.is_file():
        return {"ok": False, "error": "not_found"}

    size = p.stat().st_size
    if max_bytes > 0 and size > max_bytes:
        return {"ok": False, "error": "too_large", "size": size, "max_bytes": max_bytes}

    try:
        text = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {"ok": False, "error": "read_failed"}

    return {"ok": True, "path": str(p), "content": redact_secrets(text)}


def list_repo_dir(repo_root: Path, rel_dir: str) -> dict[str, Any]:
    d = (repo_root / rel_dir).resolve()
    repo_root = repo_root.resolve()

    rel_posix = _rel_posix_in_repo(repo_root, d)
    if rel_posix is None:
        return {"ok": False, "error": "path_outside_repo"}

    if is_blocked_path(d):
        return {"ok": False, "error": "blocked_path"}

    if not _is_allowed_list_dir(rel_posix):
        return _not_allowed_error(tool="list_repo_dir")

    if not d.exists() or not d.is_dir():
        return {"ok": False, "error": "not_found"}

    items: list[dict[str, Any]] = []
    for p in sorted(d.iterdir(), key=lambda x: x.name.lower()):
        if is_blocked_path(p):
            continue

        child_rel_posix = _rel_posix_in_repo(repo_root, p)
        if child_rel_posix is None:
            continue
        if p.is_dir():
            if not _is_allowed_list_dir(child_rel_posix):
                continue
        else:
            if not _is_allowed_read_path(child_rel_posix):
                continue
        items.append(
            {
                "name": p.name,
                "type": "dir" if p.is_dir() else "file",
                "size": int(p.stat().st_size) if p.is_file() else None,
            }
        )

    return {"ok": True, "path": str(d), "items": items}


@dataclass(frozen=True)
class OnboardingWizardRequest:
    input_path: str
    output_path: str
    timeout_seconds: int = 4200


def enqueue_onboarding_job(
    repo_root: Path, run_id: str, req: OnboardingWizardRequest
) -> dict[str, Any]:
    from control_plane.json_io import write_json_atomic
    from control_plane.paths import get_paths

    paths = get_paths()
    paths.jobs_pending.mkdir(parents=True, exist_ok=True)

    job_path = paths.jobs_pending / f"job_{run_id}.json"
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "job_type": "run_onboarding_wizard",
        "supplier_domain": "",
        "wizard": {
            "input": req.input_path,
            "output": req.output_path,
            "timeout_seconds": req.timeout_seconds,
        },
    }
    write_json_atomic(job_path, payload)

    return {"ok": True, "run_id": run_id, "job_path": str(job_path)}
