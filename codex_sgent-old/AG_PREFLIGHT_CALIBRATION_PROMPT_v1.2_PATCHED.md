# AGENTIC FBA CALIBRATION PROMPT (PRE-FLIGHT)

**Purpose:** Analyze a specific financial report (CSV or XLSX) *before* the main analysis to detect the supplier's unique naming conventions, pack quantity formats, and data anomalies. This output will customize the main analysis prompt.

**Input:** 
1. Path to file (CSV or XLSX): `[USER_FILE_PATH]`
2. Read first 50 rows.

**Role:** You are a Data Pattern Specialist. Your ONLY job is to identify the schema rules for this specific supplier file.

## TASK 1: DETECT PACK QUANTITY PATTERNS
Analyze `SupplierTitle` vs `AmazonTitle` for the following patterns:
1. **Explicit Units:** Does the supplier use `pcs`, `pce`, `pk`, `pack`, `unit`? (e.g., "50 PCS")
2. **Implicit/Trailing Numbers:** Does the supplier put the quantity as a raw number at the end of the string? (e.g., "TALA COCKTAIL STICKS 200")
3. **Leading Multipliers:** Does the supplier use `10x ...`, `6 x ...` at the start?
4. **Dimension vs Quantity:** How does this supplier format dimensions? (e.g., `20cm` vs `20 cm`, `500ml` vs `500 ML`)

## TASK 1B: DETECT CAPACITY MULTIPACK PATTERNS (NEW)
Analyze Amazon titles for patterns like:
- "3 x 400ml" — Should RSU = 3 (three 400ml bottles), NOT RSU = 1200
- "6 x 33ml" — Should RSU = 6 (six 33ml units), NOT RSU = 198

**Rule:** When Amazon shows `N x [capacity]ml/g/l`, the RSU = N (the first number only).
The capacity value describes SIZE of each unit, NOT quantity to multiply.

## TASK 1C: DETECT NON-PACK "Nx" SPEC / FEATURE MULTIPLIERS (NEW)
Some titles contain patterns like "2x" or "2000x" that are NOT bundle counts. Identify any examples where:
- "2x Magnification" / "3x Zoom" appear (feature, not pack)
- "Nx" appears near feature/spec words and should NOT trigger RSU

**Rule:** Only treat "N x" as pack/multipack when it clearly refers to units/packaging (e.g., "Pack of N", "Set of N", "N x 400ml", "(4 x 50)").

## TASK 1D: DETECT "PACKS OF" + EXPLICIT "TOTAL" COUNT PHRASES (NEW)
Identify Amazon title patterns like:
- "6 Packs of 40 ... 240 Bags Total"
- "12 packs of 10 ... 120 total"

**Rule:**
- If the title contains **both** `X packs of Y` (or equivalent) **and** an explicit `Z [items] total`, treat the Amazon total count as **Z**.
- Otherwise, for count-based items (bags/liners/sticks/etc.), Amazon total count = `X × Y`.
- Do **not** apply this to capacity/weight patterns like `3 x 500ml` (Task 1B rule still applies: RSU = 3).

## TASK 2: DETECT SALES SIGNAL
Identify which column contains the sales data: `sales_numeric`, `bought_in_past_month`, or `Sales`. Note if it contains text (e.g., "100+ bought") that needs parsing.

## TASK 3: DETECT BRAND PATTERNS
Does the supplier ALWAYS put the brand at the start? (e.g., "AMTECH ...") or is it mixed?

## OUTPUT FORMAT (JSON-LIKE)
Provide the configuration block below. The Agent will paste this into the main analysis prompt/config.

```python
# --- CALIBRATION CONFIGURATION ---
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack"], # Add any others found
    "allow_trailing_number_as_qty": True, # Set TRUE if trailing numbers (like 'STICKS 200') are common
    "leading_multiplier_check": True,     # Set TRUE if '10x Product' is common
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"],
    "brand_position": "start", # 'start' or 'mixed'
    "sales_column": "sales_numeric", # The detected column name
    "capacity_pattern_as_rsu": True, # TRUE if "3 x 400ml" means RSU=3, not 1200
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True # If titles contain "|", replace with "/" in output tables
}
# ---------------------------------
```

## TASK 4: CALIBRATION WARNINGS
List any specific rows from the sample that might trap the generic logic (e.g., "Row 5: '200' looks like quantity but is part of model number").
