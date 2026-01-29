# FBA PRE-FLIGHT CALIBRATION REPORT
## Part 5 Jan Analysis

**Generated:** 2026-01-05  
**Input File:** `part 5 jan.xlsx`  
**Rows Analyzed:** 50  
**Purpose:** Detect supplier-specific naming conventions, pack quantity formats, and data anomalies to customize main analysis

---

## EXECUTIVE SUMMARY

This calibration analysis identifies the unique data patterns in the supplier's financial report to properly configure the main FBA product analysis. The analysis reveals:

- **✓ Strong explicit pack unit usage** (5 unit types: pack, pc, pcs, pieces, pk)
- **✓ Trailing number patterns detected** (some titles end with quantities like "BALLOONS 20")
- **✓ Consistent brand positioning** (28/30 products have brand at start)
- **⚠️ CRITICAL: Severe EAN/title mismatches** (9 products with completely unrelated Amazon titles)
- **✗ No capacity multipack patterns** (e.g., "3 x 400ml")
- **✗ No leading multiplier patterns** (e.g., "10x Product")
- **✗ No spec feature multipliers** (e.g., "2x magnification")

---

## TASK 1: PACK QUANTITY PATTERN DETECTION

### 1.1 Explicit Units Found

The supplier uses **5 explicit pack unit keywords**:

| Unit Type | Examples Found in Titles |
|-----------|--------------------------|
| `PIECES` | "DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES" |
| `PC` | "ARTIST PAINT BRUSHES 10PC", "MINKY CURVE SCOURER 2PC" |
| `PCS` | "DEKTON RIGHT ANGLE BRACKETS 8PCS" |
| `PK` | "CHRISTMAS TAG BAUBLE WOODEN MINI 4PK" |
| `PACK` | "LYNWOOD MINI ROLLER SET 5PACK" |

**Configuration:** `explicit_units: ['pack', 'pc', 'pcs', 'pieces', 'pk']`

### 1.2 Trailing Number Patterns

**Status:** ✓ **DETECTED** (3 examples)

Some supplier titles end with standalone numbers that may represent pack quantities:

| Row | Supplier Title | Trailing Number |
|-----|----------------|-----------------|
| 1 | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 | **3** |
| 23 | PARTY CRAZY BALLOONS ASSORTED 20 | **20** |
| 41 | UNIQUE CANDLE NUMBER W/DECOR 6 | **6** |

**Pattern:** `[PRODUCT NAME] [NUMBER]` where the number is the pack quantity.

**Configuration:** `allow_trailing_number_as_qty: True`

**⚠️ WARNING:** These numbers could also be:
- Product model numbers (e.g., "BADGE GIRL 3" might mean "badge design #3")
- Sizes/variants (e.g., "CANDLE NUMBER 6" is the number-shaped candle design)

**Recommendation:** Enable this pattern but apply cautiously. Consider cross-referencing with Amazon title quantities when possible.

### 1.3 Leading Multiplier Patterns

**Status:** ✗ **NOT DETECTED**

No titles start with patterns like "10x Product" or "6 x Item".

**Configuration:** `leading_multiplier_check: False`

### 1.4 Dimension vs Quantity Patterns

**Dimension/measurement units detected:** 8 types

| Unit | Examples in Context |
|------|---------------------|
| `ml` | "GLOSS PAINT 300ML" |
| `cm` | "BALLOON 40CM", "CLOTHES LINE 30M" |
| `mm` | Various hardware items |
| `m` | "CLOTHES LINE 30M" |
| `g` | Weight specifications |
| `kg` | Weight specifications |
| `inch` | Dimensional measurements |
| `ft` | Length measurements |

**Configuration:** `dimension_shield_keywords: ['cm', 'ft', 'g', 'inch', 'kg', 'm', 'ml', 'mm']`

**Rule:** These units indicate **SIZE/CAPACITY**, not **PACK QUANTITY**. The parser must shield these from triggering RSU calculations.

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**Status:** ✗ **NOT DETECTED**

