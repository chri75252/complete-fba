# WORKFLOW SURFACES QUICK REFERENCE

The Amazon FBA Agent System operates across three primary surfaces. This guide provides a one-page-per-surface reference for developers and operators.

---

## 1. Classic Surface (CLI)

**When to Use**
* Direct, high-performance execution of extraction and analysis for specific suppliers.
* Local debugging and initial supplier setup.
* When maximum processing speed is required without the overhead of a job manager.

**Entry Point**
* `run_custom_{supplier}.py` (e.g., `run_custom_poundwholesale.py`)
* Alternative: `run_complete_fba_system.py` (Legacy)

**Core Orchestrator**
* `tools/passive_extraction_workflow_latest.py` (Class: `PassiveExtractionWorkflow`)

**Dependencies**
* **Chrome Instance**: Must be running with `--remote-debugging-port=9222`.
* **System Config**: `config/system_config.json`.
* **Supplier Config**: `config/supplier_configs/{supplier}.json`.
* **State Management**: `utils/fixed_enhanced_state_manager.py`.

**Dependencies Checklist**
- [ ] Chrome started with `--remote-debugging-port=9222` and profile data directory.
- [ ] Supplier-specific runner script exists in the root directory.
- [ ] Supplier configuration JSON exists in `config/supplier_configs/`.
- [ ] Python environment satisfies `requirements.txt`.
- [ ] `OUTPUTS/` directory is writable.

---

## 2. Dashboard Surface (Visual)

**When to Use**
* Real-time monitoring of processing state and system progression.
* Visualization of financial reports (ROI, Net Profit, etc.).
* Inspecting debug and health logs through a graphical interface.
* Comparing multiple supplier results side-by-side.

**Entry Point**
* `dashboard/run_dashboard.py` (launches `dashboard/app_fixed.py`)
* Command: `python dashboard/run_dashboard.py`

**Technology Stack**
* **Streamlit**: Web framework for the UI.
* **Pandas**: Data manipulation for report visualization.

**Dependencies**
* **Output Data**: Reads directly from `OUTPUTS/CACHE/processing_states/`.
* **Financial Reports**: Reads CSVs from `OUTPUTS/FBA_ANALYSIS/financial_reports/`.
* **Logs**: Accesses `logs/debug/` for live log streaming.

**Dependencies Checklist**
- [ ] Streamlit installed (`pip install streamlit`).
- [ ] Pandas installed (`pip install pandas`).
- [ ] `OUTPUTS/` directory populated with at least one processing state or financial report.
- [ ] Port 8501 (default) is available for the Streamlit server.

---

## 3. Control Plane Surface (Autonomous)

**When to Use**
* Managed background execution and job queuing.
* Remote control capabilities via job manifests.
* Autonomous operation with RAG-enabled querying about system status.
* Running jobs with dynamic configuration overrides.

**Entry Point**
* `control_plane/worker.py`
* Command: `python -m control_plane worker`

**Core Components**
* **Job Manager**: `control_plane/job_manager.py`.
* **RAG System**: `control_plane/rag_index.py` and `control_plane/rag_retrieval.py`.
* **Operator UI**: `dashboard/pages/01_Operator_Control_Plane.py`.

**Dependencies**
* **Job Directory**: `OUTPUTS/CONTROL_PLANE/jobs/` (subdirs: `pending`, `running`, `done`, `failed`).
* **Environment Variable**: `FBA_SYSTEM_CONFIG_PATH` for sandboxed execution.
* **Chrome Instance**: Same requirement as Classic Surface (CDP port 9222).
* **RAG Index**: Built via `python -m control_plane build-index`.

**Dependencies Checklist**
- [ ] `control_plane/` logic files exist and are verified.
- [ ] Worker process is running and polling for jobs.
- [ ] `OUTPUTS/CONTROL_PLANE/` structure initialized.
- [ ] SQLite/Vector database for RAG is initialized (if using chat features).
- [ ] `active_run.lock` is not orphaned from a previous crash.
