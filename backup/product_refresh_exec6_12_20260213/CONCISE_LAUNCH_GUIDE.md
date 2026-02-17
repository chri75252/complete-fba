# FBA Agent System Launch Guide (CMD, Current)

Repo root:
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-`

This guide is optimized for:
- Windows **CMD** only (no PowerShell)
- Local LLM via **Ollama** using **qwen3:8b-q4_K_M**
- Streamlit dashboard chat UI + control plane worker

---

## 0) One-time prerequisites

### A) Start Chrome for automation (CDP port 9222)
You must launch a dedicated Chrome instance with remote debugging enabled.

**Recommended (matches current operator workflow):**
```bat
Chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
```

Notes:
- Install Keepa/SellerAmp into this Chrome profile once.
- Make sure you’re looking at the *debug Chrome window* launched with `--user-data-dir`, not your normal Chrome.

### B) Start Ollama (Local LLM)
This project expects an Ollama server at `http://localhost:11434`.

CMD:
```bat
ollama run qwen3:8b-q4_K_M
```
Keep this terminal running.

---

## 1) Start the system (3 terminals)

### Terminal 1: Dashboard (UI)
CMD:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
set "CONTROL_PLANE_LLM_PROVIDER=ollama"
set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_LLM_MODEL=qwen3:8b-q4_K_M"
set "CONTROL_PLANE_OLLAMA_BASE_URL=http://localhost:11434"
set "CONTROL_PLANE_OLLAMA_MODEL=qwen3:8b-q4_K_M"
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

### Terminal 3: Optional quick health checks
CMD:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
curl http://localhost:9222/json/version
curl http://localhost:11434/api/tags
```

---

## 2) How the chat system works (important)

- The chat planner will propose a tool call.
- For write tools, the UI shows **“Proposed action requires confirmation”**.
- Clicking **Confirm execute** only **queues a job**.
- The worker (`python -m control_plane worker`) must be running to execute queued jobs.

Artifacts:
- Pending jobs: `OUTPUTS\CONTROL_PLANE\jobs\pending\`
- Running jobs: `OUTPUTS\CONTROL_PLANE\jobs\running\`
- Done jobs: `OUTPUTS\CONTROL_PLANE\jobs\done\`
- Failed jobs: `OUTPUTS\CONTROL_PLANE\jobs\failed\`
- Status file: `OUTPUTS\CONTROL_PLANE\status\<run_id>.json`
- Log file: `OUTPUTS\CONTROL_PLANE\logs\<run_id>.log`

---

## 3) Main prompts (copy/paste into Chat)

### A) Analyze supplier categories (category run)
Paste category URLs (one per line) and ask for analysis:

Example:
```
Analyze these categories for angelwholesale.co.uk:
https://angelwholesale.co.uk/Category/A-To-Z-wholesale
https://angelwholesale.co.uk/Category/All-Baby-and-child
```

Expected behavior:
- Tool proposed: `enqueue_run`
- You confirm execute
- Worker runs the job

### B) Analyze a product list from a JSON input file (product-list refresh)

#### Where to place the input file
Put the JSON file here:
- `OUTPUTS\CONTROL_PLANE\inputs\`

Example file currently used in this repo:
- `OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_6.json`

#### Naming conventions
- No strict naming required.
- Recommended: `products_subset_<supplier>_<short_description>.json`
- Re-using the same `run_id` will overwrite job artifacts for that run; using a new `run_id` creates a new sandbox supplier.

#### Prompt example
```
Run product-list refresh for angelwholesale.co.uk using this products file:
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_6.json
Use a new run_id.
```

Expected behavior:
- Tool proposed: `enqueue_product_list_refresh`
- You confirm execute
- Worker runs the job

### C) Ask for status / logs
Provide the run_id:

```
Show me the status and latest log lines for run_id: <run_id>
```

---

## 4) Common recovery actions

### A) If jobs queue but never start: stale lock
The worker uses a global lock file:
- `OUTPUTS\CONTROL_PLANE\lock\active_run.lock`

If the worker was terminated mid-run, the lock can remain and block future jobs.

**Safe reset** (only if worker is NOT running):
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir OUTPUTS\CONTROL_PLANE\lock
rename "OUTPUTS\CONTROL_PLANE\lock\active_run.lock" "active_run.lock.bak_02-02-26_manual"
python -m control_plane worker
```

### B) Kill and restart the Chrome 9222 debug browser

If the browser looks "headless" (extensions not showing, Keepa/SellerAmp missing, pages not reflecting what the system is doing), the most common cause is attaching to the wrong Chrome instance/profile.

1) Kill **all** Chrome instances (safe if you have no important sessions open):
```bat
taskkill /F /IM chrome.exe /T
```

2) Start the dedicated debug Chrome again (your standard command):
```bat
Chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebugProfile"
```

3) Confirm CDP is reachable:
```bat
curl http://localhost:9222/json/version
```

4) In the debug Chrome window, confirm extensions exist:
- Open `chrome://extensions`
- Ensure Keepa/SellerAmp are installed + enabled in `C:\ChromeDebugProfile`

### C) Restart processes after code changes
After updating code, restart long-running processes so they pick up changes:
- Stop worker with `Ctrl+C`, then run: `python -m control_plane worker`
- Stop dashboard with `Ctrl+C`, then run: `python dashboard\run_dashboard.py`
- Ollama usually does NOT need restart unless it is erroring.

Note: if you updated dashboard files (`dashboard\*.py`) but didn’t restart Streamlit, the UI may continue running old code.
---

## 5) Verify success

### Product-list refresh succeeded when:
- Job moves: `pending/` → `running/` → `done/`
- `OUTPUTS\CONTROL_PLANE\status\<run_id>.json` shows completion
- `OUTPUTS\FBA_ANALYSIS\linking_maps\<sandbox_supplier>\linking_map.json` has `amazon_asin` populated for matched items
- `OUTPUTS\FBA_ANALYSIS\amazon_cache\amazon_<ASIN>_<EAN>.json` files exist and contain `keepa.product_details_tab_data`
- Financial report exists only when there were successful matches:
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\<sandbox_supplier>\*.csv`
