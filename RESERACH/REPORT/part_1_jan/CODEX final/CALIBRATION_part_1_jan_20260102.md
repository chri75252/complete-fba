# Calibration Addendum (Data Patterns) — part_1_jan.xlsx

**Report analyzed (verified):**  
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx`

**Sheet:** `Sheet1`  
**Shape:** `2402 rows × 25 columns`  
**Primary supplier (from `SupplierURL` in first 50 rows):** `www.efghousewares.co.uk`

## Detected schema notes (important for parsing)

- `EAN` and `EAN_OnPage` are stored as **floats** in Excel (risk: scientific notation / loss of formatting). Treat as **strings** when reading.
- `bought_in_past_month` is **numeric** (int) in this file and is the best “sales signal” column.
- `fba_seller_count` / `fbm_seller_count` are frequently the literal string `Available (see Keepa data)` and are **not reliable numeric counts**.

## TASK 1: Detect pack quantity patterns (SupplierTitle vs AmazonTitle)

### 1) Explicit units (supplier)
Common explicit unit tokens found across the file:
- `set`, `pack`, `pieces`, `pcs`, `pce`, `pk`, `case`, `cases`, `pair`, `pairs`

Compound “number+unit” tokens used by this supplier (no space):
- `3PC`, `12pk`, `6PK` (expect mixed casing)

Common phrases:
- `PACK OF <N>`
- `SET OF <N>`

### 2) Implicit/trailing numbers (supplier)
This supplier **does** sometimes end titles with a raw number that represents pack quantity (example: cocktail sticks).

However, trailing numbers are also frequently **model/part codes** (often large values) and sometimes appear as **date-like fragments** (slashes/dots elsewhere in the title). Treat trailing numbers as **high risk** unless corroborated by context (e.g., “STICKS 200”, “PACK OF 50”).

### 3) Leading multipliers (supplier)
No meaningful `^\d+\s*x` style leading multipliers detected in this file’s supplier titles (when `x` appears, it is usually a **dimension separator**).

### 4) Dimension vs quantity (supplier formatting)
This supplier frequently uses **unspaced** dimension/capacity formatting:
- `70X100CM`, `5X60MM`, `280ML`, `40CM`
- `MMxM` style also appears (e.g., `5MX500M` in titles where “x” is a separator, not a multiplier)

Parsing implication:
- Prefer treating `<number>x<number><unit>` as **dimensions** (RSU should remain 1).
- Treat `<number><unit>` (e.g., `280ML`, `40CM`) as size/dimension, not pack quantity.

## TASK 1B: Capacity multipack patterns (AmazonTitle)

Across the full file, Amazon titles include `N x <capacity><unit>` multipacks (examples include `10 x 90g`, `6 X 70 ML`, `12x 280ml`, `2 x 1L`, `5 x 60L`).

**Calibration rule for this dataset:** when Amazon shows `N x [capacity]ml/g/l/kg/oz`, interpret **RSU = N** (the first number). The capacity describes size **per unit**, not a quantity to multiply.

Ambiguity to guard:
- Amazon titles sometimes include both total and per-unit capacity, e.g. `420 ML (6 X 70 ML)`; use the `N x ...` part to set RSU, not the total.

## TASK 2: Detect sales signal

- Detected sales column: `bought_in_past_month` (numeric, already parsed as integers in this file)

## TASK 3: Detect brand patterns (supplier)

- Supplier titles are predominantly uppercase and most often start with a brand token (heuristic ratio in first 50 rows ≈ 0.98).
- `brand_position`: `"start"`

## OUTPUT FORMAT (JSON-LIKE)

```python
# --- CALIBRATION CONFIGURATION (part_1_jan.xlsx / www.efghousewares.co.uk) ---
SUPPLIER_NAMING_CONVENTION = {
    # Explicit unit tokens seen in SupplierTitle across this file
    "explicit_units": ["set", "pack", "pieces", "pcs", "pce", "pk", "case", "cases", "pair", "pairs"],

    # True because patterns like "... STICKS 200" exist, but treat as HIGH RISK unless context confirms
    # (many trailing numbers are model/part codes, e.g. very large integers).
    "allow_trailing_number_as_qty": True,

    # No leading “10x Product” style detected in supplier titles (x is usually dimensional here)
    "leading_multiplier_check": False,

    # Units frequently used in unspaced dimension/capacity strings (e.g., 70X100CM, 280ML, 5X60MM, 5MX500M)
    "dimension_shield_keywords": ["cm", "mm", "ml", "m", "ltr", "l", "inch", "in", "ft", "kg", "g", "oz"],

    # Brand is typically at the start of SupplierTitle
    "brand_position": "start",

    # Numeric sales signal column for this file
    "sales_column": "bought_in_past_month",

    # Amazon “N x 400ml/g/...” patterns appear; treat RSU as N (not N*capacity)
    "capacity_pattern_as_rsu": True,
}
# ---------------------------------------------------------------------------
```

## TASK 4: Calibration warnings (row-level traps)

Format: `Row N: '[pattern]' should be [correct interpretation], not [wrong interpretation]`

- Row 1: `'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3'` — `3` is a variant/age marker, not a pack quantity.
- Row 1: `'EUROWRAP...` vs Amazon `'Motorola edge 60 fusion...'` — treat as a **linking/matching anomaly**; do not infer pack rules by comparing these two titles.
- Row 11: `'EASY STORAGE VACUUM BAG 70X100CM'` should be RSU=1 (70×100 is dimension), not RSU=7000.
- Row 19: `'PARTY CRAZY BALLOONS ASSORTED 20'` should be RSU=1 pack containing 20, not RSU=20 packs.
- Row 35: `'UNIQUE CANDLE NUMBER W/DECOR 6'` — `6` is the candle number (variant), not quantity.
- Row 37: `'SECURPAK POZI COUNTERSUNK SCREWS ZP 5X60MM'` should be RSU=1 (5×60mm is dimension), not RSU=300.

Extended-sample (needed to detect broader patterns beyond first 50 rows):
- Row 517 (AmazonTitle): `'420 ML (6 X 70 ML)'` should be RSU=6 (6 units), not RSU=420 or RSU=6*70.
- Row 551 (AmazonTitle): `'12x 280ml'` should be RSU=12 (12 units), not RSU=3360.
- Row 1512: `'QUEST TURBO BLENDER 2 IN 1 32129'` — `32129` is a model/part code, not a pack quantity.
- Row 2046: `'TALA COCKTAIL STICKS 200'` should be RSU=1 pack of 200, not RSU=200 packs.

