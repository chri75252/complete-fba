# Draft: Control-plane Chat ULW execution sequence update (2026-02-10)

## Requirements (confirmed)
- Update/confirm execution sequence for approved plan: `.sisyphus/plans/control-plane-chat-ulw-20260209.md`.
- Produce a concrete “next-wave” execution plan: tasks + ordering + checkpoints.
- Incorporate new evidence: run `df9037be` job JSON shows runtime `max_products=0`, merged config sets `system.max_products=0`.
- Known code delta:
  - `control_plane/chat_orchestrator.py` patched at `:659-683` to default missing limits to base config defaults.
  - Root `chat_orchestrator.py` still parses with `int(p.get("max_products") or 0)` (and similarly for per-category), which collapses “missing” to `0`.
- Must propose minimal surgical diffs for root `chat_orchestrator.py` to match the fix (no code changes performed by Prometheus).
- Must propose verification steps that check job JSON + merged config + log + processing state (not logs alone).
- Must include backup folder naming convention: backup subfolder named after task/group.
- Must not propose scope creep outside the existing plan.

## Scope Boundaries
- INCLUDE: sequencing changes, verification checkpoints, minimal diff proposal for root `chat_orchestrator.py`, confirm which UI module imports which orchestrator.
- EXCLUDE: unrelated refactors, new features, unrelated bug fixes.

## Open Questions
- Which chat UI code path is producing the run `df9037be`:
  - `dashboard/chat_panel.py` (imports `control_plane.chat_orchestrator`?)
  - or root `chat_panel.py` (imports root `chat_orchestrator.py`)?
- Is the worker job execution path using the same orchestrator module as the UI, or does it independently parse `max_products` from job payload?

## Evidence Collected (file-grounded)

### Chat UI entrypoint + module resolution
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py:6` imports from `control_plane.chat_orchestrator`.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\chat_panel.py:6` also imports from `control_plane.chat_orchestrator` (root duplicate).
- Background explore indicates `dashboard/app_fixed.py` uses `from chat_panel import render_chat_panel` and, because it lives under `dashboard/`, that import resolves to `dashboard/chat_panel.py` (not the root file).

### Orchestrator parsing difference (current working tree)
- Root orchestrator still collapses missing/None to `0`:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\chat_orchestrator.py:659-666`
- Control-plane orchestrator has defaulting helper:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py:659-683`

### Run df9037be artifact evidence
- Job JSON shows runtime limits are `0/0`:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\jobs\done\job_df9037be-24b6-495a-8b66-8ef5bb8bc2da.json:14-17`
- Merged config contains `system.max_products=0` and `system.max_products_per_category=0`:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\overrides\df9037be-24b6-495a-8b66-8ef5bb8bc2da\system_config.merged.json:24-28`
- Base config defaults are non-zero:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json:24-28` shows `system.max_products=1000000`, `system.max_products_per_category=2000`.
- Status JSON confirms a sandbox processing state path (important for post-run verification beyond logs):
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\status\df9037be-24b6-495a-8b66-8ef5bb8bc2da.json:9-15`
- Runner log shows it executed in infinite mode (supporting evidence, but not sufficient alone):
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\logs\df9037be-24b6-495a-8b66-8ef5bb8bc2da.log:123-126` shows `max_products_to_process: 0` and `INFINITE MODE DETECTED`.

### Audit trail (chat tool call params)
- Audit shows the user/tooling did enqueue with `max_products: null` and `max_products_per_category: null` near the time of the df9037be run:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\audit\chat_tool_calls.jsonl:54`

## Implication / Hypotheses to validate
- Even if the Streamlit UI imports `control_plane.chat_orchestrator`, run `df9037be` can still have 0/0 if:
  - the run was created before the patch was in effect, or
  - the running Streamlit process had stale code loaded, or
  - another entrypoint created the job using the root `chat_orchestrator.py`, or
  - constraints were explicitly interpreted as unlimited somewhere upstream.
