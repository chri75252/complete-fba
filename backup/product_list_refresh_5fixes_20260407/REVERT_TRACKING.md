# REVERT_TRACKING — product_list_refresh_5fixes_20260407

**Date:** 2026-04-07
**Reason:** Fix product-list-refresh resume regression introduced by `product_refresh_live_scrape_20260314`. Five surgical fixes restore correct skip-on-resume behavior, eliminate cache shrinking bug, complete linking-map data, and tolerate sandbox name variants.
**Backup root:** `backup/product_list_refresh_5fixes_20260407/`

## Files Modified

| File | Backup Path | Validation |
|---|---|---|
| `control_plane/run_product_list_refresh.py` | `backup/product_list_refresh_5fixes_20260407/run_product_list_refresh.py` | py_compile PASSED |

## Historical Context

The bugs originated on **2026-03-14** in `product_refresh_live_scrape_20260314`, which introduced the supplier live-refresh loop and per-category cache overwrite without corresponding skip-on-resume logic. Before that change, the workflow used existing supplier data from the product list and only performed Amazon analysis — there was no waste on resume because there was no re-scraping.

After Mar 14, every resume re-scraped all ~1776 supplier pages from product 1 of category 1, even when 861 products were already complete. The bugs were masked when staying in the same chat (planner_hints carried supplier_domain forward) and surfaced when starting a new chat (LLM had to reconstruct supplier_domain from text and sometimes hallucinated `co-uk` instead of `co.uk`, causing state file lookup to fail and the run to start completely fresh).

## Fixes Applied (in order)

### Fix 5 — Sandbox name fuzzy resolution against on-disk truth
**Location:** New helper function `_resolve_canonical_sandbox_supplier()` after `_cancel_requested()` (~line 81). Called immediately after `sandbox_supplier` is loaded from job payload (~line 386).

**What it does:**
- Scans `OUTPUTS/FBA_ANALYSIS/linking_maps/` for any directory whose normalized name (dots/hyphens/underscores collapsed) matches the requested sandbox_supplier
- If found, replaces `sandbox_supplier` with the on-disk canonical form
- If no match, returns the requested name unchanged (genuine fresh run)

**Why:** Tolerates LLM hallucinations of `co-uk` vs `co.uk` vs `co_uk`. Without this, a new chat session that produces a hyphenated supplier name causes state file lookup, linking map lookup, and credential lookup to all miss the existing on-disk data, forcing a full re-process of 1776 products.

**Code added:**
```python
def _normalize_sandbox_for_match(value: str) -> str:
    return re.sub(r"[._-]+", "_", str(value or "")).lower()

def _resolve_canonical_sandbox_supplier(repo_root: Path, requested: str) -> str:
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
```

**Call site added:**
```python
# FIX 5: Resolve sandbox name against on-disk truth (handles co.uk/co-uk/co_uk variants)
sandbox_supplier = _resolve_canonical_sandbox_supplier(repo_root, sandbox_supplier)
```

### Fix B — Category skip on resume
**Location:** Inside the outer category loop (~line 548), immediately after `for category_index, ...:`.

**What it does:**
- Builds the set of identity keys for all products in the current category
- If every key is already in `processed_keys` (linking map), skip the entire category with `continue`
- Uses `issubset()` for mathematically definitive completion check (handles partial categories correctly — even one missing product means the category is entered)

**Why:** Before this fix, the runner ALWAYS started from category 1 even if `persistent_category_index=3`. Categories 1 and 2 (561 fully processed products) were re-entered, causing wasted authentication checks and supplier re-scraping.

**Code added:**
```python
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
```

### Fix A — Per-product skip in supplier refresh loop
**Location:** Inside the supplier live-refresh loop (~line 573), immediately after `for prod_idx, _prod in enumerate(...):`.

**What it does:**
- Computes the product's identity key
- If the key is already in `processed_keys`, append the existing data to `refreshed_products` (preserving title/url/ean/price as-is) and skip the supplier page scrape
- Increments a counter `_skipped_in_refresh` for visibility logging
- Logs a summary at the end of the category showing how many products were skipped

**Why:** Before this fix, the supplier refresh loop visited EVERY product page on the supplier site unconditionally, even for the 861 products already in the linking map. Each page visit takes ~7 seconds. The Amazon analysis loop (which has a `processed_keys` skip at line 636) was never reached because the supplier loop ran first and was killed before completing. Result: zero progress on every interrupted resume.

