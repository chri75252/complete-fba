# PROMPT CORRECTION PLAN - FBA Manual Analysis

**Date:** 2026-01-05  
**Issue:** Misalignment between intended task and actual execution

---

## 🎯 CORE ISSUE IDENTIFIED

### What User WANTED (Initial Intent):
```
1. Take GENERATED REPORT (e.g., PHASEA_MANUAL_REPORT_20260102_081924.md)
2. Manually REVIEW that report's categorizations
3. GO BACK to SOURCE DATA (part_1_jan.xlsx) to find MISSED products
4. Generate UPDATED report with:
   - Corrected categorizations from review
   - Newly discovered products that were missed
```

### What Actually Happened (Reformulated Prompt):
```
1. Analyzed SOURCE DATA (part_1_jan.xlsx) directly
2. Generated FRESH report from scratch
3. Expanded brand detection (good!)
4. BUT: Did NOT review existing report or perform gap analysis
```

---

## 📊 GAP ANALYSIS: What Went Wrong

| Aspect | Expected Behavior | Actual Behavior | Impact |
|--------|------------------|-----------------|--------|
| **Input** | Existing generated report | Source Excel file | ❌ Wrong starting point |
| **Process** | Review → Validate → Find gaps | Fresh analysis | ❌ Duplicate work |
| **Output** | Updated report with fixes | New report | ❌ Lost context |
| **Gap Detection** | Explicit comparison | Implicit (expanded brands) | ⚠️ Partial success |

---

## 🔧 SUGGESTED FIXES (DIFF FORMAT)

### FIX 1: Clarify Input Sources

```diff
- **INPUT:** part_1_jan.xlsx (source data)
+ **PRIMARY INPUT:** Previously generated report (e.g., PHASEA_MANUAL_REPORT_20260102_081924.md)
+ **REFERENCE INPUT:** part_1_jan.xlsx (for gap analysis only)
```

### FIX 2: Define Two-Phase Process

```diff
# Task: Thorough Manual FBA Product Analysis

+ ## PHASE A: REVIEW EXISTING REPORT
+ 1. Load previously generated report: [REPORT_PATH]
+ 2. Review each categorized product against methodology guidelines
+ 3. Identify miscategorizations:
+    - Products in wrong category
+    - Incorrect pack size calculations
+    - Missed dimension traps
+ 4. Create correction list
+ 
+ ## PHASE B: GAP ANALYSIS FOR MISSED PRODUCTS
+ 1. Extract all Row IDs from existing report
+ 2. Compare against source data (part_1_jan.xlsx)
+ 3. Identify products NOT in report but should be:
+    - Has brand match but missed
+    - Has high profit but missed
+    - Has good title similarity but missed
+ 4. Categorize newly found products following methodology

- Execute Phases 1-4 and 6-7 from the methodology guide
+ Execute:
+ - PHASE A: Review existing report (Phases 3-4, 6-7)
+ - PHASE B: Gap analysis (Phases 1-2, then 3-4, 6-7 for new finds)
```

### FIX 3: Specify Output Structure

```diff
**OUTPUT:** Generate PHASEA_MANUAL_REPORT_YYYYMMDD.md following the report structure

+ **OUTPUT STRUCTURE:**
+ 
+ # PHASEA_MANUAL_REPORT_UPDATED_YYYYMMDD.md
+ 
+ ## Section 1: REVIEW CORRECTIONS
+ - Products moved from category X → category Y (with reasoning)
+ - Profit recalculations
+ - Pack size corrections
+ 
+ ## Section 2: NEWLY DISCOVERED PRODUCTS
+ - Products found in gap analysis
+ - Categorized following methodology
+ 
+ ## Section 3: FINAL CONSOLIDATED REPORT
+ - All products (original + corrections + newly found)
+ - Sorted by category and confidence
+ - Summary statistics comparing old vs new
```

### FIX 4: Add Explicit Gap Detection Logic

```diff
+ ## GAP DETECTION METHODOLOGY
+ 
+ ### Step 1: Extract Existing Coverage
+ ```python
+ # Extract all Row IDs from existing report
+ existing_rows = set()
+ for section in ["VERIFIED", "HIGHLY LIKELY", "NEEDS VERIFICATION", "FILTERED OUT"]:
+     existing_rows.update(extract_row_ids(report, section))
+ ```
+ 
+ ### Step 2: Identify Candidates from Source
+ ```python
+ # Load source data
+ df = pd.read_excel('part_1_jan.xlsx')
+ df['RowID'] = df.index + 1
+ 
+ # Find products NOT in existing report
+ missing_rows = df[~df['RowID'].isin(existing_rows)]
+ 
+ # Filter for high-value candidates
+ candidates = missing_rows[
+     (missing_rows['NetProfit'] > 1.0) |  # High profit
+     (missing_rows['Sales'] >= 100) |      # Good sales
+     (missing_rows['title_sim'] >= 0.35)   # Decent title match
+ ]
+ ```
+ 
+ ### Step 3: Categorize Found Products
+ Apply methodology Phases 3-4, 6-7 to candidates
```

