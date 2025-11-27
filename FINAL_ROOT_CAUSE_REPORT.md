# FINAL ROOT CAUSE REPORT - Amazon FBA System Issues

**Date**: 2025-11-27
**Analysis Method**: Triangular Protocol (Logs + Cache + Linking Map + Manifest)
**Critical Finding**: 281 products exist in BOTH cache AND linking_map (IMPOSSIBLE!)

---

## EXECUTIVE SUMMARY

The system is **double-counting 281 products**, causing:
1. ❌ Reprocessing of already-completed products (10+ ASINs confirmed)
2. ❌ Incorrect resume pointer calculations
3. ❌ Denominator shifts (401 → 397)
4. ❌ Products being lost or skipped

**Root Cause**: Products are NOT being removed from cache after being added to linking_map.

---

## TRIANGULAR PROTOCOL VERIFICATION

### SOURCE 1: Actual File Counts (Ground Truth)

```
Manifest:       401 URLs (denominator)
Cache:          397 products for category
Linking Map:    285 entries matching manifest
Overlap:        281 products in BOTH cache AND linking_map ⚠️
```

### SOURCE 2: Log Analysis

**First Run (154127)**:
- Claimed denominator: 401 ✅
- Amazon extractions: 72 unique ASINs

**Resume Run (155617)**:
- Claimed denominator: 397 (WRONG - should be 401)
- Amazon extractions: 14 unique ASINs
- **10 ASINs duplicated from first run** ⚠️

---

## THE CORE PROBLEM: Double-Counting

### Normal Workflow (Expected)
```
Product Lifecycle:
1. URL in manifest (denominator: 401)
2. Supplier extraction → Added to CACHE
3. Amazon analysis → Added to LINKING_MAP, REMOVED from cache
4. Product now only in linking_map
```

### Actual Broken Workflow
```
Current Behavior:
1. URL in manifest (denominator: 401)
2. Supplier extraction → Added to CACHE
3. Amazon analysis → Added to LINKING_MAP, but STAYS in cache!
4. Product exists in BOTH places (281 products)
```

### Why This Causes Reprocessing

When system resumes:
```python
# System counts:
skip_count = 285  # linking_map entries (includes 281 overlaps)
cached_count = 397  # cache entries (includes 281 overlaps)

# But these 281 products are counted TWICE!
# So system thinks:
remaining = 401 - 285 - 397 = -281 ⚠️ NEGATIVE!

# System logic gets confused:
# - "397 in cache" suggests they need Amazon extraction
# - But 281 of them are already in linking_map!
# - So it re-processes them unnecessarily
```

---

## NUMERICAL EVIDENCE

### Overlap Breakdown

```
Category: All-Baby-and-child (401 URLs in manifest)

├─ In BOTH cache and linking_map: 281 ⚠️ DUPLICATES
│  └─ These are COMPLETED products that shouldn't be in cache
│
├─ In linking_map ONLY: 4
│  └─ These are correctly completed
│
├─ In cache ONLY: 116
│  └─ These need Amazon analysis
│
└─ In NEITHER: 2
   └─ These need supplier extraction

CORRECT counts:
  Skip (completed): 281 + 4 = 285
  Cached (pending Amazon): 116
  Remaining (not extracted): 2
  Total: 285 + 116 + 2 = 403 ⚠️ (2 over manifest!)
```

### Reprocessing Evidence

**ASINs extracted multiple times**:
```
First run: 72 unique ASINs
Resume run: 14 unique ASINs
Duplicates: 10 ASINs (13.9% waste)

Sample duplicates:
  - B0BQJHGCM9
  - B01N702CNN
  - B0C44LT7M7
  - B07BNQ2X49
  - B01FRGNV84
```

---

## ROOT CAUSES IDENTIFIED

### Issue 1: Cache Not Cleared After Linking Map Entry

**Location**: `tools/passive_extraction_workflow_latest.py`

