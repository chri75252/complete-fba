# PRD #2 — Webchat UI + Agent Behaviors (Execution‑Ready)

**Repo:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

**Phase 1 dependency:** Must already exist and be functional:
- `control_plane/*`
- `dashboard/operator_control_plane.py`
- Operator tab in `dashboard/app_fixed.py`
- Control-plane job/status folders under `OUTPUTS/CONTROL_PLANE/*`

**Local LLM:** Ollama + `deepseek-r1:7b` running on `http://localhost:11434`

---

## 0) Goal
Deliver a **single webchat interface inside the existing dashboard** that can:
- understand user requests in natural language
- call deterministic tools to query outputs / monitor runs / troubleshoot
- (with explicit confirmation) enqueue runs and invoke supplier onboarding
- maintain “system awareness” via a curated index derived from:
  - `OUTPUTS/DIAGNOSTICS/system_touch_report.json`
  - `.qoder/repowiki/en/content/**/*.md`
  - key curated folders and configs

The chat must be **safe** and **file-grounded**:
- default = read-only
- write/exec requires explicit confirmation

---

## 1) Non‑Goals
- No autonomous code patching of workflow scripts.
- No refactor of `tools/passive_extraction_workflow_latest.py`.
- No multi-user support.
- No external hosting.

---

## 2) User Stories
### Read-only
1. “Show me products where ROI > 30% and NetProfit > 5 for poundwholesale.”
2. “What is the system doing right now? Which phase/category?”
3. “Why did the last run fail?” (summarize status + last log lines + recommendation)
4. “Find products with EAN 503123… across latest report.”

### Write/Exec (explicitly confirmed)
5. “Run poundwholesale only on categories A,B,C with max 50 products.”
6. “Onboard supplier `newsupplier.com` using these categories and selectors.”
7. “Monitor run <run_id> and update me when category index changes.”

---

## 3) UX Requirements
### 3.1 Placement
- Add a third tab in `dashboard/app_fixed.py`: `Chat`.
  - `Dashboard` tab: existing
  - `Operator` tab: existing
  - `Chat` tab: Phase 2

### 3.2 Chat UI
- Use Streamlit chat primitives:
  - `st.chat_message`
  - `st.chat_input`
- Conversation stored in `st.session_state["chat_messages"]`.
- Display tool actions taken (transparent tool traces).

### 3.3 Confirmation gating
- Any tool classified as `write` or `exec` must require:
  - a UI confirmation step (checkbox + “Confirm execute” button)
  - a generated “execution preview” describing what files will be written and what job will be enqueued

