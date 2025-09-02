# CRITICAL RESUME LOGIC REQUIREMENTS - Amazon FBA Agent System

## 🚨 FUNDAMENTAL RESUME LOGIC PRINCIPLES

### **FRESH START DETECTION**
- **Fresh Run**: NO processing state file exists → Start from URL index 0 (first category in config)
- **Resume Run**: Processing state file EXISTS with valid data → Use system_progression resume markers

### **INCORRECT CURRENT BEHAVIOR (TO FIX)**
The system is incorrectly using `category_completion_status` count to determine starting position:
- System counting 92-93 entries in `category_completion_status`
- Then starting from URL index 93-94 in `poundwholesale_categories.json`
- **THIS IS WRONG** - `category_completion_status` should NOT determine starting position

## 🎯 PRIMARY RESUME SOURCE: system_progression Section

**system_progression takes ABSOLUTE PRECEDENCE over all other sources**

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

## 🔄 PHASE DETECTION LOGIC

### **Supplier Website Extraction Interruption**
- **When**: `current_phase == "supplier"`
- **Resume Action**: Continue supplier product extraction
- **Resume Point**:
  - Category: `current_category_index` (e.g., category 5)
  - Product: `current_product_index_in_category` (e.g., product 10 within that category)
  - URL: Validate against `current_category_url`

### **Amazon Detail Extraction Interruption**
- **When**: `current_phase == "amazon"`
- **Resume Action**: Continue Amazon analysis/linking
- **Resume Point**:
  - Category: `current_category_index` (e.g., category 5)
  - Product: `current_product_index_in_category` (e.g., product 10 within that category)
  - URL: Validate against `current_category_url`

## 📋 LEGACY SECTION: supplier_extraction_progress
**Used for backward compatibility only - system prefers system_progression**

```json
{
  "supplier_extraction_progress": {
    "current_category_index": 5,          // ← LEGACY: Mirrors system_progression
    "last_processed_index": 10,           // ← LEGACY: Product index (less reliable)
    "progress_index": 10                  // ← LEGACY: Alternative product index
  }
}
```

## 🎯 RESUME DECISION MATRIX

| Scenario | Primary Source | Fallback Source | Action |
|----------|---------------|-----------------|---------| 
| Both sections exist | system_progression | supplier_extraction_progress | Use system_progression values |
| Only legacy exists | supplier_extraction_progress | None | Use legacy values |
| Inconsistent values | system_progression | None | system_progression takes precedence |
| Missing phase info | Infer from context | Default to "supplier" | Start with supplier phase |

## 🔧 SPECIFIC RESUME ALGORITHM

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

## 🚨 CRITICAL FIXES NEEDED

1. **STOP using category_completion_status count for resume calculation**
2. **IMPLEMENT proper fresh start detection**
3. **ENFORCE system_progression precedence over all other sources**
4. **VALIDATE resume points against actual config file indices**

## 📍 KEY RESUME INDEXES SUMMARY

**Primary Resume Indexes (from system_progression):**
- `current_category_index` - Which category (0-based)
- `current_product_index_in_category` - Which product within category (0-based)
- `current_phase` - "supplier" or "amazon" phase
- `current_category_url` - URL validation/consistency check

**Legacy Resume Indexes (from supplier_extraction_progress):**
- `current_category_index` - Which category (mirrors primary)
- `last_processed_index` - Which product (less reliable naming)
- `progress_index` - Alternative product index (redundant)

## 🎯 PHASE CONTINUATION LOGIC

**Supplier Phase Resume:**
- Continue extracting products from supplier website
- Start at `current_product_index_in_category` within `current_category_index`
- Complete supplier extraction before moving to Amazon phase

**Amazon Phase Resume:**
- Continue Amazon detail extraction/linking
- Start at `current_product_index_in_category` within `current_category_index`
- Process products that need Amazon analysis

The system uses `current_phase` as the definitive marker to determine whether it was interrupted during supplier extraction or Amazon analysis, then resumes at the exact product position within the exact category.