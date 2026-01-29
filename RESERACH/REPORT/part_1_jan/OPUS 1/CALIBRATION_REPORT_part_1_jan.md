# =============================================================================
# SUPPLIER CALIBRATION ANALYSIS REPORT
# File: part_1_jan.xlsx
# Generated: 2026-01-01
# Output Directory: OPUS 1
# =============================================================================

## EXECUTIVE SUMMARY

This pre-flight calibration analysis examines the first 50 rows of `part_1_jan.xlsx` 
to detect supplier-specific naming conventions, pack quantity formats, and data 
anomalies that will customize the main FBA analysis script.

---

## TASK 1: PACK QUANTITY PATTERNS DETECTED

### 1.1 Explicit Units Found
The supplier uses the following explicit unit patterns:

| Pattern | Examples Found |
|---------|----------------|
| `PC` / `PCS` | Row 4: "MINKY CURVE SCOURER **2PC**", Row 9: "FESTIVE MAGIC BELLS **8PC** ASSORTED" |
| `PIECES` | Row 3: "DLUX PEGS... **12 PIECES**", Row 35: "BRIGHT & HOMELY... **4 PIECES**" |
| `PACK` | Row 29: "LYNWOOD MINI ROLLER SET **5PACK**" |
| `PK` (shorthand) | Row 21: "AIRWICK CANDLE... **PK6**", Row 47: "FAIRY... **PK8**" |
| `CASES` | Row 1: "LUXURY CUPCAKE **100 CASES**" |

**Detected Explicit Unit Keywords:** `pc`, `pcs`, `pce`, `pk`, `pack`, `pieces`, `cases`

### 1.2 Trailing Numbers as Quantity
**MINIMAL USAGE** - Only 1 clear example found:
- Row 18: "PARTY CRAZY BALLOONS ASSORTED **20**" → `20` is quantity at end

**Recommendation:** `allow_trailing_number_as_qty = False` (or handle with caution)

### 1.3 Leading Multipliers
**NO EXAMPLES FOUND** in this sample.
- No patterns like `10x Product` or `6 x Item` detected in SupplierTitle.

**Recommendation:** `leading_multiplier_check = False`

### 1.4 Dimension vs Quantity Formats

The supplier frequently uses dimensions in titles. Key patterns:

| Dimension Format | Examples |
|-----------------|----------|
| `NNcm` (no space) | Row 2: "BALLOON **40CM**", Row 8: "PLACEMAT... **37CM**", Row 19: "LAUNCHER **50CM**" |
| `NNXNNCM` (dimension) | Row 10: "VACUUM BAG **70X100CM**" ← This is dimensions, NOT 70 × 100 quantity! |
| `NNml` (volume) | Row 32: "500ML", Row 44: "750ML", Row 49: "250ML" |
| `NNxNNmm` (dimension) | Row 36: "SCREWS ZP **5X60MM**" ← Screw size, NOT quantity |
| `NNm` (length) | Row 5: "CLOTHES LINE **30M**" |
| `NNg` (weight) | Row 21: "105G PK6" |

**⚠️ CRITICAL WARNING:** 
- `70X100CM` → **Dimensions** (70cm × 100cm bag), NOT 70 × 100 = 7000 items!
- `5X60MM` → **Screw specification**, NOT pack quantity!

---

## TASK 2: SALES SIGNAL DETECTION

### Sales Column: `bought_in_past_month`
- **Data Type:** `int64` (numeric, pre-parsed)
- **Format:** Clean integer values (50, 100, 200, 300, 400, 500)
- **No Parsing Required:** Values are already numeric, no text like "100+ bought"

**Unique Values Detected:**
```
50, 100, 200, 300, 400, 500
```

**Recommendation:** `sales_column = "bought_in_past_month"`

---

## TASK 3: BRAND PATTERNS

### Brand Position Analysis
Based on first word analysis of SupplierTitle:

| First Word | Count | Type |
|------------|-------|------|
| DLUX | 3 | **Brand** |
| CHEF | 2 | Brand (Chef Aid) |
| PROKLEEN | 2 | **Brand** |
| PRIMA | 2 | **Brand** |
| BETTINA | 2 | **Brand** |
| PANASONIC | 1 | **Brand** |
| AIRWICK | 1 | **Brand** |
| DUNLOP | 1 | **Brand** |
| FAIRY | 1 | **Brand** |
| MINKY | 1 | **Brand** |
| TALA | 1 | **Brand** |

**Mixed Position Words (NOT brands):**
- `LUXURY`, `EASY`, `CHRISTMAS`, `HAPPY`, `LOVE`, `SNOW`, `BRIGHT`, `SPRAY`, `PAPER`, `PLATE`, `WET`, `PLUNGER`, etc.

**Conclusion:** Brand position is **MIXED**. Some titles start with brand names, others start with product descriptors.

