# AG1 Surgical Prompt Fix Plan (Validated)

**Status:** FINAL VALIDATED
**Reference Report:** `OPUS AG1\PHASEA_MANUAL_REPORT_20251231.md`
**Validation:** Confirmed via `AG1_REPORT_PERFORMANCE_AUDIT` (Comparison with CODEX/webapp reports).

## 1. The Core Problem
The LLM's Python script (embedded in the prompt) fails to normalize supplier-specific quantity shorthands (e.g., "20PCE", "50 PCS") and lacks a "benefit of the doubt" shield when numerical quantities match but text differs. This causes **False Positive RSU (Required Supplier Unit) calculations**, leading to:
*   `RSU > 1` (e.g., RSU=20)
*   `Adjusted Profit < 0` (due to multiplying cost by 20)
*   **Item Filtered Out** (despite being profitable)

## 2. Surgical Fixes (Python Code Blocks)
Replace the existing functions in the Prompt's Python block with these **Exact Replacements**.

### Fix A: `extract_quantity` (Add Shorthand Regex)
**Goal:** Capture "20PCE", "50 PCS", "10PK" correctly.

```python
def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    # IMPROVED: Added supplier shorthand patterns (PCE, PCS, PK)
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',           # New: 10pk
        r'(\d+)\s*pcs\b',            # New: 50pcs
        r'(\d+)\s*pce\b',            # New: 20pce
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\b(\d+)\s*piece\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0
```

### Fix B: `calculate_rsu_robust` (The "Equality Shield")
**Goal:** If Amazon says "10" and Supplier says "10" (even if text differs), force RSU=1.0.

```python
def calculate_rsu_robust(row):
    """
    Robust RSU calculation with 'Numeric Equality Shield'.
    If strict Pack Match detects 1:1 numerical equality, RSU is forced to 1.0.
    """
    amz_qty = extract_quantity(row['AmazonTitle'])
    sup_qty = extract_quantity(row['SupplierTitle'])
    
    # 1. Exact Numerical Match Shield (The "Phoods/Chef Aid" Fix)
    # If both have extracted a quantity > 1, and they ARE THE SAME, then RSU = 1.
    if amz_qty > 1 and sup_qty > 1 and amz_qty == sup_qty:
        return 1.0
        
    # 2. Logic for 'Pack of X' vs Single
    # Amazon sells 20, Supplier sells 1 -> RSU = 20
    if amz_qty > 1 and sup_qty == 1.0:
        return amz_qty
        
    # 3. Logic for Bulk Supplier
    # Amazon sells 1, Supplier sells 20 -> RSU = 0.05 (Technically correct but usually we buy 1 pack of 20 to sell 20 singles? No, usually not for arbitrage logic here. Stick to simple RSU.)
    # For this report, we focus on needing MORE supplier units to fulfill Amazon order.
    
    # Standard Ratio
    ratio = amz_qty / sup_qty
    return ratio
```

### Fix C: `recalculate_profit` (Use New RSU Logic)
**Goal:** Apply the robust RSU to profit calc.

```python
def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        
        # Use ROBUST RSU calculation
        rsu = calculate_rsu_robust(row)
        row['RSU'] = rsu # Store for verdict
        
        # If RSU is 1, profit is unchanged (minus minor adjustment logic if any?)
        # Logic: Adjusted = Sale - (Cost * RSU) - Fees
        # Actually our NetProfit already includes ONE cost.
        # So we subtract (RSU-1) * Cost.
        
        adjustment_cost = supplier_cost * (rsu - 1.0)
        return original_profit - adjustment_cost
    except:
        return 0.0
```

## 3. Implementation Instructions
1.  Open `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md`.
2.  Locate the Python Code Block (` ```python ... ``` `).
3.  Replace the `extract_quantity` function.
4.  Replace/Update `recalculate_profit` to include the `calculate_rsu_robust` logic (or add the helper and call it).
5.  Save as `FINANCIAL REPORT PROMPT ANALYSIS_AG1_v3.md`.
