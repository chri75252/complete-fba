# Post-Implementation Follow-up Fixes (Product-List + Dashboard + Observability)

## TL;DR

> **Quick Summary**: Finish the second-wave surgical fixes so product-list refresh produces the same downstream artifacts and visibility guarantees as the main workflow, while keeping category-lineage behavior unchanged and avoiding risky extraction changes.
>
> **Deliverables**:
> - Product-list refresh writes correct `match_method`, writes sandbox supplier cache first, mirrors Amazon cache into both override and canonical locations, and generates sandbox financial CSVs.
> - Worker log preserves same-`run_id` attempt history instead of overwriting it.
> - Product-list refresh emits dashboard-visible debug logs.
> - Dashboard supports explicit lineage selection (`base` vs `latest_sandbox`) and displays `effective_supplier`.
> - Session transcript JSON includes approved tool execution details (`tool`, `params`, `expected_outputs`, `result`).
> - FastAPI dashboard restores a read-only validation button that respects the current lineage selection.
>
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 4 waves + final verification wave
> **Critical Path**: T1 -> T3 -> T5/T8 coordinated API pass -> T7/T9a -> T9

---

## Context

### Original Request
- Generate the final complete comprehensible implementation plan after deeply reviewing the proposed corrections, comparing them to the existing plan, and running the result through Momus.

### Source Of Truth Used
- `.sisyphus/notepads/handoff/session_handoff.md`
- `.sisyphus/drafts/workflow-followup-analysis-20260313.md`
- `control_plane/run_product_list_refresh.py`
- `control_plane/worker.py`
- `dashboard/api.py`
- `dashboard/templates/index.html`
- `dashboard/static/js/app.js`
- `dashboard_legacy_streamlit/metrics_core.py`
- `control_plane/audit.py`
- `tools/FBA_Financial_calculator.py`
- `tools/amazon_playwright_extractor.py`

### Confirmed Root Causes
- Product-list refresh currently writes Amazon JSON only to `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache` via `control_plane/run_product_list_refresh.py:46-52` and `control_plane/run_product_list_refresh.py:389-392`.
- Product-list refresh defines `_write_supplier_cache(...)` at `control_plane/run_product_list_refresh.py:85-91` but never calls it.
- Product-list refresh sets `match_method = "EAN" if ean else "title"` before extraction at `control_plane/run_product_list_refresh.py:327-329` and never updates it from the actual extractor result.
- `tools/amazon_playwright_extractor.py:2382` emits `_search_method_used = "title"` for title fallback and `tools/amazon_playwright_extractor.py:2473` emits `_search_method_used = "EAN"` for EAN search.
- `tools/FBA_Financial_calculator.py:12` hardcodes canonical `AMAZON_SCRAPE_DIR`, while `tools/FBA_Financial_calculator.py:169-261` reads Amazon cache through helper functions that use that module constant directly.
- `tools/FBA_Financial_calculator.py:472-519` accepts `amazon_scrape_dir` but only validates/logs it; it never forwards that directory into `find_amazon_json(...)`.
- `control_plane/worker.py:343` opens `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log` in `"w"` mode, so reruns overwrite prior attempts.
- `dashboard_legacy_streamlit/metrics_core.py:462-487` only tails `logs/debug` files matching `run_custom_.*\.log` and filters by `run_custom_<normalized_supplier>`.
- `dashboard/api.py:171-176` stringifies all `metrics_data["paths"]` values and should not lose that safety guard.
- `dashboard/api.py:345-388` clears `pending_tool_call` before persisting `approval_executed`, so current transcript JSON loses approved tool params / expected outputs.

### Evidence Examples
- Bad `match_method` row: `OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk__sandbox__44b12007/linking_map.json:82`
- Corresponding override cache showing title fallback: `OUTPUTS/CONTROL_PLANE/overrides/44b12007-86f0-4c2c-a93b-dd80f10b7b9c/amazon_cache/amazon_B0BJ6M9ZYW_5063389048457.json:102`
- Product-list status showing missing artifacts: `OUTPUTS/CONTROL_PLANE/status/44b12007-86f0-4c2c-a93b-dd80f10b7b9c.json:23` and `OUTPUTS/CONTROL_PLANE/status/44b12007-86f0-4c2c-a93b-dd80f10b7b9c.json:25`

### Metis Review - Gaps Addressed
- Replaced the earlier helper-based `match_method` idea with the minimal inline expression because extractor outputs are confirmed to be `EAN` or `title` in the live code.
- Reversed the earlier "do not copy to canonical amazon_cache" guardrail because the financial calculator still reads canonical Amazon cache via hardcoded helpers.
- Revised the debug-log plan so the filename matches current dashboard discovery rules instead of inventing a new pattern that would never surface.
- Replaced the old `ui_events` accumulator plan with targeted `tool_executions` persistence only.
- Revised validation so it respects the same lineage resolution as the metrics endpoint instead of validating only the base supplier.

---

## Work Objectives

### Core Objective
Make product-list refresh operationally complete and dashboard-visible without touching protected workflow files or changing fragile category-lineage semantics.

