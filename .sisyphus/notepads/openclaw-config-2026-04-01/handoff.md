# Session Handoff — OpenClaw Configuration & Setup
**Date:** 2026-04-01
**Work Type:** ARCHITECTURE + DEBUGGING
**Session Duration:** ~12 hours (multi-compaction session, 2026-03-31 → 2026-04-01)
**Primary Tool:** Claude Code (Sonnet 4.6)
**Working Directory:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`
**OpenClaw Config Dir:** `C:\Users\chris\.openclaw\`

---

## Executive Objective

Configure OpenClaw (Blacksmith Discord bot) from a broken post-cascade-failure state to a fully operational production setup: correct API keys, correct model hierarchy, authenticated providers, working plugins, fixed Command Center, and comprehensive workspace documentation.

---

## Session Narrative Arc

### Where we started
OpenClaw suffered cascading failures during a prior Discord session. 14 issues were identified: ClawBay 402 billing errors, free-tier 429 cascades, OpenAI embeddings 403 (text-embedding-3-small), ghost sessions, chat freeze, stale workflow registry, wrong provider prefixes, missing plugins, and more. The user had also provided new credentials (GCP OAuth, ClawBay API key, Gemini API key) and wanted a full reconfiguration.

### What was done (chronological)

**Phase 1: Core config fixes (`openclaw.json`)**
- Corrected ClawBay API key to `ca_v1.aHR0cHM6Ly90aGVjbGF3YmF5LmNvbQ.eQp4nJ2OxKe7jSQZOQIX0KA9al4wXin60JVCCn-c33A`
- Set primary model to `theclawbay/gpt-5.3-codex`
- Fixed `thinkingDefault: "high"` — had been placed inside `model` object (invalid), correct location is `agents.defaults.thinkingDefault`
- Added Google Vertex provider block with `auth: "oauth"`, GCP project embedded in baseUrl
- Built full 16-model `agents.defaults.models` list
- Fixed `llm-task` plugin config keys: `defaultProvider`/`defaultModel`/`timeoutMs` (were wrong: `provider`/`model`/`timeout`)
- Enabled `lobster` plugin
- Removed `qwen3-coder:free` from defaults.models (permanently removed: security failures)

**Phase 2: Google Vertex auth investigation**
- Ran `openclaw models auth login --provider google-vertex` → error: "Unknown provider google-vertex"
- Root cause: `google-vertex` has NO plugin in OpenClaw. Plugin list confirmed: only `google` plugin handles Gemini (via API key at `generativelanguage.googleapis.com`)
- Ran `openclaw models auth login --provider google` → authenticated using `GEMINI_API_KEY` env var (`AIza...EWoA`)
- Side effect: auth wizard changed `agents.defaults.model` to `{ "primary": "google/gemini-3.1-pro-preview" }` — this was reverted back to `"theclawbay/gpt-5.3-codex"`
- Decision: replaced `google-vertex/` model refs with `google/` (same Gemini models, working API key path)
- `google-vertex` provider block kept in config for future OAuth use but removed from `defaults.models`

**Phase 3: Command Center fixes**
- Added `sessions-prune` to ALLOWED_ACTIONS in `actions.js`
- Added handler case in `actions.js` for `sessions-prune`
- Fixed `index.html` button: was calling `action=prune-stale`, now calls `action=sessions-prune`
- Added Command Center URL to `TOOLS.md` so Blacksmith knows to use it for read-only monitoring

**Phase 4: Documentation generated**
- `OPENCLAW_CURRENT_SETUP.md` — full current config, all 7 workflows with prompt examples and model chains
- `OPENCLAW_OPTIMAL_MAPPING.md` — upgrade path to gpt-5.4-mini as primary, with full diffs
- `MODEL_POLICY.md` (Rev 6) — per-phase routing, per-workflow table, fallback chains, critical warnings
- `REGISTRY.md` — updated model assignments
- `index.json` — aligned model IDs with REGISTRY.md (was using short-form)
- `OPENCLAW_PLUGINS_SETUP.md` — oh-my-openclaw assessment updated (was "pending" → completed assessment)
- `STATE.yaml` — bootstrapped
- `FBA_PROJECT_PATH.md` — canonical FBA project path recorded

**Phase 5: Session/gateway operations**
- `openclaw gateway restart` — executed, successful
- `openclaw sessions cleanup` — ran, kept 3 sessions (all within maintenance window)
- Confirmed: sessions showing as IDLE consume 0 tokens, tok/min shown is historical rolling average

**Phase 6: Workflow audit (by Blacksmith)**
- Blacksmith ran a full workflow audit via Discord at ~22:30
- Confirmed Command Center reachable, Chrome CDP reachable, Tavily key present
- Found: provider naming drift (clawbay/ vs theclawbay/ vs openai/ in per-workflow files), 2 missing config.json, missing product-bank.json, STATE.log, nemotron-3-super-free in Results Reviewer SKILL

### Key discoveries

1. `google-vertex` is a custom provider with no plugin handler — OAuth auth flow impossible without gcloud or a plugin
2. The auth wizard (`openclaw models auth login`) auto-changes `agents.defaults.model` as a side effect when run — always verify the primary model afterward
3. Sessions store `abortedLastRun` flag — the 20h stale session was the old clearance-king ghost subagent that had timed out
4. ClawBay 500/503 errors during the session were transient backend failures, not config issues — Blacksmith eventually responded successfully
5. `openclaw sessions prune` is NOT a valid command — correct command is `openclaw sessions cleanup`
6. IDLE sessions consume 0 tokens — tok/min in Command Center is historical rolling average, not live rate
7. Native dashboard chat and Discord are separate sessions — opening native dashboard creates a parallel session

### Direction changes

- **google-vertex → google/**: Initially configured Vertex AI with OAuth. Discovered no plugin exists. Switched to `google/` provider (Gemini API key, working).
- **No null in providers**: Tried `"google-vertex": null` to remove it → broke config validation. Restored the provider block, just removed from defaults.models.
- **`thinkingDefault` placement**: Was inside `model` object, then tried `agents.defaults.thinking` — both invalid. Correct: `agents.defaults.thinkingDefault`.

---

## Current State of openclaw.json

```
Primary model:    theclawbay/gpt-5.3-codex
thinkingDefault:  high
Auth profiles:    openai-codex (OAuth), google:default (api_key)
Plugins enabled:  brave, firecrawl, tavily, llm-task, lobster
Providers:        theclawbay (6 models), google-vertex (kept, no auth), opencode/openrouter (via plugins)
defaults.models:  15 models (qwen3-coder removed)
```

Key models in defaults.models:
- `theclawbay/gpt-5.3-codex` ← PRIMARY
- `theclawbay/gpt-5.4`
- `opencode-go/minimax-m2.7` ← workhorse
- `opencode-go/kimi-k2.5`
- `opencode-go/minimax-m2.5`
- `opencode/minimax-m2.5-free`
- `openrouter/minimax/minimax-m2.5:free`
- `opencode/mimo-v2-omni-free`
- `opencode/mimo-v2-pro-free`
- `google/gemini-3.1-pro-preview` ← authenticated, API key
- `google/gemini-3.1-flash-lite-preview` ← classifier only
- `opencode-go/glm-5`
- `openrouter/stepfun/step-3.5-flash:free`
- `openrouter/meta-llama/llama-3.3-70b-instruct:free`
- `openrouter/z-ai/glm-4.5-air:free`

---

## Files Modified This Session

| File | What Changed |
|------|-------------|
| `C:\Users\chris\.openclaw\openclaw.json` | API key, primary model, thinkingDefault, google-vertex provider, llm-task keys, lobster, google/ model refs, removed qwen3-coder |
| `C:\Users\chris\.openclaw\workspace\memory\MODEL_POLICY.md` | Rev 6: per-phase routing, per-workflow table, fallback chains, google-vertex→google, qwen3-coder removed from catalog |
| `C:\Users\chris\.openclaw\workspace\memory\OPENCLAW_CURRENT_SETUP.md` | Full current config documentation, all 7 workflows |
| `C:\Users\chris\.openclaw\workspace\memory\OPENCLAW_OPTIMAL_MAPPING.md` | Upgrade path to gpt-5.4-mini, full diffs |
| `C:\Users\chris\.openclaw\workspace\memory\OPENCLAW_PLUGINS_SETUP.md` | oh-my-openclaw assessment completed |
| `C:\Users\chris\.openclaw\workspace\workflows\REGISTRY.md` | Model assignments updated, google-vertex→google |
| `C:\Users\chris\.openclaw\workspace\workflows\index.json` | Model IDs aligned, removed deleted workflows, added current |
| `C:\Users\chris\.openclaw\workspace\STATE.yaml` | Bootstrapped |
| `C:\Users\chris\.openclaw\workspace\memory\FBA_PROJECT_PATH.md` | Created |
| `C:\Users\chris\.openclaw\workspace\TOOLS.md` | Added Local Services section (Command Center, CDP, FBA Dashboard URLs) |
| `C:\Users\chris\.openclaw\skills\openclaw-command-center\src\actions.js` | Added sessions-prune action |
| `C:\Users\chris\.openclaw\skills\openclaw-command-center\public\index.html` | Fixed button action from prune-stale to sessions-prune |

---

## Open Issues / Pending P0 Work (from Blacksmith's workflow audit)

Blacksmith ran a full workflow audit and offered to do a P0 fix pass. User had not yet responded "yes". These are the outstanding items:

### P0 — Do immediately

| Item | Location | Detail |
|------|----------|--------|
| Create `config.json` | `workflows/results-reviewer/` | Missing entirely |
| Create `config.json` | `workflows/reverse-product-search/` | Missing entirely |
| Create `product-bank.json` | `workspace/` | Required by wholesaler-research and reverse-product-search |
| Create `STATE.log` | `workspace/` | Required by control-center-sync SKILL |
| Normalize model/provider IDs | All workflow SKILL.md + config files | `clawbay/` → `theclawbay/`, `openai/` → `theclawbay/` |
| Replace `nemotron-3-super-free` | `workflows/results-reviewer/SKILL.md` | Not in active model policy |
| Add `FIRECRAWL_API_KEY` | Env / config | Wholesaler Research will fail without it |
| Add `AMAZON_PRODUCT_API_KEY` | Env / config | Product enrichment steps fail without it |

### P1 — Same day

| Item | Detail |
|------|--------|
| Choose canonical output dir | `parity-reports/` vs `stale-check/` — used inconsistently in Stale Revalidation |
| Remove retired workflow refs | `wf_fba_analysis_parity`, `wf_wholesaler_onboarding` still referenced in some files |
| Verify/remove `ak-rss-24h-brief` | Referenced in Morning AI Brief but not confirmed installed |

---

## Known Issues / Risks

| Issue | Severity | Detail |
|-------|----------|--------|
| `text-embedding-3-small` still being called | Medium | Memory sync still logs 403 from OpenAI embeddings. memory-core should handle this but the old path still fires. |
| `google-vertex` can't auth | Low | Provider kept in config but OAuth requires gcloud (not installed). Use `google/` prefix instead. |
| ClawBay transient 500/503 | Medium | Happened once during session. Backend failures, not config. Fallback: switch to `opencode-go/minimax-m2.7`. |
| Workflow files have drift | High | Per-workflow SKILL.md/config files still reference wrong provider prefixes. P0 fix needed. |
| heartbeat is disabled | Low | `heartbeat.every: "0m"` — intentional but means no auto-keepalive |

---

## Critical API Keys & Auth

| Service | Auth Type | Key/Location |
|---------|-----------|-------------|
| ClawBay | Subscription OAuth proxy | `ca_v1.aHR0cHM6Ly90aGVjbGF3YmF5LmNvbQ.eQp4nJ2OxKe7jSQZOQIX0KA9al4wXin60JVCCn-c33A` |
| Google Gemini | API key (env: GEMINI_API_KEY) | `AIza...EWoA` (in env, not in config) |
| Google Vertex | OAuth (NOT WORKING — no gcloud) | Credentials exist but no auth path in OpenClaw |
| Firecrawl | API key | `fc-dcb583303780435791d5b949a4dd7061` (in openclaw.json plugins) |
| Tavily | API key | `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` |
| Brave | API key | `BSACnLF154aiY_SL7BE4d8tEa_5Qrm-_` |

---

## Local Services

| Service | URL | Auth | Notes |
|---------|-----|------|-------|
| OpenClaw Gateway | `ws://127.0.0.1:18789` | Token: `cbc8b2f3921e4a3faf1cfb7f7e84837568f7dcdc9f14b5cf` | Core gateway |
| Native Dashboard | `http://127.0.0.1:18789/#token=cbc8b2f3...` | Token in URL | Avoid for monitoring — creates parallel sessions |
| Command Center | `http://localhost:3333` | None | Read-only, start with: `cd C:\Users\chris\.openclaw\skills\openclaw-command-center && node lib/server.js` |
| Chrome CDP | `http://localhost:9222` | None | Required for browser workflows |
| FBA Dashboard | `http://localhost:8501` | None | Streamlit, start with: `streamlit run dashboard/app.py` |

