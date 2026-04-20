# Revert Tracking - API budget split update

Date: 2026-04-15
Purpose: Add provided Apify key and set explicit per-run action split in stale-data workflow docs.

## Files and Scope

1. `.env`
- Change: update `APIFY_TOKEN` to user-provided key.
- Validation: read-back confirms exact value present.
- Restore source: `backup/api_budget_split_20260415/.env`
- Validation status: Completed

2. `workflows/stale-data-workflow/SKILL.md`
- Change: add explicit per-run tool action split for Firecrawl/Tavily/Scrapify/Apify in Phase 5.
- Validation: grep/read-back confirms new split section.
- Restore source: `backup/api_budget_split_20260415/workflows_stale-data-workflow_SKILL.md`
- Validation status: Completed

3. `.opencode/skills/stale-data-workflow/SKILL.md`
- Change: mirror action split section for OpenCode skill copy.
- Validation: grep/read-back confirms new split section.
- Restore source: `backup/api_budget_split_20260415/.opencode_skills_stale-data-workflow_SKILL.md`
- Validation status: Completed

4. `OUTPUTS/PRODUCTS_LISTS/tool_budget_recalibration_report_20260415_0225.md`
- Change: add empirical benchmark report and revised action split rationale.
- Validation: file read-back and backup copy created.
- Restore source: `backup/api_budget_split_20260415/tool_budget_recalibration_report_20260415_0225.md`
- Validation status: Completed

## Non-goals

- No edits to protected `tools/*` or `run_custom_*.py`
- No runtime execution changes, only key placement + workflow budgeting guidance