### FIX 5: Clarify "Highly Likely" Guards Issue

```diff
+ ## ADDRESSING "HIGHLY LIKELY" RESTRICTIVE GUARDS
+ 
+ **User Concern:** "I believe your highly likely category used very restrictive guards"
+ 
+ ### Current Criteria (Too Restrictive):
+ ```python
+ # OLD: Requires exact brand match in KNOWN_BRANDS list
+ if brand_match and adj_profit > 0:
+     return 'HIGHLY_LIKELY'
+ ```
+ 
+ ### Proposed Relaxed Criteria:
+ ```python
+ # NEW: Multiple pathways to HIGHLY_LIKELY
+ 
+ # Path 1: Brand match (existing)
+ if brand_match and adj_profit > 0:
+     return 'HIGHLY_LIKELY'
+ 
+ # Path 2: High keyword overlap + title similarity
+ if keyword_overlap >= 4 and title_sim >= 0.45 and adj_profit > 0:
+     return 'HIGHLY_LIKELY'
+ 
+ # Path 3: Very high title similarity alone
+ if title_sim >= 0.65 and adj_profit > 0:
+     return 'HIGHLY_LIKELY'
+ 
+ # Path 4: Multiple weak signals combined
+ if keyword_overlap >= 3 and title_sim >= 0.35 and sales >= 200 and adj_profit > 2:
+     return 'HIGHLY_LIKELY'
+ ```
```

---

## 📝 CORRECTED PROMPT (FINAL VERSION)

### File: `MANUAL_REVIEW_AND_GAP_ANALYSIS_PROMPT.md`

```markdown
# Task: Manual Review & Gap Analysis of FBA Report

## OBJECTIVE
Review a previously generated FBA analysis report, correct any miscategorizations, and identify products that were missed in the initial analysis.

---

## INPUTS

| Input Type | File Path | Purpose |
|------------|-----------|---------|
| **PRIMARY** | Previously generated report | Report to review and correct |
| **REFERENCE** | `part_1_jan.xlsx` | Source data for gap analysis |
| **METHODOLOGY** | `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` | Categorization rules |

**Example:**
```
PRIMARY: RESERACH\REPORT\part_1_jan\opu v1.1\PHASEA_MANUAL_REPORT_20260102_081924.md
REFERENCE: RESERACH\REPORT\part_1_jan\part_1_jan.xlsx
```

---

## PHASE A: REVIEW EXISTING REPORT

### Step A1: Load Existing Report
1. Parse the existing report
2. Extract all products by category:
   - VERIFIED — RECOMMENDED
   - VERIFIED — FILTERED OUT
   - HIGHLY LIKELY — RECOMMENDED
   - HIGHLY LIKELY — FILTERED OUT
   - NEEDS VERIFICATION
   - FILTERED OUT

3. For each product, extract:
   - Row ID
   - Category assigned
   - Pack verdict
   - Adjusted profit
   - Key evidence

### Step A2: Validate Categorizations

For each product, check:

#### ✅ VERIFIED Products
- [ ] EAN truly matches (exact string comparison)
- [ ] Pack sizes correctly identified (check dimension traps)
- [ ] Adjusted profit correctly calculated
- [ ] Should NOT be here if: pack mismatch causes loss

#### ✅ HIGHLY LIKELY Products
- [ ] Brand truly present in both titles
- [ ] Product type matches
- [ ] No major variant differences (size, scent, color)
- [ ] Adjusted profit > 0

#### ✅ NEEDS VERIFICATION Products
- [ ] Has 1-2 blocking details preventing upgrade
- [ ] Details are actually confirmable
- [ ] Adjusted profit > 0

#### ✅ FILTERED OUT Products
- [ ] Clearly unprofitable OR clear mismatch
- [ ] Reason documented

### Step A3: Create Correction List

Document all errors found:

```markdown
## CORRECTIONS NEEDED

### Miscategorizations

