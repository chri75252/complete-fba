# AG1 Report Performance Audit & Comprehensive Discrepancy Analysis

**Date:** 2025-12-31
**Analyzer:** Antigravity (Agent)
**Context:** Multi-folder report comparison (`OPUS`, `CODEX`, `webapp`) to validate Prompt Fixes.
**Status:** **RE-EVALUATED** with full breakdown of all categories.

## 1. Comprehensive Report Comparison

| Metric | **OPUS AG1** | **CODEX AG1** | **webapp ag1** |
| :--- | :--- | :--- | :--- |
| **Total Rows Analyzed** | **2221** (Full) | 2221 | 2221 |
| **Total Rows Listed in Report** | **~2126** | 140 (Truncated) | 202 (Truncated) |
| **VERIFIED — RECOMMENDED** | **34** | 26 | 26 |
| **VERIFIED — FILTERED OUT** | 2 | 8 | 10 |
| **HIGHLY LIKELY — RECOMMENDED** | **146** | 23 | 60 |
| **HIGHLY LIKELY — FILTERED** | *Not listed explicitly* | 9 | 7 |
| **NEEDS VERIFICATION** | **60** | 24 | 40 |
| **FILTERED OUT (Total/Sample)** | 1884 | 50 (Sample) | 59 (Sample) |

### Key Observation: Recall vs. Precision
*   **OPUS AG1:** Exhibited the **Highest Recall**. It passed 34 items as "Verified" and found 146 "Highly Likely". However, this came at the cost of **Safety** (see Section 2).
*   **CODEX AG1:** Exhibited the **Strictess Filtering**. It aggressively filtered items where it detected *any* pack mismatch, resulting in only 26 Verified items.
*   **webapp ag1:** Occupied a middle ground but leaned closer to Codex in strictness.

## 2. Deep Dive: The "False Positive" Trap in OPUS AG1
A critical analysis of the "Verified Recommended" items reveals that **OPUS AG1's higher count (34) is partially due to Loose Pack Detection**, not just better finding.

### Case Study 1: TIDYZ DOGGY BAGS
*   **Item:** `TIDYZ DOGGY BAGS STRONG 50 PCS`
*   **Amazon:** "200 x Extra Large... (4 x 50)"
*   **Supplier:** "50 PCS"
*   **True Status:** **Mismatch / Bundle Required** (RSU = 4).
*   **OPUS Verdict:** **VERIFIED (1:1 Match)**. *Failure.* OPUS missed the "4 x 50" or "200" on Amazon and erroneously treated it as a single unit, identifying it as a profitable 1:1 match.
*   **CODEX Verdict:** **FILTERED OUT**. *Success.* Codex correctly identified "BUNDLE (4x)" and calculated RSU=4. Since this killed the profit, it filtered it.
*   **Conclusion:** OPUS was "Wrong" (Dangerous), Codex was "Right" (Safe).

### Case Study 2: CHEF AID SHOT GLASSES
*   **Item:** `CHEF AID SHOT GLASSES ASSORTED 20PCE`
*   **Amazon:** "Pack of 20"
*   **Supplier:** "20PCE"
*   **True Status:** **1:1 Match** (Both are 20).
*   **OPUS Verdict:** **VERIFIED (1:1 Match)**. *Accidentally Correct?* OPUS likely missed *both* pack counts (Amazon "Pack of 20" and Supplier "20PCE") and defaulted both to 1. Result: RSU=1, Profitable.
*   **CODEX Verdict:** **FILTERED OUT**. *Partial Failure.* Codex correctly saw Amazon "Pack of 20" but **failed** to parse Supplier "20PCE". Result: RSU=20 -> Expense spiked -> Filtered.
*   **Conclusion:** Both failed logic, but Codex's failure mode (Filtering) is safer than OPUS's failure mode (Accidental Verify).

## 3. Discrepancy & Fix Validation
The analysis confirms that the proposed **Prompt Fixes** are absolutely necessary to bridge the gap between "OPUS Recall" and "CODEX Safety".

### Validated Prompt Injections:
1.  **Regex for Supplier Shorthand (`20PCE`):**
    *   **Why:** This will fix the **CODEX Failure** on Chef Aid. It will allow the system to see "20" on the supplier side.
2.  **Numeric Equality Shield:**
    *   **Why:** This will ensure that when *both* sides are "20" (Chef Aid), RSU is forced to 1, effectively "Verifying" the item correctly (unlike Codex which filtered it, and OPUS which likely verified it by accident).
3.  **Strict Amazon Pack Detection:**
    *   **Why:** Ensure cases like `TIDYZ` (4x50) are ALWAYS caught (like Codex did), preventing the false "Verified" status seen in OPUS.

## 4. Final Recommendation
*   **Base Reference for Logic:** Use **CODEX** logic (strictness) as the baseline for *behavior*, but aim for **OPUS** numbers (recall) by fixing the parsing errors that caused Codex to over-filter.
*   **Immediate Action:** Apply the **Surgical Fixes** detailed in `AG1_PROMPT_FIX_PLAN_WITH_REFERENCE.md` to `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md`.
