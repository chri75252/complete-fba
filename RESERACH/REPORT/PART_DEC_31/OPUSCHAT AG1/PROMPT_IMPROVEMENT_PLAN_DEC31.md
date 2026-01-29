# Prompt Improvement Plan for AG1 (Dec 31)

**Status:** Draft Recommendation
**Based On:** Discrepancy Analysis of `PHASEA_MANUAL_REPORT_20251231.md` vs Initial Runs.
**Reference Prompt:** `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md`

---

## 1. Root Cause Identification

The "Incorrect Outputs" (specifically the loss of profitable verified items) were traced directly to **Stage 4: Pack Size Extraction** and **Stage 4B: Multipack Calculation Rule** in the existing prompt.

### Specific Failure Points:
1.  **Regex Asymmetry (The "PCE" Blindspot):**
    *   **Current Prompt Logic (Lines 604-617):** Includes standard English patterns (`pack of`, `set of`).
    *   **Missing Patterns:** Does **NOT** include supplier shorthand commonly found in the dataset: `(\d+)pce`, `(\d+)pcs`, `(\d+)pk`.
    *   **Result:** Supplier title "Item 20PCE" was parsed as Quantity=1. Amazon title "Pack of 20" was parsed as Quantity=20.
    *   **Impact:** Calculated `RSU = 20`. Cost multiplied by 20. Profit became negative. Item Filtered.

2.  **Profit Recalculation Rigidity:**
    *   **Current Logic:** The `recalculate_profit` function applies the RSU adjustment blindly.
    *   **Refinement Needed:** If `Supplier_Qty` == `Amazon_Qty`, the RSU should be locked to 1 *regardless* of keyword matching (e.g. if one says "Pack" and the other doesn't, but numbers match).

---

## 2. Surgical Fix Proposals

The following changes are recommended for the `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md` file.

### Fix A: "Symmetric Extraction" Regex Block (Replace Lines 604-617)

**Current Code:**
```python
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        # ...
    ]
```

**Proposed Replacement (Enhanced):**
```python
    patterns = [
        # Explicit Supplier Shorthand (Priority)
        r'(\d+)\s*pce\b',       # e.g. "20pce" or "20 pce"
        r'(\d+)\s*pcs\b',       # e.g. "50pcs"
        r'(\d+)\s*pk\b',        # e.g. "10pk"
        r'(\d+)\s*piece\b',     # e.g. "10 piece"
        
        # Standard Pack Indicators
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
    ]
```

### Fix B: The "1:1 Equality Shield" (Update `extract_multipack_total` or `RSU` logic)

**Current Instruction:**
"Calculate RSU (Required Supplier Units) = Amz_Total / Sup_Qty"

**Proposed Instruction (Add Logic):**
> **CRITICAL LOGIC ADDITION:**
> Before calculating RSU mismatch, check for **Numeric Equality**:
> ```python
> if supplier_qty_extracted > 1 and amazon_qty_extracted > 1:
>     if supplier_qty_extracted == amazon_qty_extracted:
>         RSU = 1.0  # Force 1:1 match even if keywords differ
> ```
> *Rationale:* If Supplier says "20PCE" and Amazon says "Pack of 20", the numbers match. Do NOT penalize profit.

---

## 3. Reference to "Golden Report"

When implementing these fixes, use **`PHASEA_MANUAL_REPORT_20251231.md`** as the **Golden Reference**.

*   **Why:** This report contains the manually recovered items (e.g., `CHEF AID SHOT GLASSES`, `FIRE UP FIRELIGHTERS`) that were correctly identified *after* applying the manual fixes equivalent to the proposals above.
*   **Verification:** Any future prompt run should be tested against this report. If `CHEF AID SHOT GLASSES` is missing or filtered, the prompt is failing the "PCE" test.

---

## 4. Summary of Impact

Implementing these fixes will:
1.  **Prevent False Negatives:** Profitable items like "20PCE" goods will no longer be filtered out.
2.  **Increase Verification Count:** Directly increases the yield of "VERIFIED" items without lowering safety standards.
3.  **Reduce Manual Review:** "Highly Likely" items that were actually exact matches (but failed pack logic) will correctly move to "Verified".
