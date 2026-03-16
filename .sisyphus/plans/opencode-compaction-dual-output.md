# OpenCode Compaction: Dual-Output (Default + Handoff Addendum)

## TL;DR

> Goal: When compaction runs (auto or manual), the compaction summary must contain BOTH:
> 1) the default OpenCode continuation summary (the standard template), and
> 2) a handoff-grade addendum (only non-redundant info).
>
> Approach: Tune OpenCode compaction headroom + (optionally) enable OhMyOpenCode preemptive compaction + add a small local OpenCode plugin that appends compaction instructions via `experimental.session.compacting`.

Estimated Effort: Short
Parallel Execution: YES (2 waves)
Critical Path: config edits + plugin file -> verification via /compact

---

## Context

### What you asked for
- A detailed/extensive plan with patches/diffs/snippets/steps.
- Ensure that at compaction time we get both:
  - the default OpenCode compaction summary output, and
  - the richer handoff information (merge redundant sections if needed).

### Verified environment facts (file-grounded)
- OpenCode version: `opencode --version` => `1.2.20`
- OhMyOpenCode version: `oh-my-opencode --version` => `3.7.1`
- OpenCode v1.2.20 compaction default prompt + hook trigger is in:
  - https://raw.githubusercontent.com/anomalyco/opencode/v1.2.20/packages/opencode/src/session/compaction.ts
  - It builds `promptText = compacting.prompt ?? [defaultPrompt, ...compacting.context].join("\n\n")`.
  - It triggers plugin hook `experimental.session.compacting` before summarization.
- Local OpenCode plugin typings confirm the hook is available:
  - `C:\Users\chris\.config\opencode\node_modules\@opencode-ai\plugin\dist\index.d.ts:203`
- Local OpenCode config typings confirm `compaction.auto/prune/reserved`:
  - `C:\Users\chris\.config\opencode\node_modules\@opencode-ai\sdk\dist\v2\gen\types.gen.d.ts:1225`
- OhMyOpenCode (3.7.1) already wires compaction hooks into OpenCode's compaction hook:
  - `C:\Users\chris\AppData\Roaming\npm\node_modules\oh-my-opencode\dist\index.js:70391`

### Plugin loading expectations (OpenCode v1.2.20)
- Local plugin directories (official docs):
  - Global: `~/.config/opencode/plugins/` (Windows equivalent: `C:\Users\chris\.config\opencode\plugins\`)
  - Project: `.opencode/plugins/`
- Supported: JavaScript and TypeScript plugin files (`.js` and `.ts`) per official plugins docs.
- Load order per official docs: config -> global plugins dir -> project plugins dir.
- Known pitfall: avoid having multiple local plugins named `index.ts` (OpenCode issue reports a load bug). This plan uses a uniquely named file.

### Current config state (verified)
- `C:\Users\chris\.config\opencode\opencode.json` currently has no `compaction` block.
- `C:\Users\chris\.config\opencode\oh-my-opencode.json` currently has no `experimental` block; preemptive compaction is therefore not enabled.

---

## Work Objectives

### Core Objective
Make compaction reliably produce a single compaction summary that includes:
- Block A: the default OpenCode continuation summary (Goal / Instructions / Discoveries / Accomplished / Relevant files / directories)
- Block B: a Handoff Addendum containing critical continuity information that is often lost in compaction, without repeating Block A.

### Deliverables
- Config change: `C:\Users\chris\.config\opencode\opencode.json` adds `compaction` settings.
- Config change (optional but recommended): `C:\Users\chris\.config\opencode\oh-my-opencode.json` enables `experimental.preemptive_compaction`.
- New local plugin file: `C:\Users\chris\.config\opencode\plugins\compaction-dual-output.js`

### Guardrails (must NOT do)
- Do NOT set `output.prompt` in our custom plugin, because that would bypass/ignore other plugins' `output.context` injections (including OhMyOpenCode's compaction-context-injector).
- Do NOT attempt to "run /handoff as a separate command" during compaction. That would require an additional LLM turn at the worst possible time (near token limits) and is more fragile.
- Do NOT edit any bundled runtime files under `node_modules` to customize compaction; use local plugin + config only.
- Do NOT name multiple local plugins `index.ts`; keep unique filenames.

---

## Verification Strategy (Agent-Executable)

### Primary verification commands
1) Verify OpenCode sees compaction config:

```bash
opencode debug config
```

Expected: output includes `compaction.auto`, `compaction.prune`, `compaction.reserved` with the values set.

Note: after changing configs and adding a local plugin file, restart OpenCode (exit the TUI and relaunch) so the new plugin/config is loaded.

2) Verify OhMyOpenCode experimental preemptive compaction flag is active (if enabled):

```bash
opencode debug config
```

Expected: merged config shows `experimental.preemptive_compaction: true` for OhMyOpenCode.

3) Trigger a compaction and confirm dual-output format:
- In TUI: run `/compact`
- Or via CLI if available in your setup:

```bash
opencode chat --message "/compact"
```

Expected: the compaction summary includes both:
- Block A headings: `## Goal`, `## Instructions`, `## Discoveries`, `## Accomplished`, `## Relevant files / directories`
- Block B heading: `# Block B` and `## Handoff Addendum` (or equivalent) and its required subsections.

4) Verify todo preservation (OhMyOpenCode hook):
- Create at least one todo in session, compact, ensure todo list remains.

