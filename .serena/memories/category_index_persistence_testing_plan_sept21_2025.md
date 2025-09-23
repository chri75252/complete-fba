# Category Index Persistence Testing Plan - September 21, 2025

## Context
Following our critical fixes to the `mark_category_completed` method in `utils/fixed_enhanced_state_manager.py`, we need to verify that category index persistence and counter preservation work correctly between system interruptions.

## Root Cause Fixed
**ISSUE**: `mark_category_completed()` was unconditionally resetting all progress counters to 0:
```python
# BEFORE (BROKEN):
sp["supplier_products_completed"] = 0
sp["supplier_products_needing_extraction"] = 0
sp["amazon_products_completed"] = 0
sp["amazon_products_needing_analysis"] = 0

# AFTER (FIXED):
# Only reset per-category state, preserve global progress counters
sp["category_denominator_frozen"] = False
sp["current_category_url"] = ""
```

## Critical Files to Monitor

### 1. Processing State File
**Path**: `OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json`
**Key Fields**:
```json
{
  "system_progression": {
    "persistent_category_index": 0,  // MUST advance 0→1→2→3
    "supplier_products_completed": 0, // MUST preserve between runs
    "amazon_products_completed": 0,   // MUST preserve between runs
    "supplier_products_needing_extraction": 6,
    "amazon_products_needing_analysis": 6,
    "current_phase": "supplier",
    "category_denominator_frozen": false,
    "current_category_url": ""
  }
}
```

### 2. Debug Log Files
**Pattern**: `logs/debug/run_custom_poundwholesale_YYYYMMDD_HHMMSS.log`
**Key Log Messages**:
- `"✅ Category marked as completed: <url> → next index=<N>"`
- `"RESUME PTR: phase=supplier cat_idx=<N>/231 prod_idx=<M>"`
- `"Processing chunk <N>: categories <start>-<end>"`
- `"📊 WORK DEFINED (resume): denominators frozen → not overwriting totals/completed"`

## Step-by-Step Testing Protocol

### TEST 1: Initial Category Advancement
```bash
# Clean start
rm "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"

# Start system
python run_custom_poundwholesale.py

# Monitor initial state
jq '.system_progression.persistent_category_index' "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"
# Expected: 0

# Process 3-5 products, then interrupt (Ctrl+C)
# Check state preservation
jq '.system_progression | {pci: .persistent_category_index, sup_done: .supplier_products_completed, amz_done: .amazon_products_completed}' "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"
# Expected: pci=0, sup_done=4, amz_done=0 (values preserved, not reset)
```

### TEST 2: Category Completion and Index Advancement
```bash
# Resume system
python run_custom_poundwholesale.py

# Monitor for category completion in logs
tail -f logs/debug/run_custom_poundwholesale_*.log | grep "Category marked as completed"
# Expected: "✅ Category marked as completed: <url> → next index=1"

# Verify index advanced
jq '.system_progression.persistent_category_index' "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"
# Expected: 1

# Verify counters NOT reset
jq '.system_progression | {sup_done: .supplier_products_completed, amz_done: .amazon_products_completed}' "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"
# Expected: Values preserved, NOT reset to 0
```

### TEST 3: Resume Logic Verification
```bash
# Process into category 1, then interrupt again
# Check resume pointer on restart
python run_custom_poundwholesale.py 2>&1 | grep "RESUME PTR"
# Expected: "RESUME PTR: phase=supplier cat_idx=1/231 prod_idx=<N>"

# Verify chunk processing alignment
tail -f logs/debug/run_custom_poundwholesale_*.log | grep "Processing chunk"
# Expected: "Processing chunk 2: categories 2-2" (matches cat_idx=1+1)
```

## Critical Success Criteria

### ✅ MUST PASS:
1. **Category Index Progression**: `persistent_category_index` advances 0→1→2→3 after each category completion
2. **Counter Persistence**: `supplier_products_completed` and `amazon_products_completed` NEVER reset to 0 between runs
3. **Resume Accuracy**: `RESUME PTR: cat_idx=N` matches actual category being processed
4. **Chunk Alignment**: `Processing chunk N` matches `cat_idx=N-1` (accounting for 0-based indexing)
5. **State Preservation**: Interrupting and resuming preserves all progress counters