---

## Startup Commands

```powershell
# Start gateway
openclaw gateway start

# Reload config
openclaw gateway restart

# Clean stale sessions
openclaw sessions cleanup

# Check all models auth status
openclaw models list

# Start Command Center
cd C:\Users\chris\.openclaw\skills\openclaw-command-center && node lib/server.js

# Open native dashboard
openclaw dashboard
```

---

## Optimal Model Upgrade Path (NOT YET APPLIED)

File: `C:\Users\chris\.openclaw\workspace\memory\OPENCLAW_OPTIMAL_MAPPING.md`

One-line change to apply when ready:
```diff
- "model": "theclawbay/gpt-5.3-codex",
+ "model": "theclawbay/gpt-5.4-mini",
```
Plus add `"theclawbay/gpt-5.4-mini": {}` to defaults.models.
Also update REGISTRY.md and MODEL_POLICY.md per the diff in OPENCLAW_OPTIMAL_MAPPING.md.
Why: 400k context (+47%), 2× faster, 29% cheaper than gpt-5.3-codex.

---

## oh-my-openclaw (NOT YET INSTALLED)

Assessment complete, install deferred until current setup confirmed stable.
- Install: `openclaw plugin install oh-my-openclaw`
- CRITICAL: Do NOT run `omoc-setup --force` — overwrites existing agent configs
- After install: `openclaw gateway restart` then test `/omoc list`