**Recommendation:** `brand_position = "mixed"`

---

## TASK 4: CALIBRATION CONFIGURATION BLOCK

```python
# --- CALIBRATION CONFIGURATION for part_1_jan.xlsx ---
SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity explicit unit keywords found in this supplier file
    "explicit_units": ["pc", "pcs", "pce", "pk", "pack", "pieces", "piece", "cases"],
    
    # Set FALSE - trailing numbers are rare and often cause false positives
    # Only 1 example found (Row 18: "BALLOONS ASSORTED 20")
    "allow_trailing_number_as_qty": False,
    
    # Set FALSE - no "10x Product" patterns found in supplier titles
    "leading_multiplier_check": False,
    
    # Dimension/measurement keywords to SHIELD from quantity parsing
    # These are NOT pack quantities - they are physical measurements
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", 
        "ft", "m", "w"  # watts, meters
    ],
    
    # Additional dimension patterns to explicitly ignore
    "dimension_x_patterns": True,  # e.g., 70X100CM, 5X60MM (NOT quantities!)
    
    # Brand position in supplier title
    "brand_position": "mixed",  # Some start with brand, some with descriptor
    
    # Sales column to use
    "sales_column": "bought_in_past_month",  # Already numeric, no parsing needed
    
    # Sales data type
    "sales_requires_parsing": False  # Already int64
}
# -------------------------------------------------------
```

---

## TASK 5: CALIBRATION WARNINGS (Potential False Positive Traps)

### ⚠️ HIGH RISK ROWS

| Row | SupplierTitle | Warning | Reason |
|-----|--------------|---------|--------|
| **1** | LUXURY CUPCAKE 100 CASES | **Quantity Trap** | "100 CASES" = pack of 100 cupcake cases (product name), NOT 100 separate items |
| **10** | EASY STORAGE VACUUM BAG 70X100CM | **Dimension Trap** | "70X100CM" = bag dimensions (70cm × 100cm), NOT 70×100 = 7000 quantity |
| **16** | PANASONIC UPRIGHT SDB113 | **Model Number Trap** | "SDB113" is a model number, NOT quantity |
| **36** | SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM | **Dimension Trap** | "5X60MM" = screw specification (5mm diameter × 60mm length), NOT pack quantity |
| **37** | DEKTON MASONRY DRILL BIT 5MM X 85MM | **Dimension Trap** | "5MM X 85MM" = drill bit size, NOT quantity |
| **5** | STARWASH CLOTHES LINE 30M | **Measurement Trap** | "30M" = 30 meters length, NOT 30 packs |
| **38** | HAPPY 6TH BIRTHDAY BANNER BLUE 9FT | **Mixed Trap** | "6TH" is ordinal (birthday), "9FT" is length |
| **6** | STATUS LED G9 2W LED CAPSULE BULB EACH | **Model Number Trap** | "G9" is bulb type, "2W" is wattage |

### ⚠️ MEDIUM RISK PATTERNS

1. **PK Suffix Pattern:** `PK6`, `PK8` → These ARE valid pack quantities (e.g., "PK6" = pack of 6)
2. **CASES Pattern:** "100 CASES" in Row 1 needs human review - is this 100 items or a product called "cupcake cases"?

### ✅ SAFE PATTERNS

- `12 PIECES` → Clear quantity indicator
- `2PC`, `8PC` → Clear pack count
- `5PACK` → Clear pack count

---

## DATA QUALITY OBSERVATIONS

### EAN-to-Amazon Mismatch Concerns
**CRITICAL:** Many rows show severe EAN-to-Amazon mismatches:
- Row 0: Supplier = "BIRTHDAY BADGE" → Amazon = "Motorola edge 60 fusion" (phone!)
- Row 1: Supplier = "CUPCAKE CASES" → Amazon = "Turbo Dryer Blower" (car accessory!)
- Row 2: Supplier = "BALLOON" → Amazon = "V8 Engine Building Blocks"

This suggests:
1. EAN data may be incorrect/corrupted
2. EAN matching needs strict validation
3. High false positive risk if relying on EAN alone

---

## RECOMMENDED MAIN ANALYSIS ADJUSTMENTS

1. **Enable Dimension Shield:** Treat any `NxNcm`, `NxNmm` patterns as dimensions, not quantities
2. **Model Number Detection:** Exclude alphanumeric codes like `SDB113`, `G9` from quantity parsing
3. **Strict EAN Validation:** Given the mismatch issues, verify EAN checksums and title similarity
4. **Manual Review Required:** Flag any row where SupplierTitle vs AmazonTitle have <30% word overlap
5. **"CASES" Handling:** Treat "100 CASES" as product name, not pack quantity unless explicitly marked

---

*Report generated for OPUS 1 pre-flight calibration*
