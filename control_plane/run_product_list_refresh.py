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
from tools.configurable_supplier_scraper import ConfigurableSupplierScraper
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

import logging

log = logging.getLogger(__name__)


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


def _amazon_cache_dir(repo_root: Path, run_id: str) -> Path:
    return repo_root / "OUTPUTS" / "CONTROL_PLANE" / "overrides" / run_id / "amazon_cache"


def _amazon_cache_path(repo_root: Path, run_id: str, asin: str, ean: str) -> Path:
    ean_safe = _sanitize_ean(ean) or "N"
    return _amazon_cache_dir(repo_root, run_id) / f"amazon_{asin}_{ean_safe}.json"


def _canonical_amazon_cache_path(repo_root: Path, asin: str, ean: str) -> Path:
    ean_safe = _sanitize_ean(ean) or "N"
    return (
        repo_root
        / "OUTPUTS"
        / "FBA_ANALYSIS"
        / "amazon_cache"
        / f"amazon_{asin}_{ean_safe}.json"
    )


def _cancel_marker_path(repo_root: Path, run_id: str) -> Path:
    return repo_root / "OUTPUTS" / "CONTROL_PLANE" / "status" / f"{run_id}.cancelled"


def _legacy_cancel_marker_path(repo_root: Path, run_id: str) -> Path:
    return repo_root / "OUTPUTS" / "CONTROL_PLANE" / "locks" / f"cancel_{run_id}.flag"


def _cancel_requested(repo_root: Path, run_id: str) -> bool:
    return _cancel_marker_path(repo_root, run_id).exists() or _legacy_cancel_marker_path(
        repo_root, run_id
    ).exists()


def _normalize_sandbox_for_match(value: str) -> str:
    """Collapse dot/hyphen/underscore variants so co.uk == co-uk == co_uk."""
    return re.sub(r"[._-]+", "_", str(value or "")).lower()


def _resolve_canonical_sandbox_supplier(
    repo_root: Path, requested: str
) -> str:
    """Find an existing on-disk sandbox dir whose name matches when normalized.

    The LLM (or job creator) may hallucinate dot/hyphen variants of the
    supplier domain (e.g. "co-uk" instead of "co.uk"). This causes state
    file and linking map lookups to miss real on-disk data and start fresh.

    This helper scans the linking_maps directory for any sibling whose
    normalized form matches the requested sandbox_supplier and returns
    that on-disk name as authoritative. If no match exists, returns the
    requested name unchanged (genuine fresh run).
    """
    requested_norm = _normalize_sandbox_for_match(requested)
    if not requested_norm:
        return requested
    linking_maps_root = repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps"
    if not linking_maps_root.exists():
        return requested
    for entry in linking_maps_root.iterdir():
        if not entry.is_dir():
            continue
        if _normalize_sandbox_for_match(entry.name) == requested_norm:
            if entry.name != requested:
                log.warning(
                    "Sandbox name mismatch resolved: requested=%s, on-disk=%s",
                    requested, entry.name,
                )
            return entry.name
    return requested


def _normalize_match_method(extraction_result: dict[str, Any]) -> str:
    raw = str(extraction_result.get("_search_method_used") or "").strip().lower()
    if raw in {
        "ean",
        "ean_cached",
        "ean_verified",
        "ean_visibility",
        "ean_search_bar_with_verification",
    }:
        return "EAN"
    if raw in {"title", "title_cached", "ean_verification_failed"}:
        return "title"
    if raw == "captcha":
        return "captcha"
    return "unknown"


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


def _append_supplier_cache(
    repo_root: Path, sandbox_supplier: str, product: dict[str, Any]
) -> int:
    """FIX 2 (20260408): Append a single live-scraped product to the sandbox cache file
    with atomic dedup. Mirrors the main workflow's per-product cache write pattern
    (_save_products_to_cache / update_frequency_products=1 in system_config).

    Dedup uses _product_identity (EAN preferred, else URL, else title) so cross-category
    duplicates and restart-from-older-point scenarios do not create double entries.

    Only call this on SUCCESSFUL live-scrape paths. Failed/fallback paths (where
    the original raw product is used) are intentionally excluded so the cache only
    holds newly extracted enriched data. Failed products will be retried on the
    next resume run.

    Returns the new total entry count after the append (0 if dedup hit, no write).
    """
    if not product:
        return 0
    path = _supplier_cache_path(repo_root, sandbox_supplier)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[dict[str, Any]] = []
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                loaded = json.load(fh)
                if isinstance(loaded, list):
                    existing = loaded
        except Exception:
            existing = []
    new_key = _product_identity(product)
    if new_key:
        for ep in existing:
            if _product_identity(ep) == new_key:
                return len(existing)  # dedup hit — skip write
    existing.append(product)
    write_json_atomic(path, existing)
    return len(existing)


