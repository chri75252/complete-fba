# PRD #1 — Control Plane + Tool Contracts (Execution‑Ready)

**Repo:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

**Date:** 2026-01-25

## 0. Summary
Build a minimal-risk “control plane” that lets a future Webchat UI (Phase 2) safely:
- enqueue runs (supplier + category subset + runtime limits)
- monitor progress from file-grounded truth
- query outputs (financial reports, linking maps, caches)
- run supplier onboarding wizard

Key principles:
- minimal / surgical edits to existing core scripts
- all write actions are gated, atomic, and backed up
- default behavior is read-only querying

This PRD intentionally treats the existing workflow and runners as a “black box” that produces file outputs.

## 1. Goals
### 1.1 Primary Goals
1. Provide a stable, file-grounded interface to run and monitor the system.
2. Allow per-run config/category overrides without repeatedly editing canonical `config/system_config.json`.
3. Make all run operations addressable by a deterministic tool layer (Python functions) for later LLM tool-calling.
4. Maintain single-user / single-machine assumptions.

### 1.2 Non-Goals
- No refactor of `tools/passive_extraction_workflow_latest.py` beyond minimal hook(s).
- No change to scraping/matching business logic.
- No attempt to “auto-fix” code bugs.

## 2. Constraints & Guardrails
1. **Backups mandatory** before modifying any existing script or canonical config file.
2. **Atomic writes mandatory** for any JSON / config files written by control plane.
3. **Single-writer rule**: only the control-plane executor writes config overrides and enqueues jobs.
4. **Write actions require explicit confirmation** (enforced in Phase 2 chat UI; in Phase 1 via CLI flags).
5. **No secrets exposure**: log redaction for obvious API key patterns.

## 3. High-Level Architecture
### 3.1 Components
1. **Control Plane Worker** (new): watches a jobs directory and executes jobs as subprocesses.
2. **Tool Contract Library** (new): pure-Python functions for reading status, querying outputs, and creating jobs.
3. **Per-Run Overrides** (new): files stored under a run workspace; control plane points system to these.
4. **System Awareness Index** (new): curated index JSON listing key paths/artifacts for the assistant.
5. **Operator UI (Phase 1)** (new): Streamlit UI with forms/buttons to create jobs, monitor status, and query outputs.
6. **Optional LLM Parser (Phase 1)** (new): natural-language → structured parameters *only* (fills the Operator UI form; does not execute writes without confirmation).

### 3.2 Why This Approach
- You should not have to hand-write job JSON or CLI commands.
- Streamlit reruns make direct subprocess spawning risky; worker isolates execution.
- Per-run overrides reduce risk of corrupting canonical configs.
- Deterministic tool contracts are reusable for future MCP (optional) with minimal rewrite.
- LLM is optional and constrained to parameter extraction so Phase 1 remains low-risk.

## 4. Directory Layout (New)
All Phase 1 artifacts live under:
- `C:\...\OUTPUTS\CONTROL_PLANE\`

### 4.1 Paths
- `OUTPUTS/CONTROL_PLANE/jobs/pending/`
- `OUTPUTS/CONTROL_PLANE/jobs/running/`
- `OUTPUTS/CONTROL_PLANE/jobs/done/`
- `OUTPUTS/CONTROL_PLANE/jobs/failed/`
- `OUTPUTS/CONTROL_PLANE/status/`
- `OUTPUTS/CONTROL_PLANE/logs/`
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/`
- `OUTPUTS/CONTROL_PLANE/index/system_index.json`

## 5. Run & Job Model
### 5.1 Run ID
- `run_id`: UUID4 string.

### 5.2 Job Manifest (Schema)
File: `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`

```json
{
  "schema_version": "1.0",
  "run_id": "<uuid>",
  "created_at": "2026-01-25T00:00:00Z",
  "job_type": "run_workflow",
  "supplier_domain": "poundwholesale.co.uk",
  "workflow_key": "poundwholesale_workflow",
  "runner_script": "run_custom_poundwholesale.py",
  "override": {
    "system_config_path": "OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json",
    "categories_path": "OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json"
  },
  "runtime": {
    "max_products": 100,
    "max_products_per_category": 5
  },
  "notes": "user request"
}
```

Supported `job_type` values:
- `run_workflow`
- `run_onboarding_wizard`

