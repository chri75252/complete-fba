# AGENTS.md

Authoritative agent/contributor guide for the Amazon FBA Agent System. Mirrors prior AGENTS.md/CLAUDE.md with updated, exhaustive, file‑grounded instructions. MCP/Serena‑specific items intentionally excluded.

---

## 🚨 Agent Directives — Execute Immediately

### Mandatory Verification Protocols
- ✅ NO_CLAIMS_WITHOUT_VERIFICATION: Never mark done without reproducible, file‑grounded proof.
- ✅ FILE_VERIFICATION: For every referenced path:
  1) VERIFY_EXISTENCE (list/inspect path), 2) CHECK_TIMESTAMP (recent), 3) VERIFY_CONTENT (read/analyze),
  4) CONFIRM_SUPPLIER (default poundwholesale.co.uk), 5) USE_ABSOLUTE_PATHS in explanations, 6) NO_ASSUMPTIONS.

### Backup Protocol — Critical
1) CREATE_BACKUP_DIR `backup/<reason>_<YYYYMMDD>/` 2) COPY_ALL_AFFECTED 3) VERIFY_BACKUP (size/time) before edits.

### Update Protocol — Cascading Changes
1) CASCADE_UPDATES across code/tests/docs/dashboard 2) DOC_SYNC (AGENTS.md, CLAUDE.md, docs/) 3) PATH_CONSISTENCY (system_config.json, path helpers).

### Atomic Save & Resume Semantics
- All state is file‑grounded; resume pointers are monotonic and must only advance. Do not “reset” without explicit backup + approval. Use WindowsSaveGuardian patterns for critical writes.

---

## 📦 Architecture Overview

- Entry runner: `run_custom_poundwholesale.py` — initializes logging, loads `config/system_config.json`, attaches to Chrome CDP via BrowserManager, orchestrates PassiveExtractionWorkflow.
- Core engine: `tools/passive_extraction_workflow_latest.py` (PassiveExtractionWorkflow) — deterministic, config‑driven scrape/match/financials with batched saves and resumable state.
- Browser attach: `utils/browser_manager.py` — attaches to existing Chrome (v139+), IPv6/IPv4 auto‑detect, health checks, single‑page LRU policy.
- Authentication: `tools/poundwholesale/supplier_authentication_service.py` (selector checks), `tools/standalone_playwright_login.py` (config‑driven login + price access verification).
- State safety: `utils/fixed_enhanced_state_manager.py` (resume pointers), `utils/windows_save_guardian.py` (atomic writes + telemetry).
- UI/monitoring: `dashboard/` (Streamlit), `tools/run_monitor.py` (state/log tail to DIAGNOSTICS).

Chrome v139+ Note — Use existing Chrome only; BrowserManager resolves `[::1]`/`localhost`. Verify CDP: `curl http://localhost:9222/json/version`.

---

## 🧭 End‑to‑End Workflow (Authoritative Trace)

1) Initialization
- Launch Chrome with CDP: Windows `chrome --remote-debugging-port=9222 --user-data-dir=C:\\ChromeDebugProfile`; Linux/WSL `google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_debug &`.
- Verify endpoint, then runner loads config, sets up BrowserManager/logging.

2) Authentication
- Verify current session via selectors; login if needed with config‑driven selectors (no vision required). Optional price‑access verification.

3) Supplier Scraping (Deterministic)
- Predefined categories (AI disabled). Processed in batches controlled by `supplier_extraction_batch_size`. Product cache saved atomically.

4) Amazon Matching
- EAN‑first, title fallback with similarity check; exclude sponsored/invalid results. Cache JSON per ASIN.

5) Financial Analysis
- Compute net profit, ROI, margins; VAT/referral/FBA/prep/ship handled explicitly.

6) Atomic State & Resume
- Write linking maps and processing state atomically; store resume pointers `{phase, cat_idx, prod_idx}`.

7) Finalization & Reports
- Save final CSV under `financial_reports`. Optionally print top 5 by ROI.

ASCII
```
run_custom_poundwholesale.py -> BrowserManager.attach(CDP) -> PassiveExtractionWorkflow.run()
  -> scrape supplier (batched) -> match amazon -> financials
  -> cache + linking_map + processing_state (atomic) -> reports
```

---

## 🗃️ Active Component Inventory (Files, Scripts, Logs)

Runner
- `run_custom_poundwholesale.py` — main orchestrator; prints platform info, sets up logger, loads SystemConfigLoader, launches BrowserManager, calls PassiveExtractionWorkflow.run().