### Concrete Deliverables
- `control_plane/run_product_list_refresh.py` emits correct `match_method`, writes supplier cache early, mirrors Amazon cache to canonical, triggers financial calculations, and mirrors logs into `logs/debug` using dashboard-compatible naming.
- `control_plane/worker.py` appends same-run logs with attempt delimiters.
- `dashboard_legacy_streamlit/metrics_core.py` can discover the latest sandbox lineage for a base supplier.
- `dashboard/api.py` supports `lineage`, exposes `effective_supplier`, preserves current path serialization, persists approved tool executions, and exposes a read-only validation endpoint.
- `dashboard/templates/index.html` adds lineage and validation controls.
- `dashboard/static/js/app.js` wires lineage selection, effective supplier display, and validation actions.

### Definition Of Done
- [ ] Product-list refresh with >=1 match creates sandbox cached-products, canonical+override Amazon cache JSON, and sandbox financial CSV.
- [ ] Linking-map `match_method` aligns with extractor `_search_method_used`.
- [ ] Reused `run_id` logs append with explicit attempt delimiters.
- [ ] Dashboard can switch between `base` and `latest_sandbox` deterministically.
- [ ] Transcript JSON includes approved tool params / expected outputs / result in the same session file.
- [ ] Validation button remains read-only and reports against the currently selected lineage.

### Must Have
- Keep all edits surgical and confined to `control_plane/*`, `dashboard/*`, and `dashboard_legacy_streamlit/*`.
- Preserve current `str()` coercion loop in `dashboard/api.py`.
- Use atomic writes for all new JSON output paths.
- Use the same transcript JSON files under `OUTPUTS/CONTROL_PLANE/transcripts/`; do not create a second transcript format.

### Must NOT Have (Guardrails)
- No edits to protected files under `tools/*` or any `run_custom_*.py`.
- No category sandbox lineage rewiring, no same-run-id lineage semantics changes, and no category-state duplication work.
- No car-accessories extraction/workflow fix.
- No naive timestamp-only dashboard file mixing across base and sandbox variants.
- No unbounded accumulation of UI trace events in transcript state.
- No change to `validate_supplier_data(...)` semantics beyond passing the right effective supplier into it.

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (repo has `pytest`, `ruff`, and related tooling configured), but this pass is best verified with tests-after plus agent-executed workflow checks.
- **Automated tests**: Tests-after / targeted checks.

### QA Policy
- Every task includes an agent-executed QA scenario.
- Evidence lands under `.sisyphus/evidence/`.
- Product-list verification must prefer sandbox suppliers / run ids used in the actual refresh, not base-supplier guesses.

---

## Execution Strategy

### Parallel Execution Waves

Wave 0 (foundation)
- T1: Backup + revert tracking

Wave 1 (core backend fixes, parallel)
- T2: Worker log append + delimiter
- T3: Product-list refresh completeness (supplier cache + dual-write + financials + match_method)
- T3b: Product-list debug log mirror
- T4: Latest sandbox lineage helper

Wave 2 (dashboard/API surfacing, parallel with coordination)
- T5: Metrics endpoint lineage support
- T6: Template lineage selector
- T7: Frontend lineage wiring + effective supplier display
- T8: Transcript tool execution persistence
- T9a: Read-only validation endpoint/button

Wave 3 (grouped verification)
- T9: Functional verification pass across refresh, logs, dashboard, transcripts, validation

Wave FINAL (independent review)
- F1: Plan compliance audit
- F2: Code quality / targeted sanity review
- F3: Real QA execution of grouped scenarios
- F4: Scope fidelity check

Critical Path: T1 -> T3 -> T5/T8 coordinated `dashboard/api.py` pass -> T7/T9a -> T9 -> F1-F4

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|---|---|---|---|
| T1 | - | T2, T3, T3b, T4, T5, T8, T9a | 0 |
| T2 | T1 | T9 | 1 |
| T3 | T1 | T9 | 1 |
| T3b | T1 | T9 | 1 |
| T4 | T1 | T5, T9a | 1 |
| T5 | T4 | T6, T7, T9a, T9 | 2 |
| T6 | T5 | T7, T9 | 2 |
| T7 | T5, T6 | T9 | 2 |
| T8 | T1 | T9 | 2 |
| T9a | T4, T5 | T9 | 2 |
| T9 | T2, T3, T3b, T5, T6, T7, T8, T9a | F1-F4 | 3 |

> Coordination note: T5, T8, and T9a all modify `dashboard/api.py`. They should be executed as one coordinated pass on that file to avoid patch drift.

---

## TODOs

- [ ] T1. Create backup root + `REVERT_TRACKING.md`

  **What to do**:
  - Create `backup/workflow_followup_fixes_20260313/`.
  - Copy every planned edit target into that backup tree.
  - Create `backup/workflow_followup_fixes_20260313/REVERT_TRACKING.md` listing file, intent, validation, and exact restore path.

  **Must NOT do**:
  - Do not back up protected `tools/*` files because they are not in scope for editing.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocks: all later tasks

  **References**:
  - `.sisyphus/notepads/handoff/session_handoff.md`
  - `.sisyphus/drafts/workflow-followup-analysis-20260313.md`

  **Acceptance Criteria**:
  - [ ] Backup directory exists.
  - [ ] Every planned edit target has a non-empty backup copy.
  - [ ] `REVERT_TRACKING.md` lists each file and revert source.

  **QA Scenario**:
  ```text
  Scenario: backup inventory exists
    Tool: Bash
    Steps:
      1. List backup/workflow_followup_fixes_20260313/
      2. Verify each planned file exists under backup.
      3. Open REVERT_TRACKING.md and confirm every planned file is listed.
    Expected Result: backup tree is complete and readable.
    Evidence: .sisyphus/evidence/T1-backup-inventory.txt
  ```

