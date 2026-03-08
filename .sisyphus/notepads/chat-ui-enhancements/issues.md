## 2026-03-01 - Issues observed

- The provided plan path `.sisyphus/plans/chat_ui_enhancements.md` does not exist in this workspace, so design grounding was done against the active code files and closest related plans.
- The current UI only shows terse step labels (`Step N: tool`) with optional caption; there is no persistent per-step reasoning transcript in chat history.
- Worker completion is decoupled from the chat loop, so post-run QA must be explicitly triggered by user action or a UI button.

## 2026-03-01 - Verification constraints encountered

- `lsp_diagnostics` could not run in this environment because the tool runtime cannot resolve `basedpyright-langserver`, even though `basedpyright` is installed.
- Targeted pytest execution is currently blocked by repository test harness state: `tests/conftest.py` contains null bytes and fails before test collection.

## 2026-03-01 - Additional issues observed for sandbox planning

- `control_plane/checklists.py` path templates are currently inconsistent with run sandbox naming (`__sandbox_<id>` vs `__sandbox__<id>`), which contributes to incorrect expected-output messaging.
- `control_plane/tools/run_outputs.py` scans only immediate children in key artifact roots, so nested `sandboxed/` layouts will be invisible without recursive discovery updates.

## 2026-03-01 - Sandbox output relocation hazards

- `get_run_outputs` currently uses non-recursive `iterdir()` scans, so relocating sandbox artifacts under `*/sandboxed/*` will make the tool report missing outputs for otherwise successful runs.
- Chat planner fallback/preview paths in `control_plane/chat_orchestrator.py` and readiness expected outputs in `control_plane/checklists.py` are hardcoded to current root layout and become stale immediately after path relocation.
- Existing linking map schemas differ by workflow (dict in some flows, list in refresh flow), so a naive "count dict keys" validator will misclassify healthy refresh runs.

## 2026-03-01 - Validation task issues encountered

- `lsp_diagnostics` is currently blocked in this environment because `basedpyright-langserver` is not installed, so LSP error checks could not be executed.
- Focused pytest execution is blocked before collection due missing plugin dependency (`ModuleNotFoundError: No module named 'superclaude'`).
- `python -m ruff check ...` is not available in this interpreter (`No module named ruff`), so lint validation had to rely on `py_compile` and runtime smoke checks.

## 2026-03-02 - Validation follow-up issues

- `lsp_diagnostics` remains unavailable because the tool runtime cannot resolve `basedpyright-langserver` on PATH, even though `basedpyright` is installed in the user site-packages.

## 2026-03-02 diagnostics environment note
- lsp_diagnostics could not execute because basedpyright-langserver is not discoverable in PATH, even though basedpyright package is installed in user site-packages.
- Used python -m py_compile control_plane/tools/run_validation.py as syntax validation fallback.

## 2026-03-05 - Chat cancel/clarify regressions

- `cancel_run` confirmation can loop because the UI resumes autonomous planning immediately after approval and can re-emit `cancel_run` for the same original user text.
- Prompt/backend mismatch: planner is told to pass empty `run_id` for cancel (expecting backend `last_run_id` resolution), but backend run resolution is filesystem-based and does not use Streamlit `last_run_id` directly.
- Planner hard rules force `ask_clarify` when any required field is missing and prohibit path guessing, which causes clarification prompts even when path discovery could be done with read tools.

## 2026-03-05 - Remaining open risk after code cross-check

- `cancel_run` can still re-loop after approval because `dashboard/chat_panel.py` resumes the autonomous loop for all approved write tools (via retained `agent_scratchpad` + `agent_user_text`), including cancellation, which can re-propose the same action depending on planner output.
