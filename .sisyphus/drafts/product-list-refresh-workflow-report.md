# Product List (Sandboxed) Workflow — Audit + Next Steps

**Scope (strict):** Product list refresh run `run_angelwholesale_mixed_6` only.

**Key question:** Should the product-list workflow (A) produce a full financial report like the main workflow, or (B) remain a lightweight refresh that avoids shared cache mutation?

---

## 1) What you observed (confirmed) and why

### 1.1 Log says Amazon cache files saved “quickly”

**Observation confirmed:** timestamps between saves are seconds-to-tens-of-seconds.

**Why it’s possible:** the product-list runner does **minimal extraction** (search page + product page HTML, regex for ASIN/title/price). It does **not** run the heavy Keepa/SellerAmp extraction loop.

**Evidence (3 sources):**
- Runner log: `OUTPUTS/CONTROL_PLANE/logs/run_angelwholesale_mixed_6.log` lines 2–7 show 6 amazon cache saves within ~40s.
- Runner code: `control_plane/run_product_list_refresh.py#L229-L307` does `page.goto(search_url)` then `page.goto(product_url)` and parses HTML via `_first_result_asin/_extract_title/_extract_price`.
- Cache file sizes: `control_plane/OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_B0FV8KV3FS_5012866069058.json` and `amazon_B01MSZQ37V_5035320257174.json` are ~500–600 bytes, consistent with a minimal payload, not full extraction.

### 1.2 Log says linking map saved but the folder you checked was empty

**Observation confirmed:** `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/` is empty.

**Root reason:** the runner wrote outputs under `control_plane/OUTPUTS/...` instead of repo-root `OUTPUTS/...`.

**Evidence (3 sources):**
- Runner log: `OUTPUTS/CONTROL_PLANE/logs/run_angelwholesale_mixed_6.log` line 8 shows `ATOMIC SAVE: linking_map.json (6 entries)`.
- File exists (wrong tree): `control_plane/OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/linking_map.json` exists.
- File missing (expected tree): `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/` contains no `linking_map.json`.

### 1.3 “No processing state file was created”

**This is expected** for `run_product_list_refresh`.

**Evidence (3 sources):**
- Status file: `OUTPUTS/CONTROL_PLANE/status/run_angelwholesale_mixed_6.json` has `resolved_paths.processing_state = null`.
- Job type: `OUTPUTS/CONTROL_PLANE/jobs/failed/job_run_angelwholesale_mixed_6.json` has `job_type = "run_product_list_refresh"`.
- Runner code: `control_plane/run_product_list_refresh.py` contains no EnhancedStateManager / FixedEnhancedStateManager usage and no writes to `OUTPUTS/CACHE/processing_states`.

---

## 2) The real failure: why the run ended as FAILED

The run did **write** cache + linking_map (in the wrong `control_plane/OUTPUTS` tree), then failed during financial calculation.

**Evidence (3 sources):**
- Status: `OUTPUTS/CONTROL_PLANE/status/run_angelwholesale_mixed_6.json` shows `state: failed` + `summary: Process exited with code 1`.
- Log traceback: `OUTPUTS/CONTROL_PLANE/logs/run_angelwholesale_mixed_6.log` lines 10–28 show `FileNotFoundError` for `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__run_ange_products_cache.json`.
- File exists elsewhere: `control_plane/OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__run_ange_products_cache.json` exists, proving it was written but in a different root.

### 2.1 Root cause: wrong repo_root in product-list runner

**What’s wrong:** `control_plane/run_product_list_refresh.py` uses `repo_root = Path(__file__).resolve().parent`, which evaluates to the `control_plane/` directory.

So the runner writes to `control_plane/OUTPUTS/...` while the financial calculator reads from repo-root `OUTPUTS/...`.

**Evidence (3 sources):**
- Code: `control_plane/run_product_list_refresh.py:178` sets repo_root to `control_plane/`.
- Filesystem: `control_plane/OUTPUTS/...` directories exist and contain this run’s artifacts.
- Traceback: `OUTPUTS/CONTROL_PLANE/logs/run_angelwholesale_mixed_6.log` shows financial calculator looking for `...\OUTPUTS\cached_products\...` (repo-root).

---

## 3) Your concern about “minimal amazon cache payload” and the financial calculator

### 3.1 Will financial calculator “definitely fail” because Keepa/SellerAmp fields are missing?

**No, not necessarily.** The calculator’s *hard requirement* is that the Amazon JSON has a sell price.

**What it needs at minimum:** `current_price` or `price`.

**Evidence (3 sources):**
- Financial code: `tools/FBA_Financial_calculator.py`’s `financials()` returns empty `{}` only when `current_price` and `price` are both missing.
- Product-list amazon payload: `control_plane/run_product_list_refresh.py#L94-L113` writes `current_price` when price is parsed.
- Product-list linking map confirms prices were parsed: `control_plane/OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/linking_map.json` includes `amazon_price` values for all 6 products.

### 3.2 Accuracy caveat (your point is valid)

Even if the calculator runs, **fee accuracy will be worse** because Keepa absolute fees may not be present.

