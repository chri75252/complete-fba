# Calibration Addendum (Data Pattern Detection) — `part_2_jan.xlsx` (v1.1)

**Input file (verified):**  
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx`  
**LastWriteTime:** `2026-01-02 21:28:06` (local)

**Detected supplier (from `SupplierURL` host):** `www.efghousewares.co.uk`

**Sample windows used**
- Supplier-side pattern scan: first ~80 rows (SupplierTitle + key columns)
- Amazon-title capacity multipack scan: first 5000 rows (AmazonTitle)
- EAN sanity scan: first 1000 rows (EAN, EAN_OnPage)

---

## TASK 1: DETECT PACK QUANTITY PATTERNS (SupplierTitle vs AmazonTitle)

### 1) Explicit Units (SupplierTitle)
Supplier titles frequently embed pack quantities using:
- Compact suffix: `10PC`, `2PC`, `8PC`
- Spaced variant: `2 PCE`
- Worded: `12 PIECES`, `4 PIECES`, `20 PACK`, `36 PACK`
- Compact “pack” form: `5PACK` (digit + `PACK` with no space)
- `PKN` form: `PK6`, `PK8` (e.g., `105G PK6`, `440ML PK8`)
- Other observed unit-ish tokens: `CASES`, `EACH`, `SET`, `BAG`

### 2) Implicit/Trailing Numbers (SupplierTitle)
Trailing raw numbers exist but are **rare** and **ambiguous** in this file:
- Examples: `... GIRL 3`, `... ASSORTED 20`, `... NUMBER ... 6`
Interpretation is mixed (variant number vs pack size), so treating *any* trailing number as RSU is unsafe.

### 3) Leading Multipliers (SupplierTitle)
No clear `10x ...` / `6 x ...`-at-start patterns observed in the first ~80 rows.

### 4) Dimension vs Quantity (SupplierTitle formatting)
This supplier uses very compact dimension/capacity formats that can be misread as multipacks:
- No-space dimensions: `70X100CM`, `5X60MM`
- Spaced dimensions: `5MM X 85MM`, `10.5 INCH`, `7 INCH`
- Capacity/size: `500ML`, `750ML`, `105G`, `1.6L`, `5LT`
- Length: `30M`, `100 YARDS`, `4 X 4M`

---

## TASK 1B: DETECT CAPACITY MULTIPACK PATTERNS (AmazonTitle)

Amazon titles in this report *do* contain common capacity multipack patterns, including:
- With spaces: `10 x 90g`, `7 x 100g`, `6 X 70 ML`
- No spaces: `12x 280ml`, `2x450g`, `2x250ML`
- “Total + detail” style: `Pack of 6, 420 ML (6 x 70 ML)`
- Multiple segments: `1 x 800 g/2 x 400 g` (can imply **sum of multipliers**)

**Rule confirmation for this file:** when Amazon shows `N x [capacity]ml/g/l`, treat **RSU = N** (capacity is size-per-unit, not quantity to multiply).

---

## TASK 2: DETECT SALES SIGNAL

**Detected sales column:** `bought_in_past_month`  
In the scanned rows it is **numeric (int)**, not strings like `"100+ bought"`.

---

## TASK 3: DETECT BRAND PATTERNS

Supplier titles are mostly uppercase and commonly start with a brand-like token (examples seen early: `PRIMA`, `UNIQUE`, `BETTINA`, `APAC`, `DLUX`, `EUROWRAP`, `MINKY`, `PALOMA`).

**brand_position:** `"start"`

---

## OUTPUT FORMAT (JSON-LIKE)

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    # Observed explicit quantity/unit markers used by this supplier in SupplierTitle
    # Includes compact forms (e.g., "10PC", "PK6") that require regex, not word-boundary splitting.
    "explicit_units": ["pc", "pce", "pieces", "pack", "pk", "cases", "each", "set", "bag"],

    # Trailing raw numbers are present but appear ambiguous (variant vs qty), so do NOT treat
    # "TITLE ... 20" as pack qty without extra context words (e.g., "BALLOONS", "PACK", "PCS").
    "allow_trailing_number_as_qty": False,

    # No clear "10x Product" patterns observed in SupplierTitle sample.
    "leading_multiplier_check": False,

    # Shield size/dimension tokens from RSU parsing (observed in SupplierTitle)
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "lt", "m", "g", "kg", "inch", "in", "yards", "yds", "w"
    ],

    # Brand-like token typically appears at the start of SupplierTitle in this file.
    "brand_position": "start",

    # Sales signal column in this file
    "sales_column": "bought_in_past_month",

    # AmazonTitle frequently uses "N x 400ml/g" style; interpret RSU as N, not N*capacity
    "capacity_pattern_as_rsu": True,
}
# ---------------------------------
```

---

## TASK 4: CALIBRATION WARNINGS (traps found in sample)

Row 1: `'... GIRL 3'` should be treated as a **variant/label number**, not RSU=3  
Row 13: `'70X100CM'` should be RSU=1 (dimensions), not RSU=7000  
Row 21: `'... BALLOONS ... 20'` is **ambiguous**; likely 1 pack-of-20 balloons, not 20 packs (do not auto-RSU from trailing number alone)  
Row 24: `'105G PK6'` should be RSU=6 (pack size), not RSU=105 (105g is capacity/size)  
Row 37: `'... CANDLE NUMBER ... 6'` should be treated as a **numbered candle variant**, not RSU=6  
Row 39: `'5X60MM'` should be RSU=1 (dimensions), not RSU=300  
Row 40: `'5MM X 85MM'` should be RSU=1 (dimensions), not RSU=425  
Row 50: `'440ML PK8'` should be RSU=8 (pack size), not RSU=440 (440ml is capacity/size)  
Row 61: `'2INCH 100 YARDS'` should be RSU=1 (dimensions/length), not RSU=200  
Row 73: `'4 X 4M'` should be RSU=4 (4 rolls/units), not RSU=16 (do not multiply dimensions/length)  

Row 1: AmazonTitle appears unrelated to SupplierTitle (`badge` vs `smartphone`) — do not infer pack rules by comparing SupplierTitle ↔ AmazonTitle unless match quality is verified.

**EAN warning:** `EAN`/`EAN_OnPage` contain mixed numeric formatting; some `EAN_OnPage` entries appear as scientific notation when read naïvely. Treat EAN fields as **strings** and validate length (mostly 13 digits, but 11/12/14-digit anomalies exist).

