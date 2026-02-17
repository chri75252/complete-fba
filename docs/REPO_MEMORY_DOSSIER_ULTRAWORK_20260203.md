# Repo Memory Dossier (UltraWork)

**Repo**: Amazon FBA Agent System (v3.5+)

**Generated**: 2026-02-03

**Scope**: This dossier is intentionally **code-grounded**. Markdown docs are treated as secondary and may be outdated. Where docs disagree with code, this dossier follows code and records drift.

**Root path** (as requested):
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

---

## 0) Executive Summary (What exists today)

This repo currently contains **three major operational surfaces**:

1) **Supplier scraping + Amazon matching + financial reporting** (“classic workflow”)
- Entry points: `run_custom_*.py`
- Orchestrator: `tools/passive_extraction_workflow_latest.py` (class `PassiveExtractionWorkflow`; entry `run()` at `tools/passive_extraction_workflow_latest.py#L2125`)
- Persistence: `OUTPUTS/*` (supplier cache, Amazon cache, linking map, processing state)

2) **Dashboard (Streamlit)** (“monitoring + operator + chat”)
- Launcher: `dashboard/run_dashboard.py`
- Main app: `dashboard/app_fixed.py`
- Key new tabs: `Dashboard`, `Operator`, `Chat`

3) **Control Plane** (“chat/ops backend + job runner + RAG”) 
- CLI: `python -m control_plane worker` and `python -m control_plane build-index`
- Job queue + status files persisted under: `OUTPUTS/CONTROL_PLANE/*`
- Chat uses tool planning + execution with write-confirmation gating

Additionally, there is a **separate analysis subsystem** under `src/fba_agent/` with its own CLI entrypoint under `fba_agent/__main__.py` and tests under `tests/fba_agent/*`. This appears to be distinct from the scraping workflow.

---

## 1) Tech Stack / Tooling (verified)

### Python
- Project targets `>=3.12` per `pyproject.toml`.
- Current environment reports: `Python 3.13.3` (note: some runner scripts contain explicit Windows event-loop logic for Python 3.13+).

### Key libraries
- Browser automation: `playwright==1.40.0` (`requirements.txt`)
- Data processing: `pandas==2.1.4`, `numpy==1.26.2` (`requirements.txt`)

### Quality gates
- `pyproject.toml` defines:
  - Black: line length 100
  - Ruff: enabled
  - Mypy: configured (gradual strictness)
- `tox.ini` defines environments: `py312`, `lint`, `type-check`, `security`, `coverage-report`.

---

## 2) Core “Classic Workflow” Architecture (code-grounded)

### 2.1 Supplier runner scripts (entrypoints)
- Runners use `SystemConfigLoader`, `BrowserManager`, and then `PassiveExtractionWorkflow`.
- Example: `run_custom_poundwholesale.py#L61` loads config and workflow key `poundwholesale_workflow`.

### 2.2 Orchestrator: `PassiveExtractionWorkflow`
- `tools/passive_extraction_workflow_latest.py#L2125` is the main `run()` loop.
- Configuration is split:
  - `system` section read into `self.system_config` (for limits)
  - root-level config used for `hybrid_processing`.

### 2.3 State manager: `FixedEnhancedStateManager`
- `utils/fixed_enhanced_state_manager.py#L247` declares `initialize_workflow_session()` as the *PRIMARY ENTRY POINT*.
- It loads state, runs startup analysis, returns `persistent_category_index`.
- Resume toggle exists:
  - `pipeline_toggles.resume.use_reverse_gap_heuristic` read in `perform_startup_analysis`.

### 2.4 Supplier scraping: `ConfigurableSupplierScraper`
- Uses the shared `BrowserManager`.
- Page fetch: `tools/configurable_supplier_scraper.py#L329`.

### 2.5 Amazon extraction: `tools/amazon_playwright_extractor.py`
- `AmazonExtractor.connect()` attaches via `BrowserManager` singleton (see file header section).
- IMPORTANT: module hard-exits if `OPENAI_API_KEY` missing:
  - `tools/amazon_playwright_extractor.py#L43`
  - This is a *runtime behavior* and impacts any script importing this module.

### 2.6 Persistence patterns
- Linking map saves are guarded and atomic:
  - `tools/passive_extraction_workflow_latest.py#L3521` uses `WindowsSaveGuardian.save_json_atomic(..., min_entries_guard=1000)`.