**Problem**: When Amazon analysis completes and adds entry to linking_map:
```python
# CURRENT (WRONG):
1. Extract supplier data → cache
2. Amazon analysis → linking_map
3. Cache entry REMAINS ⚠️

# EXPECTED (CORRECT):
1. Extract supplier data → cache
2. Amazon analysis → linking_map + REMOVE from cache
3. Product only in linking_map ✅
```

**Impact**:
- 281 products remain in cache after completion
- Resume logic counts them as "needing Amazon extraction"
- System reprocesses them unnecessarily

### Issue 2: Resume Logic Counts Both Sources

**Location**: `tools/passive_extraction_workflow_latest.py::_run_amazon_phase_from_resume()`

**Problem**:
```python
# System does:
skip_count = len(linking_map_entries)  # 285
cached_count = len(cache_entries)      # 397
# These overlap by 281!

# Should do:
skip_count = len(linking_map_entries)  # 285
cached_count = len(cache_entries NOT in linking_map)  # 116 (excluding overlap)
```

**Impact**:
- Incorrect remaining calculation
- Resume pointer points to wrong products
- Products are reprocessed

### Issue 3: Denominator Mismatch (401 → 397)

**Observation**: First run uses 401, resume uses 397

**Hypothesis**: Cache count (397) is being used as denominator instead of manifest count (401)

**Code to Check**:
```python
# Suspect this line is using len(cache) instead of len(manifest):
denominator = len(self.product_cache)  # WRONG - uses 397
# Should be:
denominator = len(manifest['product_urls'])  # CORRECT - uses 401
```

**Impact**:
- 4 products are "lost" in transition (401 - 397)
- Resume pointer shifts incorrectly

### Issue 4: Extra 2 Products Mystery

**Observation**: 285 + 116 + 2 = 403 (but manifest has 401)

**Possible causes**:
1. Linking_map has 2 entries not in manifest (contamination from other categories)
2. Cache has 2 entries not in manifest (stale data)
3. Manifest is missing 2 URLs (scraping incomplete)

**Needs Investigation**: Check timestamps and source_url for all entries

---

## EXPECTED BEHAVIOR (POST-FIX)

### Correct Workflow
```
1. Manifest scraped: 401 URLs frozen
2. Supplier extraction: 401 products → cache
3. Amazon analysis loop:
   - Process product from cache
   - Extract Amazon data
   - Add to linking_map
   - REMOVE from cache ✅
4. Resume: Count only linking_map (285) + cache (116) + neither (2) = 403
```

### Correct Resume Calculation
```python
# Load manifest
manifest_urls = load_manifest()  # 401 URLs

# Count completed (in linking_map)
completed_urls = {entry['supplier_url'] for entry in linking_map}
skip_count = len(completed_urls & manifest_urls)  # Only matching manifest

# Count cached (in cache but NOT in linking_map)
cached_urls = {p['url'] for p in cache if p['source_url'] == category_url}
cached_not_completed = cached_urls - completed_urls  # Exclude overlap!
cached_count = len(cached_not_completed)

# Calculate remaining
remaining = len(manifest_urls) - skip_count - cached_count

# Validate invariant
assert skip_count + cached_count + remaining == len(manifest_urls), "Invariant failed!"
```

### Expected Log Output
```
✅ FILTER INVARIANT VALIDATED:
  in=401 == skip=285 + cached=116 + remaining=2
  (Note: cached=116 excludes 281 already in linking_map)

🎯 RESUMING IN AMAZON PHASE:
  Resume from product: 286
  Skipping:
    - 285 in linking map (already complete)
  Cached (need Amazon):
    - 116 in cache (not yet analyzed)
  Not yet extracted:
    - 2 products

Resume pointer: 286/401 ✅ VALID
```

---

## FIXES REQUIRED

### Fix 1: Remove from Cache After Linking Map Entry

**File**: `tools/passive_extraction_workflow_latest.py`

**Location**: After successful Amazon extraction and linking_map update

