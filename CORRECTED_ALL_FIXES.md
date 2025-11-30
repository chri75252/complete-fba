================================================================================
CORRECTED UNIFIED DIFF FILE: 6 Issue Fixes
================================================================================
Date: 2025-11-27
Status: REVISED - Fix 1B removed (mutually exclusive with 1A)
Total Fixes: 6
Total Lines: 93 (1 comment + 92 additions)
================================================================================

================================================================================
FIX 1: Remove Resume Sorting (ISS-003)
FILE: tools/passive_extraction_workflow_latest.py
LINE: 7678
CHANGE: Comment out sort operation (1 line)
================================================================================

--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@ -7674,7 +7674,10 @@ class PassiveExtractionWorkflow:
         # Deterministic order
         def _nurl(u): 
             try: return normalize_url(u) if u else ""
             except Exception: return u or ""
-        queue.sort(key=lambda x: _nurl(x.get("url")))
+        # 🚨 FIX ISS-003: REMOVED - Resume must use same discovery order as initial run
+        # Sorting caused index N to point to different products between runs
+        # Evidence: Log 154127 idx 298 ("Sequin Deep Lace...") ≠ Log 155617 idx 298 ("Lovely mixed design...")
+        # queue.sort(key=lambda x: _nurl(x.get("url")))
 
         self.log.info(f"📦 CATEGORY QUEUE: url={ncat} size={len(queue)} allowed_gate={'on' if allowed else 'off'}")
         return queue

================================================================================
FIX 2: Denominator Alignment (ISS-002, ISS-006)
FILE: tools/passive_extraction_workflow_latest.py
LINE: After 7852
CHANGE: Add validation block (20 lines)
================================================================================

--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@ -7849,6 +7849,26 @@ class PassiveExtractionWorkflow:
         products = filtered
         total = len(products)
 
+        # 🚨 FIX ISS-002/ISS-006: Detect and align denominator mismatch
+        frozen_denom = self.state_manager.get_frozen_denominator(category_url)
+        if frozen_denom is not None and frozen_denom != total:
+            self.log.warning(
+                f"⚠️ DENOMINATOR MISMATCH DETECTED:\n"
+                f"   Frozen denominator: {frozen_denom}\n"
+                f"   Actual queue size:  {total}\n"
+                f"   Difference: {frozen_denom - total} products\n"
+                f"   Action: Aligning state to actual queue size ({total})"
+            )
+            # Update frozen_category_denominators map
+            try:
+                nurl = normalize_url(category_url)
+            except Exception:
+                nurl = category_url
+            frozen_cats = self.state_manager.state_data.setdefault("frozen_category_denominators", {})
+            frozen_cats[nurl] = total
+            # Also update system_progression
+            sp_update = self.state_manager.state_data.setdefault("system_progression", {})
+            sp_update["amazon_products_needing_analysis"] = total
+            sp_update["supplier_products_needing_extraction"] = total
+
         sp = self.state_manager.state_data.get("system_progression", {})
         saved_amazon_offset = int(sp.get("amazon_products_completed", 0)) if isinstance(sp.get("amazon_products_completed", 0), (int, float)) else int(sp.get("amazon_products_completed", 0) or 0)

================================================================================
FIX 3: Periodic Linking Map Save (ISS-001)
FILE: tools/passive_extraction_workflow_latest.py
LINE: Inside _add_linking_map_entry_optimized, after line 1659
CHANGE: Add safety save block (10 lines)
================================================================================

--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@ -1656,6 +1656,16 @@ class PassiveExtractionWorkflow:
         if is_new_entry:
             # Only append to main linking map if truly new
             self.linking_map.append(entry)
+            
+            # 🚨 FIX ISS-001: Periodic save to prevent data loss
+            # Evidence: 392 products processed but 0 entries in linking_map.json
+            # Save every 10 entries OR on first entry to ensure data persists
+            linking_map_size = len(self.linking_map)
+            if linking_map_size == 1 or linking_map_size % 10 == 0:
+                try:
+                    self._save_linking_map(self.supplier_name)
+                    self.log.info(f"💾 SAFETY SAVE: Linking map saved at {linking_map_size} entries")
+                except Exception as save_err:
+                    self.log.error(f"⚠️ CRITICAL: Failed to save linking map: {save_err}")
+            
             self.log.debug(
                 f"🚀 HASH OPTIMIZATION: Added entry to linking map and indexes - EAN: {entry.get('supplier_ean', 'N/A')}, URL: {entry.get('supplier_url', 'N/A')}"
             )

================================================================================
FIX 4: Category Scope Filter (ISS-004)
FILE: tools/passive_extraction_workflow_latest.py
LINE: Start of _process_chunk_with_main_workflow_logic, after 10927
CHANGE: Add category validation block (25 lines)
================================================================================

--- a/tools/passive_extraction_workflow_latest.py
+++ b/tools/passive_extraction_workflow_latest.py
@@ -10925,6 +10925,31 @@ class PassiveExtractionWorkflow:
     ) -> List[Dict[str, Any]]:
         """Process products using the same detailed logic as main workflow (not simplified batch processing)"""
         profitable_results = []
