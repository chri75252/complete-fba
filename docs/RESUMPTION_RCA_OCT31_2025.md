# Resumption Failure RCA — Poundwholesale (Oct 31, 2025)

## Executive Summary

- Problem: On startup, three state writes occur before initialization, overwriting prior state and causing hidden fresh starts instead of resuming.
- Root Cause: In `tools/passive_extraction_workflow_latest.py`, totals are frozen and saved before `initialize_workflow_session()`. In `utils/fixed_enhanced_state_manager.py`, `save_state_atomic()` and `save_debounced()` allow writes during startup (no guard).
- Impact: Resumption fails; prior state is replaced at launch. Verified by millisecond logs and state file timestamps.
- Recommendation:
  - Tactical: Add startup guards in `save_state_atomic()` and `save_debounced()` to early-return until `_startup_completed` is true.
  - Structural: Call `initialize_workflow_session()` before any early freeze/save operations.
  - Defense-in-depth: Optional low-level guard in `save()`.
  - Reconciliation: Keep MAX binding, category skip, and observability; optionally remove redundant mid-startup save to reduce I/O after fixes.

## Which Prior Report Was More Accurate

- More accurate: Report 1
- Why: It matches the repository’s current code and logs precisely and uses the actual flag name (`_startup_completed`) present in `utils/fixed_enhanced_state_manager.py`. It also correctly identifies all three pre-init save sites and their ordering, matching both code and logs.

## File Verification Protocol (Performed)

- Verified existence and read contents:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\tools\passive_extraction_workflow_latest.py`
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\utils\fixed_enhanced_state_manager.py`
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\logs\debug\run_custom_poundwholesale_20251017_031605.log`
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json`
- Checked timestamps:
  - State: `CreationTimeUtc=2025-10-16 23:16:05Z`, `LastWriteTimeUtc=2025-10-16 23:16:06Z`.
- Supplier correctness: poundwholesale.co.uk confirmed in both logs and state JSON.

## Attempted Fixes From Memories (Already Tried) and Why They Failed

- Fix A (Phase Guard): Implemented in places; later flagged as mis-placed → even reverted in one session. Does not prevent pre-init overwrites because it runs after state destruction.
  - Evidence: `.serena\memories\RESUMPTION_FAILURE_CORRECTED_AUDIT_OCT08_2025.md`, `.serena\memories\SESSION_2025_10_08_RESUMPTION_FIXES_REVERTED_OCT08_2025.md`.
- Fix B (PCI Hardening): MAX logic present but evaluates after state reset (1 vs 1), so ineffective.
  - Evidence: `tools\passive_extraction_workflow_latest.py:2037–2041`.
- Fix C (Index Binding): Present (“FIX C”) but post-destruction; no effect.
  - Evidence: `tools\passive_extraction_workflow_latest.py:2037–2041`.
- Fix D (Category Skip): Present; with PCI reset to 1, nothing to skip.
  - Evidence: `tools\passive_extraction_workflow_latest.py:5014–5016`.
- Fix E (Observability): Present and useful; not preventive.

## Tri‑Source Evidence for Root Cause (Log + Script + Output)

1) Three atomic saves occur before initialization
- Log:
  - `...\logs\debug\run_custom_poundwholesale_20251017_031605.log:53` → `💾 ATOMIC SAVE START...`
  - `...\run_custom_poundwholesale_20251017_031605.log:67` → `💾 ATOMIC SAVE START...`
  - `...\run_custom_poundwholesale_20251017_031605.log:81` → `💾 ATOMIC SAVE START...`
  - `...\run_custom_poundwholesale_20251017_031605.log:106` → `🚀 INITIALIZING WORKFLOW SESSION...`
- Script:
  - `...\tools\passive_extraction_workflow_latest.py:1928` (set_total_categories)
  - `...\tools\passive_extraction_workflow_latest.py:1929` (save_state_atomic)
  - `...\tools\passive_extraction_workflow_latest.py:1932` (mark_frozen_totals_committed)
  - `...\tools\passive_extraction_workflow_latest.py:2035` (initialize_workflow_session)
- Output:
  - `...\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json:1` `created_at="2025-10-16T23:16:05.878..."`, `last_updated="2025-10-16T23:16:06.178..."`.

2) Save #1: set_total_categories() → save_debounced("manifest")
- Script: `...\utils\fixed_enhanced_state_manager.py:1444–1456` → calls `save_debounced("manifest")`; `:1400–1409` still calls `self.save()` during startup.
- Log: `...\run_custom_poundwholesale_20251017_031605.log:53–65` save sequence; `:80` “FROZEN TOTAL CATEGORIES set to 230...”.
- Output: State JSON shows `total_categories=230`.

3) Save #2: explicit save_state_atomic() before initialization
- Script: `...\tools\passive_extraction_workflow_latest.py:1929`; `...\utils\fixed_enhanced_state_manager.py:1392–1399` (no guard).
- Log: `...\run_custom_poundwholesale_20251017_031605.log:67–79`.

