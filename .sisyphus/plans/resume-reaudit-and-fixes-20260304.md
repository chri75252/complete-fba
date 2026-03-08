# Resume Re-Audit + Fixes (Sandbox Categories + Run Integrity)

## TL;DR

> Quick summary: Re-audit two specific runs (0695 + d8f5) with 3-source triangulation (status JSON + logs + output artifacts), then apply a minimal-risk fix set so (a) sandbox resume cannot crash on empty manifests, and (b) control-plane validation/status no longer lies (done vs traceback).
>
> Deliverables:
> - Deterministic re-audit write-up for both run IDs (file-grounded)
> - Fixes in control-plane logic (enqueue + worker status + validation logic)
> - Agent-executable verification commands proving the before/after state
>
> Estimated effort: Medium
> Parallel execution: YES (3 waves)
> Critical path: T2 (state-manager fix) -> T4 (worker/validation correctness) -> T6/T7 (re-run verification)

---

## Context

### Original request (user intent)
- "I strongly believe your analysis is wrong regarding the categories workflow (sandboxed)." User reports they interrupted and resumed the main workflow without issues.
- Revisit and confirm/refute prior hypotheses with at least 3 sources of truth simultaneously (logs + scripts + outputs).
- Use Momus after re-audit.

### Runs in scope (ONLY)
- `06956903-c98e-4867-a1b4-e19798a1bb40` (Angel sandbox category resume)
- `d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5` (EFG product list refresh)

### Evidence anchors (must be used in verification)
- Scripts:
  - `control_plane/tools/jobs.py`
  - `control_plane/chat_orchestrator.py`
  - `control_plane/run_product_list_refresh.py`
  - `control_plane/worker.py`
  - `control_plane/tools/run_validation.py`
  - `utils/fixed_enhanced_state_manager.py`
  - `run_custom_angelwholesale-co-uk.py` (PROTECTED)
- Outputs/logs:
  - `OUTPUTS/CONTROL_PLANE/status/06956903-c98e-4867-a1b4-e19798a1bb40.json`
  - `OUTPUTS/CONTROL_PLANE/status/d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5.json`
  - `OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json`
  - `logs/debug/run_custom_angelwholesale-co-uk__sandbox__06956903_20260302_160809.log`

### Re-audit baseline conclusion (from Oracle critique; must be re-verified by executor)
- `0695...` is a real failure (IndexError during startup) but recorded as `state="done"` because the runner prints the traceback but exits with code 0 and `control_plane/worker.py` uses returncode.
- `d8f5...` completed its refresh; "Event loop is closed" is a shutdown artifact.
- `validate_run_integrity()` false-fails completed runs because `control_plane/tools/run_validation.py` expects the job JSON to remain under `OUTPUTS/CONTROL_PLANE/jobs/pending/` after the worker moves it.

---

## Work objectives

### Core objective
Make sandbox resume and run-integrity classification deterministic and crash-proof for the two anchored runs (no broad refactors).

### Must-have outcomes
- 0695: no startup crash in state manager; status reflects failure if traceback occurs; validation does not mislabel due to pending-job path.
- d8f5: remains a clean "done"; validation does not false-fail; shutdown artifacts do not flip it to failed.

### Must NOT do (guardrails)
- Do not edit processing state JSONs or output artifacts as a "repair".
- Do not expand scope beyond the two run IDs unless the user names additional IDs.
- Do not advance resume pointers backwards; preserve monotonic semantics.
- Avoid large refactors of control-plane orchestration.
- Do not edit any main workflow scripts (e.g. `run_custom_*.py`, `utils/fixed_enhanced_state_manager.py`).

### Defaults applied (override if you disagree)
- Main workflow scripts are treated as NOT editable. Fixes must stay in `control_plane/*` and be minimal.
- Sandbox identity should be stable across runs (avoid embedding run_id into sandbox supplier name), so resume/copy logic can reliably find previous sandbox artifacts.

---

## Verification strategy (agent-executable; no human confirmation)

### Test strategy decision
- Automated tests: Tests-after (add targeted tests only where low-effort and high-signal)
- Primary verification: scripted checks + controlled re-runs producing evidence files

