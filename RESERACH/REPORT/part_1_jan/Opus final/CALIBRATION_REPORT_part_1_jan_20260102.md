# PRE-FLIGHT CALIBRATION REPORT
## Supplier File: `part_1_jan.xlsx`
**Generated:** 2026-01-02  
**Purpose:** Detect supplier naming conventions and data patterns for main analysis customization

---

## EXECUTIVE SUMMARY

This calibration analysis examined the first 500 rows of `part_1_jan.xlsx` (total 2402 rows) to identify supplier-specific naming conventions that will customize the main FBA analysis logic.

**Key Findings:**
- This supplier uses **multiple explicit unit keywords**: PCE (11), PCS (7), PK (15), PACK (12), PIECES (8)
- **Trailing numbers ARE common** (18 occurrences in first 500 rows) - these often represent pack quantities
- **NO leading multiplier patterns** (e.g., "10x Product") found
- **Dimension patterns are prevalent**: CM (60), MM (14), ML (40), INCH (23) - shield needed
- **Brand names appear at START** in 96% of detected cases
- **Sales column is numeric** (`bought_in_past_month`, int64) - no parsing needed
- **5 capacity multipack patterns** detected in Amazon titles (e.g., "10 x 90g")

---

## TASK 1: PACK QUANTITY PATTERNS DETECTED

### 1.1 Explicit Unit Keywords Found

| Keyword | Count | Example |
|---------|-------|---------|
| **PCE** | 11 | "ARENA GLASS TUMBLERS 360ML 3PCE" |
| **PCS** | 7 | "DEKTON CABLE TIES BLACK 100PCS 4.8MMX300MM" |
| **PK** | 15 | "AIRWICK CANDLE VANILLA & BROWN SUGAR 105G PK6" |
| **PACK** | 12 | "BRIGHT & HOMELY WOODEN PEGS 36 PACK" |
| **PIECES** | 8 | "DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES" |
| **PACK OF** | 7 | "PUREBREED PUPPY TRAINING PADS 40X50CM PACK OF 10" |

### 1.2 Trailing Number Patterns (Potential Quantity)

**18 occurrences found.** Examples:
- Row 0: "EUROWRAP GIANT BIRTHDAY BADGE GIRL **3**"
- Row 18: "PARTY CRAZY BALLOONS ASSORTED **20**"
- Row 34: "UNIQUE CANDLE NUMBER W/DECOR **6**"

⚠️ **CAUTION:** Some trailing numbers are part codes, not quantities (e.g., "DECOR 6" = candle number 6, not pack of 6)

### 1.3 Leading Multiplier Check

**0 occurrences found.** This supplier does NOT use "10x Product" style at title start.

### 1.4 Dimension vs Quantity Shield

The supplier uses these dimension formats:
- **CM format:** Numbers directly attached (`40CM`, `26.5CM`) or with space (`40 CM`)
- **MM format:** Usually attached (`5MM`, `4.8MM`)
- **ML format:** Usually attached (`440ML`, `1200ML`)
- **INCH format:** Both `2INCH` and `IN` suffix (e.g., `6X8`, `8X10INCH`)
- **LTR format:** Used for litres (`0.5LTR`, `1.3 LTR`)

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**5 capacity multipack patterns detected in Amazon titles:**

| Row | Pattern | Full Context | RSU Should Be |
|-----|---------|--------------|---------------|
| 228 | `10 x 90g` | "Good Boy Chicken & Rice Sticks - Bulk B..." | RSU = 10 (10 bags) |
| 243 | `7 x 100g` | "Natures Menu Meaty Treats for Adult Dogs" | RSU = 7 (7 bags) |
| 254 | `4 x 100g` | "Forthglade Meaty Sausages (4 x 100g Bags)" | RSU = 4 (4 bags) |
| 374 | `16 x 6g` | "Mixed Perfume Wax Melts: 16 x 6g Heart Shaped" | RSU = 16 (16 melts) |
| 456 | `6 x 15ml` | "NexGen 6 x 15ml Fragrance Oils Set" | RSU = 6 (6 bottles) |

