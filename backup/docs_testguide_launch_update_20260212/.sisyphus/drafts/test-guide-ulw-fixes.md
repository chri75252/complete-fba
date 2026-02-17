# Test Guide: Control Plane Chat ULW Fixes (2026-02-10)

This section covers **every fix and implementation** from the Control Plane Chat ULW plan.
For each test, we describe the **pre-fix behavior** (what used to happen) and the **expected post-fix behavior** (what should happen now).

> **Prerequisites for every test below:**
> - Start the system using the 3-terminal setup from Section 1 of CONCISE_LAUNCH_GUIDE.md.
> - Have Chrome on port 9222, Ollama running, Dashboard on 8501, Worker running.
> - Navigate to `http://localhost:8501` and click the **Chat** tab.

---

## Test 6A — Limits defaults: missing values use system defaults (Task 1.3)

**What this tests:** When you submit a run without specifying limits, the system uses defaults from `config\system_config.json` instead of silently setting them to 0 (unlimited).

**Pre-fix behavior:** Omitting `max_products` in a chat request would result in `max_products=0` (unlimited), causing the system to attempt processing every single product.

**Post-fix behavior:** Omitting `max_products` falls back to the value in `config\system_config.json` → `system.max_products` (currently 1000000). Explicitly typing `0` still means unlimited.

**Chat prompt:**
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

**What to check after confirming and the job is queued:**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -c "import json, pathlib; jobs=sorted(pathlib.Path('OUTPUTS/CONTROL_PLANE/jobs').rglob('job_*.json')); j=json.loads(jobs[-1].read_text(encoding='utf-8')); print('max_products:', j.get('runtime',{}).get('max_products')); print('max_products_per_category:', j.get('runtime',{}).get('max_products_per_category'))"
```

**Expected output:** `max_products` and `max_products_per_category` should show the system defaults (e.g., `1000000` and `1000`), NOT `0`.

---

## Test 6B — Natural language limit editing: numeric values (Task 1.4, existing)

**What this tests:** While a run is pending confirmation, typing a natural language phrase like "first 12 products" updates the pending run's `max_products` parameter.

**Pre-fix behavior:** This already worked for numeric values ("first 12 products", "only 5 products").

**Post-fix behavior:** Same — still works. This test confirms it did not regress.

**Chat prompts (two-step sequence):**

Step 1 — Get a pending run proposed:
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

Step 2 — **Do NOT click Confirm yet.** Instead, type:
```
first 12 products
```

**Expected response:** Chat shows: `Updated pending run: max_products=12`

**Verify the pending tool call was updated:**
- The confirmation card should now show `max_products: 12` in the parameters.

---

## Test 6C — Natural language limit editing: "unlimited" / "no limit" / "all products" (Task 1.4, NEW FIX)

**What this tests:** Typing "unlimited", "no limit", or "all products" while a run is pending sets `max_products=0` (meaning unlimited).

**Pre-fix behavior:** These phrases were NOT recognized. The system would reply with a generic "A pending action is waiting for confirmation" warning and ignore the intent.

**Post-fix behavior:** The regex `\b(?:unlimited|no\s+limit|all\s+products)\b` now catches these phrases and sets `max_products=0`.

**Chat prompts (two-step sequence):**

Step 1 — Get a pending run proposed:
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

Step 2 — **Do NOT click Confirm yet.** Instead, type one of these variants:

Variant A:
```
unlimited
```

Variant B:
```
no limit
```

Variant C:
```
all products
```

**Expected response (all variants):** Chat shows: `Updated pending run: max_products=0`

**Verify the pending tool call was updated:**
- The confirmation card should now show `max_products: 0` in the parameters.

---

## Test 6D — Natural language limit editing: "analyze only 20 products" (Task 1.4, existing)

**What this tests:** The "analyze N products" pattern updates `max_products`.

**Chat prompts (two-step sequence):**

Step 1:
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

Step 2 — **Do NOT click Confirm.** Type:
```
analyze only 20 products
```

**Expected response:** `Updated pending run: max_products=20`

---

## Test 6E — Natural language limit editing: max_products_per_category (existing)

**What this tests:** Editing `max_products_per_category` via natural language while a run is pending.

**Chat prompts (two-step sequence):**

Step 1:
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

Step 2 — **Do NOT click Confirm.** Type:
```
max products per category to 5
```

**Expected response:** `Updated pending run: max_products_per_category=5`

---

## Test 6F — Persist last_run_id and use it for follow-up queries (Tasks 1.5 + 1.6)

**What this tests:** After confirming a run, the system remembers the `run_id` so you can ask for status without re-typing it.

**Pre-fix behavior (already correct, verified):** `last_run_id` was already persisted.

**Post-fix behavior:** Same — confirmed working.

**Chat prompts (three-step sequence):**

Step 1 — Start a run:
```
Run product-list refresh for angelwholesale.co.uk using this products file:
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_5.json
Use a new run_id.
```

Step 2 — Click **Confirm execute**. Note the `run_id` shown in the response.

Step 3 — Ask for status WITHOUT providing the run_id:
```
Show me the status
```

**Expected behavior:** The system should use the `last_run_id` from step 2 and return the status for that run, without asking you to provide a run_id.

---

## Test 6G — Cancellation writes both markers (Task 1.8)

**What this tests:** When you cancel a run, the system writes two files: canonical `.cancelled` and legacy `cancel_*.flag`.

**Pre-fix behavior (already correct, verified):** Both markers were already written.

**Post-fix behavior:** Same — confirmed working.

**Chat prompts (two-step sequence):**

Step 1 — Start a run (same as Test 6F Step 1), confirm it, and note the `run_id`.

Step 2 — While the worker is executing, type:
```
Cancel the current run
```

**Verify both markers exist:**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir OUTPUTS\CONTROL_PLANE\status\*.cancelled
dir OUTPUTS\CONTROL_PLANE\lock\cancel_*.flag
```

