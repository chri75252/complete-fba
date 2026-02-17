# Issues Encountered (2026-02-14)

## products_path_not_allowed
- Root cause: `control_plane/tools/product_list_refresh.py` previously only allowed `OUTPUTS/PRODUCTS_LISTS/**` and the per-run override file.
- Fix: explicitly allow `OUTPUTS/CONTROL_PLANE/inputs/**`.

## cancel_run / tail_logs / show_status require run_id
- Root cause: `control_plane/chat_orchestrator.py` attempted Streamlit session state fallback only; outside Streamlit it used run_id="".
- Symptom: log path became `OUTPUTS/CONTROL_PLANE/logs/.log` and cancel returned `run_id is required`.
- Fix: add `_resolve_contextual_run_id` with filesystem fallback (jobs/running -> jobs/pending -> status/*.json).

## processing_state null for refresh runs
- Root cause: `FixedEnhancedStateManager.save_state_atomic()` calls `save()` which blocks until `_startup_completed` is True.
- Symptom: processing state file never written, so worker `resolved_paths.processing_state` stayed null.
- Fix: call `state_manager.enter_runtime_phase()` before first `save_state_atomic()` in `control_plane/run_product_list_refresh.py`.
