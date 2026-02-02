# Implementation Prompt: Chat UI (PRD_03 v1.1) + Product‑List Refresh (PRD_04)

Use this prompt to drive an implementation agent. It references the authoritative PRDs and the current repo state.

---

## 0) Repo Root (absolute)

`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

---

## 1) Authoritative PRDs

1) Chat UX only (must implement first):
- `SYSTEM_CHAT_UI_PRDS/PRD_03_CHAT_UX_ONLY_v1_1.md`

2) Chat UX + product list refresh capability:
- `SYSTEM_CHAT_UI_PRDS/PRD_04_CHAT_PLUS_PRODUCT_LIST_REFRESH.md`

---

## 2) Existing State (important)

### 2.1 OllamaProvider methods already added

The agent previously started PRD_03’s first step by adding `generate_with_tools()` and `generate_text()` to:
- `control_plane/llm/providers.py`

Confirm current state:
- `OllamaProvider.generate_json()` uses `format="json"` and `temperature=0`
- `OllamaProvider.generate_with_tools()` exists and calls `/api/chat`
- `OllamaProvider.generate_text()` exists and calls `/api/generate`

**Do NOT revert these.** Only adjust if needed for reliability (e.g., `temperature=0` for deterministic planner mode; `think` optional).

### 2.2 Chat UI already has tool output expander

- `dashboard/chat_panel.py` currently stores tool results in `tool_result` and renders JSON in an expander.
- Ensure it stays that way (no raw dict string dumping).

### 2.3 Ask‑clarify tool exists

- `control_plane/tools/clarify.py` exists and returns structured questions.
- PRD_03 v1.1 requires tools return structured output; UI renders prose.

### 2.4 Sandbox category runs already exist

- `control_plane/chat_orchestrator.py` already enforces `enqueue_run` requires non-empty `category_urls` (otherwise switches to `ask_clarify`).
- It writes sandbox overrides via:
  - `write_categories_subset`
  - `write_merged_system_config`
  - `enqueue_run_job`

---

## 3) Hard Constraints (do not violate)

- Do NOT edit core workflow engine:
  - `tools/passive_extraction_workflow_latest.py`
  - `utils/*`
  - existing `run_custom_*.py` scripts

- Do NOT modify main OUTPUTS artifacts for production suppliers.

- Do NOT add secrets.

---

## 4) Implementation Goals

### Phase A: Implement PRD_03 v1.1 (Chat UX only)

**Goal**: Conversational chat with deterministic tool execution.

Required behaviors:
1) Message contract: store prose in `content`, tool JSON in `tool_call`/`tool_result`.
2) Read vs write tool UX:
   - Read: execute immediately
   - Write: require confirmation
3) Clarify-first: ambiguous -> `ask_clarify`
4) Local LLM reliability:
   - schema-validated tool selection
   - whitelist tool names
   - validate required params
   - retry up to 2 times if invalid JSON
   - fallback to clarify
5) Tool schema single source of truth (registry) to avoid drift.

Target files:
- `control_plane/chat_orchestrator.py`
- `control_plane/tools/__init__.py` and potentially a new `control_plane/tools/registry.py`
- `dashboard/chat_panel.py`

### Phase B: Implement PRD_04 product‑list Amazon refresh

Add new write tool:
- `enqueue_product_list_refresh`

Add new job type:
- `run_product_list_refresh`

Add new runner script under `control_plane/` (not `tools/`):
- `control_plane/run_product_list_refresh.py`

Outputs must be sandboxed:
- `sandbox_supplier = <supplier_domain>__sandbox__<run_id[:8]>`

Amazon cache freshness policy (approved):
- overwrite canonical file:
  - `OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_{ASIN}_{EAN}.json`

Then run:
- `tools.FBA_Financial_calculator.run_calculations(sandbox_supplier)`

---

## 5) Critical Technical Notes

### 5.1 Financial calculator lookup behavior

Financial calculator prefers:
- `amazon_{asin}_{ean}.json` first
and otherwise falls back to scanning for any file containing the ASIN.

Therefore canonical overwrite is required for determinism.

Reference:
- `tools/FBA_Financial_calculator.py` (functions: `find_amazon_json_by_linking_map`, `find_amazon_json_by_asin`)

### 5.2 Avoid relying on OpenAI

`tools/amazon_playwright_extractor.py` hard exits if `OPENAI_API_KEY` missing.

Product list refresh workflow should avoid importing modules that exit, or else require dummy key.

Preferred: implement a minimal Amazon search/extract module under `control_plane/` using BrowserManager.

---

## 6) Verification Requirements

- Run `python -m py_compile` on modified/new files.
- Ensure LSP diagnostics are clean on changed files.
- Provide a manual test script / steps:
  - start streamlit dashboard
  - run a read tool query
  - run enqueue_run with confirmation
  - run enqueue_product_list_refresh with confirmation

---

## 7) Deliverables

1) PRD_03 behaviors implemented.
2) Product list refresh implemented and runnable via chat.
3) UI shows prose-first + JSON expanders for tool call and tool result.
4) Tool registry prevents schema drift.

---

## 8) Notes about Serena MCP

Serena MCP is for code navigation/research, not for executing operational workflows.

Reference:
- `LOCAL_LLM_SERENA_MCP_INTEGRATION_GUIDE.md` (aligned with PRD_03/PRD_04)
- `.serena/project.yml` is read-only and ignores OUTPUTS/logs (expected).

---

**END IMPLEMENTATION PROMPT**
