# AGENTIC FBA CALIBRATION REPORT (PRE-FLIGHT) v1.2

**Generated:** 2026-01-03T17:30:10+04:00  
**Input File:** `part 3 jan.xlsx`  
**Total Rows:** 2,666 products  
**Analysis Scope:** Full dataset pattern analysis with 60-row deep inspection

---

## EXECUTIVE SUMMARY

This pre-flight calibration analyzed the supplier file `part 3 jan.xlsx` to detect naming conventions, pack quantity formats, and data anomalies. The main analysis prompt should reference this configuration to avoid common parsing traps.

### Key Findings:
- **Pack Units:** Uses `pk`, `pack`, `pce`, `pcs`, `piece`, `set` (230 occurrences of "pk" alone)
- **Trailing Numbers:** RARE pattern - only 1 instance detected
- **Leading Multipliers:** NOT USED by this supplier
- **Dimensions:** Heavy use of `cm`, `ml`, `mm`, `ltr` - DIMENSION SHIELD CRITICAL
- **Brand Position:** 98% at START (all-caps first word pattern)
- **Sales Column:** `bought_in_past_month` (numeric, integers 50-900)
- **Pipe Symbols:** NOT PRESENT in titles

---

## TASK 1: PACK QUANTITY PATTERN ANALYSIS

### 1.1 Explicit Unit Patterns

| Unit Keyword | Occurrences in Dataset | Example Pattern |
|--------------|------------------------|-----------------|
| `pk`         | 230                    | "440ML PK8", "4PK" |
| `set`        | 160                    | "SET 2PC", "SHOESHINE SET" |
| `pack`       | 103                    | "5PACK", "10 PACK" |
| `pce`        | 63                     | "2 PCE", "12PCE" |
| `piece`      | 60                     | "12 PIECES", "4 PIECES" |
| `pcs`        | 43                     | "10PC", "8PCS" |
| `each`       | 25                     | "EACH", "SOLD EACH" |
| `unit`       | 2                      | "PER UNIT" |

**Pattern Style:** This supplier uses SUFFIXED quantities:
- "...10PC", "...PK6", "...4PK", "...12 PIECES"
- Numbers typically appear BEFORE the unit keyword

### 1.2 Trailing Number as Quantity

**Detection Result:** RARE (1 instance in 60-row sample)  
**Example Found:** "PARTY CRAZY BALLOONS ASSORTED 20"

**Recommendation:** `allow_trailing_number_as_qty: False`  
Most trailing numbers in this dataset are dimensions or model numbers, NOT pack quantities.

### 1.3 Leading Multiplier Check

**Detection Result:** NOT USED by this supplier  
No instances of "10x Product" or "6 x Item" patterns at the START of titles.

**Recommendation:** `leading_multiplier_check: False`

### 1.4 Dimension vs Quantity Patterns

**CRITICAL: High Dimension Density**

This supplier file contains EXTENSIVE dimension patterns that could be misinterpreted as pack quantities:

| Dimension Unit | Occurrences | Example |
|----------------|-------------|---------|
| `cm`           | 226         | "40CM", "37CM", "70X100CM" |
| `ml`           | 170         | "300ML", "500ML", "750ML" |
| `mm`           | 78          | "5X60MM", "120X215MM" |
| `ltr`          | 70          | "1.6L", "0.7 LTR" |
| `inch`         | 57          | "7 INCH", "10.5 INCH" |
| `g`            | 41          | "105G", "90g" |
| `l`            | 32          | "1.6L" |
| `oz`           | 32          | "8oz" |
| `in`           | 19          | "9x9in", "2 IN 1" |
| `kg`           | 6           | "5KG" |

**Dimension "X" Patterns (TRAP ALERT):**
- "70X100CM" → Dimension (70cm × 100cm), NOT 7000 items
- "5X60MM" → Screw size, NOT 300 items
- "120X215MM" → Paper size, NOT 25,800 items

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**Detection Result:** FOUND (approximately 8 instances in first 650 rows)

When Amazon title shows `N x [capacity]ml/g/l`, the RSU = N (the first number only).
The capacity value describes SIZE of each unit, NOT quantity to multiply.

### Examples Detected:

