# PRD 04: Conversational Chat + Product‑List Amazon Refresh (Sandboxed)

**Version**: 1.0  
**Date**: 2026-01-29  
**Status**: Draft (Ready for Implementation)  
**Author**: Sisyphus (OhMyOpenCode)  

---

## 0. Positioning vs PRD_03

This document is **PRD_04** (a new PRD), not a revision of PRD_03.

- **PRD_03 scope**: Chat UX transformation (natural language explanations + JSON expanders + deterministic tool execution), without adding domain capabilities.
- **PRD_04 scope (this PRD)**: Includes **all PRD_03 chat UX requirements**, and adds a **new domain capability**: **product-list Amazon refresh** (accept a list of supplier products in cached-products format, refresh Amazon metrics, write linking map entries, generate financial report).

### What is still needed for PRD_03 (if kept as a standalone PRD)
PRD_03 should be updated into a clean “Chat UX PRD” that:
- Explicitly states: it **improves conversational output only**, and **does not** add missing domain tools/capabilities.
- Removes/softens any hard dependency on `message.thinking` (treat as optional).
- Avoids requiring tools to return prose (tools return structured; UI renders prose).
- Adds explicit reliability constraints for local LLMs (schema validation, retries, whitelist).

PRD_04 intentionally bundles both chat UX + a critical missing capability (product list refresh) because operators expect the chat to *do real work* beyond formatting.

---

## 1. Executive Summary

### 1.1 Problem Statement

1) The Chat UI currently returns tool JSON without sufficient user-facing explanation, leading to operator confusion and mis-execution risk.

2) The system lacks a **first-class** workflow to:
- accept a curated list of supplier products (title/price/ean/url, etc.),
- refresh Amazon metrics now (not reuse stale cache),
- write/update linking map entries,
- generate a financial report.

### 1.2 Goals

- Make the Chat UI conversational **without losing determinism**.
- Enable a new **product-list Amazon refresh** workflow that is:
  - high success rate
  - minimal risk to existing workflow
  - implemented without editing the core workflow engine (`tools/`) unless absolutely necessary.

### 1.3 Key Constraints

- **Do not modify** the core workflow engine files under `tools/` (especially `tools/passive_extraction_workflow_latest.py`) unless explicitly approved later.
- Prefer not to modify `utils/`.
- Product-list workflow must work with a locally hosted LLM (Qwen3-8B via Ollama) and be robust to tool-calling/JSON failures.

---

## 2. Glossary

- **Control Plane**: `control_plane/` job system that enqueues work, runs workers, writes status/logs.
- **Write Tool**: tool that enqueues or modifies state (requires confirmation).
- **Read Tool**: tool that only reads status/files.
- **Sandbox Supplier**: unique supplier name for isolation: `<supplier_domain>__sandbox__<run_id[:8]>`.
- **Canonical Amazon Cache File**: `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json`.

---

## 3. Functional Requirements

### 3.1 Chat UX and Behavior

**FR-CHAT-1 (Prose-first)**: Every assistant response must include a human-readable explanation in `content`.

**FR-CHAT-2 (Deterministic execution)**: LLM only selects tools. Python executes tools. No direct action without tool execution.

**FR-CHAT-3 (Confirmation gating)**: Any write tool must require explicit UI confirmation before execution.

**FR-CHAT-4 (Technical details)**: Tool JSON result must be available via an expander (never spam inline).

**FR-CHAT-5 (Clarify-first)**: If required parameters are missing or request is ambiguous, the system must use `ask_clarify` instead of guessing.

**FR-CHAT-6 (No schema drift)**: Tool definitions and schemas must come from a single source of truth.

### 3.2 Product‑List Amazon Refresh (New Capability)

**FR-PROD-1 (Input)**: Accept product list in cached-products entry format:
- required: `title`, `price`, `url`
- optional: `ean`, `sku`, `availability`, `image_url`, `source_url`, `scraped_at`

**FR-PROD-2 (Amazon refresh)**: For each product:
- If EAN present: search Amazon by EAN (primary)
- Else: search Amazon by title (fallback)
- Extract ASIN and metrics needed by financial analysis

