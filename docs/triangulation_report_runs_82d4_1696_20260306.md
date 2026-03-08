# Triangulation Report: clearance-king (82d4...) + angelwholesale (1696...)

Date: 2026-03-06

This report triangulates two control-plane runs using the audit tool call log plus per-run job/status/overrides/logs and processing state.

Runs:
- clearance-king: `82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb`
- angelwholesale: `1696ab51-7366-4b1a-ab12-532eb0af0514`

## Evidence Index (File-Grounded)

Audit / intent:
- `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`
  - Line 154: `enqueue_run` for `82d4...` with `max_products=10`, `max_products_per_category=10`, `sandbox_suffix="sandbox"`
  - Line 155: `enqueue_run` for `1696...` with `max_products=6`, `max_products_per_category=6`, `sandbox_suffix="sandbox"`

Per-run artifacts:
- `OUTPUTS/CONTROL_PLANE/jobs/done/job_82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb.json`
- `OUTPUTS/CONTROL_PLANE/status/82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb.json`
- `OUTPUTS/CONTROL_PLANE/overrides/82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/logs/82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb.log`
- `OUTPUTS/CACHE/processing_states/clearance-king_co_uk__sandbox_processing_state.json`

- `OUTPUTS/CONTROL_PLANE/jobs/done/job_1696ab51-7366-4b1a-ab12-532eb0af0514.json`
- `OUTPUTS/CONTROL_PLANE/status/1696ab51-7366-4b1a-ab12-532eb0af0514.json`
- `OUTPUTS/CONTROL_PLANE/overrides/1696ab51-7366-4b1a-ab12-532eb0af0514/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/logs/1696ab51-7366-4b1a-ab12-532eb0af0514.log`
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox_processing_state.json`

Angel run cancellation markers:
- `OUTPUTS/CONTROL_PLANE/lock/cancel_1696ab51-7366-4b1a-ab12-532eb0af0514.flag`
- `OUTPUTS/CONTROL_PLANE/status/1696ab51-7366-4b1a-ab12-532eb0af0514.cancelled`

Debug logs (same run content, more verbose):
- `logs/debug/run_custom_clearance-king-co-uk__sandbox_20260306_021726.log`
- `logs/debug/run_custom_angelwholesale-co-uk__sandbox_20260306_022610.log`

## Run 1: clearance-king (82d4...)

### What was requested

Audit tool call shows a request to analyze 10 products with 2 category URLs, but the enqueue parameters were:
- `max_products=10`
- `max_products_per_category=10`
- `sandbox_suffix="sandbox"`

This implies a finite-mode interpretation of only one category needed: `ceil(10/10)=1`.

### What happened

The run status is `done` but performed zero category extraction.

Evidence:
- `OUTPUTS/CONTROL_PLANE/logs/82d4d6c5-24a0-42ee-a1eb-b78813e9ebeb.log` contains:
  - `FINITE MODE: 10 ... 10 ... = 1 categories needed`
  - `WORKFLOW START CURSOR: category_index=2 (pci=2, cursor=2, max=2)`
  - `ENUMERATING FROM CURSOR: 0 categories starting from index 2`
- `OUTPUTS/CACHE/processing_states/clearance-king_co_uk__sandbox_processing_state.json` contains:
  - `system_progression.persistent_category_index=2`
  - `session_resume_cursor=2`
  - `system_progression.total_categories=2`
  - `original_category_url` is unrelated to the two-category subset (indicates shared sandbox state reuse)

### Root cause

Shared sandbox state collision.

The run used `clearance-king.co.uk__sandbox` and reused the existing processing state file for that sandbox supplier. The persistent cursor (`pci=2`) was already at/after the end of the finite subset runlist (1 category), resulting in 0 categories enumerated.

### Minimal fixes

1) Stop using `sandbox_suffix="sandbox"` as a literal shared suffix; generate a run-scoped suffix for each run so processing state and caches are isolated per run.
2) If the user intent is "10 per category across 2 URLs", translate to `max_products=20` at enqueue time when `max_products == max_products_per_category` and URL count > 1.

## Run 2: angelwholesale (1696...)

### What was requested

Audit tool call shows "first 6 products of each" of 2 categories, but enqueue parameters were:
- `max_products=6`
- `max_products_per_category=6`
- `sandbox_suffix="sandbox"`

This implies a finite-mode interpretation of only one category needed: `ceil(6/6)=1`.

### What happened

The run status is `cancelled`.

Observed issues (all evidence-backed):

1) Cursor mismatch / 0-category enumeration in early workflow path
- `OUTPUTS/CONTROL_PLANE/logs/1696ab51-7366-4b1a-ab12-532eb0af0514.log` contains:
  - `START MODE ... pci=3, session_cursor=3`
  - `FINITE MODE: 6 ... 6 ... = 1 categories needed`
  - `ENUMERATING FROM CURSOR: 0 categories starting from index 3`

2) Manifest/worklist pollution: category URL treated as product URL
- `OUTPUTS/CACHE/processing_states/angelwholesale_co_uk__sandbox_processing_state.json` includes in `category_allowed_keys`:
  - `url:https://angelwholesale.co.uk/Category/Items-for-personalisation-wholesale`