| Row | Pattern | Correct RSU | Wrong RSU (if multiplied) |
|-----|---------|------------|---------------------------|
| 260 | "10 x 90g" | 10 | 900 |
| 276 | "7 x 100g" | 7 | 700 |
| 420 | "16 x 6g" | 16 | 96 |
| 506 | "1 x 800 g" | 1 | 800 |
| 512 | "6 x 15ml" | 6 | 90 |
| 589 | "6 X 70 ML" | 6 | 420 |
| 609 | "3 x 10ml" | 3 | 30 |
| 629 | "12x 280ml" | 12 | 3360 |

**Recommendation:** `capacity_pattern_as_rsu: True`  
When encountering "N x [capacity]", extract N as RSU.

---

## TASK 1C: NON-PACK "Nx" SPEC/FEATURE MULTIPLIERS

**Detection Result:** NONE FOUND in sample

No instances of "2x Magnification", "3x Zoom", or similar feature multipliers were detected in this supplier dataset.

**Recommendation:** `spec_x_shield_keywords: ["magnification", "zoom", "power", "brightness"]`  
Include these as a safety filter, but they are not common in this dataset.

---

## TASK 2: SALES SIGNAL DETECTION

**Sales Column Identified:** `bought_in_past_month`

| Property | Value |
|----------|-------|
| Data Type | int64 (numeric integer) |
| Non-null Count | 2,666 (100% populated) |
| Minimum Value | 50 |
| Maximum Value | 900 |
| Sample Values | 500, 100, 100, 50, 50, 50, 400, 100, 50, 500 |

**Parsing Required:** NO  
Values are clean integers, no text parsing (like "100+ bought") needed.

---

## TASK 3: BRAND POSITION ANALYSIS

### Brand Location Detection

| Metric | Value |
|--------|-------|
| Brand at START (all-caps first word) | **98%** (98/100 sample) |
| Brand elsewhere (middle/end) | **2%** (2/100 sample) |

### Most Common First Words (Likely Brands):

| Brand | Occurrences |
|-------|-------------|
| BETTINA | 4 |
| DLUX | 3 |
| CHRISTMAS* | 3 |
| ECO | 3 |
| EUROWRAP | 2 |
| MINKY | 2 |
| CHEF | 2 |
| ADORN | 2 |
| FESTIVE* | 2 |
| CEMENT* | 2 |
| PROKLEEN | 2 |
| DEKTON | 2 |
| PRIMA | 2 |
| UNIQUE | 2 |
| BRIGHT | 2 |
| IMPERIAL | 2 |
| PALOMA | 2 |
| ART | 2 |
| APOLLO | 2 |

*Note: CHRISTMAS, FESTIVE, CEMENT may be descriptors, not brands.

**Recommendation:** `brand_position: "start"`  
This supplier consistently places brand names at the START of product titles.

---

## TASK 4: CALIBRATION WARNINGS (Potential Traps)

### 4.1 DIMENSION TRAPS (Highest Priority)

These patterns look like pack quantities but are actually product dimensions. **RSU should be 1.**

| Row | Pattern | Wrong Interpretation | Correct Interpretation |
|-----|---------|----------------------|------------------------|
| 14 | "70X100CM" | RSU=7000 | RSU=1 (vacuum bag size) |
| 42 | "5X60MM" | RSU=300 | RSU=1 (screw dimensions) |
| 60 | "40X40CM" | RSU=1600 | RSU=1 (product dimensions) |
| 112 | "30 x 20 cm" | RSU=600 | RSU=1 (product size) |
| 179 | "25X14CM" | RSU=350 | RSU=1 (product size) |
| 335 | "120X215MM" | RSU=25800 | RSU=1 (envelope size) |
| 385 | "150x122cm" | RSU=18300 | RSU=1 (fabric/cover size) |
| 393 | "40X60CM" | RSU=2400 | RSU=1 (rug/mat size) |
| 477 | "180X265MM" | RSU=47700 | RSU=1 (paper size) |
| 519 | "220 x 260mm" | RSU=57200 | RSU=1 (product size) |
| 621 | "230X340MM" | RSU=78200 | RSU=1 (envelope size) |

### 4.2 CAPACITY MULTIPACK TRAPS

These patterns contain a multipack count AND a capacity. Use the COUNT, not the multiplied value.

