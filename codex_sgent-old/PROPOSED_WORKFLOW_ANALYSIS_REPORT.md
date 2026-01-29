# ANALYSIS OF USER-PROPOSED WORKFLOW ADJUSTMENTS (v5.0 Strategy)

**Date:** 2026-01-08  
**Subject:** Detailed Feasibility & Optimization Report on User's Proposed "Inspector-Supervisor-Executor" Workflow (Steps 5, 7, 6)

---

## 1. EXECUTIVE SUMMARY

I have analyzed your proposed adjustments to the agent workflow, specifically the interaction between **Step 5 (Adjudication)**, **Step 7 (Comprehensive Adjudication)**, and **Step 6 (AI Critique)**.

**Verdict:** Your proposed flow represents a **significant architectural improvement** over the current model. By transforming Step 5 into a "mass inspection" layer that feeds Step 7 (Root Cause Analysis) and elevating Step 6 (Critique) to an "Executive Decision Maker," you solve the core problem of *fragmented context*.

The separation of **Observation** (Step 5), **Synthesis** (Step 7), and **Execution** (Step 6) is a highly robust "Agentic Design Pattern."

---

## 2. COMPARISON: CURRENT VS. PROPOSED WORKFLOW

### A. The Separation of Duties

| Feature | Current Workflow | **YOUR PROPOSED WORKFLOW (v5.0)** |
| :--- | :--- | :--- |
| **Step 5 (Adjudication)** | **Selective Fixer:** Picks top ~100 "Ambiguous" rows. Makes decisions in isolation. Writes to ledger immediately. | **Mass Inspector:** Scans **ALL** rows in batches (25). Generates analysis *metadata* for every product. Does NOT write to ledger directly; passes findings to Step 7. |
| **Step 7 (Comprehensive)** | **Report Proofreader:** Reads the MD report to find linguistic/logic errors. No access to individual row analysis history. | **Root Cause Analyst:** Receives **aggregated row analyses** from Step 5 + MD Report + **Source Script**. Correlates individual errors to find *Algorithmic Root Causes*. |
| **Step 6 (Critique)** | **Gatekeeper:** Checks valid/invalid counts. Says "Stop" or "Go". Passive observer. | **Executive:** Receives the "Fix Plan" from Step 7. Decides **WHAT** to do: (1) Apply specific row edits, OR (2) Update the python script and Re-run. |
| **Data Flow** | Ledger → Adjudication → Report → Comprehensive | MD Report → **Step 5 (Inspection)** → **Step 7 (Synthesis)** → **Step 6 (Decision)** → Action |

---

## 3. DETAILED ASSESSMENTS & REFINEMENTS

### STEP 5: AI ADJUDICATION (The "Mass Inspector")

**User Requirement:**
> "Group entries into batches of 20 or 25... analyze ALL product rows (not just top 50/100)... reference the MD report... removing NET PROFIT/ROI as a filter."

**Observation & Feasibility:**
*   **Feasibility:** ✅ **HIGH**.
    *   Analyzing 2,500+ rows in batches of 25 requires ~100 LLM calls. This is computationally heavier but provides *massive* context benefits.
    *   **Cost/Time:** Estimated 3-5 minutes runtime for parallel batches. Acceptable for a "Thorough" mode.
*   **The "Context" Shift:**
    *   You explicitly stated this step refers to the **Generated MD Report**.
    *   *Refinement:* To make this efficient, Step 5 should parse the **Markdown Report Rows** (or the exact data prepared for them) and feed them to the LLM. This ensures the LLM sees exactly what the user sees.

**AGREEMENT:**
*   **DELETE** "High Profit / Low Confidence" filter.
*   **DELETE** "Top N" limit.
*   **ACTION:** Process **EVERY** row that appears in the report (Verified, Highly Likely, Needs Verification) AND potentially high-relevance "Filtered" items to check for False Negatives.

**SUGGESTED OPTIMIZATION:**
*   Do not just send the row. Send the **Row + The Determination Logic** used.
*   *Prompt Tweak:* "Here is a batch of 25 rows from the generated report. For each, verify if the categorization is correct based on [Rules]. If incorrect, flag for Step 7."

---

## 4. STEP 7: COMPREHENSIVE ADJUDICATION (The "Root Cause Analyst")

**User Requirement:**
> "Has now all combined analyses... access to MD report... AND ACCESS TO THE SCRIPT... identify root cause... suggest fixes for script."

**Observation:**
*   **This is the "Brain" of the operation.**
*   Giving it access to the **Deterministic Script** (`analysis.py`, `pack.py`) is brilliant. It allows the AI to say: *"I see 50 rows failing because of logic on line 140, not just 'random errors'."*

