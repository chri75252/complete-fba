# PROMPT ALIGNMENT ANALYSIS

**Date:** 2026-01-06  
**User Expectation:** Manual review of existing report + gap analysis for missed products

---

## 📋 USER'S CLEAR EXPECTATIONS

### What "Manual Analysis" Means:
1. **Review existing generated report** (e.g., PHASEA_MANUAL_REPORT_20260102_081924.md)
2. **Read listed product rows** one by one
3. **Analyze metrics, titles, EAN** for each row
4. **Make educated decisions** on correctness of categorization
5. **Identify incorrectly categorized rows**
6. **Understand root causes** of errors/discrepancies
7. **Go back to source data** (part_1_jan.xlsx) to find missed products
8. **Focus on VERIFIED and HIGHLY LIKELY** sections
9. **Remove or recategorize** incorrectly listed products
10. **Generate updated report:** `MANUAL_REPORT_YYMMDDHHMM.md`

### Expected Workflow:
```
INPUT: Existing report → REVIEW: Validate categorizations → 
GAP ANALYSIS: Find missed products → OUTPUT: Updated report
```

---

## ❌ SECTIONS NOT ALIGNED

### File 1: `MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md`

#### ❌ Issue 1: Wrong Input Source (Lines 15-16)
```markdown
CURRENT (Line 16):
"You must read and evaluate every row in the financial report (RowID 1..N)"

PROBLEM:
- Tells LLM to analyze SOURCE EXCEL FILE
- Does NOT instruct to review EXISTING REPORT first
- Missing two-phase approach

EXPECTED:
- Primary Input: Previously generated report
- Reference Input: Source Excel (for gap analysis only)
```

#### ❌ Issue 2: No Review Phase Instructions
```markdown
CURRENT:
- Only has "Revisit Loop" (lines 35-45)
- This is for checking false positives WITHIN a single analysis pass
- NOT for reviewing an existing report

MISSING:
- Instructions to load existing report
- Instructions to validate each categorized product
- Instructions to identify miscategorizations
- Instructions to understand root causes
- Instructions to create correction list
```

#### ❌ Issue 3: No Gap Analysis Phase
```markdown
CURRENT:
- No instructions to extract Row IDs from existing report
- No instructions to compare against source data
- No instructions to find products that were missed

MISSING:
- Extract Row IDs from report
- Compare against all 2,402 source rows
- Filter for high-value candidates
- Use relaxed criteria to find more products
```

#### ❌ Issue 4: Wrong Output Schema Reference (Lines 48-49)
```markdown
CURRENT:
Generate PHASEA_MANUAL_REPORT_YYYYMMDD.md using schema from:
"FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md"

PROBLEM:
- References the ANALYSIS PROMPT (not a report)
- Should reference methodology guide or example report

EXPECTED:
Output: MANUAL_REPORT_YYMMDDHHMM.md
Schema: From FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
```

#### ❌ Issue 5: No "Relaxed Criteria" for Gap Analysis
```markdown
CURRENT (Line 41-42):
"same brand token in both titles, or strong shared product-type anchors"

MISSING:
- Multiple pathways to HIGHLY LIKELY beyond brand match
- Keyword overlap threshold (e.g., ≥4 shared keywords)
- Title similarity threshold (e.g., ≥65% match)
- Multiple moderate signals combined
- These would help find products missed due to strict filters
```

#### ❌ Issue 6: No Explicit Correction Workflow
```markdown
MISSING ENTIRELY:
1. Load existing report
2. For each categorized product:
   - Validate EAN match
   - Validate pack size calculation
   - Validate adjusted profit
   - Check for dimension traps
3. Create list of corrections:
   - Products to move from X → Y
   - Pack calculations to fix
   - Profit recalculations needed
4. Document root causes of errors
```

---

### File 2: `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`

#### ✅ Mostly Aligned BUT Missing Key Sections:

#### ❌ Issue 1: No "Review Existing Report" Phase
```markdown
PHASES DEFINED:
- Phase 1: Data Extraction (from source)
- Phase 2: EAN Match Analysis
- Phase 3: Title-Based Verification
- Phase 4: Pack Size Detection
- Phase 5: Browser Verification
- Phase 6: Adjusted Profit Calculation
- Phase 7: Final Categorization
- Phase 8: Report Comparison (Optional) ← This is close but not enough

MISSING:
- Phase 0 or Phase 1A: "Review Existing Report"
  - Load previously generated report
  - Validate each product's categorization
  - Identify errors
  - Create correction list
```

#### ❌ Issue 2: Phase 8 is Optional Comparison, NOT Review
```markdown
CURRENT Phase 8 (Lines 473-505):
- Compares MULTIPLE LLM reports against each other
- Finds agreements/disagreements
- Documents differences

PROBLEM:
- This is for comparing DIFFERENT reports (Report A vs Report B)
- NOT for reviewing a SINGLE report to find errors

EXPECTED:
- Review ONE report's categorizations
- Validate correctness
- Find miscategorizations
- Identify root causes
```

#### ❌ Issue 3: No Gap Analysis Methodology
```markdown
MISSING:
- Extract Row IDs from existing report
- Compare against source data
- Find products NOT in report
- Filter for high-value candidates
- Use relaxed criteria to categorize them
- Add to updated report
```

#### ❌ Issue 4: Coverage Contract is for Fresh Analysis, Not Review
```markdown
CURRENT (Lines 71-82):
"Read every row in the financial report (RowID 1..N)"

PROBLEM:
- This is for analyzing SOURCE EXCEL FILE
- NOT for reviewing an existing report

EXPECTED:
- Review all products IN existing report
- THEN check for gaps in source data
```

#### ❌ Issue 5: No "Relaxed Pathways" for HIGHLY LIKELY
```markdown
CURRENT (Lines 438-446):
HIGHLY LIKELY Criteria:
- Brand name matches exactly
- Product type matches exactly
- Size/variant identical or within tolerance

MISSING:
Alternative pathways wenn brand not in list:
- High keyword overlap (≥4 shared keywords)
- High title similarity (≥65%)
- Multiple moderate signals combined
- These would find products your brand list missed
```

#### ❌ Issue 6: UNRELATED vs FILTERED OUT Distinction
```markdown
CURRENT (Lines 60-65):
- UNRELATED / NOT INCLUDED: Not confirmed match (don't list)
- FILTERED OUT: Confirmed match but excluded

PROBLEM FOR YOUR USE CASE:
- This applies to FRESH analysis from source
- For REVIEW + GAP ANALYSIS, need different approach:
  - Review Phase: Validate existing categorizations
  - Gap Phase: Find products that should be HIGHLY LIKELY but were missed
```

---

## 📊 SUMMARY: WHAT'S NOT ALIGNED

| Aspect | User Expectation | Current Prompts | Aligned? |
|--------|------------------|-----------------|----------|
| **Primary Input** | Existing generated report | Source Excel file | ❌ NO |
| **Review Phase** | Validate existing categorizations | Not defined | ❌ NO |
| **Correction List** | Document miscategorizations | Not defined | ❌ NO |
| **Root Cause Analysis** | Identify why errors happened | Not defined | ❌ NO |
| **Gap Analysis** | Find missed products | Not explicitly defined | ❌ NO |
| **Relaxed Criteria** | Multiple HIGHLY LIKELY pathways | Only brand match | ❌ NO |
| **Output Filename** | MANUAL_REPORT_YYMMDDHHMM.md | PHASEA_MANUAL_REPORT_YYYYMMDD.md | ❌ NO |
| **Two-Phase Approach** | Review → Gap Analysis | Single pass analysis | ❌ NO |
| **Focus Areas** | VERIFIED & HIGHLY LIKELY | All categories equally | ⚠️ PARTIAL |
| **Methodology Quality** | Manual-style reasoning | Automated filters | ⚠️ PARTIAL |

---

## 🔧 WHAT NEEDS TO BE ADDED

### To `MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md`:

1. **Change Primary Input:**
   ```diff
   - You must read and evaluate every row in the financial report
   + PRIMARY INPUT: Previously generated report (e.g., PHASEA_MANUAL_REPORT_20260102_081924.md)
   + REFERENCE INPUT: Source Excel (part_1_jan.xlsx) for gap analysis only
   ```

