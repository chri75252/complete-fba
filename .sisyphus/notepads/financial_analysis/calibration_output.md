# PREFLIGHT CALIBRATION REPORT - finales26jan.xlsx
**Generated:** 2025-01-30
**File:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finales26jan.xlsx
**Rows Analyzed:** 8 (complete dataset)

---

## FILE INTAKE SUMMARY

- **Columns:** 15 total
- **Primary product column:** `Product (short)`
- **Sales columns detected:** `Badge (SellerAmp) Mine`, `Keepa Sold-30d Mine (now)`
- **Data quality:** 0% missingness across all columns

---

## TASK 1: PACK QUANTITY PATTERNS DETECTED

### 1. Explicit Units (5 occurrences)
- `"pk"` found in:
  - Row 0: Superior trays 32"x26 (10pk)
  - Row 1: Superior 9"x9 + lids (10pk)
  - Row 3: Aladino Jasmine tea lights 50pk
  - Row 6: Superior 9"x13 + lids (5pk)
  - Row 7: Superior 10"x12 + lids (10pk)

### 2. Trailing/Implicit Numbers
- **NOT COMMON:** Only Row 3 has trailing "50" in "50pk" (explicit unit present)
- **Recommendation:** Set `allow_trailing_number_as_qty = False`

### 3. Leading Multipliers
- **NOT FOUND:** No "10x Product" or "6 x Product" patterns detected
- **Recommendation:** Set `leading_multiplier_check = False`

### 4. Dimension Patterns
- **HIGH FREQUENCY:** All rows contain dimension numbers
- **Examples:** 32"x26", 9"x9", 6", 10"x12"
- **CRITICAL:** Dimension numbers must be shielded from quantity parsing
- **Shield keywords needed:** cm, mm, ml, ltr, kg, g, oz, inch, "

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**PATTERN DETECTED:** Row 2 - "Air Wick Mulled Wine (5x30ml)"

- **Format:** N x [capacity][unit] = (5x30ml)
- **Interpretation:** 5 units × 30ml capacity per unit
- **RSU Calculation:** RSU = 5 (pack count), NOT 150 (5×30)
- **Rule:** When pattern is "N x [capacity]ml/g/l", RSU = N only

**Recommendation:** Set `capacity_pattern_as_rsu = True`

---

## TASK 1C: NON-PACK "Nx" SPEC MULTIPLIERS

**NOT DETECTED** in this sample (household/candle products)

No magnification, zoom, or feature multipliers found.

**Spec shield keywords for future protection:**
- magnification, zoom, microscope, scope, times, power

---

## TASK 2: SALES SIGNAL DETECTION

### Primary Sales Column: `Keepa Sold-30d Mine (now)`
- **Format:** "~XXX" or "~XXX (CONFIRMED TOTAL)"
- **Examples:** ~527, ~373, ~237, ~143 (CONFIRMED TOTAL)
- **Parsing required:** Remove "~" prefix and extract numeric value

### Secondary (Badge): `Badge (SellerAmp) Mine`
- **Format:** "XXX+/mo"
- **Examples:** 400+/mo, 200+/mo, 50+/mo, 100+/mo
- **Less precise than Keepa data**

**Recommendation:** Use `"Keepa Sold-30d Mine (now)"` as primary sales_column

---

## TASK 3: BRAND PATTERNS & THRESHOLDS

### Brand Position Analysis
- All products have brand at START (Title Case format)
- **Unique brands:** Superior (50%), Air Wick (12.5%), Aladino (12.5%), Green/Red (25%)
- **Brand format:** TITLE_CASE_AT_START

### Brand Presence Reliability
- **Supplier:** `brand_in_supplier_usually_present = True` (100% have brand)
- **Amazon:** `brand_in_amazon_usually_present = False` (likely inconsistent)
- **Mode:** `brand_sparse_supplier_mode = True`

