# AGENTIC FBA CALIBRATION PROMPT (PRE-FLIGHT) v1.1

**Purpose:** Analyze a specific financial report CSV *before* the main analysis to detect the supplier's unique naming conventions, pack quantity formats, and data anomalies. This output will customize the main analysis prompt.

**Version:** 1.1 (Updated 2026-01-02)

**Input:** 
1. Path to CSV: `[USER_FILE_PATH]`
2. Read first 50 rows (or more if needed to detect patterns).

**Role:** You are a Data Pattern Specialist. Your ONLY job is to identify the schema rules for this specific supplier file. The main analysis will reference your output to avoid common parsing traps.

---

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
- "4 x 50" — Should RSU = 4 (if supplier sells 50 per pack)

**Rule:** When Amazon shows `N x [capacity]ml/g/l`, the RSU = N (the first number only).
The capacity value describes SIZE of each unit, NOT quantity to multiply.

Note any patterns where this interpretation might be ambiguous for this supplier.

---

## TASK 2: DETECT SALES SIGNAL
Identify which column contains the sales data: `sales_numeric`, `bought_in_past_month`, or `Sales`. Note if it contains text (e.g., "100+ bought") that needs parsing.

---

## TASK 3: DETECT BRAND PATTERNS
Analyze where brand names appear in supplier titles:

1. **At START:** "AMTECH LED TORCH", "PYREX DISH 20CM"
2. **In MIDDLE:** "LED TORCH AMTECH 9 LED", "OVAL DISH PYREX"
3. **At END:** "LED TORCH - AMTECH", "DISH 20CM PYREX"

Note the most common pattern for this supplier. The main analysis will use word-boundary matching (brand can appear anywhere), but knowing the typical position helps prioritize scanning.

Set `brand_position` to: `"start"`, `"middle"`, `"end"`, or `"mixed"`

---

## OUTPUT FORMAT (JSON-LIKE)
Provide the configuration block below. This is an **EXAMPLE** — adjust values based on what you detect for this specific supplier.

```python
# --- CALIBRATION CONFIGURATION ---
# NOTE: These are EXAMPLE values — adjust based on detected patterns for this supplier
SUPPLIER_NAMING_CONVENTION = {
    "explicit_units": ["pce", "pcs", "pk", "pack"],  # Add any others found for this supplier
    "allow_trailing_number_as_qty": True,  # TRUE if trailing numbers (like 'STICKS 200') are common
    "leading_multiplier_check": True,      # TRUE if '10x Product' is common at title start
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch"],  # Add supplier-specific
    "brand_position": "mixed",  # 'start', 'middle', 'end', or 'mixed'
    "sales_column": "sales_numeric",  # The detected column name
    "capacity_pattern_as_rsu": True  # TRUE if "3 x 400ml" means RSU=3, not 1200 (typical)
}
# ---------------------------------
```

**Note:** Different supplier websites may have different patterns. The main analysis will adapt based on these calibration settings.

---

## TASK 4: CALIBRATION WARNINGS
List any specific rows from the sample that might trap the generic analysis logic.

**Types of traps to identify:**

| Trap Type | Example Pattern | Wrong Interpretation | Correct |
|-----------|-----------------|----------------------|---------|
| Dimension trap | "9 x 9 inch" | RSU = 81 | RSU = 1 (dimensions) |
| Model number trap | "SOUDAL 750" | 750ml capacity | Model number |
| Capacity multipack | "3 x 400ml" | RSU = 1200 | RSU = 3 (bottles) |
| Quantity-inside trap | "STICKS 200" | 200 packs | 1 pack of 200 |

**Format each warning as:**
```
Row N: '[pattern]' should be [correct interpretation], not [wrong interpretation]
```

**Examples:**
- "Row 15: 'SUPERIOR FOIL 9X9IN' should be RSU=1 (9x9 is dimension), not RSU=81"
- "Row 42: 'SOUDAL 750' — 750 is likely a model number, not 750ml capacity"
- "Row 8: '3 x 400ml' should be RSU=3 (3 bottles), not RSU=1200"
