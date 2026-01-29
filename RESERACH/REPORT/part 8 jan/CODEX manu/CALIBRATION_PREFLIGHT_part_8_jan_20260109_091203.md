Calibration preflight for: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx
Generated: 2026-01-09T09:12:03

Detected supplier host (from SupplierURL sample): www.efghousewares.co.uk

## Configuration block
```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": [
        "pk",
        "cases",
        "plates"
    ],
    "allow_trailing_number_as_qty": false,
    "leading_multiplier_check": false,
    "dimension_shield_keywords": [
        "cm",
        "mm",
        "ml",
        "ltr",
        "l",
        "kg",
        "g",
        "oz",
        "inch",
        "in",
        "m",
        "ft"
    ],
    "brand_position": "start",
    "brand_in_supplier_usually_present": true,
    "brand_in_amazon_usually_present": true,
    "brand_format_patterns": [
        "ALL_CAPS_AT_START",
        "TITLECASE_AT_START"
    ],
    "brand_sparse_supplier_mode": false,
    "strong_similarity_threshold": 0.35,
    "strong_shared_tokens_threshold": 4,
    "very_strong_similarity_threshold": 0.45,
    "very_strong_shared_tokens_threshold": 6,
    "gate_mode": "A_strict",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": true,
    "spec_x_shield_keywords": [
        "magnification",
        "zoom",
        "microscope",
        "scope",
        "times"
    ],
    "table_pipe_sanitization": true
}
# ---------------------------------
```

## Warnings
- Sample shows very low SupplierTitle↔AmazonTitle overlap (likely widespread mismatches); use strict gating.
- Supplier pack counts appear as 'PK6' and as 'N <unit>' (e.g., '100 CASES', '10 PLATES').
- Trailing numbers are rare in the first 50 rows, but exist (e.g., '... ASSORTED 20') and may be pack size.
- At least one Amazon title contains a pipe '|' which can break markdown tables; sanitize to '/'.

## Examples (from first 50 rows)
- supplier_pack_examples:
  - LUXURY CUPCAKE 100 CASES
  - PAPER EASTER 10 PLATES 7 INCH
  - AIRWICK CANDLE VANILLA & BROWN SUGAR 105G PK6
- mismatch_examples:
  - 151 WHITE NO-DRIP GLOSS PAINT 300ML  ↔  LG OLED48C45LA 48-Inch OLED Evo 4K UHD Smart TV ...
  - EUROWRAP GIANT BIRTHDAY BADGE GIRL 3  ↔  Motorola edge 60 fusion ...