- `OUTPUTS/CONTROL_PLANE/status/1696ab51-...json` last_log_lines show that same category URL being "extracted" as a product.

3) Page-load instability: repeated 10s `networkidle` timeouts
- `OUTPUTS/CONTROL_PLANE/status/1696ab51-...json` last_log_lines show repeated `Timeout 10000ms exceeded` while fetching product pages.

4) Non-atomic processing state write warning
- `OUTPUTS/CONTROL_PLANE/logs/1696ab51-...log` contains:
  - `WindowsSaveGuardian: Used non-atomic direct write for ...angelwholesale_co_uk__sandbox_processing_state.json`

5) Status artifact mismatch for cached products (fixed in dashboard)
- `OUTPUTS/CONTROL_PLANE/status/1696ab51-...json` reports `artifacts.cached_products_exists=false`
- But the run itself logs saving to `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox_products_cache.json` and the file exists.

### Root causes

Primary:
- Shared sandbox state collision (`angelwholesale.co.uk__sandbox`) causes resume cursor to be unrelated to the 2-URL subset list.

Secondary:
- URL harvesting includes non-product URLs (e.g., `/Category/...`) and those are later treated as product pages.
- Aggressive `networkidle` waits (10s) make item page fetch fragile on slower pages.
- Status artifact existence checks were using a path-mangling rule that broke `__sandbox` cache filenames.

### Minimal fixes

1) Same as clearance-king: isolate sandbox suffix per run and avoid literal `"sandbox"`.
2) Tighten product URL filtering to exclude `/Category/` URLs from "product" worklists.
3) Relax/adjust the item-page fetch strategy (timeouts/load state) and fix the confirmed `get_page_content()` Response-path return bug.
4) Keep status checks aligned with actual cache filenames (dashboard fix already applied).
5) Non-atomic direct-write warning: treat as a durability risk signal; investigate why atomic rename fell back (Windows lock/AV) but do not change behavior without reproducing.

## Cross-Run Synthesis (Why both failed differently)

Both runs used a shared sandbox suffix (`sandbox_suffix="sandbox"`) so they shared processing state and caches. The system then applied finite-mode category truncation (`max_products == max_products_per_category`) which often creates a 1-category runlist. When the shared resume cursor is already past that runlist, the run silently enumerates 0 categories and appears "done".

For angelwholesale, additional scraping instability and polluted worklists contributed to the observed timeouts and cancellation.

## Control Plane Worker Exit During Cancel (1696...)

This is separate from the supplier workflow itself: the control-plane worker process can exit if a job file disappears before the worker moves it from `jobs/running/` to `jobs/failed/`.

Evidence:
- User stack trace indicates `control_plane/worker.py` raised `FileNotFoundError` inside `_move_job()` while executing `os.replace(src, dst)`.
- In `control_plane/worker.py`, the cancel branch calls `_move_job(running_job_path, paths.jobs_failed)` immediately after writing status `cancelled`.

Root cause:
- `_move_job()` used `os.replace()` without handling `FileNotFoundError`. If the source file `OUTPUTS/CONTROL_PLANE/jobs/running/job_<run_id>.json` is already moved/deleted (e.g., by a concurrent worker instance or external action), the worker crashes and the terminal exits.

Fix implemented:
- `control_plane/worker.py`: `_move_job()` now catches `FileNotFoundError` and returns without crashing, keeping the worker loop alive.

## Fixes Already Implemented (Safe Scope)

Backups:
- `backup/sandbox_suffix_metricsfix_20260306/chat_orchestrator.py`
- `backup/sandbox_suffix_metricsfix_20260306/metrics_core.py`

Changes:
- `control_plane/chat_orchestrator.py`: treat `sandbox_suffix="sandbox"` as placeholder and auto-generate `sandbox__<run_id[:8]>`.
- `dashboard/metrics_core.py`: preserve `__suffix` when building cached-products filenames so `cached_products_exists` checks match real files.

Local verification run:
- `python -m py_compile dashboard/metrics_core.py control_plane/chat_orchestrator.py`

## Specialist Review Status

- Oracle feedback was incorporated into the above findings.
- Metis/Momus tasks repeatedly returned no messages due to stale timeouts, so no additional plan/critique was available to integrate.
