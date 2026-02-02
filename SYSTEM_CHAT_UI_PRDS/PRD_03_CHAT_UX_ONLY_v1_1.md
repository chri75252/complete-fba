# PRD 03 v1.1: Natural Language Chat UX (Chat‑Only)

**Version**: 1.1  
**Date**: 2026-01-29  
**Status**: Draft (Ready for Implementation)  
**Author**: Sisyphus (OhMyOpenCode)  

---

## 0. Positioning (What PRD_03 Is / Is Not)

This is a **revised PRD_03** focused exclusively on **Chat UX + local LLM reliability + deterministic tool execution**.

- **PRD_03 (this doc)**: Makes the chat *usable* (prose-first, JSON in expanders, clarify-first, deterministic tool calling).
- **PRD_04**: Adds **new domain capabilities** (e.g., product-list Amazon refresh workflow). PRD_04 is a separate PRD because it introduces new tools and new job types.

### Explicit statement (prevents operator confusion)
PRD_03 improves **how the assistant communicates** and **how tools are chosen/executed**. It does **not** add new analysis capabilities beyond the tools already present.

---

## 1. Executive Summary

### 1.1 Problem Statement

The current Chat UI behaves like a raw tool console:
- It executes a tool and returns mostly JSON.
- Operators cannot tell:
  - what will happen,
  - why a tool was chosen,
  - what results mean,
  - what the next step should be.

This causes: wasted time, wrong tool usage, and repeated runs.

### 1.2 Proposed Solution

Transform chat into a **conversational control plane UI** while keeping execution deterministic:
- Always show **prose** for intent + outcome.
- Always keep raw JSON accessible in expanders.
- Enforce **clarify-first** and **confirm-before-write**.

---

## 2. Goals and Non‑Goals

### 2.1 Goals

| ID | Goal | Success Metric |
|----|------|----------------|
| G1 | Prose-first responses | 100% assistant messages contain a human explanation |
| G2 | Deterministic tool execution | 0 tools executed without Python executor |
| G3 | JSON still available | 100% tool outputs viewable via expander |
| G4 | Clarify-first | Ambiguous requests produce clarifying questions, not guesses |
| G5 | Local LLM reliability | Tool selection is schema-validated + retried + safe fallback |
| G6 | No workflow breakage | No edits to `tools/` / `utils/` are required |

### 2.2 Non‑Goals

| ID | Non‑Goal | Reason |
|----|----------|--------|
| NG1 | Add new domain tools | Belongs in PRD_04+ capability PRDs |
| NG2 | Make runs faster | UX PRD; performance work is separate |
| NG3 | Require `thinking` always | Thinking is unstable; treat as optional debug |
| NG4 | Replace control plane job system | Out of scope |

---

## 3. UX Requirements

### 3.1 Message Model Contract (UI)

Each stored message uses the same schema:

```json
{
  "role": "user" | "assistant",
  "content": "prose",
  "thinking": "optional debug text or null",
  "tool_call": {"name": "...", "params": {...}} | null,
  "tool_result": {...} | null
}
```

Rules:
- `content` is always human-readable prose.
- Raw tool JSON is never placed into `content`.
- Tool JSON is rendered in an expander.
- `thinking` is hidden by default behind an expander.

### 3.2 Read vs Write Tool UX

**Read tools**:
- Immediately execute.
- Show: intent → result summary → JSON expander.

**Write tools**:
- Must require confirmation.
- Show: intent → what will happen → confirmation prompt.
- After confirm: execute tool → show “queued/done” summary → JSON expander.

---

## 4. Local LLM (Qwen3‑8B / Ollama) Reliability Requirements

### 4.0 Planner System Instructions

The chat planner’s instructions are currently assembled inline in:
- `control_plane/chat_orchestrator.py` (`build_prompt(...)`)

If you want a dedicated, editable instruction file (recommended once behavior stabilizes), use:
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

The intention is:
- keep the stable “policy” in a file
- keep dynamic schemas and context (tools + system index + RAG context) assembled at runtime


### 4.1 Planner must be schema-constrained

Tool selection must be returned as structured JSON that can be validated.

Requirements:
- `temperature=0`
- validate tool name against whitelist
- validate required params
- retry up to 2 times if invalid
- if still invalid → `ask_clarify`

### 4.2 Thinking is optional

- If Ollama returns a thinking/reasoning field, store it.
- If absent/empty, UI hides it.
- Correctness must not depend on it.

### 4.3 Never feed huge tool results back to the LLM

Summarization (if used) must pass only:
- `ok`
- `count`
- top N rows (small)
- key file paths
- key error fields

No raw multi‑MB JSON dumps.

### 4.4 Failure modes and required mitigations

- **Tool hallucination**: reject unknown tool names.
- **Param hallucination**: validate required keys/types; retry.
- **Invalid JSON**: retry with stricter instruction; then fallback to clarify.
- **Ambiguous user input**: do not enqueue; clarify.

---

## 5. Tool Schema + Drift Prevention

### 5.1 Single source of truth

Tool schema must be defined once (registry), and used by:
- the planner prompt/schema,
- the executor validation,
- the UI display.

No duplicated manual schemas in multiple files.

### 5.2 Clarify tool contract

Clarify tools must return structured output:

```json
{ "ok": true, "questions": ["..."], "hint": "..." }
```

UI renders the questions conversationally.

---

## 6. RAG Policy (Optional, Non‑Blocking)

RAG can be used to improve tool selection for:
- code/documentation questions
- config questions

RAG must never bypass confirmation gating or execute tools.

---

## 7. Operator Cheat Sheet (avoid wrong tool routing)

The planner is optimized for deterministic tool calls. Still, phrasing matters.

**Use these phrases when you want a sandboxed workflow run (category analysis)**
- "run sandboxed category analysis" + the category URL(s)
- "enqueue sandbox run for category" + the category URL(s)
- "analyze category URL(s) and generate sandbox linking map + financial report"
- "run workflow for these categories" + URLs

**Use these phrases when you want to *refresh Amazon for a product list***
- "run sandboxed product list refresh" + product list file path
- "refresh Amazon data for this product list" + file path
- "enqueue product list refresh" + file path

**Use these phrases when you want a read-only lookup (no run)**
- "show existing linking map" + supplier domain
- "find linking entries" + supplier domain + filters (ean/url/asin)
- "show cached products" + supplier domain

**Avoid ambiguous phrasing**
- Avoid: "analyze this supplier" (could route to read tools)
- Prefer: explicitly include "sandbox run" or "enqueue" when you want a job queued.

## 7. Test Plan

### Objective
Verify conversational UX does not reduce determinism.

### Test cases
1) Ambiguous input → clarify
2) Read query → intent + summary + JSON expander
3) Write tool proposal → requires confirm
4) Tool output huge → expander truncation, no chat spam
5) LLM failure → fallback to clarify

### Success criteria
All tests pass with local LLM enabled and disabled.

---

## 8. Rollback

All changes limited to `control_plane/` and `dashboard/`.
Rollback = restore those files from backup.

---

**END PRD_03 v1.1**