### 5.3 Job Status (Schema)
File: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`

```json
{
  "schema_version": "1.0",
  "run_id": "<uuid>",
  "state": "queued|running|done|failed",
  "supplier_domain": "poundwholesale.co.uk",
  "started_at": "...",
  "ended_at": "...",
  "pid": 12345,
  "resolved_paths": {
    "processing_state": "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json",
    "runner_log": "OUTPUTS/CONTROL_PLANE/logs/<run_id>.log",
    "latest_financial_report": "OUTPUTS/FBA_ANALYSIS/financial_reports/poundwholesale-co-uk/fba_financial_report_*.csv"
  },
  "progress": {
    "current_phase": "supplier|amazon_analysis|...",
    "persistent_category_index": 1,
    "total_categories": 233,
    "current_category_url": "...",
    "supplier_products_completed": 0,
    "supplier_products_needing_extraction": 0,
    "amazon_products_completed": 0,
    "amazon_products_needing_analysis": 0
  },
  "artifacts": {
    "cached_products_exists": true,
    "linking_map_exists": true,
    "financial_report_exists": false
  },
  "error": {
    "summary": "",
    "last_log_lines": []
  }
}
```

## 6. Per-Run Overrides
### 6.1 Categories Subset File
File: `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json`

```json
{
  "schema_version": "1.0",
  "supplier_domain": "poundwholesale.co.uk",
  "category_urls": ["https://...", "https://..."]
}
```

### 6.2 System Config Merge Strategy
- Base config: canonical `config/system_config.json`
- Merge rules:
  - deep-merge dicts
  - arrays replaced (not concatenated)
  - write merged JSON to `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`

## 7. Tool Contract Library (New)
Location:
- `control_plane/` package (new) OR `utils/control_plane/` (new)

### 7.0 LLM Provider Abstraction (Phase 1 optional)
If Phase 1 includes the optional LLM parser, implement a small provider interface so we can support:
- cloud API LLMs (OpenAI/Anthropic)
- local model runtime (Ollama, LM Studio HTTP, etc.)

**Provider interface (conceptual):**
- `generate_json(prompt: str) -> dict`

**Provider selection (env/config):**
- `CONTROL_PLANE_LLM_PROVIDER=none|openai|anthropic|ollama|lmstudio`

**Required behavior:**
- hard JSON output (no prose) for the parser
- deterministic schema validation + retry if invalid JSON
- configurable model name and base URL

**Note:** In Phase 1 the LLM acts only as a *parser* (parameter extraction). It does not execute tools.

### 7.1 Read-Only Tools
- `get_latest_status(run_id: str) -> dict`
- `get_supplier_status(supplier_domain: str) -> dict` (reads processing state + latest log)
- `tail_run_log(run_id: str, lines: int) -> list[str]`
- `find_latest_financial_report(supplier_domain: str) -> str | None`
- `query_financial_rows(supplier_domain: str, filters: dict, limit: int) -> dict`
  - filters: EAN, ASIN, ROI min/max, NetProfit min/max, Sales min, etc.

### 7.2 Write/Exec Tools (Phase 1 CLI-gated)
- `create_job_run_workflow(...) -> run_id`
- `create_job_onboarding_wizard(input_json_path, output_json_path) -> run_id`
- `write_categories_subset(run_id, urls) -> path`
- `write_merged_system_config(run_id, overrides) -> path`

## 8. Control Plane Worker (New)
### 8.1 Operation
- Poll `jobs/pending` every 1s (no watchdog dependency).
- Acquire global lock file: `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`.
  - If lock exists: do not start a second run.
- Move job file to `jobs/running`.
- Spawn subprocess:
  - `python <runner_script>` for `run_workflow`
  - `python utils/supplier_onboarding_wizard.py --input ... --output ...` for onboarding
- Tee stdout/stderr to `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`.
- Update `status/<run_id>.json` every 2 seconds.
- On completion, update status state and move job to done/failed.

### 8.2 Worker Launch
- Manual start (recommended):
  - `python -m control_plane.worker`

## 8.3 Operator UI (Phase 1) — Streamlit Forms + Buttons
### 8.3.1 Purpose
Provide a **non-chat** interface so you can use Phase 1 immediately without writing JSON or CLI commands.

### 8.3.2 UI Entry
- New file: `dashboard/operator_control_plane.py` (or `dashboard/pages/Operator.py` if you prefer Streamlit pages).
- The UI is a thin client over the Tool Contract Library.

### 8.3.3 Features
- **Run Builder**
  - Supplier dropdown (from `config/system_config.json` workflows)
  - Category selection:
    - multi-select categories (loaded from the supplier’s categories JSON)
    - paste category URLs (textarea)
  - Limits:
    - max products
    - max products per category
  - Button: **Create Job** → writes subset + merged config + job manifest
  - Button: **Start Worker** (optional) or “Worker status” indicator

- **Monitor Run**
  - Select run_id (from `OUTPUTS/CONTROL_PLANE/status/`)
  - Show progress bar and key fields from status JSON
  - Show last N log lines (from per-run log)

- **Query Financials**
  - Supplier dropdown
  - Filters (EAN, ROI min, NetProfit min, limit)
  - Button: **Run Query** → loads latest CSV and shows results table

### 8.3.4 Write/Exec Confirmation
- Operator UI must have an explicit confirmation checkbox:
  - “I understand this will start a workflow run / write override files”
- Without confirmation, UI can still do read-only queries.

## 8.4 Optional LLM Parser (Phase 1) — Parameter Extraction Only
### 8.4.1 What This Adds (vs no parser)
**Without parser:** you manually fill the Operator UI fields (supplier dropdown, categories, limits).

**With parser:** you type natural English, and the UI auto-fills fields.

Example input:
- “Run poundwholesale on categories A, B, C, max 50 products”

Example result:
- supplier dropdown auto-selected
- limits auto-filled
- category URLs auto-populated (if provided)

### 8.4.2 Purpose
Reduce friction for you (no CLI, no JSON authoring) while keeping Phase 1 low-risk.

### 8.4.3 LLM Parser Input/Output
- Input: natural language text
- Output: **JSON only** payload, validated by code, used to populate the Operator UI.

```json
{
  "intent": "enqueue_run",
  "supplier_domain": "poundwholesale.co.uk",
  "max_products": 50,
  "max_products_per_category": 50,
  "category_urls": ["https://...", "https://..."],
  "roi_min": null,
  "netprofit_min": null,
  "ean": null,
  "limit": null,
  "confidence": 0.8,
  "missing_fields": []
}
```

### 8.4.4 Intent Set
- `enqueue_run`
- `query_financial`
- `show_status`
- `tail_logs`

### 8.4.5 Critical Constraint (Safety Boundary)
- The LLM parser **must not** enqueue runs, write files, or start subprocesses.
- It only proposes parameters.
- The Operator UI performs validation and requires explicit confirmation before any write/exec.

### 8.4.6 What You *Can* Do With This In Phase 1
You **can** type:
- “Analyze poundwholesale categories a,b,c max 50 products”

The actual execution will still follow this deterministic chain:
1) LLM outputs parameters (fills form)
2) You confirm
3) Operator UI writes job + overrides
4) Worker runs `run_custom_*.py`

So the workflow can run; the LLM is just not allowed to run it without your click.

## 9. Minimal Core Script Changes (Planned)
These changes are explicitly allowed by user instruction, and are intended to be minimal but high-impact.

### 9.1 Change A: Config path override via ENV (SystemConfigLoader)
**File:** `config/system_config_loader.py`

**Current**: constructor accepts `config_path`, otherwise uses canonical `config/system_config.json`.

**Planned**: if `config_path` is None, check env var `FBA_SYSTEM_CONFIG_PATH` first.

**Impact**:
- No behavior change unless env var is set.
- Enables per-run merged config without touching canonical config.

**Test surface affected**:
- Any code that instantiates `SystemConfigLoader()` without args.

### 9.2 Change B: Categories path override in workflow
**File:** `tools/passive_extraction_workflow_latest.py`

**Current** `_get_predefined_categories` (lines ~3893-3924): loads `config/<base_name>_categories.json` by convention.

**Planned**: prefer `self.workflow_config.get("categories_config_path")` (same as `_get_authoritative_category_count` already does at lines ~1902-1916), fallback to current convention.

**Impact**:
- No behavior change if workflow_config has no `categories_config_path`.
- Enables per-run category subset safely by pointing workflow config to a generated subset file.

**Test surface affected**:
- Category list selection at run start.

## 10. System Awareness Index
File: `OUTPUTS/CONTROL_PLANE/index/system_index.json`

Contents:
- list of suppliers (from `config/system_config.json` workflows)
- known runner scripts
- known category config files
- last modified timestamps for key outputs
- resolved root paths

Refresh:
- `python -m control_plane.build_index` (manual)

## 11. Acceptance Criteria (Phase 1)
1. Creating a job manifest creates `run_id` and pending job file.
2. Worker picks it up, writes status file within 2 seconds.
3. Status file updates progress fields based on processing state.
4. Logs are captured to per-run log file.
5. Financial query tool can filter latest report and return top N rows.
6. If env var not set, system behaves identically.

## 12. Out of Scope / Deferred (Phase 2)
- Streamlit chat UI integration.
- LLM tool-calling integration.
- Background streaming UI.

