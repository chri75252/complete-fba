# SURGICAL PREFLIGHT PROMPT FIXES (v1.2)
**Generated:** 2026-01-03
**Applies to:** ANY supplier / ANY report file

## Source File
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\AG_PREFLIGHT_CALIBRATION_PROMPT.md`

---

## A) File type assumption (CSV-only)
**Why it matters:** The workflow uses XLSX sometimes; preflight must not fail just because the input isn't CSV.

**Lines 3, 8–9 (v1.1 text):**
```text
   1: # AGENTIC FBA CALIBRATION PROMPT (PRE-FLIGHT) v1.1
   2: 
   3: **Purpose:** Analyze a specific financial report CSV *before* the main analysis to detect the supplier's unique naming conventions, pack quantity formats, and data anomalies. This output will customize the main analysis prompt.
   4: 
   5: **Version:** 1.1 (Updated 2026-01-02)
   6: 
   7: **Input:** 
   8: 1. Path to CSV: `[USER_FILE_PATH]`
   9: 2. Read first 50 rows (or more if needed to detect patterns).
  10: 
  11: **Role:** You are a Data Pattern Specialist. Your ONLY job is to identify the schema rules for this specific supplier file. The main analysis will reference your output to avoid common parsing traps.
  12: 
```

**Surgical fix:**
- Change wording to "CSV or XLSX" everywhere in Purpose/Input.

---

## B) Missing 'non-pack Nx' spec detection (magnification/zoom)
**Why it matters (supplier-agnostic):** Titles often contain "2x" / "3x" that are feature multipliers (optical zoom/magnification), not bundle quantity; this can create false RSU>1.

**Gap:** TASK 1 covers pack units + leading multipliers, but does not ask to identify "Nx" feature patterns that must be shielded in the main prompt.

**Surgical fix:**
- Add a new "TASK 1C" instructing the analyst to identify "2x Magnification" / "3x Zoom"-style patterns as NOT pack.
- Add output keys (generic): `spec_x_shield_keywords` (default: ["magnification", "zoom"]) and a boolean to enable it.

---

## C) Table delimiter hazard (pipe character)
**Why it matters (supplier-agnostic):** Amazon titles frequently include "|". If the main report uses markdown tables with `|` delimiters, unescaped pipes inside cell text can corrupt tables and effectively "drop" rows during parsing/review.

**Surgical fix:**
- Add an output flag `table_pipe_sanitization: True` so the main prompt knows to replace `|` with `/` inside titles/evidence before emitting fixed-width tables.