**Evidence (3 sources):**
- Product-list payload explicitly sets `keepa: {}` and `selleramp: {"status": "not_run"}`: `control_plane/run_product_list_refresh.py#L94-L105`.
- Financial calculator uses defaults if Keepa fee data is missing: `tools/FBA_Financial_calculator.py` initializes defaults then optionally overrides from Keepa.
- PRD/gaps doc explicitly warns minimal cache is “no Keepa/SellerAmp parsing”: `SYSTEM_CHAT_UI_PRDS/PRODUCT_LIST_REFRESH_GAPS_REPORT_AND_AGENT_PROMPT.md`.

---

## 4) Amazon cache overwrite policy (critical design decision)

### 4.1 Current product-list behavior (when repo_root is corrected)

If repo_root is fixed to repo root, the product-list runner will write into the shared directory:
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{asin}_{ean}.json`

That **can overwrite** existing cache files with the same ASIN+EAN.

**Evidence (3 sources):**
- Writer path: `control_plane/run_product_list_refresh.py#L40-L47` uses a global amazon_cache dir.
- Write semantics: `control_plane/run_product_list_refresh.py#L80-L93` calls `write_json_atomic(out_path, ...)` (atomic replace).
- It creates backups before overwrite: `control_plane/run_product_list_refresh.py#L82-L92` backs up to `OUTPUTS/CONTROL_PLANE/overrides/<runid>/amazon_cache_backups/`.

### 4.2 What you proposed (reasonable)

If we *keep minimal extraction*, safest is:
- Write Amazon cache outputs into a **run-scoped folder** (sandboxed), and
- **Do not run** `FBA_Financial_calculator` (or run it only if a “full cache” exists).

This avoids poisoning the shared amazon_cache with low-fidelity data.

---

## 5) Sandbox directory grouping you want (supplier__sandbox/...) — impact assessment

Today, sandboxing is implemented by **suffixing supplier_name** (`supplier__sandbox__<id>`). It is *not* implemented as nested directories like `supplier__sandbox/<runid>/...`.

Changing to nested run directories would touch multiple systems (higher risk):
- Dashboard path resolver (`dashboard/metrics_core_fixed.py`)
- Control-plane tool resolvers (`control_plane/tools/*`)
- Financial calculator path resolution (`tools/FBA_Financial_calculator.py`)
- Possibly workflow path resolution (`utils/path_manager.py` / workflow code)

**Recommendation:** treat this as a second-phase refactor after the product-list workflow is functional.

---

## 6) Recommended next steps (surgical, highest likelihood)

### Phase 1 — Make product-list workflow functional (minimal risk)

1) Fix repo_root bug in `control_plane/run_product_list_refresh.py` so it writes to repo-root `OUTPUTS/`.
- Impact: high (unblocks all expected artifacts)
- Risk: low (single-file, single-line change)

2) Decide Amazon cache policy for product-list refresh (choose one):

**Option A (lowest change): allow overwrite + keep backups (current design)**
- Keep writing to `OUTPUTS/FBA_ANALYSIS/amazon_cache`.
- Rely on existing backup mechanism.
- Financial calculator can run (but fee accuracy may be lower).

**Option B (recommended if you want strict safety): do NOT overwrite shared amazon cache**
- Write amazon cache to a run-scoped folder (e.g. `OUTPUTS/FBA_ANALYSIS/amazon_cache/<sandbox_supplier>/...`).
- Disable financial calculator execution in product-list workflow unless a full cache exists.
- This avoids degrading your shared amazon_cache.

### Phase 2 — Upgrade to “main workflow quality” (only if required)

If you truly need Keepa/SellerAmp-level extraction for product-list refresh:
- Replace minimal extraction in `control_plane/run_product_list_refresh.py` with calls into the same Amazon extractor used by the main workflow.
- This is higher risk due to dependencies (BrowserManager, extension timing, possible environment requirements).

---

## 7) Decisions needed from you (to finalize a plan)

1) For product-list refresh, should it be:
- **A)** “Fast refresh” (minimal extraction) and never overwrite shared amazon_cache?
- **B)** “Full parity” (heavy extraction) and produce the same financial outputs?

2) Should product-list refresh run `FBA_Financial_calculator`?
- **YES**, even if fees are defaults
- **NO**, only when full Keepa fee data exists

3) Do you want the per-supplier sandbox parent folder refactor now, or later?

---

## Appendix: Concrete artifact locations from `run_angelwholesale_mixed_6`

**Log:** `OUTPUTS/CONTROL_PLANE/logs/run_angelwholesale_mixed_6.log`

**Artifacts actually written (wrong tree due to repo_root bug):**
- `control_plane/OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__run_ange_products_cache.json`
- `control_plane/OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/linking_map.json`
- `control_plane/OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_B0FV8KV3FS_5012866069058.json` (and 5 others)

**Artifacts missing where you expected (repo-root OUTPUTS):**
- `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox__run_ange_products_cache.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__run_ange/linking_map.json`
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_B0FV8KV3FS_5012866069058.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/angelwholesale-co-uk__sandbox__run_ange/` (empty)
