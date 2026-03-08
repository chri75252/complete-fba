## 2026-03-01 - Chat UI reasoning + validation workflow

- `dashboard/chat_panel.py` already surfaces planner explanation during the autonomous loop (`step.tool_call.explanation`), so live reasoning can be improved without backend/tool schema changes.
- `control_plane/chat_orchestrator.py` carries explanation end-to-end in `ToolCall`, meaning UI-only rendering upgrades are sufficient for a first "Show Reasoning" release.
- `last_run_id` and `last_sandbox_supplier` are already persisted in Streamlit session state after enqueue confirmation, which is enough context for a one-click post-run review trigger.
- `get_run_outputs` + `tail_logs` + `read_repo_file` are already allowlisted and can support deterministic run validation with evidence citations.

## 2026-03-01 - Reasoning trace persistence pattern

- Streamlit output inside `st.status(...)` is transient across `st.rerun()`, so step reasoning should be copied into session state for persistence.
- Storing `agent_trace` during the loop and attaching it as `thought_trace` on the final assistant message preserves a readable thought timeline in chat history.
- `st.expander` is a better fit than `st.info` for multi-step reasoning because it keeps the trace visible on demand without flooding the main chat thread.

## 2026-03-01 - Sandbox pathing risk map

- `control_plane/tools/run_outputs.py` scans only first-level entries in `OUTPUTS/CACHE/processing_states`, `OUTPUTS/cached_products`, `OUTPUTS/FBA_ANALYSIS/linking_maps`, and `OUTPUTS/FBA_ANALYSIS/financial_reports`; moving sandbox artifacts to nested `sandboxed/` paths will make discovery return false negatives unless scanning becomes recursive.
- `dashboard/metrics_core.py` path resolution is direct and non-recursive; it expects sandbox supplier artifacts in current root locations and will not detect files moved under `sandboxed/` subdirectories without resolver changes.
- `control_plane/tools/state.py`, `control_plane/tools/cached_products.py`, `control_plane/tools/linking_map.py`, and `control_plane/tools/financial.py` all use fixed root paths and would silently stop finding sandbox outputs if only write-path logic changes.

## 2026-03-01 - Expected output determinism learnings

- `control_plane/chat_orchestrator.py` already has deterministic placeholder substitution via `_substitute_expected_output_placeholders(...)`, so reliability should come from backend-generated templates rather than asking the model to invent concrete paths.
- `control_plane/chat_orchestrator.py` fallback expected outputs are currently hardcoded and not derived from resolver utilities, which creates drift risk when filesystem layout changes.
- `control_plane/checklists.py` expected output templates currently use `__sandbox_<id>` while active run creation uses `sandbox__{run_id[:8]}`; this formatting mismatch can confuse preview/verification messaging.

## 2026-03-01 - Deterministic validation design learnings

- `control_plane/worker.py` status refresh already captures deterministic counts (`linking_map_entries`, `matched_asins`, `amazon_cache_files`) for product-list-refresh jobs; a shared validator can reuse this pattern for full workflow jobs.
- `control_plane/tools/run_outputs.py` is deterministic but currently artifact-presence only; quality checks (missing keys, 404/captcha/error signatures, URL-vs-price sanity) should be implemented in a dedicated backend tool instead of model-side file interpretation.

## 2026-03-01 - Run integrity validator learnings

- `control_plane/tools/run_validation.py` can deterministically resolve run-scoped artifacts by prioritizing `run_id[:8]` sandbox pattern matches, then falling back to supplier/status hints.
- Deterministic sampling is stable when seeded by `f"{run_id}:{namespace}:{len(rows)}"`, which makes repeated checks reproducible for the same artifact files.
- Linking map and cached product payloads are both schema-variant in practice (`list` vs `dict` / `dict.products`), so normalization before counting/sampling avoids false negatives.

## 2026-03-02 - Onboarding + full-product validation learnings

