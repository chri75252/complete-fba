# PROMPT FIXES PLAN v4.2
## For: FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md

**Created:** 2026-01-01
**Purpose:** Address two critical issues causing LLM misinterpretation and inconsistent categorization

---

## 📋 SUMMARY OF ISSUES TO FIX

| # | Issue | Impact | Location(s) |
|---|-------|--------|-------------|
| 1 | Pre-filtered data references are confusing | LLMs may try to re-filter already-filtered data | A3, A4, V2, V3, lines 27-30, 94, 103-105, 263-266 |
| 2 | NEEDS VERIFICATION criteria too vague | LLMs interpret "1-2 confirmable details" too conservatively, missing valid candidates | Lines 19, 78, 95, 256-278 |
| 3 | Pack parsing lacks supplier-specific calibration | LLMs misread compact units (e.g., `2PC`, `5PACK`) and dimension suffixes (`40CM`, `500ML`) as pack counts | Stage 4/Stage 6 pack rules + supplier preflight step |

---

## 🔧 FIX #1: ACKNOWLEDGE PRE-FILTERING CONSISTENTLY

### Problem Statement:
The prompt currently contains acceptance tests (A3, A4) and verification checks (V2, V3) that instruct the agent to filter out Sales=0 and NetProfit≤0 items. However, Line 4 now states that input data is **already pre-filtered**. This creates confusion:
- LLMs may waste effort re-checking conditions that are already guaranteed
- Worse: LLMs may misinterpret remaining items as "failed pre-filtering" despite being valid

### Current Text (Lines 27-30):
```markdown
- A3. You do NOT output ANY non-sellable items in the **recommendation tables**: **Sales must be > 0** for every row that appears in VERIFIED or HIGHLY LIKELY tables.
  - However, if Sales = 0 but match confidence is high (exact EAN or strong title match), route to **NEEDS VERIFICATION** section, do NOT silently drop.
- A4. You do NOT output ANY non-profitable items in the **recommendation tables**: **NetProfit must be > 0** AND **Profit-after-pack-sanity must be > 0** for every row in VERIFIED or HIGHLY LIKELY.
  - If Adjusted Profit ≤ 0 after pack calculation → Route to FILTERED OUT, NOT NEEDS VERIFICATION.
```

### Replacement Text (Lines 27-30):
```markdown
- A3. **PRE-FILTERED ACKNOWLEDGMENT:** The input data has already been pre-filtered to remove rows with Sales = 0 and NetProfit ≤ 0. 
  - You should NOT encounter Sales = 0 or NetProfit ≤ 0 rows in the input.
  - Your focus is on pack-adjusted profitability: If **Adjusted Profit ≤ 0** after pack calculation → Route to **FILTERED OUT** (not NEEDS VERIFICATION).
- A4. **POST-ANALYSIS PROFITABILITY CHECK:** For VERIFIED and HIGHLY LIKELY tables, verify that:
  - **Profit-after-pack-sanity must be > 0** (adjusted profit considering Required Supplier Units).
  - If pack mismatch causes Adjusted Profit ≤ 0 → Route to FILTERED OUT with explicit reason.
```

---

### Current Text (Lines 94-95):
```markdown
   - Recommendation tables (VERIFIED, HIGHLY LIKELY) enforce Sales>0, NetProfit>0, Profit-after-pack-sanity>0.
   - NEEDS VERIFICATION contains ONLY items where 1-2 confirmable details would upgrade the match.
```

### Replacement Text (Lines 94-95):
```markdown
   - Recommendation tables (VERIFIED, HIGHLY LIKELY) require positive Adjusted Profit (profit-after-pack-sanity).
   - NEEDS VERIFICATION contains items matching specific inclusion criteria (see NEEDS VERIFICATION section).
```

---

### Current Text (Lines 103-105):
```markdown
- V2. Every listed row in **VERIFIED and HIGHLY LIKELY** tables has Sales>0 and NetProfit>0.
- V3. Every listed row in **VERIFIED and HIGHLY LIKELY** tables has profit-after-pack-sanity > 0.
  - Uncertain pack math → Route to NEEDS VERIFICATION (not excluded).
```