- [ ] T2. Preserve control-plane attempt logs on reused `run_id`

  **What to do**:
  - Change `control_plane/worker.py` from truncate mode to append mode for `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log`.
  - Write a delimiter line before each subprocess start containing UTC timestamp, `run_id`, and `job_type`.

  **Must NOT do**:
  - Do not change the authoritative log path.
  - Do not change final status logic unless evidence proves tail-of-log detection breaks after delimitering.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: T9

  **References**:
  - `control_plane/worker.py:341-353`
  - `control_plane/worker.py:470-523`

  **Patch Preview**:
  ```diff
  diff --git a/control_plane/worker.py b/control_plane/worker.py
  @@
  -                with open(log_path, "w", encoding="utf-8") as log_file:
  +                with open(log_path, "a", encoding="utf-8") as log_file:
  +                    log_file.write(
  +                        "\n\n===== CONTROL_PLANE ATTEMPT "
  +                        f"start={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
  +                        f"run_id={run_id} job_type={job.get('job_type')} =====\n"
  +                    )
  +                    log_file.flush()
                       env["CONTROL_PLANE_LOG_PATH"] = str(log_path)
  ```

  **Acceptance Criteria**:
  - [ ] Same-`run_id` rerun appends instead of overwriting.
  - [ ] Delimiter is visible for each attempt.
  - [ ] Final status still reflects the latest attempt outcome.

  **QA Scenarios**:
  ```text
  Scenario: append preserves old attempt
    Tool: Bash
    Steps:
      1. Run a refresh, let the log populate, then cancel.
      2. Resume using the same run_id.
      3. Open OUTPUTS/CONTROL_PLANE/logs/<run_id>.log.
      4. Confirm two delimiter headers exist and older lines remain.
    Expected Result: both attempts are present in one log.
    Evidence: .sisyphus/evidence/T2-log-append.txt

  Scenario: latest attempt drives final status
    Tool: Bash
    Steps:
      1. Create a failed first attempt.
      2. Re-run the same run_id to successful completion.
      3. Inspect OUTPUTS/CONTROL_PLANE/status/<run_id>.json.
    Expected Result: status reports the latest attempt outcome, not the stale failure.
    Evidence: .sisyphus/evidence/T2-latest-attempt-status.txt
  ```

- [ ] T3. Product-list refresh completeness (`match_method` + supplier cache + canonical bridge + financial CSV)

  **What to do**:
  1. Replace the current pre-extraction `match_method` assumption with the minimal inline post-extraction expression:
     - `match_method = extraction_result.get("_search_method_used") or ("EAN" if ean else "title")`
  2. Write the sandbox supplier cache before `asyncio.run(run())` so cached products exist before any linking-map flush.
  3. Add a canonical Amazon-cache helper and write each matched Amazon JSON to both:
     - `OUTPUTS/CONTROL_PLANE/overrides/<run_id>/amazon_cache/`
     - `OUTPUTS/FBA_ANALYSIS/amazon_cache/`
  4. Remove `amazon_scrape_dir` from the planned `run_calculations(...)` call because the current calculator does not honor it for actual reads.
  5. After refresh, call `run_calculations(sandbox_supplier, supplier_cache_path=<sandbox cache path>)` if there is at least one matched ASIN.

  **Must NOT do**:
  - Do not edit `tools/FBA_Financial_calculator.py`.
  - Do not leave a matched linking-map row behind if one of the two Amazon-cache writes failed.
  - Do not move financial logic into the worker.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: T9

  **References**:
  - `control_plane/run_product_list_refresh.py:30-52`
  - `control_plane/run_product_list_refresh.py:85-91`
  - `control_plane/run_product_list_refresh.py:322-404`
  - `control_plane/run_product_list_refresh.py:448-454`
  - `tools/FBA_Financial_calculator.py:12`
  - `tools/FBA_Financial_calculator.py:169-261`
  - `tools/FBA_Financial_calculator.py:472-519`
  - `tools/amazon_playwright_extractor.py:2382`
  - `tools/amazon_playwright_extractor.py:2473`

  **Patch Preview**:
  ```diff
  diff --git a/control_plane/run_product_list_refresh.py b/control_plane/run_product_list_refresh.py
  @@
   def _amazon_cache_path(repo_root: Path, run_id: str, asin: str, ean: str) -> Path:
       ean_safe = _sanitize_ean(ean) or "N"
       return _amazon_cache_dir(repo_root, run_id) / f"amazon_{asin}_{ean_safe}.json"
  +
  +def _canonical_amazon_cache_path(repo_root: Path, asin: str, ean: str) -> Path:
  +    ean_safe = _sanitize_ean(ean) or "N"
  +    return (
  +        repo_root / "OUTPUTS" / "FBA_ANALYSIS" / "amazon_cache" / f"amazon_{asin}_{ean_safe}.json"
  +    )
  @@
  +    if not dry_run:
  +        try:
  +            _write_supplier_cache(repo_root, sandbox_supplier, products)
  +        except Exception as e:
  +            log.warning("Failed to write sandbox supplier cache: %s", e)
  +
       try:
           asyncio.run(run())
       finally:
           _write_linking_map(repo_root, sandbox_supplier, results)
  @@
  -                    query = ean or title
  -                    match_method = "EAN" if ean else "title"
  +                    query = ean or title
  @@
                       extraction_result = await extractor.search_by_ean_and_extract_data(
                           ean=ean, supplier_product_title=title, page=page
                       )
  +                    match_method = extraction_result.get("_search_method_used") or ("EAN" if ean else "title")
  @@
                       if not dry_run:
                           out_path = _amazon_cache_path(repo_root, run_id, asin, ean)
                           out_path.parent.mkdir(parents=True, exist_ok=True)
                           write_json_atomic(out_path, extraction_result)
  +                        canonical_path = _canonical_amazon_cache_path(repo_root, asin, ean)
  +                        canonical_path.parent.mkdir(parents=True, exist_ok=True)
  +                        write_json_atomic(canonical_path, extraction_result)
  @@
           try:
               from tools.FBA_Financial_calculator import run_calculations
               supplier_cache_path = str(_supplier_cache_path(repo_root, sandbox_supplier))
               fin = run_calculations(
                   sandbox_supplier,
                   supplier_cache_path=supplier_cache_path,
               )
  ```

  **Acceptance Criteria**:
  - [ ] Linking-map `match_method` reflects actual `_search_method_used` (`title` fallback -> `title`, EAN search -> `EAN`).
  - [ ] Sandbox cached-products file is written before refresh execution begins.
  - [ ] Each matched Amazon cache JSON exists in both override and canonical locations.
  - [ ] Refresh with >=1 match creates sandbox financial CSV under `OUTPUTS/FBA_ANALYSIS/financial_reports/<sandbox-normalized>/`.
  - [ ] Product-list status eventually reports `cached_products_exists: true` and `financial_report_exists: true`.

  **QA Scenarios**:
  ```text
  Scenario: title fallback never reports EAN
    Tool: Bash
    Steps:
      1. Run a non-dry-run product-list refresh on a subset known to include at least one title fallback.
      2. Open the matched override JSON and confirm `_search_method_used` is `title`.
      3. Open the sandbox linking_map row for the same ASIN and confirm `match_method` is `title`.
    Expected Result: no `EAN` label appears for title-fallback rows.
    Evidence: .sisyphus/evidence/T3-match-method.txt

  Scenario: dual-write + financial CSV complete
    Tool: Bash
    Steps:
      1. Run a refresh to completion.
      2. Confirm sandbox cache exists in OUTPUTS/cached_products/.
      3. Confirm the same ASIN/EAN JSON exists in override and canonical amazon_cache locations.
      4. Confirm sandbox CSV exists in OUTPUTS/FBA_ANALYSIS/financial_reports/<sandbox-normalized>/.
      5. Inspect OUTPUTS/CONTROL_PLANE/status/<run_id>.json for `cached_products_exists` and `financial_report_exists`.
    Expected Result: all required artifacts exist and status reflects them.
    Evidence: .sisyphus/evidence/T3-artifact-completeness.txt
  ```

