# Verified Implementation Plan: All 7 Issues

**Date:** 2025-11-27  
**Status:** Complete with Verified Code Diffs  
**Analyst:** Claude (Counter-verified against actual code)

---

## 🔴 Critical Errors in Original Implementation Plan

| Plan Item | Error | Correction |
|-----------|-------|------------|
| Fix 2: Count Mismatch | Uses `get_category_denominator()` / `set_category_denominator()` | **These methods DO NOT EXIST.** Use `get_frozen_denominator()` (line 924) and update `frozen_category_denominators` dict directly |
| Fix 3: Data Loss | Uses `_save_linking_map(force=True)` | **Wrong signature.** Method is `_save_linking_map(self, supplier_name: str)` at line 3309 |
| ISS-004 | Not addressed | **MISSING:** Bulk mode switch (15 → 3312 products) |
| ISS-005 | Not addressed | **MISSING:** Invalid index validation (576/15) |
| ISS-007 | Not addressed | **MISSING:** Counter desynchronization |

---

## ✅ Complete Verified Fixes

### Fix 1: Resume Sort Mismatch (ISS-003) ✓ VERIFIED

**File:** `tools/passive_extraction_workflow_latest.py`

#### Fix 1A: Remove sorting from resume queue

**Location:** Line 7678

```python
# CURRENT CODE (Line 7674-7679):
        # Deterministic order
        def _nurl(u): 
            try: return normalize_url(u) if u else ""
            except Exception: return u or ""
        queue.sort(key=lambda x: _nurl(x.get("url")))

        self.log.info(f"📦 CATEGORY QUEUE: url={ncat} size={len(queue)} allowed_gate={'on' if allowed else 'off'}")
```

```python
# FIXED CODE:
        # Deterministic order helper (kept for potential future use)
        def _nurl(u): 
            try: return normalize_url(u) if u else ""
            except Exception: return u or ""
        # 🚨 FIX ISS-003: REMOVED sorting to match Initial Run's discovery order
        # Resume must use same order as initial run for index-based resumption
        # queue.sort(key=lambda x: _nurl(x.get("url")))

        self.log.info(f"📦 CATEGORY QUEUE: url={ncat} size={len(queue)} allowed_gate={'on' if allowed else 'off'}")
```

#### Fix 1B: Add sorting to initial run for future stability

**Location:** After Line 2304

```python
# CURRENT CODE (Lines 2301-2307):
            price_filtered_products = [
                p for p in valid_supplier_products 
                if p.get("_skipped") or (MIN_PRICE <= p.get("price", 0) <= MAX_PRICE)
            ]
            self.log.info(
                f"Found {len(valid_supplier_products)} valid supplier products, {len(price_filtered_products)} within price range [£{MIN_PRICE}-£{MAX_PRICE}]"
            )
```

```python
# FIXED CODE:
            price_filtered_products = [
                p for p in valid_supplier_products 
                if p.get("_skipped") or (MIN_PRICE <= p.get("price", 0) <= MAX_PRICE)
            ]
            
            # 🚨 FIX ISS-003: Sort products by URL for deterministic order
            # This ensures resume runs will have the same product order as initial run
            def _safe_url_sort(p):
                u = p.get("url", "")
                try:
                    return normalize_url(u) if u else ""
                except Exception:
                    return u or ""
            price_filtered_products.sort(key=_safe_url_sort)
            
            self.log.info(
                f"Found {len(valid_supplier_products)} valid supplier products, {len(price_filtered_products)} within price range [£{MIN_PRICE}-£{MAX_PRICE}]"
            )
```

---

### Fix 2: Count Mismatch / Denominator Drift (ISS-002, ISS-006) ✓ CORRECTED

**File:** `tools/passive_extraction_workflow_latest.py`  
**Location:** Method `_run_amazon_phase_from_resume`, after Line 7852

**⚠️ ORIGINAL PLAN ERROR:** Referenced non-existent methods `get_category_denominator()` and `set_category_denominator()`