### Replacement Text (Lines 103-105):
```markdown
- V2. Every listed row in **VERIFIED and HIGHLY LIKELY** tables has positive **Adjusted Profit** (profit-after-pack-sanity > 0).
  - Note: Input data is pre-filtered for Sales > 0 and NetProfit > 0, so focus on pack-adjusted profitability.
- V3. Uncertain pack math where Adjusted Profit outcome is unclear → Route to NEEDS VERIFICATION (not excluded).
```

---

### Current Text (Lines 263-266):
```markdown
2. **Financial Metrics are in "Realistic Range"**
   - **Net Profit > £0.50** (worth the verification effort)
   - **ROI > 15%** (meaningful return)
   - **Sales > 0** (evidence of market demand) - OR Sales = 0 with very strong title match
```

### Replacement Text (Lines 263-266):
```markdown
2. **Financial Metrics are in "Actionable Range"**
   - **Adjusted Profit > £0** (still profitable after any pack adjustments)
   - **ROI > 15%** (meaningful return) — use as guidance, not hard filter
   - Note: Input is pre-filtered; all rows already have Sales > 0 and NetProfit > 0
```

---

## 🔧 FIX #2: CLARIFY "NEEDS VERIFICATION" WITH CONCRETE EXAMPLES

### Problem Statement:
The current phrasing "1-2 confirmable details that would upgrade to HIGHLY LIKELY" is too abstract. LLMs are interpreting this as:
- **Too conservative:** Requiring extremely high evidence before including
- **Vague threshold:** What exactly counts as "1-2 confirmable details"?

One LLM stated: *"the remaining rows generally lacked enough title-anchored evidence (or did not meet the profitability/ROI thresholds) to be 'upgradeable by 1–2 checks' without risking false positives."*

This indicates the LLM set an impossibly high bar because it didn't understand what scenarios qualify.

### Current Text (Lines 19):
```markdown
- NEEDS VERIFICATION is **highly selective**: only items with 1-2 confirmable details that would upgrade to HIGHLY LIKELY.
```

### Replacement Text (Lines 19):
```markdown
- NEEDS VERIFICATION is **selective but practical**: include items where confirming ONE of the following would upgrade to HIGHLY LIKELY: brand presence, pack count, product variant (size/color/scent), or model number.
```

---

### Current Text (Lines 77-78):
```markdown
- Prioritize **quality over quantity** in NEEDS VERIFICATION.
- Only include rows where confirmation of 1-2 specific details would upgrade to HIGHLY LIKELY.
```

### Replacement Text (Lines 77-78):
```markdown
- NEEDS VERIFICATION should capture **potentially valid matches** requiring minimal confirmation.
- Include rows where confirming ONE of: brand name on packaging, exact pack count, or correct variant would upgrade to HIGHLY LIKELY.
```

---

### Current Text (Lines 256-278) - COMPLETE REWRITE:

**Current:**
```markdown
### **NEEDS VERIFICATION (v4.1 HIGHLY SELECTIVE)**
**ONLY include rows where ALL of the following are TRUE:**
1. **Match is Plausible but Missing 1-2 Confirmable Details**
   - Brand appears in one title but not the other
   - Size/variant description is present but slightly ambiguous
   - EAN mismatch but titles strongly align
   - Model number not visible but product type matches
2. **Financial Metrics are in "Realistic Range"**
   - **Net Profit > £0.50** (worth the verification effort)
   - **ROI > 15%** (meaningful return)
   - **Sales > 0** (evidence of market demand) - OR Sales = 0 with very strong title match
3. **Confirmation Would LIKELY Result in HIGHLY LIKELY or VERIFIED**
   - The "gap" is just packaging confirmation, not fundamental product mismatch
   - Example: Same product, different EAN (manufacturer rebrand)
   - Example: Brand in supplier title, generic description in Amazon title
**DO NOT include in NEEDS VERIFICATION if:**
- Adjusted Profit ≤ 0 (negative profit) → Route to FILTERED OUT
- Brand mismatch with generic competitor match → Too risky, do not include
- Capacity difference >50% (e.g., 150ml vs 750ml) → Route to FILTERED OUT
**Key Question for NEEDS VERIFICATION:**
> "If I could verify ONE specific detail (brand on packaging, exact pack count, model number), would I confidently buy this product?"
> - If YES → Include in NEEDS VERIFICATION
> - If NO (would need multiple confirmations or seems unlikely) → Do NOT include
```

