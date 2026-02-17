# Draft: Control Plane Chat/UI Remaining Fixes (A–F)

## Requirements (confirmed)
- Address remaining report items **A–F** for Control Plane Chat/UI.
- Already implemented (do not redo): run_id placeholder normalization, limits parity, safe_json_loads, LLM generate_json try/except, sandbox credential aliasing.
- Constraints:
  - **No git commands**.
  - **No edits** to `tools/` or any `run_custom_*.py`.
  - **Backup any files before editing** under `backup/<reason>_20260211/` preserving relative paths.
- Deliverable: a single plan with waves, verification steps, and classification of items safe to execute immediately vs requiring user confirmation.

## Items Under Review
- **A**: `dashboard/pages/01_Operator_Control_Plane.py` — add `sandbox_supplier` isolation: ensure `write_categories_subset` uses sandbox supplier; ensure overrides include `workflows[workflow_key].supplier_name`; pass `sandbox_supplier` to `enqueue_run_job`.
- **B**: `config/system_config.json` — set `efghousewares_workflow.authentication_required` to `false` (must verify key exists).
- **C**: `dashboard/chat_panel.py` — add intercepts: cancel command; stop-at-N while running job; pending-edits regex for "both-should-be-N".
- **D**: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` — instruct to not use `<run-id>` and use empty string instead.
- **E**: `control_plane/chat_orchestrator.py` — remove `product_list_refresh` `products_path` placeholder path; replace with descriptive text.
- **F**: `control_plane/chat_orchestrator.py` — wrap reading `config/system_config.json` in try/except; return `ok:false` with helpful error.

## Evidence Collected (so far)
- `control_plane/chat_orchestrator.py` currently contains `enqueue_product_list_refresh` schema with `"products_path": "C:/path/to/products_subset.json"` placeholder.
- `control_plane/chat_orchestrator.py` reads system config via `read_json(repo_root / "config" / "system_config.json")` (needs try/except hardening for F).
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` contains a reference to `OUTPUTS/CONTROL_PLANE/logs/{run_id}.log` (candidate for D).

## Decisions (confirmed)
- **A sandbox isolation**: YES — Operator UI should create sandbox-isolated supplier name (`<supplier>__sandbox__<id>` style), override `workflows[workflow_key].supplier_name` to sandbox supplier, alias credentials, and pass `sandbox_supplier` through to `enqueue_run_job`.
- **B scope**: GLOBAL change — set `workflows.efghousewares_workflow.authentication_required` to `false` in `config/system_config.json`.
- **C cancel behavior**: BOTH — if a tool call is pending confirmation, cancel clears the pending action; otherwise it should enqueue `cancel_run` using last_run_id fallback.

## C Behavior (confirmed)
- **Cancel phrases**: "cancel family" — any message that contains the word `cancel` (recommend implement with word-boundary match `\bcancel\b` to reduce false positives).
- **Cancel behavior**:
  - If a tool call is pending confirmation: clear pending action immediately.
  - Else: cancel running job immediately (execute `cancel_run` using `last_run_id` fallback) without extra confirmation.
- **Stop-at-N during running job**: NOT supported — respond with guidance to cancel + requeue with updated limits.
- **Both-should-be-N** (pending action edits): support phrase like `both should be N` to set both `max_products` and `max_products_per_category` to N.

## Scope Boundaries
- INCLUDE: only A–F changes and required verification.
- EXCLUDE: unrelated refactors, changes to protected scripts, or altering workflow engine behavior beyond requested items.
