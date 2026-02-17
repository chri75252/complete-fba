# Product List Refresh + Worker UX (Minimal-Risk Plan)

## TL;DR

> **Quick Summary**: Make `enqueue_product_list_refresh` fail fast on bad `products_path`, and make the dashboard explicitly tell the user that a job was queued and a worker must be started.
>
> **Deliverables**:
> - Clear “job queued; start worker” UX in `dashboard/chat_panel.py`
> - `products_path` existence validation in `control_plane/tools/product_list_refresh.py`
> - Updated planner system prompt to mention worker requirement and allow 2–4 sentence explanation
>
> **Estimated Effort**: Short
> **Parallel Execution**: YES (2 waves)
> **Critical Path**: Backup → code edits → verification

---

## Context

### Original Request
We have verified: `enqueue_product_list_refresh` creates a job file in `OUTPUTS/CONTROL_PLANE/jobs/pending` and requires a separate worker process to execute; currently no worker process running. Priority is “system works first, then more natural language”; least-risk, highest success.

### Verified Codebase Facts
- Worker entrypoint: `control_plane/worker.py` and CLI wiring in `control_plane/__main__.py`.
- Start worker: `python -m control_plane worker`.
- Job lifecycle directories:
  - Pending: `OUTPUTS/CONTROL_PLANE/jobs/pending/`
  - Running: `OUTPUTS/CONTROL_PLANE/jobs/running/`
  - Done: `OUTPUTS/CONTROL_PLANE/jobs/done/`
  - Failed: `OUTPUTS/CONTROL_PLANE/jobs/failed/`
- Global lock file: `OUTPUTS/CONTROL_PLANE/lock/active_run.lock`.
- Status file: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`.
- Log file: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`.
- Product list refresh execution command used by worker:
  - `python -m control_plane.run_product_list_refresh` with `CONTROL_PLANE_JOB_PATH` env set.

---

## Scope

### IN
- Operational guidance for starting worker and observing job consumption.
- Minimal code changes in exactly the 3 specified files.

### OUT (guardrails)
- No worker redesign (locking, state machine changes, retries).
- No new dependencies.
- No new UI panels beyond the requested message.
- No changes to job schema unless strictly required.
- No commits/push.

---

## Verification Strategy

### Test Infrastructure
- No dedicated unit test harness is required for these minimal changes.
- Verification is a combination of:
  - Deterministic CLI checks (`python -c ...`) for the `products_path` validation.
  - Operational checks for job consumption (job file moves pending → running → done/failed, status/log created).

### Note on "success" for refresh jobs
`control_plane/run_product_list_refresh.py` will likely require Chrome CDP + Amazon extraction dependencies. For least-risk verification, it’s acceptable if the job is consumed and ends in `failed/` with a clear status/log (that still proves the worker is functioning and consuming the queue).

---

## Operational Guidance (User-Facing)

### 1) Start the worker
Run in a separate terminal (repo root):
- `python -m control_plane worker`