**Replacement:**
```markdown
### **NEEDS VERIFICATION (v4.2 PRACTICAL SELECTIVE)**

**PURPOSE:** Capture potentially valid matches where confirming ONE specific detail would upgrade to HIGHLY LIKELY. This category is a "holding zone" for promising-but-incomplete matches.

**INCLUDE in NEEDS VERIFICATION when the row matches one of these SPECIFIC SCENARIOS:**

| Scenario | What's Present | What's Missing | Example |
|----------|----------------|----------------|---------|
| **A. Brand Mismatch** | Similar product descriptions | Brand name differs or missing in one title | "PRIMA MULTI SHOWERHEAD CHROME" vs "Lara Multi Spray Shower Head Chrome" |
| **B. Pack Ambiguity** | Brand match + product type match | Pack count unclear (e.g., "3PCS" could mean 3 items or 1 set of 3) | "FAIRY DISH BRUSH & REFILLS 3PCS" vs "Fairy Soap Dispensing Dish Brush" |
| **C. Variant Unclear** | Brand match + product type match | Size/color/scent not confirmable from titles | "PAN AROMA CANDLE 85G" vs "Pan Aroma Decorative Holder & Scented Candle" |
| **D. Model Discrepancy** | Brand match + product type match | Model numbers differ or one is missing | "AMTECH TROWEL 6" vs "Amtech G0230 Pointing Trowel" |
| **E. Capacity Tolerance** | Brand match + product type match | Capacity difference 10-25% (within tolerance zone) | "BOWL 4 LITRE" vs "Bowl 4.1L" |
| **F. EAN Mismatch** | Titles align strongly | EANs are different (possible rebrand) | Identical titles but different barcodes |

**CONFIRMATION TEST:** Ask yourself:
> "If I could verify ONE of the following ON THE PHYSICAL PRODUCT, would I buy it?"
> - ✅ Brand name printed on packaging
> - ✅ Exact pack count labeled
> - ✅ Correct size/color/scent confirmed
> - ✅ Model number matches

**If YES → Include in NEEDS VERIFICATION**
**If NO (fundamental product mismatch) → Do NOT include**

**MANDATORY EXCLUSIONS (route to FILTERED OUT instead):**
- Adjusted Profit ≤ 0 after pack calculation
- Capacity difference >50% (different product)
- Completely different product types (e.g., candle vs diffuser)
- Clear brand + product type mismatch (different manufacturer AND different item)
```

---

## 📊 IMPLEMENTATION CHECKLIST

| Step | File | Lines to Edit | Status |
|------|------|---------------|--------|
| 1 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 27-30 (A3/A4) | ✅ **COMPLETE** |
| 2 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Line 19 | ✅ **COMPLETE** |
| 3 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 77-78 | ✅ **COMPLETE** |
| 4 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 94-95 | ✅ **COMPLETE** |
| 5 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 103-105 (V2/V3) | ✅ **COMPLETE** |
| 6 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 240-247 (HIGHLY LIKELY + EAN guidance) | ✅ **COMPLETE** |
| 7 | FINANCIAL REPORT PROMPT ANALYSIS_AG1_v2.md | Lines 256-278 (NEEDS VERIFICATION rewrite) | ✅ **COMPLETE** |

---

## 🆕 FIX #3: EAN STATUS DISTINCTION (ADDED)

### Problem Statement:
LLMs were not distinguishing between "Amazon EAN is missing" and "EANs are different." These are fundamentally different situations:
- **Missing EAN:** Amazon didn't provide barcode data. This is neutral/common.
- **Different EANs:** Both have barcodes but they don't match. Warrants scrutiny (could be rebrand).

### Implementation:
Added two new sections to clarify EAN status impact:

**In HIGHLY LIKELY section:**
```markdown
**🆕 EAN STATUS GUIDANCE FOR HIGHLY LIKELY:**
| EAN Status | Interpretation | Confidence Adjustment |
|------------|----------------|----------------------|
| **Amazon EAN Missing** | Common for many listings | No penalty if Brand+Product+Specs match |
| **EANs Different** | Could be rebrand OR different product | Slight caution; verify titles align perfectly |

- **Missing EAN ≠ Different EAN**: A missing EAN is neutral. A *different* EAN warrants scrutiny but doesn't automatically disqualify.
```

