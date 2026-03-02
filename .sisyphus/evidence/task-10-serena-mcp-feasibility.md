# Task 10 - Serena MCP Read-Only Feasibility

## Verdict

Feasible with low implementation risk if integrated as an optional read backend behind existing allowlist and redaction policy.

## Current State

- Chat assistant read tools currently flow through `control_plane/tools/repo_files.py` and are guarded by:
  - blocklist/redaction in `control_plane/rd2_policy.py`
  - allowlist gating in `control_plane/tools/repo_files.py`
- Planner/dispatcher path is in `control_plane/chat_orchestrator.py`.
- No unrestricted shell/file execution is required for read operations.

## Integration Model (Recommended)

1. Keep existing tools (`read_repo_file`, `list_repo_dir`) as primary API contract.
2. Add optional backend switch (env/config) to resolve reads via Serena MCP when enabled.
3. Always enforce local allowlist + `is_blocked_path` before MCP query dispatch.
4. Always run `redact_secrets(...)` on returned content before exposing to chat.
5. Fall back to local filesystem read if MCP is unavailable.

## Safety Guardrails

- Never bypass allowlist prefixes or blocked-path patterns.
- Never allow external path traversal (outside repo root).
- Never expose credentials, `.env`, `.git`, or auth files.
- Return deterministic errors (`path_not_allowed`, `blocked_path`, `not_found`, `read_failed`).

## User-Facing Behavior

- No change in tool names or planner output schema.
- Optional quality gain: better retrieval speed/indexing for large repos.
- No change to write confirmation gate or job-execution model.

## Rollout Sequence

1. Add MCP adapter layer under `control_plane/tools/`.
2. Wire adapter behind feature flag.
3. Add parity tests against local read behavior.
4. Enable in staged mode and monitor error rates.