- [ ] T3b. Mirror product-list logs into `logs/debug` using dashboard-compatible naming

  **What to do**:
  - Add `_setup_debug_log(...)` in `control_plane/run_product_list_refresh.py`.
  - Create a second file handler under `logs/debug/` using a filename that still matches dashboard discovery, for example:
    - `run_custom_<sandbox-normalized>__product_list_refresh_<timestamp>.log`
  - Set handler level/formatter and ensure root logger level is at least `INFO` so existing `log.info(...)` lines are captured.
  - Call helper once after `repo_root` and `sandbox_supplier` are known.

  **Must NOT do**:
  - Do not replace the authoritative control-plane log in `OUTPUTS/CONTROL_PLANE/logs/`.
  - Do not invent a filename pattern the dashboard will never tail.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: T9

  **References**:
  - `dashboard_legacy_streamlit/metrics_core.py:462-487`
  - `control_plane/run_product_list_refresh.py:17`
  - `control_plane/run_product_list_refresh.py:278`
  - `control_plane/run_product_list_refresh.py:454`

  **Patch Preview**:
  ```diff
  diff --git a/control_plane/run_product_list_refresh.py b/control_plane/run_product_list_refresh.py
  @@
  +def _setup_debug_log(repo_root: Path, sandbox_supplier: str) -> None:
  +    import time as _time
  +    debug_dir = repo_root / "logs" / "debug"
  +    debug_dir.mkdir(parents=True, exist_ok=True)
  +    safe = sandbox_supplier.replace(".", "-").replace("/", "-")
  +    ts = _time.strftime("%Y%m%d_%H%M%S", _time.gmtime())
  +    log_file = debug_dir / f"run_custom_{safe}__product_list_refresh_{ts}.log"
  +    root = logging.getLogger()
  +    fh = logging.FileHandler(log_file, encoding="utf-8")
  +    fh.setLevel(logging.INFO)
  +    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
  +    if root.level > logging.INFO:
  +        root.setLevel(logging.INFO)
  +    root.addHandler(fh)
  @@
       sandbox_supplier = str(job.get("supplier_domain") or "")
  +    _setup_debug_log(repo_root, sandbox_supplier)
  ```

  **Acceptance Criteria**:
  - [ ] After refresh, a `logs/debug/run_custom_<sandbox-normalized>__product_list_refresh_<timestamp>.log` file exists.
  - [ ] Dashboard log panel can surface that file for the same sandbox supplier.

  **QA Scenario**:
  ```text
  Scenario: product-list debug log is discoverable
    Tool: Bash
    Steps:
      1. Run product-list refresh once.
      2. Confirm a matching log exists in logs/debug/.
      3. Open dashboard metrics for the sandbox supplier and confirm the surfaced log filename matches the new debug file.
    Expected Result: dashboard log panel can read product-list refresh logs.
    Evidence: .sisyphus/evidence/T3b-dashboard-log.txt
  ```

