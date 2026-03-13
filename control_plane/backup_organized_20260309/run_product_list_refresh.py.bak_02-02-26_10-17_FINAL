from __future__ import annotations

import asyncio
import json
import os
import re
import time
from pathlib import Path
from typing import Any

from control_plane.internal.file_io import read_json, write_json_atomic
from tools.amazon_playwright_extractor import FixedAmazonExtractor


def _utc_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _sanitize_ean(ean: str | None) -> str:
    if not ean:
        return ""
    return re.sub(r"[^0-9]", "", str(ean))


def _supplier_cache_path(repo_root: Path, sandbox_supplier: str) -> Path:
    normalized = sandbox_supplier.replace(".", "-")
    return repo_root / "OUTPUTS" / "cached_products" / f"{normalized}_products_cache.json"


def _linking_map_path(repo_root: Path, sandbox_supplier: str) -> Path:
    return (
        repo_root
        / "OUTPUTS"
        / "FBA_ANALYSIS"
        / "linking_maps"
        / sandbox_supplier
        / "linking_map.json"
    )


def _amazon_cache_dir(repo_root: Path) -> Path:
    return repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "amazon_cache"


def _amazon_cache_path(repo_root: Path, asin: str, ean: str) -> Path:
    ean_safe = _sanitize_ean(ean) or "N"
    return _amazon_cache_dir(repo_root) / f"amazon_{asin}_{ean_safe}.json"


def _parse_price(text: str | None) -> float | None:
    if not text:
        return None
    cleaned = text.strip()
    cleaned = cleaned.replace("£", "").replace(",", "")
    m = re.search(r"(\d+(?:\.\d{1,2})?)", cleaned)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


def _detect_captcha(page_text: str) -> bool:
    lowered = (page_text or "").lower()
    return (
        "validatecaptcha" in lowered
        or "not a robot" in lowered
        or "enter the characters" in lowered
    )


def _write_linking_map(repo_root: Path, sandbox_supplier: str, rows: list[dict[str, Any]]) -> Path:
    path = _linking_map_path(repo_root, sandbox_supplier)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, rows)
    return path


def _write_supplier_cache(
    repo_root: Path, sandbox_supplier: str, products: list[dict[str, Any]]
) -> Path:
    path = _supplier_cache_path(repo_root, sandbox_supplier)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_atomic(path, products)
    return path


