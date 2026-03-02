# FBA Agent System - Concise Launch Guide (Windows)

Repo root (this machine):
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

This guide is intentionally short. For deep verification + schemas + detailed troubleshooting, see:
`docs/LAUNCH_GUIDE_DETAILED.md`

---

## 1) Start Chrome (CDP) for automation

CMD:
```bat
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
```

Verify CDP is reachable:
```bat
curl http://localhost:9222/json/version
```

If Chrome is not reflecting what the system is doing (wrong profile / extensions missing):
```bat
taskkill /F /IM chrome.exe /T
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
curl http://localhost:9222/json/version
```

---

## 2) Pick an LLM provider for the Chat Planner

The dashboard chat uses environment variables to select a provider.

Provider key (required):
- `CONTROL_PLANE_LLM_PROVIDER` = `opencode` | `ollama` | `lmstudio` | `openai` | `anthropic` | `none`

Notes:
- `.env` is auto-loaded by `control_plane/env_config.py:ensure_llm_env()` if present.
- Do not paste real API keys into docs. Use environment variables or `.env`.

### Option A (Recommended): OpenCode (API key)

CMD:
```bat
set "CONTROL_PLANE_LLM_PROVIDER=opencode"
set "CONTROL_PLANE_LLM_BASE_URL=https://opencode.ai/zen"
set "OPENCODE_MODEL=minimax-m2.5-free"
set "OPENCODE_API_KEY=<YOUR_OPENCODE_API_KEY>"
```

### Option B: Local Ollama

Start Ollama in a separate terminal:
```bat
ollama run qwen3:8b-q4_K_M
```

Dashboard env:
```bat
set "CONTROL_PLANE_LLM_PROVIDER=ollama"
set "CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_OLLAMA_MODEL=qwen3:8b-q4_K_M"
```

### Option C: LM Studio (OpenAI-compatible local server)

Dashboard env:
```bat
set "CONTROL_PLANE_LLM_PROVIDER=lmstudio"
set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:1234"
set "CONTROL_PLANE_LLM_MODEL=<YOUR_LMSTUDIO_MODEL_ID>"
```

Switching providers: stop the dashboard (`Ctrl+C`) and restart it with different env vars.

---

## 3) Start the system (2 terminals)

### Terminal 1: Dashboard (UI)

CMD:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python dashboard\run_dashboard.py
```

Open:
- `http://localhost:8501`

### Terminal 2: Worker (executes queued jobs)

CMD:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

---

## 4) How chat execution works

- The chat planner proposes a tool call.
- For write tools, the UI shows a confirmation step.
- Confirming queues a job JSON under `OUTPUTS\CONTROL_PLANE\jobs\pending\`.
- The worker must be running to execute jobs.

Core artifacts (always):
- Pending jobs: `OUTPUTS\CONTROL_PLANE\jobs\pending\`
- Running jobs: `OUTPUTS\CONTROL_PLANE\jobs\running\`
- Done jobs: `OUTPUTS\CONTROL_PLANE\jobs\done\`
- Failed jobs: `OUTPUTS\CONTROL_PLANE\jobs\failed\`
- Status JSON: `OUTPUTS\CONTROL_PLANE\status\<run_id>.json`
- Run log: `OUTPUTS\CONTROL_PLANE\logs\<run_id>.log`

---

## 5) Common prompts (copy/paste)

### A) Run a category workflow (`enqueue_run`)
Example:
```
Run analysis for angelwholesale.co.uk on these categories with max_products=50:
https://angelwholesale.co.uk/Category/A-To-Z-wholesale
https://angelwholesale.co.uk/Category/All-Baby-and-child
```

Expected outputs preview (UI will show paths):
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`
- `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json`

### B) Run product-list refresh from a JSON file (`enqueue_product_list_refresh`)

Allowed `products_path` roots (enforced in `control_plane/tools/product_list_refresh.py`):
- `OUTPUTS\PRODUCTS_LISTS\` (recommended)
- `OUTPUTS\CONTROL_PLANE\inputs\` (ad-hoc)
- Run override file: `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\products_subset.json`

Example:
```
Run product-list refresh for angelwholesale.co.uk using:
OUTPUTS\PRODUCTS_LISTS\products_subset_angelwholesale_mixed_6.json
Use a new run_id.
```

### C) Cancel a run
If you know the run_id:
```
Cancel run_id: <run_id>
```

---

## 6) Expected outputs (high level)

For `enqueue_run` (workflow runs), the UI's "expected outputs" preview (see `control_plane/chat_orchestrator.py`) may include:
- `OUTPUTS\CONTROL_PLANE\jobs\pending\job_<run_id>.json`
- `OUTPUTS\CONTROL_PLANE\status\<run_id>.json`
- `OUTPUTS\CONTROL_PLANE\logs\<run_id>.log`
- `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\system_config.merged.json`
- `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\categories_subset.json`
- `OUTPUTS\CACHE\processing_states\<sandbox_supplier>_processing_state.json`
- `OUTPUTS\FBA_ANALYSIS\linking_maps\<sandbox_supplier>\linking_map.json`
- `OUTPUTS\cached_products\<sandbox_supplier>_products_cache.json`
- `OUTPUTS\FBA_ANALYSIS\financial_reports\<sandbox_supplier>\fba_financial_report_*.csv`

Note: Not every artifact is guaranteed for every run. Treat the job JSON + status JSON + log as the authoritative minimum.

For `enqueue_product_list_refresh` (product-list refresh runs), the refresh runner produces:
- Linking map: `OUTPUTS\FBA_ANALYSIS\linking_maps\<sandbox_supplier>\linking_map.json`
- Run-scoped Amazon cache: `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\amazon_cache\amazon_<ASIN>_<identifier>.json`
- Processing state (sandbox): `OUTPUTS\CACHE\processing_states\<sandbox_supplier>_processing_state.json`
- Status JSON includes `refresh.paths` and `refresh.counts`.

---

## 7) Fast troubleshooting

### A) Jobs queue but never start
1) Confirm worker is running.
2) Check lock file:
- `OUTPUTS\CONTROL_PLANE\lock\active_run.lock`

Safe reset (ONLY if worker is NOT running):
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir OUTPUTS\CONTROL_PLANE\lock
rename "OUTPUTS\CONTROL_PLANE\lock\active_run.lock" "active_run.lock.bak_manual"
python -m control_plane worker
```

### B) Status file exists but progress looks wrong
Check the log:
```bat
type OUTPUTS\CONTROL_PLANE\logs\<run_id>.log
```

### C) Cancel flags not clearing
The worker checks either of these:
- `OUTPUTS\CONTROL_PLANE\status\<run_id>.cancelled`
- `OUTPUTS\CONTROL_PLANE\lock\cancel_<run_id>.flag`

If the run is already over, you can delete them.

---

## 8) Detailed guide

Open:
- `docs/LAUNCH_GUIDE_DETAILED.md`

It contains:
- Exact job JSON schemas (`run_workflow`, `run_product_list_refresh`)
- Exact status JSON schema (including `status["refresh"]`)
- Verification + cancellation test procedure
- Deeper troubleshooting (lock file, Chrome profile, provider errors)
