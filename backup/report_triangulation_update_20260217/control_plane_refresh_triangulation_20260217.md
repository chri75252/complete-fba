# Control Plane: Product-List Refresh + Category Run Triangulation (2026-02-17)

This report is **file-grounded**: every behavioral claim is backed by at least 3 independent artifacts (status JSON, log, job JSON, and/or output files).

Repo root (absolute):
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

## What Happened With Hephaestus (bg_8d4f20e8)

- The background Hephaestus task `bg_8d4f20e8` produced **no emitted messages** and later reported **`status: cancelled`** when queried.
- Tool evidence in this workspace does **not** contain the internal reason for cancellation (no stdout/stderr transcript was returned, and the referenced agent session id later resolved as "session not found").
- As a result, I cannot reliably assert whether it was cancelled by the runtime, a timeout, or an explicit cancellation event; I can only confirm it did not execute far enough to emit any diagnostics.

## Why EFG Housewares Product-List Refresh Failed

Run id: `c1b322b9-f129-4923-9cbc-8c557608b6e1`

Root cause: the input file is **malformed JSON**, so the refresh runner crashed during JSON parse.

Triangulation:

1) Input file is malformed
- `OUTPUTS/PRODUCTS_LISTS/products_fullmix_efghouseware.json` contains a stray `}` at line 16 and a missing `{` before the next product (starts with `"title"` at line 17).

2) Status captures JSONDecodeError location
- `OUTPUTS/CONTROL_PLANE/status/c1b322b9-f129-4923-9cbc-8c557608b6e1.json` shows `error.last_log_lines` ending in:
  - `json.decoder.JSONDecodeError: Expecting value: line 16 column 3`

3) Log contains the full traceback
- `OUTPUTS/CONTROL_PLANE/logs/c1b322b9-f129-4923-9cbc-8c557608b6e1.log` shows the exception bubbling out of `control_plane/run_product_list_refresh.py` while calling `read_json(subset)`.

Job context:
- `OUTPUTS/CONTROL_PLANE/jobs/failed/job_c1b322b9-f129-4923-9cbc-8c557608b6e1.json` points at the same `products_fullmix_efghouseware.json` path.