**Expected:** Both files exist for your run_id.

---

## Test 6H — Worker lock release on crash/timeout (Task 1.9, NEW FIX)

**What this tests:** If the worker's subprocess crashes or times out, the lock file is always released so future jobs are not permanently blocked.

**Pre-fix behavior:** If the subprocess threw an unhandled exception or timed out, the `active_run.lock` file could remain, blocking ALL future jobs until manually deleted.

**Post-fix behavior:** The lock acquisition is now wrapped in `try/finally`, guaranteeing `_release_lock()` is always called. Additionally, `proc.kill()` is called if `proc.terminate()` + 30s wait doesn't work.

**How to test (simulated crash):**

Step 1 — Start a run that will fail quickly (e.g., a supplier with a bad runner script):
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```
Confirm and let it run. Wait for it to complete (success or failure).

Step 2 — Check that the lock was released:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir OUTPUTS\CONTROL_PLANE\lock\active_run.lock
```

**Expected:** File should NOT exist after the run completes. If it does NOT exist = PASS.

Step 3 — Submit another job immediately after:
```
Show me the status
```

**Expected:** The worker picks up the new job without you having to manually delete the lock file.

---

## Test 6H-2 — Worker lock release after cancellation (Task 1.9 + 1.8)

**What this tests:** After cancelling a running job, the lock is released AND both cancel markers are cleaned up.

**Chat prompts:**

Step 1 — Start a product-list refresh (takes longer):
```
Run product-list refresh for angelwholesale.co.uk using this products file:
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_5.json
Use a new run_id.
```
Confirm and let the worker start.

Step 2 — Cancel it while running:
```
Cancel the current run
```

Step 3 — Wait a few seconds, then verify:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
REM Lock should be gone:
dir OUTPUTS\CONTROL_PLANE\lock\active_run.lock
REM Cancel markers should be cleaned up (worker removes them after processing):
dir OUTPUTS\CONTROL_PLANE\status\*.cancelled
dir OUTPUTS\CONTROL_PLANE\lock\cancel_*.flag
```

**Expected:**
- `active_run.lock` should NOT exist.
- Cancel markers should be cleaned up (the worker deletes them after processing the cancellation).
- Status JSON for the run should show `"state": "cancelled"`.

Verify status:
```bat
python -c "import json, pathlib; files=sorted(pathlib.Path('OUTPUTS/CONTROL_PLANE/status').glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True); r=json.loads(files[0].read_text(encoding='utf-8')); print('state:', r['state']); print('run_id:', r.get('run_id',''))"
```

---

## Test 6I — Clarify includes error context (Task 1.7)

**What this tests:** When the LLM cannot resolve a supplier from your prompt, the error message includes real context about what went wrong (not a generic "please clarify").

**Pre-fix behavior (already correct, verified):** `error_context` was already passed.

**Post-fix behavior:** Same — confirmed working.

**Chat prompt:**
```
Run analysis for fake-supplier-that-does-not-exist.com on all categories
```

**Expected behavior:** The chat should return a clarification response that includes specific error context, such as "Invalid workflow_key" or "supplier is not configured" — not just a generic "I didn't understand".

---

## Test 6J — Diagnostics probe CLI (Task 2.2, NEW)

**What this tests:** The new `diagnostics-probe` CLI subcommand that captures HTML, screenshots, and selector analysis from a URL via the existing Chrome CDP connection.

**Pre-fix behavior:** This command did not exist. The only control plane CLI subcommands were `worker` and `build-index`.

**Post-fix behavior:** `python -m control_plane diagnostics-probe` is now registered and functional.

**Terminal command (requires Chrome on port 9222):**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane diagnostics-probe --url "https://www.poundwholesale.co.uk/household" --probe-id "test_probe_001" --html --screenshot
```

**Expected output:**
```
Probe test_probe_001: title='...', selectors=N, errors=0
```

**Verify artifacts created:**
```bat
dir OUTPUTS\CONTROL_PLANE\diagnostics\test_probe_001\
```

