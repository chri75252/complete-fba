## 2026-02-26

- Blocking issue: `enqueue_onboarding_job` writes payload with `"supplier_domain": ""` in `control_plane/tools/repo_files.py`, which is incompatible with worker preflight checks.
- Capability gap: Chat planner cannot fully follow Step 0 and Step 2 from the onboarding skill without write permissions to `setup/`, `temp/`, and onboarding config destinations.
- Capability gap: onboarding validation references in SKILL require reading `docs/` and `sample_data/`, currently not guaranteed by read allowlists.
- Prompt/schema drift: planner prompt text says `path` for write tool, executor expects `rel_path`.
- Interface mismatch: enqueue_onboarding schema/examples in chat_orchestrator omit supplier_domain, but worker hard-requires non-empty supplier_domain and fails jobs otherwise.
- Validation mismatch: tool_param_validation strips unknown params for enqueue_onboarding, so even if planner emits supplier_domain it is discarded unless validation is updated.
- Coverage gap for SKILL verification: read allowlist currently misses docs/ and sample_data/, which blocks Step 4 comparison against reference runners/auth helpers.
- Critical planner-design mismatch: SYSTEM_INSTRUCTIONS_CHAT_PLANNER enforces exactly one tool per turn, so a single response cannot execute read skill file + read setup file + write staged JSON + enqueue onboarding.
- Config-path drift in wizard: `atomic_move_to_final()` writes one categories path to `workflows.*.categories_config_path`, but `generate_mode()` later calls `register_workflow()` with a different `categories_path` value, risking path inconsistency despite atomic writes.

## 2026-02-27

- Confirmed architectural limitation for autonomous chaining in Chat panel: one tool plan and one execution per prompt/turn.
- If onboarding tests assume LangChain-style internal loops (tool->observe->tool...), they will fail without explicit user "continue" style turns or a new backend loop implementation.
- Verification blocker observed during this task: `pytest` cannot run due to existing `SyntaxError: source code string cannot contain null bytes` from `tests/conftest.py` (pre-existing repo issue, unrelated to prompt-lock edits).
