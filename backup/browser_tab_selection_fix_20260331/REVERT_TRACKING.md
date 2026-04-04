## Revert Tracking - browser_tab_selection_fix_20260331

Date: 2026-03-31
Scope: Surgical browser tab-selection hardening only

### Planned file edits

1) `utils/browser_manager.py`
- Change scope: Improve `get_page()` tab selection to avoid blind `context.pages[0]` reuse.
- Backup source: `backup/browser_tab_selection_fix_20260331/browser_manager.py.bak`
- Planned validation:
  - LSP diagnostics on edited file
  - Quick syntax check by Python compile
- Status: COMPLETED

### Validation results

- LSP diagnostics (`utils/browser_manager.py`): no errors/warnings; only existing hints.
- Python compile check: `python -m py_compile utils/browser_manager.py` passed.

### Rollback procedure

If rollback is needed:

1. Copy backup over edited file:
   - from `backup/browser_tab_selection_fix_20260331/browser_manager.py.bak`
   - to `utils/browser_manager.py`
2. Re-run diagnostics/compile checks.