Expected:
- Process stays running.
- When jobs exist, it creates/updates:
  - `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
  - `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`

### 2) Observe queue consumption
- Pending jobs appear as: `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`
- Worker moves them to:
  - `OUTPUTS/CONTROL_PLANE/jobs/running/` (while executing)
  - then `done/` or `failed/`

### 3) Interpreting `active_run.lock`
- If `OUTPUTS/CONTROL_PLANE/lock/active_run.lock` exists:
  - Worker will not start a new job (it polls and sleeps).
  - Treat it as “one run already claimed”.

**Minimal-risk guidance**:
- Do **not** delete the lock file automatically.
- If a lock persists and no worker is running, inspect:
  - the file contents (it should be a `run_id`)
  - whether `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` exists and is updating
  - whether a `python` process is running the worker

---

## Execution Strategy (Task Graph Waves)

### Wave 1 (Safe correctness + planner guidance)
1) Add `products_path` existence validation
2) Update chat planner system instructions (still JSON-only)

### Wave 2 (Dashboard success messaging)
3) Update `dashboard/chat_panel.py` to show “job queued + start worker” plus queue/lock diagnostics

### Wave 3 (Verification)
4) Run deterministic CLI checks for validation + run worker + observe job movement/status/log creation

---

## TODOs (single plan)

### 1) Add `products_path` validation (least-risk)

**What to do**:
- File: `control_plane/tools/product_list_refresh.py`
- In `enqueue_product_list_refresh(...)`, after `products_path` is determined and `if not products_path` check, add:
  - `Path(products_path).exists()` and `is_file()` validation
  - On missing: return `{"ok": False, "error": "products_path_not_found", "products_path": "...", "message": "..."}` (keep wording clear)
- Ensure validation happens before writing job file.

**Must NOT do**:
- Do not change job payload shape (beyond adding extra return fields on error).
- Do not attempt to auto-create missing files.

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Small, localized guardrail in one function.
- **Skills**: none (optional: `git-master` only if later asked to commit)

**Parallelization**:
- Can Run In Parallel: YES (with Task 2)
- Blocks: Task 4 verification

**References**:
- `control_plane/tools/product_list_refresh.py:34` - enqueue function and existing missing-products checks
- `control_plane/run_product_list_refresh.py:122` - consumer reads subset JSON via `read_json(Path(subset_path))` (will crash if missing)

**Acceptance Criteria / Verification**:
- `python -c "from pathlib import Path; from control_plane.tools.product_list_refresh import ProductListRefreshRequest, enqueue_product_list_refresh; from control_plane.paths import get_repo_root; r=enqueue_product_list_refresh(get_repo_root(), ProductListRefreshRequest(supplier_domain='poundwholesale.co.uk', products_path='C:/does_not_exist/products.json', dry_run=True)); print(r); assert r.get('ok') is False; assert 'products_path' in r"`
  - Expected: prints dict with `ok: False` and clear error/message.

---

### 2) Update planner system instructions (reduce confusion)

**What to do**:
- File: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- Keep “Return ONLY valid JSON. No markdown. No prose outside JSON.”
- Change rule that `explanation` must be single sentence → allow 2–4 sentences.
- Add explicit instruction for enqueue tools (at least `enqueue_product_list_refresh`, and optionally also `enqueue_run`):
  - Explanation must mention that it *queues a job* and that the user should *start the worker* (`python -m control_plane worker`) to execute.

**Must NOT do**:
- Do not change JSON schema shape.
- Do not introduce markdown fences that could confuse the local LLM (keep as current style).

**Recommended Agent Profile**:
- **Category**: `writing`
  - Reason: Prompt text, precision matters.
- **Skills**: none

**Parallelization**:
- Can Run In Parallel: YES (with Task 1)
- Blocks: None (but improves UX)

**References**:
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md:29` - JSON output shape and explanation rules
- `dashboard/chat_panel.py:214` - explanation is used as assistant message content

**Acceptance Criteria / Verification**:
- Run dashboard and ensure planned tool call JSON remains valid (manual observation is fine).
- Confirm no markdown/prose leaks outside JSON in planner outputs (log / audit files if available).

---

### 3) Dashboard message after enqueue (operational success)

**What to do**:
- File: `dashboard/chat_panel.py`
- After tool execution (both paths):
  - The “Confirm execute” branch around `dashboard/chat_panel.py:143`
  - The non-confirm immediate execution branch around `dashboard/chat_panel.py:211`
