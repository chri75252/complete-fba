from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_plane.json_io import write_json_atomic
from control_plane.paths import get_paths


@dataclass(frozen=True)
class ProductListRefreshRequest:
    supplier_domain: str
    products: list[dict[str, Any]] | None = None
    products_path: str | None = None
    run_id: str | None = None
    notes: str | None = None
    dry_run: bool = False


def _normalize_products_payload(products: object) -> list[dict[str, Any]]:
    if products is None:
        return []
    if not isinstance(products, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in products:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def enqueue_product_list_refresh(
    repo_root: Path, request: ProductListRefreshRequest
) -> dict[str, Any]:
    run_id = (request.run_id or "").strip() or str(uuid.uuid4())

    supplier_domain = (request.supplier_domain or "").strip()
    if not supplier_domain:
        return {"ok": False, "error": "missing_supplier_domain"}

    sandbox_supplier = f"{supplier_domain}__sandbox__{run_id[:8]}"

    paths = get_paths()
    run_dir = paths.overrides_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    products_in: list[dict[str, Any]] = []
    products_path: str | None = request.products_path

    if request.products is not None:
        products_in = _normalize_products_payload(request.products)
        products_subset_path = run_dir / "products_subset.json"
        write_json_atomic(
            products_subset_path,
            {
                "schema_version": "1.0",
                "supplier_domain": supplier_domain,
                "sandbox_supplier": sandbox_supplier,
                "products": products_in,
                "notes": request.notes,
            },
        )
        products_path = str(products_subset_path)

    if not products_path:
        return {"ok": False, "error": "missing_products_or_products_path"}

    # Validate products_path exists before creating job
    if not Path(products_path).exists():
        return {
            "ok": False,
            "error": "products_path_not_found",
            "products_path": products_path,
            "message": f"Products file not found: {products_path}",
        }

    job_path = paths.jobs_pending / f"job_{run_id}.json"
    payload = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": None,
        "job_type": "run_product_list_refresh",
        "supplier_domain": sandbox_supplier,
        "source_supplier_domain": supplier_domain,
        "refresh": {
            "products_path": products_path,
            "notes": request.notes,
            "dry_run": bool(request.dry_run),
        },
    }

    if bool(request.dry_run):
        return {
            "ok": True,
            "dry_run": True,
            "run_id": run_id,
            "sandbox_supplier": sandbox_supplier,
            "job_path": str(job_path),
            "refresh": payload["refresh"],
        }

    paths.jobs_pending.mkdir(parents=True, exist_ok=True)
    write_json_atomic(job_path, payload)

    return {
        "ok": True,
        "run_id": run_id,
        "sandbox_supplier": sandbox_supplier,
        "job_path": str(job_path),
        "refresh": payload["refresh"],
    }