+        
+        # 🚨 FIX ISS-004: Validate products belong to expected categories BEFORE processing
+        # Evidence: Category 8 had frozen_denom=15 but processed 3312 products (bulk mode)
+        if category_urls:
+            normalized_cats = set()
+            for cu in (category_urls if isinstance(category_urls, list) else [category_urls]):
+                try:
+                    normalized_cats.add(normalize_url(cu))
+                except Exception:
+                    normalized_cats.add(str(cu))
+            
+            # Filter to only products matching the expected categories
+            original_count = len(products)
+            category_filtered = []
+            for p in products:
+                src = p.get("source_url") or p.get("category_url") or ""
+                try:
+                    n_src = normalize_url(src) if src else ""
+                except Exception:
+                    n_src = src
+                if not normalized_cats or n_src in normalized_cats:
+                    category_filtered.append(p)
+            
+            if len(category_filtered) != original_count:
+                self.log.warning(
+                    f"⚠️ ISS-004 CATEGORY SCOPE FILTER: {original_count} → {len(category_filtered)} products\n"
+                    f"   Removed {original_count - len(category_filtered)} products from other categories"
+                )
+            products = category_filtered
 
         # Filter and prepare products for analysis (same as main workflow)
         valid_products = [

================================================================================
FIX 5: Invalid Index Validation (ISS-005)
FILE: utils/fixed_enhanced_state_manager.py
LINE: Start of commit_amazon_progress, after 1636
CHANGE: Add index validation block (12 lines)
================================================================================

--- a/utils/fixed_enhanced_state_manager.py
+++ b/utils/fixed_enhanced_state_manager.py
@@ -1635,6 +1635,18 @@ class EnhancedStateManager:
     def commit_amazon_progress(self, *, cat_idx: int, queue_idx: int,
                                total_cats: int, cat_url: str, queue_len: int) -> None:
         """Thread-safe atomic Amazon-phase commit (queue-relative cursor)."""
+        
+        # 🚨 FIX ISS-005: Detect impossible index values BEFORE processing
+        # Evidence: Log showed prod_idx=576/15 (mathematically impossible)
+        # This catches bulk mode corruption (ISS-004) that causes index overflow
+        if queue_len is not None and queue_len > 0 and queue_idx >= queue_len:
+            self.log.error(
+                f"🚨 ISS-005 INVALID INDEX DETECTED:\n"
+                f"   prod_idx={queue_idx} but queue_len={queue_len}\n"
+                f"   This indicates bulk mode corruption (ISS-004)\n"
+                f"   Clamping to last valid index: {queue_len - 1}"
+            )
+            queue_idx = queue_len - 1
+        
         # Emit a clear progress line with clamp preview and normalized URL
         original_idx = int(queue_idx)
         clamped_idx = original_idx

================================================================================
FIX 6: Counter Reconciliation (ISS-007)
FILE: utils/fixed_enhanced_state_manager.py
LINE: Inside perform_startup_analysis, after 474
CHANGE: Add reconciliation block (25 lines)
================================================================================

--- a/utils/fixed_enhanced_state_manager.py
+++ b/utils/fixed_enhanced_state_manager.py
@@ -472,6 +472,31 @@ class EnhancedStateManager:
 
         # Calculate file-grounded totals
         file_grounded_data = self._calculate_file_grounded_totals()
+        
+        # 🚨 FIX ISS-007: Reconcile all counters using linking_map as single source of truth
+        # Evidence: gap_processing.processed=392, amazon_completed=394, resume_ptr=298, linking_map=0
+        linking_map_count = file_grounded_data.get("linking_map_count", 0)
+        
+        sp = self.state_data.get("system_progression", {})
+        amazon_completed = sp.get("amazon_products_completed", 0)
+        
+        gap = self.state_data.get("gap_processing", {})
+        gap_processed = gap.get("gap_products_processed", 0)
+        
+        # Detect counter mismatches
+        counters_match = (linking_map_count == amazon_completed == gap_processed)
+        if not counters_match:
+            log.warning(
+                f"⚠️ ISS-007 COUNTER MISMATCH DETECTED:\n"
+                f"   linking_map_count:        {linking_map_count}\n"
+                f"   amazon_products_completed: {amazon_completed}\n"
+                f"   gap_products_processed:    {gap_processed}\n"
+                f"   Action: Aligning all counters to linking_map ({linking_map_count})"
+            )
+            # Align all counters to linking_map (single source of truth)
+            sp["amazon_products_completed"] = linking_map_count
+            gap["gap_products_processed"] = linking_map_count
+            
+            # Also update category completion status
+            ccs = gap.get("category_completion_status", {})
+            if ccs:
+                ccs["processed"] = linking_map_count
 
         # Toggle: allow disabling reverse gap heuristic entirely via config

================================================================================
REMOVED FROM PLAN
================================================================================

FIX 1B (Add Initial Sort) - REMOVED
Reason: Mutually exclusive with Fix 1A
        Applying both would reverse the mismatch, not fix it
        Fix 1A is more surgical (1 line vs 10 lines)

================================================================================
VERIFICATION COMMANDS
================================================================================

# After applying all fixes, run these to verify:

# Fix 1: Verify sort is commented out
grep -n "queue.sort" tools/passive_extraction_workflow_latest.py | grep -v "#"
# Expected: No output (all sort lines commented)

# Fix 2: Verify denominator check added
grep -n "DENOMINATOR MISMATCH" tools/passive_extraction_workflow_latest.py
# Expected: Line ~7855 found

# Fix 3: Verify safety save added
grep -n "SAFETY SAVE" tools/passive_extraction_workflow_latest.py
# Expected: Line ~1667 found

# Fix 4: Verify category filter added
grep -n "ISS-004 CATEGORY SCOPE" tools/passive_extraction_workflow_latest.py
# Expected: Line ~10950 found

# Fix 5: Verify index validation added
grep -n "ISS-005 INVALID INDEX" utils/fixed_enhanced_state_manager.py
# Expected: Line ~1643 found

# Fix 6: Verify counter reconciliation added
grep -n "ISS-007 COUNTER MISMATCH" utils/fixed_enhanced_state_manager.py
# Expected: Line ~485 found

================================================================================
END OF CORRECTED DIFF FILE
================================================================================
