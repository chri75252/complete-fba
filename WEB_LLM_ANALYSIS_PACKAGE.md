# Web LLM Analysis Package - Amazon FBA System Issues

**Date**: 2025-11-27
**Issue Category**: Resume Logic Discrepancies & Product Count Mismatches
**Severity**: CRITICAL - Causes reprocessing and data loss

---

## FILES REQUIRED FOR ANALYSIS

### 1. Core Workflow Scripts
```
tools/passive_extraction_workflow_latest.py
    - Main orchestrator with resume logic
    - Contains _run_amazon_phase_from_resume() method
    - Contains _extract_supplier_products() method
    - Contains filtering and counting logic
```

### 2. State Management
```
utils/fixed_enhanced_state_manager.py
    - State file management
    - Resume pointer calculation
    - Atomic save operations
```

### 3. Configuration Files
```
config/angelwholesale_categories.json
    - Category URLs and order
    - Defines total categories (should be 328 for angelwholesale)
```

### 4. Output Files (Current State)
```
OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json
    - List of completed Amazon extractions
    - Each entry has: supplier_url, amazon_asin, supplier_ean
    - Used to determine "skip" count

OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json
    - List of extracted supplier products
    - Each entry has: url, ean, source_url (category URL)
    - Used to determine "cached" count

OUTPUTS/manifests/angelwholesale.co.uk/angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json
    - List of all product URLs for this category
    - Generated during URL discovery phase
    - Defines the denominator (total products)

OUTPUTS/CACHE/processing_states/angelwholesale-co-uk_processing_state.json
    - Current system state
    - Contains resume pointers and phase information
```

### 5. Debug Logs
```
logs/debug/run_custom_poundwholesale_20251127_072429.log
    - "GOOD" run that appeared to work correctly
    - Shows: skip=393, cached=5, full=3, total=401

logs/debug/run_custom_poundwholesale_20251127_093803.log
    - "BAD" run with incorrect behavior
    - Shows: skip=287, cached=114, full=0, total=401
    - Resume pointer 402 exceeds denominator 401
```

---

## DOCUMENTED ISSUES

### Issue 1: Product Count Migration (Good → Bad Run)
**Symptom**: Between runs using identical scripts/config, product counts shifted dramatically

**Good Run (072429)**:
```
- Skip (linking_map): 393
- Cached (supplier): 5
- Full extraction needed: 3
- Total: 401
- Resume pointer: 399/401 ✅ VALID
```

**Bad Run (093803)**:
```
- Skip (linking_map): 287  ← DECREASED by 106
- Cached (supplier): 114   ← INCREASED by 109
- Full extraction needed: 0
- Total: 401
- Resume pointer: 402/401 ❌ OUT OF BOUNDS
```

**Numerical Analysis**:
- 393 → 287 = -106 products lost from linking_map
- 5 → 114 = +109 products gained in cache
- Net difference: +3 products appeared from nowhere
- This suggests linking_map is being UNDERCOUNTED in bad run

**Expected Behavior**:
- Counts should remain stable across runs when processing_state.json is deleted
- Resume pointer should NEVER exceed denominator
- Sum invariant should hold: skip + cached + full = denominator

### Issue 2: Resume Pointer Out of Bounds
**Symptom**: System calculates resume pointer as 402 when denominator is 401

**Log Evidence (093803)**:
```
RESUME PTR: phase=supplier cat_idx=2/326 url=...All-Baby-and-child prod_idx=401/401
Resume from product: 402  ← OUT OF BOUNDS
Denominator: 401
```

**Mathematical Error**:
- If prod_idx=401 and denominator=401, system is already AT THE END
- Resume should be 401 (last item) or category should be marked complete
- Calculating 402 suggests off-by-one error in pointer arithmetic

**Impact**:
- Category is treated as "complete" but with products remaining
- Those products are never processed
- Data loss occurs silently

### Issue 3: Incorrect Linking Map Count
**Symptom**: System claims 287 entries in linking_map when actual count is different

