# MANUAL REVIEW & GAP ANALYSIS PROMPT

**Purpose:** Review a previously generated FBA report, correct categorizations, and find missed products  
**Version:** 1.0  
**Date:** 2026-01-05

---

## 📥 INPUTS REQUIRED

### Primary Input (What to Review):
```
Previously Generated Report: 
RESERACH\REPORT\part_1_jan\opu v1.1\PHASEA_MANUAL_REPORT_20260102_081924.md
```

### Reference Input (For Gap Analysis):
```
Source Data: 
RESERACH\REPORT\part_1_jan\part_1_jan.xlsx
```

### Methodology Guide:
```
RESERACH\REPORT\PROMPTS GUIDES\ANTI-GRAVITY\guides\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
```

---

## 🎯 TASK OVERVIEW

This is a **TWO-PHASE** process:

### PHASE A: Review Existing Report
- Validate each product's categorization
- Check pack size calculations
- Verify adjusted profit calculations
- Identify miscategorizations
- Create correction list

### PHASE B: Gap Analysis
- Extract Row IDs from existing report
- Compare against source data (part_1_jan.xlsx)
- Find products that were MISSED
- Categorize newly found products
- Use RELAXED criteria (multiple pathways to HIGHLY LIKELY)

---

## 📋 PHASE A: REVIEW EXISTING REPORT

### Step A1: Load and Parse Report

Load: `PHASEA_MANUAL_REPORT_20260102_081924.md`

Extract all products from these sections:
- ✅ VERIFIED — RECOMMENDED
- ✅ VERIFIED — FILTERED OUT
- ✅ HIGHLY LIKELY — RECOMMENDED
- ✅ HIGHLY LIKELY — FILTERED OUT
- ✅ NEEDS VERIFICATION
- ✅ FILTERED OUT (if present)

For each product, note:
```
- Row ID (if mentioned)
- Supplier Title
- Amazon Title
- Current Category
- Pack Verdict
- Adjusted Profit
- Key Evidence
- Filter Reason (if applicable)
```

### Step A2: Validate Each Product

Apply methodology from `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` (Phases 3-4, 6-7):

#### For VERIFIED Products:
```
Check:
□ EAN exactly matches between supplier and Amazon
□ Pack sizes correctly extracted (watch for dimension traps!)
□ "9X9IN" identified as SIZE not 81-pack
□ "15 x 5.5 x 5.5 cm" identified as dimensions not pack
□ Adjusted profit correctly calculated
□ If RSU > 1, profit adjustment applied

Action:
- If adjusted profit ≤ 0 → Move to FILTERED OUT
- If pack mismatch not handled → Recalculate
- If dimension trap missed → Correct pack verdict
```

#### For HIGHLY LIKELY Products:
```
Check:
□ Brand truly present in BOTH titles
□ Product type matches
□ No major variant differences (e.g., scent, color, size)
□ Adjusted profit > 0
□ Pack sizes make sense

Action:
- If brand doesn't actually match → Move to NEEDS VERIFICATION or remove
- If profit calculation wrong → Recalculate
```

#### For NEEDS VERIFICATION Products:
```
Check:
□ Has 1-2 specific blocking details
□ Details are confirmable
□ Adjusted profit > 0

Action:
- If enough evidence exists → Upgrade to HIGHLY LIKELY
- If clearly doesn't match → Move to FILTERED OUT
```

### Step A3: Create Corrections List

Document format:
```markdown
## CORRECTIONS FROM REVIEW

| Row ID | Supplier Title | Current Cat | Should Be | Reason |
|--------|---------------|-------------|-----------|--------|
| 1234 | EXAMPLE PRODUCT | VERIFIED | FILTERED OUT | Adjusted profit = -£2.50 (pack 1→10) |
| 5678 | ANOTHER PRODUCT | HIGHLY LIKELY | NEEDS VERIFICATION | Brand doesn't match; only 2 keyword overlap |
```

---

## 🔍 PHASE B: GAP ANALYSIS FOR MISSED PRODUCTS

### Step B1: Extract Coverage from Existing Report

