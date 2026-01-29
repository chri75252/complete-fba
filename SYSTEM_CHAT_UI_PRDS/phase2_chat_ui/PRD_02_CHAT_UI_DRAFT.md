# PRD #2 — Webchat UI (Draft)

This is a draft copied from the earlier discussion and will be finalized after PRD #1 is implemented.

## Goal
Add a chat UI on the same page as the existing dashboard that can:
- answer questions about outputs (financial reports, linking maps, caches)
- start new runs safely (via control-plane job manifests)
- run supplier onboarding (via wizard session protocol)
- monitor progress and troubleshoot based on status + state + logs

## Non-goals
- No direct edits to core workflow logic beyond Phase 1 hooks.
- No autonomous code patching.

## UX
- Integrate into `dashboard/app_fixed.py` via `st.tabs()`:
  - Dashboard (existing)
  - Chat (new)
  - Jobs/History (optional)

## LLM
- LLM used for intent parsing + parameter extraction.
- Deterministic tool execution via Phase 1 tool contract library.
- Write/exec tools require explicit confirmation.
- Phase 1 already introduces an optional LLM parser + provider abstraction (API + local). Phase 2 upgrades this into full chat tool-calling + agent behaviors.

## Monitoring
- Primary: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
- Secondary: processing state + logs

## Acceptance (high level)
- Query: ROI/netprofit filters
- Enqueue run: supplier + category subset
- Status updates: run_id progress
- Troubleshoot: summarize logs + state

