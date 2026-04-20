# Revert Tracking - API key placement for stale-data-workflow

Date: 2026-04-15
Scope: Surgical key placement and retrieval guidance only.

## Planned Files and Scope

1. `.env`
- Intended change: Add provider keys required by stale-data-workflow (`FIRECRAWL_API_KEY`, `TAVILY_API_KEY`, `APIFY_TOKEN`, optional `SCRAPIFY_API_KEY`).
- Validation: Read back file and verify keys present exactly once.
- Restore source: `backup/api_keys_stale_workflow_20260415/.env`
- Validation status: Completed (keys read back and verified)

2. `.env.example`
- Intended change: Add placeholder entries for the same workflow keys so setup is deterministic on new machines.
- Validation: Read back section and confirm placeholders added.
- Restore source: `backup/api_keys_stale_workflow_20260415/.env.example`
- Validation status: Completed (placeholders read back and verified)

3. `workflows/stale-data-workflow/SKILL.md`
- Intended change: Add deterministic key retrieval order for Phase 5 and explicit env var names.
- Validation: Read back and confirm section appears and aligns with current budgets.
- Restore source: `backup/api_keys_stale_workflow_20260415/workflows_stale-data-workflow_SKILL.md`
- Validation status: Completed (retrieval-order section and declaration update verified)

4. `.opencode/skills/stale-data-workflow/SKILL.md`
- Intended change: Mirror key retrieval section so OpenCode skill copy stays aligned.
- Validation: Read back and confirm mirrored section present.
- Restore source: `backup/api_keys_stale_workflow_20260415/.opencode_skills_stale-data-workflow_SKILL.md`
- Validation status: Completed (retrieval-order section and declaration update verified)

## Non-Goals

- No changes to protected `tools/*` or `run_custom_*.py` files.
- No workflow logic changes outside key retrieval instructions.
- No sandbox/validation reruns in this pass.
