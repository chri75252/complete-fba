# Pre-flight Calibration (first 50 rows)

Source file (verified):  
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\part 4 jan.xlsx`

Sample notes:
- `SupplierURL` domain is consistently `www.efghousewares.co.uk` in the first 50 rows.
- `bought_in_past_month` is `int64` (no “100+ bought” text patterns observed in the first 50 rows).

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    # Observed supplier pack/unit indicators include: "PK6", "2PC", "5PACK", and "SET".
    # Note: many appear attached to the number (e.g., "PK6", "2PC", "5PACK"), not as separate tokens.
    "explicit_units": ["pc", "pcs", "pk", "pack", "set"],

    # Trailing numbers exist but are ambiguous in this sample (can be variant/age or product number).
    "allow_trailing_number_as_qty": False,

    # No leading "10x ..." multipliers observed in the first 50 rows.
    "leading_multiplier_check": False,

    # Dimensions/capacity appear in multiple formats: "300ML", "7 INCH", "10.5 INCH", "1.6L", "5MM X 85MM".
    "dimension_shield_keywords": ["cm", "mm", "ml", "m", "inch", "inches", "l", "ltr", "litre", "kg", "g", "oz"],

    # Supplier titles overwhelmingly start with an all-caps token (brand-like).
    "brand_position": "start",  # 'start' or 'mixed'

    "sales_column": "bought_in_past_month",

    # No "N x 400ml/g/l" patterns observed in AmazonTitle in the first 50 rows.
    "capacity_pattern_as_rsu": False,

    # Not observed in this sample, but keep enabled in the main prompt to avoid false RSU from feature multipliers.
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times", "power"],

    # Amazon titles contain '|' in this sample.
    "table_pipe_sanitization": True,
}
# ---------------------------------
```

## Calibration Warnings (sample traps)

- Row 1–5: `SupplierTitle` and `AmazonTitle` appear semantically unrelated (e.g., Row 1 paint vs TV). Cross-field pack inference is unreliable; prefer parsing pack only from each field independently.
- Row 27: `AIRWICK ... 105G PK6` — parse `PK6` as pack quantity 6 (attached pattern).
- Row 34: `... COLOURING SET 2PC` — parse `2PC` as quantity 2 (attached pattern).
- Row 36: `... ROLLER SET 5PACK` — parse `5PACK` as quantity 5 (attached pattern).
- Row 2 / Row 40: trailing numbers likely *not* pack counts (`... GIRL 3`, `... CANDLE NUMBER ... 6`).
- Row 24: trailing number *might* be pack count (`... BALLOONS ASSORTED 20`) but ambiguous without a noun/pack keyword rule.
- Row 44: `5MM X 85MM` — `X` is a dimension separator, not a multipack multiplier.
- Row 4 (AmazonTitle): `... 2250 PCS ...` likely indicates “pieces” in a model kit, not a multipack RSU; avoid treating `PCS` on Amazon titles as RSU.
- Row 27 / Row 39 (AmazonTitle): titles include `|` characters (sanitize in table output).

