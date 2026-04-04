## Revert Tracking - browser_run_scoped_tab_20260401

Date: 2026-04-01
Scope: Product-list run-scoped dedicated tab creation and reuse.

### Planned files

1) `utils/browser_manager.py`
- Change scope: Add run-scoped page lifecycle helpers and prefer dedicated run page in `get_page()`.
- Backup source: `backup/browser_run_scoped_tab_20260401/browser_manager.py.bak`
- Planned validation:
  - LSP diagnostics clean on file
  - `python -m py_compile` passes
- Status: COMPLETED

2) `control_plane/run_product_list_refresh.py`
- Change scope: Request dedicated run page at start, release run page at shutdown/finalization.
- Backup source: `backup/browser_run_scoped_tab_20260401/run_product_list_refresh.py.bak`
- Planned validation:
  - LSP diagnostics clean on file
  - `python -m py_compile` passes
- Status: COMPLETED

### Validation results

- `lsp_diagnostics` on `utils/browser_manager.py`: no errors or warnings (existing hints only).
- `lsp_diagnostics` on `control_plane/run_product_list_refresh.py`: no errors or warnings (existing hints only).
- `python -m py_compile "utils/browser_manager.py" "control_plane/run_product_list_refresh.py"`: passed.

### Rollback procedure

1. Restore `utils/browser_manager.py` from `backup/browser_run_scoped_tab_20260401/browser_manager.py.bak`.
2. Restore `control_plane/run_product_list_refresh.py` from `backup/browser_run_scoped_tab_20260401/run_product_list_refresh.py.bak`.
3. Re-run diagnostics and compile checks.