### 3-source triangulation rule (MANDATORY)
For each run ID, verification must include ALL of:
1) Status JSON: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`
2) Log file: `logs/debug/run_custom_...<run_id>...log` and/or `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`
3) Output artifacts: existence + non-zero-size check for required files (linking map, caches, overrides)

### Evidence policy
Store artifacts for each QA scenario under:
- `.sisyphus/evidence/task-<N>-<scenario>.txt` (terminal output)
- `.sisyphus/evidence/task-<N>-<scenario>.json` (extracted/normalized JSON)

---

## Execution strategy

### Parallel execution waves

Wave 1 (audit + foundational fixes; safe to run in parallel)
- T1. Build a deterministic re-audit table for both run IDs (3-source triangulation)
- T2. Fix sandbox enqueue so the state manager never sees an empty manifest (control-plane only)
- T3. Fix `run_validation` false-fail logic for completed runs
- T4. Fix worker/status correctness WITHOUT editing protected runners (traceback classifier + shutdown whitelist)
- T5. (Optional) Add a tiny control-plane self-check script for sandbox manifest readiness

Wave 2 (integration)
- T6. Start control-plane worker + enqueue an Angel sandbox run (single category subset)
- T7. Interrupt + resume the same Angel sandbox run_id and capture evidence
- T8. Enqueue an EFG product list refresh run and capture evidence (status + outputs + validation)

---

## TODOs

- [ ] 1. Re-audit both runs with 3-source triangulation table

  What to do:
  - For each run ID (0695, d8f5), extract:
    - `status.state`, any `error` fields, and log tail excerpt
    - presence/non-zero size of key artifacts (categories_subset, linking map, caches)
  - Write a short, file-grounded table summarizing:
    - Which source says what (status vs log vs outputs)
    - Where contradictions exist

  Must NOT do:
  - Do not infer success/failure from only one source.

  Recommended agent profile:
  - Category: `writing`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 1)

  References:
  - `OUTPUTS/CONTROL_PLANE/status/06956903-c98e-4867-a1b4-e19798a1bb40.json` - reported state + embedded traceback
  - `logs/debug/run_custom_angelwholesale-co-uk__sandbox__06956903_20260302_160809.log` - true workflow failure marker (`IndexError`)
  - `OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json` - subset size (1 URL)
  - `OUTPUTS/CONTROL_PLANE/status/d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5.json` - shows done + shutdown artifact

  Acceptance criteria:
  - A single table exists (markdown or text) that, for BOTH run IDs, lists:
    - status JSON verdict
    - log verdict
    - artifact verdict
    - final reconciled verdict

  QA scenarios:
  ```
  Scenario: Re-audit 0695 triangulation
    Tool: Bash (python)
    Steps:
      1. Read and print `state` from OUTPUTS/CONTROL_PLANE/status/0695....json
      2. Search log file for `Traceback` and `IndexError`
      3. Confirm categories_subset.json exists and has 1 URL
    Expected Result: Evidence text shows contradiction (done + traceback) and subset=1
    Evidence: .sisyphus/evidence/task-1-0695-triangulation.txt

  Scenario: Re-audit d8f5 triangulation
    Tool: Bash (python)
    Steps:
      1. Read and print `state` from OUTPUTS/CONTROL_PLANE/status/d8f5....json
      2. Search log tail for `Event loop is closed` and confirm no earlier workflow tracebacks
      3. Confirm linking map exists and has 6 entries
    Expected Result: Evidence text supports "done" and identifies shutdown-only traceback
    Evidence: .sisyphus/evidence/task-1-d8f5-triangulation.txt
  ```

- [ ] 2. Fix sandbox enqueue so the state manager never sees an empty manifest (control-plane only)

  What to do:
  - Root cause (as observed in 0695): `utils/fixed_enhanced_state_manager.py` falls back to loading `config/<supplier_name_without_.co.uk>_categories.json` when the processing state has no frozen manifest. For sandbox runs, `supplier_name` currently includes a sandbox suffix, so the derived config path does not exist and the manifest becomes `[]`, leading to `IndexError`.
  - Fix this WITHOUT touching main workflow scripts by changing how sandbox runs are enqueued.
  - Apply the sandbox naming/enqueue fixes to BOTH `chat_orchestrator.py` (repo root, where UI enqueues happen) and `control_plane/chat_orchestrator.py` (if/where applicable to the control plane agent UI paths):
    1) Make the default sandbox identity stable (do not include run_id in the sandbox name). Example: `sandbox_suffix = "sandbox"`.
    2) Ensure the sandbox categories config file exists at the path the state manager expects:
       - Derive expected path exactly as the state manager does: `config/{sandbox_supplier.replace('.co.uk','')}_categories.json`.
       - If missing, copy from the base supplier categories file `config/{supplier_domain.replace('.co.uk','')}_categories.json`.
       - If the base file is missing, fail early in the control plane with a clear error (do not enqueue the job).
    3) (Resume safety) If a resume is requested (non-trivial sandbox_suffix already in use) and the user did not provide category URLs, implement Fix-B style fallback:
       - Find the latest non-empty `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json` that matches the same stable `sandbox_supplier`.
       - Use its `category_urls` to populate the current run's `categories_subset.json`.

  Must NOT do:
  - Do not mutate processing state files directly.
  - Do not advance resume pointers based on guesses when manifest is empty.
  - Do not change main workflow scripts; only adjust control-plane enqueue behavior.

  Recommended agent profile:
  - Category: `unspecified-high`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: NO (Wave 1, but should not overlap with other tasks touching same file)
  - Blocked by: None
  - Blocks: T6

  References:
  - `utils/fixed_enhanced_state_manager.py:3077-3111` - shows the exact config-path derivation used when no frozen manifest exists (read-only reference)
  - `control_plane/chat_orchestrator.py` - where sandbox_supplier + overrides are constructed today
  - `control_plane/tools/jobs.py` - job payload includes `sandbox_supplier`
  - `OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json` - example sandbox subset (currently 1 URL)

  Acceptance criteria:
  - Enqueuing a sandbox run causes the expected sandbox categories config file to exist under `config/` BEFORE the runner starts.
  - Reproducing the 0695 startup conditions no longer yields the "Category config file not found" warning for the sandbox supplier.
  - The sandbox run no longer crashes with `IndexError` in `_first_incomplete_index_by_url`.

  QA scenarios:
  ```
  Scenario: Control-plane creates sandbox categories config file
    Tool: Bash (python)
    Steps:
      1. Compute sandbox_supplier (stable) for angelwholesale.co.uk
      2. Compute expected config file path using the same string transform as state manager
      3. Enqueue a sandbox run and confirm the file exists and has non-empty `category_urls`
    Expected Result: sandbox categories config file exists and is non-empty
    Evidence: .sisyphus/evidence/task-2-sandbox-config-file.txt
  ```

- [ ] 3. Fix `run_validation` false-fails for completed runs

  What to do:
  - Update `control_plane/tools/run_validation.py` so completed runs do not fail integrity checks due to missing `OUTPUTS/CONTROL_PLANE/jobs/pending/job_<run_id>.json`.
  - Make the check conditional on `status.state`:
    - pending/running: job in pending may exist
    - done/failed: job should be searched in done/failed dirs or the requirement dropped

  Must NOT do:
  - Do not loosen validation of actual required output artifacts.

  Recommended agent profile:
  - Category: `quick`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 1)
  - Blocks: T6, T7 (verification)

  References:
  - `control_plane/tools/run_validation.py` - Oracle pointed to ~223-228 pending-job expectation
  - `OUTPUTS/CONTROL_PLANE/status/d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5.json` - state=done example
  - `OUTPUTS/CONTROL_PLANE/status/06956903-c98e-4867-a1b4-e19798a1bb40.json` - state=done but should be reconciled

  Acceptance criteria:
  - `validate_run_integrity()` returns PASS for d8f5 (assuming artifacts are present) and does not fail solely due to missing pending job JSON.
  - For 0695, validation failure (if any) is tied to real missing artifacts or real crash indicators, not the pending-job path.

  QA scenarios:
  ```
  Scenario: Validation no longer depends on jobs/pending for done runs
    Tool: Bash (python)
    Steps:
      1. Run the validation tool for d8f5
      2. Confirm result does not cite jobs/pending missing
    Expected Result: PASS or failure reasons unrelated to jobs/pending
    Evidence: .sisyphus/evidence/task-3-validation-d8f5.txt

  Scenario: 0695 validation is meaningful
    Tool: Bash (python)
    Steps:
      1. Run validation for 0695
      2. Confirm failure (if any) cites real crash/outputs
    Expected Result: Failure reasons are actionable and grounded
    Evidence: .sisyphus/evidence/task-3-validation-0695.txt
  ```

- [ ] 4. Make worker/status reflect real failures without editing protected runners (default path)

  What to do:
  - In `control_plane/worker.py`, augment status finalization:
    - If `returncode != 0` -> failed (existing)
    - If `returncode == 0` but log tail contains strong failure markers (Traceback + IndexError + known "Workflow failed" markers) -> mark failed OR set `error.summary`.
  - Add a whitelist for known shutdown-only artifacts so d8f5 stays done. Concretely, treat these as NON-fatal only if they appear after a clear success marker:
    - `Exception ignored in: <function BaseSubprocessTransport.__del__`
    - `RuntimeError: Event loop is closed`
    - `asyncio.base_subprocess` destructor context

  Must NOT do:
  - Do not mark failed on any traceback blindly (avoid false positives).

  Recommended agent profile:
  - Category: `unspecified-high`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 1)
  - Blocks: T6/T7 correctness checks

  References:
  - `control_plane/worker.py` - returncode-based done/failed selection (Oracle pointed to ~485-493)
  - `OUTPUTS/CONTROL_PLANE/status/d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5.json` - example of shutdown artifact
  - `logs/debug/run_custom_angelwholesale-co-uk__sandbox__06956903_20260302_160809.log` - example of real failure signature

  Acceptance criteria:
  - 0695 is marked failed (or has explicit error summary) when a real traceback is present, even if returncode is 0.
  - d8f5 remains done (shutdown artifacts are ignored when success marker exists).

  QA scenarios:
  ```
  Scenario: 0695 classified as failed by heuristic
    Tool: Bash (python)
    Steps:
      1. Re-run the worker classification logic against the saved log/status artifacts
      2. Confirm status becomes failed or error summary is populated
    Expected Result: Classification matches real failure
    Evidence: .sisyphus/evidence/task-4-0695-classification.txt

  Scenario: d8f5 stays done
    Tool: Bash (python)
    Steps:
      1. Re-run the worker classification logic against d8f5 artifacts
      2. Confirm done remains done
    Expected Result: No regression due to shutdown traceback
    Evidence: .sisyphus/evidence/task-4-d8f5-classification.txt
  ```

- [ ] 5. (Optional) Add a tiny control-plane self-check script for sandbox manifest readiness

  What to do:
  - Add a small, standalone control-plane script (or tool function) that:
    - Given `supplier_domain` and `sandbox_suffix`, prints the expected sandbox categories config path and whether it exists / is non-empty.
    - Exits non-zero if missing/empty.

  Must NOT do:
  - Do not create a large test suite; keep it minimal.

  Recommended agent profile:
  - Category: `quick`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 1)

  Acceptance criteria:
  - A single automated check exists that fails on old behavior and passes with fix.

  QA scenarios:
  ```
  Scenario: Run targeted test
    Tool: Bash (pytest or python)
    Steps:
      1. Execute the check
    Expected Result: PASS
    Evidence: .sisyphus/evidence/task-5-test.txt
  ```

- [ ] 6. Start worker + enqueue Angel sandbox run (single URL subset)

  What to do:
  - Ensure the control-plane worker is running.
    - Canonical command: `python -m control_plane worker`
  - Enqueue a sandbox run for Angel using `control_plane/tools/jobs.py` helpers (no UI required):
    - Load a real category URL from `OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json` (first URL)
    - Create a new run_id (UUID)
    - Write overrides via `write_categories_subset()` + `write_merged_system_config()`
    - Create `RunRequest(supplier_domain='angelwholesale.co.uk', workflow_key='angelwholesale_workflow', runner_script='run_custom_angelwholesale-co-uk.py', ...)`
    - Use a stable sandbox identity (per Task 2): `sandbox_suffix = "sandbox"`, `sandbox_supplier = f"{supplier_domain}__{sandbox_suffix}"`
    - Call `enqueue_run_job(..., sandbox_supplier=sandbox_supplier)`

  Recommended agent profile:
  - Category: `unspecified-high`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 2)
  - Blocked by: T2, T3, T4

  Acceptance criteria:
  - Worker is running and the job is enqueued (job JSON present under `OUTPUTS/CONTROL_PLANE/jobs/pending/`).
  - Status file is created for the new run_id: `OUTPUTS/CONTROL_PLANE/status/<run_id>.json`.
  - The overrides dir contains both:
    - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/categories_subset.json`
    - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/system_config.merged.json`

  QA scenarios:
  ```
  Scenario: Enqueue Angel sandbox run via Python (no UI)
    Tool: Bash (python)
    Steps:
      1. Start worker (background): `python -m control_plane worker`
      2. Enqueue the job:

         ```python
         import json
         import uuid
         from pathlib import Path

         from control_plane.tools.jobs import (
             RunRequest,
             enqueue_run_job,
             write_categories_subset,
             write_merged_system_config,
         )

         base_cfg = json.loads(Path("config/system_config.json").read_text(encoding="utf-8"))
         seed_subset = json.loads(
             Path(
                 "OUTPUTS/CONTROL_PLANE/overrides/06956903-c98e-4867-a1b4-e19798a1bb40/categories_subset.json"
             ).read_text(encoding="utf-8")
         )
         url = seed_subset["category_urls"][0]

         run_id = str(uuid.uuid4())
         supplier = "angelwholesale.co.uk"
         sandbox_suffix = "sandbox"
         sandbox_supplier = f"{supplier}__{sandbox_suffix}"

         categories_path = write_categories_subset(run_id, sandbox_supplier, [url])

         overrides = {
             "system": {
                 "max_products": 10,
                 "max_products_per_category": 10,
             },
             "workflows": {
                 "angelwholesale_workflow": {
                     "supplier_name": sandbox_supplier,
                     "categories_config_path": str(categories_path),
                 }
             },
         }

         base_creds = (base_cfg.get("credentials") or {}).get(supplier)
         if isinstance(base_creds, dict) and base_creds:
             overrides["credentials"] = {sandbox_supplier: base_creds}

         merged_cfg_path = write_merged_system_config(run_id, base_cfg, overrides=overrides)

         req = RunRequest(
             supplier_domain=supplier,
             workflow_key="angelwholesale_workflow",
             runner_script="run_custom_angelwholesale-co-uk.py",
             category_urls=[url],
             max_products=10,
             max_products_per_category=10,
             notes="repro: angel sandbox single-url",
         )

         job_path = enqueue_run_job(
             run_id,
             req,
             merged_cfg_path,
             categories_path,
             sandbox_supplier=sandbox_supplier,
         )

         print("run_id=", run_id)
         print("sandbox_supplier=", sandbox_supplier)
         print("job_path=", job_path)
         print("categories_path=", categories_path)
         print("merged_cfg_path=", merged_cfg_path)
         ```
      3. Wait until `OUTPUTS/CONTROL_PLANE/status/<run_id>.json` exists
    Expected Result: status file created; categories_subset exists under overrides; no immediate startup crash
    Evidence: .sisyphus/evidence/task-6-angel-enqueue.txt
  ```

- [ ] 7. Interrupt + resume the same Angel sandbox run_id (prove resume stability)

  What to do:
  - Using the run_id from Task 6:
    - Interrupt the worker mid-run (simulate a crash/stop)
    - Restart the worker
    - Re-enqueue the SAME run_id (write a new pending job JSON with the same run_id) pointing at the SAME overrides paths
  - Confirm the run resumes without the startup `IndexError` that occurred in 0695.
  - Follow the natural language testing guide (`docs/chat_ui_natural_language_guide.md`) to verify the end-to-end Chat UI experience works flawlessly without regressions.

  Recommended agent profile:
  - Category: `unspecified-high`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 2)
  - Blocked by: T2, T3, T4, T6

  Acceptance criteria:
  - No startup crash occurs on resume.
  - 3 sources of truth align:
    - Status reflects real state
    - Logs do not show the previous `IndexError`
    - Expected artifacts exist under the run_id overrides dir

  QA scenarios:
  ```
  Scenario: Interrupt worker and resume same run_id
    Tool: Background process control + Bash (python)
    Steps:
      1. Stop worker process while the run is in progress
      2. Restart worker: `python -m control_plane worker`
      3. Re-enqueue the SAME run_id, reusing the existing override files:

         ```python
         from pathlib import Path

         from control_plane.tools.jobs import RunRequest, enqueue_run_job

         run_id = "<paste-run_id-from-task-6>"
         supplier = "angelwholesale.co.uk"
         sandbox_suffix = "sandbox"
         sandbox_supplier = f"{supplier}__{sandbox_suffix}"
         url = "<same-url-as-task-6>"

         merged_cfg_path = Path(f"OUTPUTS/CONTROL_PLANE/overrides/{run_id}/system_config.merged.json")
         categories_path = Path(f"OUTPUTS/CONTROL_PLANE/overrides/{run_id}/categories_subset.json")

         req = RunRequest(
             supplier_domain=supplier,
             workflow_key="angelwholesale_workflow",
             runner_script="run_custom_angelwholesale-co-uk.py",
             category_urls=[url],
             max_products=10,
             max_products_per_category=10,
             notes="resume repro",
         )

         job_path = enqueue_run_job(
             run_id,
             req,
             merged_cfg_path,
             categories_path,
             sandbox_supplier=sandbox_supplier,
         )

         print("job_path=", job_path)
         ```
      4. Confirm status/logs show resume (not a fresh start), and no IndexError occurs
    Expected Result: Resume proceeds; no startup IndexError; status/logs/artifacts consistent
    Evidence: .sisyphus/evidence/task-7-angel-resume.txt
  ```

- [ ] 8. Re-run EFG product list refresh and prove validation/status correctness

  What to do:
  - Validate the existing d8f5 run artifacts after T3/T4 changes:
    - `validate_run_integrity("d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5")` should not false-fail due to jobs/pending.
  - Optional (only if inputs exist and you want an end-to-end re-run): enqueue a fresh PLR job via `control_plane.tools.product_list_refresh.enqueue_product_list_refresh()`.

  Recommended agent profile:
  - Category: `unspecified-high`
  - Skills: (none)

  Parallelization:
  - Can run in parallel: YES (Wave 2)
  - Blocked by: T3, T4

  Acceptance criteria:
  - d8f5-like run is consistently classified as done.
  - validation output does not reference jobs/pending missing.

  QA scenarios:
  ```
  Scenario: Validate existing d8f5 run_id
    Tool: Bash (python)
    Steps:
      1. Run:

         ```python
         from control_plane.tools.run_validation import validate_run_integrity
         import json

         out = validate_run_integrity("d8f5d679-1fa2-4d6e-ad5e-f5c5acc4a8e5")
         print(json.dumps(out, indent=2, sort_keys=True))
         ```
      2. Confirm output does NOT cite missing `OUTPUTS/CONTROL_PLANE/jobs/pending/job_d8f5....json`
    Expected Result: PASS (or meaningful failures unrelated to jobs/pending)
    Evidence: .sisyphus/evidence/task-8-d8f5-validate.txt
  ```

---

## Success criteria
- 0695-equivalent sandbox resume cannot crash due to empty manifest list.
- Status and validation outputs are consistent with the logs and artifacts (no more "done" while a real traceback occurred).
- d8f5-equivalent refresh runs remain "done"; shutdown artifacts do not cause false failures.
