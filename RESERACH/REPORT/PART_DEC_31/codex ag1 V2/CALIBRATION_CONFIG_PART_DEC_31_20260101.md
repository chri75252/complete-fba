# Calibration Output (Pre-Main-Analysis)

Input analyzed (first 50 rows):

- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx` (sheet: `Sheet1`)

Detected relevant columns:

- `SupplierTitle`
- `AmazonTitle`
- Sales signal column: `bought_in_past_month` (numeric in first 50 rows)

## --- CALIBRATION CONFIGURATION ---

```python
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": [
        "pc", "pcs", "pce",
        "piece", "pieces",
        "pk", "pack", "case", "cases",
        "each",
    ],
    "allow_trailing_number_as_qty": True,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": [
        "cm", "mm", "ml", "ltr", "l", "m",
        "kg", "g", "oz",
        "inch", "in",
        "w",
    ],
    "brand_position": "start",
    "sales_column": "bought_in_past_month",
}
```

## Calibration Warnings (rows from first 50)

- Row 2: `EUROWRAP GIANT BIRTHDAY BADGE GIRL 3` → trailing `3` is likely a variant/age, not a pack quantity.
- Row 20: `PARTY CRAZY BALLOONS ASSORTED 20` → trailing `20` likely *is* a pack quantity; treat as qty only if not a dimension.
- Row 36: `UNIQUE CANDLE NUMBER W/DECOR 6` → trailing `6` likely a “number 6” product, not a pack quantity.
- Row 39: `DEKTON MASONRY DRILL BIT 5MM X 85MM` → `X` is a dimension separator (not a multiplier); shield `mm`/`cm` patterns.
- Row 6: `MINKY CURVE SCOURER 2PC` → quantity can be fused (`2PC`) with no space; ensure regex handles it.
- Row 31: `LYNWOOD MINI ROLLER SET 5PACK` → quantity can be fused (`5PACK`) with no space.
- Row 23: `AIRWICK ... 105G PK6` and Row 49: `... 440ML PK8` → pack size can be encoded as `PK6` / `PK8` (suffix).
- Row 8: `STATUS LED G9 2W ... EACH` → `2W` is wattage (not qty); `EACH` is a unit marker.