---

## Session Continuity Notes

- Discord channel session (`agent:main:discord:channel:1487266989402488945`) persists across gateway restarts — next message in that Discord channel continues from where it left off
- If session aged out, tell Blacksmith: "Read session memory file from 2026-03-31 and continue"
- Session memory files auto-saved to: `C:\Users\chris\.openclaw\workspace\memory\`
- Blacksmith now has Command Center URL in TOOLS.md — will use `http://localhost:3333` proactively for read-only monitoring

---

## MD File vs JSON Config Enforcement

| Rule Type | Mechanism | Enforcement |
|-----------|-----------|-------------|
| Behavioral rules (folder access, ask permission) | Workspace MD files (TOOLS.md, AGENTS.md, WORKFLOW_RULES.md) | SOFT — LLM follows as instructions |
| Hard command blocking | `gateway.nodes.denyCommands` in openclaw.json | HARD — framework blocks at runtime |
| Tool category allowlist | `tools.profile` in openclaw.json | HARD — gateway enforced |

MD files work for behavioral rules — no JSON config needed for things like "ask before running bash" or "don't access folder X".

---

## Next Session First Actions

1. Open Discord, check if Blacksmith responded to the "So?" message — if yes, reply "yes fix it now" to trigger P0 pass
2. If no response, send fresh prompt: "Run P0 fix pass — create missing config.json for results-reviewer and reverse-product-search, product-bank.json, STATE.log, and normalize all model/provider IDs across workflow files"
3. After P0 pass complete, verify: `openclaw gateway restart` to reload any config changes
4. Start Command Center: `cd C:\Users\chris\.openclaw\skills\openclaw-command-center && node lib/server.js`
5. Check models list: `openclaw models list` — all 15 should show `yes` auth
6. When stable: install oh-my-openclaw (see above, NO --force flag)
7. When stable: apply gpt-5.4-mini optimal upgrade (single line change + REGISTRY.md + MODEL_POLICY.md)
