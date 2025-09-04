# Repository Guidelines

## Project Structure & Module Organization
- Tools: core agents in `tools/` (e.g., `supplier_authentication_service.py`, `configurable_supplier_scraper.py`, `amazon_playwright_extractor.py`, `FBA_Financial_calculator.py`, `passive_extraction_workflow_latest.py`).
- Utilities: shared infra in `utils/` (e.g., `enhanced_state_manager.py`, `browser_manager.py`).
- Config: settings in `config/` (`system_config.json`, `poundwholesale_categories.json`).
- Outputs: caches/reports in `OUTPUTS/` (`FBA_ANALYSIS/`, `CACHE/`).
- Orchestration: `PassiveExtractionWorkflow` in `tools/passive_extraction_workflow_latest.py` coordinates agents.
- Tests: reside in `tests/`, named `test_*.py` with markers.

## Build, Test, and Development Commands
- Install deps: `python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt`.
- Run workflow: `python run_complete_fba_system.py` (or `python run_custom_poundwholesale.py`).
- Run tests: `pytest -q`; fast subset: `pytest -m "not requires_browser"`.
- Coverage: `pytest --cov`.
- Lint/format: `ruff check .` and `black .` (see `pyproject.toml`).

## Coding Style & Naming Conventions
- Python 3.12; 4-space indentation; max line length 100.
- Naming: functions/modules `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Imports: follow Ruff/isort grouping (standard, third-party, first-party: `tools`, `utils`, `config`).
- Type hints encouraged; MyPy config present (optional run: `mypy .`).

## Testing Guidelines
- Framework: `pytest` with markers: `unit`, `integration`, `requires_browser`.
- Location/naming: put tests in `tests/`, files `test_*.py`.
- Browser tests: isolate with `-m requires_browser`; avoid network by default.
- Aim to cover code paths you touch; verify with `pytest --cov`.

## Commit & Pull Request Guidelines
- Commits: use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`), subject ≤72 chars; body explains why.
- PRs: clear summary, linked issues, validation steps, risks/rollbacks; include sample outputs or screenshots when logs/UI change.

## Security & Configuration Tips
- Do not commit secrets; prefer `.env` and load via config. Review `config/system_config.json` for placeholders only.
- Authentication uses a pre-launched Chrome with remote debugging; ensure the configured port is running before scraping.
- Long runs write to `OUTPUTS/`; do not remove caches while agents run.

## Agent-Specific Pointers
- Authentication: `tools/supplier_authentication_service.py` uses `standalone_playwright_login.py`; verify login via visible prices (source of truth).
- Supplier Scraper: `tools/configurable_supplier_scraper.py`; consider periodic flushes to `OUTPUTS/cached_products/...` for resilience.
- Amazon Extractor: `tools/amazon_playwright_extractor.py` (EAN-first, title fallback); caches JSON under `OUTPUTS/FBA_ANALYSIS/amazon_cache/`.
- Financial Analysis: `tools/FBA_Financial_calculator.py`; writes CSV to `OUTPUTS/FBA_ANALYSIS/financial_reports/`.
- State Manager: `utils/enhanced_state_manager.py`; persists at `OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json`.

## Architecture Overview
The system runs primarily in Hybrid Processing Mode: per-category loop performing supplier extraction → Amazon matching → financial analysis, with deterministic resumption via `system_progression` and atomic writes.

```mermaid
flowchart TD
  EP[Entry Points\nrun_custom_poundwholesale.py\nrun_complete_fba_system.py] --> WF[Orchestrator\nPassiveExtractionWorkflow\n tools/passive_extraction_workflow_latest.py]

  subgraph Config
    SC[config/system_config.json]
    PC[config/poundwholesale_categories.json]
    CL[config/system_config_loader.py]
  end
  SC --> CL --> WF
  PC --> WF

  subgraph Utils
    BM[utils/browser_manager.py]
    WSG[utils/windows_save_guardian.py]
    UF[utils/url_cache_filter.py]
    PM[utils/path_manager.py]
  end
  BM --> WF
  WSG --> WF
  PM --> WF

  subgraph Agents
    AU[Authentication\n tools/supplier_authentication_service.py]
    SS[Supplier Scraper\n tools/configurable_supplier_scraper.py]
    AX[Amazon Extractor\n tools/amazon_playwright_extractor.py]
    FC[Financial Calculator\n tools/FBA_Financial_calculator.py]
    SM[State Manager\n utils/enhanced_state_manager.py]
  end

  WF --> AU -->|session cookies| WF
  WF -->|category loop (hybrid)| SS
  SS -.->|Filter: LM → Cache → Extract| UF
  SS -->|products JSON\nOUTPUTS/cached_products/...| WF
  WF -->|EAN-first, title fallback| AX
  AX -->|amazon_cache JSON\nOUTPUTS/FBA_ANALYSIS/amazon_cache/| WF
  WF --> FC -->|CSV append| OUT[OUTPUTS/FBA_ANALYSIS/financial_reports]
  WF -->|update + resume\nsystem_progression| SM
  SM -->|processing_state JSON\nOUTPUTS/CACHE/processing_states/...| WF
  WF --> BM
  BM --> AU
  BM --> AX

  classDef store fill:#f7f7f7,stroke:#999,color:#333
  OUT:::store
  SC:::store
  PC:::store
```
