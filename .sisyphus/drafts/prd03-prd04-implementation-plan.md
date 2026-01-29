# Draft: PRD_03 → PRD_04 Implementation Plan (Chat UX + Product Refresh)

## Requirements (confirmed)
- Deliver PRD_03 first, then PRD_04.
- Authoritative PRDs:
  - `SYSTEM_CHAT_UI_PRDS/PRD_03_CHAT_UX_ONLY_v1_1.md`
  - `SYSTEM_CHAT_UI_PRDS/PRD_04_CHAT_PLUS_PRODUCT_LIST_REFRESH.md`
- Hard constraints:
  - Allowed edits: `control_plane/` and `dashboard/` only (plus new files under those).
  - Must NOT edit core workflow engine: `tools/`, `utils/`, `run_custom_*.py`.
  - Must NOT modify main `OUTPUTS/` artifacts, except PRD_04 explicitly allows overwriting canonical Amazon cache files.
- Current state notes (user-provided):
  - `control_plane/llm/providers.py` already has `generate_with_tools()` and `generate_text()` (do not revert).
  - `control_plane/chat_orchestrator.py` still uses JSON-only planner prompt and minimal validation.
  - `dashboard/chat_panel.py` already renders `tool_result` JSON in an expander.
  - `control_plane/tools/clarify.py` exists.
- Deliverable needed from planning:
  - Step-by-step tasks with dependencies
  - Files to change/add
  - Category+skills recommendations per task
  - Test/verification plan
  - Highlight risks (PRD_04 Amazon refresh) + mitigations

## Technical Decisions (tentative / to confirm)
- PRD_03: Introduce single source-of-truth tool registry (names, schemas, read/write) used by:
  - Planner prompt/schema generation
  - Executor validation
  - UI rendering labels
- PRD_03: Implement confirmation gating for write tools in Streamlit UI.
- PRD_03: Add planner JSON validation with retries and fallback to `ask_clarify`.
- PRD_04: Add new write tool `enqueue_product_list_refresh` and a job runner under `control_plane/`.
- PRD_04: Implement sandbox supplier identity (`<supplier_domain>__sandbox__<run_id[:8]>`) for supplier-scoped artifacts.
- PRD_04: Allow overwrite of canonical Amazon cache files only where PRD permits.

## Research Findings
### Codebase (verified)
- `control_plane/chat_orchestrator.py`:
  - Planner prompt is built in `build_prompt()` and hard-codes a `tools_desc` dict (schema duplication / drift risk).
  - Tool planning currently uses `provider.generate_json(prompt)` (JSON-only), then minimal post-check for `enqueue_run` missing `category_urls`.
  - Execution does parameter “healing” (infer `supplier_domain`, normalize `url` list → first string).
  - Tool sets exist as `READ_TOOLS` + `WRITE_TOOLS`, but are not the schema source-of-truth.
- `dashboard/chat_panel.py`:
  - Already has confirmation gating for write tools via `pending_tool_call` in `st.session_state`.
  - Already truncates large JSON with `_truncate_value()` and shows `tool_result` JSON in an expander.
  - Current stored message objects are *not yet* the PRD message contract (`thinking` + `tool_call` fields not stored).
- `control_plane/llm/providers.py`:
  - `OllamaProvider.generate_with_tools()` exists (native tool calling + optional `thinking` field).
  - `OllamaProvider.generate_text()` exists (summarizer-style output).
  - `generate_with_tools()` currently uses `temperature=0.3` (PRD wants deterministic `temperature=0`).
- `control_plane/worker.py`:
  - Worker executes jobs from `OUTPUTS/CONTROL_PLANE/jobs/pending/` and updates status/logs.
  - Worker currently supports only two job types: run workflow and onboarding wizard.
  - Worker uses `dashboard.metrics_core.MetricsLoader` to resolve `OUTPUTS/` paths and progress snapshots.

### Best-practice checklist (to embed into plan)
- Tool calling safety:
  - Pydantic (or equivalent) schema validation for tool params before execution.
  - Retry LLM tool selection up to N times with explicit validation feedback.
  - Strict whitelist of tool names; never execute invalid tool calls.
- Refresh / overwrite safety:
  - Always write atomically (temp + replace).
  - Create timestamped backups before overwrite.
  - Add rollback (keep last N backups).
  - Add guards against truncation / partial writes.
  - Handle Windows file locking with retry/backoff.

## Open Questions
- Confirmation gating UX: per-message confirm button, or global “pending tool call” queue?
- Test strategy constraints: may we add tests outside `control_plane/` and `dashboard/`?
- PRD_04 Amazon refresh: how will control_plane safely invoke Amazon extraction without modifying `tools/`?
- Which suppliers are in scope for product-list refresh (default `poundwholesale.co.uk` only, or any supplier domain)?
- Operational constraints: Must work with local LLM always, or support “LLM off / fallback” mode?

## Scope Boundaries
- INCLUDE:
  - PRD_03 chat message contract (prose-first, JSON in expanders, thinking optional)
  - Deterministic tool execution, schema validation, clarify-first
  - Confirmation gating for write tools
  - PRD_04 product-list Amazon refresh as sandboxed job
- EXCLUDE:
  - Any edits to `tools/`, `utils/`, or `run_custom_*.py`
  - Any changes to category extraction workflow
  - Any non-PRD features (performance, new unrelated UI)
