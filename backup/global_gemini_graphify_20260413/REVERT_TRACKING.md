# REVERT_TRACKING.md

## Change Set
Global Gemini/Antigravity Graphify always-on integration (manual surgical patch)
Date: 2026-04-13

## Source of truth used
- Graphify v3 upstream `graphify/__main__.py`
  - `_GEMINI_HOOK`
  - `_GEMINI_MD_SECTION`

## Files modified

| File | Change |
|---|---|
| `C:\Users\chris\.gemini\settings.json` | Added `hooks.BeforeTool` entry using upstream Graphify hook matcher `read_file|list_directory` and graph reminder command |
| `C:\Users\chris\.gemini\GEMINI.md` | Added project-agnostic Graphify always-on instructions for Antigravity/Gemini |

## Backup copies

| Original file | Backup file |
|---|---|
| `C:\Users\chris\.gemini\settings.json` | `backup/global_gemini_graphify_20260413/settings.json` |
| `C:\Users\chris\.gemini\GEMINI.md` | `backup/global_gemini_graphify_20260413/GEMINI.md` |

## Restore commands

```cmd
copy "backup\global_gemini_graphify_20260413\settings.json" "C:\Users\chris\.gemini\settings.json"
copy "backup\global_gemini_graphify_20260413\GEMINI.md" "C:\Users\chris\.gemini\GEMINI.md"
```

## Notes
- No project code modified
- No installer command used
- Existing settings keys (`mcpServers.context7`, `security`, `ui`, `general`, `model`) preserved