### ❌ FAILURE INDICATORS:
1. **Index Stuck**: `persistent_category_index` remains 0 despite category completions
2. **Counter Reset**: Any completed/needing counters reset to 0 unexpectedly
3. **Resume Mismatch**: `RESUME PTR: cat_idx=0` when system should be on category 2+
4. **Chunk Disconnect**: `Processing chunk 3` but `cat_idx=0`

## Monitoring Commands

### Real-Time State Monitoring:
```bash
# Watch processing state changes
watch -n 2 'jq ".system_progression | {persistent_category_index, supplier_products_completed, amazon_products_completed, current_phase}" "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"'

# Monitor log for key events
tail -f logs/debug/run_custom_poundwholesale_*.log | grep -E "(RESUME PTR|Category marked as completed|Processing chunk)"

# Quick state check
jq '.system_progression | {pci: .persistent_category_index, sup_done: .supplier_products_completed, amz_done: .amazon_products_completed}' "OUTPUTS/CACHE/poundwholesale_co_uk_processing_state.json"
```

## Expected Behavior Flow

### Fresh Start → First Interruption:
```
Start: persistent_category_index=0, supplier_products_completed=0
Process: Category 0, products 0→4 (5 products completed)
Interrupt: persistent_category_index=0, supplier_products_completed=5 ✅ PRESERVED
```

### Resume → Category Completion:
```
Resume: RESUME PTR: cat_idx=0, prod_idx=5
Continue: Process remaining products in category 0
Complete: ✅ Category marked as completed: <url> → next index=1
Result: persistent_category_index=1, supplier_products_completed=5 ✅ PRESERVED
```

### Next Category → Second Interruption:
```
Start: Processing chunk 2: categories 2-2, persistent_category_index=1
Process: Category 1, add 3 more products (total=8)
Interrupt: persistent_category_index=1, supplier_products_completed=8 ✅ PRESERVED
```

## Fixed Implementation Details

### Enhanced Method Signature:
```python
def mark_category_completed(self, category_url: str, absolute_cat_index: int = None):
```

### Fixed Index Advancement Logic:
```python
if absolute_cat_index is not None:
    sp["persistent_category_index"] = int(absolute_cat_index) + 1
else:
    sp["persistent_category_index"] = int(sp.get("persistent_category_index", 0)) + 1
```

### Updated Workflow Calls:
- Line 5165: `self.state_manager.mark_category_completed(category_url, absolute_cat_index)`
- Line 5415: `self.state_manager.mark_category_completed(category_url, absolute_cat_index)`
- Line 6973: `self.state_manager.mark_category_completed(category_url, category_index - 1)`

## Guards and Clamps Verified Working

### WORK DEFINED Block (lines 5436-5446):
```python
if not (frozen or prior_freeze or prior_work):
    sp["supplier_products_needing_extraction"] = supplier_total
    sp["amazon_products_needing_analysis"] = amazon_total
    sp["supplier_products_completed"] = 0  # only for brand-new category
    sp["amazon_products_completed"] = 0    # only for brand-new category
else:
    self.log.info("📊 WORK DEFINED (resume): denominators frozen → not overwriting totals/completed")
```

This guard prevents overwriting existing progress when resuming.

## Status
- ✅ **PRIMARY BUG FIXED**: Category index advancement logic corrected
- ✅ **COUNTER PERSISTENCE FIXED**: Removed unconditional resets from mark_category_completed
- ⏳ **TESTING NEEDED**: Verify fixes work end-to-end with interruptions
- ⏳ **VALIDATION PENDING**: Confirm resume logic works with correct indexes

## Next Steps
1. Run the testing protocol above
2. Verify all success criteria are met
3. Document any remaining issues for further surgical fixes
4. Create backup before testing to preserve current stable state