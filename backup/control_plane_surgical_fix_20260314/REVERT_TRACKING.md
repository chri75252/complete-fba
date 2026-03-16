# REVERT TRACKING

## `dashboard/api.py`
- Scope: Preserve per-turn transcript context inside existing session snapshot before working buffers reset.
- Backup: `backup/control_plane_surgical_fix_20260314/dashboard/api.py`
- Validation: chat send -> approval reject -> second chat send -> inspect `session_<id>.json` for archived turn history.
- Validation result: `lsp_diagnostics` clean (hints only), `py_compile` passed, helper smoke confirmed archived `turn_history` entry and cleared working buffers.
- Status: passed

## `control_plane/chat_orchestrator.py`
- Scope: Recover authoritative category resume context from existing run artifacts and rewrite bare category resume requests deterministically.
- Backup: `backup/control_plane_surgical_fix_20260314/control_plane/chat_orchestrator.py`
- Validation: start category sandbox run -> cancel -> bare resume -> confirm rewritten `enqueue_run` preserves original category URLs and limits.
- Validation result: `lsp_diagnostics` clean (hints only), `py_compile` passed, `_load_last_category_resume_context(...)` recovered run `3f8fb567-a164-45fe-84b8-12d6bb96875e` with sandbox suffix, workflow key, runner, and 2 category URLs.
- Status: passed

## `control_plane/run_product_list_refresh.py`
- Scope: Add cooperative cancellation checkpoints, guaranteed partial-run finalization, and truthful `match_method` normalization.
- Backup: `backup/control_plane_surgical_fix_20260314/control_plane/run_product_list_refresh.py`
- Validation: run refresh -> cancel mid-run -> verify flushed linking map, synced cancelled state, and normalized `match_method` output.
- Validation result: `lsp_diagnostics` clean (hints only), `py_compile` passed, cancel marker helper smoke confirmed both primary and legacy markers resolve as cancelled.
- Status: passed

## `control_plane/worker.py`
- Scope: Give product-list refresh jobs a bounded cancellation grace window before force-terminate and recompute final refresh counts for cancelled runs.
- Backup: `backup/control_plane_surgical_fix_20260314/control_plane/worker.py`
- Validation: cancel refresh job -> observe `cancelling` grace state -> confirm terminal cancelled state reflects finalized partial artifacts.
- Validation result: `lsp_diagnostics` clean (hints only), `py_compile` passed, logic review confirmed refresh jobs now enter `cancelling`, wait for the grace window, then terminate only if still alive.
- Status: passed
