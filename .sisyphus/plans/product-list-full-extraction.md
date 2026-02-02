# Product List Refresh: Full Amazon Extraction Parity

## TL;DR

> **Quick Summary**: Fix the product-list refresh workflow to use `FixedAmazonExtractor` (same as main workflow) instead of custom inline regex extraction, enabling full Keepa data capture and successful financial report generation.
> 
> **Deliverables**:
> - Fixed `repo_root` path resolution (1-line fix)
> - FixedAmazonExtractor integration replacing inline extraction
> - Full amazon_cache schema with Keepa/SellerAmp data
> - Per-product error handling for resilience
> - `created_at` timestamp in linking map entries
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential (single file modification)
> **Critical Path**: Fix 1 (repo_root) -> Fix 2 (extractor integration) -> Fix 3 (linking map) -> Test

---

## Context

### Original Request
Fix the product-list refresh workflow so it produces amazon_cache files with full Keepa data (like the main workflow), enabling the existing FBA_Financial_calculator to generate reports without modification.

### Interview Summary
**Key Discussions**:
- User chose **Option B: Full parity extraction** over minimal/wrapper approaches
- User emphasized: **NEVER modify main workflow scripts** - changes isolated to `control_plane/`
- Run `run_angelwholesale_mixed_6` failed due to: wrong `repo_root` + minimal amazon_cache schema

**Research Findings**:
- **Amazon Extractor Schema**: 50+ fields, Keepa at lines 1267-1515, timing 5s+7s wait
- **Linking Map Schema**: Financial calculator only reads 3 fields - schema is COMPATIBLE
- **Workflow Integration**: Category analysis uses `FixedAmazonExtractor`; product-list uses inline regex

### Metis Review
**Identified Gaps** (addressed):
- Error handling per-product: Added try-except around extraction loop
- `created_at` field missing: Added to linking map entries
- AI client not required: FixedAmazonExtractor works without it (line 79 note)

---

## Work Objectives

### Core Objective
Replace the custom inline Amazon extraction in `run_product_list_refresh.py` with `FixedAmazonExtractor` from the main workflow, achieving full data parity.

### Concrete Deliverables
- Modified `control_plane/run_product_list_refresh.py` (~100 lines changed)
- Amazon cache files with full Keepa data structure
- Linking map entries with `created_at` timestamps
- Financial reports generated successfully via existing calculator

### Definition of Done
- [ ] `repo_root` resolves to project root (not `control_plane/`)
- [ ] Amazon cache files contain `keepa.product_details_tab_data` with fee fields
- [ ] Linking map entries have `created_at` ISO timestamp
- [ ] FBA_Financial_calculator runs without errors
- [ ] No modifications to forbidden files

