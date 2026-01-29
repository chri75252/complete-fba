# V430 Pre-Flight Calibration (first 50 rows)

**Input file (verified):** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx`  
- size_bytes: `914396`  
- last_write_time_local: `2026-01-08 01:11:27`

**Sheet:** `Sheet1`

**Columns (25):**
`EAN`, `EAN_OnPage`, `ASIN`, `SupplierTitle`, `AmazonTitle`, `SupplierURL`, `AmazonURL`, `bought_in_past_month`, `fba_seller_count`, `fbm_seller_count`, `total_offer_count`, `SupplierPrice_incVAT`, `SupplierPrice_exVAT`, `SellingPrice_incVAT`, `ReferralFee`, `FBAFee`, `PrepHouseFee`, `OutputVAT`, `InputVAT`, `NetProceeds`, `HMRC`, `NetProfit`, `ROI ( % ) `, `Breakeven`, `ProfitMargin`

## Key Observations (file-grounded)

- Supplier URLs in the sample are `efghousewares.co.uk` (not `poundwholesale.co.uk`).
- Supplier titles are **100% ALL CAPS** across the first 50 rows.
- Multiple rows show **severe SupplierTitle ↔ AmazonTitle mismatch** (examples: rows 1–3).
- Sales signal column is `bought_in_past_month` (numeric in first 50 rows).
- Amazon titles can contain `|` (row 39).

## Pack / Quantity Pattern Findings

### SupplierTitle
- **Explicit units found:** `CASES`, `BAG`, `CAPSULE`, and compact pack markers like `PK6`.
- **Trailing raw numbers at end (ambiguous):** seen, but not reliably a pack count (e.g., “GIRL 3”, “... NUMBER ... 6”).
- **Leading multipliers (e.g., “10x ...”):** not observed in first 50 rows.
- **Dimensions/capacity formats:** mostly *no-space* uppercase units (e.g., `300ML`, `40CM`, `1.6L`, `105G`), with occasional spaced units (e.g., `7 INCH`).

### AmazonTitle
- **Capacity multipack (“N x 400ml/g”) patterns:** not observed in the first 50 rows.
- **Non-pack spec “Nx” patterns (“2x zoom/magnification”)**: not observed in the first 50 rows.

## --- CALIBRATION CONFIGURATION ---

```python
SUPPLIER_NAMING_CONVENTION = {
    # Explicit unit markers observed in SupplierTitle (first 50 rows)
    "explicit_units": ["pk", "cases", "bag", "capsule"],

    # Trailing numbers occur but are ambiguous in this supplier file sample
    "allow_trailing_number_as_qty": False,

    # No clear leading multipliers like "10x ..." seen in sample
    "leading_multiplier_check": False,

    # Supplier dimensions/capacities observed: 300ML, 40CM, 1.6L, 105G, 7 INCH, 10.5 INCH
    "dimension_shield_keywords": ["cm", "mm", "ml", "l", "ltr", "kg", "g", "oz", "inch", "in"],

    # SupplierTitle is ALL CAPS; brand-like tokens often appear at the start but are not reliably separable from product type
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": True,
    "brand_format_patterns": ["ALL_CAPS_AT_START"],

    # Given the observed SupplierTitle↔AmazonTitle mismatch in the sample, prefer strict similarity gating
    "brand_sparse_supplier_mode": False,

    # Similarity thresholds: set conservatively strict (sample overlap is near-zero for many rows)
    "strong_similarity_threshold": 0.33,
    "strong_shared_tokens_threshold": 3,
    "very_strong_similarity_threshold": 0.45,
    "very_strong_shared_tokens_threshold": 4,
    "gate_mode": "A_strict",

    # Sales column in this report
    "sales_column": "bought_in_past_month",

    # Even though not observed in first 50 rows, keep this rule enabled when it appears
    # ("3 x 400ml" => RSU=3)
    "capacity_pattern_as_rsu": True,

    # Shield keywords for non-pack "Nx" usage (feature/spec multipliers)
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],

    # AmazonTitle contains "|" in the sample (row 39)
    "table_pipe_sanitization": True
}
```

## Calibration Warnings (rows from the first-50 sample)

- Row 1: Supplier looks like paint (`151 WHITE NO-DRIP GLOSS PAINT 300ML`) but Amazon is an LG TV.
- Row 2: Supplier is a birthday badge (“GIRL 3”) but Amazon is a Motorola smartphone.
- Row 3: Supplier is cupcake cases (“100 CASES”) but Amazon is a turbo dryer blower.
- Row 2: Trailing `3` is likely an age/variant, not a pack quantity.
- Row 26: Trailing `20` in `... BALLOONS ASSORTED 20` might be quantity (pack), but could still be a variant; treat cautiously.
- Row 44: Trailing `6` in `... NUMBER ... 6` is likely a variant number (candle number), not pack quantity.
- Row 29: `PAPER EASTER 10 PLATES 7 INCH` contains both a count (`10`) and a dimension (`7 INCH`) — do not treat the dimension as RSU.
- Row 38: `PLATE 10.5 INCH...` contains a decimal dimension (`10.5`) — do not treat as RSU.
- Row 39: `... 105G PK6` uses compact `PK6` pack notation; parse as pack-of-6.
- Row 39: AmazonTitle contains `|`; sanitize if exporting to pipe-delimited tables.
