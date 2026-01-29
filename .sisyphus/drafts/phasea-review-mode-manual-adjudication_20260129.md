# Draft: PhaseA Review Mode Manual Adjudication (2026-01-29)

## Core Objective (confirmed)
- Produce an execution plan for **REVIEW MODE** manual adjudication of an existing PhaseA Markdown report, correcting false positives/negatives **without re-running pipeline logic**.

## Inputs (confirmed)
- Primary MD report (review target):
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\OC\PHASEA_MANUAL_REPORT_20260129.md`
- Source XLSX for disputed-field spot checks only:
  - `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx`
- Optional run artifacts folder (prefer not to use to decide verdicts):
  - `...\RESERACH\REPORT\part 8 jan\OC\runs\20260129_075537\` (coverage_ledger.csv, evidence.jsonl)

## Required Output (confirmed)
- Step-by-step plan + verification checklist to manually adjudicate each printed row into one of:
  - `VERIFIED`
  - `VERIFIED-AUDITED OUT`
  - `HIGHLY LIKELY`
  - `HIGHLY LIKELY-AUDITED OUT`
  - `NEEDS VERIFICATION`
- Produce:
  - (a) a **Corrections** section (REMOVE / MOVE / EDIT)
  - (b) a **reviewed corrected report** (same report format, but corrected)

## Methodology Gates / Guardrails (confirmed)
- **EAN normalization guardrail** (strict order; show raw + normalized when used)
  - Convert to string → strip → remove trailing `.0` → treat `e+` as corrupted/untrusted → digits-only + length/checksum.
- **Dimension/capacity shield**
  - Numbers with units (cm/mm/inch/ml/l/g/kg, WxHxD patterns like `9x9 inch`) are **specs**, not pack counts.
- **Split-candidate handling**
  - SPLIT CANDIDATE rows cannot be auto-upgraded based on ratios; must route to NV unless pack truth is confirmed.
- **Unique-anchor eligibility**
  - HIGHLY LIKELY / NEEDS VERIFICATION require at least one unique anchor (model/MPN/SKU/part#/series token).
- **UNRELATED handling**
  - UNRELATED is count-only and must **not** be listed in output tables.

## Must NOT Do (confirmed)
- Do not re-run pipeline logic to decide verdicts.
- No similarity scoring.
- No automated pack parsing.

## Observations from current report (evidence)
- The report contains sections:
  - `VERIFIED - RECOMMENDED` (34)
  - `VERIFIED - AUDITED OUT` (6)
  - `HIGHLY LIKELY - RECOMMENDED` (185)
  - `HIGHLY LIKELY - AUDITED OUT` (45)
  - `NEEDS VERIFICATION` (86)
  - `Reconciliation` uses combined totals for VERIFIED/HIGHLY_LIKELY.

## Open Questions
- What is the **row identifier** to use in Corrections? The PhaseA tables do not include an explicit `RowID` column.
- Where should the corrected output be written?
  - New file path/name vs overwrite-in-place instructions.
- Are run artifacts (`coverage_ledger.csv`, `evidence.jsonl`) allowed for *bookkeeping only* (e.g., confirming we reviewed all printed rows), while still forbidden for deciding verdicts?
