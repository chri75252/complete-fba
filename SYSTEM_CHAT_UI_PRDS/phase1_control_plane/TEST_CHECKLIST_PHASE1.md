# Phase 1 Test Checklist

## 1) Worker boots
- Run: `python -m control_plane worker`
- Expect: creates directories under `OUTPUTS/CONTROL_PLANE/`

## 2) Operator UI loads
- Run: `python dashboard/run_dashboard.py`
- Open Streamlit
- Expect: Page `Operator Control Plane (Phase 1)` is visible

## 3) Create a job
- Choose a supplier + paste 1-2 category URLs
- Set max products small (e.g., 5)
- Tick confirmation
- Click Create Job
- Expect files:
  - `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`

## 4) Job executes
- Worker should move job into running then done/failed
- Expect status:
  - `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` updated periodically

## 5) LLM parser optional
- Set `CONTROL_PLANE_LLM_PROVIDER` env vars
- In Operator UI: type request, click Parse
- Expect: parsed fields populate defaults
- Verify: parser does not run anything until you confirm + Create Job

## 6) Core hooks
- Validate existing runs still work with env var unset
- Validate run uses merged config when env var set
