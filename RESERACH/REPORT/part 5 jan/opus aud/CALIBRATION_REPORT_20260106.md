# FBA CALIBRATION ANALYSIS REPORT
**Date:** 2026-01-06
**File:** part 5 jan.xlsx
**Total Rows:** 2789
**Sample Analyzed:** First 50 rows

## EXECUTIVE SUMMARY

- **Explicit Units Detected:** pack, pcs, piece, pk
- **Trailing Number Pattern:** Rare/Not detected
- **Leading Multiplier Pattern:** Rare
- **Capacity Multipack Pattern:** Not detected
- **Brand Position:** START
- **Sales Column:** bought_in_past_month
- **Pipe Character Issues:** Yes - sanitization required

## DETAILED FINDINGS

### TASK 1: Pack Quantity Patterns

#### 1.1 Explicit Units
Detected: `pack, pcs, piece, pk`

#### 1.2 Trailing Numbers
- **Row 3:** `EUROWRAP GIANT BIRTHDAY BADGE GIRL 3` → trailing `3`
- **Row 25:** `PARTY CRAZY BALLOONS ASSORTED 20` → trailing `20`
- **Row 43:** `UNIQUE CANDLE NUMBER W/DECOR 6` → trailing `6`

#### 1.3 Leading Multipliers
No leading multiplier patterns detected.

#### 1.4 Dimensions
- **Row 2:** Contains `('300', 'ML')`
- **Row 5:** Contains `('40', 'CM')`
- **Row 6:** Contains `('62', 'CM')`
- **Row 10:** Contains `('30', 'M')`
- **Row 14:** Contains `('37', 'CM')`

### TASK 1B: Capacity Multipack Patterns

No capacity multipack patterns detected.

### TASK 1C: Spec/Feature 'Nx' Patterns (Non-Pack)

No spec/feature 'Nx' patterns detected.

### TASK 2: Sales Signal

- **Column:** `bought_in_past_month`
- **Needs Parsing:** False
- **Sample Values:** ['500', '100', '100', '50', '50']

### TASK 3: Brand Patterns

- **Position:** START
- **Confidence:** 28/30 titles start with uppercase word

**Examples:**
- **Row 3:** `EUROWRAP` in title
- **Row 4:** `RSW` in title
- **Row 6:** `WORLD` in title
- **Row 7:** `DLUX` in title
- **Row 8:** `ARTIST` in title

### TASK 4: Calibration Warnings

#### Row 28: Contains pipe character (|) - may break table formatting
```
Lenovo Idea Tab Pro Android Tablet | 12.7 inch Full HD Display | MediaTek Dimensity 8300 | 128GB | Wi-Fi 6 | 8GB RAM | Luna Grey + Pen
```

#### Row 42: Contains pipe character (|) - may break table formatting
```
LEGO | Marvel Iron Man Mark 3 Collectors' Edition Figure - Avengers Display Model Kit for Adults - incl. a Minifigure & Arc Reactor - Collectible Gift for Fans - 76344
```

## CONFIGURATION OUTPUT


```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pcs', 'piece', 'pk'],  # Detected units
    "allow_trailing_number_as_qty": False,  # FALSE - rare/not detected
    "leading_multiplier_check": False,     # FALSE - rare
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "ft", "m"],
    "brand_position": "start", # start
    "sales_column": "bought_in_past_month", # Detected column name
    "capacity_pattern_as_rsu": False, # FALSE - not detected
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],
    "table_pipe_sanitization": True # TRUE - pipes detected
}
# ---------------------------------
```

## RECOMMENDATIONS

1. **Pack Quantity Extraction:**

2. **Brand Detection:**
   - Consistent brand positioning at start (high confidence)

3. **Data Quality:**
   - Enable pipe character sanitization for table formatting

4. **Edge Cases:**
   - 2 potential traps detected - review warnings section

---
**End of Calibration Report**
