# Browser Connection & Linking Map Resolution Plan

## TL;DR

> **Quick Summary**: Clean up the `linking_map.json` using a dedicated Python utility, fix the misleading `match_method` logging in the refresh script, and remove the destructive inline connection-restart logic from `BrowserManager.get_page()` while preserving the HTTP-tab preference to prevent hidden-tab latching.
> 
> **Deliverables**: 
> - Standalone linking map cleanup script (`utils/clean_linking_map.py`)
> - Updated `utils/browser_manager.py` (removing inline restart, keeping HTTP preference)
> - Updated `control_plane/run_product_list_refresh.py` (accurately recording `_search_method_used`)
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 2 waves
> **Critical Path**: Task 1 (Cleanup Utility) & Task 2 (Browser Fix) -> Task 3 (Refresh Script Fix)

---

## Context

### Original Request
User reported the previous linking map cleanup failed (bash script threw exceptions) and the browser tab latching fixes worsened crashing. Explicit instructions given: manual testing will be conducted by the user, revert unnecessary browser fixes but retain the HTTP-tab preference, and clean the linking map immediately.

### Interview Summary
**Key Discussions**:
- **Linking Map Issue**: The previous agent attempted to clean `linking_map.json` using a bash heredoc Python script, which crashed because it failed to resolve the correct sandbox paths.
- **Browser Issue**: `BrowserManager.get_page()` was previously modified to prefer HTTP/HTTPS tabs to avoid Chrome extension background pages (the "hidden tab" issue). However, the page selection was also wrapped in a `verify_connection_health` loop that attempts to restart the connection *inline* if a page closes. This inline restart conflicts with the external Chrome instance and `BrowserCircuitBreaker`, causing a cascade of "Target page, context or browser has been closed" errors.
- **Verification**: The user will manually test the fixes by running the script; no automated test infrastructure is to be built.

---

## Work Objectives

### Core Objective
Resolve the browser crashing caused by inline health-check restarts, ensure the system only latches onto visible user tabs, accurately log the Amazon extraction method in the linking map during product list refreshes, and cleanly purge foreign entries from the linking map.

### Concrete Deliverables
- `utils/clean_linking_map.py` (New utility script)
- `utils/browser_manager.py` (Modified)
- `control_plane/run_product_list_refresh.py` (Modified)

### Definition of Done
- [ ] `utils/clean_linking_map.py` successfully reads a linking map and product list, filters out entries not in the product list, and overwrites the linking map.
- [ ] `utils/browser_manager.py`'s `get_page()` method only iterates `context.pages`, prefers HTTP/HTTPS URLs, and does *not* contain `verify_connection_health` or connection-restart logic.
- [ ] `control_plane/run_product_list_refresh.py` captures the actual `_search_method_used` from the Amazon extractor and writes that to the `linking_map.json` instead of hardcoding "EAN".

### Must Have
- [ ] Explicit backups created for all modified files using the standard `backup/<reason>_<YYYYMMDD>/` protocol before editing.
- [ ] `REVERT_TRACKING.md` updated in the backup folder.
- [ ] All file changes must be surgical and minimal.

### Must NOT Have (Guardrails)
- [ ] Do NOT build automated tests (pytest, etc.) per user direction.
- [ ] Do NOT edit `tools/passive_extraction_workflow_latest.py`, `tools/configurable_supplier_scraper.py`, or `run_custom_*.py` files.
- [ ] Do NOT use bash one-liners for the linking map cleanup.

---

## Verification Strategy (MANDATORY)

> **USER DIRECTED MANUAL VERIFICATION** — Automated test infrastructure is excluded by user request. However, Agent-Executed QA must still be performed to verify the *mechanics* of the changes before handoff.

### Test Decision
- **Infrastructure exists**: YES (pytest)
- **Automated tests**: None requested by user
- **Agent-Executed QA**: YES. The executing agent must run the new utility script and perform dry-run validation of the Python syntax for the modified scripts.

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately — Utilities & Core Fixes):
├── Task 1: Create Linking Map Cleanup Utility [quick]
└── Task 2: Fix BrowserManager get_page Logic [deep]