**Change**:
```python
# After adding to linking_map:
self.linking_map_entries.append(new_entry)

# ADD THIS: Remove from cache
supplier_url = product_data['url']
self.product_cache = [
    p for p in self.product_cache
    if p.get('url') != supplier_url
]
# Or update cache file atomically
```

### Fix 2: Exclude Overlap in Resume Calculations

**File**: `tools/passive_extraction_workflow_latest.py`

**Location**: `_run_amazon_phase_from_resume()` method

**Change**:
```python
# Get linking_map URLs
completed_urls = {
    entry.get('supplier_url')
    for entry in self.linking_map_entries
}

# Get cached URLs for category, EXCLUDING those already completed
cached_urls = {
    p.get('url')
    for p in self.product_cache
    if p.get('source_url') == category_url
    and p.get('url') not in completed_urls  # ← ADD THIS FILTER
}

cached_count = len(cached_urls)  # Now correctly excludes overlap
```

### Fix 3: Always Use Manifest as Denominator

**File**: `tools/passive_extraction_workflow_latest.py`

**Ensure**:
```python
# Load manifest URLs (frozen denominator)
manifest_urls = load_manifest(category_url)
denominator = len(manifest_urls)  # Always 401, never 397

# Never use len(cache) as denominator!
```

### Fix 4: Investigate 2-Product Mismatch

**Action**: Add validation to detect contamination

```python
# Check all cache entries belong to target category
for product in cache:
    if product['source_url'] != category_url:
        logger.warning(f"Cache contamination: {product['url']} from {product['source_url']}")

# Check all linking_map entries are in manifest
manifest_urls = set(load_manifest(category_url))
for entry in linking_map:
    if entry['supplier_url'] not in manifest_urls:
        logger.warning(f"Linking map contamination: {entry['supplier_url']}")
```

---

## VERIFICATION STEPS

After implementing fixes:

1. **Delete** processing_state.json, cache file, linking_map file
2. **Run** fresh extraction for All-Baby-and-child
3. **Verify** during run:
   ```
   - Denominator stays 401 throughout
   - No products in both cache and linking_map
   - Invariant: manifest = skip + cached + remaining (always balanced)
   ```
4. **Interrupt** and resume
5. **Verify** resume:
   ```
   - Denominator still 401
   - No ASINs reprocessed
   - Resume pointer ≤ denominator
   ```

---

## FILES FOR WEB LLM ANALYSIS

To conduct independent verification, provide these files:

### Code Files
```
tools/passive_extraction_workflow_latest.py
  - Lines containing cache operations
  - Lines containing linking_map operations
  - _run_amazon_phase_from_resume() method
  - _extract_supplier_products() method
```

### Data Files (Current State)
```
OUTPUTS/cached_products/angelwholesale-co-uk_products_cache.json
  - All 3343 products (397 for target category)

OUTPUTS/FBA_ANALYSIS/linking_maps/angelwholesale.co.uk/linking_map.json
  - All 351 entries (285 matching manifest)

OUTPUTS/manifests/angelwholesale.co.uk/angelwholesale.co.uk_Category_All-Baby-and-child_manifest.json
  - 401 URLs (frozen denominator)
```

### Logs
```
logs/debug/run_custom_poundwholesale_20251125_154127.log
  - First run (401 denominator, 72 ASINs)

logs/debug/run_custom_poundwholesale_20251125_155617.log
  - Resume run (397 denominator, 14 ASINs, 10 duplicates)
```

### Verification Scripts
```
check_overlap.py - Detects 281-product overlap
triangular_nov25_analysis.py - Cross-verifies all sources
```

---

## PRIORITY CLASSIFICATION

**P0 - CRITICAL**:
- Fix 1: Remove from cache after linking_map entry (prevents 281 duplicates)
- Fix 2: Exclude overlap in resume calculations (prevents reprocessing)

**P1 - HIGH**:
- Fix 3: Always use manifest as denominator (prevents 401→397 shift)

**P2 - MEDIUM**:
- Fix 4: Investigate 2-product mismatch (data integrity)

---

**END OF REPORT**
