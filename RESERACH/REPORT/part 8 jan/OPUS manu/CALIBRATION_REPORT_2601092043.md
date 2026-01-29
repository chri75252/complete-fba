# AGENTIC FBA CALIBRATION REPORT
## Pre-Flight Analysis for: `part 8 jan.xlsx`

**Generated:** 2026-01-09 20:43  
**Analyzed Rows:** First 50 rows  
**Purpose:** Detect supplier naming conventions, pack patterns, and data anomalies to customize the main analysis prompt.

---

## 🚨 CRITICAL FINDING: DATA QUALITY ISSUE

### **78% of rows have NO word overlap between SupplierTitle and AmazonTitle**

This indicates **severe EAN-to-ASIN mapping issues**. The Amazon titles appear to be from completely different products than the supplier titles. Examples:

| Row | Supplier Title | Amazon Title (mapped via EAN) |
|-----|----------------|-------------------------------|
| 0 | 151 WHITE NO-DRIP GLOSS PAINT 300ML | LG OLED48C45LA 48-Inch OLED Evo 4K UHD Smart TV... |
| 1 | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 | Motorola edge 60 fusion, Pantone Slipstream... |
| 2 | LUXURY CUPCAKE 100 CASES | Oversize Turbo Dryer Blower, Car Accessories... |
| 4 | RSW BRIGHTS WASHING UP BOWL | Hyundai Petrol Backpack Leaf Blower... |

**Implication:** EAN validation and checksum verification is the **ONLY reliable link** between supplier and Amazon data. Title-based similarity matching will produce false positives/negatives.

---

## TASK 1: PACK QUANTITY PATTERN ANALYSIS

### 1.1 Explicit Unit Keywords Found
```
{'PIECES', 'PK', 'PCS', 'PC', 'PACK'}
```

**Examples:**
- Row 7: `DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES` → **12 units**
- Row 8: `MINKY CURVE SCOURER 2PC` → **2 units**
- Row 12: `ARTIST PAINT BRUSHES 10PC` → **10 units**
- Row 38: `AIRWICK CANDLE VANILLA & BROWN SUGAR 105G PK6` → **6 units**
- Row 39: `LYNWOOD MINI ROLLER SET 5PACK` → **5 units**

### 1.2 Trailing Numbers (DANGEROUS - Often NOT Quantity)
**Found: 3 instances**

| Row | Trailing Number | Full Title | Assessment |
|-----|-----------------|------------|------------|
| 1 | `3` | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 | **VARIANT CODE** (Girl 3, not 3-pack) |
| 25 | `20` | PARTY CRAZY BALLOONS ASSORTED 20 | **LIKELY QUANTITY** (20 balloons) |
| 43 | `6` | UNIQUE CANDLE NUMBER W/DECOR 6 | **PRODUCT DESIGN** (Number 6 candle, not 6-pack) |

⚠️ **Recommendation:** `allow_trailing_number_as_qty: False` — Trailing numbers are often variant/model codes in this supplier's data.

### 1.3 Leading Multipliers (e.g., "10x Product")
**Found: 0 instances**

No leading multiplier patterns detected in this dataset.

### 1.4 Dimension Patterns (Shield from Quantity Detection)
**Found: 9 instances**

| Row | Dimension | Context |
|-----|-----------|---------|
| 5 | 40CM | I LOVE YOU BALLOON 40CM |
| 6 | 62CM | WORLD OF PETS TOY BALL LAUNCHER 62CM ASSORTED |
| 14 | 37CM | ADORN PLACEMAT GOLD EMBOSSED 37CM ASSORTED |
| 16 | 70X100CM | EASY STORAGE VACUUM BAG 70X100CM |
| 26 | 50CM | PRIMA PET BALL LAUNCHER 50CM |
| 28 | 7 INCH | PAPER EASTER 10 PLATES 7 INCH |
| 37 | 10.5 INCH | PLATE 10.5 INCH ASSORTED |
| 42 | 26.5CM | PRIMA DINNER PLATE FLOWER DESIGN 26.5CM |
| 49 | 60MM | SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM |

⚠️ **Note:** Row 28 has BOTH dimension (7 INCH) AND quantity (10 PLATES) — requires careful parsing.

### 1.5 Capacity Patterns
**Found: 5 instances**

| Row | Capacity | Context |
|-----|----------|---------|
| 0 | 300ML | 151 WHITE NO-DRIP GLOSS PAINT 300ML |
| 33 | 1.6L | SQUARE CANISTER CLASSIC 1.6L SURT VRM |
| 38 | 105G | AIRWICK CANDLE VANILLA & BROWN SUGAR 105G PK6 |
| 47 | 85ML | REVITALISE ELIXIR EDT 85ML POUR FEMME EACH |
| 48 | 100ML | RED CROWN EDT100ML POUR FEMME EACH |

---

## TASK 1B: CAPACITY MULTIPACK PATTERNS

**Found: 0 instances**

No "N x [capacity]ml/g/l" patterns detected (e.g., "3 x 400ml") in the first 50 rows.

