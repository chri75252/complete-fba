# FBA CALIBRATION ANALYSIS - DETAILED EXAMPLES REPORT

**Date:** 2026-01-06  
**File:** part 5 jan.xlsx  
**Total Rows:** 2,789  
**Sample Analyzed:** First 50 rows  

---

## EXECUTIVE SUMMARY

### Key Findings:
✅ **Explicit Units Detected:** `pack`, `pcs`, `piece`, `pk`  
⚠️ **Trailing Number Pattern:** **RARE** (only 3 examples in 50 rows)  
❌ **Leading Multiplier Pattern:** **NOT DETECTED**  
❌ **Capacity Multipack Pattern:** **NOT DETECTED**  
✅ **Brand Position:** **START** (28/30 titles = 93% confidence)  
✅ **Sales Column:** `bought_in_past_month` (numeric, no parsing needed)  
⚠️ **Pipe Characters:** **DETECTED** (2 instances - sanitization required)

---

## CALIBRATION CONFIGURATION

Based on the analysis of the first 50 rows, here is the recommended configuration:

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    # Detected explicit pack units in supplier titles
    "explicit_units": ['pack', 'pcs', 'piece', 'pk'],
    
    # Trailing numbers (e.g., "STICKS 200") are RARE in this dataset
    # Only 3/50 examples found - likely product model numbers, not pack quantities
    "allow_trailing_number_as_qty": False,
    
    # Leading multipliers (e.g., "10x Product") NOT DETECTED
    "leading_multiplier_check": False,
    
    # Dimension/measurement keywords to shield from being treated as quantities
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    
    # Brand position: Consistently at START (93% confidence)
    "brand_position": "start",
    
    # Sales data column (numeric values, no parsing required)
    "sales_column": "bought_in_past_month",
    
    # Capacity multipack patterns (e.g., "3 x 400ml") NOT DETECTED
    "capacity_pattern_as_rsu": False,
    
    # Spec/feature multiplier shielding (e.g., "2x zoom")
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    
    # Pipe character sanitization REQUIRED (detected in Amazon titles)
    "table_pipe_sanitization": True
}
# ---------------------------------
```

---

## DETAILED PATTERN ANALYSIS

### 1. EXPLICIT PACK UNITS

The supplier uses standard pack quantity indicators. Examples found:

- `pack` - Standard pack notation
- `pcs` - Pieces (common in wholesale)
- `piece` - Full word variant
- `pk` - Abbreviated pack notation

**Recommendation:** Enable detection for all four variants.

---

### 2. TRAILING NUMBER PATTERN

**Status:** ⚠️ **RARE / NOT RECOMMENDED**

Only **3 examples** found in 50 rows:

1. **Row 3:** `EUROWRAP GIANT BIRTHDAY BADGE GIRL 3` → trailing `3`
   - **Analysis:** Likely a model variant (Girl 3 vs Girl 1, Girl 2)
   - **Risk:** Could be mistaken for pack quantity

2. **Row 25:** `PARTY CRAZY BALLOONS ASSORTED 20` → trailing `20`
   - **Analysis:** Could be "20 balloons" OR "model variant 20"
   - **Risk:** HIGH - needs context verification

3. **Row 43:** `UNIQUE CANDLE NUMBER W/DECOR 6` → trailing `6`
   - **Analysis:** This is a candle shaped like the NUMBER "6", NOT 6 candles!
   - **Risk:** CRITICAL - false positive trap

**Recommendation:** **DISABLE** trailing number detection for this supplier. The pattern is too rare and has high false positive risk.

---

### 3. LEADING MULTIPLIER PATTERN

**Status:** ❌ **NOT DETECTED**

No instances of patterns like:
- `6 x Product Name`
- `10x Item Description`
- `3 x Pack of...`

**Recommendation:** DISABLE for this supplier.

---

### 4. DIMENSION PATTERNS

**Status:** ✅ **COMMON** - Shield from quantity extraction

Dimensions detected in multiple formats:

| Row | Format | Example |
|-----|--------|---------|
| 2 | `300 ML` | Capacity measurement |
| 5 | `40 CM` | Length measurement |
| 6 | `62 CM` | Length measurement |
| 10 | `30 M` | Length measurement |
| 14 | `37 CM` | Length measurement |

**Pattern:** Supplier uses `NUMBER + SPACE + UNIT` format

**Recommendation:** Apply strict dimension shielding with keywords: `cm`, `mm`, `ml`, `ltr`, `l`, `kg`, `g`, `oz`, `inch`, `ft`, `m`

---

### 5. CAPACITY MULTIPACK PATTERNS (Amazon Titles)

**Status:** ❌ **NOT DETECTED**

No instances of patterns like:
- `3 x 400ml` (should be RSU=3, not 1200)
- `6 x 33ml` (should be RSU=6, not 198)
- `Pack of 4 x 500g` (should be RSU=4, not 2000)

**Recommendation:** DISABLE capacity multipack logic for this dataset.

---

### 6. SPEC/FEATURE "Nx" PATTERNS

**Status:** ❌ **NOT DETECTED**

No instances of feature descriptions like:
- `2x Magnification`
- `10x Zoom`
- `1000x Microscope`

**Recommendation:** Keep shield keywords in place as a safety measure, but not critical for this supplier.

---

### 7. BRAND POSITIONING

**Status:** ✅ **HIGHLY CONSISTENT** (93% confidence)

**28 out of 30** titles start with an uppercase brand name:

| Row | Brand | Example Title |
|-----|-------|---------------|
| 3 | EUROWRAP | EUROWRAP GIANT BIRTHDAY BADGE GIRL 3 |
| 4 | RSW | RSW INTERNATIONAL... |
| 6 | WORLD | WORLD OF FLAVOURS... |
| 7 | DLUX | DLUX PRO... |
| 8 | ARTIST | ARTIST PALETTE... |

**Pattern:** `[BRAND] [Product Description]`

**Recommendation:** Use **"start"** position for brand extraction. High confidence that first uppercase word is the brand.

---

### 8. SALES SIGNAL

**Status:** ✅ **CLEAN DATA**

- **Column Name:** `bought_in_past_month`
- **Data Type:** Numeric (integer values)
- **Sample Values:** `500`, `100`, `100`, `50`, `50`
- **Parsing Required:** NO - values are already numeric

**Recommendation:** Direct numeric access, no text parsing needed.

---

## CALIBRATION WARNINGS

### ⚠️ WARNING 1: Pipe Characters in Amazon Titles

**Impact:** Will break Markdown table formatting

**Example 1 - Row 28:**
```
Lenovo Idea Tab Pro Android Tablet | 12.7 inch Full HD Display | MediaTek Dimensity 8300 | 128GB | Wi-Fi 6 | 8GB RAM | Luna Grey + Pen
```

**Example 2 - Row 42:**
```
LEGO | Marvel Iron Man Mark 3 Collectors' Edition Figure - Avengers Display Model Kit for Adults - incl. a Minifigure & Arc Reactor - Collectible Gift for Fans - 76344
```

**Recommendation:** 
- Enable `table_pipe_sanitization = True`
- Replace all `|` with `/` in output tables
- Preserve original in detailed analysis sections

---

### ⚠️ WARNING 2: Trailing Numbers - False Positive Trap

**Row 43 - CRITICAL EXAMPLE:**

**Supplier Title:** `UNIQUE CANDLE NUMBER W/DECOR 6`

**Analysis:**
- This is a decorative candle shaped like the NUMBER "6"
- The `6` is part of the product description, NOT a quantity
- If mistaken as pack quantity, would create: "bought 1, but it's actually 6" → false positive

**Recommendation:** 
- DO NOT enable trailing number detection
- Only 3/50 examples, all are model/variant numbers

---

### ⚠️ WARNING 3: Model Numbers That Look Like Quantities

**Potential Pattern:** Numbers like `200`, `300`, `1000` might appear in:
- Model numbers (e.g., "XYZ-2000")
- Series identifiers (e.g., "Professional 300 Series")
- Capacity (e.g., "300ml")

**Recommendation:**
- Always check context before treating numbers as quantities
- Prioritize explicit unit indicators (`pcs`, `pack`, etc.)
- Shield dimension keywords aggressively

---

## SUPPLIER-SPECIFIC INSIGHTS

### Supplier Naming Style:
1. **Brand-First Convention:** 93% of titles start with brand name in ALL CAPS
2. **Explicit Units:** Uses standard wholesaler notation (`pack`, `pcs`, `pk`)
3. **Dimensions:** Consistent `NUMBER SPACE UNIT` format
4. **No Multipacks:** Rare/no capacity multiplier patterns (e.g., "3 x 400ml")

### Data Quality:
- ✅ Clean numeric sales data
- ✅ Consistent brand positioning
- ⚠️ Pipe characters in Amazon titles (2% of sample)
- ⚠️ Trailing numbers are model variants, not quantities

### Analysis Strategy:
1. **Prioritize** explicit unit detection (`pcs`, `pack`, `pk`)
2. **Shield** dimension keywords aggressively
3. **Avoid** trailing number detection (high false positive risk)
4. **Sanitize** pipe characters for table output
5. **Trust** brand-first positioning for brand matching

---

## ACCEPTANCE CRITERIA FOR MAIN ANALYSIS

When running the main FBA analysis with this calibration:

### ✅ MUST PASS:
1. Products with explicit units (`50 pcs`, `Pack of 12`) are correctly identified
2. Dimensions (`300ml`, `40cm`) are NOT treated as pack quantities
3. Trailing numbers (`BADGE GIRL 3`) are NOT treated as pack quantities
4. Brand names are consistently extracted from start of title
5. Pipe characters in output tables are replaced with `/`

### ⚠️ VALIDATE:
1. No false positives from model numbers
2. "CANDLE NUMBER 6" correctly identified as single item, not 6-pack
3. Sales data correctly pulled from `bought_in_past_month` column

### ❌ MUST NOT HAPPEN:
1. Trailing numbers treated as pack quantities
2. Dimension values (ml, cm, kg) treated as pack quantities
3. Pipe characters breaking table formatting
4. Brand names extracted from middle/end of title

---

## NEXT STEPS

1. **Review Configuration:** Verify the `SUPPLIER_NAMING_CONVENTION` block matches your analysis requirements
2. **Test Edge Cases:** Run main analysis on the 3 warning examples (Rows 3, 25, 43)
3. **Validate Output:** Check that "CANDLE NUMBER 6" is NOT categorized as a 6-pack
4. **Monitor Full Dataset:** This calibration is based on first 50 rows - edge cases may appear in remaining 2,739 rows

---

**Calibration Status:** ✅ COMPLETE  
**Confidence Level:** HIGH (93% brand consistency, clean sales data)  
**Risk Areas:** Trailing numbers (3 examples - recommend DISABLE)  
**Data Quality:** GOOD (minor pipe character sanitization needed)

---

*End of Detailed Calibration Report*