### Similarity Threshold Calibration
- **Sample size:** 8 rows (small dataset)
- **Product diversity:** Mixed household/candle products
- **Brand diversity:** 5 unique brands
- **Recommended thresholds (relaxed for sparse brand matching):**
  - strong_similarity_threshold: 0.30
  - strong_shared_tokens_threshold: 3
  - very_strong_similarity_threshold: 0.40
  - very_strong_shared_tokens_threshold: 4

### Gate Mode Selection: C_brand_sparse
- **Rationale:** Amazon titles may omit brands that are present in supplier data
- **Requires relaxed matching** to account for brand absence in Amazon titles

---

## TASK 4: CALIBRATION WARNINGS (8 rows)

### Row 0: "Superior trays 32"x26 (10pk)"
- ⚠️ Numbers 32 and 26 are DIMENSIONS (32x26cm), NOT quantities
- ⚠️ Only "10pk" is the pack count
- ⚠️ Risk: Generic logic might interpret 32 or 26 as quantity

### Row 1: "Superior 9"x9 + lids (10pk)"
- ⚠️ Numbers 9 and 9 are DIMENSIONS (9x9 inches), NOT quantities
- ⚠️ Only "10pk" is the pack count
- ⚠️ Risk: Generic logic might interpret 9 as quantity

### Row 2: "Air Wick Mulled Wine (5x30ml)"
- ⚠️ **CAPACITY MULTIPACK PATTERN:** 5x30ml
- ⚠️ RSU should be 5 (pack count), NOT 150 (5×30)
- ⚠️ 30ml describes unit SIZE, not quantity to multiply
- ⚠️ Risk: Generic logic might multiply 5×30=150 (WRONG)

### Row 3: "Aladino Jasmine tea lights 50pk"
- ⚠️ Clear pack format (50pk)
- ⚠️ Risk: If "pk" suffix parsing fails, trailing "50" could be misinterpreted

### Row 4: "Green pillar 6""
- ⚠️ Number 6 is DIMENSION (6 inches), NOT quantity
- ⚠️ No pack count specified - likely single item (RSU=1)
- ⚠️ Risk: Generic logic might interpret 6 as quantity

### Row 5: "Red pillar 6""
- ⚠️ Number 6 is DIMENSION (6 inches), NOT quantity
- ⚠️ No pack count specified - likely single item (RSU=1)
- ⚠️ Risk: Generic logic might interpret 6 as quantity

### Row 6: "Superior 9"x13 + lids (5pk)"
- ⚠️ Numbers 9 and 13 are DIMENSIONS (9x13), NOT quantities
- ⚠️ Only "5pk" is the pack count
- ⚠️ Risk: Generic logic might interpret 9 or 13 as quantity

### Row 7: "Superior 10"x12 + lids (10pk)"
- ⚠️ Numbers 10 and 12 are DIMENSIONS (10x12), NOT quantities
- ⚠️ Only "10pk" is the pack count
- ⚠️ **CRITICAL:** "10" appears TWICE - once as dimension, once as pack count
- ⚠️ Risk: Logic must distinguish dimension 10 from pack count 10

---

## FINAL CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pk", "pack"],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "\""],
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": False,
    "brand_format_patterns": ["TITLE_CASE_AT_START"],
    "brand_sparse_supplier_mode": True,
    "strong_similarity_threshold": 0.30,
    "strong_shared_tokens_threshold": 3,
    "very_strong_similarity_threshold": 0.40,
    "very_strong_shared_tokens_threshold": 4,
    "gate_mode": "C_brand_sparse",
    "sales_column": "Keepa Sold-30d Mine (now)",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": True
}
# ---------------------------------
```

---

## USAGE INSTRUCTIONS

1. Copy the `SUPPLIER_NAMING_CONVENTION` dict above into your analysis script
2. Use these settings for all pack quantity calculations on this supplier
3. Pay special attention to the 8 calibration warnings when debugging
4. For capacity multipacks (e.g., 5x30ml), RSU = first number only (5)
5. For dimension shields, always check for unit keywords (cm, ml, inch, etc.)

---

**END OF CALIBRATION REPORT**