| Row ID | Current Category | Should Be | Reason |
|--------|-----------------|-----------|--------|
| 1234 | HIGHLY LIKELY | NEEDS VERIFICATION | Brand doesn't actually match |
| 5678 | VERIFIED | FILTERED OUT | Adjusted profit = -£2.50 |
```

---

## PHASE B: GAP ANALYSIS FOR MISSED PRODUCTS

### Step B1: Identify Coverage Gaps

```python
# 1. Extract all Row IDs from existing report
existing_row_ids = set()
# Parse report and collect all Row IDs mentioned

# 2. Load source data
df = pd.read_excel('part_1_jan.xlsx')
df['RowID'] = df.index + 1

# 3. Find products NOT in existing report
not_analyzed = df[~df['RowID'].isin(existing_row_ids)]

print(f"Total rows in source: {len(df)}")
print(f"Rows in existing report: {len(existing_row_ids)}")
print(f"Rows NOT analyzed: {len(not_analyzed)}")
```

### Step B2: Filter for High-Value Candidates

Apply filters to `not_analyzed` DataFrame:

```python
candidates = not_analyzed[
    # Filter 1: Financial viability
    (
        (not_analyzed['NetProfit'] > 1.0) |
        (not_analyzed['ROI'] > 0.5)
    ) &
    # Filter 2: Sales volume
    (not_analyzed['bought_in_past_month'] >= 50) &
    # Filter 3: At least some match signal
    (
        (not_analyzed['EAN'] == not_analyzed['EAN_OnPage']) |
        (not_analyzed['title_sim'] >= 0.30) |
        (not_analyzed['keyword_overlap'] >= 2)
    )
]

print(f"High-value candidates found: {len(candidates)}")
```

### Step B3: Categorize Newly Found Products

For each candidate in `candidates`:

1. **Check EAN Match** (Phase 2)
   - If exact EAN match → Proceed to VERIFIED logic
   
2. **Check Brand Match** (Phase 3)
   - Extract brand from both titles
   - If brand matches → Proceed to HIGHLY LIKELY logic
   
3. **Check Title Similarity** (Phase 3)
   - Calculate title similarity
   - If sim >= 0.45 → Proceed to HIGHLY LIKELY logic
   - If sim >= 0.35 → Proceed to NEEDS VERIFICATION logic

4. **Pack Size Detection** (Phase 4)
   - Extract pack quantities
   - Calculate RSU
   - Avoid dimension traps

5. **Adjusted Profit** (Phase 6)
   - Calculate adjusted profit
   - If ≤ 0 → FILTERED OUT

6. **Final Category** (Phase 7)
   - Apply decision tree from methodology

### Step B4: Relaxed "HIGHLY LIKELY" Criteria

**IMPORTANT:** Use MULTIPLE pathways to HIGHLY LIKELY (not just brand match):

```python
def categorize_relaxed(row):
    # Pathway 1: Brand match
    if brand_matches(row) and adjusted_profit > 0:
        return 'HIGHLY_LIKELY'
    
    # Pathway 2: Strong keyword overlap
    if keyword_overlap >= 4 and title_sim >= 0.45 and adjusted_profit > 0:
        return 'HIGHLY_LIKELY'
    
    # Pathway 3: Very high title similarity
    if title_sim >= 0.65 and adjusted_profit > 0:
        return 'HIGHLY_LIKELY'
    
    # Pathway 4: Multiple moderate signals
    if (keyword_overlap >= 3 and 
        title_sim >= 0.40 and 
        sales >= 200 and 
        adjusted_profit > 2):
        return 'HIGHLY_LIKELY'
    
    # Pathway 5: Moderate match with high value
    if (title_sim >= 0.35 and 
        adjusted_profit > 5 and 
        sales >= 100):
        return 'NEEDS_VERIFICATION'  # Worth manual check
    
    # Otherwise
    if adjusted_profit <= 0:
        return 'FILTERED_OUT'
    else:
        return None  # Don't report
```

---

## EXECUTION INSTRUCTIONS

### Skip Browser Verification (Phase 5)
```markdown
✅ Execute: Phases 1-4, 6-7
⏭️ SKIP: Phase 5 (Browser Verification)

Note: Browser checks should be done later for top candidates
```

### Apply Appendix C Reasoning

For EVERY product categorized, apply explicit reasoning:

**Dimension Traps:**
- `9x9 inch` → Tray size, NOT 81-pack
- `15 x 5.5 x 5.5 cm` → Dimensions (L×W×H), NOT pack
- `9 LED` → Specification, NOT 9-pack

**Pack Detection:**
- `(4 x 50)` → 4 packs of 50 = 200 total, RSU = 4
- `3 x 400ml` → 3 bottles of 400ml, RSU = 3 (NOT 1200!)

**Capacity Tolerance:**
- `407ml` vs `408ml` → Within 15% → MATCH ✅
- `407ml` vs `600ml` → Exceeds 15% → MISMATCH ❌

---

## OUTPUT STRUCTURE

Generate: `PHASEA_MANUAL_REPORT_UPDATED_YYYYMMDD.md`

### Template:

```markdown
# PHASEA MANUAL REPORT - UPDATED