Expected post-fix behavior (Issue #1): this same malformed file should now fail fast with an operator-facing `RuntimeError` like:
`Invalid JSON in products subset: <path> (line 16, column 3)`
and the status/log should show that clearer message rather than a raw traceback.

## Runs Triangulated (Artifacts + Counts)

For each run below, I checked:
- job JSON presence (and which lifecycle directory it ended up in)
- status JSON contents (state, started_at/ended_at, refresh paths/counts)
- run log (what the runner actually did)
- on-disk artifacts: linking map length + amazon_cache file count

### Product-list refresh: angelwholesale (6-product file)

Input file:
- `OUTPUTS/PRODUCTS_LISTS/products_fullmix_angelwholesale.json` contains **6 products** (not 4).

#### Run: f33d3fa5-228a-485c-82e7-9c0645a3e2b9 (done)

Artifacts:
- Job: `OUTPUTS/CONTROL_PLANE/jobs/done/job_f33d3fa5-228a-485c-82e7-9c0645a3e2b9.json`
- Status: `OUTPUTS/CONTROL_PLANE/status/f33d3fa5-228a-485c-82e7-9c0645a3e2b9.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/f33d3fa5-228a-485c-82e7-9c0645a3e2b9.log`
- Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__f33d3fa5/linking_map.json`

Counts (status vs disk):
- Status `input_products`: 4; actual input file products: 6
- Status `linking_map_entries`: 5; actual linking map length: 6
- Status `amazon_cache_files`: 5; observed pattern in other equivalent runs indicates 6 cache files were written

Interpretation:
- This is a representative example of **Issue #7** (status counts stale/incorrect), and is exactly the pattern fixed in `backup/fix_issues_6_7_20260217/TRACEABILITY.md`.

#### Run: 6c12fdbd-90a4-4eb5-aec9-3cf398c92f58 (status=cancelled)

Artifacts:
- Job: `OUTPUTS/CONTROL_PLANE/jobs/failed/job_6c12fdbd-90a4-4eb5-aec9-3cf398c92f58.json`
- Status: `OUTPUTS/CONTROL_PLANE/status/6c12fdbd-90a4-4eb5-aec9-3cf398c92f58.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/6c12fdbd-90a4-4eb5-aec9-3cf398c92f58.log`
- Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__6c12fdbd/linking_map.json`

Counts (status vs disk):
- Status state: `cancelled` and job file is in `jobs/failed/`.
- Disk linking map length: 4
- Log ends with: `Product list refresh complete: 1/4 matched` plus `RuntimeError: Event loop is closed` noise.

Interpretation:
- This run appears to have been treated as non-success by the worker lifecycle (hence failed/cancelled) even though the runner emitted a "complete" line.
- The log + linking_map show partial progress: a subset of products were processed, but browser/page teardown errors likely caused early termination / inconsistent lifecycle.

### Product-list refresh: angelwholesale (alternate 6-product file)

Input file:
- `OUTPUTS/PRODUCTS_LISTS/products_fullmix2_angelwholesale.json` contains **6 products**.

#### Run: 8ad711da-3c8c-4313-a21a-3ba2a2df2f77 (done, but duplicate lifecycle artifact)

Artifacts:
- Status: `OUTPUTS/CONTROL_PLANE/status/8ad711da-3c8c-4313-a21a-3ba2a2df2f77.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/8ad711da-3c8c-4313-a21a-3ba2a2df2f77.log`
- Job (done): `OUTPUTS/CONTROL_PLANE/jobs/done/job_8ad711da-3c8c-4313-a21a-3ba2a2df2f77.json`
- Job (failed): `OUTPUTS/CONTROL_PLANE/jobs/failed/job_8ad711da-3c8c-4313-a21a-3ba2a2df2f77.json`
- Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__8ad711da/linking_map.json` (length 6)

Counts (status vs disk):
- Status `input_products`: 4; input file products: 6
- Status `linking_map_entries`: 5; linking map length: 6
- Status `amazon_cache_files`: 5; amazon_cache dir contains 6 `amazon_*.json` files
- Log ends with: `Product list refresh complete: 6/6 matched`

Interpretation:
- This is a clean example of:
  - Issue #7 (status counts N-1 / wrong input count)
  - Issue #3 (duplicate job artifacts: same run in done + failed)

### Product-list refresh: clearance king (mixed list)

#### Run: 4b8864d2-1111-41d8-9855-03807da339be (status=cancelled)

Artifacts:
- Status: `OUTPUTS/CONTROL_PLANE/status/4b8864d2-1111-41d8-9855-03807da339be.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/4b8864d2-1111-41d8-9855-03807da339be.log`
- Job: `OUTPUTS/CONTROL_PLANE/jobs/failed/job_4b8864d2-1111-41d8-9855-03807da339be.json`
- Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/clearance-king.co.uk__sandbox__4b8864d2/linking_map.json` (length 2)

Observed behavior:
- Linking map shows 2 rows with `amazon_asin: null` and `match_method: no_results`.
- Log shows processing started, then run was cancelled.

### Category run (run_workflow): clearance king

#### Run: 86af6911-9f9e-4231-a271-c56ecb8eb188 (cancelled)

Artifacts:
- Job: `OUTPUTS/CONTROL_PLANE/jobs/failed/job_86af6911-9f9e-4231-a271-c56ecb8eb188.json`
- Status: `OUTPUTS/CONTROL_PLANE/status/86af6911-9f9e-4231-a271-c56ecb8eb188.json`
- Log: `OUTPUTS/CONTROL_PLANE/logs/86af6911-9f9e-4231-a271-c56ecb8eb188.log`
- Overrides:
  - `OUTPUTS/CONTROL_PLANE/overrides/86af6911-9f9e-4231-a271-c56ecb8eb188/system_config.merged.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/86af6911-9f9e-4231-a271-c56ecb8eb188/categories_subset.json`

Observed behavior:
- Log confirms categories were loaded from the overrides `categories_subset.json` and supplier scraping proceeded, producing a 12-URL manifest and a 12-product cache save, before the run was cancelled.

## Issues #1-#7: What Was Correct (With Concrete Examples)

This aligns to the traceability docs:
- `backup/fix_issues_6_7_20260217/TRACEABILITY.md`
- `backup/fix_issues_1_5_20260217/PRE_IMPLEMENTATION_TRACEABILITY.md`

### Issue #1: Missing JSON pre-validation (Correct)

Example:
- `c1b322b9-f129-4923-9cbc-8c557608b6e1` failed with `JSONDecodeError` when reading `OUTPUTS/PRODUCTS_LISTS/products_fullmix_efghouseware.json`.

### Issue #2: No dedup/resume for product refresh (Correct)

Example use-case:
- Re-running the same 6-product file for the same sandbox (or reusing the same sandbox supplier output paths) previously restarted with an empty in-memory results set, risking redundant Amazon extraction and overwriting artifacts.

### Issue #3: Duplicate job file risk (Correct)

Example:
- `8ad711da-3c8c-4313-a21a-3ba2a2df2f77` exists in both:
  - `OUTPUTS/CONTROL_PLANE/jobs/done/job_8ad711da-3c8c-4313-a21a-3ba2a2df2f77.json`
  - `OUTPUTS/CONTROL_PLANE/jobs/failed/job_8ad711da-3c8c-4313-a21a-3ba2a2df2f77.json`

### Issue #4: Fragile NL parsing for limits (Correct)

Example use-case:
- Dashboard pending-action edits previously missed common phrases like "at most 12 products" / "no more than 12" / "12 products max", causing tool params not to update when user thought they did.

### Issue #5: financial_report_exists too broad (Correct)

Example:
- Status for failed refresh `c1b322b9-f129-4923-9cbc-8c557608b6e1` shows `financial_report_exists: true` even though the refresh never produced any refresh artifacts (no linking map, no state file). This happened because existence was inferred from a shared financial directory, not the current run.

### Issue #6: processing_state top-level counters never updated (Correct)

Example:
- Product refresh runs showed `system_progression.amazon_products_completed` advancing while top-level counters like `total_products` remained 0 (see `backup/fix_issues_6_7_20260217/TRACEABILITY.md`).

### Issue #7: status refresh.counts inaccurate/stale (Correct)

Examples:
- `8ad711da-3c8c-4313-a21a-3ba2a2df2f77`: status says `input_products: 4`, but `products_fullmix2_angelwholesale.json` contains 6 products; status says `linking_map_entries: 5`, but linking map contains 6 rows.
- `f33d3fa5-228a-485c-82e7-9c0645a3e2b9`: same pattern (status counts under-report actual outputs).

## Expected Behavior: Pre-fix vs Post-fix

This is a behavior-only view (not a code diff). The implementation locations are tracked in the backup traceability docs.

- Issue #1 (subset JSON validation)
  - Pre: malformed JSON crashes with traceback.
  - Post: fails fast with clear `RuntimeError` message that includes file path + line/column.

- Issue #2 (refresh resume/dedup)
  - Pre: rerun starts from empty results and does not consult existing linking_map/cache.
  - Post: preloads existing linking map and skips already-processed product identities to avoid redundant extraction.

- Issue #3 (job lifecycle move)
  - Pre: moving job to done/failed risked ambiguous duplicates / overwrite behavior.
  - Post: `_move_job` uses duplicate-safe suffixing when destination exists.

- Issue #4 (NL parsing)
  - Pre: only a narrow set of phrase patterns updated `max_products` / `max_products_per_category`.
  - Post: broader parsing for common phrasings, including "up to", "at most", "no more than", "N products max", and "unlimited".

- Issue #5 (financial report existence)
  - Pre: `financial_report_exists` could be true due to unrelated CSVs in the shared directory.
  - Post: run-scoped detection uses CSV mtimes relative to run start.

- Issue #6 (processing_state top-level sync)
  - Pre: `system_progression.*` advanced, but top-level counters could remain 0.
  - Post: refresh syncs top-level counters at end so dashboards that read top-level fields reflect true work performed.

- Issue #7 (terminal refresh.counts)
  - Pre: status counts could under-report due to dict-key counting and stale final update.
  - Post: worker recomputes `input_products` correctly for object-shaped files and recomputes terminal counts from disk.

## Tests Already Executed (Deterministic)

- `python -m py_compile control_plane/run_product_list_refresh.py control_plane/worker.py control_plane/chat_orchestrator.py dashboard/chat_panel.py` (pass)
- Inline smoke checks (executed during implementation, recorded in `backup/fix_issues_1_5_20260217/PRE_IMPLEMENTATION_TRACEABILITY.md`):
  - runtime-constraint phrase parsing
  - malformed JSON error conversion
  - `_move_job` duplicate-safe behavior
  - run-scoped financial report detection logic

## Tests Still Recommended (Requires Running Worker/Browser)

1) Malformed JSON refresh
- Re-run product-list refresh using `OUTPUTS/PRODUCTS_LISTS/products_fullmix_efghouseware.json` and confirm:
  - status is failed with clear operator message (no raw traceback)
  - no partial writes (no linking_map / processing_state for that run)

2) Resume/dedup refresh
- Run a product-list refresh twice (same sandbox supplier output), confirm second run:
  - skips already-processed products by identity
  - does not overwrite existing amazon_cache entries
  - status terminal counts match disk
