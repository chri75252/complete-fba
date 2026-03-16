# Revert Tracking - workflow_followup_fixes_20260313

Backup root: `backup/workflow_followup_fixes_20260313/`
Created for surgical implementation of `.sisyphus/plans/post-implementation-followup-fixes-20260313.md`.

| File | Planned scope | Validation plan | Restore source |
|---|---|---|---|
| `control_plane/run_product_list_refresh.py` | Add canonical Amazon cache bridge, early sandbox cache write, correct `match_method`, financial trigger, debug-log mirror | LSP diagnostics, targeted refresh run, artifact triangulation | `backup/workflow_followup_fixes_20260313/control_plane/run_product_list_refresh.py` |
| `control_plane/worker.py` | Append same-run logs and add attempt delimiter | LSP diagnostics, repeated-run log inspection | `backup/workflow_followup_fixes_20260313/control_plane/worker.py` |
| `dashboard_legacy_streamlit/metrics_core.py` | Add latest-sandbox supplier discovery helper | LSP diagnostics, API lineage test, dashboard check | `backup/workflow_followup_fixes_20260313/dashboard_legacy_streamlit/metrics_core.py` |
| `dashboard/api.py` | Add lineage-aware metrics/validation behavior and bounded transcript tool execution persistence | LSP diagnostics, API tests, transcript file inspection | `backup/workflow_followup_fixes_20260313/dashboard/api.py` |
| `dashboard/templates/index.html` | Add lineage selector and Run Validation button | Browser verification in dashboard | `backup/workflow_followup_fixes_20260313/dashboard/templates/index.html` |
| `dashboard/static/js/app.js` | Wire lineage selector, effective supplier display, validation action | Browser verification in dashboard | `backup/workflow_followup_fixes_20260313/dashboard/static/js/app.js` |

Restore rule: if any edited section produces negative output, restore only the affected file from the backup path above and re-run the corresponding validation step.
