# REVERT_TRACKING

- Date: 2026-04-03
- Reason: Browser connection dies after first product navigation in product-list-refresh runs. Root cause: scraper constructed without browser_manager (singleton fallback) + no reconnection when CDP connection drops.
- Backup root: backup/browser_connection_stability_20260403

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `control_plane/run_product_list_refresh.py` | `backup/browser_connection_stability_20260403/run_product_list_refresh.py` | Completed |
| `utils/browser_manager.py` | `backup/browser_connection_stability_20260403/browser_manager.py` | Completed |

## Root Cause Analysis

In 8 consecutive runs on Apr 3, the browser CDP connection dropped after the first product navigation in every single run. The scraper was constructed as `ConfigurableSupplierScraper()` (no browser_manager), causing it to use the `BrowserManager.get_instance()` singleton fallback on every `get_page_content()` call. Meanwhile, the main runner scripts construct the scraper with `ConfigurableSupplierScraper(browser_manager=browser_manager)` (direct reference) and never experience this failure.

Additionally, when the connection dropped, `get_page()` had no recovery mechanism — it logged a warning and continued, guaranteeing every subsequent product fetch would also fail. The run would cycle through all 1776 products hitting "Browser connection not established" on each one.

## Changes Made

### control_plane/run_product_list_refresh.py

**Fix 1 — Pass browser_manager to the scraper.**
- Changed `scraper = ConfigurableSupplierScraper()` (line 385) to a deferred initialization.
- Scraper is now created INSIDE `async def run()` AFTER `_ensure_playwright_page()` connects the browser:
  ```python
  scraper = ConfigurableSupplierScraper(browser_manager=BrowserManager.get_instance())
  ```
- This aligns with how main runners (`run_custom_clearance_king.py`, `run_custom_efghousewares-co-uk.py`) construct the scraper.
- The scraper now uses `self.browser_manager.get_page()` (direct path, logs "Using BrowserManager page") instead of the singleton fallback (which logged "Using BrowserManager singleton page").

### utils/browser_manager.py

**Fix 2 — Add browser reconnection fallback in `get_page()`.**
- When `verify_connection_health()` returns False, `get_page()` now attempts `launch_browser()` to reconnect to Chrome via CDP.
- If reconnection succeeds, the run continues with a fresh browser context.
- If reconnection fails, an error is logged but the system continues (caller's retry loop handles it).
- This only triggers when the connection is already dead — no impact on healthy connections.

**Fix 2b — Clean up stale Playwright on reconnect.**
- Added cleanup of old `self.playwright` instance in `launch_browser()` before creating a new one.
- Prevents Playwright instance leaks during reconnection.

## Impact Assessment

- **Main runner scripts**: Not affected. They already pass `browser_manager` to the scraper. The reconnection fallback only triggers when the connection is dead (never happens with healthy Chrome).
- **Product-list refresh (fresh + resume)**: Fixed. Scraper gets direct browser_manager. Reconnection provides safety net.
- **Category workflows via chat**: Use main runner scripts. Not affected.
- **Same-chat interrupt + resume**: Same `run_product_list_refresh.py` code path. Fixed.

## Validation Evidence

- `python -m py_compile control_plane/run_product_list_refresh.py utils/browser_manager.py` passed.

## To Revert

```
cp backup/browser_connection_stability_20260403/run_product_list_refresh.py control_plane/run_product_list_refresh.py
cp backup/browser_connection_stability_20260403/browser_manager.py utils/browser_manager.py
```