---

## TASK 1C: NON-PACK "Nx" SPEC/FEATURE PATTERNS

**Found: 0 instances**

No feature/spec multipliers detected (e.g., "2x magnification", "3x zoom").

---

## TASK 2: SALES SIGNAL DETECTION

| Column | Status | Data Type | Sample Values |
|--------|--------|-----------|---------------|
| `bought_in_past_month` | ✅ FOUND | int64 | [500, 100, 50, 100, 100, 50, 50, 50, 100, 50] |

**Notes:**
- Clean integer data, no parsing required
- Values represent monthly sales counts directly
- No text prefixes like "100+ bought" to strip

---

## TASK 3: BRAND PATTERN DETECTION

### Brand Presence Analysis

| Metric | Value |
|--------|-------|
| Brands in Supplier Titles | **23/50 (46.0%)** |
| Brands in Amazon Titles | **0/50 (0.0%)** |
| Brands at START of Supplier Title | **23/50 (46.0%)** |

### Detected Brands (from known brand list)
`MINKY`, `CHEF AID`, `TALA`, `PANASONIC`, `DUNLOP`, `AIRWICK`, `TONKITA`, `PROKLEEN`, `DEKTON`, `GRAFIX`, `EUROWRAP`, `STATUS`, `TOM SMITH`, `LYNWOOD`, `PRIMA`, `SECURPAK`, `STARWASH`, `DLUX`, `RSW`

### Brand Format Patterns
- **ALL_CAPS_AT_START**: Brands appear at the beginning of supplier titles in ALL CAPS
- **SPARSE IN AMAZON**: 0% brand presence in Amazon titles (likely due to mapping issues)

---

## TASK 4: CALIBRATION WARNINGS

### Critical Warnings

1. **CRITICAL: 78.0% of rows have NO word overlap between SupplierTitle and AmazonTitle.**  
   This dataset has severe EAN-to-ASIN mapping issues. Most Amazon titles appear to be wrong products!

### Specific Row Warnings

| Row | Warning | Title |
|-----|---------|-------|
| 1 | Trailing '3' is VARIANT CODE, not quantity | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 |
| 25 | Trailing '20' might be model OR quantity | PARTY CRAZY BALLOONS ASSORTED 20 |
| 43 | Trailing '6' is PRODUCT DESIGN (number-shaped candle) | UNIQUE CANDLE NUMBER W/DECOR 6 |

---

## FINAL CALIBRATION CONFIGURATION

```python
# --- CALIBRATION CONFIGURATION (part 8 jan.xlsx) ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['PIECES', 'PK', 'PCS', 'PC', 'PACK'],
    "allow_trailing_number_as_qty": False,  # DANGEROUS - trailing numbers are often variant codes (e.g., "GIRL 3")
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "m"],
    "brand_position": "start",  # Brands like MINKY, CHEF AID, TALA appear at start
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": False,
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": True,  # Amazon titles rarely have matching brand
    "strong_similarity_threshold": 0.20,  # LOW due to high mismatch rate
    "strong_shared_tokens_threshold": 2,  # LOW due to high mismatch rate
    "very_strong_similarity_threshold": 0.30,
    "very_strong_shared_tokens_threshold": 3,
    "gate_mode": "C_brand_sparse",  # Use sparse mode due to title mismatches
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,  # "3 x 400ml" means RSU=3
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True,
    
    # CRITICAL WARNING FLAGS
    "high_mismatch_rate": True,  # 39/50 rows have no title overlap
    "mismatch_percentage": 78.0,
    "require_strict_ean_validation": True,  # EAN validity is the only reliable link
}
# ---------------------------------
```

---

## RECOMMENDATIONS FOR MAIN ANALYSIS

1. **Rely on EAN Validation, NOT Title Similarity**  
   Due to 78% mismatch rate, EAN checksum validation is the only reliable way to verify product matches.

2. **Use Strict Pack Detection**  
   Only accept explicit unit keywords (`PCS`, `PC`, `PACK`, `PIECES`, `PK`). Do NOT treat trailing numbers as quantity.

3. **Apply Dimension Shielding**  
   Numbers followed by CM/MM/INCH/ML/G/KG/L should be shielded from pack detection.

4. **Use `gate_mode: C_brand_sparse`**  
   Amazon titles have 0% brand presence from the known brand list, so brand matching should be relaxed.

5. **Lower Similarity Thresholds**  
   Due to data quality issues, use lower thresholds (0.20-0.30) and accept fewer shared tokens (2-3).

6. **Manual Review Required**  
   Given the severe data quality issues, any automated analysis should flag items for manual review rather than auto-approving.

---

## FILES GENERATED

| File | Purpose |
|------|---------|
| `CALIBRATION_CONFIG.py` | Python configuration to import into main analysis |
| `calibration_output.txt` | Raw console output from analysis |
| `calibration_analysis.txt` | Side-by-side title comparison |
| `CALIBRATION_REPORT_2601092043.md` | This report |

---

*Report generated by Agentic FBA Calibration System*
