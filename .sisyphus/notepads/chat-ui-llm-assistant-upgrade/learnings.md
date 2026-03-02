# Learnings

## 2026-02-18
- `dashboard/chat_panel.py` passes `st.session_state['chat_messages']` to `control_plane.chat_orchestrator.plan_tool_call(..., chat_history=...)` to keep context in-session only.
- `control_plane/chat_orchestrator.py` sanitizes history before prompt injection via `_sanitize_chat_history(...)` (default last 10 messages; truncates per-message content; drops large `tool_result` payloads and keeps only a small scalar summary).
- Planner prompt includes `Conversation history` as JSON to keep parsing deterministic and avoid leaking huge tool outputs.

## 2026-02-18 (Task 3: Token Budget + Truncation - VERIFIED COMPLETE)
- Task 3 verification: Centralized truncation/token-budget logic is already robust:
  - History window: `_sanitize_chat_history(max_messages=10, max_content_chars=2000, max_total_chars=12000)`
  - Tool result summarization: extracts only key scalar fields (ok, error, run_id, sandbox_supplier, message, job_path, log_path) from tool_result dicts
  - Responder truncation: `_truncate_for_prompt(result, max_str=1000, max_list=10, max_dict_items=30, depth=2)`
  - Display truncation: `_truncate_value(..., max_str=5000, max_list=50, max_dict_items=50)` in dashboard
- py_compile verification: PASSED for dashboard/chat_panel.py and control_plane/chat_orchestrator.py
- No refactoring needed; implementation already satisfies Task 3 acceptance criteria:
  - Large tool results do not blow up prompt size
  - Assistant remains responsive with history window

## 2026-02-18 (Task 4: OpenAI-Compatible Provider generate_text Parity)
- Added `generate_text` method to `OpenAiCompatProvider` in `control_plane/llm/providers.py`
- Method mirrors `OllamaProvider.generate_text` pattern:
  - Uses OpenAI-compatible `/v1/chat/completions` endpoint
  - temperature=0.3 for natural language generation
  - Returns plain text string (no JSON parsing)
  - Handles HTTP errors with raise_for_status()
- Responder phase already checks `getattr(provider, "generate_text", None)` at line 1415 in chat_orchestrator.py
- Planner still uses `generate_json` for deterministic JSON tool selection (unchanged)
- py_compile verification: PASSED for control_plane/llm/providers.py, control_plane/chat_orchestrator.py, dashboard/chat_panel.py
- Provider parity achieved: both OllamaProvider and OpenAiCompatProvider now support generate_text()

## 2026-02-18 (Task 5: Route Category URL Prompts Through The Planner)
- Removed the deterministic category URL short-circuit in `control_plane/chat_orchestrator.py:plan_tool_call` (no immediate `enqueue_run` return just because URLs exist).
- Category URLs are still extracted and passed into the planner prompt via a new `Planner hints` JSON block.
- The hints include (when available): `detected_category_urls`, `inferred_supplier_domain`, `suggested_workflow_key`, `suggested_runner_script`, and `parsed_constraints`.
- Verification: `python -m py_compile control_plane/chat_orchestrator.py dashboard/chat_panel.py control_plane/llm/providers.py` passes.

## 2026-02-18 (Task 6: Remove Dashboard Cancel Regex Bypass)
- Removed the `cancel_pat` short-circuit in `dashboard/chat_panel.py` so cancel/stop requests route through `plan_tool_call(...)` and the existing write confirmation gate.

## 2026-02-18 (Task 7: Update Planner Instructions for Multi-Turn + Assistant-Like Behavior)
- Updated `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` with:
  - **Multi-Turn Context section**: Explains how to use `Conversation history` JSON to resolve ambiguous references, remember constraints, and handle clarifying questions.
  - **Category URL Handling section**: Replaced "highest priority" auto-enqueue rule with nuanced guidance:
    - URLs are context inputs, NOT automatic run triggers
    - Explicit examples of informational URL prompts that should NOT enqueue
    - Explicit examples of execution prompts that SHOULD enqueue
  - **max_products Constraint Handling section**: Added rule to NOT default to 0/2000 unless user explicitly says "unlimited"/"no limit"/"all products"
  - Preserved JSON output contract and tool schema usage intact
- py_compile verification: PASSED for control_plane/chat_orchestrator.py, dashboard/chat_panel.py, control_plane/llm/providers.py
- This instruction update aligns with Task 5 (code routing) and Task 6 (cancel routing) behavior changes
- Output JSON contract is now strict: only `tool`, `params`, and `explanation`.

## 2026-02-18 (Task 8: Allowlist-Based Repo Reads For Assistant)
- Added allowlist enforcement in `control_plane/tools/repo_files.py` for `read_repo_file` and `list_repo_dir`.
- Existing secret-path blocklist remains active via `control_plane/rd2_policy.py:is_blocked_path` (checked before allowlist decisions).
- Allowlisted read prefixes: `OUTPUTS/CONTROL_PLANE/{status,logs,jobs,diagnostics,index}/...`, `OUTPUTS/CACHE/processing_states/...`, `OUTPUTS/FBA_ANALYSIS/{linking_maps,financial_reports}/...`, `logs/...`.
- Allowlisted config reads: `config/system_config.json`, `config/*_categories.json`, `config/*_workflow_categories.json`, `config/*_system_config_additions.json`, `config/test_*.json`, `config/supplier_configs/*.json`.
- Disallowed paths return deterministic `path_not_allowed` with a stable `allowed` hint list; no stack traces.

## 2026-02-18 (Task 9: Tight Schema Validation For Tool Params)
- Centralized tool param validation added in `control_plane/tools/tool_param_validation.py` and applied in `control_plane/chat_orchestrator.py` before tool execution.
- Validation is enforced for: `enqueue_run`, `enqueue_product_list_refresh`, `query_financial`, `enqueue_onboarding`, `cancel_run`.
- Rejections are deterministic and tool-safe: `ok=False` plus explicit `error` (human message), `code` (stable), `tool`, `field`, and `message`.
- Numeric coercion is strict-but-robust: accepts ints, integer-valued floats, and numeric strings; rejects bools and non-integer floats.

## 2026-02-18 (Task 10: Pending Preview Expected Outputs Normalization)
- `control_plane/chat_orchestrator.py:plan_tool_call` now assigns a backend-generated `run_id` for `enqueue_run` and `enqueue_product_list_refresh` before the write-confirmation preview is shown.
- `expected_outputs` is normalized by substituting `<run_id>` / `{run_id}` and `<id>` (using `run_id[:8]`); if omitted, deterministic fallback paths are provided.