- Processing state writes are via state manager atomic save.

### 2.7 Financial reporting triggers
- End-of-run trigger:
  - `tools/passive_extraction_workflow_latest.py#L3163` calls `tools.FBA_Financial_calculator.run_calculations(self.supplier_name)`
- Hybrid batch trigger:
  - `_check_financial_report_trigger` reads `financial_report_batch_size` via config loader and triggers on linking map size.

### 2.8 Hybrid mode
- Hybrid enabled by config:
  - `tools/passive_extraction_workflow_latest.py#L2385` reads `full_config["hybrid_processing"]["enabled"]`
- Hybrid runs chunk loop + filtering and per-category completion writes.

---

## 3) Browser Model (CDP attach) (code + best practices)

### 3.1 Repo implementation
- `utils/browser_manager.py#L77` connects to an *existing* Chrome instance via CDP.
- Probes `/json/version` on IPv6 first, then IPv4:
  - `utils/browser_manager.py#L242` and `utils/browser_manager.py#L281`
- Uses `chromium.connect_over_cdp` with an HTTP endpoint:
  - `utils/browser_manager.py#L108`

### 3.2 Best-practice alignment (Playwright)
- Playwright’s canonical connect-over-CDP examples use an HTTP URL like `http://127.0.0.1:<port>/`.
- Robust readiness pattern is `/json/version` + optional `webSocketDebuggerUrl`.
- Python API supports `is_local=True` optimization (not currently used in repo).

---

## 4) Dashboard (Streamlit) (code-grounded)

### 4.1 Launcher
- `dashboard/run_dashboard.py#L90` runs Streamlit pointing at `dashboard/app_fixed.py` when present.

### 4.2 Main app: tabs include Chat + Operator
- `dashboard/app_fixed.py#L523` sets tabs: `["Dashboard", "Operator", "Chat"]`.
- It injects `st.session_state["supplier"] = supplier` before rendering chat:
  - `dashboard/app_fixed.py#L543`

### 4.3 Chat panel
- `dashboard/chat_panel.py#L88` is the entrypoint.
- State is stored in Streamlit session state:
  - `dashboard/chat_panel.py#L79` initializes `chat_messages` and pending tool call fields.
- Confirmation gating:
  - Write tools are staged in `pending_tool_call`, then executed only on “Confirm execute”.

### 4.4 Operator control plane UI
- `dashboard/pages/01_Operator_Control_Plane.py` provides a UI to enqueue runs with explicit confirmation.
- It merges overrides into a per-run `system_config.merged.json` and writes a `categories_subset.json`.

---

## 5) Control Plane (Chat backend + jobs + RAG)

### 5.1 CLI
- `control_plane/__main__.py#L9` supports:
  - `python -m control_plane worker`
  - `python -m control_plane build-index`

### 5.2 Worker (job runner)
- Job types:
  - `control_plane/job_types.py#L5`
- Worker reads pending jobs, moves them pending→running→done/failed, writes status/logs:
  - `control_plane/worker.py#L174` selects job type
  - For run workflow jobs it sets `FBA_SYSTEM_CONFIG_PATH` if provided:
    - `control_plane/worker.py#L186`
  - For product list refresh it executes `python -m control_plane.run_product_list_refresh`:
    - `control_plane/worker.py#L190`

### 5.3 Chat orchestrator (tool planning + execution)
- Tool planning / execution lives in `control_plane/chat_orchestrator.py`.
- `enqueue_run` creates sandbox supplier domains and writes override config + category subset (see `chat_orchestrator.py` around the `enqueue_run` tool handler).

### 5.4 Audit
- Tool calls are appended to JSONL:
  - `control_plane/audit.py#L15` writes to `OUTPUTS/CONTROL_PLANE/audit/chat_tool_calls.jsonl`

### 5.5 RAG
- Index is written to `OUTPUTS/CONTROL_PLANE/index/rag_index.json`.
- Builder reads:
  - `.qoder/repowiki/en/content/*.md`
  - `OUTPUTS/DIAGNOSTICS/trace_*.json`
  - `OUTPUTS/DIAGNOSTICS/system_touch_report.json`
- Builder: `control_plane/rag_index.py#L51` and `control_plane/rag_index.py#L140`.
- Retrieval uses simple token overlap scoring with budgets, and skips secrets:
  - `control_plane/rag_retriever.py#L53`

