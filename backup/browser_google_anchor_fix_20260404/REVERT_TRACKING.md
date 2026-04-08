# REVERT_TRACKING

- Date: 2026-04-04
- Reason: Surgical browser tab selection fix using confirmed top-level Google tab anchor and removal of inline reconnection from get_page()
- Backup root: backup/browser_google_anchor_fix_20260404

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `utils/browser_manager.py` | `backup/browser_google_anchor_fix_20260404/browser_manager.py` | Completed |

## Planned Scope

### utils/browser_manager.py
- Remove inline reconnection from `get_page()` and keep health check as log-only.
- Replace generic first-http-page fallback with top-level Google-tab preference when exactly one Google page exists.
- Preserve exact requested URL reuse logic already present.
- Do not target subframes like `accounts.google.com`; selection remains based on top-level `page.url`.

## Validation

- `lsp_diagnostics` clean or only pre-existing hints on `utils/browser_manager.py`
- `python -m py_compile utils/browser_manager.py` passes

## Rollback

Copy `backup/browser_google_anchor_fix_20260404/browser_manager.py` back to `utils/browser_manager.py`.


## Validation Results

- `lsp_diagnostics` on `utils/browser_manager.py`: no errors/warnings; pre-existing hints only.
- `python -m py_compile utils/browser_manager.py`: passed.
