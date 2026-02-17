# AGENTS.md

Authoritative contributor guide for the Amazon FBA Agent System. This file consolidates the December 3rd wiki (`wiki-dec-3`), legacy CLAUDE guidance, and the current codebase into a single, file-grounded reference. References to automation tooling are intentionally excluded; this document is for humans working in this repository.

---

## 1. Verification, Backup, and Update Protocols

### 1.1 Mandatory Verification Protocols

- **NO_CLAIMS_WITHOUT_VERIFICATION**  
  Never claim that a task is done without reproducible, file-grounded proof.

- **FILE_VERIFICATION** – For any path you reference in code review, docs, or analysis:
  1. **VERIFY_EXISTENCE** – Check that the file/directory actually exists (e.g. `Get-ChildItem`).
  2. **CHECK_TIMESTAMP** – Confirm that timestamps are consistent with the workflow you are describing.
  3. **VERIFY_CONTENT** – Read and analyze the file content before making assertions about behaviour.
  4. **CONFIRM_SUPPLIER** – Ensure you are reasoning about the correct supplier (default: `poundwholesale.co.uk`).
  5. **USE_ABSOLUTE_PATHS** – When describing locations, use full paths rooted at  
     `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`.
  6. **NO ASSUMPTIONS** – Do not reference files or settings you have not actually opened.

### 1.2 Backup Protocol (Critical)

Before editing code, configuration, or key documentation:

1. **CREATE_BACKUP_DIR** – Under the repo root, create  
   `backup/<reason>_<YYYYMMDD>/`.  
   Example for documentation edits:  
   `backup\agents_update_20251203\AGENTS.md`.
2. **COPY_ALL_AFFECTED** – Copy every file you plan to modify into that directory.
3. **VERIFY_BACKUP** – Confirm the backup file(s) exist and have non-zero length before editing.

This mirrors the behaviour described in `wiki-dec-3\6. State Management System\6.2. Fixedenhancedstatemanager Implementation.md` and `utils\fixed_enhanced_state_manager.py`, which always create safe, atomic snapshots before modifying processing state files.

### 1.3 Update Protocol – Cascading Changes

When you change any code, path, or configuration:

1. **CASCADING UPDATES**  
   - Check all files that reference the modified symbol or path (use `rg` + `diagnostics_output\workflow_files.json`).  
   - Update acceptance tests and integration tests if behaviour changes.
2. **DOCUMENTATION SYNC**  
   - Update `AGENTS.md` when high-level workflow or structure changes.  
   - Update `CLAUDE.md` and `CLAUDE_STANDARDS.md` to keep human and tool guidance coherent.  
   - Update relevant `wiki-dec-3` pages if they have diverged from the actual code paths.
3. **PATH CONSISTENCY**  
   - Verify that `utils\path_manager.py` and `config\system_config.json` reflect any path changes.  
   - Check that the dashboard still resolves the same output locations.

### 1.4 Atomic Save and Resume Semantics

The system is intentionally designed to be **file-grounded** and **resumable**, as detailed in:

- `wiki-dec-3\6. State Management System\6.1. Processing State Tracking.md`  
- `wiki-dec-3\6. State Management System\6.3. Resumption Logic And Recovery.md`  
- `utils\fixed_enhanced_state_manager.py`  
- `utils\windows_save_guardian.py`

Key rules:

