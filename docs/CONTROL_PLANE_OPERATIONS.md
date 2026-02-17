# Control Plane Operations Guide

This document describes the architecture, job lifecycle, and management of the Amazon FBA Agent System's Control Plane.

## Architecture Overview

The Control Plane provides a deterministic orchestration layer for running FBA workflows, managing jobs, and providing RAG-enabled querying capabilities.

### Core Components

- **`control_plane/worker.py`**: The central execution engine. It runs a continuous polling loop that monitors for new jobs, manages process lifecycle, and updates job status in real-time.
- **`control_plane/job_manager.py`**: Handles the creation and preparation of jobs. It manages configuration merging, category subsetting, and atomic writing of job manifests.
- **`control_plane/paths.py`**: Defines the standardized directory structure for the control plane under `OUTPUTS/CONTROL_PLANE/`.
- **`control_plane/job_types.py`**: Defines supported operation types including `run_workflow`, `run_product_list_refresh`, and `run_onboarding_wizard`.
- **`control_plane/chat_orchestrator.py`**: (Planner layer) Drives the control plane based on high-level user intents.

## Job Lifecycle

Jobs transition through the following states in `OUTPUTS/CONTROL_PLANE/jobs/`:

1.  **Pending (`pending/`)**: New job manifests created by the `JobManager`.
2.  **Running (`running/`)**: Jobs currently being executed by a `ControlPlaneWorker`. A lock file (`active_run.lock`) ensures only one job runs at a time.
3.  **Done (`done/`)**: Successfully completed jobs.
4.  **Failed (`failed/`)**: Jobs that exited with a non-zero code or encountered a startup error.

### Status and Logs
- **Status JSON**: Located in `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`. Contains start/end times, PID, progress snapshots, and error summaries.
- **Execution Logs**: Located in `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`. Captures stdout and stderr from the runner process.

## RAG & Indexing

The Control Plane uses a Retrieval-Augmented Generation (RAG) system to provide context-aware answers about the repository and execution history.

### Build Index Command
To refresh the system knowledge base, run:
```bash
python -m control_plane build-index
```

### RAG Components
- **`control_plane/rag_index.py`**: Extracts knowledge from:
    - **System Touch Reports**: File access and modification patterns.
    - **Execution Traces**: Historical performance and input/output samples.
    - **Repository Wiki**: Documentation from `.qoder/repowiki/`.
- **`control_plane/rag_retrieval.py`**: Handles semantic searching across the generated index.

## Sandbox Isolation

Sandbox isolation is critical for safe, reproducible execution of supplier workflows.

- **Config Isolation**: Every job can specify an `override` configuration. The `JobManager` merges these into a temporary `system_config.merged.json` located in `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/`.
- **Category Isolation**: Category subsets are written to a temporary JSON file to ensure the runner only processes requested URLs.
- **Environment Control**: The worker uses the `FBA_SYSTEM_CONFIG_PATH` environment variable to force the core system to use the isolated sandbox configuration.

## Troubleshooting Matrix

| Issue | Symptom | Likely Cause | Resolution |
| :--- | :--- | :--- | :--- |
| **Worker Stalled** | Job stays in `pending` | Worker process not running | Run `python -m control_plane worker` |
| **Lock Contention** | Job fails to start | Orphaned `active_run.lock` | Check for active processes; delete lock file manually if safe |
| **Script Missing** | Status: `Runner script missing` | Incorrect path in job manifest | Verify `runner_script` path relative to repo root |
| **Timeout** | Job moved to `failed` | Process exceeded `timeout_seconds` | Increase timeout in job creation or check for browser hangs |
| **JSON Error** | Job moved to `failed` | Corrupt job or state file | Check `OUTPUTS/CONTROL_PLANE/logs/` for IO errors |

## Management Commands

- **Start Worker**: `python -m control_plane worker`
- **Build RAG Index**: `python -m control_plane build-index`
- **Check Status**: Inspect files in `OUTPUTS/CONTROL_PLANE/status/`