```python
# Pseudocode
existing_row_ids = set()

# Parse the existing report and extract all mentioned Row IDs
# (These are the products that WERE analyzed)

for section in report_sections:
    for product in section:
        if 'Row' mentioned or identifiable:
            existing_row_ids.add(row_id)

print(f"Products in existing report: {len(existing_row_ids)}")
```

### Step B2: Load Source Data and Find Gaps

```python
import pandas as pd

# Load source
df = pd.read_excel('part_1_jan.xlsx')
df['RowID'] = df.index + 1  # Create Row IDs

# Find products NOT in existing report
not_in_report = df[~df['RowID'].isin(existing_row_ids)]

print(f"Total rows in source: {len(df)}")
print(f"Analyzed in report: {len(existing_row_ids)}")
print(f"NOT analyzed: {len(not_in_report)}")
```

### Step B3: Filter for High-Value Candidates

**Apply these filters to find products worth reviewing:**

```python
candidates = not_in_report[
    # Financial filter
    (
        (not_in_report['NetProfit'] > 0.50) |  # Some profit
        (not_in_report['ROI'] > 0.3)           # Or decent ROI
    ) &
    
    # Sales filter
    (not_in_report['bought_in_past_month'] >= 50) &  # Minimum sales
    
    # Match signal filter (at least ONE of these)
    (
        # Has EAN match
        (not_in_report['EAN'].notna() & 
         not_in_report['EAN_OnPage'].notna() &
         (not_in_report['EAN'] == not_in_report['EAN_OnPage'])) |
        
        # Or has reasonable title match potential
        # (This requires calculating title similarity)
        # For now, use keyword overlap or other heuristic
    )
]

print(f"High-value candidates to review: {len(candidates)}")
```

### Step B4: Categorize Found Products (RELAXED CRITERIA)

**CRITICAL:** Use MULTIPLE pathways to HIGHLY LIKELY, not just brand match!

For each candidate product:

#### Pathway 1: EAN Match
```
If supplier EAN == Amazon EAN (exact):
  → Check pack sizes
  → Calculate adjusted profit
  → If adjusted profit > 0: VERIFIED
  → If adjusted profit ≤ 0: FILTERED OUT
```

#### Pathway 2: Brand Match
```
If brand present in both titles:
  AND product type matches:
  AND adjusted profit > 0:
  → HIGHLY LIKELY
```

#### Pathway 3: High Keyword Overlap
```
Calculate keyword overlap (shared meaningful words)

If keyword_overlap >= 4:
  AND adjusted profit > 0:
  → HIGHLY LIKELY
  
Example:
  Supplier: "QUEST ESPRESSO COFFEE MACHINE WITH MILK FROTHER"
  Amazon: "Quest 36569 Espresso Coffee Machine With Milk Frother"
  Keywords: {QUEST, ESPRESSO, COFFEE, MACHINE, MILK, FROTHER} = 6 overlap
  → HIGHLY LIKELY
```

#### Pathway 4: High Title Similarity
```
Calculate title similarity (SequenceMatcher ratio)

If title_similarity >= 0.65:
  AND adjusted profit > 0:
  → HIGHLY LIKELY
  
If title_similarity >= 0.45:
  AND keyword_overlap >= 3:
  AND adjusted profit > 0:
  → HIGHLY LIKELY
```

#### Pathway 5: Multiple Moderate Signals
```
If ALL of these:
  - keyword_overlap >= 3
  - title_similarity >= 0.35
  - sales >= 100
  - adjusted_profit > 1.50
  → HIGHLY LIKELY
  
Example:
  Decent title match + good sales + profitable = worth including
```

#### Pathway 6: Needs Verification
```
If:
  - title_similarity >= 0.35 OR keyword_overlap >= 3
  - adjusted_profit > 0.50
  - sales >= 50
  - Has 1-2 confirmable blocking details
  → NEEDS VERIFICATION
```

### Step B5: Apply Pack Detection (Watch for Traps!)

**From Appendix C of Methodology Guide:**

