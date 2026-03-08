# Resume Root-Cause Reaudit (2026-03-04)

## Scope
- Reaudit two runs:
  - `d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5` (EFG product-list refresh)
  - `06956903-c98e-4867-a1b4-e19798a1bb40` (Angel category sandbox resume)

## Evidence Snapshot
- `control_plane/tools/jobs.py`: `enqueue_run_job` has no sandbox category-copy logic; `RunRequest` has no `sandbox_suffix` field.
- `control_plane/chat_orchestrator.py`: current enqueue path writes categories from `req.category_urls` only; no `_find_latest_nonempty_categories_subset_for_sandbox` helper in current file.
- `OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json` has exactly one URL.
- `OUTPUTS/CONTROL_PLANE/status/06956903-c98e-4867-a1b4-e19798a1bb40.json` contains stack trace with `IndexError` in `utils/fixed_enhanced_state_manager.py` at `_first_incomplete_index_by_url`.
- `logs/debug/run_custom_angelwholesale-co-uk__sandbox__06956903_20260302_160809.log` confirms state loaded with resume index 13 and single-category subset before crash.
- `control_plane/run_product_list_refresh.py` writes linking map and state but never calls `tools.FBA_Financial_calculator.run_calculations`.
- `OUTPUTS/CONTROL_PLANE/status/d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5.json` shows `state=done`, `linking_map_exists=true`, `financial_report_exists=false`.
- `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__d8f5d679/linking_map.json` contains 6 entries.
- `control_plane/internal/path_resolver.py` sets control-plane `logs_dir` to `OUTPUTS/CONTROL_PLANE/logs`; `worker.py` writes subprocess logs there.

## Hypotheses To Critique
1. `enqueue_run_job` categories-copy behavior is the real root fix for category resume.
2. Angel category resume crash is primarily subset-size/state-pointer mismatch in state-manager startup logic.
3. EFG missing financial report is because PLR runner does not trigger financial calculations.
4. Dashboard log visibility issue is caused by worker log path mismatch (`OUTPUTS/CONTROL_PLANE/logs` vs `logs/debug`).

## Requested Critique Output
- Claim matrix (CONFIRMED/PARTIAL/REJECTED) with file-grounded evidence.
- Root-cause tree separating primary vs contributing factors.
- Minimal-risk fix order (P0/P1/P2) and blast radius.
- Note any contradictions such as `status.state=done` while stack traces exist in log payload.