**Refinement on "Script Access":**
*   We should not dump the *entire* codebase into the context (too much noise).
*   **Optimization:** We will inject the **specific logic files**: `src/fba_agent/analysis.py` (decision trees) and `src/fba_agent/pack.py` (pack logic). These contain 90% of the decision logic.

**Output Structure for Step 7:**
Step 7 must output a structured **"Hypothesis & Fix Object"**:
```json
{
  "row_level_corrections": [
    {"row_id": 101, "action": "move_to_highly_likely", "reason": "Brand match ignored"}
  ],
  "systemic_issues": [
    {
      "pattern": "50 rows excluded due to 'Pack' mismatch on 'Sets'",
      "suspected_root_cause": "script logic for 'Set' keyword is too aggressive",
      "suggested_script_fix": "Modify analysis.py line 150 to allow..."
    }
  ]
}
```

---

## 5. STEP 6: AI CRITIQUE (The "Executive Decision Maker")

**User Requirement:**
> "Instruct the LLM to use all info... make a calculated decision on: (1) Implementing row changes, (2) Deciding if script adjustment is needed... Execute Second Iteration."

**Observation:**
*   This transforms the workflow from **Linear** to **Looping/Iterative**.
*   **Critique is now the "Boss".**

**The Decision Matrix for Step 6:**
1.  **If Issues are Isolated (Row Specific):**
    *   Action: Apply manual overrides to `coverage_ledger.csv`.
    *   Result: Regenerate Report (Fast).
2.  **If Issues are Systemic (Script Logic):**
    *   Action: **Apply Code Patch** (via `multi_replace_file` or explicit instruction) -> **CLEAR MEMORY/CACHE** -> **RERUN ANALYSIS**.
    *   *Risk:* Allowing AI to auto-edit script logic is high-risk.
    *   *Safe Approach:* The Critique should output a **"Proposed Patch"** and trigger a re-run with a *temporary* override or halt for user approval if "SafeToAutoRun" is false.
    *   *User's explicit instruction:* "Agent is going to execute/run the second iteration." -> Implies full autonomy. We will implement strict **Regression Checks** (as you described) to ensure the fix didn't break other things.

---

## 6. PROPOSED NEW WORKFLOW DIAGRAM

Based on your description, here is the new logic flow:

```mermaid
graph TD
    A[Deterministic Run (Phase 1)] --> B[Generate MD Report v1]
    B --> C[Step 5: Mass Inspection (Batches of 25)]
    C -- "Analysis Metadata of ALL Rows" --> D[Step 7: Comprehensive Analyst]
    D -- "Context: MD Report + Script + Row Metdata" --> D
    D -- "Output: Row Fixes + Script Fixes" --> E[Step 6: AI Critique (Executive)]
    
    E{Decision?}
    E -- "Systemic Bug Found" --> F[Update Script / Logic]
    F --> G[Rerun Analysis (Iter 2)]
    G --> H[Regression Check (Iter 1 vs Iter 2)]
    H -- "Improved?" --> I[Finalize Report]
    H -- "Worsened?" --> J[Revert & Use Report v1]
    
    E -- "Only Row Errors" --> K[Apply Row Overrides]
    K --> L[Regenerate Report v1.1]
    L --> I
```

---

## 7. RECOMMENDATIONS FOR IMPLEMENTATION

1.  **Batching Logic (Step 5):**
    *   Implementation: Use a generator to yield chunks of 25 rows from the `PHASEA_MANUAL_REPORT` (parsed back from MD or using the source dataframe filtered by the report inclusion criteria).
    *   **Crucial:** Ensure "FILTERED OUT" items that *should* be in (False Negatives) are included in the inspection. I suggest analyzing **Top 200 Filtered Items** (sorted by profit/relevance) in addition to all Included items, to check for missed opportunities.

2.  **Script Context (Step 7):**
    *   We will load `fba_agent/analysis.py` into the context window of Step 7. This allows the LLM to quote the exact line causing the issue.

3.  **The "Profit" Rule (Step 5):**
    *   **CONFIRMED:** I will remove the `if net_profit > 10` filter from the Adjudication candidate selector.
    *   **New Selector:** `if product_in_report OR (product_in_filtered AND looks_relevant)` -> Select for Step 5 inspection.

4.  **Regression Check:**
    *   The "Iteration Regression Check" becomes critical here. If Step 6 modifies the script and reruns, we MUST compare specific metrics (Total Verified Profit, # of False Positives) to ensure the "Fix" didn't cause a "Collapse".

## 8. CONCLUSION

Your design is feasible and highly logical. It correctly places the LLM in positions where its strengths (context, reading, reasoning) are utilized (Step 7 & 6) while using the deterministic system (Step 1-4) for the heavy lifting.

**I am ready to proceed with the edits to `run.py`, `iteration.py`, `adjudication.py`, `comprehensive_adjudication.py`, and `critique.py` to implement this "Inspector-Supervisor" architecture.**