**FR-PROD-3 (Amazon cache overwrite)**: Write refreshed Amazon JSON to the canonical file:
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json`
- Overwrite is **allowed** and required for freshness.

**FR-PROD-4 (Linking map output)**: Create/update sandbox linking map:
- `OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json`

**FR-PROD-5 (Financial report)**: Generate report by calling existing calculator:
- `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`

**FR-PROD-6 (Sandbox isolation)**: All supplier-specific artifacts must be written under sandbox supplier identity:
- cached products file
- linking map
- financial reports
- processing state (if any)

---

## 4. Non‑Functional Requirements

**NFR-1 (No existing workflow breakage)**: Existing category workflow must continue working unchanged.

**NFR-2 (Local LLM reliability)**: Tool selection must be schema-validated with retries and safe fallback to clarify.

**NFR-3 (Latency)**:
- Read tools: <10s typical
- Write tools: return quickly (“queued job”), do not block for run completion

**NFR-4 (No huge payloads to LLM)**: Summarization uses extracted fields only; never feed full JSON blobs.

---

## 5. Architecture

### 5.1 Message Contract (UI)

Each stored chat message is:

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
- `content` is always prose.
- Raw tool data lives only under `tool_call`/`tool_result` and is rendered in expanders.

### 5.2 LLM Orchestration Strategy (Qwen3‑8B via Ollama)

#### 5.2.1 Planner: Schema‑constrained JSON tool selection

- Use deterministic settings: `temperature=0`
- Validate output against schema
- Validate tool name against whitelist
- Validate required params
- Retry up to 2 times with stricter prompt
- If still invalid -> `ask_clarify`

#### 5.2.2 Thinking mode: Optional

- “thinking” output is optional and used only for debugging.
- Never rely on it for correctness.

#### 5.2.3 Summarizer: Optional second call

- Generate 2–5 sentence summary.
- Must not guess: missing/empty data must be stated explicitly.

### 5.3 Tool Registry and Schema Source of Truth

- Introduce a single registry that defines:
  - tool name
  - type (read/write)
  - parameters schema
  - required fields

Both planner schema generation and executor validation must use this registry.

---

## 6. Product‑List Amazon Refresh Workflow Design

### 6.1 New Write Tool

**Tool name**: `enqueue_product_list_refresh`

**Parameters**:
- `supplier_domain` (string)
- `products` (array of product dicts) OR `products_path` (string path)
- optional: `run_id`, `notes`

**Returns**:
- `run_id`
- `sandbox_supplier`
- paths to generated artifacts (products_subset.json, sandbox cache, sandbox linking map)

### 6.2 Job Type

Add job type constant:
- `run_product_list_refresh`

### 6.3 Runner Script

A new runner script under `control_plane/` executes:
1) Load the products list
2) Create sandbox supplier identity
3) Write sandbox cached-products file:
   - `OUTPUTS/cached_products/<sandbox_supplier_normalized>_products_cache.json`
4) For each product:
   - Search Amazon (EAN first, title fallback)
   - Extract ASIN + required metrics
   - Write canonical Amazon cache file:
     - overwrite `amazon_{ASIN}_{EAN}.json`
   - Update sandbox linking map entry
5) Run financial calculations:
   - `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`

### 6.4 Amazon Cache Policy (Freshness)

- Canonical overwrite is required to guarantee the financial calculator reads updated data.
- Optional historical snapshot file may be written with timestamp for audit.

---

## 7. Chat UI Behavior by Tool Category

### 7.1 Read Tools
- Show intent (“I’m going to…”) -> execute -> show summary -> expander contains JSON.

### 7.2 Write Tools
- Show intent + what will happen
- Require Confirm
- On confirm:
  - enqueue job
  - respond with run_id + where to view status/log

---

## 8. Test Plan

### Objective
- Verify chat is conversational and deterministic.
- Verify product-list refresh generates linking map + updated amazon cache + financial report.
- Verify existing workflow unaffected.

### Prerequisites
- Ollama running with qwen3 model
- Chrome running with CDP port (if required by Amazon extraction)

### Test Cases
1) Ambiguous request -> ask_clarify
2) enqueue_product_list_refresh -> requires confirmation
3) Job runs -> linking_map.json created under sandbox supplier
4) Amazon cache canonical file updated (mtime changes)
5) Financial report CSV generated for sandbox supplier
6) Regression: category workflow still runs unchanged

---

## 9. Rollback

- All changes confined to `control_plane/` and `dashboard/`.
- Rolling back is restoring those directories from backup.

---

## 10. Acceptance Criteria

- Chat UI: prose-first + expander JSON + confirmation gating.
- LLM: schema-validated tool selection with retries and clarify fallback.
- Product-list refresh: produces sandbox linking map and financial reports, and refreshes canonical Amazon cache files.
- Existing workflows: unaffected.

---

**END PRD_04**
