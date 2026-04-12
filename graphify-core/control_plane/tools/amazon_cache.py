from __future__ import annotations

from pathlib import Path
from typing import Any

from control_plane.json_io import read_json


def get_amazon_cache_dir(repo_root: Path) -> Path:
    return repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "amazon_cache"


def read_amazon_cache_by_asin(repo_root: Path, asin: str) -> dict[str, Any] | None:
    cache_dir = get_amazon_cache_dir(repo_root)
    if not cache_dir.exists():
        return None

    asin = asin.strip()
    for p in cache_dir.glob(f"amazon_{asin}_*.json"):
        try:
            data = read_json(p)
        except Exception:
            continue
        if isinstance(data, dict):
            return {"path": str(p), "data": data}

    return None