**ACTUAL AVAILABLE METHODS:**
- `get_frozen_denominator(category_url)` - Line 924 of `fixed_enhanced_state_manager.py`
- Direct update to `frozen_category_denominators` dict

```python
# CURRENT CODE (Lines 7851-7862):
        products = filtered
        total = len(products)

        sp = self.state_manager.state_data.get("system_progression", {})
        saved_amazon_offset = int(sp.get("amazon_products_completed", 0)) if isinstance(sp.get("amazon_products_completed", 0), (int, float)) else int(sp.get("amazon_products_completed", 0) or 0)
```

```python
# FIXED CODE:
        products = filtered
        total = len(products)

        # 🚨 FIX ISS-002/ISS-006: Detect and align denominator mismatch
        frozen_denom = self.state_manager.get_frozen_denominator(category_url)
        if frozen_denom is not None and frozen_denom != total:
            self.log.warning(
                f"⚠️ DENOMINATOR MISMATCH DETECTED:\n"
                f"   Frozen denominator: {frozen_denom}\n"
                f"   Actual queue size:  {total}\n"
                f"   Difference: {frozen_denom - total} products\n"
                f"   Action: Aligning state to actual queue size ({total})"
            )
            # Update frozen_category_denominators map
            try:
                nurl = normalize_url(category_url)
            except Exception:
                nurl = category_url
            frozen_cats = self.state_manager.state_data.setdefault("frozen_category_denominators", {})
            frozen_cats[nurl] = total
            # Also update system_progression
            sp_update = self.state_manager.state_data.setdefault("system_progression", {})
            sp_update["amazon_products_needing_analysis"] = total
            sp_update["supplier_products_needing_extraction"] = total

        sp = self.state_manager.state_data.get("system_progression", {})
        saved_amazon_offset = int(sp.get("amazon_products_completed", 0)) if isinstance(sp.get("amazon_products_completed", 0), (int, float)) else int(sp.get("amazon_products_completed", 0) or 0)
```

---

### Fix 3: Linking Map Data Loss (ISS-001) ✓ CORRECTED

**File:** `tools/passive_extraction_workflow_latest.py`

**⚠️ ORIGINAL PLAN ERROR:** Used `_save_linking_map(force=True)` but actual signature is:
```python
def _save_linking_map(self, supplier_name: str):  # Line 3309
```

**CORRECT FIX:** Modify `_add_linking_map_entry_optimized` to trigger periodic saves.

**Location:** Method `_add_linking_map_entry_optimized`, Line 1644

```python
# CURRENT CODE (Lines 1644-1673):
    def _add_linking_map_entry_optimized(self, entry: Dict[str, Any]) -> None:
        """
        Add entry to linking map with hash index optimization.
        ...
        """
        # Add to hash indexes first to detect duplicates
        is_new_entry = self.hash_optimizer.add_entry(entry)

        if is_new_entry:
            # Only append to main linking map if truly new
            self.linking_map.append(entry)
            self.log.debug(
                f"🚀 HASH OPTIMIZATION: Added entry to linking map and indexes - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )
        else:
            self.log.debug(
                f"🔄 HASH OPTIMIZATION: Duplicate entry updated - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )

        # Update performance metrics
        stats = self.hash_optimizer.get_index_stats()
        if stats["total_lookups"] > 0 and stats["total_lookups"] % 100 == 0:
            self.log.info(
                f"🚀 HASH PERFORMANCE: {stats['total_lookups']} lookups, {stats['cache_hit_rate']:.1f}% hit rate, {stats['performance_improvement']:.1f}x improvement"
            )
```