**Code added (skip block):**
```python
_skipped_in_refresh = 0
for prod_idx, _prod in enumerate(source_products, start=1):
    # FIX A: Skip supplier re-scrape for products already in the linking map.
    # Their existing data (title/url/ean/price) is preserved as-is.
    _prod_key = _product_identity(_prod)
    if _prod_key and _prod_key in processed_keys:
        refreshed_products.append(_prod)
        _skipped_in_refresh += 1
        continue
    _prod_url = _prod.get("url") or _prod.get("normalized_url")
    ...
```

**Code added (summary log):**
```python
if refreshed_products:
    if _skipped_in_refresh:
        log.info(
            "FIX A: Refresh loop skipped %d already-processed products in this category",
            _skipped_in_refresh,
        )
    source_products = refreshed_products
    log.info("Refreshed %d products for %s", len(refreshed_products), source_url)
```

### Fix C — Remove per-category cache overwrite
**Location:** ~line 603 (the `_write_supplier_cache(repo_root, sandbox_supplier, refreshed_products)` call inside the category loop).

**What it does:**
- Removes the call entirely
- The full 1776-product cache is already seeded at line 423 at startup; the per-category overwrite was destroying that and replacing it with only the current category's products (e.g., 238 for category 1)

**Why:** The per-category cache write was a misguided "Mar 14" attempt to persist live-scraped data. It actually broke things: after category 1 finished, the cache had 238 products instead of 1776. Downstream consumers (FBA financial calculator) read this cache and saw incomplete data. The fresh data still ends up in the linking map; the cache file's purpose is to provide a stable seed for downstream consumers, not to mirror live scraping.

**Code removed:**
```python
# Update cached product file with live data
if not dry_run:
    try:
        _write_supplier_cache(repo_root, sandbox_supplier, refreshed_products)
    except Exception:
        pass
```

**Code added (comment placeholder):**
```python
# FIX C: Per-category cache overwrite removed. Cache is seeded once
# at startup (line 423) with the full 1776-product list, and that
# full set is what downstream consumers (financial calculator) read.
# Overwriting with a single category's products shrinks the cache
# from 1776 to ~238 entries and breaks downstream reports.
```

### Fix D — Add `supplier_price` to all 4 failure-path linking-map entries
**Locations:** Four `results.append(...)` blocks for the `missing_query`, `captcha`, `no_results`, and `error` paths (~lines 652, 678, 695, 742).

**What it does:** Adds `"supplier_price": product.get("price"),` to each failure-path dict.

**Why:** Pre-existing bug (predates Mar 14). Before this fix, only the success path (line 725) included `supplier_price`. The 4 failure paths omitted it, leaving 683/861 linking map entries with no price data. Financial reports for non-matched products were incomplete.

**Code added (4 places):**
```python
"supplier_price": product.get("price"),
```

## Validation Performed

```
python -m py_compile control_plane/run_product_list_refresh.py
→ COMPILE OK
```

Programmatic verification:
```
Fix 5 helper:                  True
Fix 5 call site:               True
Fix B:                         True
Fix A:                         True
Fix A log:                     True
Fix C:                         True
Fix D supplier_price count:    5  (1 pre-existing success + 4 newly added failure paths)
Cache overwrite call removed:  True
File size:                     36947 bytes (was 34294, +2653 bytes for additions)
```

## To Revert (single command)

```bash
cp backup/product_list_refresh_5fixes_20260407/run_product_list_refresh.py control_plane/run_product_list_refresh.py
```

Verify revert with:
```bash
python -m py_compile control_plane/run_product_list_refresh.py
diff control_plane/run_product_list_refresh.py backup/product_list_refresh_5fixes_20260407/run_product_list_refresh.py
# (diff should show no output)
```

## Files NOT Modified

The following files were CONSIDERED but deliberately NOT touched:
- `tools/passive_extraction_workflow_latest.py` — main workflow, has its own working skip logic
- `utils/path_manager.py` — `get_processing_state_path` is shared across workflows; the fuzzy resolution is done at the runner level instead so other workflows are unaffected
- `config/system_config_loader.py` — already received the credential fuzzy lookup fix in a prior session
- `control_plane/chat_orchestrator.py` — AI assistant behavior must remain unchanged
- `control_plane/tools/clarify.py` — AI assistant behavior must remain unchanged
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` — AI assistant behavior must remain unchanged

## Workflows NOT Affected

- **Main workflow** (`run_custom_*.py` → `passive_extraction_workflow_latest.py`): completely separate code path, has its own working skip logic at line 5481
- **Category sandbox workflow**: uses `passive_extraction_workflow_latest.py` in sandbox mode, also separate
- **AI assistant / chat orchestrator**: zero changes to assistant code; newer "interpret responses" behavior preserved
