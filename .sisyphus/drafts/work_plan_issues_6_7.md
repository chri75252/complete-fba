# Work Plan: Fix Issues #6 and #7
**Date:** 2026-02-17  
**Status:** Ready for Implementation  
**Priority:** HIGH (Issue #6), MEDIUM (Issue #7)

---

## Overview

This work plan addresses two critical bugs identified in the triangulated analysis:
- **Issue #6 (HIGH):** Processing state top-level counters never updated by product-list refresh runner
- **Issue #7 (MEDIUM):** Status JSON `refresh.counts` inaccurate/stale

---

## Phase 1: Fix Issue #6 - Processing State Counter Sync

### File: `control_plane/run_product_list_refresh.py`

### Problem
After product-list refresh completes, the processing state file has incorrect top-level counters:
- `total_products: 0` (should be N)
- `session_products_processed: 0` (should be N)
- `successful_products: 0` (should be N)
- `processing_status: "initialized"` (should be "complete")
- `is_fresh_start: true` (should be `false`)
- `last_updated: <created_at>` (should be updated timestamp)

### Root Cause
The runner updates `system_progression` fields but never syncs top-level state counters.

### Implementation Location
**Line 359** (after `state_manager.save_state_atomic()` in the `run()` function)

### Required Changes

```python
# After line 359: state_manager.save_state_atomic()

# Sync top-level counters from system_progression
sd = state_manager.state_data
sp = sd["system_progression"]
sd["total_products"] = sp.get("supplier_products_completed", 0)
sd["session_products_processed"] = sp.get("amazon_products_completed", 0)
sd["successful_products"] = sum(1 for r in results if r.get("amazon_asin"))
sd["processing_status"] = "complete"
sd["is_fresh_start"] = False
sd["last_updated"] = _utc_now_iso()
state_manager.save_state_atomic()
```

### Verification Criteria
- [ ] Processing state file has `total_products` = actual product count
- [ ] Processing state file has `session_products_processed` = actual processed count
- [ ] Processing state file has `successful_products` = count of entries with ASINs
- [ ] Processing state file has `processing_status` = "complete"
- [ ] Processing state file has `is_fresh_start` = false
- [ ] Processing state file has `last_updated` > `created_at`

---

## Phase 2: Fix Issue #7 - Status JSON Count Accuracy

### File: `control_plane/worker.py`

### Problem A: Input Products Count Wrong for Object-Shaped Files
**Location:** Lines 355-360

Current code:
```python
products_path = refresh.get("products_path")
input_products = 0
if products_path:
    try:
        input_products = len(read_json(Path(products_path)))
    except Exception:
        input_products = 0
```

This counts `len(data)` which returns 4 for object-shaped files (keys: schema_version, supplier_domain, notes, products) instead of `len(data['products'])` = 6.

### Fix A: Handle Object-Shaped JSON
```python
products_path = refresh.get("products_path")
input_products = 0
if products_path:
    try:
        data = read_json(Path(products_path))
        if isinstance(data, dict) and "products" in data:
            input_products = len(data["products"])
        elif isinstance(data, list):
            input_products = len(data)
        else:
            input_products = 0
    except Exception:
        input_products = 0
```

### Problem B: Terminal Status Counts Are Stale
**Location:** Lines 395-407

At terminal status (done/failed/cancelled), the code does NOT recompute `refresh.counts` from authoritative sources. It keeps whatever was last written during periodic updates (which can be N-1 or stale).

### Fix B: Recompute Counts at Terminal Status

Add a helper function to recompute all counts from disk:

```python
def _recompute_refresh_counts(status, job, paths, resolved):
    """Recompute refresh.counts from authoritative sources at terminal status."""
    import time as time_module
    
    refresh = job.get("refresh", {})
    run_id = str(job.get("run_id", ""))
    overrides_dir = (
        paths.repo_root
        / "OUTPUTS"
        / "CONTROL_PLANE"
        / "overrides"
        / run_id
    )
    amazon_cache_dir = overrides_dir / "amazon_cache"
    
    status["refresh"]["last_updated"] = time_module.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time_module.gmtime()
    )
    status["refresh"]["paths"] = {
        "products_path": str(refresh.get("products_path", "")),
        "overrides_run_dir": str(overrides_dir),
        "amazon_cache_dir": str(amazon_cache_dir),
        "linking_map": resolved.get("linking_map"),
        "processing_state": resolved.get("processing_state"),
    }
    
    # Recompute input_products correctly
    products_path = refresh.get("products_path")
    input_products = 0
    if products_path:
        try:
            data = read_json(Path(products_path))
            if isinstance(data, dict) and "products" in data:
                input_products = len(data["products"])
            elif isinstance(data, list):
                input_products = len(data)
        except Exception:
            input_products = 0
    
    status["refresh"]["counts"] = {
        "input_products": input_products,
        "linking_map_entries": _count_linking_map_entries(
            resolved.get("linking_map")
        ),
        "amazon_cache_files": _count_amazon_cache_files(
            amazon_cache_dir
        ),
        "matched_asins": _count_matched_asins(
            resolved.get("linking_map")
        ),
    }
```

Then call this function at terminal status (before writing status):
- Line 399-402 (done state)
- Line 403-407 (failed state)

---

## Implementation Sequence

1. **Issue #6 First** (higher priority, simpler fix)
   - Modify `control_plane/run_product_list_refresh.py`
   - Add counter sync after line 359
   - Test with a small product list refresh

2. **Issue #7 Second** (depends on Issue #6 being stable)
   - Modify `control_plane/worker.py`
   - Fix input_products count (lines 355-360)
   - Add _recompute_refresh_counts function
   - Call at terminal status (lines 395-407)
   - Test with a small product list refresh

---

## Testing Plan

### Pre-Implementation Baseline
1. Run a small product-list refresh (4-6 products)
2. Capture:
   - Processing state file content
   - Status JSON content
   - Linking map entry count
   - Amazon cache file count

### Post-Implementation Verification
1. Run same product-list refresh
2. Verify:
   - Processing state top-level counters match actual counts
   - Status JSON `refresh.counts` match actual counts
   - No regressions in existing functionality

---

## Rollback Plan

If issues arise:
```bash
cp backup/fix_issues_6_7_20260217/run_product_list_refresh.py control_plane/
cp backup/fix_issues_6_7_20260217/worker.py control_plane/
```

---

## Files Modified

- `control_plane/run_product_list_refresh.py` - Issue #6 fix
- `control_plane/worker.py` - Issue #7 fix

## Files Referenced (Read-Only)

- `utils/fixed_enhanced_state_manager.py` - State manager API
- `OUTPUTS/CONTROL_PLANE/status/*.json` - Status JSON evidence
- `OUTPUTS/CACHE/processing_states/*_processing_state.json` - Processing state evidence