4) Save #3: mark_frozen_totals_committed() → save_state_atomic()
- Script: `...\utils\fixed_enhanced_state_manager.py:1473–1477`.
- Log: `...\run_custom_poundwholesale_20251017_031605.log:81–93`.

5) Debounce is not a startup guard
- Script: `...\utils\fixed_enhanced_state_manager.py:1400–1409` (rate-limit only; no block when `_startup_completed` is False).
- Log: Early saves happen before init line 106.

## Suggested Fixes (No Code Applied in This Commit)

1) Guard saves during startup in state manager (tactical)
- Change: Add early return in `save_state_atomic()` and `save_debounced()` when `not _startup_completed`.
- Why: Blocks Save #1–#3 until initialization completes.

2) Reorder workflow (structural)
- Change: Call `initialize_workflow_session()` before any freeze/save calls in `run()`.
- Why: Ensures state loads first; then safe to freeze/persist.

3) Defense-in-depth (optional)
- Change: Low-level guard in `save()` to prevent any startup writes.
- Why: Catch unforeseen save paths.

See `patches/RESUMPTION_STARTUP_GUARDS_AND_INIT_ORDER.patch` for review-only diffs.

## Reconciliation & Reversion Plan (Avoiding Discrepancies Post-Fix)

- Keep (do not revert):
  - MAX binding (monotonic PCI): `tools\passive_extraction_workflow_latest.py:2037–2041`.
  - Category skip logic: `tools\passive_extraction_workflow_latest.py:5014–5016`.
  - Observability logging: `tools\passive_extraction_workflow_latest.py:2045`.

- Audit for unconditional phase clobbers:
  - Search for any active `sp["current_phase"] = "supplier"` assignments and guard them (`only if empty/None`). Active code scan showed FIX markers and guarded logic; backups show historical unconditional assignments.

- Optional simplification to reduce double-writes:
  - After reordering + guards, consider removing the explicit `save_state_atomic("manifest-after-init")` and rely on `mark_frozen_totals_committed()` as the single authoritative commit. Benefit: less I/O; Risk: minimal if commit always follows.

- Rollback readiness:
  - If any unexpected startup deadlock or resume anomalies occur, revert the startup guards first; keep initialization order change (structural) and re-test.

## Behavioral Verification Plan (File‑Grounded)

- Fresh Start
  - Remove `...\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json`.
  - Run entry point and stop after “WORKFLOW INITIALIZED”.
  - Expect: “⏸️ SAVE BLOCKED...” messages before init; first write only after init; state file timestamps ≥ init log time.

- Resume With Existing State
  - Ensure state has `persistent_category_index > 1` and phase preserved.
  - Run; expect no pre-init saves; resume from stored indices; timestamps unchanged pre-init.

- Denominator Preservation
  - After freezing denominators, interrupt and resume; expect `frozen_totals_committed=True` and preserved denominators.

- Regression Monitoring
  - Confirm no new “FRESH START CONTRADICTION” warnings in new runs; compare historical count (22 matches) to 0 post-fix.

## Artifacts Verified (Existence, Timestamps, Content)

- Logs
  - `...\logs\debug\run_custom_poundwholesale_20251017_031605.log:53,67,81,106` — three saves then init.
- Scripts
  - `...\tools\passive_extraction_workflow_latest.py:1928,1929,1932,2035` — save sites precede init.
  - `...\utils\fixed_enhanced_state_manager.py:1392,1400,1444,1473` — missing startup guards in save methods.
- Output
  - `...\OUTPUTS\CACHE\processing_states\poundwholesale_co_uk_processing_state.json:1` — timestamps align with early writes; `supplier_name="poundwholesale.co.uk"`, `total_categories=230`, `frozen_totals_committed=True`.

## Appendix A — Key Snippets (Excerpts)

- Log (Oct 17):
  - `:53` `💾 ATOMIC SAVE START: preserve=True, startup_completed=False`
  - `:67` `💾 ATOMIC SAVE START: preserve=True, startup_completed=False`
  - `:81` `💾 ATOMIC SAVE START: preserve=True, startup_completed=False`
  - `:106` `🚀 INITIALIZING WORKFLOW SESSION...`

- Workflow call order:
  - `:1928` `self.state_manager.set_total_categories(len(category_urls), cfg_hash)`
  - `:1929` `self.state_manager.save_state_atomic()`
  - `:1932` `self.state_manager.mark_frozen_totals_committed()`
  - `:2035` `start_category_index = self.state_manager.initialize_workflow_session()`

- State manager save methods:
  - `save_state_atomic()` (`:1392–1399`) → calls `save()` (no guard)
  - `save_debounced()` (`:1400–1409`) → still calls `save()` during startup

---

Prepared by: Codex CLI — Read-only RCA with verified file paths, timestamps, and content.

