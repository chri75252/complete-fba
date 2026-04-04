## Revert Tracking - browser_run_scoped_tab_completion_20260402

Date: 2026-04-02
Scope: Complete product-list run dedicated-tab fix with explicit activation logging and removal of one invalid call.

### Planned files

1) `utils/browser_manager.py`
- Change scope: Add explicit dedicated-run-page activation/reuse logging with page counts and URLs.
- Backup source: `backup/browser_run_scoped_tab_completion_20260402/browser_manager.py.bak`
- Planned validation:
  - LSP diagnostics clean
  - Python compile check passes
- Status: COMPLETED

2) `control_plane/run_product_list_refresh.py`
- Change scope: Add startup run-page bind logging and remove invalid `scraper._ensure_browser()` call.
- Backup source: `backup/browser_run_scoped_tab_completion_20260402/run_product_list_refresh.py.bak`
- Planned validation:
  - LSP diagnostics clean
  - Python compile check passes
  - Runtime log shows dedicated run-page marker during test launch
- Status: COMPLETED

### Validation results

- `lsp_diagnostics` on `utils/browser_manager.py`: no errors/warnings; existing hints only.
- `lsp_diagnostics` on `control_plane/run_product_list_refresh.py`: no errors/warnings; existing hints only.
- `python -m py_compile "utils/browser_manager.py" "control_plane/run_product_list_refresh.py"`: passed.
- Runtime smoke test launched via `python -m control_plane.run_product_list_refresh` with one-product dry-run job.
- Verified dedicated run tab activation in runtime output:
  - `Created dedicated run page for tabtest01-...`
  - `RUN_PAGE_BIND run_id=tabtest01-... total_pages=4 page_url=about:blank`
  - `Reusing dedicated run page for tabtest01-... via get_page(...)`
- Additional follow-on issue discovered during smoke test:
  - dedicated run page became closed mid-run, causing fallback to `Reusing existing page in persistent context` and later Amazon extractor page-closed errors.
  - This is recorded as a new downstream issue, not evidence that the run-tab activation fix failed.

### Rollback procedure

1. Restore `utils/browser_manager.py` from `backup/browser_run_scoped_tab_completion_20260402/browser_manager.py.bak`.
2. Restore `control_plane/run_product_list_refresh.py` from `backup/browser_run_scoped_tab_completion_20260402/run_product_list_refresh.py.bak`.
3. Re-run diagnostics and compile checks.