Core Workflow (tools)
- `tools/passive_extraction_workflow_latest.py` — engine. Key methods: `run()`, `_extract_supplier_products()` (batched), `_get_amazon_data()` (EAN‑first/title‑fallback), state saves, report generation.
- `tools/configurable_supplier_scraper.py` — supplier scraping. Key APIs: `scrape_products_from_url(...)`, `scrape_products_from_prefiltered_urls(...)`, extraction helpers (`extract_title/price/url/image/identifier/ean/...`).
- `tools/amazon_playwright_extractor.py` — Amazon extraction. Classes: `AmazonExtractor`, `FixedAmazonExtractor`. APIs: `search_by_ean_and_extract_data(...)`, `search_by_title(...)`, `extract_data(asin)`.
- `tools/FBA_Financial_calculator.py` — financials. Functions: `financials(supplier, amazon, supplier_price)`, `run_calculations(...)` → CSV. Reads VAT and fee config; extracts Keepa‑derived fees when present.
- `tools/standalone_playwright_login.py` — selector‑based login, price‑access verification; supports supplier_config JSON.
- `tools/run_monitor.py` — tails `OUTPUTS/DIAGNOSTICS/save_telemetry.log` and processing state; writes `OUTPUTS/DIAGNOSTICS/monitor_trace.log`.

Utilities (utils)
- `utils/browser_manager.py` — attach over CDP to existing Chrome; IPv6/IPv4 resolution; health checks; LRU page reuse; navigation via circuit breaker.
- `utils/fixed_enhanced_state_manager.py` — resume pointers, high water marks, progress indexes (file‑grounded semantics).
- `utils/windows_save_guardian.py` — atomic writes with telemetry (`OUTPUTS/DIAGNOSTICS/save_telemetry.log`), fallback strategies for WinError 5, temp‑then‑replace.
- `utils/sentinel_monitor.py` — divergence detection between linking map and caches; records shrink events; tracks retries.
- `utils/path_manager.py` — path normalization and cross‑platform helpers.
- `utils/logger.py` — logger setup (debug/info). Prefer logging over prints.

Configuration (config)
- `config/system_config_loader.py` — typed loader around `config/system_config.json` with helpers (system/amazon/supplier/workflow getters).
- `config/system_config.json` — single source of truth for limits, batching, timeouts, output roots, and feature toggles.
- `config/supplier_configs/<domain>.json` — supplier‑specific base_url, login selectors, test product URL, and price selectors. Secrets excluded.

Dashboard (dashboard)
- `dashboard/run_dashboard.py` — launcher, dependency checks, base dir env set, chooses `app_fixed.py` when present.
- `dashboard/app.py` / `dashboard/app_fixed.py` — Streamlit app; reads processing state, linking map, financial CSVs, and logs.
- `dashboard/metrics_core.py` / `metrics_core_fixed.py` — aggregation helpers for KPIs.
- `dashboard/samples/` — example CSV/JSON/logs for demo.

Tests (tests)
- Not exhaustive here; key acceptance/flow tests include: `tests/test_acceptance_gate.py`, `tests/test_login_step.py`, `tests/test_integration.py`, plus unit suites.

Logs & Diagnostics
- `logs/application/*.log` — historical runs and system logs.
- `logs/api_calls/*.jsonl` — API call logs (legacy/optional; AI features disabled by default).
- `OUTPUTS/DIAGNOSTICS/save_telemetry.log` — atomic save telemetry (WindowsSaveGuardian).
- `OUTPUTS/DIAGNOSTICS/monitor_trace.log` — monitor tail output.