- [ ] T4. Add latest-sandbox lineage discovery helper

  **What to do**:
  - Add `discover_latest_sandbox_supplier(base_supplier)` to `dashboard_legacy_streamlit/metrics_core.py`.
  - Discover the newest sandbox by `processing_states` mtime only when the caller requests `latest_sandbox`.

  **Must NOT do**:
  - Do not auto-switch base metrics to sandbox silently.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  - Blocks: T5, T9a

  **References**:
  - `dashboard_legacy_streamlit/metrics_core.py:43-161`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard_legacy_streamlit/metrics_core.py b/dashboard_legacy_streamlit/metrics_core.py
  @@
   class MetricsLoader:
  +    def discover_latest_sandbox_supplier(self, base_supplier: str) -> str | None:
  +        base_supplier = (base_supplier or "").strip()
  +        if not base_supplier or "__sandbox__" in base_supplier:
  +            return base_supplier or None
  +        state_dir = os.path.join(self.base_dir, "OUTPUTS", "CACHE", "processing_states")
  +        if not os.path.exists(state_dir):
  +            return None
  +        normalized_base = base_supplier.replace(".", "_").lower()
  +        prefix = f"{normalized_base}__sandbox__"
  +        suffix = "_processing_state.json"
  +        candidates = [f for f in os.listdir(state_dir) if f.startswith(prefix) and f.endswith(suffix)]
  +        if not candidates:
  +            return None
  +        candidates.sort(key=lambda f: os.path.getmtime(os.path.join(state_dir, f)), reverse=True)
  +        sandbox_id = candidates[0][len(prefix):-len(suffix)]
  +        return f"{base_supplier}__sandbox__{sandbox_id}" if sandbox_id else None
  ```

  **Acceptance Criteria**:
  - [ ] Base supplier with sandbox states returns newest sandbox supplier hint.
  - [ ] Base supplier without sandbox states returns `None`.

  **QA Scenario**:
  ```text
  Scenario: latest sandbox resolution
    Tool: Bash
    Steps:
      1. Run a small Python one-liner that imports MetricsLoader and calls the helper.
      2. Compare returned suffix to newest processing-state mtime.
    Expected Result: helper returns deterministic latest sandbox hint.
    Evidence: .sisyphus/evidence/T4-latest-sandbox.txt
  ```

- [ ] T5. Add lineage-aware metrics endpoint while keeping current path serialization guard

  **What to do**:
  - Update `GET /api/metrics/{supplier}` in `dashboard/api.py` to accept `lineage: str = "base"`.
  - Resolve `effective_supplier` using T4 when `lineage == "latest_sandbox"`.
  - Use `effective_supplier` for `validate_supplier_data(...)` and `load_metrics(...)`.
  - Add `meta = { requested_supplier, lineage, effective_supplier }` and `paths.base_dir`.
  - Keep the existing `str()` coercion loop exactly as-is.

  **Must NOT do**:
  - Do not remove or weaken the existing path stringification loop.
  - Do not bury lineage metadata inside nested `paths` structures other than simple `base_dir`.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**:
  - Can Run In Parallel: YES (coordinated with T8/T9a on same file)
  - Parallel Group: Wave 2
  - Blocks: T6, T7, T9a, T9

  **References**:
  - `dashboard/api.py:114-180`
  - `dashboard_legacy_streamlit/metrics_core.py:654-669`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard/api.py b/dashboard/api.py
  @@
  -@app.get("/api/metrics/{supplier}")
  -def get_supplier_metrics(supplier: str):
  +@app.get("/api/metrics/{supplier}")
  +def get_supplier_metrics(supplier: str, lineage: str = "base"):
       base_dir = get_base_directory()
       try:
  +        effective_supplier = supplier
  +        if lineage == "latest_sandbox":
  +            loader = MetricsLoader(base_dir)
  +            latest = loader.discover_latest_sandbox_supplier(supplier)
  +            if latest:
  +                effective_supplier = latest
  -        issues, paths = validate_supplier_data(base_dir, supplier)
  +        issues, paths = validate_supplier_data(base_dir, effective_supplier)
  -        metrics_data = load_metrics(base_dir, supplier)
  +        metrics_data = load_metrics(base_dir, effective_supplier)
  +        metrics_data["meta"] = {
  +            "requested_supplier": supplier,
  +            "lineage": lineage,
  +            "effective_supplier": effective_supplier,
  +        }
  +        metrics_data.setdefault("paths", {})["base_dir"] = base_dir
  ```

  **Acceptance Criteria**:
  - [ ] `?lineage=base` keeps base-supplier behavior.
  - [ ] `?lineage=latest_sandbox` returns latest sandbox metrics and exposes `meta.effective_supplier`.
  - [ ] Existing path coercion still serializes response safely.

  **QA Scenario**:
  ```text
  Scenario: metrics lineage selection works
    Tool: Bash (curl)
    Steps:
      1. GET /api/metrics/<base>?lineage=base
      2. GET /api/metrics/<base>?lineage=latest_sandbox
      3. Compare meta.effective_supplier and relevant path fields.
    Expected Result: latest_sandbox resolves to sandbox-specific data source, base does not.
    Evidence: .sisyphus/evidence/T5-lineage-metrics.json
  ```

