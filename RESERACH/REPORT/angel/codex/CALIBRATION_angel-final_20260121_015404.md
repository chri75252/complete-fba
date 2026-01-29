# Angel Wholesale – Pre-flight Calibration

- Report: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\angel\angel-final.xlsx`
- Generated: `2026-01-21T01:54:04`
- Rows analyzed: 50

## Detected Columns
- Columns: EAN, EAN_OnPage, ASIN, SupplierTitle, AmazonTitle, SupplierURL, AmazonURL, bought_in_past_month, fba_seller_count, fbm_seller_count, total_offer_count, SupplierPrice_incVAT, SupplierPrice_exVAT, SellingPrice_incVAT, ReferralFee, FBAFee, PrepHouseFee, OutputVAT, InputVAT, NetProceeds, HMRC, NetProfit, ROI, Breakeven, ProfitMargin, eanmach
- Sales column: `bought_in_past_month` (dtype: `int64`)

## Pack/Quantity Patterns (SupplierTitle)
- Explicit unit tokens observed: `['pack', 'set']`
- Leading multipliers like `10x ...`: `False`
- Trailing bare number-as-qty common: `False`

## Dimension Patterns
- Observed formats: `(22cm)`, `30cm x 50mm`, `19x25cm`, `38mm x 20m`

## Brand Signal
- Brand-like ALL_CAPS token at start (SupplierTitle): 0%
- Brand-like ALL_CAPS token at start (AmazonTitle): 32%

## Title Similarity Health Check
- Similarity (token_set) median: 0.201 | 90th pct: 0.324 | max: 0.867

## Calibration Config

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'set'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ["cm", "mm", "m", "ml", "ltr", "l", "kg", "g", "oz", "inch", "in"],
    "brand_position": "mixed",
    "brand_in_supplier_usually_present": False,
    "brand_in_amazon_usually_present": False,
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": True,
    "strong_similarity_threshold": 0.55,
    "strong_shared_tokens_threshold": 2,
    "very_strong_similarity_threshold": 0.7,
    "very_strong_shared_tokens_threshold": 3,
    "gate_mode": "A_strict",
    "sales_column": 'bought_in_past_month',
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True
}
# ---------------------------------
```

## Calibration Warnings
- Row 1: SupplierTitle contains explicit pack quantity (e.g. 'Gold Table Number Cards (12 Pack)'); use this as RSU when matching.
- Row 4: SupplierTitle has parenthesized dimensions (e.g. 'Frosted Pine Cone & Greenery Pick (22cm)'); shield dimension units from quantity parsing.
- Row 5: SupplierTitle has parenthesized dimensions (e.g. 'Assorted Puppy with Love Heart Plush (26cm)'); shield dimension units from quantity parsing.
- Row 12: SupplierTitle has parenthesized dimensions (e.g. 'Hortus Vienna Matt Pink Ceramic Pot (15cm)'); shield dimension units from quantity parsing.
- Row 16: SupplierTitle has parenthesized dimensions (e.g. 'Pack of 4 Silver Disco Bauble (10cm)'); shield dimension units from quantity parsing.
- Row 16: SupplierTitle contains explicit pack quantity (e.g. 'Pack of 4 Silver Disco Bauble (10cm)'); use this as RSU when matching.
- Row 35: SupplierTitle has parenthesized dimensions (e.g. 'Keeleco Teddy (20cm)'); shield dimension units from quantity parsing.
- Row 42: SupplierTitle looks like dimensions using 'x' (e.g. 'Black Hand Tie Bag (19x25cm)'); avoid treating 'Nx' as multipack.
- Row 45: SupplierTitle has parenthesized dimensions (e.g. 'Giant Red Poinsettia Head (50cm)'); shield dimension units from quantity parsing.
- Row 39: AmazonTitle contains '|' (e.g. 'Belaco Heater 2000W Turbo Convector Electric Heater with Fan Heater 3-speed Setting & 24Hr Timer | Energy Saving Portable Heater| Fast Heating Room Heaters for Home, Electric radiator â€“ Black'); sanitize table pipes in outputs.
- Row 2: EAN_OnPage is numeric/float (e.g. 4820184121324.0); treat EAN fields as strings to avoid scientific-notation/precision loss.
- SupplierTitle vs AmazonTitle similarity is very low across most of the first 50 rows; linking/matching may be incorrect, so calibrations based on title overlap should be treated cautiously.

## Concrete Examples
- Row 1 (SupplierTitle pack): Gold Table Number Cards (12 Pack)
- Row 42 (SupplierTitle dimensions): Black Hand Tie Bag (19x25cm)
- Row 39 (AmazonTitle pipe): Belaco Heater 2000W Turbo Convector Electric Heater with Fan Heater 3-speed Setting & 24Hr Timer | Energy Saving Portable Heater| Fast Heating Room Heaters for Home, Electric radiator â€“ Black