- Resume pointers (e.g. `system_progression.resumption_ptr`, `persistent_category_index`) **must only advance**; do not reduce them manually in state files.
- All critical writes to:
  - `OUTPUTS\CACHE\processing_states\*`  
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\*`  
  - `OUTPUTS\FBA_ANALYSIS\amazon_cache\*`  
  must go through atomic write patterns (WindowsSaveGuardian, `save_json_atomic`, or equivalent temp-then-replace logic in code).
- When repairing or migrating state, always:
  - Back up the original file under `backup\state_repair_<YYYYMMDD>\`.  
  - Record what changed and why in a small markdown note under `docs\` or `wiki-dec-3\11. Troubleshooting Guide\11.3. State Management Issues\`.

---

## 2. Architecture Overview (Code-Grounded)

This section aligns with `wiki-dec-3\1. Project Overview.md` and `3. Core Architecture\3.1. Workflow Engine.md`, but is constrained to what the current code actually does.

### 2.1 Primary Entry Points

The system uses per-supplier runner scripts as the primary entry points. Each supplier has its own `run_custom_{supplier}.py` file:

| Runner Script | Supplier Domain | Auth Helper Location |
|---------------|-----------------|---------------------|
| `run_custom_poundwholesale.py` | poundwholesale.co.uk | `tools/poundwholesale/` |
| `run_custom_clearance_king.py` | clearance-king.co.uk | `tools/clearance_king/` |
| `run_custom_angelwholesale-co-uk.py` | angelwholesale.co.uk | `tools/angelwholesale-co-uk/` |
| `run_custom_dkwholesale-com.py` | dkwholesale.com | `tools/dkwholesale-com/` |
| `run_custom_efghousewares-co-uk.py` | efghousewares.co.uk | `tools/efghousewares-co-uk/` |
| `run_custom_kdwholesale-co-uk.py` | kdwholesale.co.uk | `tools/kdwholesale-co-uk/` |
| `run_custom_laceywholesale-co-uk.py` | laceywholesale.co.uk | `tools/laceywholesale-co-uk/` |
| `run_custom_wholesaletradingsupplies-co-uk.py` | wholesaletradingsupplies.co.uk | `tools/wholesaletradingsupplies-co-uk/` |

Each runner follows the same structure:
- Initializes logging via `utils\logger.py`
- Loads configuration from `config\system_config.json` through `SystemConfigLoader`
- Connects to an existing Chrome instance via `utils\browser_manager.BrowserManager`
- Performs authentication (if required) using the supplier-specific authentication service
- Invokes `tools\passive_extraction_workflow_latest.PassiveExtractionWorkflow.run()`

- **Legacy master runner** – `run_complete_fba_system.py`  
  - Older orchestration script that still sets a hard-coded OpenAI key and uses `tools\output_verification_node` and `tools\supplier_guard`.  
  - Behaviour differs from the per-supplier runners documented in `wiki-dec-3`; treat it as **legacy** unless you have a specific reason to use it.

### 2.2 Core Workflow Engine

The central orchestrator is:

- `tools\passive_extraction_workflow_latest.py` → class `PassiveExtractionWorkflow`

Responsibilities (as confirmed by the wiki and code):

- Loads the full configuration via `SystemConfigLoader.get_full_config()` and derives the `system` section into `self.system_config`.
- Initializes:
  - State management via `utils\fixed_enhanced_state_manager.FixedEnhancedStateManager` (imported as `EnhancedStateManager` in code).  
  - Supplier scraping via `tools\configurable_supplier_scraper.ConfigurableSupplierScraper`.  
  - Amazon data extraction via `tools\amazon_playwright_extractor.FixedAmazonExtractor`.  
  - Atomic persistence via `utils\windows_save_guardian.WindowsSaveGuardian`.  
  - Path handling via `utils\path_manager.path_manager`.  
  - Monitoring via `utils\sentinel_monitor.SentinelMonitor`.
- Coordinates the full loop:
  1. Load predefined category URLs from `config\*_categories.json` using `_get_predefined_categories`.
  2. Initialize or resume state using the `FixedEnhancedStateManager` and `system_progression` fields.
  3. Run supplier extraction and Amazon analysis in **hybrid mode** (see `hybrid_processing` in `config\system_config.json`) so long as the config enables it.
  4. Save supplier caches, Amazon caches, linking maps, and processing state using atomic operations.
  5. Trigger financial calculations in `tools\FBA_Financial_calculator.run_calculations` once sufficient linking map entries exist.

For detailed sequence diagrams and method-level breakdowns, see:

- `wiki-dec-3\3. Core Architecture\3.1. Workflow Engine.md`
- `wiki-dec-3\5. Data Processing Workflow\5.2. Amazon Product Matching\`

### 2.3 Browser Management

Browser lifecycle is centralized in:

- `utils\browser_manager.py`  
- `wiki-dec-3\8. Browser Automation\8.1. Browser Management.md`

Key facts:

- Uses Playwright’s `chromium.connect_over_cdp` to attach to an **existing** Chrome instance. It does not launch Chromium on its own.  
- Supports IPv6 (`[::1]`) and IPv4 (`127.0.0.1`) endpoints for CDP.  
- Maintains a single, shared browser instance with an LRU page cache (`MAX_CACHED_PAGES = 1`) to keep extension behaviour stable.  
- Implements health monitoring, restart intervals, and memory thresholds to protect long-running sessions.

When running locally:

- Start Chrome explicitly, for example:  
  `chrome --remote-debugging-port=9222 --user-data-dir=C:\ChromeDebugProfile`
- The connection port is currently hard-coded to `9222` in the runners and the workflow’s `_initialize_amazon_extractor`, regardless of the `"chrome"` block in `system_config.json`. Changing `chrome.debug_port` alone will not change the actual port without code changes.

---

## 3. Configuration Management (system_config.json and Supplier Configs)

This section is aligned with `wiki-dec-3\4. Configuration Management\4.1. System Configuration.md` and `4.2. Supplier Configuration.md`, adjusted for the current code.

### 3.1 System Configuration Structure

Primary configuration file:

- `config\system_config.json`

Important top-level sections (as used by current code):

- `"system"` – Global processing settings:
  - `max_products`, `max_products_per_category`, `max_products_per_cycle`, `max_analyzed_products`.  
  - `supplier_extraction_batch_size`, `linking_map_batch_size`, `financial_report_batch_size`.  
  - `reuse_browser`, `max_tabs`, `output_root`.
- `"processing_limits"` – Price and quantity limits:
  - `min_price_gbp`, `max_price_gbp` (the £20 upper bound documented in wiki-dec-3).
- `"performance"` – Request concurrency, timeouts, and rate limiting.
- `"chrome"` – Browser-related settings (currently **not wired** to the actual CDP port in runners or workflow).
- `"analysis"` – ROI and profitability thresholds.
- `"amazon"` – Marketplace, currency, VAT, and fee defaults.
- `"supplier"` – Flags such as `prices_include_vat`.
- `"workflows"` – Per-supplier workflow definitions (PoundWholesale, Clearance King, etc.).
- `"hybrid_processing"` – Controls whether supplier extraction and Amazon analysis are interleaved.

The wiki’s configuration mermaid diagram in `4.1. System Configuration.md` accurately reflects these blocks and how they are intended to be used.

### 3.2 Configuration Loader Usage

File: `config\system_config_loader.py`

- `get_system_config()` – Returns the `"system"` block.  
- `get_full_config()` – Returns the entire parsed JSON; use this when you need access to `"chrome"`, `"performance"`, `"hybrid_processing"`, etc.  
- `get_workflow_config(key)` – Returns `full_config["workflows"][key]`.  
- `get_supplier_config(supplier_name)` and `get_credentials(supplier_name)` – Provide supplier defaults and credentials.

Important nuance:

- The workflow engine uses `get_full_config()` for root-level settings like `"hybrid_processing"` and `"processing_limits"`, but still attempts to read the CDP port from `self.system_config.get("chrome_debug_port", 9222)`. That key does not exist in the current `"system"` block; the default of `9222` is therefore always used.

### 3.3 Supplier Configuration Files

Directory:

- `config\supplier_configs\`

Examples:

- `poundwholesale.co.uk.json`  
- `clearance-king.co.uk.json`

Each supplier config typically includes:

- `base_url` – e.g. `https://www.poundwholesale.co.uk`  
- `login_config`:
  - `login_path`  
  - `test_product_url`  
  - `price_selectors`  
  - `authentication.login_selectors`

