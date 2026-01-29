# Task: Thorough Manual FBA Product Analysis (Skip Browser for Now)
**Version:** v1.0  
**Created:** 2026-01-04  

## Role
You are a **Principal E-Commerce Analyst** specializing in Amazon FBA arbitrage.



## Methodology Reference (must follow)
Follow the methodology in:
"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md"
Execute **Phases 1–4 and 6–7**. **Skip Phase 5 (Browser Verification)** for this pass.

## Non‑Negotiable Coverage Contract (prevents missed rows)
1. You must **read and evaluate every row** in the financial report (RowID 1..N).
2. Every row must be assigned to **exactly one** bucket:
   - `VERIFIED`, `HIGHLY LIKELY`, `NEEDS VERIFICATION`, `FILTERED OUT`, or `UNRELATED / NOT INCLUDED`.
3. **Do not cap** any category (no “top 60” lists). If output is too large, split into multiple output files/messages.
4. You must finish with a **reconciliation**:
   - `VERIFIED + HIGHLY LIKELY + NEEDS VERIFICATION + FILTERED OUT + UNRELATED = TOTAL ROWS`
   - No duplicate RowIDs across buckets.

## Critical Category Clarification (do not confuse these)
- **UNRELATED / NOT INCLUDED**: weak/contradictory/non‑matching rows. These are **not listed** in report tables (count only).
- **FILTERED OUT**: **confirmed matches** excluded due to pack/variant/profit gates (audit trail). These **are listed** (because the match is real, but un-actionable).

## Strict Manual Reasoning Requirements
- Apply Appendix‑C style reasoning (dimension traps, pack detection, etc.) **for every row that you include in a table**.
- Use **strict barcode validity** for “Exact EAN match” (digits‑only + GTIN length + checksum + left‑padding attempts where applicable).
- **Dimension / measurement shield:** never treat `cm/mm/inch/ml/l/g/kg/oz/w/led/x magnification` as pack counts.
- **Capacity multipack rule:** `N x 400ml` means RSU = `N` (pack count), not `N×400`.
- **Quantity‑inside rule:** `STICKS 200` usually means *one pack containing 200*, not 200 packs (unless titles explicitly indicate multipacks).

## Revisit Loop (prevents false positives + misses)
After your first categorization pass:
1. **False‑positive sweep:** Recheck every `VERIFIED`/`HIGHLY LIKELY` row for:
   - explicit pack contradictions, variant mismatch, invalid/unchecked EAN assumptions, dimension misreads
   - move items to `NEEDS VERIFICATION` or `FILTERED OUT` as appropriate
2. **Miss sweep:** Recheck `UNRELATED / NOT INCLUDED` rows that have:
   - same brand token in both titles, or
   - strong shared product‑type anchors, or
   - any strict exact EAN
   If any were incorrectly excluded, promote them to the correct bucket.
3. Run the reconciliation check again (no duplicates, no missing RowIDs).

## Output Requirements
Generate `PHASEA_MANUAL_REPORT_YYYYMMDD.md` using the same table schema and formatting rules as:
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\FINANCIAL REPORT PROMPT ANALYSIS_AG1_v1.2.md`

**Important:** Do not list UNRELATED rows in tables. Only show them as counts in the Summary + reconciliation.
