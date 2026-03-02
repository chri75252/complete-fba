# FBA Agent System - Launch Guide (Detailed)

This file intentionally contains the "long form" operator material that was removed from:
`docs/CONCISE_LAUNCH_GUIDE.md`

What this file includes:
- Canonical job JSON schemas for `run_workflow` and `run_product_list_refresh`
- Canonical status JSON schema (including refresh-specific fields)
- Verification commands (pre-run, mid-run, post-run)
- Cancellation test procedure
- Troubleshooting for stuck locks / wrong Chrome profile / LLM provider misconfig

All examples are grounded in current code paths in this repo:
- Job schemas: `control_plane/tools/jobs.py`, `control_plane/tools/product_list_refresh.py`
- Status schema + lock behavior: `control_plane/worker.py`, `control_plane/internal/path_resolver.py`
- Expected outputs preview: `control_plane/chat_orchestrator.py`
- LLM provider env: `control_plane/env_config.py`, `control_plane/llm_provider.py`, `control_plane/llm/providers.py`

---

## 1) Canonical paths and artifacts

Control plane dirs (created automatically):
- `OUTPUTS\CONTROL_PLANE\jobs\pending\`
- `OUTPUTS\CONTROL_PLANE\jobs\running\`
- `OUTPUTS\CONTROL_PLANE\jobs\done\`
- `OUTPUTS\CONTROL_PLANE\jobs\failed\`
- `OUTPUTS\CONTROL_PLANE\status\`
- `OUTPUTS\CONTROL_PLANE\logs\`
- `OUTPUTS\CONTROL_PLANE\overrides\`
- `OUTPUTS\CONTROL_PLANE\lock\`

Global worker lock file:
- `OUTPUTS\CONTROL_PLANE\lock\active_run.lock`

Cancel flags checked by worker:
- `OUTPUTS\CONTROL_PLANE\status\<run_id>.cancelled`
- `OUTPUTS\CONTROL_PLANE\lock\cancel_<run_id>.flag`

---

## 2) Job JSON schemas (canonical)

### A) Workflow run job (`job_type: run_workflow`)

Source of truth: `control_plane/tools/jobs.py:80-100`

Shape:
```json
{
  "schema_version": "1.0",
  "run_id": "<run_id>",
  "created_at": "<utc_iso>",
  "job_type": "run_workflow",
  "supplier_domain": "poundwholesale.co.uk",
  "sandbox_supplier": "<sandbox_supplier>",
  "workflow_key": "<workflow_key>",
  "runner_script": "run_custom_poundwholesale.py",
  "override": {
    "system_config_path": "OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json",
    "categories_path": "OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json"
  },
  "runtime": {
    "max_products": 50,
    "max_products_per_category": 50
  },
  "notes": "<optional>"
}
```

Notes:
- `sandbox_supplier` is the supplier identity the worker uses for progress polling and file resolution.
- Use `job.sandbox_supplier` (not `job.supplier_domain`) when you want the exact sandbox output paths.

### B) Product-list refresh job (`job_type: run_product_list_refresh`)

Source of truth: `control_plane/tools/product_list_refresh.py:114-127`

Shape:
```json
{
  "schema_version": "1.0",
  "run_id": "<run_id>",
  "created_at": null,
  "job_type": "run_product_list_refresh",
  "supplier_domain": "angelwholesale.co.uk__sandbox__<run_id_first8>",
  "source_supplier_domain": "angelwholesale.co.uk",
  "refresh": {
    "products_path": "OUTPUTS/PRODUCTS_LISTS/products_subset_angelwholesale_mixed_6.json",
    "notes": "<optional>",
    "dry_run": false
  }
}
```

Allowed `products_path` roots (enforced in `control_plane/tools/product_list_refresh.py:88-101`):
- `OUTPUTS\PRODUCTS_LISTS\...`
- `OUTPUTS\CONTROL_PLANE\inputs\...`
- Run override file: `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\products_subset.json`

---

## 3) Status JSON schema (canonical)

Source of truth: `control_plane/worker.py:_status_template`

Always present:
```json
{
  "schema_version": "1.0",
  "run_id": "<run_id>",
  "state": "queued|running|done|failed|cancelled",
  "supplier_domain": "<job.supplier_domain>",
  "started_at": "<utc_iso_or_null>",
  "ended_at": "<utc_iso_or_null>",
  "pid": 12345,
  "resolved_paths": {
    "processing_state": "<path-or-null>",
    "linking_map": "<path-or-null>",
    "financial_dir": "<path-or-null>",
    "logs_dir": "<path-or-null>",
    "runner_log": "OUTPUTS/CONTROL_PLANE/logs/<run_id>.log"
  },
  "progress": {"...": "..."},
  "artifacts": {"...": "..."},
  "error": {"summary": "", "last_log_lines": []}
}
```

For product-list refresh jobs, the worker also populates:
- `status["refresh"]["paths"]`
- `status["refresh"]["counts"]`
- `status["refresh"]["source_supplier_domain"]`

Source of truth: `control_plane/worker.py:399-450` and final recompute `control_plane/worker.py:474-483`.

---

## 4) Verification checklist (copy/paste)

### A) Pre-run health

Chrome CDP reachable:
```bat
curl http://localhost:9222/json/version
```

Ollama reachable (if using Ollama):
```bat
curl http://localhost:11434/api/tags
```

Dashboard reachable:
```bat
curl http://localhost:8501
```

Worker running:
```bat
tasklist | findstr /i python
```

### B) Confirm a job was queued

```bat
dir OUTPUTS\CONTROL_PLANE\jobs\pending /b
type OUTPUTS\CONTROL_PLANE\jobs\pending\job_<run_id>.json
```

### C) Confirm status + logs

```bat
type OUTPUTS\CONTROL_PLANE\status\<run_id>.json
type OUTPUTS\CONTROL_PLANE\logs\<run_id>.log
```

### D) Product-list refresh artifacts

Linking map:
```bat
dir OUTPUTS\FBA_ANALYSIS\linking_maps /s /b | findstr /i linking_map.json
```

Amazon cache (run-scoped for refresh runs):
```bat
dir OUTPUTS\CONTROL_PLANE\overrides\<run_id>\amazon_cache /b
```

Processing state (sandbox):
```bat
dir OUTPUTS\CACHE\processing_states\*sandbox*processing_state.json /b
```

### E) Cancellation test

Create one of these flags while job is running:
```bat
echo.> OUTPUTS\CONTROL_PLANE\status\<run_id>.cancelled
REM OR
echo.> OUTPUTS\CONTROL_PLANE\lock\cancel_<run_id>.flag
```

Expected:
- status JSON ends with `state: "cancelled"`
- job JSON moved to `OUTPUTS\CONTROL_PLANE\jobs\failed\`

---

## 5) Troubleshooting

### A) Worker stuck (stale global lock)

Lock file:
- `OUTPUTS\CONTROL_PLANE\lock\active_run.lock`

Safe reset (ONLY if worker is NOT running):
```bat
type OUTPUTS\CONTROL_PLANE\lock\active_run.lock
rename OUTPUTS\CONTROL_PLANE\lock\active_run.lock active_run.lock.bak_manual
python -m control_plane worker
```

### B) Wrong Chrome window/profile

If Keepa/SellerAmp are missing, you are usually looking at the wrong Chrome profile.

```bat
taskkill /F /IM chrome.exe /T
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
curl http://localhost:9222/json/version
```

### C) LLM provider errors

Common runtime errors are thrown if required keys are missing:
- `OPENCODE_API_KEY not set` (provider `opencode`)
- `OPENAI_API_KEY not set` (provider `openai`)

Confirm what provider you started the dashboard with:
- Check the dashboard UI panel that shows `CONTROL_PLANE_LLM_PROVIDER`.
