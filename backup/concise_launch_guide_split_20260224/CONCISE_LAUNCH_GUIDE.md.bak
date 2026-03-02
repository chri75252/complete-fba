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
Product list input files must be placed in one of these locations:
- `OUTPUTS\PRODUCTS_LISTS\` (recommended for reusable product lists)
- `OUTPUTS\CONTROL_PLANE\inputs\` (allowed for ad-hoc/manual inputs)
- `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\` (run-specific product lists)

Example file currently used in this repo:
- `OUTPUTS\PRODUCTS_LISTS\products_subset_angelwholesale_mixed_6.json`

#### Naming conventions
- No strict naming required.
- Recommended: `products_subset_<supplier>_<short_description>.json`
- Re-using the same `run_id` will overwrite job artifacts for that run; using a new `run_id` creates a new sandbox supplier.

#### Accepted products_path formats
When specifying the products file in prompts, you can use:
- Full absolute path: `C:\...\OUTPUTS\PRODUCTS_LISTS\products_subset_angelwholesale_mixed_6.json`
- Relative path from repo root: `OUTPUTS\PRODUCTS_LISTS\products_subset_angelwholesale_mixed_6.json`
- Just the filename if in OUTPUTS\PRODUCTS_LISTS\: `products_subset_angelwholesale_mixed_6.json`

Also allowed:
- Relative path under CONTROL_PLANE inputs: `OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale.json`

#### Prompt example
```
Run product-list refresh for angelwholesale.co.uk using this products file:
OUTPUTS\PRODUCTS_LISTS\products_subset_angelwholesale_mixed_6.json
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
- Linking map exists with matched ASINs:
  - `OUTPUTS\FBA_ANALYSIS\linking_maps\<sandbox_supplier>\linking_map.json` has `amazon_asin` populated for matched items
- Amazon cache files exist in run-specific location:
  - `OUTPUTS\CONTROL_PLANE\overrides\<run_id>\amazon_cache\amazon_<ASIN>_<identifier>.json` files exist and contain `keepa.product_details_tab_data`
- Sandbox processing state exists:
  - `OUTPUTS\CACHE\processing_states\<sandbox_supplier>_processing_state.json`
- Financial report exists only when there were successful matches:
  - `OUTPUTS\FBA_ANALYSIS\financial_reports\<sandbox_supplier>\*.csv`

---

## 6) Using OpenCode MiniMax M2.5 (Optional - Higher Quality)

Instead of local Ollama, you can use OpenCode's MiniMax M2.5 model via API for better quality responses.

### Configuration (already set in .env)
The following is pre-configured in your `.env` file:
```bat
CONTROL_PLANE_LLM_PROVIDER=opencode
CONTROL_PLANE_LLM_BASE_URL=https://opencode.ai/zen
OPENCODE_MODEL=minimax-m2.5-free
OPENCODE_API_KEY=sk-GMbiEsviZXDUx75qccYZNDmQLypRGq4bOwughDWWu...
```

