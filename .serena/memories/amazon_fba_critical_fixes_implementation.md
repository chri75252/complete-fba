# Amazon FBA System - Critical Fixes Implementation Plan

## 🚨 IMMEDIATE PRIORITY: Dual Tracking Architecture Fix

### **Problem Identified**
8 locations in `tools/passive_extraction_workflow_latest.py` use wrong state update method:
- Using: `update_supplier_extraction_progress()` (WRONG)
- Should use: `update_progression_unified()` (CORRECT)

### **Impact**
- Breaks state synchronization between `system_progression` and `supplier_extraction_progress` 
- Causes resume functionality failures
- Leads to processing interruptions

### **Surgical Implementation Required**

**File**: `tools/passive_extraction_workflow_latest.py`
**8 locations to fix:**

1. Line 1380-1382: Auto-recovery category URL correction
2. Line 1404-1405: Auto-recovery category selection sync  
3. Line 3829-3831: Current category processing update
4. Line 3889: Wrong method variant `update_supplier_extraction_progress_new()`
5. Line 4679-4680: Next category progression logic #1
6. Line 4698-4699: Next category progression logic #2
7. Line 4752-4753: Next category progression logic #3
8. Line 7168-7170: Amazon analysis phase

**Parameter Mapping Pattern:**
```python
# BEFORE (WRONG):
self.state_manager.update_supplier_extraction_progress(
    category_index, total_categories, category_url=url
)

# AFTER (CORRECT):
self.state_manager.update_progression_unified(
    current_category_index=category_index,
    total_categories=total_categories,
    current_category_url=url
)
```

### **System Behavior Rules**
- NEVER delete cache files - system uses "reverse gap processing"
- linking_map.json is resume data source (8818 entries)
- total_categories MUST equal 233 (corruption indicator if ≠ 233)
- `system_progression` section is canonical source for resumption

### **Implementation Steps**
1. Create backup before changes
2. Replace all 8 method calls with parameter mapping
3. Test state synchronization
4. Verify resume functionality works