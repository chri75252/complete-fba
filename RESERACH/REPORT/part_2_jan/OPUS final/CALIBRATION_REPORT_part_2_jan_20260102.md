# CALIBRATION REPORT: part_2_jan.xlsx
## Pre-Flight Analysis for FBA Financial Report
**Generated:** 2026-01-02  
**File:** `part_2_jan.xlsx`  
**Total Rows:** 2,635  
**Version:** 1.1

---

## EXECUTIVE SUMMARY

This calibration analysis identifies supplier-specific naming conventions, pack quantity patterns, and potential data traps for **part_2_jan.xlsx**. The main analysis prompt should reference this configuration to avoid common parsing errors.

### Key Findings:
1. **Pack Quantity Style:** Primarily uses **explicit units** (PC, PCE, PCS, PK, PACK, PIECES) - very common (362+ rows with PIECES patterns, 233+ with PACK patterns)
2. **Trailing Numbers:** Moderate usage (86 rows) - these are context-dependent (may be quantities, model numbers, or birthday numbers)
3. **Brand Position:** Consistently at **START** of supplier titles
4. **Sales Column:** `bought_in_past_month` - numeric integers (no text parsing required)
5. **Capacity Multipacks:** Found 34 instances in Amazon titles (e.g., "10 x 90g", "7 x 100g")

---

## TASK 1: PACK QUANTITY PATTERNS DETECTED

### 1.1 Explicit Unit Keywords (HIGH CONFIDENCE)

| Pattern Type | Count | Examples |
|--------------|-------|----------|
| **PIECES/PCS/PCE** | 362+ | "12 PIECES", "10PC", "2PC", "5PCE", "6 PCS" |
| **PACK/PK** | 233+ | "PK6", "5PACK", "20 PACK", "PK8", "36 PACK" |
| **CASES** | 4 | "100 CASES", "50 CASES", "15 CASES" |

**Observed Variations:**
- `PC` (no space): "10PC", "2PC", "8PC"
- `PCE`: "2 PCE", "5PCE", "2PCE", "9PCE"
- `PCS`: "6 PCS", "3PCS"
- `PIECES`: "12 PIECES", "4 PIECES", "5 PIECES"
- `PK` (compact): "PK6", "PK8", "PK12", "PK20", "PK24", "2PK", "3PK", "4PK"
- `PACK` (spaced): "5PACK", "20 PACK", "36 PACK", "PACK OF 10"

### 1.2 Trailing Number Patterns (MODERATE - CONTEXT-DEPENDENT)

Total found: **86 rows**

**TRAP WARNING:** Trailing numbers in this supplier's data are often **NOT quantities**:
- Birthday/Age indicators: "BADGE GIRL 3", "CANDLE NUMBER W/DECOR 6", "BIRTHDAY 12"
- Model numbers: "WALLET 1148", "LID 1433", "LID 1430", "SHARPENING STONE 2000"
- Size indicators: "MASON CASH OVAL BAKING DISH size 2"

**Legitimate quantities (combined with PACK):**
- "PACK OF 10", "PACK OF 12", "PACK OF 2", "PACK OF 5", "PACK OF 18", "PACK OF 30"

### 1.3 Leading Multiplier Patterns

**NOT COMMON** in this supplier's data. Found only 1 example:
- Row 72: "NORTHPOLE CURLING RIBBON 4 X 4M" (this is 4 pieces × 4 meters each)

### 1.4 Dimension vs Quantity Formatting

**Dimension Patterns (NOT quantities):**
| Pattern | Examples |
|---------|----------|
| LxW cm | "70X100CM", "40X40CM", "25X14CM", "55X23CM" |
| LxW mm | "5X60MM" (drill bit dimensions) |
| LxW inch | "8X10INCH", "6X8" (frame sizes) |
| LxWxH | "70X55X23CM", "80X60X26CM" (laundry bags) |

**Capacity Patterns:**
- `CM/MM/INCH` following numbers = **DIMENSIONS** (RSU=1)
- `ML/L/G/KG` = **CAPACITY** (single item)

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

### Found in Amazon Titles (34 instances)

**Pattern:** `N x [capacity][unit]` where RSU = N (the first number), NOT N × capacity