### Terminal 1: Dashboard with OpenCode (replaces Terminal 1 above)
CMD:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
set "CONTROL_PLANE_LLM_PROVIDER=opencode"
python dashboard\run_dashboard.py
```

### What you gain:
- **Much better code quality** (80.2% SWE-Bench Verified - can write production code)
- **1M token context** - can see more of your codebase at once
- **Agentic coding** - better at complex multi-file orchestration
- **No GPU needed** - runs via OpenCode API

### What you lose:
- Requires internet connection
- API usage costs (see OpenCode pricing)
- Slight latency vs local Ollama

### To switch back to local Ollama:
Simply change the env var in Terminal 1:
```bat
set "CONTROL_PLANE_LLM_PROVIDER=ollama"
python dashboard\run_dashboard.py
```

Or use LM Studio locally:
```bat
set "CONTROL_PLANE_LLM_PROVIDER=lmstudio"
set "CONTROL_PLANE_LLM_BASE_URL=http://localhost:1234"
set "CONTROL_PLANE_LLM_MODEL=your-local-model"
python dashboard\run_dashboard.py
```

---

## 7) First Real Run Verification (Critical)

This section provides a comprehensive verification checklist for your first real run. Use these commands to validate that the system is working correctly at every stage.

### A) Pre-Run Checklist (Before Starting)

**Verify 3+ sources per claim:**

1. **Chrome CDP is accessible** (3 sources):
   ```cmd
   curl http://localhost:9222/json/version
   ```
   Expected: JSON response with `Browser` and `Protocol-Version` fields.

2. **Ollama is running** (3 sources):
   ```cmd
   curl http://localhost:11434/api/tags
   ```
   Expected: JSON with `models` array.

3. **Dashboard is accessible** (3 sources):
   ```cmd
   curl http://localhost:8501
   ```
   Expected: HTML response (Streamlit UI).

4. **Worker is running** (3 sources):
   ```cmd
   tasklist | findstr python
   ```
   Expected: Multiple python.exe processes (dashboard + worker).

5. **Control plane directories exist** (3 sources):
   ```cmd
   dir OUTPUTS\CONTROL_PLANE\jobs
   dir OUTPUTS\CONTROL_PLANE\status
   dir OUTPUTS\CONTROL_PLANE\logs
   ```
   Expected: All directories exist with `pending/`, `running/`, `done/`, `failed/` subdirectories.

### B) Commands to Verify Job Creation

After confirming a job in the chat UI, verify the job JSON was created:

```cmd
REM List all pending jobs
dir OUTPUTS\CONTROL_PLANE\jobs\pending /b

REM View specific job JSON (replace <run_id>)
type OUTPUTS\CONTROL_PLANE\jobs\pending\job_<run_id>.json

REM Verify job structure using Python
python -c "import json; j=json.load(open('OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json')); print('Job type:', j.get('job_type')); print('Supplier:', j.get('supplier_name')); print('Run ID:', j.get('run_id'))"
```

**Expected job JSON structure:**
```json
{
  "job_type": "product_list_refresh",
  "supplier_name": "angelwholesale.co.uk",
  "run_id": "sandbox_angelwholesale_20250214_001",
  "products_path": "OUTPUTS/PRODUCTS_LISTS/products_subset_angelwholesale_mixed_6.json",
  "override": {
    "system_config_path": null,
    "categories_path": null,
    "sandbox_supplier": "sandbox_angelwholesale_20250214_001"
  },
  "created_at": "2025-02-14T10:30:00Z",
  "status": "pending"
}
```

### C) Commands to Verify Status Updates

After the worker picks up the job, verify status JSON updates:

```cmd
REM Check if status file exists
if exist OUTPUTS\CONTROL_PLANE\status\<run_id>.json (
    echo Status file exists
    type OUTPUTS\CONTROL_PLANE\status\<run_id>.json
) else (
    echo Status file NOT found - job may not have started
)

REM Monitor status changes in real-time (PowerShell)
while ($true) { if (Test-Path "OUTPUTS\CONTROL_PLANE\status\<run_id>.json") { Get-Content "OUTPUTS\CONTROL_PLANE\status\<run_id>.json" | ConvertFrom-Json | Select-Object status, progress, last_updated }; Start-Sleep 2 }
```

**Expected status transitions:**
- `pending` → `running` → `done` (or `failed`)
- `progress` field should increment from 0 to 100
- `last_updated` timestamp should change frequently

### D) Commands to Verify Processing State Creation

After the job starts running, verify the processing state file:

```cmd
REM Find processing state file (contains "sandbox" in name)
dir OUTPUTS\CACHE\processing_states\*sandbox*processing_state.json /b

REM View processing state structure
python -c "import json; s=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); print('Schema version:', s.get('schema_version')); print('Supplier:', s.get('supplier_name')); print('Phase:', s.get('system_progression', {}).get('phase'))"