These are consumed by:

- `tools\standalone_playwright_login.py`  
- Supplier-specific authentication helpers under `tools\poundwholesale\` and `tools\clearance_king\`.

When adding a supplier, follow `wiki-dec-3\12. Supplier Integration Guide\` and ensure the new config aligns with these patterns.

---

## 4. Data Processing Workflow (Supplier → Amazon → Financials)

Reference wiki: `wiki-dec-3\5. Data Processing Workflow\`.

High-level sequence (mirrors the diagrams in `1. Project Overview.md` and `5. Data Processing Workflow`):

1. **Initialization**
   - Runners prepare logging and connect to Chrome via `BrowserManager`.
   - `PassiveExtractionWorkflow` loads configuration and state.

2. **Supplier Scraping**
   - `ConfigurableSupplierScraper` uses predefined category lists to scrape products in batches (`supplier_extraction_batch_size`).  
   - Products are cached under `OUTPUTS\cached_products\<supplier-normalized>_products_cache.json`.

3. **Amazon Matching**
   - `FixedAmazonExtractor` uses EAN-first, then title-based search to find candidate products on Amazon.  
   - Matching uses configurable similarity thresholds (see `"performance.matching_thresholds"` in `system_config.json`).
   - Results are cached to `OUTPUTS\FBA_ANALYSIS\amazon_cache\amazon_<ASIN>_<identifier>.json`.

4. **Linking and State Updates**
   - Each supplier product is associated with one Amazon ASIN in a linking map:  
     `OUTPUTS\FBA_ANALYSIS\linking_maps\<supplier>\linking_map.json`.  
   - `FixedEnhancedStateManager` updates:
     - `system_progression` (phase, persistent category index, resume pointers).  
     - Product and category counters.  
   - All writes are done atomically via WindowsSaveGuardian or equivalent.

5. **Financial Analysis**
   - `tools\FBA_Financial_calculator.run_calculations(supplier_name)` reads:
     - Supplier cache (`OUTPUTS\cached_products\...`).  
     - Amazon cache (`OUTPUTS\FBA_ANALYSIS\amazon_cache\`).  
     - Supplier-specific linking map.  
   - Computes ROI, net profit, margins, and writes CSVs under:  
     `OUTPUTS\FBA_ANALYSIS\financial_reports\<supplier-normalized>\*.csv`.

6. **Reports and Dashboard**
   - The Streamlit dashboard (`dashboard\app_fixed.py`) reads:
     - Processing state files under `OUTPUTS\CACHE\processing_states\`.  
     - Linking maps and financial reports under `OUTPUTS\FBA_ANALYSIS\`.  
     - Logs under `logs\debug\` and `OUTPUTS\DIAGNOSTICS\`.

For full diagrams, see:

- `wiki-dec-3\1. Project Overview.md` (workflow mermaid graph)  
- `wiki-dec-3\5. Data Processing Workflow\5.2. Amazon Product Matching\`  
- `wiki-dec-3\7. Financial Analysis Module\7.1. Profitability Analysis.md`

---

## 5. State Management System

Reference wiki: `wiki-dec-3\6. State Management System\`.

### 5.1 Processing State Files

Primary state paths (per `utils\path_manager.get_processing_state_path`):

- `OUTPUTS\CACHE\processing_states\<supplier-with-dots-replaced-by-underscores>_processing_state.json`

The state schema is documented in `6.1. Processing State Tracking.md` and implemented in `utils\fixed_enhanced_state_manager.py`. Key fields include:

- `schema_version` – e.g. `"1.2_THREAD_SAFE"`.  
- `created_at`, `last_updated` – ISO timestamps.  
- `supplier_name`.  
- `system_progression` – the authoritative resume pointer structure.  
- `supplier_extraction_progress` – per-category progress.  
- `metadata` – configuration hashes and fix markers.

### 5.2 FixedEnhancedStateManager Behaviour

`FixedEnhancedStateManager` (see `6.2. Fixedenhancedstatemanager Implementation.md`) is responsible for:

- Separating resumption indices from session progress so that interruptions do not reset progress.  
- Freezing category denominators once at startup and guarding against accidental overwrites.  
- Ensuring that `persistent_category_index` and other indices advance monotonically.  
- Providing atomic save methods to commit state safely on Windows.

Whenever you work on this area:

- Use the helper methods already present (e.g. `initialize_workflow_session`, `set_total_categories`, `save_state_atomic`).  
- Do not write ad-hoc JSON writes directly to processing state files.

---

## 6. Browser Automation and Diagnostics

Reference wiki: `wiki-dec-3\8. Browser Automation\`.

Key files:

- `utils\browser_manager.py` – browser lifecycle, CDP attachment, health checks.  
- `utils\browser_circuit_breaker.py` – circuit breaker for repeated failures.  
- `utils\sentinel_monitor.py` – monitors divergence between linking maps and caches.  
- `wiki-dec-3\8. Browser Automation\8.3. Chrome Devtools Protocol Diagnostics.md` – CDP troubleshooting.

Operational notes:

- Always use an existing Chrome instance with `--remote-debugging-port`.  
- Use the wiki troubleshooting guides if:
  - The workflow cannot connect to CDP.  
  - Keepa or SellerAmp extensions are not visible.  
  - The browser becomes unstable during long runs.

---

## 7. Financial Analysis and Reporting

Reference wiki: `wiki-dec-3\7. Financial Analysis Module\`.

Primary implementation:

- `tools\FBA_Financial_calculator.py`

Important details:

- Reads VAT and fee settings from `config\system_config.json` (`"amazon"` and `"supplier"` blocks).  
- Uses `get_supplier_specific_paths(supplier_name)` to:
  - Resolve supplier caches under `OUTPUTS\cached_products\`.  
  - Resolve linking maps under `OUTPUTS\FBA_ANALYSIS\linking_maps\<supplier>\`.  
  - Create supplier-specific financial reports under `OUTPUTS\FBA_ANALYSIS\financial_reports\<supplier-normalized>\`.
- Surfaces CSV fields described in `AGENTS.md`’s original financial section and elaborated in the wiki’s `7.1. Profitability Analysis.md`.

---

## 8. Coding Standards and Development Practices

These standards combine the existing `CLAUDE_STANDARDS.md` expectations with the repo’s formatting and typing rules.

- **Python version** – Target 3.12+ (3.13 is used in tests and examples).  
- **Style** – 4-space indentation, 100-character lines, imports ordered per `pyproject.toml` (Black + Ruff/isort).  
- **Typing** – Public functions should include type hints; avoid implicit `Any`.  
- **Logging** – Use `logging.getLogger(__name__)` and the shared logger configuration in `utils\logger.py`. Avoid bare `print` for runtime events.  
- **Minimal blast radius** – Keep changes as small and focused as possible; follow the update and backup protocols above.  
- **No committed secrets** – Credentials and API keys must be moved into environment variables or ignored configuration files; do not introduce new secrets into tracked files.

For detailed standards, see:

- `CLAUDE_STANDARDS.md` – development guidelines.  
- `wiki-dec-3\2. Installation And Setup.md` – environment and dependency expectations.

---

## 9. Testing, Quality Gates, and Tooling

Quality gates (mirroring earlier AGENTS content, still valid):

- **Static checks**
  - `ruff check .`  
  - `black --check .`  
  - `mypy tools config utils`
- **Tests**
  - `pytest -q`  
  - `pytest -m "requires_browser"` (with Chrome CDP running)  
  - `pytest --cov=tools --cov=config --cov=utils -q`
- **Optional tox**
  - `tox -e py312,lint,type-check,coverage-report`  
  - `tox -e security` (safety, pip-audit, bandit)

When modifying core workflow, state management, or configuration:

- Prefer targeted tests under `tests\` when available.  
- For configuration changes, run a short dry run (limit categories/products), then inspect:
  - `OUTPUTS\CACHE\processing_states\...`  
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\...`  
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\...`

---

## 10. Dashboard and Monitoring

Reference wiki: `wiki-dec-3\13. Dashboard.md`, plus `11. Troubleshooting Guide\`.

### 10.1 Dashboard

- Entry point: `dashboard\run_dashboard.py`.  
- Main app: `dashboard\app_fixed.py`.  
- Requires `streamlit` and `pandas`.

Launch examples:

```bash
python dashboard/run_dashboard.py
# or
python -m streamlit run dashboard/app_fixed.py --server.port 8501
```

The dashboard reads:

- Processing state files from `OUTPUTS\CACHE\processing_states\`.  
- Linking maps and financial CSVs from `OUTPUTS\FBA_ANALYSIS\`.  
- Debug logs from `logs\debug\`.

### 10.2 Diagnostics

- `OUTPUTS\DIAGNOSTICS\save_telemetry.log` – WindowsSaveGuardian telemetry.  
- `OUTPUTS\DIAGNOSTICS\monitor_trace.log` – run monitor output.  
- `logs\application\*.log`, `logs\debug\*.log`, `logs\api_calls\*.jsonl` – historical behaviour and API traces.

When investigating issues:

- Consult the relevant wiki troubleshooting section under `wiki-dec-3\11. Troubleshooting Guide\`.  
- Cross-check state files and linking maps for consistency (SentinelMonitor logs divergence).

---

## 11. Supplier Onboarding

For onboarding new wholesale suppliers, use the **supplier-onboarding** skill:

- **Skill location**: `.claude/skills/supplier-onboarding/SKILL.md`
- **Wizard utility**: `utils/supplier_onboarding_wizard.py`

### 11.1 Automated 7-Step Workflow

The skill provides a guided workflow:

1. **Data Preprocessing** - LLM validates categories and selectors
2. **Gather Information** - Collects domain, auth requirements, credentials
3. **Prepare Configurations** - Creates JSON config files
4. **Invoke Wizard** - Generates runner script and auth helper
5. **Validate Files** - Verifies generated files are correct
6. **Pre-Run Verification** - Checks system readiness
7. **User Decision** - Test run, main run, or fix issues

### 11.2 Naming Conventions

The system uses three distinct naming forms:

| Context | Form | Example |
|---------|------|---------|
| Config files | Dot-form | `supplier.com.json` |
| System config | Dot-form | `"supplier_name": "supplier.com"` |
| Runner scripts | Hyphen-form | `run_custom_supplier-com.py` |
| Tool directories | Hyphen-form | `tools/supplier-com/` |
| Workflow keys | Underscore-form | `supplier_workflow` |
| State files | Underscore-form | `supplier_com_processing_state.json` |

### 11.3 Quick Wizard Command

```bash
python utils/supplier_onboarding_wizard.py \
  --domain "supplier.com" \
  --categories-source "config/supplier_categories.json" \
  --selectors-source "config/supplier_configs/supplier.com.json" \
  --workflow-key "supplier_workflow" \
  --mode generate \
  --authentication-required false
