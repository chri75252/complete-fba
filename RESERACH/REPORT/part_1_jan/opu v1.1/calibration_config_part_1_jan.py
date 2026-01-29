# CALIBRATION REPORT - part_1_jan.xlsx
# Generated: 2026-01-02
# Pre-flight analysis for FBA Product Analysis

"""
================================================================================
                    AGENTIC FBA CALIBRATION REPORT v1.1
                    File: part_1_jan.xlsx (2,402 rows)
================================================================================

## TASK 1: PACK QUANTITY PATTERN ANALYSIS
--------------------------------------------------------------------------------

### Explicit Units Detected:
| Unit     | Count | Frequency |
|----------|-------|-----------|
| pack     | 83    | Common    |
| pieces   | 58    | Common    |
| pcs      | 7     | Rare      |
| pce      | 4     | Rare      |
| pk       | 3     | Rare      |
| piece    | 2     | Rare      |

### Pattern Summary:
1. **Explicit Units**: "PACK" and "PIECES" are the dominant quantity indicators
   - Example: "BRIGHT & HOMELY WOODEN PEGS 36 PACK"
   - Example: "DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES"

2. **Trailing Numbers**: 88 occurrences detected (COMMON)
   - Example: "PARTY CRAZY BALLOONS ASSORTED 20" -> 20 is the pack quantity
   - Example: "BALLOONS SILVER 20" -> 20 is the quantity
   - ⚠️ WARNING: Some trailing numbers are MODEL NUMBERS, not quantities:
     - "MENS LEATHER WALLET 1148" -> 1148 is model number
     - "PRIMA SCOOP DIE CAST 13098" -> 13098 is model number
     - "HOBBY BUTTER DISH 031229" -> 031229 is model number

3. **Leading Multipliers**: 0 occurrences (NOT USED by this supplier)
   - Pattern like "10x Product" is NOT common for this supplier

4. **Dimension vs Quantity Formatting**:
   - Dimensions use "X" separator: "70X100CM", "40X40CM", "5X60MM"
   - No space typically: "70X100CM" not "70 X 100CM"
   - Size units: CM, MM, INCH, IN, " are common
   - 118 dimension patterns detected

## TASK 1B: CAPACITY MULTIPACK PATTERNS
--------------------------------------------------------------------------------

### Amazon Title Patterns (N x Capacity):
28 patterns detected in Amazon titles with format "N x [capacity]"

Examples:
- "10 x 90g" -> RSU = 10 (ten 90g items)
- "7 x 100g" -> RSU = 7 (seven 100g items)  
- "6 X 70 ML" -> RSU = 6 (six 70ml deodorants)
- "3 x 400ml" -> RSU = 3 (three 400ml spray cans)
- "12 x 70 g" -> RSU = 12 (twelve 70g candles)
- "8 x 150g" -> RSU = 8 (eight 150g air fresheners)

**RULE**: When Amazon shows "N x [capacity]ml/g/l", the RSU = N (first number only).
The capacity value describes SIZE of each unit, NOT quantity to multiply.

## TASK 2: SALES SIGNAL DETECTION
--------------------------------------------------------------------------------

**Detected Column**: `bought_in_past_month`

**Data Type**: Numeric (integer)
**Sample Values**: [100, 50, 50, 50, 100, 50, 500, 50, 100, 50]

**Notes**: 
- Data is already parsed as integers, no text parsing required
- No "100+ bought" text format detected
- Direct numeric usage is possible

## TASK 3: BRAND PATTERN ANALYSIS
--------------------------------------------------------------------------------

### Brand Position Analysis (sample of 500 titles):
| Position | Count | Percentage |
|----------|-------|------------|
| START    | 83    | 97.6%      |
| MIDDLE   | 0     | 0.0%       |
| END      | 2     | 2.4%       |

**Conclusion**: `brand_position = "start"`

This supplier STRONGLY prefers placing brand names at the START of product titles.
Examples:
- "EUROWRAP GIANT BIRTHDAY BADGE GIRL 3"
- "MINKY CURVE SCOURER 2PC"
- "STARWASH CLOTHES LINE 30M"
- "STATUS LED G9 2W LED CAPSULE BULB EACH"
- "CHEF AID LANC PEELER PLASTIC HAND"

## TASK 4: CALIBRATION WARNINGS
--------------------------------------------------------------------------------

### ⚠️ DIMENSION TRAPS (High Risk):
These patterns LOOK like multipliers but are DIMENSIONS:

| Row | Pattern | Title | Correct Interpretation |
|-----|---------|-------|------------------------|
| 10  | 70X100CM | EASY STORAGE VACUUM BAG 70X100CM | RSU=1 (dimensions) |
| 36  | 5X60MM | SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM | RSU=1 (dimensions) |
| 55  | 40X40CM | PALOMA 2PLY IVORY 50 NAPKINS 40X40CM | RSU=1 (napkin size) |
| 81  | 70X55X23CM | LAUNDRY BAG HUL LARGE 70X55X23CM | RSU=1 (bag dimensions) |
| 99  | 80X60X26CM | LAUNDRY BAG HUL XLARGE 80X60X26CM | RSU=1 (bag dimensions) |
| 111 | 40X50CM | PUREBREED PUPPY TRAINING PADS 40X50CM PACK OF 10 | RSU=10 (pack qty) |
| 171 | 19 X 19CM | B & CO AIR FRYER LINER SILICONE 19 X 19CM | RSU=1 (liner size) |

### ⚠️ MODEL NUMBER TRAPS (Medium Risk):
These trailing numbers are MODEL NUMBERS, not quantities:

| Row | Pattern | Should NOT be interpreted as |
|-----|---------|------------------------------|
| 28  | MENS LEATHER WALLET 1148 | RSU=1148 (it's model 1148) |
| 30  | PRIMA SCOOP DIE CAST 13098 | RSU=13098 (it's model #) |
| 37  | HOBBY BUTTER DISH 031229 | RSU=31229 (it's model #) |

Model number detection rule: If trailing number > 100 and has NO unit keyword nearby, 
likely a model/SKU number.

### ⚠️ QUANTITY-INSIDE TRAPS (Medium Risk):
These patterns show quantity INSIDE the pack, not number of packs:

| Row | Pattern | Correct Interpretation |
|-----|---------|------------------------|
| 1   | LUXURY CUPCAKE 100 CASES | RSU=1 (1 pack of 100 cases) |
| 18  | PARTY CRAZY BALLOONS ASSORTED 20 | RSU=1 (1 pack of 20 balloons) |
| 55  | PALOMA 2PLY IVORY 50 NAPKINS 40X40CM | RSU=1 (1 pack of 50 napkins) |
| 74  | BRIGHT & HOMELY WOODEN PEGS 36 PACK | RSU=1 (1 pack of 36 pegs) |

### ⚠️ CAPACITY MULTIPACK TRAPS (Critical):
Amazon titles with "N x capacity" patterns:

| Example | WRONG | CORRECT |
|---------|-------|---------|
| "3 x 400ml" | RSU=1200 | RSU=3 (three bottles) |
| "6 X 70 ML" | RSU=420 | RSU=6 (six deodorants) |
| "12 x 70 g" | RSU=840 | RSU=12 (twelve candles) |

### ⚠️ PK/PACK SUFFIX PATTERNS:
Some items have pack quantities encoded as "PK" suffix:

| Row | Pattern | Pack Quantity |
|-----|---------|---------------|
| 21  | AIRWICK CANDLE VANILLA & BROWN SUGAR 105G PK6 | 6 |
| 47  | FAIRY WASHING UP LIQUID MAX POWER ORIGINAL 440ML PK8 | 8 |

================================================================================
"""