Generated Outputs (never commit)
- `OUTPUTS/CACHE/processing_states/<supplier>_processing_state.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/<supplier>/linking_map.json`
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/*.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/*.csv`

---

## 🧮 Financial Reports — Expected Columns (CSV)

Produced by `tools/FBA_Financial_calculator.py` (sorted by ROI when present):
- Identification: `ASIN`, `EAN`, `SupplierTitle` (when available)
- Prices: `SupplierPrice_incVAT`, `SupplierPrice_exVAT`, `SellingPrice_incVAT`
- Fees & VAT: `ReferralFee`, `FBAFee`, `PrepHouseFee`, `OutputVAT`, `InputVAT`
- Profitability: `NetProfit`, `ROI` (percent), `ProfitMargin` (percent)
- Notes: ROI computed on ex‑VAT cash tied up; margin computed against selling price ex‑VAT. Fees may be overridden by Keepa‑derived values when detected.

Top‑line stats (printed by calculator when run): counts over ROI thresholds and `top_5_by_roi` including `ASIN`, `EAN`, `SupplierTitle`, `ROI`, `NetProfit`, `SellingPrice_incVAT`, `SupplierPrice_incVAT`.

---

## 🧩 Multi‑Supplier Architecture

Supplier Normalization
- Supplier names normalize between `domain.tld`, `domain_tld`, and `domain-tld`. Output directories follow normalized naming (both hyphen/underscore variants are tolerated by dashboards/tools).

Adding/Enabling a Supplier
1) Create `config/supplier_configs/<domain>.json` with:
   - `base_url` (no trailing slash)
   - `login_config`: `login_path`, `test_product_url`, `price_selectors`, `authentication.login_selectors`
2) Update `config/system_config.json` supplier sections if limits/paths differ.
3) Validate login with `tools/standalone_playwright_login.py` using the supplier config (price access check).
4) Run `run_custom_poundwholesale.py` (or a supplier‑specific runner) with categories for that supplier (predefined list; AI category discovery disabled).
5) Verify OUTPUTS trees (processing_state, linking_map, financial_reports) under normalized supplier folder.

Per‑Supplier State & Output Paths
- `OUTPUTS/CACHE/processing_states/<supplier>_processing_state.json`
- `OUTPUTS/FBA_ANALYSIS/linking_maps/<supplier>/linking_map.json`
- `OUTPUTS/FBA_ANALYSIS/financial_reports/<...>.csv`
- `OUTPUTS/FBA_ANALYSIS/amazon_cache/*.json`

---

## 🖥️ Dashboard (Streamlit)

Launch
```
python dashboard/run_dashboard.py
# or
python -m streamlit run dashboard/app.py --server.port 8501
```

Environment
- Optional `FBA_BASE_DIR` to point to repo root.

Data Sources (read‑only)
- Processing state, linking map, financial CSVs, and recent logs as listed in Active Component Inventory.

Features
- Live category/progress view, matching KPIs, ROI distributions, and streaming log tail.

---

## 🔧 Commands & Quality Gates

Environment (Windows)
```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Run & Verify
```
chrome --remote-debugging-port=9222 --user-data-dir=C:\ChromeDebugProfile
curl http://localhost:9222/json/version
python run_custom_poundwholesale.py --debug
```

Quality Gates
```
ruff check .
black --check .
mypy tools config utils
pytest -q
pytest -m "requires_browser"
pytest --cov=tools --cov=config --cov=utils -q
```

Optional tox
```
tox -e py312,lint,type-check,coverage-report
tox -e security   # safety, pip-audit, bandit
```

---

## 📝 Coding Standards & Agent Conduct

- Python 3.12; 4‑space indent; 100 char lines (Black/Ruff). Keep imports ordered (Ruff/isort rules in pyproject).
- Public functions/type hints expected; avoid implicit Any; explicit returns preferred.
- Logging over prints; use `logging.getLogger(__name__)` and repo logger helpers.
- Agent Conduct (STRICT):
  - Read code/configs before proposing changes. Avoid generic claims.
  - Perform minimal‑blast‑radius edits; keep style consistent with surrounding code.
  - Never hardcode credentials/URLs that belong in config; update docs/dashboards when paths change.

---

## ✅ Testing Guidelines

- Pytest markers (pyproject): `unit`, `integration`, `requires_browser`, `slow`.
- Structure: `tests/test_*.py`; classes `Test*`; functions `test_*`.
- Keep browser‑dependent paths guarded; ensure CDP is running for `requires_browser`.
- Coverage on `tools`, `config`, `utils`; maintain acceptance suites (e.g., `tests/test_acceptance_gate.py`, `tests/test_login_step.py`).

---

## ⚙️ Configuration & Environment

- `config/system_config.json` is source of truth for limits, batching, price ranges, paths; read via `SystemConfigLoader`.
- Environment examples:
```
CHROME_REMOTE_PORT=9222
OUTPUTS_BASE_PATH=./OUTPUTS
output_root=./OUTPUTS
```
- Supplier credentials via environment or external, untracked secrets files. Do not commit secrets.

Change Validation
- For config edits, run a short dry run (limit products/categories), then inspect processing_state, linking_map, and financial CSVs for regressions.

---

## 📈 Monitoring & Diagnostics

- `tools/run_monitor.py` → `OUTPUTS/DIAGNOSTICS/monitor_trace.log` with state/log tails.
- WindowsSaveGuardian telemetry: `OUTPUTS/DIAGNOSTICS/save_telemetry.log`.
- Historical logs: `logs/application/*.log`, `logs/api_calls/*.jsonl` (legacy/optional).

---

## 🔒 Security & Safety

- Never commit secrets. Prefer env vars / ignored configs.
- Use atomic save helpers for critical state (temp‑then‑replace; WindowsSaveGuardian). Backup before recovery steps.

---

## 🔁 Commit & PR Workflow

- Commits: imperative; Conventional prefixes (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). One logical change per commit.
- PRs: pass Ruff/Black/MyPy/Pytest; update docs/dashboards for path/schema changes; include reproduction & verification steps; attach short logs/screenshots for browser/dashboard changes; exclude OUTPUTS/ and large logs.

---

## 🧩 Troubleshooting (Quick Reference)

CDP Fails
```
curl http://localhost:9222/json/version
netstat -an | findstr :9222   # Windows
taskkill /F /IM chrome.exe     # if needed, relaunch with CDP flags
```

Resume/State Issues
- Inspect latest processing_state and linking_map; ensure pointers only advance; back up before repairs.

Dashboard Empty
- Verify required OUTPUTS and logs exist; set `FBA_BASE_DIR` if running outside root.

---

## 📚 References

- CLAUDE guidance: `CLAUDE.md`, `CLAUDE_STANDARDS.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
- Knowledge base: `wiki repo 19 nov/`
- Tooling: `pyproject.toml`, `tox.ini`

