from __future__ import annotations

from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.normalize import supplier_domain_to_hyphen, supplier_domain_to_underscore


def get_cached_products_path(repo_root: Path, supplier_domain: str) -> Path:
    hyphen = supplier_domain_to_hyphen(supplier_domain)
    under = supplier_domain_to_underscore(supplier_domain)

    candidates = [
        repo_root / "OUTPUTS" / "cached_products" / f"{hyphen}_products_cache.json",
        repo_root / "OUTPUTS" / "cached_products" / f"{under}_products_cache.json",
        repo_root / "OUTPUTS" / "cached_products" / f"{supplier_domain}_products_cache.json",
    ]

    for p in candidates:
        if p.exists():
            return p

    return candidates[0]


def read_cached_products(
    repo_root: Path, supplier_domain: str
) -> list[dict[str, Any]] | dict[str, Any] | None:
    path = get_cached_products_path(repo_root, supplier_domain)
    if not path.exists():
        return None
    return read_json(path)


def find_cached_products(
    repo_root: Path,
    supplier_domain: str,
    *,
    ean: str | None = None,
    url: str | None = None,
    title_contains: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    data = read_cached_products(repo_root, supplier_domain)
    if data is None:
        return {"ok": False, "error": "cached_products_not_found", "rows": []}

    rows: list[dict[str, Any]]
    if isinstance(data, list):
        rows = [r for r in data if isinstance(r, dict)]
    elif isinstance(data, dict):
        items = data.get("products")
        if isinstance(items, list):
            rows = [r for r in items if isinstance(r, dict)]
        else:
            rows = []
    else:
        rows = []

    needle_title = title_contains.lower().strip() if title_contains else None

    def match(row: dict[str, Any]) -> bool:
        if ean is not None:
            if str(row.get("ean") or row.get("EAN") or "") != str(ean):
                return False
        if url is not None:
            if str(row.get("url") or row.get("URL") or "") != str(url):
                return False
        if needle_title is not None:
            title = str(row.get("title") or row.get("Title") or "").lower()
            if needle_title not in title:
                return False
        return True

    filtered = [r for r in rows if match(r)]
    if limit > 0:
        filtered = filtered[: int(limit)]

    return {
        "ok": True,
        "count": len(filtered),
        "rows": filtered,
        "path": str(get_cached_products_path(repo_root, supplier_domain)),
    }
