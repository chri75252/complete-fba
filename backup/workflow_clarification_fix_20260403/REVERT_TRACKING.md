# REVERT_TRACKING

- Date: 2026-04-03
- Reason: workflows trigger guidance + clarification-to-JSON routing hardening
- Backup root: backup/workflow_clarification_fix_20260403

| File | Backup Path | Validation Status |
| --- | --- | --- |
| `dashboard_v2_redesign/templates/index.html` | `backup/workflow_clarification_fix_20260403/dashboard_v2_redesign/templates/index.html` | Completed |
| `control_plane/tools/clarify.py` | `backup/workflow_clarification_fix_20260403/control_plane/tools/clarify.py` | Completed |
| `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` | `backup/workflow_clarification_fix_20260403/control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` | Completed |
| `control_plane/chat_orchestrator.py` | `backup/workflow_clarification_fix_20260403/control_plane/chat_orchestrator.py` | Completed |

## Validation Evidence

- `python -m py_compile control_plane/chat_orchestrator.py control_plane/tools/clarify.py dashboard_v2_redesign/api.py` passed.
- Targeted assertions passed for resume phrase detection, UUID validation, product-list intent checks, and `ask_clarify` questions.
- Playwright verification passed on `http://127.0.0.1:8001/` Workflows tab with visible "Prompt Triggers Quick Guide" section.