def _backup_existing(path: Path, backups_dir: Path, max_backups: int = 5) -> None:
    if not path.exists():
        return
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime(path.stat().st_mtime))
    backup_path = backups_dir / f"{path.name}.{ts}.bak"
    try:
        backup_path.write_bytes(path.read_bytes())
    except Exception:
        return

    backups = sorted(
        backups_dir.glob(f"{path.name}.*.bak"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    for extra in backups[max_backups:]:
        try:
            extra.unlink(missing_ok=True)
        except Exception:
            pass


def _ensure_playwright_page(cdp_port: int = 9222):
    from utils.browser_manager import BrowserManager

    async def _inner():
        mgr = BrowserManager.get_instance()
        await mgr.launch_browser(cdp_port=cdp_port)
        page = await mgr.get_page(reuse_existing=True)
        return page

    return _inner()


def _load_products_from_subset(
    repo_root: Path, subset_path: str
) -> tuple[str, list[dict[str, Any]]]:
    data = read_json(Path(subset_path))
    sandbox_supplier = str(data.get("sandbox_supplier") or "")
    products_raw = data.get("products")
    products: list[dict[str, Any]] = []
    if isinstance(products_raw, list):
        products = [p for p in products_raw if isinstance(p, dict)]
    return sandbox_supplier, products


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    job_env = os.environ.get("CONTROL_PLANE_JOB_PATH")
    if not job_env:
        raise RuntimeError("CONTROL_PLANE_JOB_PATH not set")

    job = read_json(Path(job_env))
    refresh = job.get("refresh") or {}

    sandbox_supplier = str(job.get("supplier_domain") or "")
    products_path = str(refresh.get("products_path") or "")
    dry_run = bool(refresh.get("dry_run"))

    if not sandbox_supplier or not products_path:
        raise RuntimeError("Invalid job payload: missing supplier_domain or products_path")

    sandbox_from_file, products = _load_products_from_subset(repo_root, products_path)
    if sandbox_from_file and sandbox_from_file != sandbox_supplier:
        sandbox_supplier = sandbox_from_file

    _write_supplier_cache(repo_root, sandbox_supplier, products)

    results: list[dict[str, Any]] = []

    # Initialize Amazon extractor for full Keepa data extraction
    extractor = FixedAmazonExtractor(chrome_debug_port=9222)

    async def run() -> None:
        page = await _ensure_playwright_page(cdp_port=9222)
        for product in products:
            try:
                title = str(product.get("title") or "")
                supplier_url = str(product.get("url") or "")
                ean = _sanitize_ean(str(product.get("ean") or ""))

                match_method = "title"
                asin: str | None = None
                price: float | None = None
                amazon_title: str | None = None

                query = ean or title
                match_method = "EAN" if ean else "title"

                if not query:
                    results.append(
                        {
                            "supplier_ean": ean,
                            "supplier_url": supplier_url,
                            "supplier_title": title,
                            "amazon_asin": None,
                            "match_method": "missing_query",
                            "confidence": 0,
                            "created_at": _utc_now_iso(),
                        }
                    )
                    continue

                extraction_result = await extractor.search_by_ean_and_extract_data(
                    ean=ean, supplier_title=title, page=page
                )

                asin = extraction_result.get("asin")
                amazon_title = extraction_result.get("title")
                price = extraction_result.get("current_price")

                if extraction_result.get("_search_method_used") == "captcha":
                    results.append(
                        {
                            "supplier_ean": ean,
                            "supplier_url": supplier_url,
                            "supplier_title": title,
                            "amazon_asin": asin,
                            "match_method": "captcha",
                            "confidence": 0,
                            "created_at": _utc_now_iso(),
                        }
                    )
                    continue

                if not asin:
                    results.append(
                        {
                            "supplier_ean": ean,
                            "supplier_url": supplier_url,
                            "supplier_title": title,
                            "amazon_asin": None,
                            "match_method": "no_results",
                            "confidence": 0,
                            "created_at": _utc_now_iso(),
                        }
                    )
                    continue

                if not dry_run:
                    out_path = _amazon_cache_path(repo_root, asin, ean)
                    backups_dir = (
                        repo_root
                        / "OUTPUTS"
                        / "CONTROL_PLANE"
                        / "overrides"
                        / str(job.get("run_id"))
                        / "amazon_cache_backups"
                    )
                    _backup_existing(out_path, backups_dir)
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    write_json_atomic(out_path, extraction_result)

                results.append(
                    {
                        "supplier_ean": ean,
                        "supplier_url": supplier_url,
                        "supplier_title": title,
                        "supplier_price": product.get("price"),
                        "amazon_asin": asin,
                        "amazon_title": amazon_title,
                        "amazon_price": price,
                        "match_method": match_method,
                        "confidence": 1 if price is not None else 0,
                        "created_at": _utc_now_iso(),
                    }
                )
            except Exception as e:
                print(f"Error processing product {product.get('title', 'Unknown')}: {e}")
                results.append(
                    {
                        "supplier_ean": ean,
                        "supplier_url": supplier_url,
                        "supplier_title": title,
                        "amazon_asin": None,
                        "match_method": "error",
                        "confidence": 0,
                        "created_at": _utc_now_iso(),
                    }
                )
                continue

    asyncio.run(run())

    _write_linking_map(repo_root, sandbox_supplier, results)

    if not dry_run:
        from tools.FBA_Financial_calculator import run_calculations

        run_calculations(sandbox_supplier)


if __name__ == "__main__":
    main()