### Must Have
- Import and use `FixedAmazonExtractor` from `tools/amazon_playwright_extractor.py`
- Preserve existing atomic write patterns (`write_json_atomic`)
- Preserve existing backup mechanism (`_backup_existing`)
- Per-product try-except for resilience (single failure doesn't crash job)
- Same browser connection pattern (CDP port 9222)

### Must NOT Have (Guardrails)
- **DO NOT modify** `tools/passive_extraction_workflow_latest.py`
- **DO NOT modify** `tools/amazon_playwright_extractor.py`
- **DO NOT modify** `tools/FBA_Financial_calculator.py`
- **DO NOT add** resume/checkpoint logic (stateless refresh only)
- **DO NOT add** parallel processing (sequential extraction)
- **DO NOT change** job payload schema (backward compatibility)
- **DO NOT introduce** new dependencies beyond existing imports

---

## Verification Strategy (MANDATORY)

### Test Decision
- **Infrastructure exists**: YES (pytest available)
- **User wants tests**: Manual verification via test run
- **Framework**: Bash/Python verification commands

### Automated Verification (Agent-Executable)

Each acceptance criterion is verifiable by running commands:

**Verification Command Suite:**
```bash
# 1. Verify repo_root fix
python -c "from pathlib import Path; p=Path('control_plane/run_product_list_refresh.py').resolve(); print('PASS' if p.parent.parent.name != 'control_plane' else 'FAIL')"

# 2. Verify FixedAmazonExtractor import
grep -c "from tools.amazon_playwright_extractor import FixedAmazonExtractor" control_plane/run_product_list_refresh.py

# 3. Verify no forbidden file modifications
git diff --name-only | grep -E "(passive_extraction_workflow|amazon_playwright_extractor|FBA_Financial)" || echo "PASS: No forbidden modifications"

# 4. After test run - verify amazon_cache schema
python -c "import json,glob; f=glob.glob('OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_*.json')[-1]; d=json.load(open(f)); print('keepa' in d and 'product_details_tab_data' in d.get('keepa',{}))"

# 5. After test run - verify linking map created_at
python -c "import json; d=json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk__sandbox__test/linking_map.json')); print(all('created_at' in e for e in d if isinstance(e, dict)))"
```

---

## Execution Strategy

### Sequential Execution (No Parallelization)

This is a single-file modification with logical dependencies:

```
Step 1: Fix repo_root (line 178)
    |
    v
Step 2: Add FixedAmazonExtractor import and instantiation
    |
    v
Step 3: Replace inline extraction with extractor calls
    |
    v
Step 4: Add per-product error handling
    |
    v
Step 5: Add created_at to linking map entries
    |
    v
Step 6: Test end-to-end
```

### Dependency Matrix

| Task | Depends On | Blocks |
|------|------------|--------|
| 1 (repo_root) | None | 2, 3, 4, 5 |
| 2 (import) | 1 | 3 |
| 3 (extraction) | 1, 2 | 4, 5 |
| 4 (error handling) | 3 | 5 |
| 5 (created_at) | 4 | 6 |
| 6 (test) | All above | None |

---

## TODOs

### Task 1: Fix repo_root Path Resolution

- [ ] 1. Fix repo_root to point to project root

  **What to do**:
  - Change line 178 from `.parent` to `.parent.parent`
  - This single character change fixes all output path resolution

  **Must NOT do**:
  - Do not change any other path resolution logic
  - Do not add additional path manipulation

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single-line change, trivial complexity
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commit after change
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Not UI work

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Step 1)
  - **Blocks**: Tasks 2, 3, 4, 5, 6
  - **Blocked By**: None

  **References**:
  - `control_plane/run_product_list_refresh.py:178` - Current buggy line: `repo_root = Path(__file__).resolve().parent`
  - `run_custom_poundwholesale.py:61-62` - Reference pattern using `Path(__file__).resolve().parent` (works because file is in repo root)

  **Acceptance Criteria**:
  ```bash
  # Agent runs:
  python -c "
  from pathlib import Path
  import sys
  sys.path.insert(0, '.')
  # Simulate the fixed logic
  repo_root = Path('control_plane/run_product_list_refresh.py').resolve().parent.parent
  print(f'repo_root: {repo_root}')
  print(f'OUTPUTS exists: {(repo_root / \"OUTPUTS\").exists()}')
  "
  # Assert: OUTPUTS exists: True
  ```

  **Commit**: YES
  - Message: `fix(control_plane): correct repo_root path resolution in product-list refresh`
  - Files: `control_plane/run_product_list_refresh.py`
  - Pre-commit: N/A (syntax check only)

---

### Task 2: Add FixedAmazonExtractor Import and Instantiation

