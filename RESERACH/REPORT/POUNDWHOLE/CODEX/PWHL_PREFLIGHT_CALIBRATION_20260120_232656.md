# PWHL Preflight Calibration (First 50 Rows)
**Generated:** 2026-01-20
**Input File:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\POUNDHWHOLE\PWHL_FINAL.xlsx
**Sheet:** Sheet1

## Detected Schema
- Columns: EAN, EAN_OnPage, ASIN, SupplierTitle, AmazonTitle, SupplierURL, AmazonURL, bought_in_past_month, fba_seller_count, fbm_seller_count, total_offer_count, SupplierPrice_incVAT, SupplierPrice_exVAT, SellingPrice_incVAT, ReferralFee, FBAFee, PrepHouseFee, OutputVAT, InputVAT, NetProceeds, HMRC, NetProfit, ROI, Breakeven, ProfitMargin
- Sales column detected: `bought_in_past_month`

## Quick Pattern Summary
- Explicit unit keywords found (titles): pack, pc, pcs, set
- Trailing raw quantity number at end (non-measurement) seen: supplier=0, amazon=0
- Leading multiplier 'N x …' at start seen: supplier=0, amazon=0
- Quantity-inside multipack 'N x M' examples in AmazonTitle: 3
- Capacity multipack 'N x 400ml/g/l' examples in AmazonTitle: 0
- Amazon contains supplier first-token (brand-like) rate: 0% (0/50)

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ['pack', 'pc', 'pcs', 'set'],
    "allow_trailing_number_as_qty": False,
    "leading_multiplier_check": False,
    "dimension_shield_keywords": ['cm', 'mm', 'ml', 'ltr', 'litre', 'liter', 'kg', 'g', 'oz', 'inch', 'in', 'w', 'wh', 'mah', 'ghz'],
    "brand_position": "start",
    "brand_in_supplier_usually_present": True,
    "brand_in_amazon_usually_present": True,
    "brand_format_patterns": ['MIXED_CASE_AT_START', 'TITLE_CASE', 'CAPACITY_SUFFIX'],
    "brand_sparse_supplier_mode": False,
    "strong_similarity_threshold": 0.55,
    "strong_shared_tokens_threshold": 4,
    "very_strong_similarity_threshold": 0.7,
    "very_strong_shared_tokens_threshold": 6,
    "gate_mode": "A_strict",
    "sales_column": "bought_in_past_month",
    "capacity_pattern_as_rsu": True,
    "spec_x_shield_keywords": ['magnification', 'zoom', 'microscope', 'scope', 'times', 'ghz', 'w', 'mah'],
    "table_pipe_sanitization": True
}
# ---------------------------------
```

## Calibration Warnings
- Row 1: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Car Pride Interior Clean & Shine 300ml' vs 'Hoover HF1 Plus Cordless Stick Vacuum Cleaner with Turbo Suction Mode, Up to 45 …'
- Row 4: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Auto Extreme Professional Petrol-Resistant Lacquer Clear Spray 400ml' vs 'Ozeino Wireless Gaming Headset, Compatible with PC Ps5 Ps4 Boasts 2.4GHz Lossles…'
- Row 6: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Car Pride Interior Clean & Shine 300ml' vs 'Hoover HF1 Plus Cordless Stick Vacuum Cleaner with Turbo Suction Mode, Up to 45 …'
- Row 9: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Auto Extreme Professional Petrol-Resistant Lacquer Clear Spray 400ml' vs 'Ozeino Wireless Gaming Headset, Compatible with PC Ps5 Ps4 Boasts 2.4GHz Lossles…'
- Row 11: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Car Pride Interior Clean & Shine 300ml' vs 'Hoover HF1 Plus Cordless Stick Vacuum Cleaner with Turbo Suction Mode, Up to 45 …'
- Row 14: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Auto Extreme Professional Petrol-Resistant Lacquer Clear Spray 400ml' vs 'Ozeino Wireless Gaming Headset, Compatible with PC Ps5 Ps4 Boasts 2.4GHz Lossles…'
- Row 16: SupplierTitle/AmazonTitle look unrelated (sim≈0.19, shared_tokens=0). Example: 'Car Pride Interior Clean & Shine 300ml' vs 'Hoover HF1 Plus Cordless Stick Vacuum Cleaner with Turbo Suction Mode, Up to 45 …'
- Row 17: SupplierTitle/AmazonTitle look unrelated (sim≈0.17, shared_tokens=0). Example: '151 White Furniture Touch Up Pen 7ml CDU' vs 'LG OLED48C45LA 48-Inch OLED Evo 4K UHD Smart TV, (Î±9 AI Processor Gen7, Dolby A…'
- Row 33: Amazon shows quantity-inside multipack pattern '7 x 50' (e.g., '(7 x 50, Total 350)'); interpret as multipack/total-items, not dimensions.