### 5.6 RD2 policy (RAG triggers + secret redaction)
- `control_plane/rd2_policy.py` defines trigger words and blocked paths.

---

## 6) Supplier Onboarding Wizard (code-grounded)

### 6.1 Invocation
- Direct: `python utils/supplier_onboarding_wizard.py --input <input.json> --output <output.json>`
- Via control plane job:
  - `control_plane/worker.py#L195` runs the wizard with `--input/--output`.

### 6.2 Naming conventions and where files land
- Wizard defines “three forms” of supplier identity:
  - dot-form domain, hyphen-form supplier_id, underscore-form for state file naming
  - `utils/supplier_onboarding_wizard.py#L101`

### 6.3 Important internal inconsistency (must know)
- The wizard contains *two competing* category config naming strategies:
  1) `NamingConventions.categories_config_path()` defaults to `config/{workflow_key}_categories.json` and writes it back if missing.
     - `utils/supplier_onboarding_wizard.py#L199`
  2) Elsewhere, generation logic writes categories as `config/{domain_first_label}_categories.json` (not shown in this excerpt, but confirmed by prior exploration).

This should be treated as a known sharp edge during onboarding.

---

## 7) Product List Refresh (control-plane job)

- Runner module: `control_plane/run_product_list_refresh.py`.
- It imports and uses `FixedAmazonExtractor` from `tools/amazon_playwright_extractor.py`:
  - `control_plane/run_product_list_refresh.py#L12`
- It uses a canonical amazon cache naming pattern `amazon_{asin}_{ean_safe}.json` where missing EAN becomes `N`:
  - `control_plane/run_product_list_refresh.py#L49`
- It hardcodes debug port usage in this module (`9222`) in the excerpted section:
  - `control_plane/run_product_list_refresh.py#L163`

---

## 8) Separate subsystem: `fba_agent` (analysis pipeline)

This repo contains a distinct analysis toolchain under `src/fba_agent/`.

- Entry point shim: `fba_agent/__main__.py#L7` inserts `src/` onto `sys.path`.
- CLI supports `analyze`, `top`, `explain`, `export`, `rerun`, `list-runs`, `show-memory`:
  - `src/fba_agent/cli.py#L21`
- Main orchestration: `src/fba_agent/run.py#L59`.
- Outputs:
  - Runs are written under a `runs_dir` (default in constants) and include `evidence.jsonl` and `run_summary.json`.

This appears orthogonal to the scraping workflow and should be documented as a separate surface.

---

## 9) Repo size signals (quick metrics)
- Python files (repo-wide): ~1117 (includes backups/copies).
- Tests under `tests/`: 47 files detected by `rg --files tests` (note: this is a file count, not number of tests).

---

## 10) Recommended “source of truth” hierarchy

1) **Code** (always)
2) Control plane on-disk artifacts:
   - `OUTPUTS/CONTROL_PLANE/index/system_index.json` (built by `python -m control_plane build-index`)
   - `OUTPUTS/CONTROL_PLANE/index/rag_index.json` (built by Chat panel button or `control_plane/rag_index.py`)
3) `.qoder/repowiki/*` (used by RAG; good for retrieval but can drift)
4) `docs/*` and root MDs (useful but not authoritative)

---

## 11) Runbooks (most useful operational commands)

### 11.1 Run classic supplier workflow
1) Start Chrome with remote debugging:
- `chrome --remote-debugging-port=9222 --user-data-dir=C:\ChromeDebugProfile`
2) Run a supplier runner:
- `python run_custom_poundwholesale.py`

### 11.2 Run Streamlit dashboard (with chat)
- `python dashboard/run_dashboard.py`

### 11.3 Run control plane worker (needed for chat “write” actions)
- `python -m control_plane worker`

### 11.4 Build system index and RAG index
- System index: `python -m control_plane build-index` (writes `OUTPUTS/CONTROL_PLANE/index/system_index.json`)
- RAG index:
  - From UI: Chat panel “Build RAG index” button (`dashboard/chat_panel.py#L117`)
  - CLI equivalent: `python -c "from control_plane.rag_index import write_rag_index; print(write_rag_index())"` (writes `OUTPUTS/CONTROL_PLANE/index/rag_index.json`)

---

## 12) Verification commands (repo-defined)

- Lint: `tox -e lint`
- Type-check: `tox -e type-check`
- Tests: `tox -e py312`

(End)