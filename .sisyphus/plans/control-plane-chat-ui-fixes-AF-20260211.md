# Control Plane Chat/UI Remaining Fixes (A–F)

## TL;DR

> **Quick Summary**: Align Operator UI job creation with sandbox isolation, harden config/tool schemas in `control_plane/chat_orchestrator.py`, and add chat UX intercepts for typed cancellation and "both should be N" pending edits.
>
> **Deliverables**:
> - Sandbox-isolated Operator UI job enqueueing (A)
> - `efghousewares_workflow.authentication_required=false` in base config (B)
> - Chat panel intercepts for typed cancel + both-should-be-N (C)
> - Updated planner instructions re: run_id placeholder (D)
> - More descriptive `products_path` schema (E)
> - `system_config.json` read hardening with `ok:false` errors (F)
>
> **Estimated Effort**: Short–Medium
> **Parallel Execution**: YES (2 waves)
> **Critical Path**: Backups → (A,B,C,D,E,F) → compile/test → smoke run

---

## Context

### Original Request
A report lists remaining fixes **A–F** for Control Plane Chat/UI. Already implemented: run_id placeholder normalization, limits parity, safe_json_loads, LLM generate_json try/except, sandbox credential aliasing. Remaining items A–F should be reviewed and implemented if needed.

### Constraints / Guardrails
- **No git commands**.
- **Do not edit** anything under `tools/` or any `run_custom_*.py`.
- **Backup every file before editing** under `backup/<reason>_20260211/` preserving relative paths.

### Verified Repo Evidence
- Operator UI enqueues jobs from `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\pages\01_Operator_Control_Plane.py#L102` but currently writes categories using non-sandbox `supplier_domain` and does not override workflow `supplier_name` (needs A).
- Control-plane sandbox isolation reference behavior exists in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L759` and calls `enqueue_run_job(..., sandbox_supplier=...)` (pattern for A).
- `efghousewares_workflow.authentication_required` currently `true` in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json#L311` (needs B).
- Typed chat input is intercepted when a pending tool call exists in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py#L215` (needs C additions).
- Cancel markers are created by tool `cancel_run` in `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L817` and polled/cleared by worker (as referenced by earlier explore findings).

---

## Work Objectives

### Core Objective
Make A–F fixes so Operator UI and Chat UI behave consistently (sandbox isolation, cancel UX, safer prompts/schemas, and robust config reads) without touching protected scripts.

### Definition of Done
- Operator UI enqueued runs use sandbox supplier naming and isolated outputs.
- `config/system_config.json` has EFG auth flag updated.
- Chat panel typed cancellation works as specified.
- Planner instructions no longer encourage `<run-id>` placeholders.
- Tool schemas avoid misleading hard-coded placeholder paths.
- Config read failures return `{ok:false,...}` instead of raising.

### Must NOT Do
- Do not edit any `tools/*` file or `run_custom_*.py` file.
- Do not introduce new secrets into repo.
- Do not change unrelated workflow behavior.

---

## Verification Strategy

### Minimal Automated Verification (agent-executable)
- `python -m compileall control_plane dashboard config` (ensures syntax correctness).

### Optional Targeted Tests
This repo has a `tests/` tree and `pytest.ini` at `tests/fba_agent/pytest.ini`. If execution time is acceptable:
- Run a fast smoke subset (executor choice): `pytest -q tests/test_import_validation.py` (or similarly quick import-only tests).

### Functional Smoke (manual / local runtime)
Because Streamlit UI changes are involved:
- Start dashboard (example): `python -m streamlit run dashboard/app_fixed.py --server.port 8501`
- Validate:
  - Operator Control Plane job creation produces sandbox supplier + merged overrides
  - Chat panel: typed "cancel" while pending clears; typed "cancel" with no pending cancels last run

---

## Execution Strategy

### Wave 0 — Preflight & Backups (blocking)
Create one backup root:
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\backup\control_plane_chat_ui_fixes_AF_20260211\`

Copy the following files into that folder preserving relative paths:
- `dashboard\pages\01_Operator_Control_Plane.py`
- `config\system_config.json`
- `dashboard\chat_panel.py`
- `control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- `control_plane\chat_orchestrator.py`

Acceptance:
- Each backed-up file exists and is non-empty.

### Wave 1 — Sandbox isolation + config flag + planner docs (parallel)
**Tasks**: A, B, D

### Wave 2 — Chat UX + orchestrator schema/hardening (parallel)
**Tasks**: C, E, F

---

## TODOs (A–F)

### A) Operator UI sandbox_supplier isolation
**Target**: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\pages\01_Operator_Control_Plane.py#L98`

**What to do**:
- Implement sandbox identity generation consistent with `control_plane/chat_orchestrator.py`:
  - `sandbox_suffix = f"sandbox__{run_id[:8]}"`
  - `sandbox_supplier = f"{supplier_domain}__{sandbox_suffix}"`
- Use sandbox supplier when writing categories subset:
  - change `write_categories_subset(run_id, supplier_domain, ...)` → `write_categories_subset(run_id, sandbox_supplier, ...)`
- Expand overrides to include workflow `supplier_name` and credentials aliasing:
  - add `workflows[workflow_key].supplier_name = sandbox_supplier`
  - if base credentials exist under canonical supplier, add overrides `credentials[sandbox_supplier]=base_creds`
