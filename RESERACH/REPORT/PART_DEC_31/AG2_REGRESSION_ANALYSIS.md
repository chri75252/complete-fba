# AG2 Analysis: Regression Report & Strategic Pivot

## 1. Executive Summary: The "AG2" Regression
The reports generated under `gem ag2` and `webapp ag2` represent a **significant degradation** in performance compared to the OPUS AG1 baseline. 

| Metric | OPUS AG1 (Baseline) | webapp ag2 | gem ag2 |
| :--- | :--- | :--- | :--- |
| **Verified** | 34 | 26 | 4 |
| **Highly Likely** | 146 | 125 | 9 |
| **Total Actionable** | **180** | **151** | **13** (Critical Failure) |
| **Key Failure Mode** | False Positives (Loose) | **Over-Filtering** | **Catastrophic Filtering** |

**Verdict:** The recent "Surgical Fixes" (Regex + Shield) functioned technically but revealed a deeper flaw: **Rigidity.** By hardcoding specific regex patterns (`pce`, `pcs`), we fixed specific items (Chef Aid) but failed to account for the infinite variability of supplier naming conventions (e.g., `TALA ... 200` vs `Pack Off 200`). Furthermore, the "Capacity Check" logic became hyper-sensitive, filtering valid matches due to "hallucinated" mismatches (e.g., Row 171 `20PCE` vs `30ml` capacity confusion).

## 2. Root Cause Analysis: Why "AG2" Failed

### A. The "Extraction Asymmetry" (The Shield didn't activate)
The **Numeric Equality Shield**—designed to verify 1:1 matches when numbers match—only works if **BOTH** sides successfully extract the number.
*   **Example:** `TALA COCKTAIL STICKS 200`
*   **Amazon:** "Pack Off 200 Stick" -> LLM/Regex might see "200".
*   **Supplier:** "200" (at end). -> The rigid regex (`(\d+) pcs`) **missed** this because it lacks a unit.
*   **Result:** Shield inactive. RSU calculated as `200 / 1 = 200`. Profit destroyed.

### B. "Capacity Hallucination" (The new filter criteria)
`gem ag2` filtered valid matches because it detected "Capacity Mismatches" that weren't real.
*   **Example:** `CHEF AID SHOT GLASSES`
*   **Result:** `NEEDS VERIFICATION` -> Filter Reason: `Capacity tokens differ (>50%)`.
*   **Reality:** It likely compared "30ml" (capacity) with "20" (count) or similar irrelevant tokens, triggering a false flag.

## 3. Strategic Pivot: Dynamic Calibration (User Proposal)
Your suggestion is correct. **We cannot "hardcode" our way to perfection** with a single static prompt script. Suppliers are too diverse.

### The "Universal" Flaw
Trying to write ONE Python script that handles `Pack of 10`, `10x`, `(10)`, `10-pk`, `10 UNIT`, and `10` (no unit) simultaneously leads to the rigidity we see now.

### The Solution: "Pre-Flight Calibration"
Instead of guessing the supplier's logic, we must **ask the Agent to analyze the file FIRST**, then **write the extraction logic CUSTOM** for that file.

#### Proposed Workflow (The "Fix"):
1.  **Step 1: The Calibration Prompt (Pre-Prompt)**
    *   **Task:** Read the first 50 rows of the *specific* supplier file.
    *   **Output:** Identify the **Naming Convention**.
        *   "This supplier uses 'X PK' for packs."
        *   "This supplier puts the quantity at the absolute end of the string (e.g. '... 200')."
        *   "This supplier uses 'Box of N'."
    *   **Action:** Generate the *custom* Regex patterns for this specific run.

2.  **Step 2: The Execution Prompt (Main Analysis)**
    *   **Input:** The custom Regex/Logic from Step 1.
    *   **Action:** Run the analysis using these tailored rules.

3.  **Step 3: The Verification Prompt (Post-Analysis Check)**
    *   **Task:** As you requested, pause and audit the `VERIFIED` / `FILTERED` lists *heuristically*.
    *   **Logic:** "I see you verified 'Tidyz 50 PCS'. Wait, Amazon says '4 x 50'. Flag this discrepancy."

## 4. Immediate Next Steps
1.  **Discard `ag2` logic:** It provides safety but destroys ROI.
2.  **Adopt the 3-Step Workflow:** I will design the **Calibration Prompt** to run *before* the financial analysis. This ensures we don't need to manually update regexes for every new supplier.
