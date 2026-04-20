# REVERT TRACKING — analysis_controls_surgical_20260418

Date: 2026-04-18
Scope: Surgical continuation of interrupted analysis cancel/lock frontend wiring.

## Planned files

1. `dashboard_v2_redesign/static/js/app.js`
   - Intended scope:
     - Add `window.cancelAnalysis()` implementation.
     - Add analysis controls lock/unlock helpers.
     - Toggle cancel button visibility during analysis fetch lifecycle.
     - Handle HTTP `409` (already running) and `499` (cancelled) explicitly.
   - Planned validation:
     - LSP diagnostics on `app.js`.
     - Ensure no missing symbol/function references around `window.cancelAnalysis`.
   - Backup restore source path:
     - `backup/analysis_controls_surgical_20260418/app.js`
   - Validation status: PENDING

2. `dashboard_v2_redesign/templates/index.html`
   - Intended scope:
     - Add stable id for analysis Apply button for deterministic lock/unlock behavior from JS.
   - Planned validation:
     - LSP diagnostics on `index.html` (if available) and smoke-read for valid structure.
   - Backup restore source path:
     - `backup/analysis_controls_surgical_20260418/index.html`
   - Validation status: PENDING

3. `dashboard_v2_redesign/api.py`
   - Intended scope:
     - Preserve already-added single active analysis guard.
     - Complete probabilistic classifier integration and ensure cleanup remains correct.
     - Surface classifier fields needed by dashboard/export flow.
   - Planned validation:
     - Python compile check.
     - LSP diagnostics on `api.py`.
   - Backup restore source path:
     - `backup/analysis_controls_surgical_20260418/api.py`
   - Validation status: PENDING

4. `tools/fba_report_filter.py`
   - Intended scope:
     - Reconcile partially implemented probabilistic integration with final plan.
     - Preserve legacy fallback and expand tier handling.
   - Planned validation:
     - Python compile check.
     - LSP diagnostics on `fba_report_filter.py`.
   - Backup restore source path:
     - `backup/analysis_controls_surgical_20260418/fba_report_filter.py`
   - Validation status: PENDING

5. `tools/_pack_extraction.py`
   - Intended scope:
     - New deterministic pack extraction helper from locked plan.
   - Planned validation:
     - Python compile check.
   - Backup restore source path:
     - NEW FILE — rollback by deletion.
   - Validation status: PENDING

6. `tools/_probabilistic_matcher_core.py`
   - Intended scope:
     - New pinned probabilistic matcher core copied from approved prototype.
   - Planned validation:
     - Python compile check.
   - Backup restore source path:
     - NEW FILE — rollback by deletion.
   - Validation status: PENDING

7. `tools/fba_probabilistic_classifier.py`
   - Intended scope:
     - New report-keyed/thread-local wrapper implementing T1_A/T1_B logic.
   - Planned validation:
     - Python compile check.
     - Import smoke check through `tools.fba_report_filter` / `dashboard_v2_redesign.api`.
   - Backup restore source path:
     - NEW FILE — rollback by deletion.
   - Validation status: PENDING

## Non-goals

- No changes to protected `tools/*` workflow engines/runners.
- No refactor of analysis backend request model.
- No classifier-logic changes.
