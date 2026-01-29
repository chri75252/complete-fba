# 📊 FBA CALIBRATION - VISUAL PATTERN GUIDE

**File:** part 5 jan.xlsx  
**Date:** 2026-01-06  
**Purpose:** Quick visual reference for supplier-specific patterns  

---

## 🎯 AT-A-GLANCE CONFIGURATION

```python
# COPY THIS INTO YOUR MAIN FBA ANALYSIS PROMPT
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pcs', 'piece', 'pk'],
    "allow_trailing_number_as_qty": False,  # ⚠️ CRITICAL: DISABLED
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    "brand_position": "start",  # ✅ 93% confidence
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": True  # ⚠️ REQUIRED
}
```

---

## 📋 ACTUAL DATA EXAMPLES

### ✅ EXAMPLE 1: Explicit Pack Quantity (RELIABLE)

**Row 7 - Supplier Title:**
```
DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES
                                                 ^^^^^^^^^
                                                 Clear pack indicator!
```

**Pattern:** `12 PIECES` → RSU = 12  
**Confidence:** ✅ **HIGH** - Explicit unit indicator  
**Action:** Extract pack quantity = 12

---

### ⚠️ EXAMPLE 2: Trailing Number (FALSE POSITIVE TRAP!)

**Row 3 - Supplier Title:**
```
EUROWRAP GIANT BIRTHDAY BADGE GIRL 3
                                   ^
                                   Model variant, NOT quantity!
```

**Pattern:** Ends with `3`  
**Trap:** Could be misinterpreted as "3 badges"  
**Reality:** Single badge (variant "Girl 3" vs "Girl 1", "Girl 2")  
**Confidence:** ❌ **DO NOT USE** - High false positive risk  
**Action:** Ignore trailing numbers for this supplier

---

### ⚠️ EXAMPLE 3: Critical False Positive

**Row 43 - Supplier Title:**
```
UNIQUE CANDLE NUMBER W/DECOR 6
                             ^
                             This is a candle SHAPED like the number "6"!
```

**Pattern:** Ends with `6`  
**Trap:** Would be interpreted as "6 candles"  
**Reality:** Single decorative candle (product IS the number 6)  
**Confidence:** ❌ **CRITICAL** - 100% false positive  
**Action:** **NEVER** treat trailing numbers as quantities for this supplier

---

### ✅ EXAMPLE 4: Dimension (SHIELD CORRECTLY)

**Row 2 - Supplier Title:**
```
151 WHITE NO-DRIP GLOSS PAINT 300ML
                              ^^^^^
                              This is capacity, NOT quantity!
```

**Pattern:** `300ML` (capacity measurement)  
**Correct Interpretation:** Single 300ml bottle (RSU = 1)  
**Incorrect Interpretation:** ❌ 300 units  
**Action:** Shield dimension keywords (`ml`, `cm`, `l`, `kg`, `g`, `oz`)

---

**Row 5 - Supplier Title:**
```
I LOVE YOU BALLOON 40CM ASSORTED
                   ^^^^
                   Size dimension, NOT quantity!
```

**Pattern:** `40CM` (size measurement)  
**Correct Interpretation:** Single 40cm balloon (RSU = 1)  
**Action:** Dimension shielding active

---

### ✅ EXAMPLE 5: Brand-First Pattern (93% CONSISTENT)

**Row 3:**
```
EUROWRAP GIANT BIRTHDAY BADGE GIRL 3
^^^^^^^^
Brand at start (ALL CAPS)
```

**Row 4:**
```
RSW BRIGHTS WASHING UP BOWL
^^^
Brand at start
```

**Row 7:**
```
DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES
^^^^
Brand at start
```

**Row 10:**
```
STARWASH CLOTHES LINE 30M
^^^^^^^^
Brand at start
```

**Pattern:** `[BRAND] [Product Description]`  
**Confidence:** ✅ **93%** (28 out of 30 titles)  
**Action:** Extract brand from first uppercase word

---

### ⚠️ EXAMPLE 6: Pipe Character (TABLE FORMATTING ISSUE)

**Row 28 - Amazon Title:**
```
Lenovo Idea Tab Pro Android Tablet | 12.7 inch Full HD Display | 
MediaTek Dimensity 8300 | 128GB | Wi-Fi 6 | 8GB RAM | Luna Grey + Pen
                                   ^     ^        ^              ^
                                   Pipe characters will break Markdown tables!
```

**Issue:** Pipe characters (`|`) are Markdown table delimiters  
**Impact:** Output tables will be malformed  
**Solution:** Replace `|` with `/` in output  
**Action:** Enable `table_pipe_sanitization = True`

---

## 🔍 PATTERN RECOGNITION GUIDE

### ✅ SAFE TO EXTRACT (High Confidence)

| Pattern | Example | Extraction | Confidence |
|---------|---------|------------|-----------|
| `X PIECES` | `12 PIECES` | RSU = 12 | ✅ HIGH |
| `X PCS` | `50 PCS` | RSU = 50 | ✅ HIGH |
| `PACK OF X` | `PACK OF 6` | RSU = 6 | ✅ HIGH |
| `X PK` | `24 PK` | RSU = 24 | ✅ HIGH |

