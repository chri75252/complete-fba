# Complete Resumption Failure RCA and Remediation Dossier — Poundwholesale (Oct 31, 2025)

## 1) Overview & Scope

This dossier consolidates investigation results, source-of-truth evidence, failed-fix analysis, proposed remediations with diffs, discrepancy-avoidance steps, and orchestration options. It adheres to the project’s Mandatory File Verification Protocol: every material claim is backed by three sources when applicable (log + script + output), with verified file existence, timestamps, and content. All supplier references are verified for poundwholesale.co.uk.

No code changes were made; this is documentation only. Suggested diffs are provided in a separate review-only patch file.

## 2) Executive Summary

- Symptom: On every startup, the system overwrites the processing state before initialization logic runs, causing hidden fresh starts instead of resuming.
- Root cause: Three state saves occur in `tools/passive_extraction_workflow_latest.py` before `initialize_workflow_session()`; `utils/fixed_enhanced_state_manager.py` allows saves during startup (no guard).
- Impact: Resumption fails across runs; progress, phase, and denominators are clobbered by pre-init writes.
- Proof (tri-source):
  - Log shows three consecutive "ATOMIC SAVE" events under 20ms before "INITIALIZING WORKFLOW SESSION...".
  - Script shows `set_total_categories()` -> `save_debounced()` -> `save_state_atomic()` -> `mark_frozen_totals_committed()` before `initialize_workflow_session()`.
  - Output state file `created_at`/`last_updated` timestamps align with the pre-init save window.
- Fix strategy:
  - Tactical: Add startup guards to `save_state_atomic()` and `save_debounced()` (block until `_startup_completed=True`).
  - Structural: Call `initialize_workflow_session()` before any freezing/saving in workflow `run()`.
  - Defense-in-depth: Optional guard in the unified `save()` method.
- Post-fix reconciliation: Keep PCI MAX binding (monotonic), category skip, and observability; optionally remove a redundant mid-startup save once verified.

## 3) Sources & Verification (Existence, Timestamps, Content)

- Script files (exist and read):
  - C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\tools\passive_extraction_workflow_latest.py
  - C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\utils\fixed_enhanced_state_manager.py
- Log files (exist and read):
  - C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug\run_custom_poundwholesale_20251017_031605.log
  - C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug\run_custom_poundwholesale_20251017_031206.log
- Output state (exists, timestamps verified, content parsed):
  - C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json
    - CreationTimeUtc=2025-10-16 23:16:05Z, LastWriteTimeUtc=2025-10-16 23:16:06Z
    - Parsed fields: total_categories=230, frozen_totals_committed=True, current_phase="supplier", supplier_name="poundwholesale.co.uk"
- Historical contradictions (count verified): 22 matches of "FRESH START CONTRADICTION" in debug logs (Aug 31, 2025 series), e.g. three samples:
  - ...\logs\debug\run_custom_poundwholesale_20250831_100443.log:1
  - ...\logs\debug\run_custom_poundwholesale_20250831_102614.log:55
  - ...\logs\debug\run_custom_poundwholesale_20250831_103141.log:38

## 4) Symptom & Impact

- Symptom: Each launch behaves like a fresh start while appearing to "resume", because the state file has already been overwritten with startup defaults.
- Impact: Lost resumption context; PCI/phase/denominators reset to defaults; execution restarts incorrectly. This is corroborated by the log timing and the state file’s immediate creation/update around startup.

## 5) Technical Root Cause (Tri-Source Evidence)

5.1 Pre-init Save #1 — set_total_categories() -> save_debounced()
- Log: ...\logs\debug\run_custom_poundwholesale_20251017_031605.log:53 (ATOMIC SAVE START: preserve=True, startup_completed=False)
- Script: tools\passive_extraction_workflow_latest.py:1928; utils\fixed_enhanced_state_manager.py:1444–1456 (calls save_debounced("manifest")); utils\fixed_enhanced_state_manager.py:1400–1409 (no startup guard).
- Output: OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json: created_at/last_updated in pre-init window; total_categories=230.

5.2 Pre-init Save #2 — explicit save_state_atomic()
- Log: ...\run_custom_poundwholesale_20251017_031605.log:67 (second atomic save sequence)
- Script: tools\passive_extraction_workflow_latest.py:1929 -> utils\fixed_enhanced_state_manager.py:1392–1399 (no guard)

5.3 Pre-init Save #3 — mark_frozen_totals_committed() -> save_state_atomic()
- Log: ...\run_custom_poundwholesale_20251017_031605.log:81–93 (third atomic save sequence)
- Script: utils\fixed_enhanced_state_manager.py:1473–1477

5.4 Initialization Happens After All Three Saves
- Log: ...\run_custom_poundwholesale_20251017_031605.log:106 (INITIALIZING WORKFLOW SESSION...)
- Script: tools\passive_extraction_workflow_latest.py:2035