# --- CALIBRATION CONFIGURATION (v1.1) ---
# NOTE: These values are DETECTED from this specific supplier file (part_1_jan.xlsx)
SUPPLIER_NAMING_CONVENTION = {
    # Pack quantity patterns
    "explicit_units": ["pack", "pieces", "pcs", "pce", "pk", "piece", "pc"],
    "allow_trailing_number_as_qty": True,  # COMMON pattern for this supplier
    "leading_multiplier_check": False,      # NOT used by this supplier
    
    # Dimension/measurement shield keywords  
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in"],
    
    # Dimension pattern detection (to exclude from pack qty parsing)
    "dimension_patterns": [
        r"\d+\s*[xX]\s*\d+\s*(CM|MM|IN|INCH)",  # 70X100CM, 40X40CM
        r"\d+\s*[xX]\s*\d+\s*[xX]\s*\d+\s*(CM|MM)",  # 70X55X23CM (3D dimensions)
    ],
    
    # Capacity pattern markers (these describe SIZE, not quantity)
    "capacity_markers": ["ml", "l", "ltr", "g", "kg", "oz", "cl"],
    
    # Brand position
    "brand_position": "start",  # 97.6% of brands appear at START of title
    
    # Sales data column
    "sales_column": "bought_in_past_month",  # Numeric, no parsing needed
    
    # Capacity multipack interpretation
    "capacity_pattern_as_rsu": True,  # "3 x 400ml" means RSU=3, NOT 1200
    
    # Model number detection threshold
    "model_number_min_digits": 4,  # Numbers >= 4 digits with no unit = likely model#
    
    # Pack quantity suffix patterns
    "pack_suffix_patterns": [
        r"PK\s*(\d+)",   # PK6, PK8, PK 12
        r"PACK\s+OF\s+(\d+)",  # PACK OF 10
        r"(\d+)\s*PACK$",  # 36 PACK
        r"(\d+)\s*PIECES$",  # 12 PIECES
        r"(\d+)\s*PCS$",  # 50 PCS
    ],
}
# -----------------------------------------

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "=" * 80)
    print("CALIBRATION CONFIG (Python Dictionary):")
    print("=" * 80)
    import json
    print(json.dumps(SUPPLIER_NAMING_CONVENTION, indent=2))
