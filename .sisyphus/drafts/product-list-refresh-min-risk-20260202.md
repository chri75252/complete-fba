# Draft: Product List Refresh - Minimal Risk (2026-02-02)

## Requirements (confirmed)
- enqueue tool `enqueue_product_list_refresh` currently writes a job file under `OUTPUTS/CONTROL_PLANE/jobs/pending/` and requires a separate worker process.
- Currently, no worker process is running.
- Priority: system works first; then improve natural language.
- Goal: least-risk, highest success.

### Requested minimal changes
- `dashboard/chat_panel.py`: after enqueue tool execution, add clear English message including:
  - `run_id`
  - `sandbox_supplier`
  - “job queued” (and that a worker is required)
  - where status/log files will appear
  - command to start worker
  - show `pending jobs` count
  - show presence/absence of `active_run.lock`
- `control_plane/tools/product_list_refresh.py`: validate `products_path` exists; return `ok:false` with clear error if missing (avoid silent enqueue of bad path).
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`: keep JSON-only output; allow `explanation` to be 2-4 sentences; explicitly instruct to say “this queues a job; start worker”.

## Codebase Findings (verified)
- Worker exists at `control_plane/worker.py` and can be started via `python -m control_plane worker` (wired via `control_plane/__main__.py`).
- Worker consumes `job_*.json` from `OUTPUTS/CONTROL_PLANE/jobs/pending/` and moves to `running/` then `done/` or `failed/`.
- Global lock path: `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`.
- Status file path: `OUTPUTS/CONTROL_PLANE/status/{run_id}.json`.
- Log file path: `OUTPUTS/CONTROL_PLANE/logs/{run_id}.log`.
- Product list refresh job_type spawns: `python -m control_plane.run_product_list_refresh` with env `CONTROL_PLANE_JOB_PATH` set to the running job file.

## Constraints (confirmed)
- No commits/push.
- Before editing each file: back up to `backup/<reason>_20260202/` AND write a next-to-file backup with suffix `.bak_02-02-26_HH-MM-SS`.
- Avoid non-essential comments.

## Open Questions
- Should `products_path` be allowed to be outside repo root? (Current implementation treats it as a raw path string and later reads it in `control_plane/run_product_list_refresh.py`.)
- If `active_run.lock` exists, do we want the dashboard message to recommend deleting it (dangerous), or only to instruct the user to inspect it / confirm worker state?
- Preferred user-facing command format: Windows `cmd` vs PowerShell examples?

## Scope Boundaries
- INCLUDE: UX messaging + path validation only.
- EXCLUDE: Changing worker mechanics, job schema redesign, adding new background services, adding new dependencies.
