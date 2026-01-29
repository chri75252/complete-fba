# PROMPT FIXES APPLIED — v4.1.1 SUMMARY

**Generated:** 2026-01-02 07:35  
**Files Modified:**
- `FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.1.md` (new file, based on AG1 v1)

**Original File Preserved:**
- `FINANCIAL REPORT PROMPT ANALYSIS_AG1.md` (unchanged backup)

---

## CLARIFICATIONS PROVIDED

### 1. "Every Product" → Realistic Language
**Issue:** "Apply deep, human-like reasoning to every product" is unrealistic for thousands of rows.

**Clarification:** This prompt is the **INITIAL FILTERING STEP**. The subsequent manual analysis (using `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`) will refine results.

**Fix Applied:** Changed to:
> "This analysis is the INITIAL FILTERING STEP before manual verification... **It is better to include borderline items than to miss valid matches** — the subsequent manual analysis step will refine the results."

---

### 2. SUPPLIER_NAMING_CONVENTION is an EXAMPLE
**Issue:** The calibration config should not dictate exact values.

**Fix Applied:** Added:
> "**Example calibration output** (actual values will vary by supplier)"
> 
> "# This is an EXAMPLE — actual values depend on the specific supplier"

---

### 3. FILTERED OUT Examples are Illustrative
**Issue:** Examples should be identified as scenarios, not exhaustive rules.

**Fix Applied:** Changed:
- "Example FILTERED OUT items (all are CONFIRMED matches)" → "**Example FILTERED OUT items (illustrative scenarios, not exhaustive)**"
- "Include in FILTERED OUT when:" → "**Include in FILTERED OUT when (examples, not exhaustive)**"

---

### 4. Pack Contradiction with Positive Adjusted Profit
**Issue:** If RSU > 1 but adjusted profit REMAINS POSITIVE, item stays in VERIFIED/HIGHLY LIKELY.

**Fix Applied:** Added explicit note:
> "Note: If RSU > 1 but adjusted profit REMAINS POSITIVE → item stays in VERIFIED/HIGHLY LIKELY with adjusted profit shown"

Updated Step 1 in decision tree:
> "If `is_exact_ean_strict == True` AND pack mismatch detected:
>   - Recalculate RSU and Adjusted Profit
>   - If Adjusted Profit > 0 → **VERIFIED** (with adjusted profit and pack note shown)
>   - If Adjusted Profit ≤ 0 → **FILTERED OUT**"

---

### 5. rsu_max_reasonable Removed from Agent Instructions
**Issue:** This was Python code guidance, not agent instruction.

**Fix Applied:** Removed from the main agent instructions. The RSU sanity check is in the Python code section only.

---

### 6. Size/Weight/Volume Differences
**Clarification Confirmed:**
- **Different sizes** (500ml vs 750ml) = Usually NOT matching → FILTERED OUT or NEEDS VERIFICATION
- **Pack × capacity** ("3 x 400ml") = 3 bottles of 400ml = RSU 3 (already correctly documented)
- Agent should NOT multiply size × pack — RSU is just the pack count

**Already present in prompt:**
> "**CRITICAL - Capacity Suffix Patterns (N x [capacity] is NOT multiplied):**
> | "3 x 400ml" | 3 bottles of 400ml each | RSU = 3 (NOT 1200) |"

---

### 7. Pre-Filtered Data Notice
**Issue:** Reports already have profit<0 and sales=0 filtered. Remove instructions asking agent to filter these.

**Fixes Applied:**
- **Rule #3:** Changed from "Sales > 0 required" to:
  > "**PRE-FILTERED INPUT DATA:** The input data has already been pre-filtered by the user... Do NOT apply additional filtering for profit or sales thresholds."

- **Acceptance Test A3/A4:** Updated to note pre-filtered data
- **Verify V2/V3:** Updated to note pre-filtered data
- **Step 8:** Updated to note pre-filtered data
- **NEEDS VERIFICATION:** Removed financial metric requirements (Net Profit > £0.50, ROI > 15%, Sales > 0)

---

## ALL CHANGES MADE TO v1.1

| Section | Line(s) | Change |
|---------|---------|--------|
| Version Header | 187-193 | Updated to v4.1.1, added purpose clarification |
| First-Pass Principle | 207 | Changed "every product" to "first-pass filtering" |
| Preflight Integration | After 207 | Added new section with calibration example |
| Rule #3 | 258-263 | Changed from Sales>0 to pre-filtered data notice |
| HIGHLY LIKELY | 286-302 | Added EAN guidance (missing vs different), brand anywhere |
| NEEDS VERIFICATION | 304-327 | Removed financial metrics, simplified |
| FILTERED OUT | 329-369 | Clarified it's for confirmed matches, added RSU>1 positive note |
| Combination 2 | 444-448 | Changed "STARTS with" to "CONTAINS brand ANYWHERE" |
| Count Limits | 461-479 | DELETED entire section |
| Decision Tree | 783-821 | Updated all 5 steps with EAN guidance, RSU recalc, clarified Step 4 |
| Acceptance Tests | 30-33 | Updated A3/A4 for pre-filtered data |
| Plan Step 8 | 100-103 | Updated for pre-filtered data |
| Verify V2/V3 | 111-113 | Updated for pre-filtered data |
| Validation Checklist | 976-991 | Added new checks, removed count limit check |
| Version Footer | 990-993 | Updated to v4.1.1 with creation date |

---

## WHAT WAS NOT CHANGED (Preserved)

- EAN validation and checksum logic (Stage 3/3B)
- Title similarity calculation (Stage 2)  
- Dimension Shield patterns (Stage 6)
- Pack extraction code snippets (Stage 4)
- Capacity tolerance thresholds
- Table schema and output format
- IP Risk flagging rules

---

## FILES CREATED

1. **`FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.1.md`** — New version with all fixes applied
2. **`PROMPT_FIXES_PLAN_v4.3.md`** — This summary document

## NEXT STEPS

1. Test v1.1 prompt on same dataset (`part_1_jan.xlsx`)
2. Compare results with OPUS 1 reference
3. Verify FILTERED OUT section is populated correctly
4. Verify RSU calculations are correct (no 81, no 1200)