def _setup_debug_log(repo_root: Path, sandbox_supplier: str) -> None:
    debug_dir = repo_root / "logs" / "debug"
    debug_dir.mkdir(parents=True, exist_ok=True)
    safe = sandbox_supplier.replace(".", "-").replace("/", "-")
    ts = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    log_file = debug_dir / f"run_custom_{safe}__product_list_refresh_{ts}.log"

    root = logging.getLogger()
    if any(getattr(handler, "baseFilename", None) == str(log_file) for handler in root.handlers):
        return

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    if root.level > logging.INFO:
        root.setLevel(logging.INFO)
    root.addHandler(file_handler)


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


def _group_products_by_source(
    products_list: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for product in products_list:
        source_url = str(product.get("source_url") or product.get("category_url") or "").strip()
        key = source_url if source_url else "__unknown_source_url__"
        grouped.setdefault(key, []).append(product)
    return grouped


def _ensure_playwright_page(cdp_port: int = 9222):
    from utils.browser_manager import BrowserManager

    async def _inner():
        mgr = BrowserManager.get_instance()
        await mgr.launch_browser(cdp_port=cdp_port)
        page = await mgr.get_page(reuse_existing=True)
        # Bring the run tab to front once at startup so the user can see navigations.
        # This is NOT called on every get_page() — only here at session start.
        try:
            await page.bring_to_front()
            log.info("Brought run page to front for visibility")
        except Exception:
            pass
        return page

    return _inner()


def _load_products_from_subset(
    repo_root: Path, subset_path: str
) -> tuple[str, list[dict[str, Any]]]:
    subset = Path(subset_path)
    if not subset.is_absolute():
        subset = repo_root / subset

    if not subset.exists():
        raise RuntimeError(f"Products subset file not found: {subset}")

    try:
        data = read_json(subset)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Invalid JSON in products subset: {subset} (line {e.lineno}, column {e.colno})"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to read products subset: {subset} ({e})") from e

    if isinstance(data, list):
        products = [p for p in data if isinstance(p, dict)]
        return "", products

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Products subset must be a JSON object or array, got: {type(data).__name__}"
        )

    sandbox_supplier = str(data.get("sandbox_supplier") or data.get("supplier_domain") or "")
    products_raw = data.get("products")
    products: list[dict[str, Any]] = []
    if products_raw is None:
        return sandbox_supplier, products
    if not isinstance(products_raw, list):
        raise RuntimeError(
            f"Invalid products payload in subset file: 'products' must be a list, got {type(products_raw).__name__}"
        )
    products = [p for p in products_raw if isinstance(p, dict)]
    return sandbox_supplier, products


def _product_identity(product: dict[str, Any]) -> str:
    ean = _sanitize_ean(str(product.get("supplier_ean") or product.get("ean") or ""))
    supplier_url = str(product.get("supplier_url") or product.get("url") or "").strip().lower()
    supplier_title = (
        str(product.get("supplier_title") or product.get("title") or "").strip().lower()
    )
    if ean:
        return f"ean:{ean}"
    if supplier_url:
        return f"url:{supplier_url}"
    if supplier_title:
        return f"title:{supplier_title}"
    return ""