**In NEEDS VERIFICATION section:**
```markdown
**🆕 EAN STATUS IMPACT ON NEEDS VERIFICATION:**
| EAN Situation | Match Likelihood | Action |
|---------------|------------------|--------|
| **Amazon EAN Missing** ("-") | HIGHER likelihood | Missing EAN is neutral—consider HIGHLY LIKELY if Brand+Product match |
| **EANs are DIFFERENT** | LOWER likelihood (not impossible) | Different barcodes suggest different products OR rebrand. Route to NEEDS VERIFICATION if titles align well |
| **Both EANs Missing** | Moderate | Rely entirely on title evidence |
```

---

## 🧭 FIX #4: INTEGRATE PREFLIGHT CALIBRATION (SUPPLIER-SPECIFIC PACK/DIMENSION RULES)

### Problem Statement:
Generic pack parsing rules are not stable across suppliers. The `part_1_jan.xlsx` sample (first 50 rows) shows supplier naming patterns that will break generic logic if not explicitly handled:
- Compact suffix quantity tokens: `2PC`, `5PACK` (no space).
- Explicit set/count words: `CASES`, `PIECES`, `EACH`.
- Dimension/capacity suffixes are common and MUST NOT be treated as pack counts: `40CM`, `30M`, `500ML`, `26.5CM`, `5MM X 85MM`.
- Trailing raw numbers exist but are ambiguous (often variant/number rather than pack quantity): `... GIRL 3`, `... NUMBER ... 6`.

### Implementation (Prompt + Script):
1. **Add/keep a mandatory Preflight Calibration step** before main analysis to derive `SUPPLIER_NAMING_CONVENTION`.
2. **Require the main analysis to load and apply** the calibration values:
   - `explicit_units` should include `case/cases`, `piece/pieces`, `each`, plus `pc/pcs`, `pack`, etc.
   - `allow_trailing_number_as_qty` should be obeyed (for this file: `False`).
   - `dimension_shield_keywords` should include at least: `cm`, `mm`, `ml`, `ltr`, `l`, `g`, `kg`, `oz`, `inch`, `in`, `m`.
   - `sales_column` should be explicitly set from calibration (for this file: `bought_in_past_month`).
3. **Update the supplier quantity regex** to accept both spaced and compact forms:
   - `(\d+)\s*(pc|pcs|piece|pieces|case|cases|pack)` catches `2PC`, `100CASES`, `5PACK`, `12 PIECES`.
   - Explicitly avoid interpreting trailing raw numbers as qty when calibration disables it.
4. **Update the dimension shield rules** to treat:
   - `\d+(\.\d+)?\s*(cm|mm|ml|m|l|ltr|g|kg|oz|inch|in)` as measurement (not pack),
   - `\d+(\.\d+)?\s*[x×]\s*\d+(\.\d+)?\s*(mm|cm|inch|in)` as dimensions (never pack).

### Reference Calibration Output:
Calibration block + warnings for `part_1_jan.xlsx` were generated here:
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\CODEX 1\calibration_config_snippet.py`

---

## 🎯 EXPECTED OUTCOMES AFTER FIXES

| Metric | Before Fixes | After Fixes |
|--------|--------------|-------------|
| NEEDS VERIFICATION clarity | Vague "1-2 details" | Specific scenario table with examples |
| Pre-filtering confusion | Mixed signals about Sales=0/NetProfit≤0 | Clear acknowledgment that data is pre-filtered |
| LLM conservatism in NEEDS VERIFICATION | Too selective (missing valid candidates) | Practical selectivity with concrete scenarios |
| Consistency across LLM runs | Variable interpretation | Standardized criteria |
| Pack mismatch false positives | Dimension/qty confusion | Calibration-driven dimension shield + explicit unit parsing |

---

## 📝 NOTES FOR IMPLEMENTATION

1. **Line numbers may shift** after edits - edit from bottom to top to preserve line numbers
2. The NEEDS VERIFICATION section (Lines 256-278) is the **most critical fix** - this is where LLMs are getting confused
3. Consider adding a "NEEDS VERIFICATION Examples" appendix similar to the existing "HIGHLY LIKELY Examples" table
4. After implementing, run a test analysis on a small subset (50-100 rows) to validate interpretation

---

*Fixes Plan v4.2*
*Generated: 2026-01-01*