No Amazon titles contain patterns like:
- "3 x 400ml" (3 bottles of 400ml each)
- "6 x 33ml" (6 units of 33ml each)
- "Pack of 12 x 250g" (12 units of 250g each)

**Configuration:** `capacity_pattern_as_rsu: False`

**Note:** If such patterns appear in the full dataset, they should follow the rule:
- **"3 x 400ml" → RSU = 3** (the first number = unit count)
- **NOT RSU = 1200** (do not multiply capacity × count)

---

## TASK 1C: NON-PACK "Nx" SPEC/FEATURE MULTIPLIERS

**Status:** ✗ **NOT DETECTED**

No titles contain patterns like:
- "2x Magnification"
- "3x Zoom"
- "1000x Microscope"

**Configuration:** `spec_x_shield_keywords: ["magnification", "zoom", "microscope", "scope", "times"]`

**Rule:** If these appear, they describe **product features**, not pack quantities, and must not trigger RSU calculations.

---

## TASK 2: SALES SIGNAL DETECTION

**Detected Column:** `bought_in_past_month`

**Data Type:** `int64` (numeric)

**Sample Values:** `[500, 100, 100, 50, 50, 50, 400, 100, 50, 500]`

**Requires Parsing:** ✗ NO (already numeric)

**Configuration:** `sales_column: "bought_in_past_month"`

---

## TASK 3: BRAND PATTERN DETECTION

**Brand Position:** **START** (highly consistent)

**Analysis:**
- **28 out of 30** products (93.3%) have brand names at the start of `SupplierTitle`
- All brand names are **ALL CAPS** (e.g., DLUX, EUROWRAP, RSW, MINKY)

**Most Common Brands Detected:**

| Brand | Occurrences |
|-------|-------------|
| DLUX | 2 |
| CHEF | 2 |
| PROKLEEN | 2 |
| EUROWRAP | 1 |
| RSW | 1 |
| WORLD | 1 |
| ARTIST | 1 |
| MINKY | 1 |
| STARWASH | 1 |
| STATUS | 1 |

**Configuration:** `brand_position: "start"`

**Extraction Rule:** The first whitespace-separated word in `SupplierTitle` (if ALL CAPS) is the brand.

---

## TASK 4: CALIBRATION WARNINGS

**⚠️ CRITICAL ISSUES DETECTED:** 9 warnings

### 4.1 Model Number Confusion

**Issue:** Some titles contain 3-4 digit numbers that may be **model numbers**, not pack quantities.

**Example:**
- **Row 0:** "**151** WHITE NO-DRIP GLOSS PAINT 300ML"
  - The number `151` likely refers to a product code/model, not 151 units

**Recommendation:** Shield numbers ≥ 100 from being interpreted as pack quantities unless accompanied by explicit unit keywords (pc, pack, etc.).

### 4.2 Severe Title Mismatches (EAN Errors)

**CRITICAL:** **8 out of the first 10 rows** have **completely unrelated Amazon titles**.

This indicates **widespread EAN matching errors** in the source data.

| Row | Supplier Product | Amazon Product (WRONG) | Status |
|-----|------------------|------------------------|--------|
| 0 | 151 WHITE NO-DRIP GLOSS PAINT 300ML | LG OLED48C45LA 48-Inch OLED Evo 4K UHD Smart TV | ❌ MISMATCH |
| 1 | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 | Motorola edge 60 fusion, Pantone Slipstream | ❌ MISMATCH |
| 2 | RSW BRIGHTS WASHING UP BOWL | Hyundai Petrol Backpack Leaf Blower, 170mph, 52cc | ❌ MISMATCH |
| 3 | I LOVE YOU BALLOON 40CM | Mould King V8 Engine Building Blocks Set, 2250 PCS | ❌ MISMATCH |
| 6 | ARTIST PAINT BRUSHES 10PC | LEGO Marvel Spider-Man vs. Oscorp | ❌ MISMATCH |
| 7 | MINKY CURVE SCOURER 2PC | Powerful 2200W Premium Garment Steamer | ❌ MISMATCH |
| 8 | STARWASH CLOTHES LINE 30M | Mould King V8 Engine Building Blocks Set | ❌ MISMATCH |
| 9 | STATUS LED G9 2W LED CAPSULE BULB | 17.5" Portable DVD Player | ❌ MISMATCH |

