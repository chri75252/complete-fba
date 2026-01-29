from __future__ import annotations

from pathlib import Path
from typing import Any

from control_plane.json_io import read_json
from control_plane.normalize import supplier_domain_to_underscore


def get_linking_map_path(repo_root: Path, supplier_domain: str) -> Path:
    dotted = supplier_domain
    underscored = supplier_domain_to_underscore(supplier_domain)

    candidate1 = (
        repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / dotted / "linking_map.json"
    )
    if candidate1.exists():
        return candidate1

    candidate2 = (
        repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / underscored / "linking_map.json"
    )
    return candidate2


def read_linking_map(repo_root: Path, supplier_domain: str) -> dict[str, Any] | list[Any] | None:
    path = get_linking_map_path(repo_root, supplier_domain)
    if not path.exists():
        return None
    return read_json(path)


def find_linking_entries(
    repo_root: Path,
    supplier_domain: str,
    *,
    supplier_ean: str | None = None,
    amazon_asin: str | None = None,
    supplier_url: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    data = read_linking_map(repo_root, supplier_domain)
    if data is None:
        return {"ok": False, "error": "linking_map_not_found", "rows": []}

    rows: list[dict[str, Any]]
    if isinstance(data, dict):
        rows = list(data.values())
    elif isinstance(data, list):
        rows = [r for r in data if isinstance(r, dict)]
    else:
        return {"ok": False, "error": "unexpected_linking_map_schema", "rows": []}

    def match(row: dict[str, Any]) -> bool:
        if supplier_ean is not None:
            if str(row.get("supplier_ean") or "") != str(supplier_ean):
                return False
        if amazon_asin is not None:
            if str(row.get("amazon_asin") or "") != str(amazon_asin):
                return False
        if supplier_url is not None:
            if str(row.get("supplier_url") or "") != str(supplier_url):
                return False
        return True

    filtered = [r for r in rows if match(r)]
    if limit > 0:
        filtered = filtered[: int(limit)]

    return {
        "ok": True,
        "count": len(filtered),
        "rows": filtered,
        "path": str(get_linking_map_path(repo_root, supplier_domain)),
    }
