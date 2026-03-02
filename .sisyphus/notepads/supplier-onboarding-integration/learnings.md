## 2026-02-26

- `enqueue_onboarding` currently fails at runtime because queued onboarding jobs have `supplier_domain` set to an empty string in `control_plane/tools/repo_files.py`, while worker validation in `control_plane/worker.py` rejects jobs missing `supplier_domain`.
- `read_repo_file` allowlists currently block key onboarding paths, including `.claude/skills/`, `setup/`, and `temp/`, which prevents the planner from reading SKILL instructions and setup inputs through the chat tool layer.
- `write_output_file` currently writes only to `OUTPUTS/CONTROL_PLANE/reports` and `OUTPUTS/PRODUCTS_LISTS`, so Step 0/2 onboarding file generation (`setup/*.json`, `temp/*.json`, `config/*.json`) cannot be completed through Chat UI tools without allowlist expansion.
- Planner instructions mention `write_output_file` should use `path`, but runtime schema/handler uses `rel_path`; this mismatch can cause empty path failures unless alias handling or prompt correction is added.
- Full-fidelity Step 0/2 execution from SKILL requires write access beyond reports: setup/*.json, temp/*_wizard_input.json, and optionally config/supplier_configs/*.json if not delegating file generation to wizard.
- Minimal-safe onboarding mode can avoid direct config writes by generating one wizard input JSON and delegating all config/runner creation to utils/supplier_onboarding_wizard.py.
- Planner currently enforces one-tool-per-turn, so onboarding must be modeled as a deterministic multi-turn sequence using read_repo_file/list_repo_dir/write_output_file/enqueue_onboarding plus ask_clarify for missing fields.
- `write_output_file` is a full-file writer with path allowlist checks only; it is not a JSON patch/merge tool and provides no schema-aware protection for partial updates.
- `supplier_onboarding_wizard.py` performs whole-document `system_config.json` updates via parse-modify-save using `WindowsSaveGuardian.save_json_atomic`, which is the only atomic/structured path currently present for onboarding config injection.
- Task 4 completed: Added new section "## Executing the Supplier Onboarding Skill" to `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` with the 5-step workflow (read SKILL.md, ask for raw .txt file, format to JSON, write to staging dir via write_output_file, use enqueue_onboarding).

## 2026-02-27

- Chat UI is single-turn tool orchestration: `plan_tool_call()` returns one `ToolCall`, and `render_chat_panel()` executes at most one tool per user input before rerun.
- There is no autonomous loop that feeds tool result back into planner for immediate next tool selection in the same turn.
- This behavior explains onboarding Skill stalls after reading `SKILL.md`: the model can select `read_repo_file` once, but step chaining to `setup/stationery_test.txt` requires another user turn.
- `read_repo_file` supports large files up to `DEFAULT_MAX_BYTES = 1_000_000`, so the stall is architecture/flow, not mainly a hard size cap.
- Implemented dynamic prompt lock for script tailoring: `_is_allowed_code_edit(rel_posix, supplier_domain)` now denies all code writes when `supplier_domain` is missing and requires fuzzy domain presence in the target path.
- `write_output_file` now accepts `supplier_domain` and forwards it into code-edit gating while keeping existing `OUTPUTS/` write-allowlist behavior intact.
- Planner tool schema now includes `supplier_domain` for `write_output_file`, and execution plumbing in `execute_tool_call` passes it through to enforce domain-locked script writes.