- [ ] T6. Add lineage selector to dashboard sidebar

  **What to do**:
  - Add `Data Lineage` selector in `dashboard/templates/index.html` under Configuration.
  - Options:
    - `Base (recommended)`
    - `Latest Sandbox`

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2
  - Blocks: T7, T9

  **References**:
  - `dashboard/templates/index.html:55-83`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard/templates/index.html b/dashboard/templates/index.html
  @@
                   <div class="input-group">
                       <label>Auto Refresh</label>
                       <select id="refreshInterval" class="glass-input">
  @@
                       </select>
                   </div>
  +                <div class="input-group">
  +                    <label>Data Lineage</label>
  +                    <select id="lineageSelect" class="glass-input">
  +                        <option value="base" selected>Base (recommended)</option>
  +                        <option value="latest_sandbox">Latest Sandbox</option>
  +                    </select>
  +                </div>
  ```

  **Acceptance Criteria**:
  - [ ] Sidebar renders `#lineageSelect`.

  **QA Scenario**:
  ```text
  Scenario: lineage selector renders
    Tool: Playwright
    Steps:
      1. Open dashboard.
      2. Assert `#lineageSelect` exists.
    Expected Result: selector is visible in Configuration.
    Evidence: .sisyphus/evidence/T6-lineage-selector.png
  ```

- [ ] T7. Wire lineage selector into dashboard requests and effective supplier display

  **What to do**:
  - Update `dashboard/static/js/app.js` so `fetchMetrics()` reads `lineageSelect`.
  - Request `/api/metrics/${supplier}?lineage=${lineage}`.
  - Show `effective_supplier` in the sidebar if returned.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2
  - Blocks: T9

  **References**:
  - `dashboard/static/js/app.js:46-78`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard/static/js/app.js b/dashboard/static/js/app.js
  @@
       const supplierSelect = document.getElementById('supplierSelect');
       const refreshSelect = document.getElementById('refreshInterval');
  +    const lineageSelect = document.getElementById('lineageSelect');
  @@
       async function fetchMetrics() {
           const supplier = supplierSelect.value;
  +        const lineage = lineageSelect ? lineageSelect.value : 'base';
  @@
  -        const res = await fetch(`/api/metrics/${supplier}`);
  +        const res = await fetch(`/api/metrics/${supplier}?lineage=${encodeURIComponent(lineage)}`);
  @@
  -        document.getElementById('sidebarSupplier').textContent = `Supplier: ${supplier}`;
  +        const effectiveSupplier = (data.meta && data.meta.effective_supplier) ? data.meta.effective_supplier : supplier;
  +        document.getElementById('sidebarSupplier').textContent = `Supplier: ${effectiveSupplier}`;
  ```

  **Acceptance Criteria**:
  - [ ] Changing lineage changes the API URL.
  - [ ] Sidebar updates to the resolved `effective_supplier`.

  **QA Scenario**:
  ```text
  Scenario: latest sandbox updates displayed supplier
    Tool: Playwright
    Steps:
      1. Open dashboard.
      2. Select a base supplier with sandbox artifacts.
      3. Switch Data Lineage to Latest Sandbox.
      4. Wait for refresh and inspect sidebar supplier label.
    Expected Result: sidebar includes `__sandbox__` supplier suffix.
    Evidence: .sisyphus/evidence/T7-effective-supplier.png
  ```

