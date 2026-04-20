# Revert Tracking — Stale Skill Update 2026-04-15

## Scope
Update stale-data-workflow SKILL.md and EXECUTION_ENFORCEMENT.md to incorporate:
1. Restructured output directory layout (subfolders for CSVs, scripts, categories)
2. Single final JSON product list at PRODUCTS_LISTS root
3. Updated tool budget with empirical evidence (Firecrawl 15, Tavily 3, Apify 2, Scrapfly 0, Playwright 6)
4. Firecrawl credit flexibility note
5. Scrapfly excluded until valid key confirmed

## Files Backed Up

| # | Original | Backup | Change Scope |
|---|----------|--------|-------------|
| 1 | `workflows/stale-data-workflow/SKILL.md` | `backup/stale_skill_update_20260415/SKILL_workflows.md` | Phase 5 tool budget, Phase 6 output layout, API keys, Firecrawl flexibility note |
| 2 | `.opencode/skills/stale-data-workflow/SKILL.md` | `backup/stale_skill_update_20260415/SKILL_opencode.md` | Identical changes as #1 (force-synced from workflows copy) |
| 3 | `workflows/stale-data-workflow/references/EXECUTION_ENFORCEMENT.md` | `backup/stale_skill_update_20260415/EXECUTION_ENFORCEMENT.md` | Phase 6 file layout, Phase 5 validation tool reference |

## Validation
- [x] Re-read Phase 5 and Phase 6 of workflows SKILL.md after edit — confirmed
- [x] Re-read Phase 5 and Phase 6 gates of EXECUTION_ENFORCEMENT.md after edit — confirmed
- [x] Diff both SKILL.md copies to confirm identical content — `fc` reports "no differences encountered"
- [x] Verify no Python scripts modified — confirmed (only .md files changed)
- [x] Verify no .env changes in this pass — confirmed (Scrapfly key was updated before this pass)

## Rollback
Copy backup files from `backup\stale_skill_update_20260415\` back to original locations:
- `SKILL_workflows.md` → `workflows\stale-data-workflow\SKILL.md`
- `SKILL_opencode.md` → `.opencode\skills\stale-data-workflow\SKILL.md`
- `EXECUTION_ENFORCEMENT.md` → `workflows\stale-data-workflow\references\EXECUTION_ENFORCEMENT.md`