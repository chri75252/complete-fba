# COMPLETE WORKFLOW UPDATED 2026 Q1

This document provides a comprehensive overview of the Amazon FBA Agent System's architecture, workflows, and operational procedures as of Q1 2026.

---

## 1. System Architecture Overview

The system operates across three primary surfaces, each serving a distinct operational need:

### 1.1 Classic Surface (CLI)
- **Entry Points**: `run_custom_{supplier}.py` (e.g., `run_custom_poundwholesale.py`).
- **Core Orchestrator**: `tools/passive_extraction_workflow_latest.py`.
- **Purpose**: Direct, high-performance execution of extraction and analysis for specific suppliers.
- **Mechanism**: Connects to an existing Chrome instance via CDP (port 9222) and executes the `PassiveExtractionWorkflow`.

### 1.2 Dashboard Surface (Visual)
- **Entry Point**: `dashboard/run_dashboard.py` (which launches `dashboard/app_fixed.py`).
- **Technology**: Streamlit.
- **Purpose**: Real-time monitoring of processing state, financial report visualization, and log inspection.
- **Mechanism**: Reads directly from the `OUTPUTS/` directory to provide a live view of system progression.

### 1.3 Control Plane Surface (Autonomous)
- **Entry Point**: `control_plane/worker.py`.
- **Purpose**: Managed background execution, job queuing, and remote control capabilities.
- **Mechanism**: Uses a worker-based architecture to spawn and manage workflow jobs, often overriding configuration via environment variables for dynamic scaling.

---

## 2. Core Workflows

### 2.1 Passive Extraction Workflow (Standard)
1. **Initialization**: Load `system_config.json`, verify Chrome connection, and initialize `FixedEnhancedStateManager`.
2. **Supplier Scraping**: `ConfigurableSupplierScraper` processes category URLs, caching products to `OUTPUTS/cached_products/`.
3. **Amazon Matching**: `FixedAmazonExtractor` performs EAN/Title searches, caching results to `OUTPUTS/FBA_ANALYSIS/amazon_cache/`.
4. **Linking**: Associations are stored in `OUTPUTS/FBA_ANALYSIS/linking_maps/`.
5. **Financial Analysis**: `FBA_Financial_calculator` triggers automatically after a batch of new links to produce CSV reports in `OUTPUTS/FBA_ANALYSIS/financial_reports/`.

### 2.2 Hybrid Mode (Interleaved)
Configured via `hybrid_processing` in `system_config.json`. This mode alternates between supplier extraction and Amazon analysis within the same session, ensuring that financial data begins appearing shortly after the run starts rather than waiting for full supplier extraction.

### 2.3 Resumption and Atomic Persistence
- **Resumption**: The `FixedEnhancedStateManager` tracks `persistent_category_index` and `system_progression` to ensure that runs can be interrupted and resumed without loss of progress or duplicate work.
- **Atomic Saves**: All critical state and data writes use `utils/windows_save_guardian.py` (or `save_json_atomic`) to perform temp-then-replace writes, preventing file corruption during crashes or power failures.

---

## 3. Data Flow and Persistence

The system follows a strict file-grounded data flow. All paths are relative to the project root.

| Data Type | Persistence Path | Description |
|-----------|------------------|-------------|
| **Supplier Cache** | `OUTPUTS/cached_products/` | Raw product data scraped from supplier websites. |
| **Amazon Cache** | `OUTPUTS/FBA_ANALYSIS/amazon_cache/` | Detailed Amazon product info (Price, Rank, Fees). |
| **Linking Maps** | `OUTPUTS/FBA_ANALYSIS/linking_maps/` | EAN-to-ASIN resolution for financial mapping. |
| **Financial Reports** | `OUTPUTS/FBA_ANALYSIS/financial_reports/` | Final ROI/Profitability CSV and JSON files. |
| **Processing State** | `OUTPUTS/CACHE/processing_states/` | Authoritative JSON files for run resumption. |
| **Diagnostics** | `OUTPUTS/DIAGNOSTICS/` | Telemetry, sentinel logs, and validation reports. |

---

## 4. Configuration Precedence

The `SystemConfigLoader` resolves configuration using the following priority (highest to lowest):

1. **Explicit Override**: A path passed directly to the `SystemConfigLoader` constructor.
2. **Environment Variable**: `FBA_SYSTEM_CONFIG_PATH` (Commonly used by the Control Plane).
3. **Base Configuration**: `config/system_config.json` (The default source).

---

## 5. Operational Runbooks

### 5.1 Starting a Supplier Run
1. Start Chrome: `chrome --remote-debugging-port=9222 --user-data-dir=C:\ChromeDebugProfile`.
2. Run the supplier script: `python run_custom_poundwholesale.py`.

### 5.2 Launching the Dashboard
1. Run: `python dashboard/run_dashboard.py`.
2. Access the UI at `http://localhost:8501`.

### 5.3 Control Plane Worker
1. Start the worker: `python control_plane/worker.py`.
2. The worker will listen for jobs and execute them using the configured system environment.

---

## 6. Maintenance and Updates

### 6.1 Documentation Policy
All architectural changes must be reflected in:
- `AGENTS.md`: The authoritative guide for developers.
- `docs/COMPLETE_WORKFLOW_UPDATED_2026_Q1.md`: This high-level workflow reference.
- **Supermemory**: Granular memories added via the `supermemory` tool.

### 6.2 Verification Gate
Before committing changes or updating documentation:
1. Run tests: `pytest`.
2. Check diagnostics: `python utils/memory_sentinel.py --check`.
3. Verify file integrity in `OUTPUTS/CACHE/processing_states/`.
