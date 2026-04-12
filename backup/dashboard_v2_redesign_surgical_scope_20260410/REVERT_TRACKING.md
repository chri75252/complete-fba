## Revert Tracking - Dashboard V2 Redesign Surgical Scope

- Date: 2026-04-10
- Scope: Fix supplier/report scoping drift + add sales-field toggle for Dashboard and Analysis views
- Backup root: `backup/dashboard_v2_redesign_surgical_scope_20260410`
- Change policy: Minimal changes only, confined to `dashboard_v2_redesign`

## Planned Files and Change Map

| File | Planned Change Scope | Backup Source | Validation Plan | Restore Command |
| --- | --- | --- | --- | --- |
| `dashboard_v2_redesign/api.py` | Add strict supplier financial-dir resolver used by metrics/reports/analysis endpoints; add `sales_field` request param; compute canonical `sales_value`; enforce selected report belongs to supplier report list | `backup/dashboard_v2_redesign_surgical_scope_20260410/api.py` | `python -m py_compile dashboard_v2_redesign/api.py` + targeted `lsp_diagnostics` | `copy "backup\dashboard_v2_redesign_surgical_scope_20260410\api.py" "dashboard_v2_redesign\api.py"` |
| `dashboard_v2_redesign/static/js/app.js` | Add sidebar sales-field toggle wiring; pass `sales_field` to API calls; use `sales_value` in dashboard/analysis displays; reset stale report selections on supplier/lineage change | `backup/dashboard_v2_redesign_surgical_scope_20260410/app.js` | `lsp_diagnostics` + manual code scan for changed selectors and fetch params | `copy "backup\dashboard_v2_redesign_surgical_scope_20260410\app.js" "dashboard_v2_redesign\static\js\app.js"` |
| `dashboard_v2_redesign/templates/index.html` | Add one sales-field checkbox under existing Financial Report selector in sidebar config | `backup/dashboard_v2_redesign_surgical_scope_20260410/index.html` | `lsp_diagnostics` + manual structure check for new element ids | `copy "backup\dashboard_v2_redesign_surgical_scope_20260410\index.html" "dashboard_v2_redesign\templates\index.html"` |

## Intended Outcome

1. Analysis and Operator report dropdowns stay supplier-scoped and no longer show cross-supplier CSV lists.
2. Supplier or lineage change clears stale selected report values.
3. A single sidebar toggle chooses which sales column drives Dashboard and Analysis sales calculations.

## Non-goals

- No edits to `dashboard_legacy_streamlit/metrics_core.py`
- No additional wholesaler dropdown in Analysis section
- No changes to core workflow/state-management scripts

## Rollback Procedure

1. Run restore commands from the table above for all modified files.
2. Re-run:
   - `python -m py_compile dashboard_v2_redesign/api.py`
   - `lsp_diagnostics` on all three restored files
3. Confirm dashboard launches and report dropdown behavior matches pre-change baseline.

## Execution Verification (This Pass)

- `python -m py_compile dashboard_v2_redesign/api.py` -> Passed.
- `lsp_diagnostics dashboard_v2_redesign/api.py` -> No errors; pre-existing hints only (unused imports/param).
- `lsp_diagnostics dashboard_v2_redesign/static/js/app.js` -> Not available in environment (missing `typescript-language-server`).
- `lsp_diagnostics dashboard_v2_redesign/templates/index.html` -> Not available in environment (missing `biome`).
