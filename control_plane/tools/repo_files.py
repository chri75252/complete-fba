from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.internal.file_io import read_json
from control_plane.rd2_policy import is_blocked_path, redact_secrets


DEFAULT_MAX_BYTES = 200_000


def read_repo_file(
    repo_root: Path, rel_path: str, *, max_bytes: int = DEFAULT_MAX_BYTES
) -> dict[str, Any]:
    p = (repo_root / rel_path).resolve()
    repo_root = repo_root.resolve()

    try:
        p.relative_to(repo_root)
    except Exception:
        return {"ok": False, "error": "path_outside_repo"}

    if is_blocked_path(p):
        return {"ok": False, "error": "blocked_path"}

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

    try:
        d.relative_to(repo_root)
    except Exception:
        return {"ok": False, "error": "path_outside_repo"}

    if is_blocked_path(d):
        return {"ok": False, "error": "blocked_path"}

    if not d.exists() or not d.is_dir():
        return {"ok": False, "error": "not_found"}

    items: list[dict[str, Any]] = []
    for p in sorted(d.iterdir(), key=lambda x: x.name.lower()):
        if is_blocked_path(p):
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