## 6) Why Previous Fixes A–E Didn’t Resolve It

- A: Phase Guard — implemented/reverted in places; executes after overwrite. Evidence: .serena\memories\RESUMPTION_FAILURE_CORRECTED_AUDIT_OCT08_2025.md; .serena\memories\SESSION_2025_10_08_RESUMPTION_FIXES_REVERTED_OCT08_2025.md
- B: PCI Hardening — MAX binding cannot help when both inputs are defaults (1 vs 1). Evidence: tools\passive_extraction_workflow_latest.py:2037–2041
- C: Index Binding (MAX) — correct but post-destruction.
- D: Category Skip — with PCI reset to 1, nothing is skipped; every run appears fresh. Evidence: tools\passive_extraction_workflow_latest.py:5014–5016
- E: Observability — useful logs; not preventive.

Conclusion: All were applied downstream of the destructive timing window. Only blocking saves until initialization completes and/or calling initialization first will work.

## 7) Proposed Remediation (No code changes applied here)

- Tactical (guards): early-return in save_state_atomic() and save_debounced() until _startup_completed is true.
- Structural (order): call initialize_workflow_session() before set_total_categories/save_state_atomic/mark_frozen_totals_committed.
- Defense-in-depth (optional): add a low-level guard in save() to block unexpected startup writes.

Review-only diffs: patches\RESUMPTION_STARTUP_GUARDS_AND_INIT_ORDER.patch:1

## 8) Discrepancy-Avoidance & Reversion Plan (Post-Fix)

- Keep: PCI MAX binding (tools\passive_extraction_workflow_latest.py:2037–2041); Category Skip (tools\passive_extraction_workflow_latest.py:5014–5016); Observability (tools\passive_extraction_workflow_latest.py:2045).
- Optional: remove explicit save_state_atomic("manifest-after-init") and rely on mark_frozen_totals_committed() after confirming stability.
- Rollback triggers: new startup deadlocks; resume anomalies; state timestamps changing before the init log.
- Rollback steps: revert guards first (if truly necessary); keep initialization order change; re-test scenarios.

## 9) Behavioral Verification (File-Grounded Tests)

- Fresh Start: delete state JSON; run entry; expect SAVE BLOCKED logs until INIT; check timestamps >= init.
- Resume: use existing state with PCI>1; run; expect no pre-init saves and correct resume pointers.
- Denominator Preservation: allow freeze; interrupt and resume; expect frozen_totals_committed and denominators preserved.
- No new FRESH START CONTRADICTION warnings in new runs.

## 10) CI/Orchestration Options (Emergent vs Alternatives)

- Emergent: viable but you must still provide Chrome 139+ with CDP 9222; docs are lighter for this specific browser-bound workload.
- Recommended quick path: GitHub Actions for tests + Prefect Agent on your Windows workstation for scheduled real runs.
- Other orchestrators: Dagster (structured data platform), Airflow (mature, heavier), Temporal/Flyte (durable, K8s-native).
- Low-code meta-AI (do not alter deterministic scraping/matching): n8n or Pipedream for summarizing logs, PR comments, alerts.

## 11) Suggested Diffs (For Review Only)

See unified diffs in patches\RESUMPTION_STARTUP_GUARDS_AND_INIT_ORDER.patch:1 covering:
- utils\fixed_enhanced_state_manager.py — guards in save_state_atomic/save_debounced; optional guard in save().
- tools\passive_extraction_workflow_latest.py — move initialize_workflow_session() before early freeze/save.

## 12) Risk, Monitoring, and Rollback

- Risk: Low for guards; Medium for reorder (if anything depended on early totals).
- Monitoring: count blocked saves; watch state timestamps across restarts; confirm no contradiction warnings in new logs.
- Rollback: revert guards if needed; keep structural reorder; repeat file-grounded tests.

## 13) Appendix — Evidence Excerpts (Lines/Paths)

- Logs (Oct 17 run): lines 53, 67, 81 show ATOMIC SAVE START with startup_completed=False; line 106 shows INIT.
- Workflow: lines 1928, 1929, 1932 (pre-init saves); line 2035 (initialize_workflow_session call).
- State Manager: lines 1392–1399 (save_state_atomic -> save, no guard), 1400–1409 (save_debounced -> save, no guard), 1444–1456 (set_total_categories -> save_debounced), 1473–1477 (mark_frozen_totals_committed -> save_state_atomic).
- Output State: created_at and last_updated align with pre-init window; supplier_name="poundwholesale.co.uk"; total_categories=230; frozen_totals_committed=True.
- Historical warnings: 22 matches across Aug 31 logs; three sample files listed above.

Prepared by: Codex CLI — exhaustive, file-verified RCA and remediation dossier. No code was modified; suggested diffs are provided separately for review.