| Row | Pattern | Correct RSU | Wrong Interpretation |
|-----|---------|-------------|----------------------|
| 248 | "10 x 90g" | RSU = 10 | NOT 900g |
| 263 | "7 x 100g" | RSU = 7 | NOT 700g |
| 275 | "4 x 100g" | RSU = 4 | NOT 400g |
| 402 | "16 x 6g" | RSU = 16 | NOT 96g |
| 493 | "6 x 15ml" | RSU = 6 | NOT 90ml |
| 559 | "20 x 15g" | RSU = 20 | NOT 300g |
| 561 | "6 X 70 ML" | RSU = 6 | NOT 420ml |
| 597 | "12x 280ml" | RSU = 12 | NOT 3360ml |
| 705 | "5 x 60L" | RSU = 5 | NOT 300L |
| 746 | "2 x 10 L" | RSU = 2 | NOT 20L |
| 794 | "2 x 1L" | RSU = 2 | NOT 2L |
| 796 | "12 x 70 g" | RSU = 12 | NOT 840g |
| 798 | "8 x 150g" | RSU = 8 | NOT 1200g |

**Special case - Row 487:** "1 x 800 g/2 x 400 g" - Complex multipack (Thermos freeze boards)

---

## TASK 2: SALES SIGNAL DETECTION

### Sales Column Identified: `bought_in_past_month`

| Property | Value |
|----------|-------|
| **Column Name** | `bought_in_past_month` |
| **Data Type** | `int64` (numeric integer) |
| **Contains Text** | No |
| **Sample Values** | 100, 50, 400, 500, 300, 200, 900, 700, 800, 600 |
| **Parsing Required** | None - direct numeric use |

**Note:** Values appear to be rounded (50, 100, 200, etc.) - likely Amazon's "bought in past month" display values.

---

## TASK 3: BRAND POSITION DETECTION

### Analysis Results (first 100 rows)

| Position | Count |
|----------|-------|
| At START | 12 |
| In MIDDLE | 0 |
| At END | 0 |
| Brand not found | 88 |

### Detected Brand Pattern: **START**

Brands consistently appear as the **first word(s)** of supplier titles.

### Top 30 Likely Brands (by first word frequency)

| Brand | Occurrences |
|-------|-------------|
| PPS | 92 |
| BRIGHT (& HOMELY) | 79 |
| APOLLO | 77 |
| DEKTON | 72 |
| PRIMA | 57 |
| SIL | 52 |
| ASHLEY | 46 |
| ADORN | 44 |
| RYSONS | 36 |
| HOBBY | 33 |
| FESTIVE | 32 |
| MASON (CASH) | 32 |
| AMTECH | 31 |
| PAN (AROMA) | 30 |
| THL | 25 |
| ROLSON | 25 |
| BLACKSPUR | 25 |
| KINGFISHER | 22 |
| SMART | 20 |
| CHEF (AID) | 19 |
| CASA | 19 |
| MARKSMAN | 18 |
| BETTINA | 16 |
| JAUNTY | 16 |
| EXTRASTAR | 15 |
| PREMIER | 15 |

**Multi-word brands detected:**
- "BRIGHT & HOMELY"
- "CHEF AID"
- "MASON CASH"
- "PAN AROMA"

---

## TASK 4: CALIBRATION WARNINGS

### Dimension Traps (NxN = dimensions, NOT quantities)

```
Row 12: '70X100CM' in 'EASY STORAGE VACUUM BAG 70X100CM' should be RSU=1 (dimensions), not RSU=7000
Row 38: '5X60MM' in 'SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM' should be RSU=1 (drill bit size), not RSU=300
Row 58: '40X40CM' in 'PALOMA 2PLY IVORY 50 NAPKINS 40X40CM' should be RSU=50 (50 napkins), not RSU=1600
Row 83: '28X38' in 'APOLLO GLASS CHOPPING BOARD CLEAR 28X38' should be RSU=1 (board size), not RSU=1064
Row 86: '70X55X23CM' in 'LAUNDRY BAG HUL LARGE 70X55X23CM' should be RSU=1 (bag dimensions), not quantity
Row 186: '19 X 19CM' in 'B & CO AIR FRYER LINER SILICONE 19 X 19CM' should be RSU=1 (liner size), not RSU=361
```

### Model Number Traps

```
Row 18: 'SDB113' in 'PANASONIC UPRIGHT SDB113' is a model number, not quantity
Row 576: '1148' in 'MENS LEATHER WALLET 1148' is likely a product code
Row 1220: '1433' in 'CAROLINE PLASTIC 10 OZ 4 TUBS & LID 1433' is product code (qty is 4)
Row 1681: '1430' in 'CAROLINE PLASTIC 2 OZ 14 TUBS & LID 1430' is product code (qty is 14)
Row 1688: '2000' in 'AMTECH SHARPENING STONE 2000' is grit number, not quantity
```

### Birthday/Age Number Traps

