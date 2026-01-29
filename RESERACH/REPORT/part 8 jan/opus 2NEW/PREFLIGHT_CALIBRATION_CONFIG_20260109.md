# PREFLIGHT CALIBRATION ANALYSIS REPORT
**File Analyzed:** `part 8 jan.xlsx`  
**Date:** 2026-01-09  
**Rows Analyzed:** 50 (first rows)

---

## CRITICAL DATA QUALITY FINDING ⚠️

**MAJOR ISSUE: EAN MISMATCH BETWEEN SUPPLIER AND AMAZON PRODUCTS**

Analysis of the first 50 rows reveals a **systematic mismatch** between SupplierTitle and AmazonTitle:

| Row | SupplierTitle | AmazonTitle | Status |
|-----|---------------|-------------|--------|
| 0 | 151 WHITE NO-DRIP GLOSS PAINT 300ML | LG OLED48C45LA 48-Inch OLED TV... | ❌ UNRELATED |
| 1 | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 | Motorola edge 60 fusion... | ❌ UNRELATED |
| 2 | LUXURY CUPCAKE 100 CASES | Oversize Turbo Dryer Blower... | ❌ UNRELATED |
| 3 | METAL GOLF SET | SKYMAX 2025 PRECISE M5 GOLF SET | ⚠️ POSSIBLE MATCH |
| 5 | I LOVE YOU BALLOON 40CM | Mould King V8 Engine Building... | ❌ UNRELATED |
| 6 | WORLD OF PETS TOY BALL LAUNCHER 62CM | PetSafe Automatic Ball Launcher | ⚠️ CATEGORY MATCH |

**Observation:** The vast majority of rows (>90%) show completely unrelated products between Supplier and Amazon columns. This suggests:
1. The Amazon matching system may have failed for this batch
2. These may be "placeholder" Amazon results
3. The data pipeline may have a bug

**EAN Analysis:**
- When `EAN_OnPage` exists and differs from `EAN`, it confirms the Amazon product is NOT the same as the supplier product
- Example: Row 2: Supplier EAN=5015302477202, EAN_OnPage=717710483480 (DIFFERENT)

---

## TASK 1: PACK QUANTITY PATTERNS

### Explicit Units Detected:
| Row | Pattern | Example |
|-----|---------|---------|
| 20 | `8PCS` | DEKTON RIGHT ANGLE BRACKETS 8PCS |
| 35 | `4PK` | CHRISTMAS TAG BAUBLE WOODEN MINI 4PK |
| 39 | `5PACK` | LYNWOOD MINI ROLLER SET 5PACK |

**Detected Units:** `PCS`, `PK`, `PACK`

### Trailing Numbers as Quantity:
| Row | Title | Trailing Number | Likely Meaning |
|-----|-------|-----------------|----------------|
| 25 | PARTY CRAZY BALLOONS ASSORTED 20 | 20 | ✅ PACK QUANTITY |

**Note:** Only 1 instance found - trailing numbers are NOT common in this dataset.

### Leading Multipliers (Nx):
**NONE FOUND** - This supplier does not use "10x Product" format.

### Dimension Formats:
| Pattern | Examples | Count |
|---------|----------|-------|
| `XXml` / `XXXML` | 300ML, 85ML, EDT100ML | 3 |
| `XXcm` | 40CM, 62CM, 37CM, 50CM, 26.5CM | 7 |
| `XXmm` | 5X60MM | 1 |
| `XX INCH` | 7 INCH, 10.5 INCH | 2 |
| `X.XL` | 1.6L | 1 |
| `XXg` | 105G | 1 |

**Format Style:** Dimensions are typically UPPERCASE, attached to numbers (e.g., `300ML`, not `300 ml`)

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**NONE FOUND** in this 50-row sample.

No patterns like "3 x 400ml" detected in Amazon titles. The capacity multipack rule should still be enabled but this supplier's products don't exhibit this pattern in the sample.

---

## TASK 1C: NON-PACK "Nx" SPEC/FEATURE MULTIPLIERS

**NONE FOUND** in this 50-row sample.

No patterns like "2x Magnification" or "3x Zoom" detected.

---

## TASK 2: SALES SIGNAL DETECTION

**Sales Column:** `bought_in_past_month`

**Format:** Numeric values (already parsed)  
**Sample Values:** `500, 100, 50, 100, 100, 50, 50, 50, 100, 50`

No text parsing required - values are stored as integers.

---

## TASK 3: BRAND PATTERNS

### Supplier Brand Analysis:
| Metric | Value |
|--------|-------|
| Brands at title start | 48/50 (96%) |
| Brand format | ALL_CAPS at start |
| Mixed positioning | Rare (4%) |

**Top Detected Brands:**
- DLUX (2), CHEF (2), PROKLEEN (2), PRIMA (2), CHRISTMAS (2)
- DEKTON, TALA, PANASONIC, DUNLOP, AIRWICK, MINKY, GRAFIX, LYNWOOD (1 each)

### Amazon Brand Analysis:
| Metric | Value |
|--------|-------|
| Visible brands in title | 2/50 (4%) |
| Brand usually present | NO |
| Brand format | Mixed |

