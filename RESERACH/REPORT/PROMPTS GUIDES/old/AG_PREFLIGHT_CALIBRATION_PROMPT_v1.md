# AGENTIC FBA CALIBRATION PROMPT (PRE-FLIGHT)

**Purpose:** Analyze a specific financial report CSV *before* the main analysis to detect the supplier's unique naming conventions, pack quantity formats, and data anomalies. This output will customize the main analysis script.

**Input:** 
1. Path to CSV: `[USER_FILE_PATH]`
2. Read first 50 rows.

**Role:** You are a Data Pattern Specialist. Your ONLY job is to identify the schema rules for this specific supplier file.

## TASK 1: DETECT PACK QUANTITY PATTERNS
Analyze `SupplierTitle` vs `AmazonTitle` for the following patterns:
1. **Explicit Units:** Does the supplier use `pcs`, `pce`, `pk`, `pack`, `unit`? (e.g., "50 PCS")
2. **Implicit/Trailing Numbers:** Does the supplier put the quantity as a raw number at the end of the string? (e.g., "TALA COCKTAIL STICKS 200")
3. **Leading Multipliers:** Does the supplier use `10x ...`, `6 x ...` at the start?
4. **Dimension vs Quantity:** How does this supplier format dimensions? (e.g., `20cm` vs `20 cm`, `500ml` vs `500 ML`)

## TASK 2: DETECT SALES SIGNAL
Identify which column contains the sales data: `sales_numeric`, `bought_in_past_month`, or `Sales`. Note if it contains text (e.g., "100+ bought") that needs parsing.

## TASK 3: DETECT BRAND PATTERNS
Does the supplier ALWAYS put the brand at the start? (e.g., "AMTECH ...") or is it mixed?

## OUTPUT FORMAT (JSON-LIKE)
Provide the configuration block below. The Agent will paste this into the main Python script.

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack"], # Add any others found
    "allow_trailing_number_as_qty": True, # Set TRUE if trailing numbers (like 'STICKS 200') are common
    "leading_multiplier_check": True,     # Set TRUE if '10x Product' is common
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"],
    "brand_position": "start", # 'start' or 'mixed'
    "sales_column": "sales_numeric" # The detected column name
}
# ---------------------------------
```

## TASK 4: CALIBRATION WARNINGS
List any specific rows from the sample that might trap the generic logic (e.g., "Row 5: '200' looks like quantity but is part of model number").