```python
# FIXED CODE:
    def _add_linking_map_entry_optimized(self, entry: Dict[str, Any]) -> None:
        """
        Add entry to linking map with hash index optimization.
        ...
        """
        # Add to hash indexes first to detect duplicates
        is_new_entry = self.hash_optimizer.add_entry(entry)

        if is_new_entry:
            # Only append to main linking map if truly new
            self.linking_map.append(entry)
            self.log.debug(
                f"🚀 HASH OPTIMIZATION: Added entry to linking map and indexes - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )
            
            # 🚨 FIX ISS-001: Periodic save to prevent data loss
            # Save every 10 entries OR on first entry to ensure data persists
            linking_map_size = len(self.linking_map)
            if linking_map_size == 1 or linking_map_size % 10 == 0:
                try:
                    self._save_linking_map(self.supplier_name)
                    self.log.info(f"💾 SAFETY SAVE: Linking map saved at {linking_map_size} entries")
                except Exception as save_err:
                    self.log.error(f"⚠️ CRITICAL: Failed to save linking map: {save_err}")
        else:
            self.log.debug(
                f"🔄 HASH OPTIMIZATION: Duplicate entry updated - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
            )

        # Update performance metrics
        stats = self.hash_optimizer.get_index_stats()
        if stats["total_lookups"] > 0 and stats["total_lookups"] % 100 == 0:
            self.log.info(
                f"🚀 HASH PERFORMANCE: {stats['total_lookups']} lookups, {stats['cache_hit_rate']:.1f}% hit rate, {stats['performance_improvement']:.1f}x improvement"
            )
```

---

### Fix 4: Workflow Mode Switch (ISS-004) - **MISSING FROM ORIGINAL PLAN**

**Problem:** At Category 8, system switches from category-scoped (15 products) to bulk mode (3312 products).

**Evidence from logs:**
```
Log 201223: "FROZEN DENOMINATOR: All-Cake-crafts-and-sweet-trees = 15"
Log 201223: "PROCESSING: 3312 products ready for Amazon extraction"
```

**File:** `tools/passive_extraction_workflow_latest.py`  
**Location:** Method `_process_chunk_with_main_workflow_logic`, Line 10924

```python
# CURRENT CODE (Lines 10924-10958):
    async def _process_chunk_with_main_workflow_logic(
        self, products: List[Dict[str, Any]], max_products_per_cycle: int, *, category_urls
    ) -> List[Dict[str, Any]]:
        """Process products using the same detailed logic as main workflow (not simplified batch processing)"""
        profitable_results = []

        # Filter and prepare products for analysis (same as main workflow)
        valid_products = [
            p
            for p in products
            if p.get("title")
            ...
        ]
        ...
        self.log.info(
            f"📍 PROCESSING: {len(price_filtered_products)} products ready for Amazon extraction"
        )
```

```python
# FIXED CODE:
    async def _process_chunk_with_main_workflow_logic(
        self, products: List[Dict[str, Any]], max_products_per_cycle: int, *, category_urls
    ) -> List[Dict[str, Any]]:
        """Process products using the same detailed logic as main workflow (not simplified batch processing)"""
        profitable_results = []

        # 🚨 FIX ISS-004: Validate products belong to expected categories BEFORE processing
        if category_urls:
            normalized_cats = set()
            for cu in (category_urls if isinstance(category_urls, list) else [category_urls]):
                try:
                    normalized_cats.add(normalize_url(cu))
                except Exception:
                    normalized_cats.add(str(cu))
            
            # Filter to only products matching the expected categories
            original_count = len(products)
            category_filtered = []
            for p in products:
                src = p.get("source_url") or p.get("category_url") or ""
                try:
                    n_src = normalize_url(src) if src else ""
                except Exception:
                    n_src = src
                if not normalized_cats or n_src in normalized_cats:
                    category_filtered.append(p)
            
            if len(category_filtered) != original_count:
                self.log.warning(
                    f"⚠️ ISS-004 CATEGORY SCOPE FILTER: {original_count} → {len(category_filtered)} products\n"
                    f"   Removed {original_count - len(category_filtered)} products from other categories"
                )
            products = category_filtered

        # Filter and prepare products for analysis (same as main workflow)
        valid_products = [
            p
            for p in products
            if p.get("title")
            ...
        ]
        ...
        self.log.info(
            f"📍 PROCESSING: {len(price_filtered_products)} products ready for Amazon extraction"
        )
```