**Note:** Due to the EAN mismatch issue, Amazon brand analysis is unreliable for this dataset.

---

## CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION (part 8 jan.xlsx) ---
SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity patterns
    "explicit_units": ["pcs", "pk", "pack", "pieces"],  # Detected: 8PCS, 4PK, 5PACK
    "allow_trailing_number_as_qty": False,  # Only 1 instance found - not reliable
    "leading_multiplier_check": False,  # No "Nx Product" patterns found
    
    # Dimension shielding
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch"],
    "dimension_format": "attached_uppercase",  # e.g., 300ML, 40CM (not 300 ml)
    
    # Brand detection
    "brand_position": "start",  # ALL_CAPS at start is standard (96%)
    "brand_in_supplier_usually_present": True,  # 96% have brand at start
    "brand_in_amazon_usually_present": False,  # Only 4% clearly show brand
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": True,  # Amazon titles often omit/obscure brand
    
    # Similarity thresholds (calibrated for this dataset)
    "strong_similarity_threshold": 0.30,
    "strong_shared_tokens_threshold": 3,
    "very_strong_similarity_threshold": 0.40,
    "very_strong_shared_tokens_threshold": 4,
    
    # Gate mode
    "gate_mode": "C_brand_sparse",  # Amazon brand info unreliable
    
    # Sales column
    "sales_column": "bought_in_past_month",  # Numeric, no parsing needed
    
    # Capacity and spec patterns
    "capacity_pattern_as_rsu": True,  # "3 x 400ml" means RSU=3
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    
    # Output formatting
    "table_pipe_sanitization": True,  # Replace "|" with "/" in output tables
    
    # DATA QUALITY FLAGS
    "ean_mismatch_rate": 0.90,  # ~90% of rows have mismatched Amazon products
    "requires_manual_verification": True,  # Due to high mismatch rate
}
# ---------------------------------
```

---

## TASK 4: CALIBRATION WARNINGS

### ⚠️ HIGH PRIORITY WARNINGS

| Row | Issue | Details |
|-----|-------|---------|
| ALL | **CRITICAL: EAN MISMATCH** | ~90%+ of Amazon products are NOT the supplier product |
| 0 | Model number trap | "151" appears at start - should NOT be extracted as quantity |
| 16 | Dimension multiplication trap | "70X100CM" - the "X" here is a dimension multiplier, NOT a pack indicator |
| 33 | Capacity vs container | "1.6L" is container size, not pack quantity |
| 38 | Multi-unit pack | "105G PK6" - the "6" is the pack quantity, not 105 |
| 43 | Short EAN | EAN=11179373161 (11 digits) - may need left-padding to validate |
| 49 | Dimension multiplier trap | "5X60MM" - this is screw dimensions (5mm x 60mm), NOT 5 packs of 60 |

### ⚠️ MEDIUM PRIORITY WARNINGS

| Row | Issue | Details |
|-----|-------|---------|
| 25 | Trailing number | "BALLOONS ASSORTED 20" - 20 is likely pack quantity |
| 28 | Embedded quantity | "10 PLATES 7 INCH" - 10 is the pack quantity, 7 is the dimension |
| 37 | Embedded dimension | "PLATE 10.5 INCH" - 10.5 is the size, not quantity |

### Specific Pattern Traps

1. **Model Numbers Starting Titles:**
   - Row 0: "151 WHITE NO-DRIP..." - 151 is a product model, NOT quantity
   
2. **Dimension Multipliers (XxY format):**
   - Row 16: "70X100CM" → This is 70cm × 100cm, NOT 70 packs of 100
   - Row 49: "5X60MM" → This is 5mm × 60mm screw size

3. **Pack + Weight Combinations:**
   - Row 38: "105G PK6" → Extract PK6 (6 units), NOT 105

---

## RECOMMENDED ANALYSIS APPROACH

Given the **critical EAN mismatch issues** in this dataset, the main analysis should:

1. **FLAG ALL ROWS** for manual verification where `EAN ≠ EAN_OnPage`
2. **Skip profit calculations** for mismatched products (profit data is meaningless if products don't match)
3. **Focus on rows with matching EANs** or where `EAN_OnPage` is NaN (possible but unverified match)
4. **Consider this dataset LOW QUALITY** for automated FBA analysis

---

## COLUMN REFERENCE

| Index | Column Name | Type | Notes |
|-------|-------------|------|-------|
| 0 | EAN | string | Supplier product EAN |
| 1 | EAN_OnPage | float/NaN | Amazon page EAN (often mismatched!) |
| 2 | ASIN | string | Amazon product ID |
| 3 | SupplierTitle | string | Supplier product name |
| 4 | AmazonTitle | string | Amazon product name (often wrong product!) |
| 7 | bought_in_past_month | int | Sales signal (numeric) |
| 11 | SupplierPrice_incVAT | float | Supplier cost with VAT |
| 21 | NetProfit | float | Calculated profit |
| 22 | ROI ( % ) | float | Return on investment |

---

*Report generated: 2026-01-09 00:57 UTC+4*