- [ ] 2. Import and instantiate FixedAmazonExtractor

  **What to do**:
  - Add import statement at top of file: `from tools.amazon_playwright_extractor import FixedAmazonExtractor`
  - Instantiate extractor before the async `run()` function
  - Call `extractor.connect()` at start of product loop

  **Must NOT do**:
  - Do not modify `amazon_playwright_extractor.py`
  - Do not pass AI client (not required)
  - Do not change constructor signature expectations

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Import + instantiation, straightforward
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commit
  - **Skills Evaluated but Omitted**:
    - `playwright`: Not browser automation work in this task

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Step 2)
  - **Blocks**: Task 3
  - **Blocked By**: Task 1

  **References**:
  - `tools/amazon_playwright_extractor.py:1729` - FixedAmazonExtractor class definition
  - `tools/amazon_playwright_extractor.py:1748-1752` - Constructor: `def __init__(self, chrome_debug_port: int = 9222, ai_client: Optional[OpenAI] = None)`
  - `tools/passive_extraction_workflow_latest.py:1813` - Reference instantiation pattern: `self.amazon_extractor = FixedAmazonExtractor(chrome_debug_port=cdp_port)`
  - `control_plane/run_product_list_refresh.py:153-162` - Existing `_ensure_playwright_page()` browser setup

  **Acceptance Criteria**:
  ```bash
  # Agent runs:
  grep -n "from tools.amazon_playwright_extractor import FixedAmazonExtractor" control_plane/run_product_list_refresh.py
  # Assert: Returns line number (import exists)
  
  grep -n "FixedAmazonExtractor(" control_plane/run_product_list_refresh.py
  # Assert: Returns line number(s) (instantiation exists)
  ```

  **Commit**: NO (group with Task 3)

---

### Task 3: Replace Inline Extraction with FixedAmazonExtractor Calls

- [ ] 3. Replace custom inline extraction with extractor method calls

  **What to do**:
  - Remove inline extraction functions: `_first_result_asin`, `_extract_title`, `_extract_price` (lines 72-91)
  - Remove `_minimal_amazon_payload` function (lines 94-113)
  - Replace the extraction logic in `run()` (lines 229-292) with:
    ```python
    extraction_result = await extractor.search_by_ean_and_extract_data(
        ean=ean,
        supplier_title=title,
        page=page
    )
    ```
  - Write full extraction result to amazon_cache instead of minimal payload

  **Must NOT do**:
  - Do not modify FixedAmazonExtractor class
  - Do not change the method signature expectations
  - Do not skip the stabilization waits (built into extractor)

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Significant code replacement requiring careful integration
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commit
  - **Skills Evaluated but Omitted**:
    - `playwright`: Extractor handles browser automation internally

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Step 3)
  - **Blocks**: Tasks 4, 5
  - **Blocked By**: Tasks 1, 2

  **References**:
  - `tools/amazon_playwright_extractor.py:2326-2400` - `search_by_ean_and_extract_data()` method
  - `tools/amazon_playwright_extractor.py:317-450` - Full extraction schema returned
  - `control_plane/run_product_list_refresh.py:229-292` - Current inline extraction to replace
  - `control_plane/run_product_list_refresh.py:94-113` - `_minimal_amazon_payload` to remove

  **Acceptance Criteria**:
  ```bash
  # Agent runs:
  grep -c "_minimal_amazon_payload" control_plane/run_product_list_refresh.py
  # Assert: Returns 0 (function removed)
  
  grep -c "search_by_ean_and_extract_data" control_plane/run_product_list_refresh.py
  # Assert: Returns >= 1 (extractor method used)
  
  grep -c "_first_result_asin" control_plane/run_product_list_refresh.py
  # Assert: Returns 0 (inline function removed)
  ```

  **Commit**: YES
  - Message: `feat(control_plane): integrate FixedAmazonExtractor for full Keepa data extraction`
  - Files: `control_plane/run_product_list_refresh.py`
  - Pre-commit: `python -m py_compile control_plane/run_product_list_refresh.py`

---

### Task 4: Add Per-Product Error Handling

