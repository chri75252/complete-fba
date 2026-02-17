# Product List Refresh Hardening - Complete Fix Plan

## TL;DR

> **Quick Summary**: Fix the product-list refresh pipeline completely: correct kwarg name, add extractor.connect(), fix exception scope, add logging, skip financial calc on zero matches, plus UX improvements for worker visibility.
>
> **Deliverables**:
> - Fixed `control_plane/run_product_list_refresh.py` (kwarg, connect, scope, logging, financial skip)
> - Added `products_path` validation in `control_plane/tools/product_list_refresh.py`
> - Updated planner instructions in `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
> - Enhanced dashboard messaging in `dashboard/chat_panel.py`
>
> **Estimated Effort**: Medium
> **Parallel Execution**: NO (sequential, single file focus for runner fixes)
> **Critical Path**: Backup → Fix runner → Fix validation → Fix planner → Fix dashboard → Verify

---

## Context

### Original Request
User wants product-list refresh to work correctly with no room for errors. Previous run failed due to wrong kwarg name (`supplier_title` vs `supplier_product_title`), but Momus/Metis analysis revealed additional lurking issues that would cause failures even after that fix.

### Verified Issues (3-source confirmed)
1. **Primary**: Wrong kwarg name in `search_by_ean_and_extract_data()` call
   - Log evidence: `unexpected keyword argument 'supplier_title'`
   - Code evidence: Line 192 uses `supplier_title=title`
   - Signature evidence: Method expects `supplier_product_title: str`

2. **Exception scope bug**: Variables not initialized before try block
   - If exception occurs before line 167, except block raises NameError

3. **Missing extractor.connect()**: No explicit connection before extraction
   - Can cause race conditions and intermittent failures

4. **Financial calc on zero matches**: Runs even when all ASINs are null
   - Produces misleading reports from stale cache

5. **Print instead of logging**: Errors don't appear in worker logs

6. **UX issues**: User doesn't know worker needs to run, no path validation

---

## Scope

### IN (Must Fix)
- `control_plane/run_product_list_refresh.py`: All 5 issues (kwarg, connect, scope, logging, financial skip)
- `control_plane/tools/product_list_refresh.py`: Add `products_path` existence validation
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`: Update explanation rules and worker guidance
- `dashboard/chat_panel.py`: Add post-enqueue messaging with worker instructions

### OUT (Guardrails)
- No worker redesign (locking, retries)
- No new dependencies
- No changes to job schema
- No commits/push
- No large refactors

---

## Execution Strategy

### Wave 1: Critical Runner Fixes (Sequential)
These must happen in order within the same file:

1. Fix kwarg name: `supplier_title` → `supplier_product_title`
2. Add `await extractor.connect()` before extraction loop
3. Initialize exception handler variables before try block
4. Replace `print()` with `logging.error()`
5. Skip financial calc when zero successful ASIN matches

### Wave 2: Validation & UX (Can parallelize with Wave 1 conceptually)
6. Add `products_path` existence validation
7. Update planner system instructions
8. Enhance dashboard messaging

### Wave 3: Verification
9. Run deterministic checks
10. Execute test job
11. Verify outputs

---

## TODOs

### Task 1: Fix Runner - Kwarg Name

**File**: `control_plane/run_product_list_refresh.py` (line ~192)

**Change**:
```python
# FROM:
extraction_result = await extractor.search_by_ean_and_extract_data(
    ean=ean, supplier_title=title, page=page
)

# TO:
extraction_result = await extractor.search_by_ean_and_extract_data(
    ean=ean, supplier_product_title=title, page=page
)
```

**Verification**:
```bash
grep -n "supplier_product_title" control_plane/run_product_list_refresh.py
# Expected: Line 192 shows supplier_product_title=title
```

---

### Task 2: Fix Runner - Add extractor.connect()

**File**: `control_plane/run_product_list_refresh.py` (after line 159)

**Change**:
```python
extractor = FixedAmazonExtractor(chrome_debug_port=9222)

async def run() -> None:
    await extractor.connect()  # ADD THIS LINE
    page = await _ensure_playwright_page(cdp_port=9222)
```

**Verification**:
```bash
grep -A2 "async def run" control_plane/run_product_list_refresh.py | grep "extractor.connect"
# Expected: Shows await extractor.connect()
```

---

### Task 3: Fix Runner - Exception Scope

**File**: `control_plane/run_product_list_refresh.py` (before line 163)

**Change**:
```python
for product in products:
    # Initialize before try block to prevent NameError in except
    title = ""
    supplier_url = ""
    ean = ""
    try:
        title = str(product.get("title") or "")
        supplier_url = str(product.get("url") or "")
        ean = _sanitize_ean(str(product.get("ean") or ""))
```

**Verification**:
```bash
grep -B2 "try:" control_plane/run_product_list_refresh.py | grep -E "title =|supplier_url =|ean ="
# Expected: Shows initialization lines before try
```

---

### Task 4: Fix Runner - Replace print with logging

**File**: `control_plane/run_product_list_refresh.py`

**Add at top**:
```python
import logging
log = logging.getLogger(__name__)
```

**Change exception handler** (line ~256):
```python
# FROM:
print(f"Error processing product {product.get('title', 'Unknown')}: {e}")

# TO:
log.error(f"Error processing product {product.get('title', 'Unknown')}: {e}", exc_info=True)
```