- Pass `sandbox_supplier` to `enqueue_run_job(..., sandbox_supplier=sandbox_supplier)`.

**References (pattern to follow)**:
- Sandbox isolation reference: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L759`
- Job payload accepts sandbox supplier: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\tools\jobs.py#L67`

**Acceptance Criteria**:
- After creating a job in Operator UI, the queued job JSON contains:
  - `sandbox_supplier` set to `<supplier_domain>__sandbox__<8chars>`
  - merged config overrides set workflow supplier_name to sandbox supplier
- The generated categories subset JSON has `supplier_domain` equal to sandbox supplier.

**Safety / Confirmation**:
- Safe to execute immediately (only affects Operator UI control plane enqueueing).

---

### B) EFG workflow authentication_required=false (global)
**Target**: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json#L311`

**What to do**:
- Set `workflows.efghousewares_workflow.authentication_required` from `true` → `false`.

**Acceptance Criteria**:
- Config JSON remains valid.
- Grep/inspection shows key is present and false.

**Safety / Confirmation**:
- **Requires user confirmation during execution** (global behavior change for non-sandbox runs).

---

### C) Chat panel intercepts: typed cancel, both-should-be-N, stop-at-N guidance
**Target**: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py#L211`

**Confirmed behavior**:
- Cancel phrases: user chose "cancel family".
- Cancel behavior:
  - pending tool call → clear pending
  - otherwise → cancel run immediately (execute cancel tool) using `last_run_id` fallback
- Stop-at-N during running job: NOT supported → explain cancel + requeue
- Pending edits: support phrase `both should be N`.

**What to do**:
1) Inside the pending-tool-call intercept block (`if pending_tool_call is not None`):
- Before the existing regex edits, check for cancel-family:
  - Recommend matching word-boundary `\bcancel\b` to avoid matching unrelated words.
  - Clear pending state and append an assistant message like "Pending action cleared." then rerun.
- Add regex for `both should be (\d+)`:
  - Set `max_products` = N and `max_products_per_category` = N and mark `updated_params=True`.

2) When there is no pending tool call:
- If input matches word-boundary cancel-family (`\bcancel\b`), run `cancel_run` directly.
  - This should reuse existing `cancel_run` tool behavior (which falls back to `last_run_id` if params omit run_id).
- If input matches `stop at (\d+)` (or similar), respond "not supported" and instruct user to cancel + requeue with updated limits.

**References**:
- Pending-tool-call intercept block: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py#L215`
- Cancel tool exists: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L817`

**Acceptance Criteria**:
- With a pending tool call, typing "cancel" clears pending state (no warning loop).
- With no pending tool call but a `last_run_id` in session, typing "cancel" creates cancel markers and reports success.
- Typing "both should be 25" during a pending tool call updates both limits.
- Typing "stop at 25" returns a not-supported guidance message.

**Safety / Confirmation**:
- Safe to execute immediately (UI-only), but watch false positives due to substring-style cancel matching.

---

### D) Planner instructions: do not use `<run-id>` placeholder
**Target**: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md#L7`

**What to do**:
- Add an explicit hard rule:
  - Never output the literal string `<run-id>`.
  - If run_id is unknown, set `run_id` to empty string `""` or omit it (depending on schema), letting the system generate one / fall back to `last_run_id`.

**Acceptance Criteria**:
- Prompt file remains valid markdown.
- Local planner has explicit guidance preventing `<run-id>` emissions.

**Safety / Confirmation**:
- Safe to execute immediately.

---

### E) Remove misleading products_path placeholder path in tool schema
**Target**: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L286`

**What to do**:
- Replace the schema example value:
  - from `"products_path": "C:/path/to/products_subset.json"`
  - to a descriptive placeholder that is not a concrete path, e.g. `"products_path": "<absolute-path-to-products-json>"`.

**Acceptance Criteria**:
- The prompt schema no longer suggests a fake path that looks real.

**Safety / Confirmation**:
- Safe to execute immediately.

---

### F) Wrap system_config.json reads in try/except and return ok:false
**Targets**:
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L104` (`_resolve_workflow_params` reads config)
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py#L687` (`enqueue_run` tool execution reads config)

**What to do**:
- Wrap `read_json(repo_root / "config" / "system_config.json")` in `try/except Exception as e`.
- On failure, return structured error:
  - `{ "ok": False, "error": "Failed to read config/system_config.json: ..." }`
- Ensure errors propagate to UI without a stack trace.

**Acceptance Criteria**:
- If config file is missing or invalid JSON, chat tool planning/execution returns `ok:false` with helpful `error` string.

**Safety / Confirmation**:
- Safe to execute immediately.

---

## Safe-to-Execute vs Needs Confirmation

### Safe to Execute Immediately
- A, C, D, E, F (UI/prompt/schema hardening; sandbox behavior aligns with existing chat path)

### Requires Explicit Confirmation During Execution
- B (global workflow auth toggle)

---

## Handoff
Plan saved to: `.sisyphus/plans/control-plane-chat-ui-fixes-AF-20260211.md`

When you’re ready to execute, run:
- `/start-work`

(Executor should also delete the draft file after plan completion; planner mode can’t perform filesystem deletions here.)