- If `tool_call.name == "enqueue_product_list_refresh"` and `result.get("ok") is True`:
  - Compose a clear English message (2–8 lines) that includes:
    - “Job queued; worker must be running”
    - `run_id` and `sandbox_supplier` from the tool result
    - Where to look:
      - Status: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
      - Log: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`
      - Pending dir: `OUTPUTS/CONTROL_PLANE/jobs/pending/`
    - Command to start worker: `python -m control_plane worker`
    - Pending jobs count right now
    - Lock status: whether `OUTPUTS/CONTROL_PLANE/lock/active_run.lock` exists
- Minimal implementation approach:
  - Use `get_paths()` already imported in `dashboard/chat_panel.py` to locate `jobs_pending` and `active_run_lock`.
  - Count pending jobs: `len(list(paths.jobs_pending.glob("job_*.json")))`.
  - Lock presence: `paths.active_run_lock.exists()`.

**Must NOT do**:
- Do not change tool execution semantics.
- Do not add additional Streamlit widgets unless requested; keep it as a plain assistant message.

**Recommended Agent Profile**:
- **Category**: `quick`
  - Reason: Small conditional messaging change.
- **Skills**: none

**Parallelization**:
- Can Run In Parallel: NO (depends on Tasks 1–2 only conceptually; technically independent, but do last to reduce user confusion while WIP)
- Blocks: Task 4 verification

**References**:
- `dashboard/chat_panel.py:143` - confirmed write-tool execution path
- `dashboard/chat_panel.py:211` - non-write tool execution path
- `control_plane/paths.py:32` - `jobs_pending` path (pending job count)
- `control_plane/paths.py:64` - `active_run_lock` path
- `control_plane/worker.py:161` - job moved pending → running (what the user should observe)

**Acceptance Criteria / Verification**:
- Run dashboard; enqueue product refresh; observe assistant message includes:
  - `run_id`, `sandbox_supplier`, “job queued”, worker command, status/log paths, pending count, lock status.

---

### 4) Backup protocol for each touched file (mandatory)

**Files to touch (exact)**
- `dashboard/chat_panel.py`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

**What to do** (before editing each file):
1) Create backup dir:
- `backup/chat_ux_and_product_refresh_20260202/`

2) Copy file into backup dir (retain filename):
- Example PowerShell:
  - `Copy-Item "dashboard\chat_panel.py" "backup\chat_ux_and_product_refresh_20260202\chat_panel.py"`

3) Create next-to-file timestamped backup:
- Suffix format: `.bak_02-02-26_HH-MM-SS`
- Example PowerShell (pattern):
  - `$ts = Get-Date -Format "HH-mm-ss"; Copy-Item "dashboard\chat_panel.py" "dashboard\chat_panel.py.bak_02-02-26_$ts"`

**Must NOT do**:
- Do not proceed with edits if backups are missing/empty.

---

## Verification Steps (Commands + Expected Outcomes)

### A) Sanity check worker help / wiring
- `python -m control_plane --help`
  - Expected: shows subcommands including `worker`.

### B) Validate `products_path` guardrail (no enqueue)
- `python -c "from control_plane.tools.product_list_refresh import ProductListRefreshRequest, enqueue_product_list_refresh; from control_plane.paths import get_repo_root; r=enqueue_product_list_refresh(get_repo_root(), ProductListRefreshRequest(supplier_domain='poundwholesale.co.uk', products_path='C:/does_not_exist/products.json', dry_run=True)); print(r)"`
  - Expected: `ok: False` with clear error and the missing path echoed.

### C) Enqueue a real job (creates pending job file)
Option 1 (enqueue with inline products to guarantee subset file exists):
- `python -c "from control_plane.tools.product_list_refresh import ProductListRefreshRequest, enqueue_product_list_refresh; from control_plane.paths import get_repo_root; req=ProductListRefreshRequest(supplier_domain='poundwholesale.co.uk', products=[{'title':'Test','url':'https://example.com','ean':'123'}], dry_run=False); print(enqueue_product_list_refresh(get_repo_root(), req))"`
  - Expected:
    - `ok: True`
    - prints `run_id`, `sandbox_supplier`
    - job file exists under `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`

### D) Start worker and see job consumed
- In a separate terminal: `python -m control_plane worker`
  - Expected:
    - Job file moves from `pending/` to `running/` quickly.
    - Status file created: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
    - Log file created: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`
    - Then job moves to `done/` or `failed/`.

### E) Dashboard UX smoke check
- `python -m streamlit run dashboard/app_fixed.py --server.port 8501`
  - Expected: chat panel shows enqueue result message with worker instructions and queue/lock info.

---

## Notes / Risk Controls
- Stale `active_run.lock` is a known operational footgun; plan does not change lock behavior, only makes it visible.
- Product refresh job may fail due to missing Chrome/CDP; that’s acceptable for verifying consumption mechanics.

---

## Handoff
Plan is ready for execution by Sisyphus.
