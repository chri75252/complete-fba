# REVERT TRACKING — dashboard_run_selector_20260416

## Purpose
Surgical dashboard-only implementation to add explicit sandbox `run_id` selection while preserving the existing financial report selector.

## Backup Location
`backup/dashboard_run_selector_20260416/`

## Planned Files

| File | Change Scope | Backup Source | Planned Validation | Status |
|---|---|---|---|---|
| `dashboard_legacy_streamlit/metrics_core.py` | Add additive helper to enumerate report-backed sandbox runs | `backup/dashboard_run_selector_20260416/metrics_core.py` | Python syntax + diagnostics | Backed up |
| `dashboard_v2_redesign/api.py` | Add run resolver helper, `/api/runs`, and optional `run_id` query threading to existing endpoints | `backup/dashboard_run_selector_20260416/api.py` | Python syntax + diagnostics + endpoint smoke checks | Backed up |
| `dashboard_v2_redesign/static/js/app.js` | Add run selector state, loaders, and minimal event wiring | `backup/dashboard_run_selector_20260416/app.js` | diagnostics + UI request-path smoke checks | Backed up |
| `dashboard_v2_redesign/templates/index.html` | Add one `Run ID` selector block | `backup/dashboard_run_selector_20260416/index.html` | diagnostics | Backed up |

## Non-Goals
- No edits to `tools/*`
- No edits to `run_custom_*.py`
- No changes to extraction workflow logic
- No redesign of dashboard layout beyond one new selector

## Restore Instructions
If rollback is needed, restore each file from the matching file under `backup/dashboard_run_selector_20260416/`.
