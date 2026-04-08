# REVERT TRACKING — product_list_refresh_cache_per_product_20260408

**Date:** 2026-04-08
**File changed:** `control_plane/run_product_list_refresh.py`
**Backup:** `backup/product_list_refresh_cache_per_product_20260408/control_plane/run_product_list_refresh.py`

To fully revert all changes below, copy the backup file back:
```
cp backup/product_list_refresh_cache_per_product_20260408/control_plane/run_product_list_refresh.py \
   control_plane/run_product_list_refresh.py
```

---

## Summary of Changes (3 fixes)

### Fix 1 — Remove startup raw-input cache paste
**Location:** After `scraper = None` assignment (near original line 464)

**Removed block:**
```python
if not dry_run:
    try:
        _write_supplier_cache(repo_root, sandbox_supplier, products)
    except Exception as e:
        log.warning("Failed to write sandbox supplier cache: %s", e)
```

**Why:** This wrote the raw 1776-entry input JSON (stale data from original full run)
to the sandbox cache file before any live scraping. The cache was therefore always
stale. Fix 2 replaces this with per-product writes of live-scraped data only.

**To revert Fix 1 only:** Re-insert the block above after the `scraper = None` line.

---

### Fix 2 — Add `_append_supplier_cache` helper + per-product cache write
**Location 1:** New function `_append_supplier_cache` added immediately after `_write_supplier_cache`
(original line ~173).

**Location 2:** Inside the supplier refresh loop (original lines 620–666), at the successful
live-scrape path only (`if _page_data and _page_data.get("title")`).

**What it does:**
- `_append_supplier_cache(repo_root, sandbox_supplier, product)` atomically loads the
  existing cache, builds a stable dedup key from EAN + normalized URL using `_product_identity`,
  skips the product if already present, appends if new, and writes back.
- Called immediately after `refreshed_products.append(_page_data)` on the success path.
- Also updates `cached_keys` in-memory so Fix 3 skip logic stays current within the same run.
- NOT called on fallback paths (failed/error scrapes) — only live-scraped enriched data
  goes into the cache. Failed products will be retried on next resume.

**To revert Fix 2 only:** Remove the `_append_supplier_cache` function definition and the
three lines `_append_supplier_cache(...)` + `cached_keys.add(...)` + `log.info("Cache appended...")`
inside the supplier refresh loop.

---

### Fix 3 — File-based resume calculation (mirrors main workflow STEP1/STEP2 pattern)
**Location 1:** Startup, after `processed_keys` set is built (original line ~453).
Builds `cached_keys` set from the existing cache file on disk (EAN+URL identity keys).

**Location 2:** Per-category, inserted after the auth check and before the supplier
refresh loop (original line ~619). Computes skip/cached/full classification per category
using both linking map (processed_keys) and cache file (cached_keys), logs:
- `STEP 1 - LINKING MAP CHECK: N complete (skipped)`
- `STEP 2 - PRODUCT CACHE CHECK (stable_key): N cached; N need extraction`
- `Filter Invariant: in=N == skip=N + cached=N + full=N (PASS/FAIL)`
- Fast-forwards state counters (supplier_products_completed, amazon_products_completed)
- `RESUME STATE: phase=... cat=N/M url=... supplier=N/M amazon=N/M`

**Location 3:** Extends Fix A skip check in the supplier loop to also check `cached_keys`,
so products already in the cache file (from a prior interrupted Phase 1 run) are not
re-scraped on resume.

**To revert Fix 3 only:**
1. Remove the `cached_keys` startup build block.
2. Remove the file-based resume calculation block inside the category loop.
3. Restore Fix A check to original: `if _prod_key and _prod_key in processed_keys:`

---

## Prior Fixes Unchanged

The following fixes applied in previous sessions remain intact:
- **Fix A** — Skip re-scrape for products already in linking map (inside supplier loop)
- **Fix B** — Skip fully-processed categories on resume (category loop)
- **Fix C** — Removed per-category cache overwrite (comment at original line 667)
- **Fix D** — `supplier_price` added to all failure-path linking map entries
- **Fix 5** — Sandbox name fuzzy resolution (`_resolve_canonical_sandbox_supplier`)