**Rule Confirmed:** When Amazon shows `N x [capacity]ml/g/l`, the RSU = N (first number only). The capacity describes SIZE, not quantity to multiply.

---

## TASK 2: SALES SIGNAL DETECTION

| Property | Value |
|----------|-------|
| **Column Name** | `bought_in_past_month` |
| **Data Type** | `int64` (numeric) |
| **Sample Values** | [100, 50, 50, 50, 100, 50, 500, 50, 100, 50] |
| **Requires Text Parsing** | ❌ NO |
| **Contains "100+ bought" style** | ❌ NO |

---

## TASK 3: BRAND POSITION ANALYSIS

| Position | Count | Percentage |
|----------|-------|------------|
| **At START** | 96 | ~98% |
| **In MIDDLE** | 0 | 0% |
| **At END** | 2 | ~2% |

**Pattern:** `brand_position = "start"`

**Detected Brand Names:**
CHEF AID, DLUX, TALA, MINKY, BETTINA, PRIMA, PYREX, DEKTON, ROLSON, APAC, OPAL, FAIRY, AIRWICK, PALOMA, EUROWRAP, APOLLO, LYNWOOD, ABBEY, STARWASH, PROKLEEN, BRIGHT & HOMELY, GLEAMAX, STATUS, PANASONIC, DUNLOP, BLACKSPUR, PPS, BBQ, GIFTMAKER, FESTIVE MAGIC, PUREBREED, THL, ARENA, BABY PIPKIN, RAVENHEAD, SUNNEX, SABICHI, COUNTRY CLUB, ADORN, SOZALI, HOBBY

---

## CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION ---
# Generated for: part_1_jan.xlsx
# Date: 2026-01-02

