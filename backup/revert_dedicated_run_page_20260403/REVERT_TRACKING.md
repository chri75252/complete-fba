# REVERT_TRACKING

- Date: 2026-04-03
- Reason: Revert dedicated run page feature that caused product-list-refresh runs to crash after first product
- Backup root: backup/revert_dedicated_run_page_20260403
- Root cause: `context.new_page()` creates a CDP-injected tab that Chrome's internal processes close mid-run. Auth navigations succeed (within seconds) but the page is found closed by the time the scraper navigates to the first product. Main runners that reuse existing tabs (not CDP-created ones) do not have this issue.

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `control_plane/run_product_list_refresh.py` | `backup/revert_dedicated_run_page_20260403/run_product_list_refresh.py` | Completed |
| `utils/browser_manager.py` | `backup/revert_dedicated_run_page_20260403/browser_manager.py` | Completed |

## Changes Made

### control_plane/run_product_list_refresh.py

**Reverted `_ensure_playwright_page`** — removed `run_id` parameter and `ensure_run_page()` call. Function now matches the pre-Apr-1 behavior: calls `mgr.get_page(reuse_existing=True)` to reuse existing tabs, identical to how the main runner scripts work.

**Removed `_release_playwright_page`** — this function called `mgr.release_run_page(run_id)` which is no longer needed since no dedicated page is created.

**Fixed call site at ~line 405** — removed `run_id=run_id` argument from `_ensure_playwright_page()` call.

**Fixed cleanup at ~line 709** — replaced `_release_playwright_page(run_id)` with a comment, since page lifecycle is now managed by BrowserManager singleton.

## Evidence Trail

- `backup/browser_run_scoped_tab_20260401/REVERT_TRACKING.md` — introduced the dedicated run page feature
- `backup/browser_run_scoped_tab_completion_20260402/REVERT_TRACKING.md` — explicitly documented (line 36): "dedicated run page became closed mid-run" as a known downstream issue
- Three consecutive runs on Apr 3 (12:52, 15:21, 15:23) all showed identical failure: page created, auth succeeded, first product navigation killed the page
- Main runner `run_custom_clearance_king.py` (15:44 Apr 3) ran successfully using existing tab reuse pattern

## Validation Evidence

- `python -m py_compile control_plane/run_product_list_refresh.py` passed.

## To Revert (restore dedicated run page feature)

```
cp backup/revert_dedicated_run_page_20260403/run_product_list_refresh.py control_plane/run_product_list_refresh.py
```

### utils/browser_manager.py

**Removed destructive health-check-restart from `get_page()`** — The `get_page()` method previously called `verify_connection_health()` and, on failure, triggered `restart_browser_gracefully()` which calls `close_browser()` → destroys the entire CDP context. This was the kill shot when Chrome was memory-stressed (2693MB) but still functional. The health check now logs only and does not restart. The scraper's own retry loop handles transient navigation failures.

Evidence: Run at 16:06 Apr 3 showed `Browser connection not established` → restart → `BrowserContext.new_page: Target page, context or browser has been closed`. The main runner (clearance-king at 15:44) also retried the first product but the health check passed — difference was Chrome memory state, not code path.

## Note on dead code

The `ensure_run_page()` and `release_run_page()` methods remain in `utils/browser_manager.py` as dead code (no callers). They can be removed in a future cleanup pass but are harmless.