**Verification**:
```bash
grep -n "log.error" control_plane/run_product_list_refresh.py
# Expected: Shows log.error in exception handler
```

---

### Task 5: Fix Runner - Skip Financial Calc on Zero Matches

**File**: `control_plane/run_product_list_refresh.py` (lines 274-277)

**Change**:
```python
if not dry_run:
    successful_matches = sum(1 for r in results if r.get("amazon_asin"))
    if successful_matches > 0:
        from tools.FBA_Financial_calculator import run_calculations
        run_calculations(sandbox_supplier)
        print(f"✅ Financial calculations completed for {successful_matches} matched products")
    else:
        print("⚠️  No successful ASIN matches - skipping financial calculations")
```

**Verification**:
```bash
grep -A5 "if not dry_run:" control_plane/run_product_list_refresh.py | grep "successful_matches"
# Expected: Shows successful_matches check
```

---

### Task 6: Add products_path Validation

**File**: `control_plane/tools/product_list_refresh.py`

**Add after products_path determination**:
```python
from pathlib import Path

if not Path(products_path).exists():
    return {
        "ok": False,
        "error": "products_path_not_found",
        "products_path": products_path,
        "message": f"Products file not found: {products_path}"
    }
```

**Verification**:
```bash
python -c "from control_plane.tools.product_list_refresh import ProductListRefreshRequest, enqueue_product_list_refresh; from control_plane.paths import get_repo_root; r=enqueue_product_list_refresh(get_repo_root(), ProductListRefreshRequest(supplier_domain='test.com', products_path='C:/does_not_exist.json', dry_run=True)); print(r)"
# Expected: ok: False with clear error
```

---

### Task 7: Update Planner Instructions

**File**: `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`

**Changes**:
1. Change explanation rule from "single short sentence" to "2-4 sentences"
2. Add explicit instruction for enqueue tools to mention worker requirement

**Verification**:
```bash
grep -n "2-4 sentences" control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md
# Expected: Shows updated explanation rule
```

---

### Task 8: Enhance Dashboard Messaging

**File**: `dashboard/chat_panel.py`

**Add after successful enqueue**:
```python
if tool_call.name == "enqueue_product_list_refresh" and result.get("ok"):
    msg = f"""✅ Job queued successfully!
    
    Run ID: {result.get('run_id')}
    Supplier: {result.get('sandbox_supplier')}
    
    ⚠️  IMPORTANT: Start the worker to execute:
        python -m control_plane worker
    
    Monitor progress:
    - Status: OUTPUTS/CONTROL_PLANE/status/{result.get('run_id')}.json
    - Log: OUTPUTS/CONTROL_PLANE/logs/{result.get('run_id')}.log
    """
    st.info(msg)
```

**Verification**: Manual dashboard test

---

### Task 9: Backup Protocol

**Before ANY edits**:
1. Create backup dir: `backup/product_list_hardening_20260202/`
2. Copy each file before editing
3. Create `.bak_02-02-26_HH-MM-SS` next to each edited file

**Files to backup**:
- `control_plane/run_product_list_refresh.py`
- `control_plane/tools/product_list_refresh.py`
- `control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md`
- `dashboard/chat_panel.py`

---

### Task 10: Verification Suite

**A. Syntax Check**:
```bash
python -c "from control_plane.run_product_list_refresh import main; print('✅ Runner syntax OK')"
python -c "from control_plane.tools.product_list_refresh import enqueue_product_list_refresh; print('✅ Tools syntax OK')"
```

**B. Import Check**:
```bash
python -c "import logging; from tools.amazon_playwright_extractor import FixedAmazonExtractor; print('✅ Imports OK')"
```

**C. Test Run**:
1. Enqueue job via dashboard
2. Start worker: `python -m control_plane worker`
3. Verify job moves: pending → running → done
4. Check status file shows state progression
5. Check log has no "unexpected keyword argument" errors
6. Check linking map has ASINs populated (not all null)

---

## Verification Commands

```bash
# 1. Verify all fixes applied
grep -n "supplier_product_title" control_plane/run_product_list_refresh.py
grep -n "extractor.connect" control_plane/run_product_list_refresh.py
grep -n "title = \"\"" control_plane/run_product_list_refresh.py
grep -n "log.error" control_plane/run_product_list_refresh.py
grep -n "successful_matches" control_plane/run_product_list_refresh.py

# 2. Verify validation
grep -n "products_path_not_found" control_plane/tools/product_list_refresh.py

# 3. Verify planner
grep -n "2-4 sentences" control_plane/prompts/SYSTEM_INSTRUCTIONS_CHAT_PLANNER.md

# 4. Verify dashboard
grep -n "Job queued successfully" dashboard/chat_panel.py
```

---

## Success Criteria

- [ ] All 5 runner fixes applied and verified
- [ ] products_path validation working
- [ ] Planner instructions updated
- [ ] Dashboard shows clear post-enqueue message
- [ ] Test job executes without kwarg errors
- [ ] Linking map has non-null ASINs for matched products
- [ ] Financial calc only runs when matches exist
- [ ] Errors appear in worker logs (not just print)
- [ ] All files backed up
- [ ] No commits/push made

---

## Handoff

Plan ready for immediate execution. Start with Task 1 (backup), then proceed sequentially through Task 10.