---

### Fix 5: Invalid Product Index Validation (ISS-005) - **MISSING FROM ORIGINAL PLAN**

**Problem:** Resume pointer shows `prod_idx=576/15` which is mathematically impossible.

**File:** `utils/fixed_enhanced_state_manager.py`  
**Location:** Method `commit_amazon_progress`, Line 1635

```python
# CURRENT CODE (Lines 1635-1658):
    def commit_amazon_progress(self, *, cat_idx: int, queue_idx: int,
                               total_cats: int, cat_url: str, queue_len: int) -> None:
        """Thread-safe atomic Amazon-phase commit (queue-relative cursor)."""
        # Emit a clear progress line with clamp preview and normalized URL
        original_idx = int(queue_idx)
        clamped_idx = original_idx
        if queue_len is not None and queue_len >= 0:
            if clamped_idx < 0:
                clamped_idx = 0
            elif clamped_idx > queue_len:
                clamped_idx = queue_len
```

```python
# FIXED CODE:
    def commit_amazon_progress(self, *, cat_idx: int, queue_idx: int,
                               total_cats: int, cat_url: str, queue_len: int) -> None:
        """Thread-safe atomic Amazon-phase commit (queue-relative cursor)."""
        
        # 🚨 FIX ISS-005: Detect impossible index values BEFORE processing
        # This catches bulk mode corruption (ISS-004) that causes 576/15 scenarios
        if queue_len is not None and queue_len > 0 and queue_idx >= queue_len:
            self.log.error(
                f"🚨 ISS-005 INVALID INDEX DETECTED:\n"
                f"   prod_idx={queue_idx} but queue_len={queue_len}\n"
                f"   This indicates bulk mode corruption (ISS-004)\n"
                f"   Clamping to last valid index: {queue_len - 1}"
            )
            queue_idx = queue_len - 1
        
        # Emit a clear progress line with clamp preview and normalized URL
        original_idx = int(queue_idx)
        clamped_idx = original_idx
        if queue_len is not None and queue_len >= 0:
            if clamped_idx < 0:
                clamped_idx = 0
            elif clamped_idx > queue_len:
                clamped_idx = queue_len
```

---

### Fix 6: State Counter Consolidation (ISS-007) - **MISSING FROM ORIGINAL PLAN**

**Problem:** Multiple counters disagree:
- `gap_processing.processed`: 392
- `amazon_products_completed`: 394  
- Resume pointer: 298
- Linking map: 0

**File:** `utils/fixed_enhanced_state_manager.py`  
**Location:** Method `perform_startup_analysis`, after Line 474

```python
# CURRENT CODE (Lines 471-476):
        log.info("📍 STARTUP ANALYSIS: Beginning comprehensive state analysis...")

        # Calculate file-grounded totals
        file_grounded_data = self._calculate_file_grounded_totals()

        # Toggle: allow disabling reverse gap heuristic...
```

```python
# FIXED CODE:
        log.info("📍 STARTUP ANALYSIS: Beginning comprehensive state analysis...")

        # Calculate file-grounded totals
        file_grounded_data = self._calculate_file_grounded_totals()
        
        # 🚨 FIX ISS-007: Reconcile all counters using linking_map as single source of truth
        linking_map_count = file_grounded_data.get("linking_map_count", 0)
        
        sp = self.state_data.get("system_progression", {})
        amazon_completed = sp.get("amazon_products_completed", 0)
        
        gap = self.state_data.get("gap_processing", {})
        gap_processed = gap.get("gap_products_processed", 0)
        
        # Detect counter mismatches
        counters_match = (linking_map_count == amazon_completed == gap_processed)
        if not counters_match:
            log.warning(
                f"⚠️ ISS-007 COUNTER MISMATCH DETECTED:\n"
                f"   linking_map_count:        {linking_map_count}\n"
                f"   amazon_products_completed: {amazon_completed}\n"
                f"   gap_products_processed:    {gap_processed}\n"
                f"   Action: Aligning all counters to linking_map ({linking_map_count})"
            )
            # Align all counters to linking_map (single source of truth)
            sp["amazon_products_completed"] = linking_map_count
            gap["gap_products_processed"] = linking_map_count
            
            # Also update category completion status
            ccs = gap.get("category_completion_status", {})
            if ccs:
                ccs["processed"] = linking_map_count

        # Toggle: allow disabling reverse gap heuristic...
```

