# Draft: Control Plane Chat/UI remaining open issues (2026-02-11)

## Requirements (confirmed)
- Plan remaining items A–F from user’s open-issues report.
- Already implemented/verified (do not re-plan unless conflicts found):
  - run_id placeholder normalization
  - limits parity in `control_plane/chat_orchestrator.py` and `dashboard/chat_panel.py`
  - `_safe_json_loads` in `control_plane/llm/providers.py` and `control_plane/llm_provider.py`
  - try/except around LLM `generate_json`
  - sandbox credential aliasing
- Remaining items to plan/execute where safe:
  - (A) `dashboard/pages/01_Operator_Control_Plane.py`: sandbox supplier isolation
  - (B) `config/system_config.json`: consider setting `workflows.efghousewares_workflow.authentication_required` true→false (requires validation)
  - (C) `dashboard/chat_panel.py`: add intercepts (cancel run command pre-LLM; stop-at-N during running job; both-should-be-N regex)
  - (D) `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`: add cancel_run instruction; if no run_id set `run_id=""` and never use `<run-id>`
  - (E) `control_plane/chat_orchestrator.py`: remove products_path placeholder `C:/path/to/products_subset.json` (and onboarding placeholders) to avoid LLM echo
  - (F) `control_plane/chat_orchestrator.py`: wrap base config load in enqueue_run with try/except and return `{ok:false, error}`

## Constraints / Guardrails (confirmed)
- No git operations.
- Do not edit anything under `tools/` or any `run_custom_*.py`.
- Back up each modified file to `backup/<reason>_20260211/` preserving relative paths.
- Avoid adding memo-comments.

## Technical Decisions
- TBD (pending codebase pattern review for sandbox supplier isolation + chat intercept syntax)

## Research Findings
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\pages\01_Operator_Control_Plane.py:98`: Run Builder always creates `sandbox_supplier = f"{supplier_domain}__sandbox__{run_id[:8]}"` and writes subset/config overrides; currently it does not isolate pasted/parsed categories by supplier domain.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py:319`: Chat UI already intercepts cancel commands pre-LLM (regex: `cancel|stop|kill|abort|terminate` + `run|job|process`) and immediately calls `cancel_run` via `execute_tool_call`.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py:350`: Chat UI already detects `stop at/after N products` while a run exists and explicitly refuses (advises cancel + restart); there is no mid-run limit override mechanism.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\dashboard\chat_panel.py:275`: When editing a pending run tool-call, setting `max_products` implicitly sets `max_products_per_category` to the same N if per-cat wasn’t explicitly set (existing “both=N” behavior).
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\prompts\SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md:12`: Planner currently says “If required information is missing, choose ask_clarify” and “Never guess … run IDs”; it does not mention `cancel_run` even though tool schema allows it.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py:277`: Tool schema includes placeholders for onboarding and product refresh paths (e.g. `C:/path/to/products_subset.json`, `C:/path/to/onboarding_input.json`) which can be echoed by the LLM.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\control_plane\chat_orchestrator.py:710`: `enqueue_run` already wraps base config load in `try/except` and returns `{ok:false, error}` on parse failure.
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\config\system_config.json:311`: `workflows.efghousewares_workflow.authentication_required` is currently `true`.
- Best-practice guidance: deterministic command parsing *before* LLM, prefer explicit command prefix (e.g. `/cancel`), and avoid unresolved placeholders in prompts (validate templates and remove sentinel placeholders).

## Open Questions
- Exact expected behavior for sandbox supplier isolation (A).
- Whether config change (B) is desired after validation, or only recommended.
- Exact “cancel run commands” syntax / examples to intercept (C).
- Definition of “stop-at-N” semantics (C) when job already running.

## Scope Boundaries
- INCLUDE: Only A–F items listed above.
- EXCLUDE: Any modifications to protected files (`tools/*`, `run_custom_*.py`) and unrelated refactors.
