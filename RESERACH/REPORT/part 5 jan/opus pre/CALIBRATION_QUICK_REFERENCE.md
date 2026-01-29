# CALIBRATION QUICK REFERENCE
## Part 5 Jan - Configuration Snippet

**Date:** 2026-01-05  
**Status:** 🟡 READY WITH WARNINGS (Critical EAN mismatch issues detected)

---

## 📋 COPY-PASTE CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION (Part 5 Jan) ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pc', 'pcs', 'pieces', 'pk'],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'ft', 'g', 'inch', 'kg', 'm', 'ml', 'mm'],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True
}
```

---

## 🚨 CRITICAL WARNINGS

### **EAN/Title Mismatch Crisis**
- **8 out of 10** first rows have completely unrelated Amazon titles
- Examples:
  - Supplier: "GLOSS PAINT 300ML" → Amazon: "LG 48-Inch OLED TV"
  - Supplier: "BIRTHDAY BADGE" → Amazon: "Motorola phone"
  - Supplier: "WASHING UP BOWL" → Amazon: "Hyundai Leaf Blower"

### **Impact:**
- ❌ Brand matching will fail (Amazon product is different)
- ❌ Pack size comparison is meaningless (unrelated products)  
- ❌ Profit calculations may use wrong Amazon pricing
- ❌ VERIFIED/HIGHLY_LIKELY categorization unreliable

### **Required Action Before Main Analysis:**
1. Validate EAN column accuracy
2. Consider using ASIN as primary identifier
3. Re-scrape Amazon data with correct identifiers
4. OR run in "supplier-only" mode (no Amazon validation)

---

## ✅ SAFE PATTERNS DETECTED

| Pattern Type | Status | Details |
|--------------|--------|---------|
| Explicit Units | ✅ Found | pack, pc, pcs, pieces, pk |
| Trailing Numbers | ⚠️ Detected | 3 examples (use with caution) |
| Leading Multipliers | ✗ None | Not used by this supplier |
| Capacity Multipacks | ✗ None | No "3 x 400ml" patterns found |
| Spec Multipliers | ✗ None | No "2x magnification" patterns |
| Brand Position | ✅ Consistent | 93% at start (ALL CAPS) |
| Sales Column | ✅ Clean | `bought_in_past_month` (numeric) |
| Dimensions | ✅ Found | cm, ft, g, inch, kg, m, ml, mm |

---

## 📊 KEY STATISTICS

- **Rows Analyzed:** 50
- **Explicit Pack Units:** 5 types
- **Brand Consistency:** 93% (28/30 at start)
- **Sales Data Quality:** Clean (numeric)
- **EAN Match Quality:** ⚠️ **20%** (only 2/10 look correct)

---

## 🎯 USAGE INSTRUCTIONS

1. **For main analysis script:**
   - Copy the configuration block above
   - Paste into your script's calibration section
   - The config will auto-tune parsing logic

2. **Before running analysis:**
   - MUST address EAN mismatch issues
   - Consider data quality gate: require 80%+ valid EAN matches

3. **Trailing number pattern:**
   - Enabled, but validate results manually
   - Could be quantities OR design variants (e.g., "BADGE GIRL 3")

4. **Model number shield:**
   - Numbers ≥ 100 should not trigger pack quantity logic
   - Unless accompanied by explicit units

---

## 📄 FILES GENERATED

1. `calibration_analysis.py` - Full analysis script
2. `CALIBRATION_REPORT_part5jan.md` - Detailed findings report
3. `CALIBRATION_QUICK_REFERENCE.md` - This file

---

**Last Updated:** 2026-01-05  
**Next Step:** Review full report → Fix EAN data → Run main analysis