def _load_existing_linking_results(
    repo_root: Path,
    sandbox_supplier: str,
    allowed_keys: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Load linking map entries, filtered to only those belonging to the current product list.

    ``allowed_keys`` is the set of _product_identity() values for every product
    in the current product list.  Entries whose key is NOT in allowed_keys are
    foreign contamination (leftover from a different run or product list) and are
    excluded so they cannot inflate processed_keys or state counters.
    """
    path = _linking_map_path(repo_root, sandbox_supplier)
    if not path.exists():
        return []
    try:
        data = read_json(path)
    except Exception:
        return []
    if not isinstance(data, list):
        return []

    out: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    excluded = 0
    for row in data:
        if not isinstance(row, dict):
            continue
        key = _product_identity(row)
        if key:
            if key in seen_keys:
                continue
            # If allowed_keys supplied, skip entries not in the current product list
            if allowed_keys is not None and key not in allowed_keys:
                excluded += 1
                continue
            seen_keys.add(key)
        out.append(row)
    if excluded:
        log.info(
            "Linking map: excluded %d foreign entries not in current product list (kept %d)",
            excluded,
            len(out),
        )
    return out


def _finalize_refresh_run(
    *,
    repo_root: Path,
    sandbox_supplier: str,
    state_manager: FixedEnhancedStateManager,
    products: list[dict[str, Any]],
    results: list[dict[str, Any]],
    dry_run: bool,
    cancelled: bool,
) -> dict[str, Any]:
    _write_linking_map(repo_root, sandbox_supplier, results)

    total_products = len(products)
    successful_matches = sum(1 for r in results if r.get("amazon_asin"))
    sp = state_manager.state_data["system_progression"]
    sp["supplier_products_completed"] = min(total_products, len(results))
    sp["supplier_products_needing_extraction"] = max(
        0, total_products - sp["supplier_products_completed"]
    )
    sp["amazon_products_completed"] = len(results)
    sp["amazon_products_needing_analysis"] = max(0, total_products - len(results))
    sp["current_phase"] = "cancelled" if cancelled else "complete"
    state_manager.save_state_atomic()

    sd = state_manager.state_data
    sd["total_products"] = total_products
    sd["session_products_processed"] = sp.get("amazon_products_completed", 0)
    sd["successful_products"] = successful_matches
    sd["processing_status"] = "cancelled" if cancelled else "complete"
    sd["is_fresh_start"] = False
    sd["last_updated"] = _utc_now_iso()
    state_manager.save_state_atomic()

    if not dry_run and successful_matches > 0:
        try:
            from tools.FBA_Financial_calculator import run_calculations

            supplier_cache_path = str(_supplier_cache_path(repo_root, sandbox_supplier))
            financial_results = run_calculations(
                sandbox_supplier,
                supplier_cache_path=supplier_cache_path,
            )
            output_file = (financial_results or {}).get("statistics", {}).get("output_file")
            if output_file:
                log.info("Financial report generated: %s", output_file)
            else:
                log.warning("Financial report ran but did not return output_file")
        except Exception as e:
            log.error("Financial report generation failed: %s", e, exc_info=True)

    return {
        "cancelled": cancelled,
        "successful_matches": successful_matches,
        "total_results": len(results),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    job_env = os.environ.get("CONTROL_PLANE_JOB_PATH")
    if not job_env:
        raise RuntimeError("CONTROL_PLANE_JOB_PATH not set")

    job = read_json(Path(job_env))
    refresh = job.get("refresh") or {}

    sandbox_supplier = str(job.get("supplier_domain") or "")
    run_id = str(job.get("run_id") or "")
    products_path = str(refresh.get("products_path") or "")
    dry_run = bool(refresh.get("dry_run"))

    if not sandbox_supplier or not run_id or not products_path:
        raise RuntimeError("Invalid job payload: missing supplier_domain, run_id, or products_path")

    # FIX 5: Resolve sandbox name against on-disk truth (handles co.uk/co-uk/co_uk variants)
    sandbox_supplier = _resolve_canonical_sandbox_supplier(repo_root, sandbox_supplier)

    _setup_debug_log(repo_root, sandbox_supplier)

    sandbox_from_file, products = _load_products_from_subset(repo_root, products_path)
    if sandbox_from_file and sandbox_from_file != sandbox_supplier:
        log.warning(
            "Ignoring supplier identity from products file; job sandbox is authoritative. job=%s file=%s",
            sandbox_supplier,
            sandbox_from_file,
        )

    # Build the set of identity keys for every product in the current product list.
    # This is used to (a) filter the linking map to exclude foreign entries, and
    # (b) populate processed_keys for skip logic.
    product_keys: set[str] = set()
    for p in products:
        k = _product_identity(p)
        if k:
            product_keys.add(k)

    results: list[dict[str, Any]] = _load_existing_linking_results(
        repo_root, sandbox_supplier, allowed_keys=product_keys
    )
    processed_keys: set[str] = set()
    for row in results:
        key = _product_identity(row)
        if key:
            processed_keys.add(key)

    # FIX 3 (20260408): Build cached_keys from the existing on-disk cache file.
    # This mirrors the main workflow's STEP 2 (PRODUCT CACHE CHECK) and lets the
    # supplier refresh loop skip products that were already live-scraped in a prior
    # interrupted run — even if they never made it through Phase 2 to the linking map.
    # Together with processed_keys (from linking map) this covers ALL resume scenarios:
    #   - Mid-Phase 1 interruption: cached_keys skips already-scraped products.
    #   - Mid-Phase 2 interruption: cached_keys skips all Phase-1-complete products
    #     so re-scraping is never needed; processed_keys (line 699) skips the
    #     already-analyzed products in Phase 2.
    cached_keys: set[str] = set()
    _existing_cache_path = _supplier_cache_path(repo_root, sandbox_supplier)
    if _existing_cache_path.exists():
        try:
            with open(_existing_cache_path, "r", encoding="utf-8") as _cf:
                _existing_cache = json.load(_cf)
            if isinstance(_existing_cache, list):
                for _cp in _existing_cache:
                    if isinstance(_cp, dict):
                        _ck = _product_identity(_cp)
                        if _ck:
                            cached_keys.add(_ck)
            log.info(
                "STEP 2 startup: loaded %d cached_keys from on-disk cache (%s entries)",
                len(cached_keys), len(_existing_cache) if isinstance(_existing_cache, list) else "?",
            )
        except Exception as _ck_err:
            log.warning("FIX 3: Failed to load cached_keys from cache file: %s", _ck_err)

    # Initialize Amazon extractor for full Keepa data extraction
    extractor = FixedAmazonExtractor(chrome_debug_port=9222)

    # Scraper is initialized after browser connection inside async run() —
    # must receive browser_manager to match how main runners work.
    scraper = None  # Set inside run() after BrowserManager is connected

    # FIX 1 (20260408): Removed startup raw-input cache paste.
    # Previously: _write_supplier_cache(repo_root, sandbox_supplier, products) here
    # overwrote the cache file with the raw 1776-entry input JSON before any live
    # scraping. The cache only ever held stale pre-scrape data.
    # Now: the cache is populated per-product inside the supplier refresh loop
    # via _append_supplier_cache (Fix 2) and only contains live-scraped enriched data.

    products_by_source = _group_products_by_source(products)
    state_manager = FixedEnhancedStateManager(sandbox_supplier)
    # Load existing state from disk so resume progress is preserved
    resumed = state_manager.load_state()
    if resumed:
        log.info("Loaded existing processing state for %s — resuming", sandbox_supplier)
    else:
        log.info("No existing processing state for %s — starting fresh", sandbox_supplier)
    sp = state_manager.state_data["system_progression"]
    sp["current_phase"] = "supplier"
    sp["total_categories"] = len(products_by_source)
    sp.setdefault("persistent_category_index", 0)
    sp.setdefault("current_category_url", "")
    if not resumed:
        # Fresh start: initialise counters from filtered linking map (which may have
        # partial results from a previous interrupted run).
        sp["supplier_products_completed"] = min(len(products), len(results))
        sp["supplier_products_needing_extraction"] = max(0, len(products) - len(results))
        sp["amazon_products_completed"] = len(results)
        sp["amazon_products_needing_analysis"] = max(0, len(products) - len(results))
    else:
        # Resume: the state file already holds progress counters written by a
        # prior session.  Do NOT overwrite them — they reflect the actual
        # category-level progress cursor set at the time of interruption.
        # Only ensure the needing_extraction fields are consistent.
        sp.setdefault("supplier_products_completed", len(results))
        sp.setdefault("amazon_products_completed", len(results))
        sp["supplier_products_needing_extraction"] = max(
            0, len(products) - sp.get("supplier_products_completed", 0)
        )
        sp["amazon_products_needing_analysis"] = max(
            0, len(products) - sp.get("amazon_products_completed", 0)
        )
        log.info(
            "Resuming — state counters preserved: supplier_completed=%s amazon_completed=%s "
            "filtered_lm_entries=%d",
            sp.get("supplier_products_completed"),
            sp.get("amazon_products_completed"),
            len(results),
        )
    state_manager.enter_runtime_phase()
    state_manager.save_state_atomic()

    cancel_requested = False

    async def run() -> None:
        nonlocal cancel_requested, scraper
        await extractor.connect()  # Ensure extractor is connected before use
        page = await _ensure_playwright_page(cdp_port=9222)
        # Create scraper AFTER browser is connected, passing browser_manager
        # (matches how main runners work — prevents singleton fallback path)
        from utils.browser_manager import BrowserManager
        scraper = ConfigurableSupplierScraper(browser_manager=BrowserManager.get_instance())
        # --- Resolve Auth Service (Login executes inside the category loop) ---
        auth_svc = None
        base_supplier = sandbox_supplier.split("__sandbox__")[0]
        try:
            import importlib
            supplier_slug = base_supplier.split(".")[0].replace("-", "_")
            auth_mod = importlib.import_module(f"tools.{supplier_slug}.supplier_authentication_service")
            auth_svc = getattr(auth_mod, "SupplierAuthenticationService")(page)
        except ModuleNotFoundError:
            log.info("ℹ️ No auth service for %s; supplier may not require login", sandbox_supplier)
        except Exception as auth_err:
            log.warning("⚠️ Auth setup failed for %s: %s", sandbox_supplier, auth_err)
        # ----------------------------------------------------------------------
        linking_map_batch_size = 1
        financial_report_batch_size = 10
        try:
            from config.system_config_loader import SystemConfigLoader

            sys_cfg = SystemConfigLoader().get_system_config() or {}
            linking_map_batch_size = max(
                1,
                int(sys_cfg.get("linking_map_batch_size") or 1),
            )
            financial_report_batch_size = max(
                1,
                int(sys_cfg.get("financial_report_batch_size") or 10),
            )
        except Exception:
            linking_map_batch_size = 1
            financial_report_batch_size = 10

        results_since_flush = 0
        successful_matches_since_financial_flush = 0

        def _flush_if_needed(*, matched: bool = False) -> None:
            nonlocal results_since_flush, successful_matches_since_financial_flush
            results_since_flush += 1
            if matched:
                successful_matches_since_financial_flush += 1
            if results_since_flush >= linking_map_batch_size:
                _write_linking_map(repo_root, sandbox_supplier, results)
                log.info("Linking map periodic flush: %d entries", len(results))
                results_since_flush = 0
                sp["amazon_products_completed"] = len(results)
                sp["amazon_products_needing_analysis"] = max(0, len(products) - len(results))
                state_manager.save_state_atomic()
            if (
                not dry_run
                and successful_matches_since_financial_flush >= financial_report_batch_size
            ):
                try:
                    from tools.FBA_Financial_calculator import run_calculations

                    supplier_cache_path = str(_supplier_cache_path(repo_root, sandbox_supplier))
                    fin = run_calculations(
                        sandbox_supplier, supplier_cache_path=supplier_cache_path
                    )
                    output_file = (fin or {}).get("statistics", {}).get("output_file")
                    if output_file:
                        log.info("Mid-run financial report: %s", output_file)
                    else:
                        log.warning("Mid-run financial report ran but returned no output_file")
                except Exception as fin_err:
                    log.error("Mid-run financial report failed: %s", fin_err, exc_info=True)
                successful_matches_since_financial_flush = 0

        source_items = list(products_by_source.items())

        for category_index, (source_url, source_products) in enumerate(source_items, start=1):
            # FIX B: Skip fully-processed categories on resume.
            # If every product in this category is already in the linking map
            # (processed_keys), the entire category is done — skip it.
            cat_keys = {_product_identity(p) for p in source_products if _product_identity(p)}
            if resumed and cat_keys and cat_keys.issubset(processed_keys):
                log.info(
                    "FIX B: Skipping fully-processed category %d/%d (%d products): %s",
                    category_index, len(source_items), len(source_products), source_url,
                )
                continue
            # --- Verify Authentication per Category ---
            if auth_svc:
                try:
                    if not await auth_svc.is_authenticated(page):
                        from config.system_config_loader import SystemConfigLoader as _SCL
                        _creds = _SCL().get_credentials(base_supplier)
                        if _creds:
                            log.info("🔐 Category %d requires login; authenticating %s…", category_index, base_supplier)
                            if await auth_svc.login(_creds, page=page):
                                log.info("✅ Category %d: Authentication successful", category_index)
                            else:
                                log.warning("❌ Category %d: Authentication failed", category_index)
                        else:
                            log.warning("⚠️ Category %d: No credentials found for %s", category_index, base_supplier)
                    else:
                        log.info("✅ Category %d: Already authenticated", category_index)
                except Exception as cat_auth_err:
                    log.warning("⚠️ Category %d: Auth check failed: %s", category_index, cat_auth_err)
            # ------------------------------------------

            # FIX 3 (20260408): File-based resume calculation per category.
            # Mirrors main workflow lines 5750-5945 (passive_extraction_workflow_latest.py):
            #   STEP 1 — linking map check (processed_keys)
            #   STEP 2 — cache file check (cached_keys)
            #   Filter invariant: in == skip + cached + full
            #   Fast-forward state counters so progress metrics are accurate on resume.
            #   RESUME STATE log in canonical format for AI assistant / forensic diagnosis.
            _skip_keys: set[str] = set()
            _cached_only_keys: set[str] = set()
            _needs_full: list[dict[str, Any]] = []
            for _fp in source_products:
                _fk = _product_identity(_fp)
                if _fk and _fk in processed_keys:
                    _skip_keys.add(_fk)
                elif _fk and _fk in cached_keys:
                    _cached_only_keys.add(_fk)
                else:
                    _needs_full.append(_fp)

            _in_count = len(source_products)
            _skip_count = len(_skip_keys)
            _cached_count = len(_cached_only_keys)
            _full_count = len(_needs_full)

            log.info(
                "STEP 1 - LINKING MAP CHECK: %d complete (skipped)", _skip_count
            )
            log.info(
                "STEP 2 - PRODUCT CACHE CHECK (stable_key): %d cached; %d need extraction",
                _cached_count, _full_count,
            )
            log.info(
                "Filter Invariant: in=%d == skip=%d + cached=%d + full=%d",
                _in_count, _skip_count, _cached_count, _full_count,
            )

            _inv_ok = _in_count == _skip_count + _cached_count + _full_count

            # Fast-forward state counters (matches main workflow lines 5839-5860)
            if _skip_count > 0:
                _cur_amz = int(sp.get("amazon_products_completed", 0) or 0)
                if _cur_amz < _skip_count:
                    sp["amazon_products_completed"] = _skip_count
                    state_manager.save_state_atomic()
            _persisted_phase = sp.get("current_phase", "supplier")
            if _persisted_phase == "supplier":
                _total_skipped_sup = _skip_count + _cached_count
                _cur_sup = int(sp.get("supplier_products_completed", 0) or 0)
                if _cur_sup < _total_skipped_sup:
                    sp["supplier_products_completed"] = _total_skipped_sup
                    state_manager.save_state_atomic()

            if not _inv_ok:
                log.error(
                    "FILTER INVARIANT VIOLATION: in=%d != skip=%d + cached=%d + full=%d",
                    _in_count, _skip_count, _cached_count, _full_count,
                )
            else:
                log.info(
                    "FILTER INVARIANT VALIDATED:\n"
                    "  in=%d == skip=%d + cached=%d + full=%d",
                    _in_count, _skip_count, _cached_count, _full_count,
                )
            _worklist_type = "full_extraction" if _full_count > 0 else ("amazon_only" if _cached_count > 0 else "complete")
            log.info(
                "FILE-BASED RESUME CALCULATION:\n"
                "  Phase (AUTHORITY): %s\n"
                "  Category: %s\n"
                "  Denominator: %d\n"
                "  Evidence:\n"
                "    - Linking map (skip): %d\n"
                "    - Supplier cache: %d\n"
                "    - Need full extraction: %d\n"
                "  Filter invariant: %s\n"
                "  Worklist type: %s",
                _persisted_phase, source_url, _in_count,
                _skip_count, _cached_count, _full_count,
                "PASS" if _inv_ok else "FAIL",
                _worklist_type,
            )
            log.info(
                "RESUME STATE: phase=%s cat=%d/%d url=%s supplier=%d/%d amazon=%d/%d",
                _persisted_phase, category_index, len(source_items), source_url,
                sp.get("supplier_products_completed", 0), _in_count,
                sp.get("amazon_products_completed", 0), _in_count,
            )
            # ------------------------------------------------------------------

            # --- Option A: Visit individual product pages directly (no category navigation) ---
            if source_url.startswith("http"):
                from bs4 import BeautifulSoup as _BS4
                refreshed_products = []
                _skipped_in_refresh = 0
                for prod_idx, _prod in enumerate(source_products, start=1):
                    # FIX A + FIX 3 (20260408): Skip supplier re-scrape for products
                    # already in the linking map (processed_keys) OR already in the
                    # on-disk cache from a prior interrupted run (cached_keys).
                    # This covers both Phase-2 and Phase-1 resume scenarios.
                    _prod_key = _product_identity(_prod)
                    if _prod_key and (_prod_key in processed_keys or _prod_key in cached_keys):
                        refreshed_products.append(_prod)
                        _skipped_in_refresh += 1
                        continue
                    _prod_url = _prod.get("url") or _prod.get("normalized_url")
                    if _prod_url and _prod_url.startswith("http"):
                        try:
                            _html = await scraper.get_page_content(_prod_url)
                            if _html:
                                _soup = _BS4(_html, "html.parser")
                                _page_data = await scraper._extract_product_data_from_soup(
                                    _soup, _prod_url, category_url=source_url
                                )
                                if _page_data and _page_data.get("title"):
                                    log.info(
                                        "Live-refreshed %d/%d: %s",
                                        prod_idx, len(source_products), _page_data["title"],
                                    )
                                    refreshed_products.append(_page_data)
                                    # FIX 2 (20260408): Write this live-scraped product to
                                    # the cache file immediately (per-product, frequency=1).
                                    # Mirrors main workflow update_frequency_products=1 in
                                    # system_config.supplier_cache_control.
                                    # Only on the SUCCESS path — failed fetches are retried
                                    # on next resume and must not pollute the cache.
                                    try:
                                        _new_total = _append_supplier_cache(
                                            repo_root, sandbox_supplier, _page_data
                                        )
                                        if _prod_key:
                                            cached_keys.add(_prod_key)
                                        log.info(
                                            "FIX 2 Cache append %d/%d: %s (cache total=%d)",
                                            prod_idx, len(source_products),
                                            _page_data.get("title", ""), _new_total,
                                        )
                                    except Exception as _cache_err:
                                        log.warning(
                                            "FIX 2 Cache append failed for %s: %s",
                                            _prod_url, _cache_err,
                                        )
                                else:
                                    log.warning("No data extracted from %s; using cached", _prod_url)
                                    refreshed_products.append(_prod)
                            else:
                                log.warning("Failed to fetch %s; using cached", _prod_url)
                                refreshed_products.append(_prod)
                        except Exception as _refresh_err:
                            log.warning("Refresh failed for %s (%s); using cached", _prod_url, _refresh_err)
                            refreshed_products.append(_prod)
                    else:
                        refreshed_products.append(_prod)
                if refreshed_products:
                    if _skipped_in_refresh:
                        log.info(
                            "FIX A: Refresh loop skipped %d already-processed products in this category",
                            _skipped_in_refresh,
                        )
                    source_products = refreshed_products
                    log.info("Refreshed %d products for %s", len(refreshed_products), source_url)
                    # FIX C: Per-category full cache overwrite was removed previously.
                    # FIX 1+2 (20260408): Startup paste also removed. Cache is now
                    # populated exclusively via _append_supplier_cache per product
                    # on the live-scrape success path above. Downstream consumers
                    # (financial calculator) read from the same cache path.
            # --------------------------------------------------------------------------
            if _cancel_requested(repo_root, run_id):
                cancel_requested = True
                log.warning("Cancellation requested before category checkpoint; finalizing partial outputs")
                break
            sp["current_category_url"] = source_url
            sp["persistent_category_index"] = max(
                int(sp.get("persistent_category_index") or 0), category_index
            )
            # Fix A (20260408): Reflect actual phase before entering Amazon analysis loop.
            sp["current_phase"] = "amazon_analysis"
            state_manager.save_state_atomic()

            for _idx, product in enumerate(source_products, start=1):
                if _cancel_requested(repo_root, run_id):
                    cancel_requested = True
                    log.warning("Cancellation requested during product refresh; stopping after checkpoint")
                    break
                # Initialize variables before try block to prevent NameError in except
                title = ""
                supplier_url = ""
                ean = ""
                product_key = ""
                try:
                    title = str(product.get("title") or "")
                    supplier_url = str(product.get("url") or "")
                    ean = _sanitize_ean(str(product.get("ean") or ""))
                    product_key = _product_identity(product)

                    if product_key and product_key in processed_keys:
                        log.info("Skipping already-processed product %d/%d: %s", _idx, len(source_products), product_key)
                        sp["supplier_products_completed"] = min(len(products), len(results))
                        sp["amazon_products_completed"] = len(results)
                        if _idx == len(source_products):
                            state_manager.save_state_atomic()
                        continue

                    match_method = "title"
                    asin: str | None = None
                    price: float | None = None
                    amazon_title: str | None = None

                    query = ean or title

                    if not query:
                        results.append(
                            {
                                "supplier_ean": ean,
                                "supplier_url": supplier_url,
                                "supplier_title": title,
                                "supplier_price": product.get("price"),
                                "amazon_asin": None,
                                "match_method": "missing_query",
                                "confidence": 0,
                                "created_at": _utc_now_iso(),
                            }
                        )
                        if product_key:
                            processed_keys.add(product_key)
                        _flush_if_needed()
                        continue

                    extraction_result = await extractor.search_by_ean_and_extract_data(
                        ean=ean, supplier_product_title=title, page=page
                    )
                    match_method = _normalize_match_method(extraction_result)

                    asin = extraction_result.get("asin")
                    amazon_title = extraction_result.get("title")
                    price = extraction_result.get("current_price")

                    if extraction_result.get("_search_method_used") == "captcha":
                        results.append(
                            {
                                "supplier_ean": ean,
                                "supplier_url": supplier_url,
                                "supplier_title": title,
                                "supplier_price": product.get("price"),
                                "amazon_asin": asin,
                                "match_method": "captcha",
                                "confidence": 0,
                                "created_at": _utc_now_iso(),
                            }
                        )
                        if product_key:
                            processed_keys.add(product_key)
                        _flush_if_needed()
                        continue

                    if not asin:
                        results.append(
                            {
                                "supplier_ean": ean,
                                "supplier_url": supplier_url,
                                "supplier_title": title,
                                "supplier_price": product.get("price"),
                                "amazon_asin": None,
                                "match_method": "no_results",
                                "confidence": 0,
                                "created_at": _utc_now_iso(),
                            }
                        )
                        if product_key:
                            processed_keys.add(product_key)
                        _flush_if_needed()
                        continue

                    if not dry_run:
                        out_path = _amazon_cache_path(repo_root, run_id, asin, ean)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        write_json_atomic(out_path, extraction_result)

                        canonical_path = _canonical_amazon_cache_path(repo_root, asin, ean)
                        canonical_path.parent.mkdir(parents=True, exist_ok=True)
                        write_json_atomic(canonical_path, extraction_result)

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
                    if product_key:
                        processed_keys.add(product_key)
                    _flush_if_needed(matched=True)
                except Exception as e:
                    log.error(
                        f"Error processing product {product.get('title', 'Unknown')}: {e}",
                        exc_info=True,
                    )
                    results.append(
                        {
                            "supplier_ean": ean,
                            "supplier_url": supplier_url,
                            "supplier_title": title,
                            "supplier_price": product.get("price"),
                            "amazon_asin": None,
                            "match_method": "error",
                            "confidence": 0,
                            "created_at": _utc_now_iso(),
                        }
                    )
                    if product_key:
                        processed_keys.add(product_key)
                    _flush_if_needed()
                    continue
                finally:
                    sp["supplier_products_completed"] = min(len(products), len(results))
                    sp["supplier_products_needing_extraction"] = max(0, len(products) - len(results))
                    sp["amazon_products_completed"] = len(results)
                    sp["amazon_products_needing_analysis"] = max(0, len(products) - len(results))
                    state_manager.save_state_atomic()

            if cancel_requested:
                break

    finalization_error: Exception | None = None
    summary: dict[str, Any] = {"cancelled": False, "successful_matches": 0, "total_results": len(results)}
    try:
        asyncio.run(run())
    except KeyboardInterrupt as e:
        cancel_requested = True
        finalization_error = e
        log.warning("Product-list refresh interrupted; finalizing partial outputs")
    except Exception as e:
        cancel_requested = cancel_requested or _cancel_requested(repo_root, run_id)
        finalization_error = e
    finally:
        summary = _finalize_refresh_run(
            repo_root=repo_root,
            sandbox_supplier=sandbox_supplier,
            state_manager=state_manager,
            products=products,
            results=results,
            dry_run=dry_run,
            cancelled=cancel_requested or _cancel_requested(repo_root, run_id),
        )
        # Page cleanup handled by BrowserManager singleton lifecycle

    if finalization_error is not None and not summary["cancelled"]:
        raise finalization_error

    if summary["cancelled"]:
        log.warning(
            "Product list refresh cancelled: %d/%d matched",
            summary["successful_matches"],
            summary["total_results"],
        )
    else:
        log.info(
            "Product list refresh complete: %d/%d matched",
            summary["successful_matches"],
            summary["total_results"],
        )


if __name__ == "__main__":
    main()