- [ ] 4. Wrap extraction loop with try-except per product

  **What to do**:
  - Add try-except around each product's extraction in the loop
  - On exception, log error and append a failed result to results list
  - Continue to next product instead of crashing entire job

  **Must NOT do**:
  - Do not add retry logic with exponential backoff
  - Do not add circuit breaker logic
  - Do not silence all errors (log them)

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple try-except wrapper
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commit
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Step 4)
  - **Blocks**: Task 5
  - **Blocked By**: Task 3

  **References**:
  - `tools/passive_extraction_workflow_latest.py:3280-3370` - Error handling pattern in main workflow
  - `control_plane/run_product_list_refresh.py:203-307` - Current product loop without try-except

  **Acceptance Criteria**:
  ```bash
  # Agent runs:
  grep -c "except Exception" control_plane/run_product_list_refresh.py
  # Assert: Returns >= 1 (error handling exists)
  
  grep -A2 "except Exception" control_plane/run_product_list_refresh.py | grep -c "continue"
  # Assert: Returns >= 1 (continues to next product)
  ```

  **Commit**: NO (group with Task 5)

---

### Task 5: Add created_at to Linking Map Entries

- [ ] 5. Add `created_at` timestamp to all linking map entries

  **What to do**:
  - Add `"created_at": _utc_now_iso()` to each result appended in the loop
  - Ensure both success and failure entries have timestamps

  **Must NOT do**:
  - Do not change linking map file path or naming
  - Do not add other fields beyond `created_at`

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single field addition to dict construction
  - **Skills**: [`git-master`]
    - `git-master`: For atomic commit
  - **Skills Evaluated but Omitted**:
    - None relevant

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Step 5)
  - **Blocks**: Task 6
  - **Blocked By**: Task 4

  **References**:
  - `control_plane/run_product_list_refresh.py:14-15` - Existing `_utc_now_iso()` helper
  - `tools/passive_extraction_workflow_latest.py:3318` - Main workflow adds `created_at` to linking entries
  - `control_plane/run_product_list_refresh.py:294-306` - Current result dict construction (missing created_at)

  **Acceptance Criteria**:
  ```bash
  # Agent runs:
  grep -c '"created_at"' control_plane/run_product_list_refresh.py
  # Assert: Returns >= 3 (multiple entry types have created_at)
  ```

  **Commit**: YES
  - Message: `fix(control_plane): add error handling and created_at timestamp to product-list refresh`
  - Files: `control_plane/run_product_list_refresh.py`
  - Pre-commit: `python -m py_compile control_plane/run_product_list_refresh.py`

---

### Task 6: End-to-End Test Run

