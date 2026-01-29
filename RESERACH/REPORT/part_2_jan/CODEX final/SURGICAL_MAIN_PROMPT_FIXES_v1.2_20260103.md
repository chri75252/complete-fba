# SURGICAL MAIN PROMPT FIXES (v1.2)
**Generated:** 2026-01-03  
**Applies to:** ANY supplier / ANY report file

## Source Prompt File (v1.1)
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.1.md`

## Updated Prompt File (v1.2, integrated)
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md`

---

## 1) Stop “selective” from becoming “silent drop”

### Line 21 (v1.1 text)
`- NEEDS VERIFICATION is **highly selective**: only items with 1-2 confirmable details that would upgrade to HIGHLY LIKELY.`

**Confusion**
- Can be misread as “don’t output borderline items”, which causes missed candidates.

**v1.2 fix (supplier-agnostic)**
- Reworded to explicitly prefer placing borderline rows into NEEDS VERIFICATION over omitting them.

---

## 2) Clarify narrative clamp scope (tables are not “select entries”)

### Line 181 (v1.1 text)
`- Select entries based on match quality, not arbitrary caps or sales ranking.`

**Confusion**
- The phrase “Select entries” can be wrongly applied to table inclusion, not just narrative.

**v1.2 fix**
- Clarified that the clamp applies ONLY to narrative text; tables must include all qualifying rows.

---

## 3) Resolve the explicit conflict: “include borderline” vs “do not include”

### Line 207 (v1.1 text)
`**It is better to include borderline items than to miss valid matches** ...`

### Lines 806–807 (v1.1 text)
`**Step 5: Default Case**`  
`- If evidence is too weak for any category  Do not include in report`

**Confusion**
- These instructions conflict; without an explicit hierarchy, “do not include” becomes an unintended hard gate.

**v1.2 fix**
- Added a tie-breaker so borderline items go to NEEDS VERIFICATION, and only clearly unrelated rows are omitted.

---

## 4) Add a supplier-agnostic “spec multiplier” shield for Nx patterns

**Problem (generic)**
- Some titles contain `Nx` that are feature multipliers (e.g., `2x Magnification`, `3x Zoom`) rather than bundle counts.

**v1.2 fix**
- Added a “Spec / Feature Shield” note so `Nx` near feature words doesn’t trigger RSU.

---

## 5) Prevent table corruption by sanitizing `|`

**Problem (generic)**
- Amazon titles frequently contain `|`. In markdown tables, unescaped `|` inside cells can break alignment and make rows appear “missing”.

**v1.2 fix**
- Added a table safety rule: replace literal `|` inside cell text with `/` and remove embedded newlines before width calculation.

