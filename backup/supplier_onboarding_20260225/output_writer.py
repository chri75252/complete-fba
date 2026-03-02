from __future__ import annotations

from pathlib import Path
from typing import Any


_ALLOWED_WRITE_DIRS: tuple[str, ...] = (
    "OUTPUTS/CONTROL_PLANE/reports",
    "OUTPUTS/PRODUCTS_LISTS",
)


def _is_allowed_write_path(repo_root: Path, target: Path) -> bool:
    """Check if target path is under an allowed write directory."""
    try:
        rel = target.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    rel_posix = rel.as_posix()
    return any(rel_posix.startswith(prefix) for prefix in _ALLOWED_WRITE_DIRS)


def write_output_file(
    repo_root: Path,
    rel_path: str,
    content: str,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write a file to an allowed output directory.

    Used by the chat LLM to generate reports (MD), product lists (JSON), etc.
    """
    if not rel_path or not content:
        return {"ok": False, "error": "missing_path_or_content"}

    target = (repo_root / rel_path).resolve()

    if not _is_allowed_write_path(repo_root, target):
        return {
            "ok": False,
            "error": "write_path_not_allowed",
            "path": str(target),
            "allowed_dirs": list(_ALLOWED_WRITE_DIRS),
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
