# Phase 1 Test Plan (Control Plane + Operator UI)

## Objective
Verify Phase 1 delivers a safe control plane that can:
- create jobs and overrides
- execute jobs via worker
- track status via status JSON
- query outputs (financials/logs/state)
- integrate Operator UI without breaking existing dashboard

## Prerequisites
- Run from repo root: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`
- At least one supplier has existing OUTPUTS so queries can be demonstrated.

## Test Cases
### 1) Import + Syntax
- Input: `python -m py_compile` for new/modified files
- Expected: exit code 0

### 2) Core hook: config env override
- Input: set `FBA_SYSTEM_CONFIG_PATH` to a valid JSON copy
- Expected: `SystemConfigLoader()` loads that file (verify by printing a known field)

### 3) Core hook: categories_config_path honored
- Input: set a workflow config to point at a small categories subset JSON
- Expected: workflow loads subset categories (verify via log line count / category count)

### 4) Job creation (no worker)
- Input: create run via JobManager
- Expected:
  - job JSON exists in `OUTPUTS/CONTROL_PLANE/jobs/pending/`
  - overrides exist in `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/`

### 5) Worker execution lifecycle
- Input: start worker, enqueue a job
- Expected:
  - job moves pending → running → done/failed
  - status file exists and updates
  - per-run log file exists

### 6) Read-only queries
- Input: run financial query tool with ROI/netprofit filters
- Expected: returns structured result; when no report exists, returns clear message

### 7) Operator UI smoke
- Input: launch dashboard and view Operator tab
- Expected:
  - dashboard still renders existing panels
  - operator tab renders, can list suppliers and status files

## Success Criteria
All tests pass. No regressions in existing dashboard startup.
