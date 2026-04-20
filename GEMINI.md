# Amazon FBA Agent System — Project Rules

Read the full project architecture, contributor guide, and absolute constraints from
the `AGENTS.md` file in the root of this repository **before** any coding, editing,
or analysis task that involves Python scripts, workflows, state files, or configuration.

This includes: workflow changes, financial calculator edits, supplier scraper updates,
state management, browser automation, and any cross-file refactoring.

---

## Antigravity / Gemini CLI — Specific Notes

### GitNexus Index Status

This project is indexed by GitNexus as **Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-** (11674 symbols, 27137 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

- Re-index: `npx gitnexus analyze`
- Check freshness: `npx gitnexus status`
- Generate docs: `npx gitnexus wiki`

### Global Skills Directory

All 59 Antigravity skills are installed at:
`C:\Users\chris\.gemini\antigravity\skills\`

A full index is at:
`C:\Users\chris\.gemini\antigravity\skills\OPTIMIZED_SKILLS_MANIFEST.md`

Key skills available (invoke by `@skill-name` or read SKILL.md):
- `supplier-onboarding` — Guided supplier onboarding (7-step)
- `stale-data-workflow` — Stale Amazon FBA data revalidation
- `playwright-skill` — Browser automation & scraping
- `browser-automation` — Selectors, waiting, anti-detection
- `systematic-debugging` — Root cause analysis before fixes
- `deep-research` — Autonomous research with synthesis
- `firecrawl-scraper` — Deep web extraction via Firecrawl API
- `apify-ecommerce` — E-commerce product data extraction

### Project-Level Skill and Rule Directories

```
.agents/skills/          # Project-scoped skills (Antigravity reads these)
  gitnexus/              # GitNexus skills (exploring, debugging, impact, refactoring, cli)
  mcp-builder/           # MCP server creation guide
  supplier-onboarding/   # Supplier onboarding workflow
  ui-ux-pro-max/         # UI/UX design intelligence

.agent/rules/            # Antigravity sidebar rules
  fba-architecture.md    # model_decision trigger → reads AGENTS.md for FBA tasks
  guide.md               # General guide
```

### Graphify (Gemini / Antigravity)

Use Graphify v3 in this repo with the Gemini installer path:

1. Build/update graph:
   - `/graphify .`
2. Install always-on Graphify behavior for Gemini/Antigravity:
   - `graphify gemini install`

Expected integration behavior:
- `GEMINI.md` receives Graphify usage rules
- `.gemini/settings.json` gets a `BeforeTool` hook so graph context is injected before file-read tool calls
- If a hook is unavailable in a client, instructions in `GEMINI.md` are the fallback mechanism

Operational rule for Antigravity in this project:
- Read `graphify-out/GRAPH_REPORT.md` before architecture/codebase answers
- If present, prefer `graphify-out/wiki/index.md` for navigation
- After code edits, keep graph fresh via either:
  - `graphify hook install` (post-commit/post-checkout)
  - `/graphify ./raw --watch` (continuous sync)
