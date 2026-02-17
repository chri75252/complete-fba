# Test Guide: Control Plane Chat ULW Fixes (Consolidated, 2026-02-12)

This guide validates the Control Plane Chat/UI fixes using a **small number of end-to-end scenarios**.

Each scenario covers multiple fixes at once. If something fails, use the **Appendix: Granular Tests** to isolate the exact regression.

> **Prerequisites for every scenario below:**
> - Start the system using the 3-terminal setup in `docs\CONCISE_LAUNCH_GUIDE.md`.
> - Chrome running on port `9222` with your Keepa/SellerAmp extensions available.
> - Ollama running.
> - Dashboard running on `http://localhost:8501`.
> - Worker running: `python -m control_plane worker`.
> - Navigate to `http://localhost:8501` and open the **Chat** tab.

---

## Scenario 1 — Propose a run, edit limits, and confirm correct job runtime

**What this tests (combined):**
- **Limits defaults**: missing values fall back to `config\system_config.json` defaults (no accidental “unlimited”).
- **Natural-language edits (pending)**:
  - numeric edits like `first 12 products`
  - “unlimited/no limit/all products” sets `max_products=0`
  - “both … should be N” sets both limits
- **Limits parity**: if you set `max_products` but not `max_products_per_category`, the system keeps them aligned to avoid huge category enumeration.

**Pre-fix behavior (problematic):**
- Missing limits could become effectively unlimited (e.g., `max_products=0`) even when the user didn’t intend it.
- Some natural-language edits were ignored while pending, leading to confusing “pending action waiting” UX.
- “First N products” could still enumerate hundreds of URLs because per-category default stayed large.

**Post-fix behavior (expected):**
- Omitting limits uses system defaults.
- Pending natural-language edits are applied to the confirmation card.
- Setting `max_products` without explicitly setting per-category keeps per-category aligned.

**Chat prompts (sequence):**

Step 1 — Create a pending run:
```
Analyze these categories for poundwholesale.co.uk:
https://www.poundwholesale.co.uk/household
```

Step 2 — While the action is pending (do NOT confirm yet), test edits:

Variant A (numeric):
```
first 12 products
```

Variant B (both limits):
```
both max_products and max_products_per_category should be 10
```

Variant C (unlimited):
```
unlimited
```

**What to check (in the UI):**
- The confirmation card parameters update (e.g., `max_products=12`, or both=10, or `max_products=0`).

**What to check after confirming and the job is queued:**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -c "import json, pathlib; jobs=sorted(pathlib.Path('OUTPUTS/CONTROL_PLANE/jobs').rglob('job_*.json')); j=json.loads(jobs[-1].read_text(encoding='utf-8')); print('run_id:', j.get('run_id')); print('max_products:', j.get('runtime',{}).get('max_products')); print('max_products_per_category:', j.get('runtime',{}).get('max_products_per_category'))"
```

**Expected output:**
- `max_products` equals what you set (or a default if you didn’t set it).
- `max_products_per_category` equals what you set; if you only set `max_products`, it should match `max_products` (parity).

---

## Scenario 2 — Cancel and stop-at-N behavior during/after execution

**What this tests (combined):**
- **Cancel intercept**: typing “cancel/stop/kill the run” cancels deterministically (does not rely on the LLM picking the right tool).
- **Cancel markers**: both `.cancelled` and legacy `cancel_*.flag` are written.
- **Stop-at-N during running job**: typing “stop at 5 products” does NOT mutate a running job; it provides safe guidance.

**Pre-fix behavior (problematic):**
- Cancellation could go through the LLM planner and sometimes produce placeholder IDs or wrong tool calls.
- “Stop at N products” after confirming a run could be misinterpreted as a new request.

**Post-fix behavior (expected):**
- “Cancel the run” writes cancellation markers for the most recent run (or the explicit UUID if provided).
- “Stop at N products” during a running job returns a message telling you to cancel + re-run (no mutation).

**Chat prompts (sequence):**

Step 1 — Ensure you have a running job (from Scenario 1), or start a longer run.

Step 2 — While it is running, type:
```
Cancel the current run
```

Step 3 — Also type (while a job is running):
```
stop at 5 products
```

**What to check (cancel markers):**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
dir OUTPUTS\CONTROL_PLANE\status\*.cancelled
ndir OUTPUTS\CONTROL_PLANE\lock\cancel_*.flag
```

**Expected output:**
- A `.cancelled` file exists for the run.
- A legacy `cancel_<run_id>.flag` exists.
- Chat indicates cancellation was requested.

---

## Scenario 3 — Operator Panel sandbox isolation (prevents state contamination)

**What this tests (combined):**
- Operator Panel runs are sandbox-isolated by setting:
  - `job.sandbox_supplier` in job JSON
  - `workflows[workflow_key].supplier_name` in merged config
- Categories subset path is written under the run’s override directory.

**Pre-fix behavior (problematic):**
- Operator Panel runs could use canonical supplier identity and therefore read/write the canonical processing state, creating resume contamination.

**Post-fix behavior (expected):**
- Operator Panel creates a sandbox supplier name (e.g. `supplier__sandbox__<run_id_prefix>`).
- Merged config uses sandbox supplier for `supplier_name`.
- Job JSON includes `sandbox_supplier`.

**Operator Panel steps:**
1) Open the Operator Panel page.
2) Create a small test run (low limits) with a known category URL.

**What to check (job JSON + merged config):**
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -c "import json, pathlib; jobs=sorted(pathlib.Path('OUTPUTS/CONTROL_PLANE/jobs').rglob('job_*.json')); j=json.loads(jobs[-1].read_text(encoding='utf-8')); print('run_id:', j.get('run_id')); print('supplier_domain:', j.get('supplier_domain')); print('sandbox_supplier:', j.get('sandbox_supplier')); cfg=json.loads(pathlib.Path(j['override']['system_config_path']).read_text(encoding='utf-8')); wf=cfg['workflows'][j['workflow_key']]; print('merged supplier_name:', wf.get('supplier_name')); print('categories_config_path:', wf.get('categories_config_path'))"
```

**Expected output:**
- `sandbox_supplier` is present and differs from canonical domain.
- Merged config `supplier_name` equals `sandbox_supplier`.

---

## Appendix: Granular Tests (use only if a scenario fails)

- If Scenario 1 fails, re-run isolated checks:
  - Numeric edit: `first 12 products`
  - Unlimited: `unlimited` → `max_products=0`
  - Per-category edit: `max products per category to 5`
- If Scenario 2 fails:
  - Try cancel with explicit UUID: `cancel run_<uuid>`
  - Verify markers exist at:
    - `OUTPUTS\CONTROL_PLANE\status\<run_id>.cancelled`
    - `OUTPUTS\CONTROL_PLANE\lock\cancel_<run_id>.flag`
- Diagnostics probe CLI (optional):
  - `python -m control_plane diagnostics-probe --help`
  - `python -m control_plane diagnostics-probe --url "https://www.poundwholesale.co.uk/household" --probe-id "test_probe_001" --html --screenshot`