| Row | Pattern | Wrong Interpretation | Correct Interpretation |
|-----|---------|----------------------|------------------------|
| 260 | "10 x 90g" | RSU=900 | RSU=10 (10 units of 90g each) |
| 276 | "7 x 100g" | RSU=700 | RSU=7 (7 units of 100g each) |
| 506 | "1 x 800 g" | RSU=800 | RSU=1 (1 unit of 800g) |
| 512 | "6 x 15ml" | RSU=90 | RSU=6 (6 bottles of 15ml) |
| 589 | "6 X 70 ML" | RSU=420 | RSU=6 (6 bottles of 70ml) |
| 629 | "12x 280ml" | RSU=3360 | RSU=12 (12 bottles of 280ml) |

### 4.3 QUANTITY-INSIDE TRAPS

These items come as a single pack with multiple items inside. The number is NOT the pack count.

| Row | Pattern | Wrong Interpretation | Correct Interpretation |
|-----|---------|----------------------|------------------------|
| 79 | "PEGS 36" | 36 packs | 1 pack of 36 pegs |

### 4.4 NESTED PACK PATTERNS

These use parentheses to indicate internal structure. Parse carefully.

| Row | Pattern | Meaning |
|-----|---------|---------|
| 622 | "(2x250)" | 500 total items in one pack |

---

## OUTPUT: CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION ---
# Generated: 2026-01-03 for supplier file: part 3 jan.xlsx

SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity unit keywords (ordered by frequency)
    "explicit_units": ["pk", "pack", "pce", "pcs", "piece", "set", "each"],
    
    # Trailing numbers are RARELY used as pack quantities in this dataset
    "allow_trailing_number_as_qty": False,
    
    # Leading multipliers (e.g., "10x Product") NOT used by this supplier
    "leading_multiplier_check": False,
    
    # CRITICAL: Dimension/measurement keywords to shield from pack detection
    # These MUST be excluded when extracting pack quantities
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", '"', "'"
    ],
    
    # Brand names appear at the START of supplier titles (98% of cases)
    "brand_position": "start",
    
    # Sales data column - clean integers, no parsing needed
    "sales_column": "bought_in_past_month",
    "sales_requires_parsing": False,
    
    # Capacity multipack interpretation:
    # "3 x 400ml" means RSU=3 (3 bottles of 400ml each), NOT RSU=1200
    "capacity_pattern_as_rsu": True,
    
    # Spec/feature multiplier keywords (if present near "Nx", NOT a pack count)
    "spec_x_shield_keywords": ["magnification", "zoom", "power", "brightness", "strength"],
    
    # No pipe symbols found in this dataset
    "table_pipe_sanitization": False,
    
    # Additional supplier-specific patterns
    "dimension_x_pattern_regex": r'\b(\d+)\s*[xX]\s*(\d+)\s*(cm|mm|in|inch|"|\'|m)\b',
    "nested_pack_pattern_regex": r'\((\d+)\s*[xX]\s*(\d+)\)',
    
    # Common false-positive dimensions to explicitly ignore
    "ignore_dimension_patterns": [
        r'\d+x\d+cm',      # e.g., 70x100cm
        r'\d+x\d+mm',      # e.g., 5x60mm
        r'\d+x\d+in',      # e.g., 9x9in
        r'\d+\s*x\s*\d+\s*inch',  # e.g., 8x10inch
    ]
}
# ---------------------------------
```

---

## SUMMARY FOR MAIN ANALYSIS

### Critical Rules for This Supplier:

1. **DIMENSION SHIELD IS CRITICAL:** 246 potential traps detected. Any pattern matching `NxN + unit` (cm/mm/inch/in) should be treated as DIMENSION, not pack quantity.

2. **Pack Units:** Look for `pk`, `pack`, `pce`, `pcs`, `piece`, `set` at END of supplier title.

3. **Capacity Multipacks:** When Amazon shows "N x [capacity]ml/g", RSU = N only.

4. **Brand Matching:** Brands are at START of supplier titles. Use word-boundary matching.

5. **Sales Data:** Use `bought_in_past_month` column directly (no parsing needed).

6. **Trailing Numbers:** Do NOT interpret trailing numbers as pack quantities by default.

---

**Pre-flight Calibration Complete.**  
This configuration should be integrated into the main FBA analysis prompt for optimal accuracy.
