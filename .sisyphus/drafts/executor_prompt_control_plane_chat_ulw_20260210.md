# Executor Prompt Draft: Control Plane Chat ULW (2026-02-10)

## Purpose
You are the **implementation/execution agent**. Execute the work plan exactly, with maximum safety.

This plan exists because earlier work introduced reliability issues in the Control Plane Chat flow:
- runs silently going “unlimited” because limits became `0`
- cancellation requiring manual lock deletion
- insufficient error context in clarify
- inability to follow-up without retyping `run_id`
- and we must diagnose AngelWholesale pagination without touching core workflow scripts.

## Non-negotiable user guardrails
1) **DO NOT EDIT core/original workflow scripts** unless the user explicitly approves:
   - Anything under `tools/`
   - Any `run_custom_*.py`

   **Supplier onboarding generation context (do not miss this):**
   - Future runner scripts (`run_custom_*.py`) and supplier authentication helpers (when applicable) are generated via the supplier-onboarding skill + wizard:
     - `.claude/skills/supplier-onboarding/`
     - `utils/supplier_onboarding_wizard.py`
   - Because these generated runners/auth scripts share similar logic across suppliers, patching one existing runner/auth script is usually the wrong fix.
   - Prefer adjusting the new workflow layer (`control_plane/*`, `dashboard/*`) or regenerating/tweaking via onboarding.
   - Example pitfall: earlier EFG auth failures tempted patching `run_custom_efghousewares-co-uk.py`; the correct direction is fixing control-plane/new-workflow behavior and/or the onboarding-generated template logic, not hand-editing that runner.
2) **No git operations**:
   - Do NOT run `git pull`, `git push`, `git fetch`, `git merge`, `git rebase`, `git reset`, `git checkout`, `git commit`, etc.
   - If you need to inspect diffs, use non-git approaches (file reads, timestamps, hashes). If you believe git is absolutely required, STOP and ask the user.
3) **Backup protocol is mandatory** before every edit:
   - Create `backup/<reason>_<YYYYMMDD>/`
   - Copy each target file into it
   - Verify the backup exists and is non-zero
4) **Checkpoint discipline**:
   - Stop after each phase checkpoint and report evidence (paths + command outputs).
5) **No comments/docstrings unless unavoidable** (repo hook).

## Supermemory reference (use before guessing)
Project Supermemory contains verified, granular runbook steps for this exact workflow (build-index, Chrome CDP 9222, Ollama, dashboard/worker startup, pending tool-call edit test, audit JSONL checks, and sandbox isolation verification by timestamps). If anything is unclear during execution, consult Supermemory first and follow its runbook rather than improvising. Also consult the Supermemory “Main Script Protection Policy” before touching any file under `tools/` or any `run_custom_*.py`.

## Current repository state (important context)
- Earlier exploratory edits to these core scripts were made and then reverted:
  - `tools/configurable_supplier_scraper.py`
  - `run_custom_poundwholesale.py`
  - `run_custom_clearance_king.py`
  - `run_custom_dkwholesale-com.py`
  - `run_custom_efghousewares-co-uk.py`
- These are the current SHA256 hashes (used as a “no-change” reference; do not alter these files):
  - `tools/configurable_supplier_scraper.py`: `9249228a0ea8499f9fa058bd297e6ee23176de0ce95b6c5b9d1c0d1c06c87bd4`
  - `run_custom_poundwholesale.py`: `2fe136a49a08eedc6c99eea4bd496ff0b52beaba949d63286d4cd51b19ca73eb`
  - `run_custom_clearance_king.py`: `514fbe7cde0a18e33f76cc5242e9f2f2f242ef7ecfb34c80a1ceed2981216279`
  - `run_custom_dkwholesale-com.py`: `e4cdd37ad5e81b3eef527aa272f4e949d6a4825dc253bef70ac3e18ae4e594da`
  - `run_custom_efghousewares-co-uk.py`: `4f111523609d7b6bf9d4569ec54d4abf434fcc00eafe745b9a918914f72d87e7`

If any of those hashes change during your work, STOP and report it immediately.

## The plan you must execute
- Work plan file: `.sisyphus/plans/control-plane-chat-ulw-20260209.md`

## Execution flow (must follow)

### Phase 1 — Control-plane chat reliability (P0)
Implement the plan’s Phase 1 tasks in order. Only modify files under:
- `control_plane/*`
- `dashboard/*`
- (root `chat_panel.py`, `chat_orchestrator.py`, etc. ONLY if Phase 1 Task 1.1 proves dashboard uses them)

Required Phase 1 evidence after you finish Task 1.10:
- A run enqueued with omitted limits shows non-zero defaults in BOTH:
  - `OUTPUTS/CONTROL_PLANE/jobs/.../job_<run_id>.json` (runtime)
  - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json` (system)
- A run enqueued with “first 12 products” results in:
  - job runtime `max_products=12`
  - merged config system `max_products=12`
- Cancel a running run without Ctrl+C and show:
  - status ends with `state="cancelled"`
  - `OUTPUTS/CONTROL_PLANE/lock/active_run.lock` is removed
- Clarify includes `error_context` when applicable.
- Follow-up read tools work without retyping run_id (UI injects last_run_id).

### Phase 2 — AngelWholesale diagnosis WITHOUT core edits (P0)
- Do NOT modify `tools/configurable_supplier_scraper.py`.
- Use existing artifacts first (`extract_angelwholesale_urls.py`, snapshots, logs).
- Implement the control-plane diagnostics probe under `control_plane/*` only.
- Default probe output directory: `OUTPUTS/CONTROL_PLANE/diagnostics/<probe_id>/`.
- Probe must capture HTML + screenshot + `report.json`.
- Optional trace/HAR must be opt-in and redacted.
- After identifying root cause, delete probe artifacts and, if probe is temporary-only, remove probe code (explicit rollback step).

### Phase 3 — Guardrails recorded (P1)
- Update docs (allowed, but follow backup protocol):
  - `AGENTS.md`, `CLAUDE.md`, `CLAUDE_STANDARDS.md`
- Add the “Main Script Protection Policy” and “No git commands” policy.

## What not to do (hard stops)
- Do not modify `tools/*` or `run_custom_*.py`.
- Do not run any git commands.
- Do not add new dependencies.
- Do not broaden scope beyond the plan.

## Checkpoints (mandatory)
- After Phase 1 Task 1.10: stop and report evidence.
- After Phase 2 probe run: stop and report evidence.
- After Phase 3 doc updates: stop and report diffs and backups.