- [ ] 6. Execute test run and verify outputs

  **What to do**:
  - Create a minimal test product list (2-3 products with known EANs)
  - Run the product-list refresh workflow
  - Verify amazon_cache files have full Keepa schema
  - Verify linking map has `created_at` fields
  - Verify FBA_Financial_calculator completes without errors

  **Must NOT do**:
  - Do not run on full production data for initial test
  - Do not skip verification steps

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Multi-step verification requiring browser automation
  - **Skills**: [`playwright`]
    - `playwright`: For browser-based verification if needed
  - **Skills Evaluated but Omitted**:
    - `git-master`: No commits in this task

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Final Step)
  - **Blocks**: None (completion)
  - **Blocked By**: All previous tasks

  **References**:
  - `OUTPUTS/CONTROL_PLANE/inputs/products_subset_angelwholesale_mixed_6.json` - Existing test input file
  - `control_plane/worker.py:190-194` - How worker invokes product-list refresh
  - `tools/FBA_Financial_calculator.py:77-132` - What financial calculator reads from linking map

  **Acceptance Criteria**:

  **Pre-run setup:**
  ```bash
  # Ensure Chrome is running with debug port
  # Agent verifies:
  curl -s http://localhost:9222/json/version | grep -q "Browser"
  # Assert: Exit code 0 (Chrome accessible)
  ```

  **After test run - Amazon cache verification:**
  ```bash
  # Agent runs:
  python -c "
  import json
  import glob
  
  # Find most recent amazon cache file
  files = sorted(glob.glob('OUTPUTS/FBA_ANALYSIS/amazon_cache/amazon_*.json'), key=lambda f: open(f).read())
  if not files:
      print('FAIL: No amazon cache files')
      exit(1)
  
  # Check schema of latest file
  with open(files[-1]) as f:
      data = json.load(f)
  
  required = ['asin', 'keepa', 'scraped_at']
  missing = [k for k in required if k not in data]
  
  if missing:
      print(f'FAIL: Missing fields: {missing}')
      exit(1)
  
  # Check Keepa has product_details_tab_data
  keepa = data.get('keepa', {})
  if 'product_details_tab_data' not in keepa and keepa.get('status') != 'Extraction process completed':
      print('WARN: Keepa data may be incomplete (extension not loaded?)')
  
  print('PASS: Amazon cache schema valid')
  "
  ```

  **After test run - Linking map verification:**
  ```bash
  # Agent runs:
  python -c "
  import json
  import glob
  
  # Find sandbox linking map
  maps = glob.glob('OUTPUTS/FBA_ANALYSIS/linking_maps/*__sandbox__*/linking_map.json')
  if not maps:
      print('FAIL: No sandbox linking maps found')
      exit(1)
  
  with open(maps[-1]) as f:
      entries = json.load(f)
  
  if not entries:
      print('FAIL: Linking map empty')
      exit(1)
  
  missing_timestamp = [i for i, e in enumerate(entries) if 'created_at' not in e]
  if missing_timestamp:
      print(f'FAIL: Entries missing created_at: {missing_timestamp}')
      exit(1)
  
  print(f'PASS: Linking map has {len(entries)} entries, all with created_at')
  "
  ```

  **After test run - Financial calculator verification:**
  ```bash
  # Agent runs:
  python -c "
  from tools.FBA_Financial_calculator import run_calculations
  import glob
  
  # Get sandbox supplier name from linking map path
  maps = glob.glob('OUTPUTS/FBA_ANALYSIS/linking_maps/*__sandbox__*/linking_map.json')
  if not maps:
      print('FAIL: No sandbox linking maps')
      exit(1)
  
  import os
  sandbox_supplier = os.path.basename(os.path.dirname(maps[-1]))
  print(f'Running calculations for: {sandbox_supplier}')
  
  try:
      run_calculations(sandbox_supplier)
      print('PASS: Financial calculator completed')
  except Exception as e:
      print(f'FAIL: Financial calculator error: {e}')
      exit(1)
  "
  ```

  **Evidence to Capture:**
  - [ ] Screenshot or log of amazon_cache file with Keepa data
  - [ ] Linking map JSON showing `created_at` fields
  - [ ] Financial report CSV in `OUTPUTS/FBA_ANALYSIS/financial_reports/`

  **Commit**: NO (verification only)

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(control_plane): correct repo_root path resolution` | run_product_list_refresh.py | py_compile |
| 3 | `feat(control_plane): integrate FixedAmazonExtractor` | run_product_list_refresh.py | py_compile |
| 5 | `fix(control_plane): add error handling and created_at` | run_product_list_refresh.py | py_compile |

---

## Success Criteria

### Verification Commands
```bash
# 1. No forbidden files modified
git diff --name-only | grep -E "(passive_extraction|amazon_playwright_extractor|FBA_Financial)" || echo "PASS"

# 2. Import exists
grep "FixedAmazonExtractor" control_plane/run_product_list_refresh.py

# 3. Minimal payload removed
grep "_minimal_amazon_payload" control_plane/run_product_list_refresh.py || echo "PASS: Removed"

# 4. Test run produces valid outputs
python -c "import json; print(json.load(open('OUTPUTS/FBA_ANALYSIS/linking_maps/test_sandbox/linking_map.json'))[0].keys())"
```

### Final Checklist
- [ ] `repo_root` resolves correctly (OUTPUTS exists at path)
- [ ] FixedAmazonExtractor imported and instantiated
- [ ] Inline extraction functions removed
- [ ] Amazon cache files have full Keepa schema
- [ ] Linking map entries have `created_at`
- [ ] Per-product error handling implemented
- [ ] FBA_Financial_calculator runs successfully
- [ ] **NO modifications** to forbidden files (passive_extraction, amazon_playwright_extractor, FBA_Financial_calculator)