REM Verify key fields exist
python -c "import json; s=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); print('Has system_progression:', 'system_progression' in s); print('Has supplier_extraction_progress:', 'supplier_extraction_progress' in s); print('Has metadata:', 'metadata' in s)"
```

**Expected processing state structure:**
```json
{
  "schema_version": "1.2_THREAD_SAFE",
  "created_at": "2025-02-14T10:30:05Z",
  "last_updated": "2025-02-14T10:35:12Z",
  "supplier_name": "sandbox_angelwholesale_20250214_001",
  "system_progression": {
    "phase": "supplier_extraction",
    "persistent_category_index": 0,
    "resumption_ptr": 0
  },
  "supplier_extraction_progress": {
    "categories": {}
  },
  "metadata": {
    "config_hash": "...",
    "fix_markers": []
  }
}
```

### E) Commands to Verify Linking Map Creation

After Amazon matching begins, verify the linking map:

```cmd
REM Find linking map directory
dir OUTPUTS\FBA_ANALYSIS\linking_maps\ /b

REM View linking map structure
python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print('Total entries:', len(lm)); print('Sample keys:', list(lm.keys())[:3])"

REM Count entries with Amazon ASINs
python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); matched = sum(1 for v in lm.values() if v.get('amazon_asin')); print(f'Matched: {matched}/{len(lm)}')"
```

**Expected linking map structure:**
```json
{
  "ean_5050375010819": {
    "supplier_product": {
      "ean": "5050375010819",
      "title": "Product Title",
      "price_gbp": 1.99
    },
    "amazon_asin": "B09W64GKR4",
    "amazon_product": {
      "asin": "B09W64GKR4",
      "title": "Amazon Product Title",
      "price_gbp": 5.99
    },
    "match_confidence": 0.95,
    "matched_at": "2025-02-14T10:32:15Z"
  }
}
```

### F) Mid-Run Verification Commands

While the job is running, monitor progress:

```cmd
REM Poll status every 5 seconds (PowerShell)
while ($true) { if (Test-Path "OUTPUTS\CONTROL_PLANE\status\<run_id>.json") { $s = Get-Content "OUTPUTS\CONTROL_PLANE\status\<run_id>.json" | ConvertFrom-Json; Write-Host "Status: $($s.status) | Progress: $($s.progress)% | Updated: $($s.last_updated)" }; Start-Sleep 5 }

REM Check partial linking map growth
python -c "import json, time; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print(f'Current entries: {len(lm)}'); matched = sum(1 for v in lm.values() if v.get('amazon_asin')); print(f'Matched: {matched}')"

REM Monitor processing state progress
python -c "import json; s=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); sp=s.get('system_progression',{}); print(f'Phase: {sp.get(\"phase\")} | Category index: {sp.get(\"persistent_category_index\")} | Resume ptr: {sp.get(\"resumption_ptr\")}')"
```

### G) Cancellation Test Procedure

Test that cancellation preserves partial state:

```cmd
REM Step 1: Start a job (via chat UI)
REM Step 2: Wait 30 seconds for some progress
REM Step 3: Create cancellation flag
echo. > OUTPUTS\CONTROL_PLANE\jobs\running\job_<run_id>.json.cancelled

REM Step 4: Verify worker detects cancellation (check logs)
type OUTPUTS\CONTROL_PLANE\logs\<run_id>.log | findstr /i "cancelled"

REM Step 5: Verify job moved to failed directory
dir OUTPUTS\CONTROL_PLANE\jobs\failed\job_<run_id>.json

REM Step 6: Verify partial state persists
python -c "import json; s=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); print('State preserved:', s.get('last_updated')); print('Processed products:', s.get('system_progression', {}).get('resumption_ptr'))"

REM Step 7: Verify partial linking map exists
python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print(f'Partial linking map: {len(lm)} entries preserved')"
```

**Expected cancellation behavior:**
- Worker detects `.cancelled` flag within 10 seconds
- Job moves from `running/` to `failed/` directory
- Processing state file is saved with partial progress
- Linking map contains all matches made before cancellation
- Status JSON shows `status: "cancelled"` with final progress

### H) Post-Run Triangulation (Compare All Sources)

After the job completes, verify consistency across all sources:

```cmd
REM === TRIANGULATION CHECKLIST ===
REM Source 1: Job JSON
python -c "import json; j=json.load(open('OUTPUTS/CONTROL_PLANE/jobs/done/job_<run_id>.json')); print('Job status:', j.get('status')); print('Job run_id:', j.get('run_id')); print('Job supplier:', j.get('supplier_name'))"