#### Dimension Traps - DO NOT TREAT AS PACK:
```
❌ "9x9 inch" → This is TRAY SIZE (9" × 9"), NOT 81-pack
❌ "15 x 5.5 x 5.5 cm" → DIMENSIONS (L×W×H), NOT pack of 15
❌ "9 LED" → Number of LEDs (spec), NOT 9-pack
❌ "4FT 36W" → Length + wattage (spec), NOT pack
❌ "26CM" → Diameter/size, NOT 26-pack
```

#### Correct Pack Detection:
```
✅ "PK5" or "5 PACK" → 5-pack
✅ "20PCE" or "20 PCS" → 20 pieces
✅ "(4 x 50)" → 4 packs of 50 = 200 total, RSU = 4
✅ "3 x 400ml" → 3 bottles of 400ml, RSU = 3 (NOT 1200!)
✅ "SET OF 2" → 2-pack
```

### Step B6: Calculate Adjusted Profit

```python
def calculate_adjusted_profit(supplier_price, selling_price, net_profit, rsu):
    """
    RSU = Required Supplier Units
    
    If Amazon sells 10-pack but supplier sells singles:
    RSU = 10
    
    Adjusted Profit = NetProfit - (SupplierPrice × (RSU - 1))
    """
    if rsu <= 1:
        return net_profit
    else:
        adjustment = supplier_price * (rsu - 1)
        return net_profit - adjustment
```

**Example:**
```
Product: TIDYZ DOGGY BAGS
Supplier: 50 bags
Amazon: "(4 x 50)" = 200 bags
RSU = 200 / 50 = 4

Supplier Price: £0.67
Net Profit (original): £0.74

Adjusted Profit = £0.74 - (£0.67 × (4-1))
                = £0.74 - (£0.67 × 3)
                = £0.74 - £2.01
                = -£1.27  ← FILTERED OUT (loss)
```

---

## 📤 OUTPUT STRUCTURE

Generate: `PHASEA_MANUAL_REPORT_UPDATED_YYYYMMDD.md`

### Report Template:

```markdown
# PHASEA MANUAL REPORT - UPDATED

**Generated:** 2026-01-05  
**Original Report Reviewed:** PHASEA_MANUAL_REPORT_20260102_081924.md  
**Source Data:** part_1_jan.xlsx  
**Total Rows in Source:** 2,402  

---

## SUMMARY OF CHANGES

| Metric | Original Report | After Review | Change |
|--------|----------------|--------------|--------|
| VERIFIED — RECOMMENDED | X | Y | +/- Z |
| HIGHLY LIKELY — RECOMMENDED | X | Y | +/- Z |
| NEEDS VERIFICATION | X | Y | +/- Z |
| **TOTAL MATCHED** | X | Y | +/- Z |

---

## SECTION 1: REVIEW CORRECTIONS

### 1.1 Products Recategorized

| Row | Supplier Title | Old Category | New Category | Reason |
|-----|---------------|--------------|--------------|--------|
| ... | ... | ... | ... | Dimension trap: "9X9IN" is size, not pack |
| ... | ... | ... | ... | Pack adjustment: RSU=4 → profit = -£1.27 |

### 1.2 Pack Verdict Corrections

| Row | Supplier Title | Old Pack Verdict | New Pack Verdict | Impact |
|-----|---------------|-----------------|-----------------|--------|
| ... | ... | "1:1 Match" | "BUNDLE (10x) - LOSS" | Moved to FILTERED OUT |

### 1.3 Profit Recalculations

[Table showing corrected profit calculations]

---

## SECTION 2: NEWLY DISCOVERED PRODUCTS

### 2.1 Gap Analysis Summary

```
Total rows in source data: 2,402
Rows in original report: [count]
Rows NOT in original report: [count]
High-value candidates reviewed: [count]
Products added to final report: [count]
```

### 2.2 Why These Were Missed Initially

| Reason | Count | Example |
|--------|-------|---------|
| Brand not in original KNOWN_BRANDS | X | QUEST, MOKATE, FALCON |
| Relaxed criteria (keyword overlap) | Y | High keyword overlap but no exact brand |
| Title similarity threshold | Z | Sim between 45-65% |

### 2.3 Pathway Analysis (How Found Products Qualified)

| Pathway | Count | Example Row IDs |
|---------|-------|----------------|
| Pathway 2: Brand match | X | ... |
| Pathway 3: Keyword overlap ≥4 | Y | ... |
| Pathway 4: High title sim ≥65% | Z | ... |
| Pathway 5: Multiple moderate signals | W | ... |

### 2.4 Newly Found VERIFIED Products

[Standard report table format]

### 2.5 Newly Found HIGHLY LIKELY Products

[Standard report table format]

### 2.6 Newly Found NEEDS VERIFICATION Products

[Standard report table format]

---

## SECTION 3: FINAL CONSOLIDATED REPORT

### 3.1 VERIFIED — RECOMMENDED (count=X)

**Products with exact EAN match + positive adjusted profit**

[Combined table: original + corrections + new finds]

### 3.2 VERIFIED — FILTERED OUT (count=X)

**Products with exact EAN match BUT pack causes loss**

[Combined table]

### 3.3 HIGHLY LIKELY — RECOMMENDED (count=X)

**Products with brand/title match + positive adjusted profit**

[Combined table: original + corrections + new finds]

### 3.4 NEEDS VERIFICATION (count=X)

**Products where 1-2 confirmable details would upgrade match**

[Combined table]

### 3.5 FILTERED OUT (count=X)

**Products with confirmed mismatch or negative profit**

[Combined table]

---

## SECTION 4: DIMENSION TRAPS AVOIDED

[Table showing patterns correctly identified as SIZE not PACK]

---

## SECTION 5: RECONCILIATION

| Metric | Value |
|--------|-------|
| Total Input Rows | 2,402 |
| Products in Original Report | X |
| Corrections Applied | Y |
| Newly Found Products | Z |
| Final Total Matched | W |

---

*Analysis: Manual Review + Gap Analysis*  
*Methodology: FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md*  
*Relaxed HIGHLY LIKELY criteria applied*
```

---

## 🚫 WHAT TO SKIP

**Phase 5: Browser Verification**
- ⏭️ SKIP all browser/online searches
- ✅ Note products that WOULD benefit from browser check
- 💡 Mark for future manual verification

---

## ⚙️ EXECUTION SETTINGS

```yaml
Phases to Execute:
  - Phase 1: Data Extraction (for gap analysis)
  - Phase 2: EAN Match Analysis (for new products)
  - Phase 3: Title-Based Verification (for review + new products)
  - Phase 4: Pack Size Detection (for review + new products)
  - Phase 6: Adjusted Profit Calculation (for review + new products)
  - Phase 7: Final Categorization (for review + new products)

Phases to Skip:
  - Phase 5: Browser Verification ⏭️

Apply from Appendix C:
  - ✅ All dimension trap examples (C.1.2, C.1.3)
  - ✅ All pack detection examples
  - ✅ All reasoning chains (C.1-C.4)
  - ✅ Capacity tolerance rules (≤15% is match)
```

---

## 📊 QUALITY CHECKS

Before finalizing report, verify:

### ✅ Review Phase Checklist
- [ ] Every product in original report was reviewed
- [ ] All miscategorizations documented
- [ ] All pack verdicts validated
- [ ] All adjusted profits recalculated where needed

### ✅ Gap Analysis Checklist
- [ ] Extracted all Row IDs from original report
- [ ] Compared against all 2,402 rows in source
- [ ] Applied multiple pathways for HIGHLY LIKELY
- [ ] Used relaxed criteria (not just brand match)
- [ ] Avoided dimension traps on new products
- [ ] Calculated adjusted profit for all new products

### ✅ Output Checklist
- [ ] Summary shows: Original vs Updated counts
- [ ] Section 1: All corrections documented
- [ ] Section 2: All newly found products listed with pathway
- [ ] Section 3: Final consolidated report complete
- [ ] All tables formatted correctly
- [ ] Reconciliation adds up

---

**END OF PROMPT**