---

### ⚠️ SHIELD (Do NOT Extract as Quantity)

| Pattern | Example | Why Shield | Action |
|---------|---------|------------|--------|
| `X ML` | `300ML` | Capacity | Dimension shield |
| `X CM` | `40CM` | Size | Dimension shield |
| `X KG` | `2KG` | Weight | Dimension shield |
| `X G` | `500G` | Weight | Dimension shield |
| `X M` | `30M` | Length | Dimension shield |

---

### ❌ IGNORE (False Positive Traps)

| Pattern | Example | Why Ignore | Risk |
|---------|---------|------------|------|
| Trailing number | `BADGE GIRL 3` | Model variant | HIGH |
| Trailing number | `CANDLE NUMBER 6` | Product IS the number | CRITICAL |
| Trailing number | `BALLOONS 20` | Ambiguous | HIGH |
| Model numbers | `SERIES 2000` | Model designation | MEDIUM |

---

## 📊 DATA QUALITY CHECKLIST

### ✅ Clean Data (Safe to Use)

- [x] **Sales Column:** `bought_in_past_month` - Numeric values (50-900)
- [x] **Brand Position:** 93% consistency (first word)
- [x] **Explicit Units:** Standard notation (`pcs`, `pack`, `pk`, `piece`)
- [x] **Dimension Format:** Consistent `NUMBER + UNIT` (e.g., "300ML", "40CM")

---

### ⚠️ Requires Special Handling

- [x] **Pipe Characters:** 2 instances detected → Enable sanitization
- [x] **Trailing Numbers:** 3 instances, all false positives → DISABLE extraction
- [ ] **Future Monitoring:** Watch for new patterns in full 2,789-row dataset

---

## 🚨 CRITICAL DECISION MATRIX

| If You See... | ✅ DO | ❌ DON'T |
|--------------|------|---------|
| `12 PIECES` | Extract RSU = 12 | - |
| `300ML` | Shield (dimension) | Extract as qty = 300 |
| `BADGE GIRL 3` | Treat as single item | Extract RSU = 3 |
| `CANDLE NUMBER 6` | Treat as single item | Extract RSU = 6 |
| `PACK OF 24` | Extract RSU = 24 | - |
| Brand at start | Extract first word | Look elsewhere |
| `Tablet | 12.7 inch` | Sanitize `|` to `/` | Leave as-is in table |

---

## 🎯 VALIDATION TEST CASES

Before running full analysis, verify these specific rows:

### Test Case 1: Row 3 (Trailing Number)
```
Supplier: EUROWRAP GIANT BIRTHDAY BADGE GIRL 3
Expected: RSU = 1 (single badge, variant "Girl 3")
Verify: System does NOT extract RSU = 3
```

### Test Case 2: Row 43 (Critical False Positive)
```
Supplier: UNIQUE CANDLE NUMBER W/DECOR 6
Expected: RSU = 1 (candle shaped like number 6)
Verify: System does NOT extract RSU = 6
```

### Test Case 3: Row 7 (Explicit Pack)
```
Supplier: DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES
Expected: RSU = 12 (explicit "12 PIECES")
Verify: System correctly extracts RSU = 12
```

### Test Case 4: Row 2 (Dimension Shield)
```
Supplier: 151 WHITE NO-DRIP GLOSS PAINT 300ML
Expected: RSU = 1 (300ml is capacity, not quantity)
Verify: System does NOT extract RSU = 300
```

### Test Case 5: Row 28 (Pipe Sanitization)
```
Amazon: Lenovo Idea Tab Pro Android Tablet | 12.7 inch...
Expected: Pipes replaced with "/" in output table
Verify: Table formatting is not broken
```

---

## 📈 CONFIDENCE LEVELS

| Aspect | Level | Symbol |
|--------|-------|--------|
| Explicit Units | Very High | 🟢🟢🟢 |
| Brand Position | Very High | 🟢🟢🟢 |
| Sales Data | High | 🟢🟢 |
| Dimension Shield | High | 🟢🟢 |
| Trailing Numbers (DISABLE) | High | 🟢🟢 |
| Capacity Multipacks (DISABLE) | High | 🟢🟢 |
| Overall Calibration | High | 🟢🟢 |

---

## ⚡ QUICK START

1. **Copy** the configuration block at the top
2. **Paste** into your main FBA analysis prompt
3. **Run** analysis on full 2,789-row dataset
4. **Validate** against test cases above
5. **Review** output for any unexpected patterns beyond first 50 rows

---

## 📞 SUPPORT NOTES

**If analysis produces unexpected results:**

1. Check Row 3, 43 - trailing numbers should be RSU = 1
2. Verify `300ML` interpreted as dimension, not qty = 300
3. Confirm brands extracted from start of titles (28/30 success rate)
4. Inspect tables for broken formatting (pipe characters)

**High-confidence areas:**
- Explicit pack units (`12 PIECES`, `50 PCS`)
- Brand positioning (93% brand-first)
- Sales data quality (clean numeric values)

**Low-confidence areas:**
- Trailing numbers (HIGH false positive risk - DO NOT USE)

---

*Visual Pattern Guide - Ready for Production*  
*Use this as a reference during main FBA analysis*