Wave 2 (After Wave 1 — Refresh Script):
└── Task 3: Fix Match Method Logging in Refresh Script [unspecified-high]

Wave FINAL:
├── Task F1: Plan compliance audit (oracle)
├── Task F2: Code quality review (unspecified-high)
└── Task F4: Scope fidelity check (deep)

Critical Path: Task 1 -> Task 2 -> Task 3 -> F1-F4
Max Concurrent: 2
```

### Dependency Matrix

| Task | Depends On | Blocks | Wave |
|------|------------|--------|------|
| 1 | — | — | 1 |
| 2 | — | 3 | 1 |
| 3 | 2 | F1-F4 | 2 |

### Agent Dispatch Summary

| Wave | # Parallel | Tasks → Agent Category |
|------|------------|----------------------|
| 1 | **2** | T1 → `quick`, T2 → `deep` |
| 2 | **1** | T3 → `unspecified-high` |
| FINAL | **3** | F1 → `oracle`, F2 → `unspecified-high`, F4 → `deep` |

---

## TODOs

- [ ] 1. **Create Linking Map Cleanup Utility**

  **What to do**:
  - Create a new file: `utils/clean_linking_map.py`
  - The script should take three arguments: `--product-list` (path to JSON), `--linking-map` (path to JSON), and `--dry-run` (boolean, default True).
  - Logic: Load product list, extract all valid URLs. Load linking map. Filter linking map to keep only entries where `supplier_url` matches a valid URL from the product list.
  - If `--dry-run` is False, write the filtered dictionary back to the linking map path atomically (using `json.dump` to a temp file, then `os.replace`).
  - Print clear summary statistics: Total Loaded, Kept, Removed.
  - **Execute the script** against the failing sandbox:
    - Product List: `OUTPUTS/PRODUCTS_LISTS/efghousewares_rerun_contaminated.json`
    - Linking Map: `OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__4e269fb4/linking_map.json`
    - Run it first with `--dry-run`, then run it for real to clean the file.

  **Must NOT do**:
  - Do not use a bash heredoc string to execute Python. Write a proper `.py` file.

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Standalone script creation, isolated logic.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocked By**: None

  **Acceptance Criteria**:
  - [ ] `utils/clean_linking_map.py` exists.
  - [ ] `python utils/clean_linking_map.py --help` returns successfully.

  **QA Scenarios:**
  ```
  Scenario: Dry Run linking map cleanup
    Tool: Bash
    Preconditions: efghousewares_rerun_contaminated.json and the 4e269fb4 linking_map.json exist.
    Steps:
      1. Execute: python utils/clean_linking_map.py --product-list "OUTPUTS/PRODUCTS_LISTS/efghousewares_rerun_contaminated.json" --linking-map "OUTPUTS/FBA_ANALYSIS/linking_maps/efghousewares.co.uk__sandbox__4e269fb4/linking_map.json" --dry-run
      2. Verify output contains "Total Kept" and "Total Removed"
    Expected Result: Script executes without errors and does not modify the file.
    Failure Indicators: FileNotFoundError, JSONDecodeError, or file modification time changes.
    Evidence: .sisyphus/evidence/task-1-dry-run.txt
  ```

- [ ] 2. **Fix BrowserManager get_page Logic**

  **What to do**:
  - Target file: `utils/browser_manager.py`
  - Create a backup of `utils/browser_manager.py` in `backup/browser_linking_map_fix_20260404/`.
  - Update `REVERT_TRACKING.md` in the backup folder.
  - Modify `get_page(self)`:
    - **Remove** the `verify_connection_health` loop and any `restart_browser_gracefully` logic from inside this method.
    - **Keep** the HTTP/HTTPS page preference logic (lines ~268-282 from recent revert track) so it correctly selects `candidate = http_pages[0] if http_pages else (other_pages[0] if other_pages else None)`.
    - If `candidate` is None, create a new page: `await self.context.new_page()`.
  - Ensure the method simply returns a valid page from the existing context without attempting to manage the connection state if a page is closed.

  **Must NOT do**:
  - Do not remove the HTTP/HTTPS preference logic. This is required to prevent latching onto hidden extension background pages.

  **Recommended Agent Profile**:
  - **Category**: `deep`
    - Reason: Modifies core browser connectivity logic; requires careful handling of Playwright context.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocked By**: None

  **References**:
  - `utils/browser_manager.py` - Core logic.
  - `backup/product_list_state_fix_20260403/REVERT_TRACKING.md` - Documentation of the HTTP-tab preference logic.

  **Acceptance Criteria**:
  - [ ] `utils/browser_manager.py` successfully compiles (`python -m py_compile utils/browser_manager.py`).

  **QA Scenarios:**
  ```
  Scenario: Syntax Check BrowserManager
    Tool: Bash
    Preconditions: File is modified.
    Steps:
      1. Execute: python -m py_compile utils/browser_manager.py
    Expected Result: Silent success (exit code 0).
    Failure Indicators: SyntaxError.
    Evidence: .sisyphus/evidence/task-2-syntax.txt
  ```

- [ ] 3. **Fix Match Method Logging in Refresh Script**

  **What to do**:
  - Target file: `control_plane/run_product_list_refresh.py`
  - Create a backup of `control_plane/run_product_list_refresh.py` in `backup/browser_linking_map_fix_20260404/`.
  - Update `REVERT_TRACKING.md` in the backup folder.
  - Around line ~328, the script determines `match_method = "EAN" if ean else "title"`.
  - Move or update this logic to occur **after** `extractor.extract_amazon_data(...)` completes.
  - Read `extraction_result.get('_search_method_used')`.
  - If `_search_method_used` is present, use that for the `match_method` in the `linking_map_entry`.
  - Fallback to the EAN/title logic only if `_search_method_used` is missing.

  **Must NOT do**:
  - Do not change how the extraction itself is performed. Only change what is recorded in the `linking_map_entry` dictionary.

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Straightforward logic adjustment but requires careful variable scope handling within a large loop.
  - **Skills**: `[]`

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2
  - **Blocked By**: Task 2

  **References**:
  - `control_plane/run_product_list_refresh.py` - Target file.

  **Acceptance Criteria**:
  - [ ] `control_plane/run_product_list_refresh.py` successfully compiles.

  **QA Scenarios:**
  ```
  Scenario: Syntax Check Refresh Script
    Tool: Bash
    Preconditions: File is modified.
    Steps:
      1. Execute: python -m py_compile control_plane/run_product_list_refresh.py
    Expected Result: Silent success (exit code 0).
    Failure Indicators: SyntaxError.
    Evidence: .sisyphus/evidence/task-3-syntax.txt
  ```

---

## Final Verification Wave (MANDATORY — after ALL implementation tasks)

> ALL must APPROVE. Rejection → fix → re-run.

- [ ] F1. **Plan Compliance Audit** — `oracle`
  Read the plan end-to-end. Verify `utils/clean_linking_map.py` exists and was executed. Verify `utils/browser_manager.py` no longer contains inline connection health checks in `get_page()`. Verify `control_plane/run_product_list_refresh.py` uses `_search_method_used` for linking map entries. Check evidence files exist in .sisyphus/evidence/.
  Output: `Must Have [N/N] | Must NOT Have [N/N] | Tasks [N/N] | VERDICT: APPROVE/REJECT`

- [ ] F2. **Code Quality Review** — `unspecified-high`
  Run `ruff check control_plane/run_product_list_refresh.py utils/browser_manager.py utils/clean_linking_map.py`.
  Output: `Lint [PASS/FAIL] | Files [N clean/N issues] | VERDICT`

- [ ] F4. **Scope Fidelity Check** — `deep`
  Verify 1:1 — everything in spec was built (no missing), nothing beyond spec was built (no creep). Confirm no modifications were made to protected scraping or workflow files.
  Output: `Tasks [N/N compliant] | Contamination [CLEAN/N issues] | Unaccounted [CLEAN/N files] | VERDICT`

---

## Success Criteria

### Verification Commands
```bash
python -m py_compile utils/browser_manager.py
python -m py_compile control_plane/run_product_list_refresh.py
python utils/clean_linking_map.py --help
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] Syntax checks pass
- [ ] Linking map utility executed and map cleaned