---

## Execution Strategy

### Parallel Execution Waves

Wave 1 (can run in parallel):
- Task 1: Backup target config files
- Task 2: Update OpenCode compaction config
- Task 3: Add local compaction dual-output plugin
- Task 4: (Optional) Enable OhMyOpenCode preemptive compaction

Wave 2 (after Wave 1):
- Task 5: Verification and tuning (reserved tokens, redundancy rules)

---

## TODOs (Detailed Patches + Steps)

Notes on patch format: This plan includes explicit diffs/snippets. The executing agent should apply them exactly, then verify with the commands above.

- [x] 1. Backup config files (safety)

  What to do:
  - Create backup directory:
    - `C:\Users\chris\.config\opencode\backup\compaction_dual_output_20260313\`
  - Copy these files into it:
    - `C:\Users\chris\.config\opencode\opencode.json`
    - `C:\Users\chris\.config\opencode\oh-my-opencode.json`

  Acceptance criteria:
  - Backup directory exists.
  - Both backup files exist and are non-empty.

  QA scenario:
  - Tool: Bash
  - Steps:
    1. Confirm backup files exist.
    2. Confirm size > 0.

- [x] 2. Patch `opencode.json` to tune compaction headroom

  File: `C:\Users\chris\.config\opencode\opencode.json`

  Patch (diff snippet):
  - Add a new top-level key `compaction`.
  - Recommended placement: near other top-level runtime settings (any top-level location is valid JSON).

  ```diff
  {
    "$schema": "https://opencode.ai/config.json",
  +  "compaction": {
  +    "auto": true,
  +    "prune": true,
  +    "reserved": 20000
  +  },
    "permission": {
      "bash": {
        "*": "allow",
        "git": "deny",
        "git *": "deny",
        "git clone *": "allow"
      }
    },
    "default_agent": "sisyphus",
    ...
  }
  ```

  Rationale:
  - `reserved: 20000` aligns with the OpenCode buffer used in v1.2.20 and keeps enough headroom for a richer compaction summary.

  Acceptance criteria:
  - JSON remains valid.
  - `opencode debug config` shows the new compaction values.

  QA scenario:
  - Tool: Bash
  - Steps:
    1. Run `opencode debug config`.
    2. Confirm it prints compaction settings.

- [x] 3. Patch `oh-my-opencode.json` to enable preemptive compaction (recommended)

  File: `C:\Users\chris\.config\opencode\oh-my-opencode.json`

  Patch (diff snippet):

  ```diff
  {
    "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-opencode/master/assets/oh-my-opencode.schema.json",
    "google_auth": false,
  +  "experimental": {
  +    "preemptive_compaction": true
  +  },
    "claude_code": {
      "mcp": false,
      "hooks": false,
      "plugins": false,
      "agents": false,
      "commands": false,
      "skills": false
    },
    "agents": {
      ...
    }
  }
  ```

  Rationale:
  - OhMyOpenCode `preemptive-compaction` triggers compaction earlier (internally ~0.78 usage), reducing last-second compaction failures.

  Acceptance criteria:
  - JSON remains valid.
  - OhMyOpenCode hook is enabled (not listed in `disabled_hooks`, if present).

  Note:
  - If you later add `disabled_hooks` to `C:\Users\chris\.config\opencode\oh-my-opencode.json`, ensure it does NOT include: `preemptive-compaction`, `compaction-context-injector`, `compaction-todo-preserver`, `context-window-monitor`.

  QA scenario:
  - Tool: Bash
  - Steps:
    1. Run `opencode debug config`.
    2. Confirm merged config includes `experimental.preemptive_compaction: true`.

- [ ] 4. Add local OpenCode plugin: compaction dual-output enforcer (core deliverable)

  Goal: Ensure the compaction summary includes both the default OpenCode summary AND a handoff addendum.

  New path: `C:\Users\chris\.config\opencode\plugins\compaction-dual-output.js`

  Create directory if missing:
  - `C:\Users\chris\.config\opencode\plugins\`

  File contents (full):

  ```js
  // OpenCode local plugin (ESM). Loaded automatically from ~/.config/opencode/plugins/
  // Goal: During compaction, keep default OpenCode summary AND force a non-redundant handoff addendum.

  export const CompactionDualOutput = async () => {
    const MARKER = "[compaction-dual-output:v1]";

    const directive = `
  ${MARKER}

  You are generating a compaction summary that will be used to continue the session.

  You MUST produce a single Markdown output containing TWO blocks, in this exact order.

  ---

  # Block A - Default OpenCode Continuation Summary

  Follow the default OpenCode template exactly with these headings:

  ## Goal

  ## Instructions

  ## Discoveries

  ## Accomplished

  ## Relevant files / directories

  ---

  # Block B - Handoff Addendum (Non-Redundant)

  Only include information NOT already captured in Block A.
  If a detail appears in Block A, do NOT repeat it in Block B.

  ## Handoff Addendum

  ### Decisions Log
  - Each decision: what was decided + why + alternatives rejected (if any)

  ### Blockers & Unknowns
  - Concrete blockers + what information is missing

  ### Verification Performed
  - Commands run and what they proved (if none, write "None")

  ### Risks / Fragile Areas
  - Anything likely to break or be forgotten after compaction

  ### Recovery / Resume Notes
  - If the agent is forced to resume mid-task: what to do first

  ### State & Variables
  - Important config values, feature flags, environment toggles

  ### Delegated Agent Sessions
  - List background agent sessions with their session_id and purpose
  `;

    return {
      "experimental.session.compacting": async (_input, output) => {
        // Ensure we DO NOT override output.prompt.
        // Keep compatibility with other plugins (eg. OhMyOpenCode compaction-context-injector).

        output.context = Array.isArray(output.context) ? output.context : [];

        // Avoid duplicating the directive if multiple plugins re-enter.
        if (output.context.some((s) => typeof s === "string" && s.includes(MARKER))) return;

        // Place our directive early so it is not lost among other injected contexts.
        output.context.unshift(directive);
      },
    };
  };
  ```

  Acceptance criteria:
  - Plugin file exists.
  - `opencode debug config` shows plugins loaded normally (no boot errors).
  - When compaction runs, the summary includes Block A and Block B headings.

  Extra guardrail check:
  - Confirm no other plugin sets `output.prompt` for `experimental.session.compacting` (if any plugin does, `output.context` injections from other plugins will be ignored). The simplest practical check is: after adding this plugin, run a compaction and confirm OhMyOpenCode's compaction context sections still appear.

  Optional deeper conflict check (read-only search):
  - Search loaded plugin code for prompt replacement logic:
    - Look for `experimental.session.compacting` handlers that assign `output.prompt =`.

  QA scenarios:
  - Scenario (happy path):
    - Tool: OpenCode TUI
    - Steps:
      1. Start any session.
      2. Run `/compact`.
      3. Confirm resulting compaction summary contains Block A default headings and Block B addendum headings.
  - Scenario (edge):
    - Preconditions: Have OhMyOpenCode background tasks spawned.
    - Steps:
      1. Spawn a background task.
      2. Compact.
      3. Confirm delegated sessions are listed and our addendum is still present.

- [ ] 5. Verification + tuning pass

  What to do:
  - Run `opencode debug config` and confirm:
    - compaction settings applied
    - OhMyOpenCode config applied
  - Trigger compaction (`/compact`) and visually inspect:
    - Block A present with default headings
    - Block B present with addendum headings
    - no obvious duplication between blocks
  - If compaction output is too long or compaction fails:
    - Increase `compaction.reserved` (eg. 20000 -> 25000)
    - Reduce Block B verbosity (keep headings but shorten required content)

  Acceptance criteria:
  - Compaction completes successfully.
  - Output contains both blocks.
  - Todo list remains after compaction (OhMyOpenCode preservation).

---

## Defaults Applied (override if you disagree)
- Plugin format: `.js` ESM (not `.ts`) to avoid any TypeScript loading assumptions.
- `compaction.reserved`: `20000` as the initial headroom baseline.
- OhMyOpenCode preemptive compaction: enabled (you can disable by setting `experimental.preemptive_compaction: false`).

---

## Rollback Plan

If you want to undo everything cleanly:
1) Restore backups for:
   - `C:\Users\chris\.config\opencode\opencode.json`
   - `C:\Users\chris\.config\opencode\oh-my-opencode.json`
2) Delete plugin file:
   - `C:\Users\chris\.config\opencode\plugins\compaction-dual-output.js`

---

## External References
- OpenCode v1.2.20 compaction source (default prompt + hook):
  - https://raw.githubusercontent.com/anomalyco/opencode/v1.2.20/packages/opencode/src/session/compaction.ts
- OpenCode config docs (compaction settings):
  - https://raw.githubusercontent.com/anomalyco/opencode/v1.2.20/packages/web/src/content/docs/config.mdx
- OpenCode plugins docs (local plugins + compaction hook):
  - https://raw.githubusercontent.com/anomalyco/opencode/v1.2.20/packages/web/src/content/docs/plugins.mdx

---

## Success Criteria
- Compaction always yields a continuation artifact that includes both:
  - default OpenCode summary sections, and
  - handoff addendum sections.
- Reduced compaction failures due to late overflow (preemptive compaction + reserved headroom mitigate this).
- Todos survive compaction (OhMyOpenCode todo preservation).
