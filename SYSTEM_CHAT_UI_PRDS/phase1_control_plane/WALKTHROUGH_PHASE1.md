# Phase 1 Walkthrough (Operator UI + Control Plane)

## 1) Start the dashboard
From repo root:
- `python dashboard/run_dashboard.py`

Then open the Streamlit UI. You should see two tabs:
- `Dashboard`
- `Operator`

## 2) (Optional) Start the worker
In a separate terminal from repo root:
- `python -m control_plane.worker`

This will watch:
- `OUTPUTS/CONTROL_PLANE/jobs/pending/`

## 3) Create a workflow job (no LLM)
In the `Operator` tab:
1. Select a workflow (e.g. `poundwholesale_workflow (poundwholesale.co.uk)`)
2. Select categories (or paste URLs)
3. Set limits
4. Tick confirmation checkbox
5. Click `Create Job`

Expected artifacts:
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json`
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`
- `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`

If worker is running, the job will move to:
- `OUTPUTS/CONTROL_PLANE/jobs/running/`

## 4) Monitor the run
In the `Operator` tab:
- Select run_id
- The status JSON is shown
- Last 50 log lines are shown

Status file:
- `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`

Log file:
- `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`

## 5) Financial query
In `Operator` tab:
- Set ROI min, NetProfit min, optional EAN
- Click `Run Financial Query`

It filters the latest CSV under:
- `OUTPUTS/FBA_ANALYSIS/financial_reports/<supplier>/`

## 6) Optional LLM parser (fills form only)
Set env vars (examples):

### OpenAI
- `set CONTROL_PLANE_LLM_PROVIDER=openai`
- `set OPENAI_API_KEY=...`

### Anthropic
- `set CONTROL_PLANE_LLM_PROVIDER=anthropic`
- `set ANTHROPIC_API_KEY=...`

### Ollama
- `set CONTROL_PLANE_LLM_PROVIDER=ollama`
- `set LOCAL_LLM_MODEL=llama3`

### LM Studio
- `set CONTROL_PLANE_LLM_PROVIDER=lmstudio`
- `set CONTROL_PLANE_LLM_BASE_URL=http://localhost:1234`

Then in Operator tab:
1. Type request into the text area
2. Click `Parse`
3. The form fields auto-fill
4. You still must tick confirm + click `Create Job`
