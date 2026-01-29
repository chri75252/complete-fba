# Pre-Flight Calibration Report: `part_1_jan.xlsx`

**Generated:** 2026-01-02 03:50 UTC+4  
**Data Pattern Specialist Analysis**  
**File:** `part_1_jan.xlsx`  
**Rows Analyzed:** 50

---

## 📊 FILE SCHEMA OVERVIEW

| Column | Data Type | Purpose |
|--------|-----------|---------|
| `EAN` | int64 | Primary EAN barcode |
| `EAN_OnPage` | float64 | Amazon page EAN (often NaN) |
| `ASIN` | object | Amazon product ID |
| `SupplierTitle` | object | Supplier product name |
| `AmazonTitle` | object | Amazon listing title |
| `bought_in_past_month` | int64 | **Sales signal** (numeric, no parsing needed) |
| `SupplierPrice_incVAT` | float64 | Cost price |
| `NetProfit` | float64 | Calculated profit |

---

## TASK 1: PACK QUANTITY PATTERNS

### 1a. Explicit Units Found ✅

| Pattern | Examples Found |
|---------|---------------|
| `PC` | Row 4: "MINKY CURVE SCOURER **2PC**", Row 9: "FESTIVE MAGIC BELLS **8PC** ASSORTED", Row 27: "CHRISTMAS VELVET COLOURING SET **2PC**" |
| `PK` | Row 21: "AIRWICK CANDLE... **PK6**", Row 47: "FAIRY WASHING UP... **PK8**" |
| `PACK` | Row 29: "LYNWOOD MINI ROLLER SET **5PACK**" |
| `PIECES` | Row 3: "DLUX PEGS... **12 PIECES**", Row 35: "BRIGHT & HOMELY... **4 PIECES**" |

**Configuration:** `["pc", "pcs", "pce", "pk", "pack", "pieces"]`

### 1b. Trailing Numbers Analysis ⚠️

| Row | Title | Trailing Number | Assessment |
|-----|-------|----------------|------------|
| 0 | EUROWRAP GIANT BIRTHDAY BADGE **GIRL 3** | 3 | ⚠️ **VARIANT NUMBER** - "Girl 3" is age/style variant |
| 16 | PANASONIC UPRIGHT **SDB113** | 113 | ⚠️ **MODEL NUMBER** - Part of model code |
| 18 | PARTY CRAZY BALLOONS ASSORTED **20** | 20 | ✅ **LIKELY PACK QTY** - 20 balloons |
| 21 | AIRWICK CANDLE... PK**6** | 6 | ✅ **PACK QTY** - Already has PK prefix |
| 34 | UNIQUE CANDLE NUMBER W/DECOR **6** | 6 | ⚠️ **PRODUCT VARIANT** - This is "Number 6" candle (birthday candle) |
| 47 | FAIRY WASHING UP... PK**8** | 8 | ✅ **PACK QTY** - Already has PK prefix |

**Configuration:** `allow_trailing_number_as_qty: True` with caution - need context validation

### 1c. Leading Multipliers ❌

**No patterns found** like "10x Product" or "6 x Product"

**Configuration:** `leading_multiplier_check: False`

### 1d. Dimension vs Quantity Formats

| Format Type | Examples | Frequency |
|-------------|----------|-----------|
| `NNcm` (no space) | 40CM, 37CM, 50CM, 20CM, 26.5CM | HIGH |
| `NNmm` (no space) | 5MM, 60MM, 85MM | MEDIUM |
| `NNml` (no space) | 500ML, 440ML, 750ML, 250ML | MEDIUM |
| `NNg` (no space) | 105G | LOW |
| `NN INCH` (with space) | 7 INCH, 10.5 INCH | LOW |
| `NNxNNcm` (dimensions) | 70X100CM | LOW |
| `N.NL` (volume) | 1.6L | LOW |

**Configuration:** Dimensions are typically **uppercase, no space** before unit

---

## TASK 2: SALES SIGNAL DETECTION ✅

| Column Name | Data Type | Sample Values | Parsing Required |
|-------------|-----------|---------------|------------------|
| `bought_in_past_month` | **int64** | [100, 50, 50, 50, 100, 500, 300, 200, 400] | **NO** - Clean numeric |

**Configuration:** `sales_column: "bought_in_past_month"`

**Note:** This is a clean integer column, no text parsing like "100+ bought" required.

---

## TASK 3: BRAND PATTERN DETECTION

### First Word Analysis (Potential Brands)

| Brand | Count | Sample Title |
|-------|-------|--------------|
| DLUX | 3 | DLUX PEGS WITH SOFT RUBBER GRIP... |
| CHEF | 2 | CHEF AID LANC PEELER PLASTIC HAND |
| PROKLEEN | 2 | PROKLEEN SPUNLACE FLOOR MOP & HANDLE |
| PRIMA | 2 | PRIMA PET BALL LAUNCHER 50CM |
| BETTINA | 2 | BETTINA SPONGE CELLULOSE 3 SCOURER |
| EUROWRAP | 1 | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 |
| MINKY | 1 | MINKY CURVE SCOURER 2PC |
| STATUS | 1 | STATUS LED G9 2W LED CAPSULE BULB EACH |
| FESTIVE | 1 | FESTIVE MAGIC BELLS 8PC ASSORTED |
| TALA | 1 | TALA STAINLESS STEEL TOWEL HOLDER |

### Brand Position Assessment

**Pattern:** MIXED - Some are clear brands (CHEF AID, MINKY, STATUS, TALA), others are descriptive first words (LUXURY, EASY, CEMENT, I)

