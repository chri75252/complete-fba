## 2026-03-02 - Current issues

- `SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md` contains conflicting guidance: it allows autonomous multi-step behavior but also states "Choose exactly ONE tool," which weakens loop reliability.
- `run_readiness_check` and `onboarding_sanity_check` are described in prompt tool schemas and implemented in `execute_tool_call`, but are missing from `READ_TOOLS`, so planner validation can reject them.
- Read-tool executions in the loop are not audited via `audit_tool_call`; only approved write actions are audited, leaving a trace gap for autonomous analysis steps.
