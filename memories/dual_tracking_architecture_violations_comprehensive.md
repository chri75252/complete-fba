# DUAL TRACKING ARCHITECTURE VIOLATIONS - COMPREHENSIVE FIX REQUIRED

## 🚨 ROOT CAUSE: ARCHITECTURAL VIOLATION

The system is designed with **dual tracking architecture** per docs/PROGRESS_TRACKING_AUDIT_REPORT.md:

### CORRECT ARCHITECTURE:
1. **system_progression**: Canonical source for resumption (system internal tracking)
2. **supplier_extraction_progress**: Legacy compatibility only (user display derived)
3. **update_progression_unified()**: Atomic updates to both sections

### CURRENT VIOLATIONS:
The workflow is calling `update_supplier_extraction_progress()` directly instead of `update_progression_unified()`, violating the dual tracking architecture.

## 🔍 ALL VIOLATION LOCATIONS IDENTIFIED

**File**: `tools/passive_extraction_workflow_latest.py`

### Violation 1: Line ~4630
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    correct_index, len(category_urls_to_scrape), category_url=expected_url
)
```

### Violation 2: Line ~4640  
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    selected_index, len(category_urls_to_scrape), category_url=selected_category_url
)
```

### Violation 3: Line ~4650
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    category_index, len(category_urls), category_url=category_url
)
```

### Violation 4: Line ~6890
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    category_index=next_category_index,
    total_categories=len(category_urls_to_scrape),
    category_url=next_category_url,
    extraction_phase='supplier'
)
```

### Violation 5: Line ~6900 (duplicate)
```python  
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    category_index=next_category_index,
    total_categories=len(category_urls_to_scrape),
    category_url=next_category_url, 
    extraction_phase='supplier'
)
```

### Violation 6: Line ~6910 (duplicate)
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    category_index=next_category_index,
    total_categories=len(category_urls_to_scrape),
    category_url=next_category_url,
    extraction_phase='supplier'  
)
```

### Violation 7: Line 7170 (THE CRITICAL ONE)
```python
# VIOLATION:
self.state_manager.update_supplier_extraction_progress(
    category_index=batch_num,
    total_categories=len(category_urls_to_scrape),  # Just fixed this line
    subcategory_index=i,
    total_subcategories=len(batch_products),
    batch_number=batch_num,
    total_batches=total_batches,
)
```

## 🔧 COMPREHENSIVE FIX STRATEGY

### Replace ALL occurrences with update_progression_unified():

**BEFORE (ALL VIOLATIONS)**:
```python
self.state_manager.update_supplier_extraction_progress(
    category_index=X,
    total_categories=Y,
    # ... other params
)
```

**AFTER (CORRECT ARCHITECTURE)**:
```python
self.state_manager.update_progression_unified(
    current_category_index=X,
    total_categories=Y,
    # ... other params mapped to correct names
)
```

## 📋 PARAMETER MAPPING
```python
# update_supplier_extraction_progress → update_progression_unified
category_index → current_category_index
total_categories → total_categories (same)
subcategory_index → current_product_index_in_category  
total_subcategories → total_products_in_current_category
category_url → current_category_url
extraction_phase → current_phase
```

## 🎯 WHY THIS FIXES THE BUG

1. **Atomic Updates**: update_progression_unified() updates BOTH system_progression AND supplier_extraction_progress atomically
2. **Canonical Source**: system_progression becomes the single source of truth for resumption
3. **Proper Values**: Uses correct total_categories consistently across both sections
4. **Dual Tracking**: Maintains proper separation between system internal tracking vs user display
5. **Mathematical Consistency**: Prevents state corruption where total_categories=1 instead of 233

## 🏗️ ARCHITECTURAL COMPLIANCE

After this fix:
- ✅ system_progression: Used for resumption (system internal tracking)
- ✅ supplier_extraction_progress: Updated atomically (legacy compatibility) 
- ✅ User progress: Calculated on-demand from system_progression
- ✅ Single source of truth: system_progression is canonical
- ✅ No more state drift: Atomic updates prevent inconsistencies

This comprehensive fix addresses the architectural violation the user identified and ensures proper dual tracking implementation.