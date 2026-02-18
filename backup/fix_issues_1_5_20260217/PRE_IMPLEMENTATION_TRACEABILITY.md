# Pre-Implementation Traceability - Next Phase (Issues #1-#5)
Date: 2026-02-17
Backup Folder: `backup/fix_issues_1_5_20260217/`
Scope: prepare and trace all upcoming fixes for Issues #1, #2, #3, #4, #5.

## Files Backed Up Before Any New Edits
- `control_plane/run_product_list_refresh.py`
- `control_plane/worker.py`
- `dashboard/chat_panel.py`
- `control_plane/chat_orchestrator.py`

## Steps/Sequences Confirmed Working (Baseline)
1. Product-list refresh runner executes and writes sandbox outputs (`linking_map`, `amazon_cache`, `processing_state`).
2. Worker moves jobs through lifecycle directories and writes status JSON.
3. Dashboard pending-tool parameter editing flow works for currently supported phrase patterns.
4. Previously implemented fixes (#6 and #7) are present in code:
   - processing_state top-level sync in `control_plane/run_product_list_refresh.py`
   - status `refresh.counts` recomputation and object-shaped input counting in `control_plane/worker.py`

## Steps/Sequences Not Working Correctly (To Fix Next)

### Issue #1 - Missing JSON Pre-Validation
- File: `control_plane/run_product_list_refresh.py`
- Current behavior: `_load_products_from_subset` calls `read_json` directly (`control_plane/run_product_list_refresh.py:145`), malformed JSON crashes run with traceback.
- Expected behavior: catch malformed/invalid schema early and raise clear operator-facing error before processing starts.

### Issue #2 - No Dedup/Resume for Product Refresh
- File: `control_plane/run_product_list_refresh.py`
- Current behavior:
  - `results` starts empty (`control_plane/run_product_list_refresh.py:187`)
  - no preload of existing linking map
  - no skip when corresponding `amazon_cache` already exists
  - per-run state pointer initialization can restart category progress.
- Expected behavior: optional resume path that reuses existing artifacts and skips already-processed products safely.

### Issue #3 - Duplicate Job File Risk (done/failed)
- File: `control_plane/worker.py`
- Current behavior: `_move_job` uses `os.replace` directly (`control_plane/worker.py:83-87`) with no explicit stale/duplicate detection metrics.
- Expected behavior: deterministic duplicate-safe move semantics and explicit handling/logging when destination already exists.

### Issue #4 - Fragile Natural-Language Parsing for Limits
- Files: `dashboard/chat_panel.py`, `control_plane/chat_orchestrator.py`
- Current behavior: only specific regex shapes are parsed for `max_products` and `max_products_per_category`; many natural phrasings still miss.
- Expected behavior: broader but safe parsing coverage without changing unrelated chat behavior.

### Issue #5 - `financial_report_exists` Is Too Broad
- File: `control_plane/worker.py`
- Current behavior: boolean checks directory existence only (`control_plane/worker.py:147-149`).
- Expected behavior: report existence should be run/sandbox scoped to avoid false positives.

## Planned Patches (Diff Intent + Behavior Expectations)

### Patch Set A - `control_plane/run_product_list_refresh.py`
1. Add input pre-validation path for malformed JSON and invalid schema shape.
   - Intent: convert opaque JSON decode crashes into clear fatal messages.
   - Expected behavior: fast-fail with explicit reason, no partial writes from invalid input.
2. Add resume/dedup mode:
   - preload existing linking map rows when present
   - skip products with existing completed mapping or existing `amazon_cache` file
   - preserve pointer semantics for already-processed categories.
   - Expected behavior: reruns avoid redundant extraction and unnecessary overwrites.

### Patch Set B - `control_plane/worker.py`
1. Harden `_move_job` with duplicate-safe semantics and explicit destination handling.
   - Intent: prevent ambiguous artifacts where same run appears in multiple lifecycle dirs.
   - Expected behavior: deterministic final location with clear overwrite/rename policy and logs.
2. Make `financial_report_exists` run-scoped.
   - Intent: avoid always-true indicator from shared directory existence.
   - Expected behavior: status reflects actual reports for current run/sandbox only.

### Patch Set C - `dashboard/chat_panel.py` and `control_plane/chat_orchestrator.py`
1. Expand NL regex coverage for limits while preserving existing patterns.
   - Intent: parse common user phrasings like "at most X", "no more than X", "per category limit X".
   - Expected behavior: fewer false "pending action" loops and fewer manual retries.

## Rollback Notes
To rollback next-phase edits, restore from this folder:
- `backup/fix_issues_1_5_20260217/run_product_list_refresh.py`
- `backup/fix_issues_1_5_20260217/worker.py`
- `backup/fix_issues_1_5_20260217/chat_panel.py`
- `backup/fix_issues_1_5_20260217/chat_orchestrator.py`

## Safety Constraints (Re-affirmed)
- No secrets/credentials touched.
- Protected files (`tools/configurable_supplier_scraper.py`, `run_custom_*.py`) remain untouched.
- Triangulation rule remains in effect for verification claims.

## Patch Execution Log (Applied)

### Applied on 2026-02-17
1. `control_plane/run_product_list_refresh.py`
   - Added strict subset input validation with explicit JSON/schema errors.
   - Added resume/dedup preload from existing linking map.
   - Added identity-based skip for already-processed products.
   - Updated state counters to start from preloaded results and clamp "needing_analysis" to non-negative values.

2. `control_plane/worker.py`
   - Hardened `_move_job` to avoid silent destination overwrite by writing duplicate-safe filename suffixes.
   - Added run-scoped financial report detection based on CSV modification times relative to run start.

3. `control_plane/chat_orchestrator.py`
   - Expanded runtime limit parsing for additional natural-language variants (`up to`, `at most`, `no more than`, `process/run/check N products`, `N products max`, `unlimited`).

4. `dashboard/chat_panel.py`
   - Expanded pending-action limit edit parsing with the same broader phrase coverage used by orchestrator.

## Post-Apply Verification Notes
- Hephaestus task `bg_8d4f20e8` returned with no session messages (`status: cancelled` in task output), so no extra deep-agent evidence was produced in this cycle.
- Local validation for these new patches is pending execution (next step: targeted checks for refresh resume/dedup, worker move behavior, and limit parsing paths).

### Local checks executed
- `python -m py_compile control_plane/run_product_list_refresh.py control_plane/worker.py control_plane/chat_orchestrator.py dashboard/chat_panel.py` (pass)
- Targeted smoke checks run via inline Python:
  - runtime-constraint phrase parsing (`set max products to`, `up to`, `N products max`, `unlimited`) (pass)
  - subset JSON validation raises explicit `RuntimeError` for malformed JSON (pass)
  - `_move_job` duplicate-safe rename behavior (pass)
  - run-scoped financial report detection by CSV mtime threshold (pass)