- [ ] T8. Persist approved tool execution details in the same session transcript JSON

  **What to do**:
  - Add `tool_executions` to `chat_state` in `dashboard/api.py`.
  - Add `_record_tool_execution(tc, result)` to capture:
    - `tool`
    - `params`
    - `expected_outputs`
    - `result`
    - `executed_at`
  - Call `_record_tool_execution(...)` immediately after `execute_tool_call(...)` and before clearing `pending_tool_call`.
  - Include `tool_executions` in `_persist_chat_session(...)` payload.
  - Clear `tool_executions` on `chat_reset`.

  **Must NOT do**:
  - Do not add a `ui_events` accumulator.
  - Do not persist every `trace_update` event separately.
  - Do not create a second transcript file type.

  **Recommended Agent Profile**:
  - Category: `unspecified-high`

  **Parallelization**:
  - Can Run In Parallel: YES (coordinated with T5/T9a on same file)
  - Parallel Group: Wave 2
  - Blocks: T9

  **References**:
  - `dashboard/api.py:50-64`
  - `dashboard/api.py:267-281`
  - `dashboard/api.py:330-388`
  - `dashboard/api.py:459-495`
  - `control_plane/audit.py:44-50`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard/api.py b/dashboard/api.py
  @@
   chat_state = {
       "messages": [],
       "scratchpad": [],
       "trace": [],
  +    "tool_executions": [],
       "pending_tool_call": None,
  @@
  +def _record_tool_execution(tc, result: dict) -> None:
  +    chat_state["tool_executions"].append({
  +        "tool": tc.name,
  +        "params": _safe_serialize(tc.params, depth=4),
  +        "expected_outputs": _safe_serialize(getattr(tc, "expected_outputs", None), depth=4),
  +        "result": _safe_serialize(result, depth=4),
  +        "executed_at": _now_iso(),
  +    })
  @@
       result = execute_tool_call(tc, repo_root)
       audit_tool_call(user_text, tc, result, rag_info)
  +    _record_tool_execution(tc, result)
  @@
       payload = {
           ...
  +        "tool_executions": _safe_serialize(chat_state.get("tool_executions") or [], depth=6),
       }
  @@
       chat_state["trace"] = []
  +    chat_state["tool_executions"] = []
  ```

  **Acceptance Criteria**:
  - [ ] `OUTPUTS/CONTROL_PLANE/transcripts/session_<id>.json` contains `tool_executions`.
  - [ ] Each approved entry includes tool, params, expected_outputs, result, and executed_at.
  - [ ] Chat reset clears the new session's tool execution history.

  **QA Scenario**:
  ```text
  Scenario: approved action appears in transcript JSON
    Tool: Bash
    Steps:
      1. Trigger one approval-needed action in the dashboard chat.
      2. Approve it.
      3. Open OUTPUTS/CONTROL_PLANE/transcripts/session_<id>.json.
      4. Inspect `tool_executions[0]`.
    Expected Result: transcript shows tool name, params, expected outputs, and result without needing chat_tool_calls.jsonl.
    Evidence: .sisyphus/evidence/T8-tool-execution-transcript.json
  ```

- [ ] T9a. Restore a read-only validation button that respects lineage selection

  **What to do**:
  - Add `GET /api/validate/{supplier}` in `dashboard/api.py`.
  - Accept `lineage: str = "base"` and resolve `effective_supplier` using the same logic as T5.
  - Call existing `validate_supplier_data(base_dir, effective_supplier)`.
  - Add light read-only checks (state readability, linking-map entry count) to the response.
  - Add a `Run Validation` button and result area in `dashboard/templates/index.html`.
  - Add JS handler in `dashboard/static/js/app.js` that sends supplier + lineage.

  **Must NOT do**:
  - Do not modify `validate_supplier_data(...)` itself.
  - Do not trigger any workflow or write any files.

  **Recommended Agent Profile**:
  - Category: `quick`

  **Parallelization**:
  - Can Run In Parallel: YES (coordinated with T5/T8 on `dashboard/api.py`)
  - Parallel Group: Wave 2
  - Blocks: T9

  **References**:
  - `dashboard/api.py:93-105`
  - `dashboard/templates/index.html:55-83`
  - `dashboard/static/js/app.js:46-78`

  **Patch Preview**:
  ```diff
  diff --git a/dashboard/api.py b/dashboard/api.py
  @@
  +@app.get("/api/validate/{supplier}")
  +def run_validation(supplier: str, lineage: str = "base"):
  +    base_dir = get_base_directory()
  +    effective_supplier = supplier
  +    if lineage == "latest_sandbox":
  +        loader = MetricsLoader(base_dir)
  +        latest = loader.discover_latest_sandbox_supplier(supplier)
  +        if latest:
  +            effective_supplier = latest
  +    issues, paths = validate_supplier_data(base_dir, effective_supplier)
  +    ...
  +    return JSONResponse({
  +        "requested_supplier": supplier,
  +        "effective_supplier": effective_supplier,
  +        "lineage": lineage,
  +        "issues": issues,
  +        "checks": checks,
  +        "paths": {k: str(v) if v else None for k, v in paths.items()},
  +        "valid": len(issues) == 0,
  +    })
  ```

  ```diff
  diff --git a/dashboard/templates/index.html b/dashboard/templates/index.html
  @@
  +                <div class="input-group">
  +                    <button id="validateBtn" class="glass-input" style="width:100%;cursor:pointer;">Run Validation</button>
  +                    <div id="validateResult" style="font-size:0.8em;margin-top:4px;"></div>
  +                </div>
  ```

  ```diff
  diff --git a/dashboard/static/js/app.js b/dashboard/static/js/app.js
  @@
  +    document.getElementById('validateBtn').addEventListener('click', async () => {
  +        const supplier = document.getElementById('supplierSelect').value;
  +        const lineage = document.getElementById('lineageSelect') ? document.getElementById('lineageSelect').value : 'base';
  +        const resultEl = document.getElementById('validateResult');
  +        resultEl.textContent = 'Validating...';
  +        const res = await fetch(`/api/validate/${encodeURIComponent(supplier)}?lineage=${encodeURIComponent(lineage)}`);
  +        ...
  +    });
  ```

  **Acceptance Criteria**:
  - [ ] Validation button returns green success for a valid selected lineage.
  - [ ] Validation button returns red issues for missing artifacts.
  - [ ] Response includes requested supplier, effective supplier, lineage, and read-only checks.

  **QA Scenarios**:
  ```text
  Scenario: validation honors lineage
    Tool: Playwright
    Steps:
      1. Select a base supplier with sandbox artifacts.
      2. Switch to Latest Sandbox.
      3. Click Run Validation.
      4. Confirm result text references sandbox-valid data instead of base-only paths.
    Expected Result: validation response matches the selected lineage.
    Evidence: .sisyphus/evidence/T9a-validation-lineage.png

  Scenario: validation remains read-only
    Tool: Bash
    Steps:
      1. Call /api/validate/<supplier>?lineage=base twice.
      2. Compare filesystem mtimes for the checked files before and after.
    Expected Result: no output files are modified.
    Evidence: .sisyphus/evidence/T9a-validation-readonly.txt
  ```

- [ ] T9. Grouped verification pass for refresh, dashboard, transcript, and validation

  **What to verify**:
  - Product-list refresh end-to-end:
    - sandbox cached-products file exists
    - override + canonical Amazon cache JSON exist
    - linking-map `match_method` aligns with extractor output
    - sandbox financial CSV exists
  - Worker append behavior for reused `run_id`
  - Dashboard lineage toggle and effective supplier display
  - Transcript `tool_executions`
  - Validation button / endpoint behavior

  **References**:
  - `OUTPUTS/CONTROL_PLANE/status/44b12007-86f0-4c2c-a93b-dd80f10b7b9c.json`
  - `OUTPUTS/CONTROL_PLANE/logs/44b12007-86f0-4c2c-a93b-dd80f10b7b9c.log`
  - `OUTPUTS/CONTROL_PLANE/transcripts/`

  **QA Scenarios**:
  ```text
  Scenario: grouped end-to-end refresh verification
    Tool: Bash
    Steps:
      1. Start worker.
      2. Enqueue a non-dry-run product-list refresh.
      3. Wait for completion.
      4. Verify sandbox cache, both Amazon-cache locations, linking_map row correctness, and financial CSV.
    Expected Result: refresh is artifact-complete.
    Evidence: .sisyphus/evidence/T9-refresh-e2e.txt

  Scenario: dashboard and validation grouped check
    Tool: Playwright
    Steps:
      1. Open dashboard.
      2. Toggle lineage to Latest Sandbox.
      3. Confirm sidebar supplier changes.
      4. Click Run Validation and confirm response is green for valid artifacts.
      5. Inspect log panel for product-list debug log visibility.
    Expected Result: dashboard surfaces lineage, validation, and logs correctly.
    Evidence: .sisyphus/evidence/T9-dashboard-grouped.png

  Scenario: transcript captures approved action
    Tool: Bash
    Steps:
      1. Trigger one approval-needed tool in chat.
      2. Approve it.
      3. Open session transcript JSON and inspect tool_executions.
    Expected Result: approved action is replayable from transcript JSON.
    Evidence: .sisyphus/evidence/T9-transcript-check.json
  ```

---

## Final Verification Wave (MANDATORY)

- [ ] F1. **Plan Compliance Audit** - `oracle`
  - Verify each Must Have exists and each Must NOT Have remains absent.
  - Confirm no protected files were edited.

- [ ] F2. **Code Quality Review** - `unspecified-high`
  - Run targeted sanity checks on changed files.
  - Check for accidental path-type regressions, duplicate log handlers, and transcript payload overreach.

- [ ] F3. **Real QA Execution** - `unspecified-high` (+ `playwright` skill for UI)
  - Execute every grouped scenario from T9.
  - Capture evidence under `.sisyphus/evidence/final-qa/`.

- [ ] F4. **Scope Fidelity Check** - `deep`
  - Confirm the diff only covers the planned files and no category-lineage / car-accessories behavior changed.

---

## Expected Outcomes / Post-Fix Behavior (and how to test)

### 1. Product-list `match_method` stops lying
- **After fix**: if the extractor falls back to title search, linking-map `match_method` is `title` even when supplier EAN exists.
- **How to test**: compare `_search_method_used` in the matched override Amazon JSON with `match_method` in the sandbox linking map.

### 2. Product-list refresh produces the same downstream artifacts it needs
- **After fix**: a successful refresh writes sandbox cached products, both Amazon-cache copies, and a sandbox financial CSV.
- **How to test**: run one non-dry-run refresh and check all four artifact families in one pass.

### 3. Same `run_id` retries remain auditable
- **After fix**: `OUTPUTS/CONTROL_PLANE/logs/<run_id>.log` contains a delimiter per attempt instead of losing earlier evidence.
- **How to test**: cancel once, rerun once, then search the log for `CONTROL_PLANE ATTEMPT`.

### 4. Dashboard tells you which lineage you are actually viewing
- **After fix**: selecting `Latest Sandbox` changes the backend source and shows the resolved sandbox supplier in the sidebar.
- **How to test**: select a base supplier with sandbox artifacts, toggle to Latest Sandbox, and confirm `effective_supplier` includes `__sandbox__`.

### 5. Session transcript JSON becomes replay-useful
- **After fix**: the transcript JSON contains approved tool calls with params, expected outputs, and result payloads, instead of only the assistant success sentence.
- **How to test**: perform one approval-needed action and inspect `tool_executions` in the saved session JSON.

### 6. Validation returns the right answer for the current lineage
- **After fix**: the validation button checks the selected lineage, not always the base supplier.
- **How to test**: toggle lineage, click validation, and inspect returned `effective_supplier` plus file checks.

---

## Success Criteria

- [ ] Product-list linking-map `match_method` never reports `EAN` when extractor used title fallback.
- [ ] Sandbox cached-products file is written before linking-map flush and is usable as the financial calculator's supplier cache input.
- [ ] Product-list matched Amazon cache JSON exists in both override and canonical locations.
- [ ] Product-list refresh generates sandbox financial CSV when >=1 product matches.
- [ ] Control-plane run log preserves attempt history for reused `run_id`.
- [ ] Product-list refresh logs appear in `logs/debug/` and are surfaced by the dashboard log panel.
- [ ] Dashboard supports explicit lineage selection and displays `effective_supplier`.
- [ ] Session transcripts contain `tool_executions` with tool name, params, expected outputs, result, and execution timestamp.
- [ ] Run Validation is read-only and respects the current lineage selection.
- [ ] No category-lineage rewiring changes and no car-accessories extraction fix were introduced.

---

Plan saved to: `.sisyphus/plans/post-implementation-followup-fixes-20260313.md`
