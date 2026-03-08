## 2026-03-02 - Architectural decisions

- Keep all upgrade logic constrained to `dashboard/chat_panel.py`, `control_plane/chat_orchestrator.py`, and `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`.
- Use a deterministic loop state machine (idle -> running -> waiting_approval -> running -> final/error) stored in Streamlit session state.
- Preserve strict write safety: write tools never auto-run; every mid-loop write intent is serialized into `pending_tool_call` and executed only after explicit user approval.