REM Source 2: Status JSON
python -c "import json; s=json.load(open('OUTPUTS/CONTROL_PLANE/status/<run_id>.json')); print('Status status:', s.get('status')); print('Status progress:', s.get('progress')); print('Status run_id:', s.get('run_id'))"

REM Source 3: Processing State
python -c "import json; ps=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); print('State supplier:', ps.get('supplier_name')); print('State phase:', ps.get('system_progression', {}).get('phase')); print('State processed:', ps.get('system_progression', {}).get('resumption_ptr'))"

REM Source 4: Linking Map
python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print(f'Linking map entries: {len(lm)}'); matched = sum(1 for v in lm.values() if v.get('amazon_asin')); print(f'Linking map matched: {matched}')"

REM === CONSISTENCY CHECKS ===
REM Check 1: All run_ids match
python -c "import json; j=json.load(open('OUTPUTS/CONTROL_PLANE/jobs/done/job_<run_id>.json')); s=json.load(open('OUTPUTS/CONTROL_PLANE/status/<run_id>.json')); print('run_id match:', j.get('run_id') == s.get('run_id'))"

REM Check 2: Status is consistent
python -c "import json; j=json.load(open('OUTPUTS/CONTROL_PLANE/jobs/done/job_<run_id>.json')); s=json.load(open('OUTPUTS/CONTROL_PLANE/status/<run_id>.json')); print('status match:', j.get('status') == s.get('status'))"

REM Check 3: Progress is 100% if done
python -c "import json; s=json.load(open('OUTPUTS/CONTROL_PLANE/status/<run_id>.json')); print('Progress 100%:', s.get('progress') == 100)"

REM Check 4: Linking map has entries
python -c "import json; lm=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/<sandbox_supplier>/linking_map.json')); print('Has entries:', len(lm) > 0)"
```

**Triangulation Success Criteria:**
- ✅ All 4 sources have matching `run_id`
- ✅ Job JSON and Status JSON have matching `status` field
- ✅ If `status == "done"`, then `progress == 100`
- ✅ Linking map has at least 1 entry (if products were processed)
- ✅ Processing state has `last_updated` timestamp close to job completion
- ✅ All timestamps are in chronological order (created < updated < completed)

### I) Quick Verification Script (All-in-One)

Save this as `verify_run.ps1` and run with `powershell -ExecutionPolicy Bypass -File verify_run.ps1 <run_id>`:

```powershell
param($run_id)

Write-Host "=== VERIFICATION CHECKLIST FOR RUN: $run_id ===" -ForegroundColor Cyan

# Check 1: Job exists
$jobPath = "OUTPUTS\CONTROL_PLANE\jobs\done\job_$run_id.json"
if (Test-Path $jobPath) {
    Write-Host "[✓] Job JSON exists" -ForegroundColor Green
    $job = Get-Content $jobPath | ConvertFrom-Json
    Write-Host "  Status: $($job.status)"
    Write-Host "  Supplier: $($job.supplier_name)"
} else {
    Write-Host "[✗] Job JSON NOT found" -ForegroundColor Red
}

# Check 2: Status exists
$statusPath = "OUTPUTS\CONTROL_PLANE\status\$run_id.json"
if (Test-Path $statusPath) {
    Write-Host "[✓] Status JSON exists" -ForegroundColor Green
    $status = Get-Content $statusPath | ConvertFrom-Json
    Write-Host "  Status: $($status.status)"
    Write-Host "  Progress: $($status.progress)%"
} else {
    Write-Host "[✗] Status JSON NOT found" -ForegroundColor Red
}

