# WORKFLOW SURFACES

This guide provides a quick reference for the three primary operating surfaces of the Amazon FBA Agent System.

---

## 1. Classic Surface (CLI)

**When to Use:**
- Primary production entry point for per-supplier extraction and analysis.
- Direct, high-performance execution of the extraction workflow for specific suppliers.
- Local debugging, initial supplier onboarding verification, and manual system tests.

**Entry Point:**
- `run_custom_*.py` (e.g., `run_custom_poundwholesale.py`)

**Dependencies:**
- **Chrome Instance:** Must be running with `--remote-debugging-port=9222`.
- **System Config:** `config/system_config.json`.
- **Supplier Config:** `config/supplier_configs/{supplier}.json`.
- **State Management:** `utils/fixed_enhanced_state_manager.py`.
- **Workflow Engine:** `tools/passive_extraction_workflow_latest.py`.

**Dependencies Checklist:**
- [ ] Chrome running with CDP port 9222 and a dedicated profile directory.
- [ ] Supplier configuration file present in `config/supplier_configs/`.
- [ ] Runner script (`run_custom_*.py`) exists in the project root.
- [ ] Python environment satisfies all `requirements.txt` dependencies.
- [ ] `OUTPUTS/` directory exists and is writable.

---

## 2. Dashboard Surface (Visual)

**When to Use:**
- Real-time visual monitoring of system progression, processing state, and category counts.
- Visualization of financial reports (ROI, Net Profit, Profit Margins) across multiple suppliers.
- Streaming logs and inspecting system health metrics via a centralized graphical interface.

**Entry Point:**
- `dashboard/run_dashboard.py` (Main launcher)
- Command: `python dashboard/run_dashboard.py` (executes `streamlit run dashboard/app_fixed.py`)

**Dependencies:**
- **Streamlit & Pandas:** Required Python libraries for UI rendering and data manipulation.
- **Processing States:** Reads from `OUTPUTS/CACHE/processing_states/`.
- **Financial Reports:** Reads CSV data from `OUTPUTS/FBA_ANALYSIS/financial_reports/`.
- **Logs:** Accesses `logs/debug/` for live log streaming and historical review.

**Dependencies Checklist:**
- [ ] `streamlit` and `pandas` installed (`pip install streamlit pandas`).
- [ ] Network port 8501 available for the Streamlit web server.
- [ ] `OUTPUTS/` directory populated with valid state files or financial reports.
- [ ] Browser access to `http://localhost:8501`.

---

## 3. Control Plane Surface (Autonomous)

**When to Use:**
- Centralized job orchestration and autonomous background execution of complex tasks.
- Managing long-running jobs (e.g., product list refreshes, main workflow runs) via a queued system.
- RAG-enabled querying and autonomous decision-making using the chat-based interface.

**Entry Point:**
- `python -m control_plane worker` (Executes the primary job polling loop)
- `python -m control_plane build-index` (Initializes/refreshes the RAG knowledge index)

**Dependencies:**
- **Job Manager:** `control_plane/job_manager.py` (Handles job creation and queuing).
- **Control Plane Root:** Directory structure under `OUTPUTS/CONTROL_PLANE/`.
- **RAG Components:** `control_plane/rag_index.py` and `control_plane/rag_retrieval.py`.
- **Chrome Instance:** Required for jobs involving browser automation (e.g., product refresh).

**Dependencies Checklist:**
- [ ] `OUTPUTS/CONTROL_PLANE/` directory structure initialized (jobs/pending, jobs/running, etc.).
- [ ] RAG index built via `python -m control_plane build-index`.
- [ ] Worker process started and actively polling for new job manifests.
- [ ] Chrome instance accessible via port 9222 for automated browser tasks.
