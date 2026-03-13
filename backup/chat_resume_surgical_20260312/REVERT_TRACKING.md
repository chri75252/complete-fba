# Chat Resume Surgical Changes - Revert Tracker

Backup root: `backup/chat_resume_surgical_20260312/`

Edited files and scope:
- `.sisyphus/notepads/handoff/session_handoff.md` - updated continuity handoff with transcript-mandatory state and implementation context
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` - explicit product-list resume routing rules
- `control_plane/chat_orchestrator.py` - backend resume rewrite guard, sandbox suffix canonicalization, sandbox alias recovery, `{sandbox_id}` placeholder support
- `dashboard/api.py` - true reset clearing, per-session transcript persistence, session ids, trace capture persistence
- `control_plane/audit.py` - per-session transcript writer helper
- `control_plane/paths.py` - `transcripts_dir` path registration
- `control_plane/worker.py` - semantic abort markers fail exit-0 runs

Planned validation targets:
- product-list resume selects `enqueue_product_list_refresh`
- bare sandbox suffix canonicalizes to `sandbox__<id>`
- `/api/chat/reset` clears all `last_*` fields
- per-session transcript file saved to `OUTPUTS/CONTROL_PLANE/transcripts/`
- `{sandbox_id}` placeholders resolve in expected outputs
- semantic aborts no longer finish as `done`

Full revert procedure:
1. Copy each file back from `backup/chat_resume_surgical_20260312/...`
2. Remove any new transcript files under `OUTPUTS/CONTROL_PLANE/transcripts/` only if rollback requires data cleanup
3. Re-run targeted verification after restore

Validation completed after edits:
- `lsp_diagnostics` on all modified Python files returned no errors
- `python -m py_compile` passed for all modified Python files
- runtime sanity check passed for `_normalize_sandbox_suffix(...)` and `write_session_transcript(...)`