# Check 3: Processing state exists
$stateFiles = Get-ChildItem "OUTPUTS\CACHE\processing_states\*sandbox*processing_state.json"
if ($stateFiles) {
    Write-Host "[✓] Processing state exists" -ForegroundColor Green
    $state = Get-Content $stateFiles[0].FullName | ConvertFrom-Json
    Write-Host "  Supplier: $($state.supplier_name)"
    Write-Host "  Phase: $($state.system_progression.phase)"
} else {
    Write-Host "[✗] Processing state NOT found" -ForegroundColor Red
}

# Check 4: Linking map exists
$linkingDirs = Get-ChildItem "OUTPUTS\FBA_ANALYSIS\linking_maps\" -Directory | Where-Object { $_.Name -like "*sandbox*" }
if ($linkingDirs) {
    Write-Host "[✓] Linking map directory exists" -ForegroundColor Green
    $linkingMap = Get-Content "$($linkingDirs[0].FullName)\linking_map.json" | ConvertFrom-Json
    Write-Host "  Entries: $($linkingMap.PSObject.Properties.Value.Count)"
} else {
    Write-Host "[✗] Linking map NOT found" -ForegroundColor Red
}

Write-Host "=== VERIFICATION COMPLETE ===" -ForegroundColor Cyan
```

**Usage:**
```cmd
powershell -ExecutionPolicy Bypass -File verify_run.ps1 sandbox_angelwholesale_20250214_001
```

### J) Troubleshooting Verification Failures

If any verification check fails:

1. **Job JSON not found:**
   - Check if job was actually queued: `dir OUTPUTS\CONTROL_PLANE\jobs\pending\`
   - Check worker logs: `type OUTPUTS\CONTROL_PLANE\logs\<run_id>.log`
   - Verify worker is running: `tasklist | findstr python`

2. **Status JSON not found:**
   - Job may not have started yet (wait 10-20 seconds)
   - Check if worker picked up job: `dir OUTPUTS\CONTROL_PLANE\jobs\running\`
   - Check for lock file: `dir OUTPUTS\CONTROL_PLANE\lock\`

3. **Processing state not found:**
   - Job may have failed before state creation
   - Check logs for errors: `type OUTPUTS\CONTROL_PLANE\logs\<run_id>.log | findstr /i error`
   - Verify sandbox supplier name in job JSON

4. **Linking map not found:**
   - Amazon matching may not have started yet
   - Check if any products were processed: `python -c "import json; s=json.load(open('OUTPUTS/CACHE/processing_states/<state_file>.json')); print(s.get('system_progression', {}).get('resumption_ptr'))"`
   - Verify supplier products exist in cache

5. **Inconsistent run_ids:**
   - Check for multiple runs with similar IDs
   - Verify you're using the correct run_id from the chat UI
   - Check job JSON for the actual run_id field

---

## 8) Quick Reference Commands

```cmd
REM List all jobs
dir OUTPUTS\CONTROL_PLANE\jobs\pending /b
dir OUTPUTS\CONTROL_PLANE\jobs\running /b
dir OUTPUTS\CONTROL_PLANE\jobs\done /b
dir OUTPUTS\CONTROL_PLANE\jobs\failed /b

REM View latest status
for /f "delims=" %f in ('dir /b /o-d OUTPUTS\CONTROL_PLANE\status\*.json') do @type "OUTPUTS\CONTROL_PLANE\status\%f" & goto :done
:done

REM View latest log
for /f "delims=" %f in ('dir /b /o-d OUTPUTS\CONTROL_PLANE\logs\*.log') do @type "OUTPUTS\CONTROL_PLANE\logs\%f" & goto :done
:done

REM Check worker lock
if exist OUTPUTS\CONTROL_PLANE\lock\active_run.lock (
    echo Worker is locked
    type OUTPUTS\CONTROL_PLANE\lock\active_run.lock
) else (
    echo No worker lock
)

REM Count linking map entries
python -c "import json, glob; lm=json.load(open(glob.glob('OUTPUTS/FBA_ANALYSIS/linking_maps/*/linking_map.json')[0])); print(f'Total entries: {len(lm)}')"
```

---
