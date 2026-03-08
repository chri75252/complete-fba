# Plan: Sandbox Control Plane Stability + Scraping Resilience

Date: 2026-03-06

This plan addresses the failures observed in sandboxed control-plane runs (cancel crash, misreporting, suffix collisions) and the scraping reliability issues (timeouts + stuck page reuse). It also addresses the BrowserManager cleanup mismatch and the noisy shutdown tracebacks so they do not cause false failures.

Scope: control plane + dashboard + browser/scraper utilities.
Protected-file note: `tools/*` and `run_custom_*.py` are protected by policy; this plan prefers fixes in `control_plane/*`, `dashboard/*`, and `utils/*` first. Where a `tools/*` change is truly needed (scraper timeout loop), it is called out explicitly.

## Observed Issues (Definitions + Evidence)

1) Worker terminal exits on cancel (hard crash)
- Symptom: cancelling a run causes the control-plane worker process to exit with a traceback.
- Root cause: `control_plane/worker.py` moves a job file from `jobs/running/` to `jobs/failed/` via `_move_job()`; if the source file is already missing (race/double-finalization), `os.replace()` raises `FileNotFoundError`.
- Evidence: user traceback; code path in `control_plane/worker.py` cancel handling and `_move_job()`.

2) Cancelled runs appear as failed (status semantics)
- Symptom: cancelled jobs end up in `jobs_failed/` and look like failures.
- Root cause: cancel path moves jobs to `paths.jobs_failed` and artifact checks can treat missing outputs (expected on cancel) as failure.
- Evidence: `control_plane/worker.py` cancel branch + status finalization logic.

3) Sandbox runs process 0 categories (subset + resume cursor mismatch)
- Symptom: "FINITE MODE ... = 1 categories needed" then "ENUMERATING ... 0 categories".
- Root cause: shared `sandbox_suffix="sandbox"` created state/cursor collisions across runs; resume cursor points past the truncated subset list.
- Evidence: run logs for `82d4...` and `1696...` + processing states under `OUTPUTS/CACHE/processing_states/*__sandbox_processing_state.json`.

4) Sandbox used `run_custom_clearance_king - Copy.py` instead of `run_custom_clearance_king.py`
- Symptom: control-plane job payload used the "Copy" runner variant.
- Root cause: `_resolve_workflow_params()` in `control_plane/chat_orchestrator.py` selects the first runner that matches `key_base`/domain base; the system index lists the " - Copy" runner before the canonical runner, so it was chosen.
- Evidence: `OUTPUTS/CONTROL_PLANE/jobs/done/job_82d4...json` `runner_script` + `_resolve_workflow_params()` heuristic selection.

5) BrowserManager cleanup mismatch + noisy asyncio shutdown tracebacks
- Symptom: logs show `BrowserManager object has no attribute cleanup` and/or `RuntimeError: Event loop is closed` on shutdown.
- Root cause: some runners call `await browser_manager.cleanup()` but `utils/browser_manager.py` defines `close_browser()` and registers an atexit `run_global_cleanup()` that can run after the event loop is already closed.
- Evidence: runner call sites (e.g. `run_custom_clearance_king.py` / `run_custom_clearance_king - Copy.py`) and `utils/browser_manager.py` atexit registration.

6) Hung tab / timeout loop (supplier scraping)
- Symptom: repeated `Timeout 10000ms exceeded` while attempting to fetch many products.
- Root causes:
  - `tools/configurable_supplier_scraper.py:get_page_content()` uses `wait_for_load_state("networkidle", timeout=10000)`.
  - `utils/browser_manager.py:get_page()` reuses `context.pages[0]` (single persistent page), so a stuck page can persist across many URLs.
- Evidence: run logs for `1696...`, `tools/configurable_supplier_scraper.py`, and `utils/browser_manager.py`.

7) Worklist pollution: category URLs treated as product URLs
- Symptom: `/Category/...` URL appears in product extraction pipeline.
- Root cause: product URL harvesting does not strictly filter to product-detail URLs.
- Evidence: `OUTPUTS/manifests/angelwholesale.co.uk__sandbox/...manifest.json` + `category_allowed_keys` in processing state.

8) cached_products_exists false negative (status/UI)
- Symptom: status said cache missing while file existed.
- Root cause: dashboard path resolution mangled `__sandbox` into `--sandbox` when building cache filename.
- Evidence: `OUTPUTS/cached_products/angelwholesale-co-uk__sandbox_products_cache.json` exists while status artifact check reported false.

## Fixes (Surgical, Ordered)

### Fix A: Control-plane cancel stability + semantics (control_plane)

A1) Idempotent job moves (prevent worker crash)
- File: `control_plane/worker.py`
- Change: `_move_job()` must not crash on missing source; treat missing source as already finalized.
- Reference diff:

```diff
 def _move_job(src: Path, dst_dir: Path) -> Path:
     dst_dir.mkdir(parents=True, exist_ok=True)
     dst = dst_dir / src.name
     if dst.exists():
         suffix = int(time.time() * 1000)
         dst = dst_dir / f"{src.stem}__dup_{suffix}{src.suffix}"
-    os.replace(src, dst)
+    try:
+        os.replace(src, dst)
+    except FileNotFoundError:
+        return dst
     return dst
```