**Investigation Needed**:
1. Count actual entries in linking_map.json where supplier_url contains `/Category/All-Baby-and-child`
2. Verify if filtering logic matches between:
   - Initial run (when building worklist)
   - Resume run (when calculating skip count)
3. Check for URL normalization differences

**Log Pattern**:
```
Good Run: "SKIP_ENTIRELY (393): ['url1', 'url2'...]"
Bad Run: "SKIP_ENTIRELY (287): ['url1', 'url2'...]"
```

**Questions to Answer**:
- Are 106 products being filtered out incorrectly?
- Is there a matching logic inconsistency?
- Does sorting affect URL matching?

### Issue 4: Cached Product Count Discrepancy
**Symptom**: System claims 114 cached products for category, but good run only found 5

**Investigation Needed**:
1. Count entries in cache file where source_url = "https://angelwholesale.co.uk/Category/All-Baby-and-child"
2. Verify if category URL matching is consistent
3. Check if cache is being contaminated with products from other categories

**Hypothesis**:
- Cache filtering may use different URL matching than linking_map
- Products from category reshuffling may remain in cache with old source_url
- Cache is not being cleared between runs as expected

### Issue 5: Category Order Sensitivity
**Symptom**: System behavior changes when category order in config is shuffled

**Observations**:
- User reshuffled categories: system worked correctly (good run)
- User restored original order: system reverted to broken behavior (bad run)
- Identical scripts, config settings, and deleted processing_state.json

**This Suggests**:
- Category order affects state calculations
- Cache or linking_map contains residual data from previous runs
- System is NOT fully stateless after deleting processing_state.json

**Expected Behavior**:
- Deleting processing_state.json should completely reset system
- Category order should NOT affect resume calculations
- Each run should be deterministic given same inputs

---

## TRIANGULAR PROTOCOL REQUIREMENTS

To properly diagnose these issues, the web LLM must simultaneously analyze:

### SOURCE 1: Linking Map (linking_map.json)
**Count Calculation**:
```python
# Count entries where supplier_url contains target category
category_entries = [
    entry for entry in linking_map
    if '/Category/All-Baby-and-child' in entry['supplier_url']
]
actual_skip_count = len(category_entries)
```

**Verify Against Log Claims**:
- Good Run claims: 393
- Bad Run claims: 287
- Actual count: ??? (web LLM must verify)

### SOURCE 2: Cache File (products_cache.json)
**Count Calculation**:
```python
# Count products where source_url matches target category
cached_products = [
    product for product in cache
    if product['source_url'] == 'https://angelwholesale.co.uk/Category/All-Baby-and-child'
]
actual_cached_count = len(cached_products)
```

**Verify Against Log Claims**:
- Good Run claims: 5
- Bad Run claims: 114
- Actual count: ??? (web LLM must verify)

### SOURCE 3: Manifest File (manifest.json)
**Count Calculation**:
```python
# Count total URLs in manifest
manifest_urls = manifest['urls']
actual_denominator = len(manifest_urls)
```

**Verify Against Log Claims**:
- Both runs claim: 401
- Actual count: ??? (web LLM must verify)

### CROSS-VERIFICATION FORMULA
```
INVARIANT: denominator = skip + cached + full_extraction

Expected (from manifest):
  401 = linking_map_count + cache_count + remaining

Good Run Claims:
  401 = 393 + 5 + 3 ✅ (sum matches)

Bad Run Claims:
  401 = 287 + 114 + 0 ✅ (sum matches)

BUT: If actual linking_map = 393 and actual cache = 5:
  401 = 393 + 5 + 3 (correct)
  401 ≠ 287 + 114 + 0 (bad run is WRONG)

This proves bad run is using incorrect counts from sources.
```

---

## EXPECTED BEHAVIOR POST-FIX

### Correct Resume Logic
When system resumes from interruption:

1. **Read Manifest**: Get denominator (e.g., 401 URLs)

2. **Count Linking Map**:
   ```
   skip_count = count entries where supplier_url IN manifest_urls
   Example: 393 entries found
   ```

