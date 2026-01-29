# SURGICAL PROMPT FIXES (POST-MORTEM)
**Generated:** 2026-01-03  
**Scope:** Identify the exact prompt lines that caused overly restrictive gating / misclassification, explain the confusion, and propose the smallest wording changes that prevent recurrence.

## Source Prompt File (line-numbered)
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.1.md`

---

## 1) “Selective NV” interpreted as “drop most rows”

### Line 21 (exact text)
`- NEEDS VERIFICATION is **highly selective**: only items with 1-2 confirmable details that would upgrade to HIGHLY LIKELY.`

**What was confusing / misinterpreted**
- This reads like a hard output-cap on NEEDS VERIFICATION, and (combined with other lines below) can be misread as: “if it’s not clearly HL/VERIFIED, omit it entirely”.

**Why Preflight didn’t prevent it**
- Preflight calibration only tunes parsing rules (pack tokens, dimension shields, naming conventions). It does not override *output inclusion* gates. This line is a categorization *policy* gate, not a parsing calibration issue.

**Surgical replacement**
- Replace with:
  - `- NEEDS VERIFICATION is selective: include items where verifying 1–2 specific details would upgrade the match; if unsure, prefer NEEDS VERIFICATION over omitting the row.`

---

## 2) “Narrative clamp” misread as “table inclusion clamp”

### Line 181 (exact text)
`- Select entries based on match quality, not arbitrary caps or sales ranking.`

**What was confusing / misinterpreted**
- This sits under “Narrative clamp”, but the phrase “Select entries” can be incorrectly applied to the entire report (tables), causing unrequested pre-filtering.

**Why Preflight didn’t prevent it**
- Preflight doesn’t address report-format ambiguity. This is an instruction-scoping problem (narrative vs table output).

**Surgical replacement**
- Replace with:
  - `- Narrative clamp applies ONLY to narrative text (not the tables): keep narrative short; tables must include all qualifying rows per the category rules.`

---

## 3) “Default case: do not include” created a hidden “hard exclusion” gate

### Lines 806–807 (exact text)
`**Step 5: Default Case**`  
`- If evidence is too weak for any category  Do not include in report`

**What was confusing / misinterpreted**
- This creates a strong “silent drop” instruction that conflicts with “better to include borderline items than to miss valid matches”.
- When combined with Row Evidence Integrity + strict anchor requirements, it pushes many plausible rows into “not shown”, which is exactly what you flagged as “missed products”.

**Why Preflight didn’t prevent it**
- Preflight can’t fix a downstream instruction that authorizes dropping rows entirely.

**Surgical replacement**
- Replace line 807 with:
  - `- If evidence is too weak for VERIFIED/HIGHLY LIKELY, place the row in NEEDS VERIFICATION (low confidence) unless there is a clear contradiction; only omit rows that are clearly unrelated (different product type/brand/category mismatch).`

---

## 4) Missing explicit “optical spec shield” (caused pack false-positives)

### Observed failure (file-grounded)
- In `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx`, RowID `2404` contains:
  - AmazonTitle: `... One Side with 2x Magnification ...`
- “2x” was misread as multipack in the initial CODEX logic, causing a false RSU>1 and moving an exact-EAN item to FILTERED OUT.

**Why Preflight didn’t prevent it**
- Preflight focused on dimensions/capacities and common pack tokens; “2x magnification” is neither a dimension unit nor an explicit pack token, so it wasn’t covered.

**Surgical addition (to the Dimension / Measurement Shield section)**
- Add one bullet:
  - `- Optical/spec tokens are NOT pack counts: patterns like \"2x Magnification\" / \"3x Zoom\" / \"10x LED\" describe features, not bundle quantity.`

---

## 5) Clarify “include borderline” vs “selective NV” hierarchy

### Line 207 (exact text)
`**It is better to include borderline items than to miss valid matches** - the subsequent manual analysis step will refine the results.`

**What went wrong**
- This instruction was not treated as the tie-breaker when it conflicted with “Default case: do not include” and “NV is highly selective”.

**Surgical fix (add one sentence immediately after line 207)**
- Add:
  - `Tie-breaker: when instructions conflict, prefer inclusion into NEEDS VERIFICATION over omission; only exclude rows with clear contradictions.`

---

## Recommended next action
- If you want, I can apply these surgical edits directly to `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.1.md` (with a mandatory backup under `backup\prompt_fix_YYYYMMDD\` first), so the prompt itself encodes the corrected intent.