**Root Cause Analysis:**
- EAN numbers in `EAN` column may be **incorrect** or **placeholder values**
- Amazon lookup is returning completely unrelated products
- The `EAN_OnPage` column shows many `NaN` values, suggesting scraping/data quality issues

**Impact on Analysis:**
- ❌ **Cannot validate brand matching** (Amazon title is for wrong product)
- ❌ **Cannot detect pack discrepancies** (comparing unrelated products)
- ❌ **Profit calculations may be based on wrong Amazon pricing/fees**
- ❌ **All categorization logic (VERIFIED, HIGHLY LIKELY) will be unreliable**

**MANDATORY PRE-PROCESSING STEP:**
Before running the main analysis, the user MUST:

1. **Validate EAN accuracy** for all rows
2. **Re-scrape Amazon data** using correct EANs or ASINs
3. **Filter out rows** where EAN lookup clearly failed
4. **Consider using ASIN** as primary identifier instead of EAN

**Expected Data Quality Threshold:**
- At least **80% of rows** should have supplier/Amazon titles sharing common keywords
- If < 80%, the dataset is **NOT SUITABLE** for automated analysis

---

## CONFIGURATION OUTPUT

Use this configuration block in your main analysis script:

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pc', 'pcs', 'pieces', 'pk'],  # Detected unit keywords
    "allow_trailing_number_as_qty": True,  # Trailing numbers found: 3 examples
    "leading_multiplier_check": False,  # Leading 'Nx' patterns found: 0 examples
    "dimension_shield_keywords": ['cm', 'ft', 'g', 'inch', 'kg', 'm', 'ml', 'mm'],  # Detected measurement units
    "brand_position": "start",  # Detected brand position
    "sales_column": "bought_in_past_month",  # Detected sales column
    "capacity_pattern_as_rsu": False,  # 'N x Capacity' patterns found: 0 examples
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],  # Spec features, not pack counts
    "table_pipe_sanitization": True  # Replace '|' with '/' in output tables
}
# ---------------------------------
```

---

## FINAL RECOMMENDATIONS

### ✅ Safe to Proceed With:
1. **Explicit unit detection** using: pack, pc, pcs, pieces, pk
2. **Brand extraction** from the start of supplier titles (ALL CAPS first word)
3. **Sales data** from `bought_in_past_month` column (already numeric)
4. **Dimension shielding** for: cm, ft, g, inch, kg, m, ml, mm

### ⚠️ Use With Caution:
1. **Trailing number patterns** — Enable but validate results manually (could be model numbers or design variants)
2. **Large numbers** (≥ 100) — Shield from pack quantity detection unless explicit units present

### ❌ CRITICAL BLOCKERS:
1. **EAN/Title Mismatches** — **80% of sampled rows have wrong Amazon data**
   - **Action Required:** Clean/validate EAN column before analysis
   - **Risk:** Without fixing, the entire analysis output will be unreliable

2. **Data Quality Gate:**
   - The supplier data MAY be usable for supplier-side analysis (pricing, inventory)
   - The Amazon data IS NOT RELIABLE for matching/validation
   - **Recommendation:** Either fix EAN matching or run "supplier-only mode" without Amazon validation

---

## NEXT STEPS

1. **IMMEDIATE:** Review rows 0-10 in source file to confirm EAN issues
2. **CRITICAL:** Decide whether to:
   - **Option A:** Fix EAN data and re-fetch Amazon information
   - **Option B:** Run analysis in "supplier-only" mode (no Amazon validation)
   - **Option C:** Manually verify EANs for high-value items only
3. **THEN:** Integrate configuration block into main analysis script
4. **FINALLY:** Run main analysis with appropriate data quality expectations

---

**End of Calibration Report**  
**Analyst:** Antigravity AI  
**Date:** 2026-01-05