3. **Count Cache**:
   ```
   cached_count = count products where url IN manifest_urls
   Example: 5 entries found
   ```

4. **Calculate Remaining**:
   ```
   full_extraction = denominator - skip_count - cached_count
   Example: 401 - 393 - 5 = 3
   ```

5. **Validate Invariant**:
   ```
   ASSERT: denominator == skip_count + cached_count + full_extraction
   ASSERT: resume_pointer <= denominator
   ```

6. **Resume from Correct Position**:
   ```
   resume_ptr = skip_count + cached_count + 1
   Example: 393 + 5 + 1 = 399 ✅ VALID (< 401)
   ```

### Deterministic Behavior
After deleting processing_state.json:
- System should recalculate ALL counts from files
- NO residual state from previous runs
- Category order should NOT affect calculations
- Counts should match across identical runs

### Correct Output
```
✅ FILTER INVARIANT VALIDATED:
  in=401 == skip=393 + cached=5 + full=3

🎯 RESUMING IN SUPPLIER PHASE:
  Resume from product: 399  ← WITHIN BOUNDS
  Skipping:
    - 393 in linking map (already complete)
    - 5 in cache (already extracted)
  Products to process: 3  ← CORRECT

Resume pointer: 399/401 ✅ VALID
```

---

## ROOT CAUSE HYPOTHESES

### Hypothesis 1: URL Matching Inconsistency
- **Initial run**: Uses EXACT URL matching from manifest
- **Resume run**: Uses NORMALIZED or PARTIAL matching
- **Result**: 106 products fail to match during resume, counted as "cached" instead of "skip"

**Evidence Needed**:
- Compare URL matching logic in `_extract_supplier_products()` vs `_run_amazon_phase_from_resume()`
- Check for `normalize_url()` calls or regex matching differences

### Hypothesis 2: Sorting Changes Order
- **Initial run**: Processes products in manifest order
- **Resume run**: Sorts products alphabetically before matching
- **Result**: Index-based resume pointer points to wrong products

**Evidence Needed**:
- Search for `sorted()` calls in resume logic
- Check if products are reordered before building worklist

### Hypothesis 3: Cache Contamination
- **Cache contains**: Products from ALL categories with stale source_url
- **Resume logic**: Overcounts cached products for target category
- **Result**: System thinks 114 products are cached when only 5 actually match

**Evidence Needed**:
- Verify cache is category-specific or global
- Check if source_url is updated when categories are reordered

### Hypothesis 4: State File Persistence
- **Assumption**: Deleting processing_state.json clears ALL state
- **Reality**: Some state persists in cache or linking_map
- **Result**: "Fresh" runs still carry residual data from previous runs

**Evidence Needed**:
- Check if cache needs manual clearing
- Verify if linking_map is cumulative across runs

---

## ANALYSIS DELIVERABLES

The web LLM should provide:

1. **Actual File Counts**:
   - linking_map entries for All-Baby-and-child: ???
   - cached products for All-Baby-and-child: ???
   - manifest URLs for All-Baby-and-child: ???

2. **Count Discrepancy Root Cause**:
   - Which hypothesis (1-4) is correct?
   - Exact code location causing mismatch
   - Why does behavior differ between runs?

3. **Resume Pointer Error**:
   - Why is 402 calculated when 401 is max?
   - Code line responsible for off-by-one error
   - Fix to ensure pointer ≤ denominator

4. **Suggested Fix**:
   - Code changes required (with line numbers)
   - Test cases to prevent regression
   - Verification steps to confirm fix

---

## VERIFICATION CHECKLIST

After fix is implemented, verify:

- [ ] linking_map count matches between runs
- [ ] cached count matches between runs
- [ ] Resume pointer always ≤ denominator
- [ ] Category order doesn't affect calculations
- [ ] Deleting processing_state.json fully resets system
- [ ] Sum invariant holds: denominator = skip + cached + full
- [ ] No products are reprocessed unnecessarily
- [ ] All 401 products are eventually processed

---

**END OF ANALYSIS PACKAGE**
