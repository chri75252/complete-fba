## 2026-03-01 - Decisions

- Implement "Show Reasoning" as a minimal UI enhancement in `dashboard/chat_panel.py`, reusing existing `explanation` from the planner rather than introducing provider-specific raw-thinking plumbing.
- Add a `Validate Last Run` button that injects a standard review prompt and runs through the existing autonomous loop, avoiding worker or job schema changes.
- Keep validation non-hallucinatory by enforcing a triangulation protocol in the prompt: every claim must cite at least 3 independent artifacts (status/log/output file contents).
- Prefer a prompt+button workflow over background auto-triggering, because chat and worker are intentionally decoupled and explicit invocation is safer and auditable.

## 2026-03-01 - Thought trace UI decision

- Use a two-layer trace: live step-level thought expanders during `_run_agent_loop`, then a persisted `Thought trace` expander on the final assistant message.
- Do not append reasoning directly into main message text or require a dedicated `think` tool; reuse `step.tool_call.explanation` from existing planner output.
- Keep the change minimal and UI-only in `dashboard/chat_panel.py`, with no orchestrator/tool schema changes.

## 2026-03-01 - Sandbox/validation planning decisions

- Introduce a centralized sandbox artifact resolver in `control_plane` and make chat previews (`expected_outputs`) consume it, so expected paths are computed from the same source of truth as backend reads.
- Move sandbox outputs under dedicated `sandboxed/` subfolders with a phased dual-read migration to avoid breaking existing runs and dashboard queries.
- Add a deterministic `validate_run` read tool that returns structured JSON checks/results; keep LLM responsibility limited to explanation, not raw artifact parsing.

## 2026-03-01 - Validation architecture decision

- Prefer deterministic Python validation (`validate_run(run_id)`) over direct LLM inspection of large JSON artifacts; feed the LLM only compact evidence summaries and bounded samples.
- Keep validation schema-aware: normalize linking map payloads that may be either dict or list, then run required-key and quality checks against normalized rows.
- If sandbox pathing is changed to nested `sandboxed/` directories, ship a compatibility phase where readers/tools search both legacy root and new nested locations before deprecating legacy paths.

## 2026-03-01 - Run validator implementation decisions

- Implemented `validate_run_integrity(run_id)` as a standalone deterministic backend function in `control_plane/tools/run_validation.py` without planner/tool-registry changes, to keep this task single-file and low blast radius.
- Used deterministic 3-row sampling for both linking map and cached product datasets, with explicit URL/price sanity checks to catch swapped field values.
- Marked any detected `404`, `EMPTY CATEGORY`, or exception signatures as structured `errors_found` entries so the LLM receives compact, evidence-oriented failure reasons.

## 2026-03-02 - Validation requirement refinement decisions

- Extend `validate_run_integrity(...)` with a mode switch (`auto`/`workflow`/`onboarding`) so onboarding checks are deterministic and not inferred from generic run artifacts.
- Replace row-fragment checks with full-product-object sampling (3 distinct dictionaries) and typed validation of `title`, `url`, `price`, optional `ean`, and `source_url`.
- In onboarding mode, enforce both filesystem artifacts and `config/system_config.json` injection checks (workflow entry, `test_product_url`, and credentials when auth is required).

## 2026-03-02 - Strict validation hardening decisions

- Keep deterministic 3-row sampling but apply it to linking-map rows for strict schema validation, with per-field error codes to keep failure explanations compact and machine-consumable.
- Define a fixed allowlist for `match_method` values and treat unknown methods as schema failures instead of soft warnings.
- Add a required fallback path that performs triangulation (log signature scan + supplier/system config selector sanity check + synthesized diagnosis) whenever sampled linking-map schema fails or linking-map is empty.

## 2026-03-02 - Triangulation execution decisions

- Rewrote `_validate_standard_workflow(...)` to always validate sampled linking-map rows and to trigger fallback only when linking-map schema fails or linking-map is empty.
- Return `triangulation_diagnosis` directly in the validation JSON payload so downstream chat/reporting can display one deterministic diagnosis string without reparsing logs/config.
- Use report discovery by run/sandbox/supplier tokens under `OUTPUTS/FBA_ANALYSIS/financial_reports` so fallback can answer both "expected" and "exists" in one pass.

## 2026-03-02 expected output verification design
- Kept deep schema validation focused on linking_map rows only; removed cached_products deep schema sampling from standard workflow validation.
- Preserved triangulation fallback path and broadened trigger to run when any validation errors exist, including missing expected outputs.

## 2026-03-05 - Regression root-cause decisions

- Classified the `cancel_run` problem as a control-flow/prompt interaction bug, not a missing `st.rerun()` or uncleared `pending_tool_call` bug.
- Classified `ask_clarify` behavior as prompt-policy overconstraint (`never guess paths` + `missing => ask_clarify`) rather than tool execution failure.
- Treated prompt claim "backend resolves empty cancel run_id from last_run_id" as inconsistent with current executor implementation, which resolves from job/status files.

## 2026-03-05 - Follow-up decision from external plan review

- Treat external findings as partially stale: keep accepted fixes marked as complete (`ask_clarify` terminal persistence, category-cap translation, deterministic expected-output merge, worker `.env` inheritance), and keep only the cancel-loop post-approval control-flow behavior as actionable.