2. **Add Review Phase:**
   ```markdown
   ## PHASE A: REVIEW EXISTING REPORT
   
   1. Load the previously generated report
   2. For each product in VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, FILTERED OUT:
      - Validate EAN match (check for false positives)
      - Validate pack size calculation (watch for dimension traps)
      - Validate adjusted profit
      - Check reasoning against methodology
   3. Create correction list (products miscategorized)
   4. Document root causes of errors
   ```

3. **Add Gap Analysis Phase:**
   ```markdown
   ## PHASE B: GAP ANALYSIS
   
   1. Extract all Row IDs from existing report
   2. Load source data (part_1_jan.xlsx)
   3. Find products NOT in existing report
   4. Filter for high-value candidates:
      - Profit > £0.50
      - Sales ≥ 50
      - Some match signal (EAN, brand, title similarity)
   5. Apply RELAXED criteria:
      - Pathway 1: Brand match
      - Pathway 2: Keyword overlap ≥ 4
      - Pathway 3: Title similarity ≥ 65%
      - Pathway 4: Multiple moderate signals
   6. Categorize newly found products
   ```

4. **Change Output Filename:**
   ```diff
   - Generate PHASEA_MANUAL_REPORT_YYYYMMDD.md
   + Generate MANUAL_REPORT_YYMMDDHHMM.md
   ```

5. **Add Two-Phase Output Structure:**
   ```markdown
   ## OUTPUT STRUCTURE
   
   Section 1: REVIEW CORRECTIONS
   - Products moved from X → Y
   - Pack calculations fixed
   - Profit recalculations
   
   Section 2: NEWLY DISCOVERED PRODUCTS
   - Gap analysis results
   - Products found via relaxed criteria
   - Pathway analysis
   
   Section 3: FINAL CONSOLIDATED REPORT
   - All products (original + corrections + new finds)
   - Summary: Original vs Updated counts
   ```

### To `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md`:

1. **Add Phase 0: Review Existing Report**
   ```markdown
   ## PHASE 0: REVIEW EXISTING REPORT (If Applicable)
   
   If you are reviewing a previously generated report rather than analyzing fresh source data:
   
   ### Step 0.1: Load Existing Report
   - Parse previously generated report
   - Extract all products by category
   
   ### Step 0.2: Validate Categorizations
   - Check each product against methodology
   - Identify miscategorizations
   
   ### Step 0.3: Create Correction List
   - Document errors found
   - Identify root causes
   ```

2. **Expand Phase 8 to Include Gap Analysis**
   ```markdown
   ## PHASE 8: REPORT REVIEW & GAP ANALYSIS
   
   ### Step 8A: Review Existing Report (if applicable)
   [Instructions for validation]
   
   ### Step 8B: Gap Analysis
   - Extract Row IDs from report
   - Compare against source data
   - Find missed products
   - Apply relaxed criteria
   ```

3. **Add Relaxed HIGHLY LIKELY Pathways**
   ```markdown
   ### Alternative Pathways to HIGHLY LIKELY:
   
   Pathway 1: Brand Match (existing)
   Pathway 2: High Keyword Overlap
   - ≥4 shared meaningful keywords + positive profit
   
   Pathway 3: High Title Similarity
   - ≥65% similarity + positive profit
   
   Pathway 4: Multiple Moderate Signals
   - ≥3 keywords + ≥35% similarity + sales ≥200 + profit >£2
   ```

---

## ✅ WHAT TO DO

**To align prompts with your expectations, you need to:**

1. **Completely rewrite** `MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_SKIP_BROWSER_v1.0.md` to be a **two-phase prompt**
2. **Add Phase 0** to the methodology guide for "Review Existing Report"
3. **Expand Phase 8** to include gap analysis methodology
4. **Define relaxed criteria** for finding missed HIGHLY LIKELY products
5. **Change output filename** to `MANUAL_REPORT_YYMMDDHHMM.md`

---

**Bottom Line:** Both prompts are designed for **fresh analysis of source data**, NOT for **reviewing an existing report + finding gaps**. They need significant restructuring to match your expectations.