**Examples:**
- ✅ Brand at start: "CHEF AID LANC PEELER", "MINKY CURVE SCOURER", "STATUS LED G9"
- ❌ Not brand at start: "I LOVE YOU BALLOON", "EASY STORAGE VACUUM BAG", "LUXURY CUPCAKE"

**Configuration:** `brand_position: "mixed"`

---

## TASK 4: CALIBRATION WARNINGS - TRAP ROWS ⚠️

### Critical Traps to Avoid

| Row | Title | Trap Description | Correct Interpretation |
|-----|-------|------------------|----------------------|
| **0** | EUROWRAP GIANT BIRTHDAY BADGE **GIRL 3** | "3" is NOT pack qty | Age variant (Girl age 3) - Pack = 1 |
| **16** | PANASONIC UPRIGHT **SDB113** | "113" is NOT pack qty | Model number - Pack = 1 |
| **34** | UNIQUE CANDLE NUMBER **W/DECOR 6** | "6" is NOT pack qty | Birthday candle "Number 6" - Pack = 1 |
| **1** | LUXURY CUPCAKE **100 CASES** | "100" IS pack qty | 100 cupcake cases in pack |
| **10** | EASY STORAGE VACUUM BAG **70X100CM** | "70X100" are NOT pack qty | Dimensions (70cm x 100cm) - Pack = 1 |
| **36** | SECURPAK POZI COUNTERSUNK SCREWS ZP **5X60MM** | "5X60" is NOT 5 packs | Dimensions (5mm x 60mm) - Pack = 1 |
| **37** | DEKTON MASONRY DRILL BIT **5MM X 85MM** | "5MM X 85MM" are NOT pack qty | Drill bit dimensions - Pack = 1 |
| **6** | STATUS LED G9 **2W** LED CAPSULE BULB | "2W" is NOT pack qty | Wattage specification - Pack = 1 |
| **25** | SQUARE CANISTER CLASSIC **1.6L** | "1.6L" is NOT pack qty | Capacity/volume - Pack = 1 |

### Dimension Shield Keywords

These patterns should **NEVER** be interpreted as pack quantities:
- `cm`, `mm`, `m` (length)
- `ml`, `l`, `ltr` (volume)
- `g`, `kg`, `oz` (weight)
- `w`, `watt` (power)
- `inch` (imperial length)

---

## 🔧 CONFIGURATION BLOCK FOR MAIN SCRIPT

```python
# --- CALIBRATION CONFIGURATION: part_1_jan.xlsx ---
# Generated: 2026-01-02 by Pre-Flight Calibration Analysis
# File: part_1_jan.xlsx | Rows Analyzed: 50

SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity explicit unit markers
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces"],
    
    # Allow trailing numbers as pack qty with context validation
    "allow_trailing_number_as_qty": True,
    
    # No leading multiplier patterns found (e.g., "10x Product")
    "leading_multiplier_check": False,
    
    # Dimension/Measurement keywords - DO NOT interpret as pack quantities
    "dimension_shield_keywords": [
        "cm", "mm", "m",           # Length
        "ml", "l", "ltr",          # Volume  
        "g", "kg", "oz",           # Weight
        "w", "watt",               # Power
        "inch", "in"               # Imperial
    ],
    
    # Brand naming is inconsistent
    "brand_position": "mixed",
    
    # Sales data column (clean integers, no parsing needed)
    "sales_column": "bought_in_past_month",
    
    # Additional dimension patterns that contain 'x' (NOT multipliers)
    "dimension_x_patterns": [
        r"\d+[xX]\d+\s*cm",        # 70X100CM (bag dimensions)
        r"\d+\s*[xX]\s*\d+\s*mm",  # 5X60MM, 5MM X 85MM (screw/drill dimensions)
    ],
    
    # Model number patterns (trailing alphanumerics, NOT pack qty)
    "model_number_patterns": [
        r"[A-Z]{2,}\d{2,}$",       # SDB113, G9 2W
    ],
    
    # Variant/Style indicators (trailing number is NOT pack qty)
    "variant_indicators": [
        "girl", "boy", "age", "size", "style", "number", "decor", "no.", "#"
    ]
}
# ---------------------------------
```

---

## 📋 QUICK REFERENCE: PACK QTY EXTRACTION RULES

### ✅ EXTRACT AS PACK QTY:
1. Numbers followed by: `pc`, `pcs`, `pce`, `pk`, `pack`, `pieces`
2. "100 CASES" - number before CASES/CASE
3. Pattern like "BALLOONS 20" where context suggests quantity

### ❌ DO NOT EXTRACT AS PACK QTY:
1. Numbers followed by dimension units (cm, mm, ml, g, kg, etc.)
2. Model numbers (SDB113, G9)
3. Numbers after variant words (GIRL 3, NUMBER 6)
4. Wattage (2W, 60W)
5. Volume/Capacity (1.6L, 500ML)
6. Dimension strings with X (70X100CM, 5X60MM)

---

## 🎯 RECOMMENDED PACK EXTRACTION PRIORITY

1. **First:** Look for explicit unit markers (`N PC`, `N PK`, `N PIECES`)
2. **Second:** Look for pack-related words (`N CASES`, `SET OF N`)
3. **Third:** Apply dimension shield to eliminate false positives
4. **Fourth:** Check variant indicators before accepting trailing numbers
5. **Fifth:** Default to Pack = 1 if uncertain

---

*End of Calibration Report*
