# Product List Refresh Audit Report (2026-02-02)

## Executive Summary

This report audits the product-list refresh run end-to-end and explains why it looked like “nothing happened” and why the results are currently **incorrect** (all `amazon_asin` null) despite producing a financial report.

### Run Under Audit
- **run_id**: `angelwholesale_co_uk_product_list_refresh_20260130`
- **sandbox_supplier**: `angelwholesale.co.uk__sandbox__angelwho`
- **products input**: `OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_6.json`

### High-level Outcome
- The job **did execute** and finished quickly (~7 seconds), but Amazon extraction failed for every product due to a **wrong keyword argument name** when calling `FixedAmazonExtractor.search_by_ean_and_extract_data(...)`.

---

## Evidence Pack (3 sources per claim)

### Claim A — The job DID run (not “stuck”)

**Source 1 (status file)**
- `OUTPUTS\CONTROL_PLANE\status\angelwholesale_co_uk_product_list_refresh_20260130.json` shows:
  - `state`: `done`
  - `started_at`: `2026-02-02T12:26:00Z`
  - `ended_at`: `2026-02-02T12:26:07Z`

**Source 2 (job file moved to done)**
- `OUTPUTS\CONTROL_PLANE\jobs\done\job_angelwholesale_co_uk_product_list_refresh_20260130.json` exists, meaning worker completed it.

**Source 3 (runner log file exists for run_id)**
- `OUTPUTS\CONTROL_PLANE\logs\angelwholesale_co_uk_product_list_refresh_20260130.log` exists and contains run activity.

### Claim B — Amazon extraction FAILED for all 6 products due to wrong argument name

**Source 1 (runner log)**
- `OUTPUTS\CONTROL_PLANE\logs\angelwholesale_co_uk_product_list_refresh_20260130.log` lines 28-33 contain:
  - `FixedAmazonExtractor.search_by_ean_and_extract_data() got an unexpected keyword argument 'supplier_title'`

**Source 2 (script call site)**
- `control_plane\run_product_list_refresh.py:191-193` calls:
  - `extractor.search_by_ean_and_extract_data(ean=ean, supplier_title=title, page=page)`

**Source 3 (actual extractor signature)**
- `python` inspection of `tools.amazon_playwright_extractor.FixedAmazonExtractor.search_by_ean_and_extract_data` reports signature:
  - `(self, ean: str, supplier_product_title: str, page: Optional[Page]=None) -> Dict[str, Any]`
  - Therefore, **the correct kw arg is `supplier_product_title`, not `supplier_title`**.

### Claim C — Linking map produced, but ALL entries are errors with `amazon_asin=null`

**Source 1 (linking map file)**
- `OUTPUTS\FBA_ANALYSIS\linking_maps\angelwholesale.co.uk__sandbox__angelwho\linking_map.json`

**Source 2 (computed summary)**
- Counted entries: 6
- `amazon_asin null count`: 6
- `match_method` counts: `{'error': 6}`

**Source 3 (status file points to the same linking_map path)**
- `OUTPUTS\CONTROL_PLANE\status\angelwholesale_co_uk_product_list_refresh_20260130.json` → `resolved_paths.linking_map` references the same file.

### Claim D — Financial report exists BUT is misleading because it used existing amazon_cache files (not fresh extraction)

**Source 1 (financial CSV exists)**
- `OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk__sandbox__angelwho\fba_financial_report_angelwholesale-co-uk__sandbox__angelwho_20260202_162606.csv`

**Source 2 (runner log indicates calculator used amazon_cache directory)**
- `OUTPUTS\CONTROL_PLANE\logs\angelwholesale_co_uk_product_list_refresh_20260130.log` shows:
  - `Using Amazon data from: ...\OUTPUTS\FBA_ANALYSIS\amazon_cache`

**Source 3 (linking_map has ASIN=None, yet report has ASIN values)**
- Linking map: all `amazon_asin` are `null`.
- Financial CSV row 2 shows `ASIN` = `B01N38NKS4` for EAN `5012866069058`.
- That mismatch indicates the calculator fell back to existing caches/heuristics and is not reflecting a true matching run.

---

## Root Causes

### Root Cause 1 (Primary): Incorrect kwarg name in product-list runner
- Code passes `supplier_title=...` but the extractor expects `supplier_product_title=...`.
- This causes **100% extraction failure**.

### Root Cause 2 (UX/operational): “Nothing happened” perception
- The UI’s tool `enqueue_product_list_refresh` only queues a job.
- Execution requires the worker; plus historically there was a stale lock (`active_run.lock`) blocking processing.

### Root Cause 3 (Status reporting bug): cached_products_exists is wrong
- Status file reports `cached_products_exists=false`, but the expected cache file exists:
  - `OUTPUTS\cached_products\angelwholesale-co-uk__sandbox__angelwho_products_cache.json`
- The worker’s status snapshot logic doesn’t include `cached_products_file` for product-list refresh suppliers.

---

## Suggested Fixes (minimal-risk, highest success)

### Fix 1 (Must do): Correct the kwarg name in `control_plane\run_product_list_refresh.py`
Change:
- `supplier_title=title`
To:
- `supplier_product_title=title`

This is the smallest possible change to restore the intended flow.

### Fix 2 (Quality): Improve status reporting for product-list refresh
- Ensure `resolved_paths` includes `cached_products_file` and `artifacts.cached_products_exists` is accurate for sandbox suppliers.

### Fix 3 (UX): Make chat output clearer without breaking JSON-only planner
- Keep planner JSON-only.
- Allow `explanation` to be 2-4 sentences.
- UI should state explicitly: enqueue queues a job; worker executes; show status/log paths.

---

## Next Verification Steps

After Fix 1, rerun the same job and verify:
1) `OUTPUTS\CONTROL_PLANE\logs\<run_id>.log` contains no “unexpected keyword argument” errors.
2) `OUTPUTS\FBA_ANALYSIS\linking_maps\<sandbox>\linking_map.json` has `amazon_asin` populated for most entries.
3) Newly written amazon_cache files for those ASIN/EAN pairs have `keepa.product_details_tab_data` fields.
