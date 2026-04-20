# REVERT TRACKING

Backup reason: api_key_env_fallback_20260419
Date: 2026-04-19

## Planned files

| Target file | Change scope | Backup source | Planned validation |
|---|---|---|---|
| workflows/stale-data-workflow/SKILL.md | Add explicit fallback lookup to `C:\Users\chris\.env` in API key retrieval order | backup/api_key_env_fallback_20260419/workflows/stale-data-workflow/SKILL.md | Re-read lines around API key retrieval section |
| .opencode/skills/stale-data-workflow/SKILL.md | Mirror same fallback lookup for active project skill copy | backup/api_key_env_fallback_20260419/.opencode/skills/stale-data-workflow/SKILL.md | Re-read lines around API key retrieval section |
| C:\Users\chris\.config\opencode\skills\stale-data-workflow\SKILL.md | Mirror fallback lookup for global project-level opencode skill copy to avoid drift | backup/api_key_env_fallback_20260419/external/C_Users_chris_.config_opencode_skills_stale-data-workflow_SKILL.md | Re-read lines around API key retrieval section |
| workflows/fba_product_validation_prompt.md | Update API/tool preflight text to include same fallback behavior | backup/api_key_env_fallback_20260419/workflows/fba_product_validation_prompt.md | Re-read Phase 0 API/tool preflight lines |
| C:\Users\chris\.env | Append durable backup keys and notes | backup/api_key_env_fallback_20260419/external/C_Users_chris_.env | Re-read appended section only |
| C:\Users\chris\.config\opencode\scripts\register_api_keys.ps1 | New bootstrap script to register user env vars from `C:\Users\chris\.env` | N/A (new file) | Read created file |

## Non-goals
- No opencode.json MCP changes
- No Playwright MCP enablement changes
- No git operations
- No hardcoding secrets into SKILL.md or prompt files
