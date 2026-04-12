from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from random import Random
from typing import Any

from control_plane.tools.cached_products import get_cached_products_path, read_cached_products
from control_plane.tools.output_writer import write_output_file


@dataclass(frozen=True)
class ProductListBuildRequest:
    supplier_domain: str
    output_path: str | None = None
    sample_size: int = 8
    category_count: int = 3
    overwrite: bool = False
    selection_mode: str = "random_categories"
    require_ean: bool = False


def default_product_list_rel_path(supplier_domain: str, *, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("%d%m%y")
    return f"OUTPUTS/PRODUCTS_LISTS/product_list_{supplier_domain}_{stamp}.json"


def normalize_product_list_rel_path(
    output_path: str | None, supplier_domain: str, *, now: datetime | None = None
) -> str:
    if not output_path or not str(output_path).strip():
        return default_product_list_rel_path(supplier_domain, now=now)

    norm = str(output_path).strip().replace("\\", "/")
    pure = PurePosixPath(norm)

    if pure.is_absolute() or Path(norm).is_absolute() or ":/" in norm:
        raise ValueError("output_path must be a relative repo path")

    if norm == ".." or norm.startswith("../") or "/../" in f"/{norm}":
        raise ValueError("output_path must stay within OUTPUTS/PRODUCTS_LISTS")

    if "/" not in norm:
        norm = f"OUTPUTS/PRODUCTS_LISTS/{norm}"

    if not norm.startswith("OUTPUTS/PRODUCTS_LISTS/"):
        raise ValueError("output_path must be under OUTPUTS/PRODUCTS_LISTS")

    return norm


def _extract_rows(data: object) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]

    if isinstance(data, dict):
        products = data.get("products")
        if isinstance(products, list):
            return [row for row in products if isinstance(row, dict)]

    return []


def _canonicalize_row(row: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    title = row.get("title") or row.get("Title")
    price = row.get("price") if "price" in row else row.get("Price")
    url = row.get("url") or row.get("URL")
    normalized_url = row.get("normalized_url") or row.get("normalizedURL") or url
    ean = row.get("ean") if "ean" in row else row.get("EAN")
    availability = row.get("availability") or row.get("Availability")
    source_url = row.get("source_url") or row.get("Source URL") or row.get("category_url")
    scraped_at = row.get("scraped_at") or row.get("Scraped At")

    missing: list[str] = []
    if not str(title or "").strip():
        missing.append("title")
    if price is None or str(price).strip() == "":
        missing.append("price")
    if not str(url or "").strip():
        missing.append("url")
    if not str(source_url or "").strip():
        missing.append("source_url")

    if missing:
        return None, missing

    return {
        "title": title,
        "price": price,
        "url": url,
        "normalized_url": normalized_url,
        "ean": ean,
        "availability": availability,
        "source_url": source_url,
        "scraped_at": scraped_at,
    }, []


def build_product_list_from_cached(
    repo_root: Path, request: ProductListBuildRequest
) -> dict[str, Any]:
    supplier_domain = str(request.supplier_domain or "").strip()
    if not supplier_domain:
        return {"ok": False, "error": "missing_supplier_domain"}

    if request.selection_mode != "random_categories":
        return {
            "ok": False,
            "error": "unsupported_selection_mode",
            "message": "Only selection_mode='random_categories' is currently supported.",
        }

    if request.sample_size <= 0:
        return {"ok": False, "error": "invalid_sample_size", "message": "sample_size must be > 0"}

    if request.category_count <= 0:
        return {
            "ok": False,
            "error": "invalid_category_count",
            "message": "category_count must be > 0",
        }

    if request.sample_size < request.category_count:
        return {
            "ok": False,
            "error": "invalid_sample_shape",
            "message": "sample_size must be >= category_count",
        }

    cache_path = get_cached_products_path(repo_root, supplier_domain)
    if not cache_path.exists():
        return {
            "ok": False,
            "error": "cached_products_not_found",
            "path": str(cache_path),
        }

    raw_data = read_cached_products(repo_root, supplier_domain)
    rows = _extract_rows(raw_data)
    if not rows:
        return {
            "ok": False,
            "error": "cached_products_empty",
            "path": str(cache_path),
        }

    normalized_rows: list[dict[str, Any]] = []
    invalid_rows = 0
    invalid_example: dict[str, Any] | None = None
    for row in rows:
        normalized, missing = _canonicalize_row(row)
        if normalized is None:
            invalid_rows += 1
            if invalid_example is None:
                invalid_example = {
                    "missing_fields": missing,
                    "sample": {
                        key: row.get(key)
                        for key in list(row.keys())[:8]
                        if isinstance(key, str)
                    },
                }
            continue
        if request.require_ean and not str(normalized.get("ean") or "").strip():
            invalid_rows += 1
            continue
        normalized_rows.append(normalized)

    if not normalized_rows:
        return {
            "ok": False,
            "error": "cached_products_schema_invalid",
            "path": str(cache_path),
            "invalid_rows": invalid_rows,
            "example": invalid_example,
        }

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in normalized_rows:
        source_url = str(row.get("source_url") or "").strip()
        grouped.setdefault(source_url, []).append(row)

    category_urls = sorted([url for url, items in grouped.items() if items])
    if not category_urls:
        return {
            "ok": False,
            "error": "cached_products_empty",
            "message": "No valid categories found in cache after normalization.",
            "path": str(cache_path),
        }

    actual_category_count = min(request.category_count, len(category_urls))
    rng = Random()
    selected_categories = rng.sample(category_urls, actual_category_count)

    chosen: list[dict[str, Any]] = []
    remaining_pool: list[dict[str, Any]] = []
    for category_url in selected_categories:
        pool = list(grouped[category_url])
        rng.shuffle(pool)
        chosen.append(pool.pop())
        remaining_pool.extend(pool)

    needed = request.sample_size - len(chosen)
    if needed > len(remaining_pool):
        return {
            "ok": False,
            "error": "insufficient_products",
            "available_products": len(chosen) + len(remaining_pool),
            "requested_products": request.sample_size,
            "selected_categories": selected_categories,
            "path": str(cache_path),
        }

    if needed > 0:
        chosen.extend(rng.sample(remaining_pool, needed))

    rng.shuffle(chosen)

    try:
        rel_path = normalize_product_list_rel_path(request.output_path, supplier_domain)
    except ValueError as exc:
        return {"ok": False, "error": "invalid_output_path", "message": str(exc)}

    payload = {
        "supplier_domain": supplier_domain,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace(
            "+00:00", "Z"
        ),
        "source_cached_file": str(cache_path.relative_to(repo_root)).replace("\\", "/"),
        "selection": {
            "mode": request.selection_mode,
            "sample_size": request.sample_size,
            "category_count": actual_category_count,
            "requested_category_count": request.category_count,
            "selected_categories": selected_categories,
        },
        "products": chosen,
    }

    content = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    written = write_output_file(repo_root, rel_path, content, overwrite=request.overwrite)
    if written.get("ok") is not True:
        return written

    return {
        **written,
        "supplier_domain": supplier_domain,
        "source_cached_file": payload["source_cached_file"],
        "selected_categories": selected_categories,
        "count": len(chosen),
        "invalid_rows_skipped": invalid_rows,
    }