```
Row 0: '3' in 'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3' is age indicator, should be RSU=1
Row 36: '6' in 'UNIQUE CANDLE NUMBER W/DECOR 6' is the candle number (digit), not quantity
Row 112: '8' in 'UNIQUE CANDLE NUMBER W/DECOR 8' is the candle number (digit), not quantity
Row 118: '1' in 'UNIQUE CANDLE NUMBER W/DECOR 1' is the candle number (digit), not quantity
Row 1296: '18' in 'UNIQUE CANDLES SPARKLE 18' is age indicator (18th birthday), not quantity
```

### Quantity-Inside Patterns (item count embedded)

```
Row 1: '100 CASES' in 'LUXURY CUPCAKE 100 CASES' means 100 cupcake liners per pack
Row 58: '50 NAPKINS' in 'PALOMA 2PLY IVORY 50 NAPKINS 40X40CM' means 50 napkins per pack
Row 22: '10 PLATES' in 'PAPER EASTER 10 PLATES 7 INCH' means 10 plates per pack
Row 1542: 'MINI MUFFIN 200' in 'QUEEN OF CAKES CUPCAKE MINI MUFFIN 200' means 200 cases per pack
```

### Capacity Multipack Traps (Amazon titles)

```
Row 248: '10 x 90g' should be RSU=10 (ten 90g bags), not RSU=900
Row 275: '4 x 100g' should be RSU=4 (four 100g bags), not RSU=400
Row 561: '6 X 70 ML' should be RSU=6 (six 70ml bottles), not RSU=420
Row 597: '12x 280ml' should be RSU=12 (twelve glasses), not RSU=3360
```

---

## CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION FOR part_2_jan.xlsx ---
# Generated: 2026-01-02
SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity keywords detected in this supplier's data
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "cases"],
    
    # Trailing numbers are NOT reliable as quantities for this supplier
    # (Often birthday ages, model numbers, or product codes)
    "allow_trailing_number_as_qty": False,
    
    # Leading multipliers (e.g., "10x Product") are rare
    "leading_multiplier_check": False,
    
    # Dimension/measurement shield keywords
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "lt", "l", "kg", "g", "oz", "inch", "in"],
    
    # Brand position in supplier titles
    "brand_position": "start",
    
    # Sales data column
    "sales_column": "bought_in_past_month",
    
    # Capacity multipack interpretation (e.g., "3 x 400ml" = RSU 3)
    "capacity_pattern_as_rsu": True,
    
    # Additional patterns specific to this supplier
    "has_pack_of_pattern": True,  # "PACK OF 10", "PACK OF 12" etc.
    "has_cases_pattern": True,    # "100 CASES", "50 CASES" etc.
    "birthday_candle_products": True,  # Has UNIQUE CANDLE NUMBER products
    
    # Common multi-word brands
    "multi_word_brands": [
        "BRIGHT & HOMELY",
        "CHEF AID", 
        "MASON CASH",
        "PAN AROMA"
    ],
    
    # Top single-word brands
    "top_brands": [
        "PPS", "APOLLO", "DEKTON", "PRIMA", "SIL", "ASHLEY", 
        "ADORN", "RYSONS", "HOBBY", "FESTIVE", "AMTECH", "THL",
        "ROLSON", "BLACKSPUR", "KINGFISHER", "SMART", "MARKSMAN",
        "BETTINA", "JAUNTY", "EXTRASTAR", "PREMIER", "EUROWRAP",
        "RSW", "DLUX", "TALA", "OPAL", "MINKY", "STARWASH"
    ]
}
# ---------------------------------
```

---

## RECOMMENDATIONS FOR MAIN ANALYSIS

1. **Pack Size Extraction Priority:**
   - First check for explicit units: `N PC`, `N PIECES`, `N PK`, `PACK OF N`
   - Check for `N CASES` pattern (cupcake liners, etc.)
   - Apply dimension shield before interpreting any `NxM` pattern

2. **Trailing Number Handling:**
   - Do NOT automatically interpret trailing numbers as quantities
   - Check context: birthday products, candle numbers, model numbers
   - Only use trailing numbers if preceded by "PACK OF" or similar

3. **Amazon Capacity Multipacks:**
   - When Amazon shows `N x [capacity][unit]`, RSU = N (first number only)
   - Capacity value describes single unit size, not total quantity

4. **Brand Matching:**
   - Brands appear at START of supplier titles
   - Check for multi-word brands first (e.g., "CHEF AID" before "CHEF")
   - Use word-boundary matching to avoid false positives

---

*Report generated by preflight calibration analysis v1.1*