```

---

## 12. References and Knowledge Base

- High-level guidance: `CLAUDE.md`, `CLAUDE_STANDARDS.md`  
- Installation and setup: `wiki-dec-3\2. Installation And Setup.md`  
- Core architecture and workflow: `wiki-dec-3\1. Project Overview.md`, `3. Core Architecture\3.1. Workflow Engine.md`  
- State management: `wiki-dec-3\6. State Management System\`  
- Financial analysis: `wiki-dec-3\7. Financial Analysis Module\`  
- Browser automation: `wiki-dec-3\8. Browser Automation\`  
- Caching and deduplication: `wiki-dec-3\9. Caching And Deduplication\`  
- Dashboard and monitoring: `wiki-dec-3\13. Dashboard.md`  
- Tooling and project layout: `PROJECT_INDEX.md`, `PROJECT_INDEX.json`, `pyproject.toml`, `tox.ini`

When in doubt, treat `wiki-dec-3` and this `AGENTS.md` as the primary documentation sources and reconcile any older documents (e.g. archived reports under `archive\` or older wiki folders) against the current code paths before relying on them.

---

## 13. Memory & Documentation Update Policy

### 13.1 When to Update Memory and Documentation

**Update ONLY after code changes are VERIFIED:**
- Tests pass (pytest, lint, type-check)
- Manual verification complete
- Code is stable (not during active development that may revert)

**Never update during:**
- Active debugging sessions
- Experimental feature development
- Before changes are committed and tested

### 13.2 Verification Gate

Before updating memory or documentation:

1. **Complete changes** → Code is written and tested
2. **Run verification** → `pytest`, `ruff`, `black --check`, or manual test
3. **Run Sentinel check** → `python utils/memory_sentinel.py --check`
4. **Review drift report** → If drift detected, verify it's intentional
5. **User confirmation** → Explicit "Update memory" approval
6. **Update documentation** → Update relevant docs/*.md files
7. **Update Supermemory** → Add new granular memories via supermemory(mode="add", ...)
8. **Refresh baseline** → `python utils/memory_sentinel.py --update`

### 13.3 Staging Area

Draft memory updates in `docs/_MEMORY_STAGING.md` before promoting to:
- Canonical documentation (docs/*.md)
- Supermemory entries (permanent knowledge)

### 13.4 Automation Hooks (Optional)

For OpenCode with plugin support, sentinel.ts can auto-detect edits:
- Events: `file.edited`, `file.watcher.updated`
- Logic: Check if file matches critical patterns → Run sentinel.py → Prompt user if drift detected

