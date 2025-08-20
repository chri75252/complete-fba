# CRITICAL RESUME LOGIC IMPLEMENTATION REQUIREMENTS

## 🚨 URGENT IMPLEMENTATION NEEDED

### **FRESH vs RESUMPTION RUN DETECTION**

#### Fresh/New Run (No Processing State File)
- **Condition**: No processing state file exists
- **Action**: Start from first URL (index 0) in poundwholesale_categories.json
- **Category**: "https://www.poundwholesale.co.uk/toys/wholesale-battery-operated-toys"
- **Product Index**: 0 (start from first product)

#### Resumption Run (Processing State File Exists)
- **Condition**: Processing state file exists with populated indexes
- **Action**: Resume from exact interruption point using system_progression
- **NO**: Do not start from beginning
- **YES**: Continue from where left off

### **PRIMARY RESUME SOURCE: system_progression Section**

**CRITICAL**: system_progression takes precedence over legacy supplier_extraction_progress

```json
{
  "system_progression": {
    "current_category_index": 5,           // ← RESUME MARKER: Which category to continue
    "current_product_index_in_category": 10, // ← RESUME MARKER: Which product within category
    "current_phase": "supplier",           // ← RESUME MARKER: Which phase was interrupted
    "current_category_url": "https://...", // ← VALIDATION: Exact category URL for consistency check
    "total_categories": 25,                // Context: Total categories to process
    "total_products_in_current_category": 100 // Context: Products in current category
  }
}
```

### **PHASE DETECTION LOGIC**

#### Supplier Website Extraction Interruption
- **When**: `current_phase == "supplier"`
- **Resume Action**: Continue supplier product extraction
- **Resume Point**:
  - Category: `current_category_index` (e.g., category 5)
  - Product: `current_product_index_in_category` (e.g., product 10 within that category)
  - URL: Validate against `current_category_url`

#### Amazon Detail Extraction Interruption
- **When**: `current_phase == "amazon"`
- **Resume Action**: Continue Amazon analysis/linking
- **Resume Point**:
  - Category: `current_category_index` (e.g., category 5)
  - Product: `current_product_index_in_category` (e.g., product 10 within that category)
  - URL: Validate against `current_category_url`

### **LEGACY SECTION: supplier_extraction_progress**

**Used for backward compatibility only** - system prefers system_progression

```json
{
  "supplier_extraction_progress": {
    "current_category_index": 5,          // ← LEGACY: Mirrors system_progression
    "last_processed_index": 10,           // ← LEGACY: Product index (less reliable)
    "progress_index": 10                  // ← LEGACY: Alternative product index
  }
}
```

### **RESUME DECISION MATRIX**

| Scenario | Primary Source | Fallback Source | Action |
|----------|---------------|-----------------|---------| 
| Both sections exist | system_progression | supplier_extraction_progress | Use system_progression values |
| Only legacy exists | supplier_extraction_progress | None | Use legacy values |
| Inconsistent values | system_progression | None | system_progression takes precedence |
| Missing phase info | Infer from context | Default to "supplier" | Start with supplier phase |

### **SPECIFIC RESUME ALGORITHM**

```python
def get_resume_point():
    # Primary source
    sp = state_data.get("system_progression", {})
    
    if sp:
        return {
            'category_index': sp.get("current_category_index", 0),
            'product_index': sp.get("current_product_index_in_category", 0), 
            'phase': sp.get("current_phase", "supplier"),
            'category_url': sp.get("current_category_url", "")
        }
    
    # Fallback to legacy
    sep = state_data.get("supplier_extraction_progress", {})
    return {
        'category_index': sep.get("current_category_index", 0),
        'product_index': sep.get("last_processed_index", 0),
        'phase': "supplier",  # Default assumption
        'category_url': sep.get("current_category_url", "")
    }
```

### **KEY RESUME INDEXES SUMMARY**

#### Primary Resume Indexes (from system_progression):
- `current_category_index` - Which category (0-based)
- `current_product_index_in_category` - Which product within category (0-based)
- `current_phase` - "supplier" or "amazon" phase
- `current_category_url` - URL validation/consistency check

#### Legacy Resume Indexes (from supplier_extraction_progress):
- `current_category_index` - Which category (mirrors primary)
- `last_processed_index` - Which product (less reliable naming)
- `progress_index` - Alternative product index (redundant)

### **PHASE CONTINUATION LOGIC**

#### Supplier Phase Resume:
- Continue extracting products from supplier website
- Start at `current_product_index_in_category` within `current_category_index`
- Complete supplier extraction before moving to Amazon phase

#### Amazon Phase Resume:
- Continue Amazon detail extraction/linking
- Start at `current_product_index_in_category` within `current_category_index`
- Process products that need Amazon analysis

### **CRITICAL IMPLEMENTATION NOTES**

1. **File Existence Check**: Must check if processing state file exists to determine fresh vs resumption run
2. **system_progression Priority**: Always prefer system_progression over supplier_extraction_progress
3. **Phase Awareness**: Use current_phase to determine which phase was interrupted
4. **URL Validation**: Validate current_category_url for consistency
5. **Exact Resume**: Resume at exact product within exact category, not from beginning

**USER REQUEST**: "the system should start from the first URL only if it is a 'fresh/new' run (meaning no processing state file exists). if the run is a resumption run (meaning system got interrupted, and we are re-launching the system (hence there is an existing processing state file populated with multiple indexes) the system should" use the above logic.

**CURRENT ISSUE**: System failed right away, need to implement this logic first, then address latest error in log output.