SUPPLIER_NAMING_CONVENTION = {
    # Explicit unit keywords used by this supplier
    "explicit_units": ["pce", "pcs", "pk", "pack", "pieces", "pc"],
    
    # TRUE: This supplier uses trailing numbers as pack quantities (e.g., "BALLOONS 20")
    # CAUTION: Some trailing numbers are product codes (e.g., "CANDLE NUMBER 6")
    "allow_trailing_number_as_qty": True,
    
    # FALSE: This supplier does NOT use "10x Product" format at title start
    "leading_multiplier_check": False,
    
    # Dimension/measurement keywords to shield from quantity extraction
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", "yd", "yards"],
    
    # Brand position pattern (start, middle, end, or mixed)
    "brand_position": "start",
    
    # Sales data column
    "sales_column": "bought_in_past_month",
    
    # TRUE: "3 x 400ml" should be RSU=3 (3 bottles), NOT RSU=1200 (capacity * count)
    "capacity_pattern_as_rsu": True,
    
    # Additional patterns for this supplier
    "pack_of_pattern": True,      # Supplier uses "PACK OF N" format
    "xN_dimension_pattern": True  # Supplier uses "NxN" for dimensions (e.g., 40X40CM)
}
# ---------------------------------
```

---

## TASK 4: CALIBRATION WARNINGS (TRAP DETECTION)

### 4.1 DIMENSION TRAPS (NxN patterns mistaken for RSU)

These patterns contain dimensions that should NOT be interpreted as pack quantities:

```
Row 10: 'EASY STORAGE VACUUM BAG 70X100CM' → RSU=1 (70x100 is dimension), NOT RSU=7000
Row 55: 'PALOMA 2PLY IVORY 50 NAPKINS 40X40CM' → RSU=50 (napkin qty), 40x40 is size
Row 78: 'APOLLO GLASS CHOPPING BOARD CLEAR 28X38' → RSU=1 (28x38 is dimension)
Row 171: 'B & CO AIR FRYER LINER SILICONE 19 X 19CM' → RSU=1 (19x19 is dimension)
Row 179: 'HOME COLLECTION WHITE FRAME 6X8' → RSU=1 (6x8 is frame size)
Row 236: 'HOME COLLECTION BLACK FRAME 8X10INCH' → RSU=1 (8x10 is frame size)
Row 328: 'ADORN MUG 10X8CM ASSORTED' → RSU=1 (10x8 is mug dimension)
Row 453: 'FRAGRANCE WARMER 8X8' → RSU=1 (8x8 is dimension)
```

### 4.2 MODEL NUMBER TRAPS

Numbers in these titles are likely model numbers, NOT quantities:

```
Row 142: 'S/STEEL DOG BOWL ANTI SKID 240Z' → 24OZ is capacity, NOT 240 units
Row 195: 'BAUER STRAIGHTENER BRUSH 38820 BLACK' → 38820 is model number
Row 353: 'PPS FOIL 5 CONTAINERS & LID 200X111X55MM' → 200x111x55 is dimension
Row 355: 'BRIGHT & HOMELY PILLAR CANDLE IVORY 100 HOUR BURN' → 100 is burn hours
```

### 4.3 QUANTITY-INSIDE TRAPS

These contain quantity-per-pack, NOT number of packs:

```
Row 1: 'LUXURY CUPCAKE 100 CASES' → 1 pack containing 100 cases, RSU=1
Row 57: 'APAC RIBBON 2INCH 100 YARDS PURPLE' → 1 roll of 100 yards, NOT 100 rolls
Row 132: 'FESTIVE MAGIC LED LIGHTS 500 CLEAR CABLE' → 1 string of 500 LEDs, NOT 500 strings
Row 363: 'ROLSON CABLE TIES BLACK 200X4.8MM 100PCS' → 1 pack of 100 ties, NOT 100 packs
```

### 4.4 CAPACITY MULTIPACK TRAPS (Amazon Titles)

These capacity patterns should use N (first number), NOT N×capacity:

```
Row 228: '10 x 90g' should be RSU=10 (10 bags of 90g each), NOT RSU=900
Row 243: '7 x 100g' should be RSU=7 (7 bags of 100g each), NOT RSU=700
Row 254: '4 x 100g' should be RSU=4 (4 bags of 100g each), NOT RSU=400
Row 374: '16 x 6g' should be RSU=16 (16 x 6g heart melts), NOT RSU=96
Row 456: '6 x 15ml' should be RSU=6 (6 bottles of 15ml each), NOT RSU=90
```

### 4.5 POSSIBLE FALSE DATA MATCHES

⚠️ **Many rows show EAN-to-Amazon mismatches** where SupplierTitle and AmazonTitle are for completely different products. Examples from first 60 rows:

| Row | Supplier Title | Amazon Title | Issue |
|-----|---------------|--------------|-------|
| 0 | EUROWRAP GIANT BIRTHDAY BADGE GIRL | Motorola edge 60 fusion... | Complete mismatch |
| 1 | LUXURY CUPCAKE 100 CASES | Oversize Turbo Dryer Blower... | Complete mismatch |
| 2 | I LOVE YOU BALLOON 40CM | Mould King V8 Engine Building Blocks... | Complete mismatch |
| 6 | STATUS LED G9 2W LED CAPSULE BULB | 17.5" Portable DVD Player... | Complete mismatch |

**Recommendation:** The main analysis MUST verify EAN match validity and filter out obvious mismatches.

---

## SUMMARY STATISTICS

| Metric | Value |
|--------|-------|
| Total Rows | 2,402 |
| Rows Analyzed | 500 |
| Explicit Pack Keywords Found | 60 instances across 6 keywords |
| Trailing Numbers (potential qty) | 18 |
| Dimension Patterns (shield needed) | 153 (CM, MM, ML, LTR, OZ, INCH combined) |
| Capacity Multipack Patterns (Amazon) | 5 |
| Brand Position | START (98%) |
| Sales Column | `bought_in_past_month` (int64) |

---

**Report Generated By:** Data Pattern Specialist  
**For Use By:** Main FBA Analysis (Phase A)