---

## 📋 Summary: All Fixes

| # | Issue ID | File | Line | Fix Type |
|---|----------|------|------|----------|
| 1A | ISS-003 | `passive_extraction_workflow_latest.py` | 7678 | Comment out `queue.sort()` |
| 1B | ISS-003 | `passive_extraction_workflow_latest.py` | ~2304 | Add sort after filtering |
| 2 | ISS-002/006 | `passive_extraction_workflow_latest.py` | ~7852 | Align denominator with queue |
| 3 | ISS-001 | `passive_extraction_workflow_latest.py` | 1644 | Periodic linking map save |
| 4 | ISS-004 | `passive_extraction_workflow_latest.py` | 10924 | Category scope filter |
| 5 | ISS-005 | `fixed_enhanced_state_manager.py` | 1635 | Index validation |
| 6 | ISS-007 | `fixed_enhanced_state_manager.py` | ~474 | Counter reconciliation |

---

## 🔍 Verification Commands

After applying fixes, run these commands to verify:

```bash
# Verify Fix 1A applied (sort removed)
grep -n "queue.sort" passive_extraction_workflow_latest.py | grep -v "#"

# Verify Fix 1B applied (sort added to initial)
grep -A5 "price_filtered_products.sort" passive_extraction_workflow_latest.py

# Verify Fix 2 applied (denominator alignment)
grep -n "DENOMINATOR MISMATCH" passive_extraction_workflow_latest.py

# Verify Fix 3 applied (periodic save)
grep -n "SAFETY SAVE" passive_extraction_workflow_latest.py

# Verify Fix 4 applied (category scope)
grep -n "ISS-004 CATEGORY SCOPE" passive_extraction_workflow_latest.py

# Verify Fix 5 applied (index validation)
grep -n "ISS-005 INVALID INDEX" fixed_enhanced_state_manager.py

# Verify Fix 6 applied (counter reconciliation)
grep -n "ISS-007 COUNTER MISMATCH" fixed_enhanced_state_manager.py
```

---

## ⚠️ Additional Information Needed

None. All fixes are complete with verified code locations and correct method signatures.

---

## 🧪 Testing Protocol

1. **Test Resume Sort (Fixes 1A/1B):**
   - Run workflow, process 10 products, interrupt
   - Resume and verify product #11 is processed (not a different product)

2. **Test Denominator (Fix 2):**
   - Check logs for "DENOMINATOR MISMATCH DETECTED" if cache differs from state
   - Verify progress shows X/397 (actual count, not frozen 401)

3. **Test Data Loss (Fix 3):**
   - Process 15 products, force-kill process (kill -9)
   - Verify `linking_map.json` has 10-15 entries (saved at 10)

4. **Test Category Scope (Fix 4):**
   - Process Category 8 (15 products)
   - Verify log shows "ISS-004 CATEGORY SCOPE FILTER" if filtering occurred
   - Verify it processes exactly 15, not 3312

5. **Test Index Validation (Fix 5):**
   - Resume with corrupted state (prod_idx > queue_len)
   - Verify log shows "ISS-005 INVALID INDEX" and clamping

6. **Test Counter Reconciliation (Fix 6):**
   - Start with mismatched counters in state file
   - Check startup logs for "ISS-007 COUNTER MISMATCH DETECTED"
   - Verify all counters aligned to linking_map count
