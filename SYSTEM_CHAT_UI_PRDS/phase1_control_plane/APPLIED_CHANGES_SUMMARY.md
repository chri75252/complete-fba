# Phase 1 Applied Changes Summary

Date: 2026-01-25

This file summarizes the actual changes applied during Phase 1.
A full patch is saved at:
- `SYSTEM_CHAT_UI_PRDS/diffs/phase1_applied.patch`

## Backups
Mandatory backup folder created and verified:
- `backup/control_plane_phase1_20260125/`
  - `backup/control_plane_phase1_20260125/system_config_loader.py`
  - `backup/control_plane_phase1_20260125/passive_extraction_workflow_latest.py`
  - `backup/control_plane_phase1_20260125/app_fixed.py`

Additional project-local backups:
- `SYSTEM_CHAT_UI_PRDS/backups/phase1_impl_20260125/`

## Modified Existing Files
### 1) Config env override
- `config/system_config_loader.py`
  - Added env var support: `FBA_SYSTEM_CONFIG_PATH`
  - Behavior unchanged unless env var set

### 2) Categories loader respects workflow_config
- `tools/passive_extraction_workflow_latest.py`
  - `_get_predefined_categories` now prefers `self.workflow_config["categories_config_path"]` when present
  - Falls back to prior convention (`config/<base>_categories.json`) if not present

### 3) Dashboard integration: Operator tab
- `dashboard/app_fixed.py`
  - Added `st.tabs(["Dashboard", "Operator"])`
  - Operator tab renders `dashboard/operator_control_plane.py` via `render_operator_panel`
  - Dashboard tab keeps existing behavior

## New Files (Additive)
### Control plane package
- `control_plane/` (new)
  - `control_plane/worker.py` (job executor)
  - `control_plane/job_manager.py` (job + overrides writer)
  - `control_plane/status_reader.py` (read-only status/log queries)
  - `control_plane/financial_query.py` (filter latest financial report)
  - `control_plane/config_merger.py` (deep merge)
  - `control_plane/llm_provider.py` (provider abstraction: openai/anthropic/ollama/lmstudio/none)
  - `control_plane/llm_parser.py` (Phase 1 parser: parameter extraction only)
  - `control_plane/internal/path_resolver.py` and `control_plane/internal/file_io.py`

### Operator UI
- `dashboard/operator_control_plane.py`
  - Operator panel: create job, monitor run, query financials
  - Optional LLM parsing: fills form only; requires confirm checkbox before writes

## Known Limitations (to resolve later)
- `dashboard/operator_control_plane.py` runner_script mapping currently defaults to `run_custom_<base>.py` (base from supplier_domain). Some suppliers use hyphenated runner names; Phase 2 can improve mapping.
- LSP diagnostics not available in this environment (`basedpyright` missing). Verification uses `py_compile` and runtime smoke checks.
