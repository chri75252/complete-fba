# AGENTIC FBA CALIBRATION (PRE-FLIGHT)

## Input verified
- Report: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx
- Sheet: Sheet1
- Rows analyzed: first 50 data rows
- Supplier domain observed (from `SupplierURL`): ('www.efghousewares.co.uk', 50)

## Pack quantity patterns (SupplierTitle)
- Explicit unit tokens found: [('pc', 4), ('pieces', 2), ('cases', 1), ('pcs', 1), ('pk', 1), ('pack', 1)]
- Examples (EXCEL_ROW, match):
  - EXCEL_ROW 4: '100 CASES' in 'LUXURY CUPCAKE 100 CASES'
  - EXCEL_ROW 9: '12 PIECES' in 'DLUX PEGS WITH SOFT RUBBER GRIP PLASTIC LARGE 12 PIECES'
  - EXCEL_ROW 10: '2PC' in 'MINKY CURVE SCOURER 2PC'
  - EXCEL_ROW 14: '10PC' in 'ARTIST PAINT BRUSHES 10PC'
  - EXCEL_ROW 17: '8PC' in 'FESTIVE MAGIC BELLS 8PC ASSORTED'
  - EXCEL_ROW 22: '8PCS' in 'DEKTON RIGHT ANGLE BRACKETS 8PCS'
  - EXCEL_ROW 37: '4PK' in 'CHRISTMAS TAG BAUBLE WOODEN MINI 4PK'
  - EXCEL_ROW 38: '2PC' in 'CHRISTMAS VELVET COLOURING SET 2PC'
- Leading multipliers like '6x ...': not observed in first 50 rows
- Trailing raw numbers exist but are rare/ambiguous; examples:
  - EXCEL_ROW 3: 'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3' (trailing '3')
  - EXCEL_ROW 27: 'PARTY CRAZY BALLOONS ASSORTED 20' (trailing '20')
  - EXCEL_ROW 45: 'UNIQUE CANDLE NUMBER W/DECOR 6' (trailing '6')

## Similarity diagnostic (SupplierTitle vs AmazonTitle)
- Top matches (ratio, EXCEL_ROW):
  - 0.43 EXCEL_ROW 50: 'RED CROWN EDT100ML POUR FEMME EACH' || 'Versace Eros Pour Femme Eau De Parfum For Women, 100 ml'
  - 0.42 EXCEL_ROW 49: 'REVITALISE ELIXIR EDT 85ML POUR FEMME EACH' || 'Versace Eros Pour Femme Eau De Parfum For Women, 100 ml'
  - 0.34 EXCEL_ROW 5: 'METAL GOLF SET' || 'SKYMAX 2025 PRECISE M5 MENS COMPLETE GOLF SET - RIGHT HAND'
  - 0.34 EXCEL_ROW 8: 'WORLD OF PETS TOY BALL LAUNCHER 62CM ASSORTED' || 'PetSafe Automatic Ball Launcher Dog Toy â€“ Tennis Ball Throwing Machine for Dog'
- Lowest matches (ratio, EXCEL_ROW):
  - 0.06 EXCEL_ROW 34: 'CAPPUCCINO CUP' || 'Tevlaphee Steering Wheel Lock with Alarm, 120dB, Wheel Spoke Width â‰¤2.75in, Ba'
  - 0.08 EXCEL_ROW 11: 'STARWASH CLOTHES LINE 30M' || 'Mould King V8 Engine Building Blocks Set, 2250 PCS Combustion Engine Model Kit T'
  - 0.09 EXCEL_ROW 25: 'PANASONIC UPRIGHT   SDB113' || 'ElecKeys Cordless Vacuum Cleaner,65 Mins 580W 48KPa 1.8L Vacuum Cleaners for Hom'
  - 0.09 EXCEL_ROW 4: 'LUXURY CUPCAKE 100 CASES' || 'Oversize Turbo Dryer Blower,Car Accessories,Max Instantaneous Thrust 1.60KG,4 Sp'

## Paste-ready configuration

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pc', 'pieces', 'cases', 'pcs', 'pk', 'pack'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in", "m"],
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": True,
    "brand_format_patterns": ["ALL_CAPS_AT_START", "IN_BRACKETS", "AFTER_HYPHEN"],
    "brand_sparse_supplier_mode": False,
    "strong_similarity_threshold": 0.3,
    "strong_shared_tokens_threshold": 3,
    "very_strong_similarity_threshold": 0.4,
    "very_strong_shared_tokens_threshold": 4,
    "gate_mode": "A_strict",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": False,
    "spec_x_shield_keywords": ['magnification', 'zoom', 'microscope', 'scope', 'times', 'optical'],
    "table_pipe_sanitization": True
}
# ---------------------------------
```

## Calibration warnings
- EXCEL_ROW 2: starts with numeric code '151' (likely model/SKU, not brand/pack).
- EXCEL_ROW 3: trailing number '3' in 'EUROWRAP GIANT BIRTHDAY BADGE GIRL 3' looks like variant/age/candle-number; do not treat trailing numbers as pack qty.
- EXCEL_ROW 27: trailing number '20' in 'PARTY CRAZY BALLOONS ASSORTED 20' looks like variant/age/candle-number; do not treat trailing numbers as pack qty.
- EXCEL_ROW 45: trailing number '6' in 'UNIQUE CANDLE NUMBER W/DECOR 6' looks like variant/age/candle-number; do not treat trailing numbers as pack qty.
- EXCEL_ROW 40: AmazonTitle contains '|' pipe characters; sanitize to '/' in output tables.
- SupplierTitle vs AmazonTitle similarity is often very low in the first 50 rows (many obvious mismatches); use strict gating before trusting RSU/pack inference from AmazonTitle.
