# Amazon FBA Agent System — Project Rules

Read the full project architecture, contributor guide, and absolute constraints from
the `AGENTS.md` file in the root of this repository **before** any coding, editing,
or analysis task that involves Python scripts, workflows, state files, or configuration.

This includes: workflow changes, financial calculator edits, supplier scraper updates,
state management, browser automation, and any cross-file refactoring.

---

## Claude Code — Specific Notes

### GitNexus Index Status

This project is indexed by GitNexus as **Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-** (14502 symbols, 23853 relationships, 300 execution flows).

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.
> A PostToolUse hook handles this automatically after `git commit` and `git merge`.

### Global Claude Code Installation

All global Claude Code data lives at `C:\Users\chris\claude-clean\`

```
C:\Users\chris\claude-clean\
  agents/                    # Global sub-agents (16 agents)
    system-architect.md      → Architecture tradeoffs
    root-cause-analyst.md    → Failure analysis
    deep-research-agent.md   → External research
    business-panel-experts.md
    backend-architect.md
    frontend-architect.md
    devops-architect.md
    performance-engineer.md
    python-expert.md
    quality-engineer.md
    refactoring-expert.md
    security-engineer.md
    requirements-analyst.md
    socratic-mentor.md
    technical-writer.md
    learning-guide.md

  commands/                  # Global slash commands
    bmad/                    → BMAD agile methodology commands
    sc/                      → SuperClaude commands
    handoff.md               → Session handoff
    index-repo.md            → Repository indexing
    pm.md                    → Project management
    research.md              → Research workflow

  skills/                    # Global skills
    agent-builder/
    bmad/
    chrome-cdp/
    learned/
    mcp-builder/

  plugins/                   # Claude Code plugins
    config.json              → Plugin config
    installed_plugins.json

  SuperClaude_Framework/     # SuperClaude framework
  claude.md                  # Global Claude instructions
  settings.json              # Global settings
```

### Project-Level Skills, Agents & Commands

```
.claude/skills/              # Project-scoped skills (read SKILL.md before using)
  gitnexus/                  # GitNexus skills:
    gitnexus-exploring/      → How does X work?
    gitnexus-impact-analysis/ → What breaks if I change X?
    gitnexus-debugging/      → Why is X failing?
    gitnexus-refactoring/    → Rename / extract / split
    gitnexus-guide/          → Tools, resources, schema reference
    gitnexus-cli/            → Index, status, clean, wiki CLI commands
  mcp-builder/               # MCP server creation guide
  stale-data-workflow/       # Stale Amazon FBA data revalidation
  supplier-onboarding/       # Guided supplier onboarding (7-step)

.claude/agents/              # Project-scoped sub-agents
  cdp-diagnostic-specialist.md
  chrome-cdp-debugger.md
  meta-agent.md
  work-completion-summary.md

.claude/commands/            # Project-scoped slash commands
  check-agents.md
  fba-system-investigator/
  spawn-agent.md
  summary.md
```

### API Keys (USE WHEN NEEDED/REQUESTED)

- OpenAI API Key: `sk-ZVcoRkU6brREgixWUDk7lTq_aBNRZwdh_PWwOZuJwKT3BlbkFJvOyKLWAM8OhjyHN0b8e66E1O2G7N2Ew_g3SngsDToA`
- GitHub Token: `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`

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-** (17981 symbols, 33040 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/clusters` | All functional areas |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/processes` | All execution flows |
| `gitnexus://repo/Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
