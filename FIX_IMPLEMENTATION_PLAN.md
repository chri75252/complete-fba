# FIX IMPLEMENTATION PLAN - CACHE PERSISTENCE ISSUES
**Date:** July 26, 2025  
**Based on:** Cache Investigation Report  
**Priority:** CRITICAL  

## PRIORITIZED FIX QUEUE

| Priority | Issue | Root Cause | Fix Blueprint | Complexity | Dependencies |
|----------|-------|------------|---------------|------------|--------------|
| 1 | Cache not updating during processing | Save only called during extraction | Add cache saves in main loop | Medium | None |
| 2 | Linking map silent failures | Atomic write pattern failing | Fix error handling in save method | Low | Fix 1 |
| 3 | Memory-disk sync disconnect | No incremental updates | Add periodic cache flushes | Medium | Fix 1,2 |
| 4 | State inconsistency | Processing state vs cache mismatch | Add cache validation | Low | Fix 1,2,3 |

## FIX BLUEPRINTS

### Fix 1: Cache Persistence During Processing
**Location:** `tools/passive_extraction_workflow_latest.py` lines 1593-1600  
**Current Code:**
```python
# Save state periodically using configurable batch sizes
if overall_product_index % linking_map_batch == 0:
    self.state_manager.save_state()
    self._save_linking_map(self.supplier_name)
```

**Fix Implementation:**
```python
# Save state AND cache periodically
if overall_product_index % linking_map_batch == 0:
    self.state_manager.save_state()
    self._save_linking_map(self.supplier_name)
    # CRITICAL FIX: Add cache persistence during processing
    self._save_incremental_cache_update(product_data)
```

### Fix 2: Linking Map Silent Failure Resolution
**Location:** `tools/passive_extraction_workflow_latest.py` lines 1721-1780  
**Issue:** Silent failures in atomic write pattern  
**Fix:** Add comprehensive error handling and validation

### Fix 3: Memory-Disk Synchronization
**Location:** Throughout main processing loop  
**Fix:** Add periodic cache flushes and memory-disk consistency checks

### Fix 4: State Validation
**Location:** State manager integration points  
**Fix:** Add cache timestamp validation and consistency checks

## IMPLEMENTATION SEQUENCE

1. **Fix 1:** Implement cache persistence during processing (30 min)
2. **Fix 2:** Resolve linking map save failures (20 min)  
3. **Fix 3:** Add memory-disk synchronization (45 min)
4. **Fix 4:** Implement state validation (15 min)

**Total Estimated Time:** 1 hour 50 minutes  
**Risk Level:** Medium (well-isolated changes)  
**Testing Required:** Cache persistence validation, resume capability testing