**Generated:** YYYY-MM-DD  
**Original Report:** [path to reviewed report]  
**Source Data:** part_1_jan.xlsx  

---

## SECTION 1: REVIEW CORRECTIONS

### 1.1 Categorization Changes

| Row ID | Original Category | New Category | Reason |
|--------|------------------|--------------|--------|
| ... | ... | ... | ... |

### 1.2 Profit Recalculations

| Row ID | SupplierTitle | Original Pack Verdict | Corrected Pack Verdict | Original Profit | Corrected Profit |
|--------|---------------|----------------------|----------------------|----------------|-----------------|
| ... | ... | ... | ... | ... | ... |

### 1.3 Summary of Corrections
- Total corrections: X
- Category changes: Y
- Profit adjustments: Z

---

## SECTION 2: NEWLY DISCOVERED PRODUCTS

### 2.1 Gap Analysis Summary
- Total rows in source: 2,402
- Rows in original report: [count]
- Rows analyzed in gap check: [count]
- High-value candidates found: [count]
- Products added to final report: [count]

### 2.2 Newly Found VERIFIED Products

[Table with same structure as original report]

### 2.3 Newly Found HIGHLY LIKELY Products

[Table with same structure as original report]

### 2.4 Newly Found NEEDS VERIFICATION Products

[Table with same structure as original report]

---

## SECTION 3: FINAL CONSOLIDATED REPORT

### Summary Counts (Original vs Updated)

| Category | Original | Added | Removed | Final |
|----------|---------|-------|---------|-------|
| VERIFIED — RECOMMENDED | X | +A | -B | Y |
| VERIFIED — FILTERED OUT | X | +A | -B | Y |
| HIGHLY LIKELY — RECOMMENDED | X | +A | -B | Y |
| NEEDS VERIFICATION | X | +A | -B | Y |
| **TOTAL MATCHED** | X | +A | -B | Y |

### 3.1 VERIFIED — RECOMMENDED (Final)

[Consolidated table: original + corrections + new finds]

### 3.2 HIGHLY LIKELY — RECOMMENDED (Final)

[Consolidated table: original + corrections + new finds]

### 3.3 NEEDS VERIFICATION (Final)

[Consolidated table: original + corrections + new finds]

---

## SECTION 4: ANALYSIS NOTES

### 4.1 Why Products Were Missed Initially

- Brand not in original KNOWN_BRANDS list: [count]
- Title similarity below threshold: [count]
- Keyword overlap not detected: [count]
- Other: [count]

### 4.2 Pathway Analysis

**How newly found products qualified:**

| Pathway | Count | Example |
|---------|-------|---------|
| Brand match | X | ... |
| High keyword overlap (≥4) | Y | ... |
| High title sim (≥65%) | Z | ... |
| Multiple moderate signals | W | ... |

---

*Report generated: [timestamp]*  
*Methodology: FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md*  
*Analysis: Manual Review + Gap Analysis*
```

---

## EXECUTION PROMPT (FOR USER)

Save as: `EXECUTE_MANUAL_REVIEW.txt`

```markdown
# EXECUTE: Manual Review & Gap Analysis

## STEP 1: Specify Inputs

**Report to Review:**
```
RESERACH\REPORT\part_1_jan\opu v1.1\PHASEA_MANUAL_REPORT_20260102_081924.md
```

**Source Data for Gap Analysis:**
```
RESERACH\REPORT\part_1_jan\part_1_jan.xlsx
```

**Methodology Guide:**
```
RESERACH\REPORT\PROMPTS GUIDES\ANTI-GRAVITY\guides\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
```

---

## STEP 2: Execute Task

Follow: `MANUAL_REVIEW_AND_GAP_ANALYSIS_PROMPT.md`

**IMPORTANT SETTINGS:**
- ✅ Execute Phases 1-4, 6-7
- ⏭️ SKIP Phase 5 (Browser Verification)
- ✅ Apply ALL Appendix C reasoning examples
- ✅ Use RELAXED "HIGHLY LIKELY" criteria (multiple pathways)

---

## STEP 3: Output

Generate: `PHASEA_MANUAL_REPORT_UPDATED_20260105.md`

Location: `RESERACH\REPORT\part_1_jan\opu v1.1\`
```
