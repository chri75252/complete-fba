# EXECUTE: Manual Review & Gap Analysis

**Quick Reference Prompt** - Use this to execute the analysis

---

## 📥 INPUTS

**Report to Review:**
```
RESERACH\REPORT\part_1_jan\opu v1.1\PHASEA_MANUAL_REPORT_20260102_081924.md
```

**Source Data (for finding missed products):**
```
RESERACH\REPORT\part_1_jan\part_1_jan.xlsx
```

**Methodology Guide:**
```
RESERACH\REPORT\PROMPTS GUIDES\ANTI-GRAVITY\guides\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
```

---

## 🎯 TASK

**Follow the detailed methodology in:**
```
RESERACH\REPORT\PROMPTS GUIDES\MANUAL_REVIEW_AND_GAP_ANALYSIS_PROMPT.md
```

### TWO-PHASE PROCESS:

**PHASE A: Review Existing Report**
1. Load the generated report (PHASEA_MANUAL_REPORT_20260102_081924.md)
2. Validate each product's categorization against methodology
3. Check for:
   - Dimension traps (9X9IN = size, not pack)
   - Pack size calculation errors
   - Adjusted profit errors
4. Create list of corrections needed

**PHASE B: Gap Analysis**
1. Extract all Row IDs from existing report
2. Compare against source data (part_1_jan.xlsx - all 2,402 rows)
3. Find products that were MISSED
4. Use **RELAXED HIGHLY LIKELY criteria**:
   - Pathway 1: Brand match
   - Pathway 2: Keyword overlap ≥ 4
   - Pathway 3: Title similarity ≥ 65%
   - Pathway 4: Multiple moderate signals
5. Categorize newly found products

---

## ⚙️ SETTINGS

```yaml
Execute Phases: 1-4, 6-7
SKIP Phase: 5 (Browser Verification) ⏭️

Apply from Appendix C:
  ✅ All dimension trap examples
  ✅ All pack detection patterns
  ✅ Explicit reasoning chains
  ✅ Capacity tolerance (≤15% = match)

Use RELAXED criteria:
  ✅ Multiple pathways to HIGHLY LIKELY (not just brand)
  ✅ Keyword overlap detection
  ✅ Title similarity thresholds
```

---

## 📤 OUTPUT

**Generate:**
```
PHASEA_MANUAL_REPORT_UPDATED_20260105.md
```

**Save to:**
```
RESERACH\REPORT\part_1_jan\opu v1.1\
```

**Report Structure:**
- Section 1: Review Corrections (miscategorizations fixed)
- Section 2: Newly Discovered Products (gap analysis results)
- Section 3: Final Consolidated Report (combined)
- Section 4: Analysis Notes (why products were missed)

---

## 🔑 KEY REMINDERS

### Dimension Traps to Avoid:
```
❌ "9x9 inch" → Tray size, NOT 81-pack
❌ "15 x 5.5 x 5.5 cm" → Dimensions, NOT pack of 15
❌ "9 LED" → LED count (spec), NOT 9-pack
❌ "26CM" → Diameter, NOT 26-pack
```

### Pack Detection Patterns:
```
✅ "(4 x 50)" → 4 packs × 50 = 200 total, RSU = 4
✅ "3 x 400ml" → 3 bottles, RSU = 3 (NOT 1200!)
✅ "PK5" → 5-pack
✅ "20PCE" → 20 pieces
```

### HIGHLY LIKELY Pathways (Use ALL, not just brand):
```
1. Brand match + product match
2. Keyword overlap ≥ 4
3. Title similarity ≥ 65%
4. Keyword ≥3 + title sim ≥40% + sales ≥200 + profit >£2
5. Title sim ≥35% + profit >£5 + sales ≥100 → NEEDS VERIFICATION
```

---

**READY TO EXECUTE** ✅
