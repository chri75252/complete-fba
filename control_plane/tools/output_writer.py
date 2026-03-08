from __future__ import annotations

from pathlib import Path
from typing import Any


_ALLOWED_WRITE_DIRS: tuple[str, ...] = (
    "OUTPUTS/CONTROL_PLANE/reports",
    "OUTPUTS/PRODUCTS_LISTS",
    "OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging",
)


def _is_allowed_write_path(repo_root: Path, target: Path) -> bool:
    try:
        rel = target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    rel_posix = rel.as_posix()
    return any(rel_posix.startswith(prefix) for prefix in _ALLOWED_WRITE_DIRS)


def _is_allowed_code_edit(rel_posix: str) -> bool:
    protected_runners = {
        "run_custom_poundwholesale.py",
        "run_custom_clearance_king.py",
        "run_custom_dkwholesale-com.py",
        "run_custom_efghousewares-co-uk.py",
        "run_custom_angelwholesale-co-uk.py",
    }

    if rel_posix in protected_runners:
        return False

    if rel_posix.startswith("run_custom_") and rel_posix.endswith(".py"):
        return True
    if rel_posix.startswith("tools/") and rel_posix.endswith("/supplier_authentication_service.py"):
        return True
    return False


def write_output_file(
    repo_root: Path,
    rel_path: str,
    content: str,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    if not rel_path or content is None:
        return {"ok": False, "error": "missing_path_or_content"}

    target = (repo_root / rel_path).resolve()
    rel_posix = target.resolve().relative_to(repo_root.resolve()).as_posix()

    is_safe_dir = _is_allowed_write_path(repo_root, target)
    is_safe_code = _is_allowed_code_edit(rel_posix)

    if not (is_safe_dir or is_safe_code):
        return {
            "ok": False,
            "error": "write_path_not_allowed",
            "path": str(target),
            "allowed_dirs": list(_ALLOWED_WRITE_DIRS)
            + ["run_custom_*.py", "tools/*/supplier_authentication_service.py"],
        }

    if target.exists() and not overwrite:
        return {
            "ok": False,
            "error": "file_exists",
            "path": str(target),
            "message": "File already exists. Set overwrite=true to replace.",
        }

    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        target.write_text(content, encoding="utf-8")
    except Exception as e:
        return {"ok": False, "error": f"write_failed: {e}"}

    return {
        "ok": True,
        "path": str(target),
        "rel_path": rel_path,
        "size": len(content),
    }