- `control_plane/tools/run_validation.py` currently validates only sampled URL/price fields, so it needs a schema-level full-object check to satisfy product entry quality expectations.
- Onboarding artifact conventions are split across files: `run_custom_{supplier}.py` runner and workflow checks in `control_plane/checklists.py`, and auth helper generation at `tools/{supplier}/supplier_authentication_service.py` in `utils/supplier_onboarding_wizard.py`.
- Reliable onboarding validation should derive `login_required` from onboarding job payload/wizard input first, then `workflows.*.authentication_required`, and only then optional selector/login hints as fallback.

## 2026-03-02 - Strict linking-map validation + fallback triangulation learnings

- `control_plane/tools/run_validation.py` currently validates sampled cached-product rows but does not enforce strict schema checks on sampled linking-map rows; this gap lets structurally invalid matches pass as successful runs.
- For linking-map integrity, high-signal fields should be hard-validated (`supplier_ean`, `supplier_url`, `supplier_price`, `amazon_asin`, `amazon_price`, `match_method`) before any success result is emitted.
- Fallback triangulation should trigger deterministically when linking-map rows are empty OR any sampled linking-map row fails schema checks, then combine evidence from logs + config + artifact state into one diagnosis string.

## 2026-03-02 - Triangulation fallback implementation learnings

- `control_plane/tools/run_validation.py` now treats linking-map validation as first-class schema validation and runs it on deterministic sampled rows before marking workflow success.
- High-signal schema checks are now explicit in `_validate_linking_map_row(...)`: EAN must be digit string, supplier/amazon URLs must be http(s), ASIN must be 10-char alphanumeric, and supplier/amazon prices must coerce to float.
- The cascade fallback now reads `config/system_config.json` `system.financial_report_batch_size`, compares against `len(linking_map_rows)`, and emits whether a financial report should have been generated plus whether one was found.

## 2026-03-02 run_validation expected-outputs checks
- Mirrored expected output derivation by job type inside run validation for run_workflow and run_product_list_refresh.
- Added physical filesystem verification for each expected output path; wildcard patterns are checked with pathlib.Path.glob and require at least one matching file.
- Validation payload now exposes missing_expected_files for deterministic downstream diagnosis.

## 2026-03-05 - Chat UI regressions (cancel loop + ask_clarify)

- In `dashboard/chat_panel.py`, `Confirm execute` already clears `pending_tool_call` and calls `st.rerun()`; the repeat-confirm loop is not caused by missing rerun/clear logic.
- The loop is driven by automatic resume (`agent_scratchpad` + `agent_user_text`) immediately re-entering `_run_agent_loop(...)` after write approval, which can re-propose the same write action.
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` includes strict hard rules (`if missing -> ask_clarify`, `never guess file paths/run IDs`) that bias the planner toward clarification instead of discovery tools.
- The prompt says empty `run_id` on `cancel_run` should resolve from `last_run_id`, but `execute_tool_call` resolves context from filesystem folders and does not read Streamlit `last_run_id` directly.

## 2026-03-05 - Cross-check of external report vs current code

- `ask_clarify` is now treated as a terminal planner tool path in `control_plane/chat_orchestrator.py`: it executes once, then returns `AgentStep(kind="final_answer", ..., result=...)`, and that result is persisted into `chat_messages` by `dashboard/chat_panel.py`.
- Deterministic expected-output handling is active in both planner paths: fallback outputs are computed in Python, placeholder-substituted with run/sandbox IDs, then merged with LLM-proposed outputs with dedupe.
- Category-cap translation for "N per category across multiple category URLs" is now implemented in orchestrator and pending-param edit logic by multiplying `max_products = max_products_per_category * url_count` when total-intent is not explicit.
- Worker env propagation is wired: `control_plane/worker.py` calls `ensure_llm_env()` and passes `env=os.environ.copy()` to `subprocess.Popen`, so `.env` values are inherited at process spawn time.