### 3.4 Run monitor UI
- Chat can pin an active `run_id`.
- Chat tab shows:
  - current `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
  - last N log lines
  - last update timestamp

---

## 4) System Awareness / Indexing
### 4.1 Inputs
- `OUTPUTS/DIAGNOSTICS/system_touch_report.json` (touched scripts/files)
- `OUTPUTS/DIAGNOSTICS/trace_*.json` (execution traces with inputs/outputs)
- `.qoder/repowiki/en/content/**/*.md` (workflow documentation)
- curated core paths:
  - `config/system_config.json`
  - `config/*_categories.json`
  - `config/supplier_configs/*.json`
  - `run_custom_*.py`
  - `tools/passive_extraction_workflow_latest.py`
  - `utils/supplier_onboarding_wizard.py`
  - `OUTPUTS/CACHE/processing_states/*`
  - `OUTPUTS/FBA_ANALYSIS/linking_maps/*/linking_map.json`
  - `OUTPUTS/FBA_ANALYSIS/financial_reports/*/*.csv`
  - `logs/debug/*.log`

### 4.2 Output index file
- Build and maintain:
  - `OUTPUTS/CONTROL_PLANE/index/system_index.json`

Index contents (minimal, structured):
- workflow list from `config/system_config.json` (workflow_key, supplier_name, categories_config_path, test_product_url, authentication_required)
- entry points from `run_custom_*.py` (filename only)
- key outputs per supplier (resolved via `dashboard/metrics_core.py::MetricsLoader.resolve_paths`)
- touched scripts list from `system_touch_report.json`
- trace summaries from `OUTPUTS/DIAGNOSTICS/trace_*.json` (inputs/outputs, scripts_loaded)
- repowiki page list + titles
- last modified timestamps for key output folders

### 4.3 Index refresh
- Provide a button in Chat tab: “Refresh system index”.
- Refresh is deterministic and local (no LLM).

---

## 5) LLM Integration
### 5.1 Default model
- Local Ollama:
  - provider: `ollama`
  - model: `deepseek-r1:7b`
  - endpoint: `http://localhost:11434/api/chat`

### 5.2 Fallback models
- OpenAI (if key present)
- Anthropic (if key present)

### 5.3 Roles in Phase 2
- LLM acts as a **tool-calling planner**:
  - reads index + user question
  - chooses tools
  - produces structured tool call(s)
  - summarizes results

### 5.4 Hard constraints
- LLM must not be allowed to write arbitrary files.
- The only write paths are:
  - `OUTPUTS/CONTROL_PLANE/*`
  - onboarding wizard session inputs under a controlled folder (e.g. `OUTPUTS/CONTROL_PLANE/onboarding_sessions/*`)

---

## 6) Tooling / Agent Capabilities
Phase 2 should call the existing deterministic tool layer (Phase 1), extending it minimally.

### 6.1 Read-only tools (no confirmation)
- `FinancialQuery.query_financial_rows(...)` via `control_plane/financial_query.py`
- `StatusReader.get_status(run_id)` via `control_plane/status_reader.py`
- `StatusReader.tail_run_log(run_id, lines)`
- `MetricsLoader.resolve_paths(supplier)` via `dashboard/metrics_core.py`
- `read_system_index()` (new small helper)
- `read_trace_summary()` (new helper for `OUTPUTS/DIAGNOSTICS/trace_*.json`)

### 6.2 Write/exec tools (require confirmation)
- `JobManager.create_run_workflow_job(...)` via `control_plane/job_manager.py`
- `JobManager.create_onboarding_job(...)`

### 6.3 Troubleshooting agent behavior (read-only)
A deterministic routine invoked by LLM:
- read `status/<run_id>.json`
- tail last 200 lines of run log
- read processing state file if present
- classify likely causes (CDP not running, missing files, auth failure, selector error)
- return “evidence + next steps”

---

## 7) Supplier Onboarding in Chat
- Chat collects inputs (domain, auth required, categories, selectors, test product URL).
- Chat writes onboarding input session JSON under:
  - `OUTPUTS/CONTROL_PLANE/onboarding_sessions/<session_id>/input.json`
- Chat enqueues onboarding job:
  - `job_type=run_onboarding_wizard`
  - worker runs `python utils/supplier_onboarding_wizard.py --input ... --output ...`
- Chat reads output JSON and summarizes generated files + remediation.

### 7.1 Onboarding Checklist (based on wizard sanity checks)
- Scraping rate: `supplier_products_completed >= 20`
- Amazon cache: at least one `amazon_*.json` within 15 minutes of run start
- Linking map: `OUTPUTS/FBA_ANALYSIS/linking_maps/<supplier>/linking_map.json` updated and >100 bytes
- Financial CSV: `OUTPUTS/FBA_ANALYSIS/financial_reports` has recent `fba_financial_report_*.csv` >1KB
- Processing state: `OUTPUTS/CACHE/processing_states/<supplier>_processing_state.json` updated after run start
- No critical errors in `logs/debug/run_custom_*.log` (ERROR/CRITICAL/Traceback)

The chat UI should expose a “Run Onboarding Checklist” action that reports pass/fail per item and shows remediation guidance from the wizard.


---

## 8) Logging / Audit
- Every tool call (read/write/exec) is recorded to:
  - `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`

For each entry:
- timestamp
- user message id
- tool name
- parameters
- result summary (redacted)

---

## 9) Safety & Permissions
- Enforce a strict tool allowlist.
- Explicit confirmation for write/exec.
- Single-run lock already exists from Phase 1 (`OUTPUTS/CONTROL_PLANE/lock/active_run.lock`).

---

## 10) Test Plan (Phase 2)
### 10.1 Prerequisites
- Ollama running: `http://localhost:11434/api/tags` must return model list.
- Phase 1 worker can run and create statuses.
- `OUTPUTS/DIAGNOSTICS/system_touch_report.json` exists.
- At least one trace file in `OUTPUTS/DIAGNOSTICS/trace_*.json`.
- Repowiki exists under `.qoder/repowiki/en/content/`.

### 10.2 Test cases
1. Chat basic: message persists across reruns.
2. Read-only query: “ROI>30 NetProfit>5” returns table with columns matching `FBA_Financial_calculator.py` output.
3. Status query: “show status for run_id …” returns JSON summary + last log lines.
4. Troubleshoot: “why failed” returns evidence-based diagnosis referencing status/logs.
5. Enqueue run: chat proposes job; requires confirm; job appears in pending folder.
6. Onboarding: chat writes onboarding session input; requires confirm; job enqueued.
7. Onboarding checklist: returns pass/fail for all six wizard checks.
8. Index refresh: updates `system_index.json` and chat can cite it.
9. Trace ingestion: chat can summarize touched scripts from `trace_*.json`.

---

## 11) Implementation Notes (minimal edits)
- Primary edit target: `dashboard/app_fixed.py` to add `Chat` tab.
- New module: `dashboard/chat_panel.py` (recommended) to keep `app_fixed.py` clean.
- New helper scripts in `control_plane/` for index building, trace ingestion, and audit writing.

## 12) Run‑Impacting Configuration (from `config/system_config.json`)
These fields directly affect run behavior and should be surfaced in the chat UI when building a run:

**System limits** (`system`):
- `max_products`
- `max_analyzed_products`
- `max_products_per_category`
- `max_products_per_cycle`
- `supplier_extraction_batch_size`
- `linking_map_batch_size`
- `financial_report_batch_size`
- `max_categories_to_process`

**Processing limits** (`processing_limits`):
- `max_products_per_category`
- `max_products_per_run`
- `pagination_safety_limit`
- `min_price_gbp`
- `max_price_gbp`
- `category_validation.timeout_seconds`

**Performance** (`performance`):
- `max_concurrent_requests`
- `request_timeout_seconds`
- `retry_attempts`
- `retry_delay_seconds`
- `rate_limiting.rate_limit_delay`
- `timeouts.*`

**Hybrid processing** (`hybrid_processing`):
- `enabled`
- `switch_to_amazon_after_categories`
- `processing_modes.chunked.chunk_size_categories`

**Workflow-specific** (`workflows.<workflow_key>`):
- `supplier_name`
- `supplier_url`
- `categories_config_path`
- `authentication_required`
- `test_product_url`

**Financial config** (impacts financial outputs):
- `amazon.vat_rate`
- `amazon.fba_fees.*`
- `supplier.prices_include_vat`
- `analysis.min_roi_percent`
- `analysis.min_profit_per_unit`

Fields like `monitoring`, `cache`, and `surgical_fixes` affect behavior but are not primary run-configuration inputs; expose them only in advanced settings.