A2) Cancel should not go to `jobs_failed/`
- File: `control_plane/worker.py`
- Change: move cancelled jobs to a new `jobs_cancelled/` directory (or keep in place with a terminal marker), and ensure artifact checks short-circuit when `status.state == "cancelled"`.
- Reference snippet (illustrative):

```python
if _is_cancelled(run_id):
    status["state"] = "cancelled"
    write_json_atomic(status_path, status)
    _move_job(resolved_job_path, paths.jobs_cancelled)
    continue
```

A3) Cancel path must resolve current job location
- File: `control_plane/worker.py`
- Change: on cancel, attempt move from `pending/` first, else `running/`.

A4) Reduce false failures from shutdown noise
- File: `control_plane/worker.py`
- Change: expand `shutdown_artifacts` to include known atexit/asyncio cleanup noise and keep them non-fatal when they appear alone.

### Fix B: Sandbox namespace isolation (control_plane)

B1) Enforce per-run sandbox suffix
- File: `control_plane/chat_orchestrator.py`
- Change: treat `sandbox_suffix="sandbox"` as placeholder and generate `sandbox__<run_id[:8]>` for every new sandbox run.
- Outcome: processing state + caches do not collide between independent sandbox runs.

### Fix C: Runner selection (control_plane)

C1) Prefer canonical runner scripts over " - Copy" variants
- File: `control_plane/chat_orchestrator.py` (`_resolve_workflow_params`)
- Change: when multiple runner candidates match, select the non-copy variant deterministically.
- Reference diff:

```diff
-runner = next((r for r in runners if key_base in r), None)
+candidates = [r for r in runners if key_base in r]
+runner = _pick_preferred_runner(candidates)
```

Verification: `clearance-king.co.uk` resolves to `run_custom_clearance_king.py`.

### Fix D: BrowserManager cleanup mismatch (utils + control_plane)

D1) Provide a `cleanup()` alias on BrowserManager
- File: `utils/browser_manager.py`
- Change: add `async def cleanup(self): await self.close_browser()`.
- Why: avoids touching protected `run_custom_*.py` while ensuring any runner that calls `.cleanup()` does not raise.

D2) Keep shutdown tracebacks from flipping job status
- File: `control_plane/worker.py`
- Change: treat `AttributeError: ... cleanup` and known asyncio teardown tracebacks as non-fatal artifacts when returncode==0.

### Fix E: Hung tab timeout loop (tools + utils)

E1) Break the stuck-page chain after repeated timeouts
- File: `tools/configurable_supplier_scraper.py` (protected)
- Change: in the retry loop, after N timeouts (e.g., 3), close the page used for scraping so the next product forces a fresh page.
- Reference snippet (illustrative):

```python
timeout_failures = 0
for attempt in range(max_retries):
    try:
        html = await self.get_page_content(url)
        timeout_failures = 0
        break
    except PlaywrightTimeoutError:
        timeout_failures += 1
        if timeout_failures >= 3 and self.use_browser_manager:
            try:
                page = await self.browser_manager.get_page(reuse_existing=True)
                await page.close()
            except Exception:
                pass
            timeout_failures = 0
        await asyncio.sleep(backoff)
```

E2) Replace `networkidle` 10s with a more resilient strategy
- File: `tools/configurable_supplier_scraper.py` (protected)
- Change: prefer `domcontentloaded` + longer timeout for supplier pages, or make the timeout configurable per supplier.

E3) Fix confirmed `get_page_content()` Response-path return bug
- File: `tools/configurable_supplier_scraper.py` (protected)
- Change: ensure both Response and non-Response navigation paths return `page.content()` on success.

### Fix F: Worklist pollution filter (tools)

F1) Filter out `/Category/` URLs from product URL harvesting
- File: `tools/configurable_supplier_scraper.py` (protected) or the specific URL-collection helper it uses
- Change: only accept URLs matching a product-detail pattern (supplier-specific or generic rules), and explicitly reject `/Category/`.

### Fix G: cached_products_exists status correctness (dashboard)

G1) Preserve `__suffix` when building cache filenames
- File: `dashboard/metrics_core.py`
- Change: keep `__sandbox` intact when translating dotted domain to hyphenated filename.

## Verification Checklist (No Claims Without Proof)

1) Cancel behavior:
- Cancel while job is in `jobs/pending/` and while in `jobs/running/`.
- Expected: worker stays alive; job ends `cancelled`; no `FileNotFoundError`.

2) Runner selection:
- Enqueue sandbox run for `clearance-king.co.uk`.
- Expected: job payload `runner_script` is `run_custom_clearance_king.py` (not " - Copy").

3) Suffix isolation:
- Run 2 sandbox jobs back-to-back.
- Expected: distinct sandbox supplier names (`domain__sandbox__<id>`) and distinct processing state paths.

4) Cleanup mismatch:
- Run any runner that calls `.cleanup()`.
- Expected: no `AttributeError` for missing cleanup.

5) Timeout loop:
- On a category with many products, ensure timeouts do not repeat indefinitely on the same stuck page.
