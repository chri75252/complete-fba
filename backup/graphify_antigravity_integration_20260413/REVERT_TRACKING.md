# REVERT_TRACKING.md

## Change Set: Graphify Antigravity/OpenCode/Codex integration guidance
Date: 2026-04-13

## Scope

- Update `AGENTS.md` graphify section with official Graphify v3 cross-CLI install behavior
- Update `GEMINI.md` with Antigravity/Gemini-specific Graphify always-on workflow

## Files and backup sources

| File | Backup copy |
|---|---|
| `AGENTS.md` | `backup/graphify_antigravity_integration_20260413/AGENTS.md` |
| `GEMINI.md` | `backup/graphify_antigravity_integration_20260413/GEMINI.md` |

## Exact additions

### AGENTS.md
- Added **Cross-CLI Always-On Integration (Graphify v3)** subsection
- Added install commands:
  - `graphify codex install`
  - `graphify opencode install`
  - `graphify gemini install`
- Added **Antigravity / Gemini Specific Behavior** subsection
- Added **Recommended Maintenance** subsection (`graphify hook install` / `--watch`)

### GEMINI.md
- Added **Graphify (Gemini / Antigravity)** section
- Added workflow:
  1. `/graphify .`
  2. `graphify gemini install`
- Added operational rules for reading `GRAPH_REPORT.md`, preferring `wiki/index.md`, and keeping graph fresh

## Validation

- Markdown-only edits, no code changes
- Paths and commands aligned with Graphify v3 official README

## Restore commands

```cmd
copy "backup\graphify_antigravity_integration_20260413\AGENTS.md" "AGENTS.md"
copy "backup\graphify_antigravity_integration_20260413\GEMINI.md" "GEMINI.md"
```