**Expected files:**
- `report.json` — contains `probe_id`, `url`, `timestamp`, `page_title`, `selectors_found`
- `page.html` — full HTML dump of the page
- `screenshot.png` — full-page screenshot

**Inspect the report:**
```bat
python -c "import json; r=json.load(open('OUTPUTS/CONTROL_PLANE/diagnostics/test_probe_001/report.json','r',encoding='utf-8')); print('title:', r['page_title']); print('selectors:', r.get('selectors_found',{})); print('errors:', r.get('errors',[]))"
```

---

## Test 6J-2 — Diagnostics probe with trace and HAR (optional, advanced)

**Terminal command:**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane diagnostics-probe --url "https://angelwholesale.co.uk/Category/A-To-Z-wholesale" --probe-id "angel_trace_001" --html --screenshot --trace --har
```

**Expected additional files in `OUTPUTS\CONTROL_PLANE\diagnostics\angel_trace_001\`:**
- `trace.zip` — Playwright trace (viewable at `https://trace.playwright.dev`)
- `network.har` — HTTP Archive (viewable in Chrome DevTools Network tab)

---

## Test 6J-3 — Diagnostics probe help text (verify registration)

```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane diagnostics-probe --help
```

**Expected:** Shows `--url`, `--probe-id`, `--html`, `--screenshot`, `--trace`, `--har` flags.

---

## Test 6K — Job path format verification (Task 1.2)

**What this tests:** Job files use the correct `job_<run_id>.json` naming pattern.

**Pre-fix behavior (already correct, verified):** Naming was already correct.

**Post-fix behavior:** Same — confirmed working.

After any run is queued via chat, verify:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir /b OUTPUTS\CONTROL_PLANE\jobs\pending\job_*.json 2>nul
dir /b OUTPUTS\CONTROL_PLANE\jobs\running\job_*.json 2>nul
dir /b OUTPUTS\CONTROL_PLANE\jobs\done\job_*.json 2>nul
```

**Expected:** All job files follow the `job_<uuid>.json` pattern (not just `<uuid>.json`).

---

## Test 6L — Full end-to-end happy path (combined)

This test exercises the entire chain: chat -> tool call -> job JSON -> worker executes -> status.

**Chat prompt:**
```
Run product-list refresh for angelwholesale.co.uk using this products file:
C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\CONTROL_PLANE\inputs\products_subset_angelwholesale_mixed_5.json
Use a new run_id.
```

**Sequence:**
1. Chat proposes `enqueue_product_list_refresh` -> click **Confirm execute**.
2. Note the `run_id` from the response.
3. Watch worker terminal — it should pick up the job and start processing.
4. Type: `Show me the status` (uses last_run_id automatically).
5. Wait for completion or type: `Cancel the current run` to test cancellation.

**Verify (replace `<RUN_ID>` with actual):**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -c "import json; r=json.load(open('OUTPUTS/CONTROL_PLANE/status/<RUN_ID>.json','r',encoding='utf-8')); print('state:', r['state']); print('progress:', r.get('progress',{})); print('sandbox:', r.get('resolved_paths',{}).get('processing_state',''))"
```

**Expected:** State is `done`, `cancelled`, or `failed` (not stuck in `running`). Lock file is released regardless of outcome.

---

## Cleanup after testing

After running tests, clean up probe artifacts:
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
rmdir /S /Q OUTPUTS\CONTROL_PLANE\diagnostics\test_probe_001
rmdir /S /Q OUTPUTS\CONTROL_PLANE\diagnostics\angel_trace_001
```

---

## Quick reference: Test matrix

| Test | Feature | New Fix? | Pre-fix Behavior | Post-fix Behavior |
|------|---------|----------|-------------------|-------------------|
| 6A | Limits defaults | No (verified) | Missing limits -> 0 (unlimited) | Missing limits -> system_config defaults |
| 6B | NL edit: "first 12" | No (verified) | Worked | Still works |
| 6C | NL edit: "unlimited" | **YES** | Ignored, showed warning | Sets max_products=0 |
| 6D | NL edit: "analyze 20" | No (verified) | Worked | Still works |
| 6E | NL edit: per-category | No (verified) | Worked | Still works |
| 6F | Persist last_run_id | No (verified) | Worked | Still works |
| 6G | Cancel markers (both) | No (verified) | Worked | Still works |
| 6H | Lock release on crash | **YES** | Lock stuck forever | Lock always released via try/finally |
| 6H-2 | Lock release + cancel | **YES** | Lock stuck + markers lingered | Lock released + markers cleaned up |
| 6I | Clarify error_context | No (verified) | Worked | Still works |
| 6J | Diagnostics probe CLI | **YES** | Command did not exist | Full probe with HTML/screenshot/selectors |
| 6J-2 | Probe with trace/HAR | **YES** | N/A | trace.zip + network.har captured |
| 6J-3 | Probe help text | **YES** | N/A | --help shows all flags |
| 6K | Job path format | No (verified) | Correct | Still correct |
| 6L | Full e2e happy path | Combined | Various issues possible | All pieces work together |
