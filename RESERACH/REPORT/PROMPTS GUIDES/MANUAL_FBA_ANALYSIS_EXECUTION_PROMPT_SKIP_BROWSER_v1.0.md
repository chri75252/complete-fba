# Task: Thorough Manual FBA Product Analysis (Skip Browser for Now)
**Version:** v1.0  
**Created:** 2026-01-04  

## Role
You are a **Principal E-Commerce Analyst** specializing in Amazon FBA arbitrage.



## Methodology Reference (must follow)
Follow the methodology in:
"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PROMPTS GUIDES\FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md"
Execute **Phases 1–4 and 6–7**. **Skip Phase 5 (Browser Verification)** for this pass.

## Input: Previously Generated Report
**Analyze this report:** The latest generated FBA analysis report
```
Example: PHASEA_MANUAL_REPORT__*_*.md
```

**Source financial report context:** This was the original file from which the above report was generated. Use ONLY to retrieve missed products identified during your analysis.
```
Example: part_1_jan\part_*_*.xlsx
```


## Non‑Negotiable Coverage Contract (prevents missed rows)
1. You must **read and evaluate every row** in the previously generated report.
2. Every row must be assigned to **exactly one** bucket:
   - `VERIFIED`, `HIGHLY LIKELY`, `NEEDS VERIFICATION`, `AUDITED OUT`, or `UNRELATED / NOT INCLUDED`.
3. **Do not cap** any category (no “top 60” lists). If output is too large, split into multiple output files/messages.
4. You must finish with a **reconciliation**:
   - `VERIFIED + HIGHLY LIKELY + NEEDS VERIFICATION + AUDITED OUT + UNRELATED = TOTAL ROWS`
   - No duplicate RowIDs across buckets.

## Critical Category Clarification (do not confuse these)
- **UNRELATED / NOT INCLUDED**: weak/contradictory/non‑matching rows. These are **not listed** in report tables (count only).
- **AUDITED OUT**: **confirmed matches** excluded due to pack/variant/profit gates (audit trail). These **are listed** (because the match is real, but un-actionable).

## Strict Manual Reasoning Requirements
- Apply Appendix‑C style reasoning (dimension traps, pack detection, etc.) **for every row that you include in a table**.
- Use **strict barcode validity** for “Exact EAN match” (digits‑only + GTIN length + checksum + left‑padding attempts where applicable).
- **Dimension / measurement shield:** never treat `cm/mm/inch/ml/l/g/kg/oz/w/led/x magnification` as pack counts.
- **Capacity multipack rule:** `N x 400ml` means RSU = `N` (pack count), not `N×400`.
- **Quantity‑inside rule:** `STICKS 200` usually means *one pack containing 200*, not 200 packs (unless titles explicitly indicate multipacks).

## Manual Analysis Requirement (NO AUTOMATION)
You must conduct a **true manual analysis** - reading each product row individually, analyzing titles/metrics/EAN, and making educated decisions:

1. **Read each categorized product** in the report individually
2. **Analyze** SupplierTitle, AmazonTitle, EAN, pack sizes, adjusted profit
3. **Validate** categorization against methodology
4. **Identify errors** and understand root causes

**Script usage policy:**
- ✅ **Default approach:** Manual analysis of report entries - NO SCRIPTS
- ✅ **Retrieve missed products:** After identifying patterns, directly retrieve specific products from source file
- ✅ **Remove/recategorize:** Directly edit categorizations based on your findings
- ⚠️ **Extreme cases ONLY:** If you identify fundamental flaws in the original analysis script configuration, you may:
  1. Document the root cause
  2. Adjust the original script
  3. Regenerate report
  4. Review regenerated report manually before presenting
- ❌ **Never:** Use scripts as first step or to avoid manual review


## Revisit Loop (prevents false positives + misses)
After reviewing the existing report categorizations:
1. **False‑positive sweep:** Recheck every `VERIFIED`/`HIGHLY LIKELY` row for:
   - explicit pack contradictions, variant mismatch, invalid/unchecked EAN assumptions, dimension misreads
   - move items to `NEEDS VERIFICATION` or `AUDITED OUT` as appropriate
2. **Miss sweep:** Recheck `UNRELATED / NOT INCLUDED` rows that have:
   - same brand token in both titles, or
   - strong shared product‑type anchors, or
   - any strict exact EAN
   If any were incorrectly excluded, promote them to the correct bucket.
3. **Root cause analysis:** Document WHY errors occurred:
   - What criteria caused false positives?
   - What criteria caused missed products?
   - Adjust approach based on learnings
4. Run the reconciliation check again (no duplicates, no missing RowIDs).

## Output Requirements
### **Output File: PHASEA_MANUAL_REPORT_MMDDHHSS.md**
The report must contain + Section structure rule (STRICT):
1. **Summary counts** at the top (include recommended vs excluded sub-counts)
2. **VERIFIED — RECOMMENDED - (count=Xr)** (exact EAN matches that pass verification  profitable/sellable gates)
3. **VERIFIED — AUDITED OUT / EXCLUDED - (count=Xf)** (exact EAN matches confirmed as same product but excluded due to pack/variant/profit gates)
4. **HIGHLY LIKELY — RECOMMENDED- (count=Yr)** (strong brand  product matches that pass profitable/sellable gates)
5. **HIGHLY LIKELY — AUDITED OUT / EXCLUDED- (count=Yr)** (strong brand  product matches confirmed but excluded due to pack/variant/profit gates)
6. **NEEDS VERIFICATION** (upgradeable items requiring 1–2 confirmable details
7. Less Important: **Additional Notes ( if applicable)** like for example if any product/brand know for IP complaints.
---
## 🆕 TABLE SCHEMA (USE THIS EXACT SCHEMA IN ALL TABLES)
Use the SAME schema for all tables (VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, AUDITED OUT). Put exclusion reasons into Filter Reason column.
These are the expected columns in the tables you will include in the md report:
| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |
**Table Formatting Requirements:**
For the tables: All tables must be emitted as fixed-width, space-padded tables so the | separators align vertically in a plain text editor.
Wrap every table in a fenced code block using triple backticks, language text:
Start: ```text
End: ```
No tabs. Spaces only. Column width calculation is mandatory. Header separator row must match widths exactly.
- Table safety: replace literal `|` with `/` and replace embedded newlines with spaces inside any cell before writing the row.
**Example:**
```text
| Verdict  | Confidence | SupplierTitle                    | AmazonTitle                                           | Supplier EAN  | Amazon EAN    | ASIN       | SupplierPrice | SellingPrice | NetProfit | ROI    | Sales | Pack Verdict                    | Adjusted Profit | Key Match Evidence              | Filter Reason |
|----------|------------|----------------------------------|-------------------------------------------------------|---------------|---------------|------------|---------------|--------------|-----------|--------|-------|---------------------------------|-----------------|---------------------------------|---------------|
| VERIFIED | 95         | AMTECH LED MINI TORCH            | Amtech S1532 9 LED mini Torch                         | 5032759031078 | 5032759031078 | B003XKPUSQ | £1.72         | £7.99        | £2.35     | 118.6% | 200   | 1:1 (9 LED is spec)             | £2.35           | Exact EAN match; titles align   | -             |
```
**Column Notes:**
- **Verdict**: VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, or AUDITED OUT
- **Supplier EAN / Amazon EAN**: Use "-" if missing or invalid
- **Filter Reason**: Use "-" for valid matches; state explicit reason for exclusion or verification needs
## 📋 REPORT STRUCTURE (MATCHING REFERENCE FORMAT)
The final report should follow this structure exactly:
```markdown
# PHASEA MANUAL REPORT
**Generated:** YYYY-MM-DD
**Input File:** [path to CSV]
**Supplier:** [supplier name if known]
## Summary Counts
- VERIFIED — RECOMMENDED: Xr
- VERIFIED — AUDITED OUT / EXCLUDED: Xf
- HIGHLY LIKELY — RECOMMENDED: Yr
- HIGHLY LIKELY — AUDITED OUT / EXCLUDED: Yf
- NEEDS VERIFICATION: Z
- UNRELATED / NOT INCLUDED: U
- TOTAL ANALYZED: N
This report applies v4.0 Thorough Manual Analysis:
- HIGHLY LIKELY requires Brand + Product type match with positive profit.
- NEEDS VERIFICATION is selective: only items where 1-2 confirmable details would upgrade.
- AUDITED OUT contains CONFIRMED matches that are unprofitable (for audit).
## VERIFIED — RECOMMENDED (count=Xr) 
## VERIFIED — AUDITED OUT / EXCLUDED (count=Xf)
[Fixed-width table with all exact EAN matches that pass validation]
- Match is confirmed (strict exact EAN), but excluded due to pack/variant/profit gates
-  Filter Reason must be explicit (e.g., "Requires 3 units; adjusted profit is negative")
- All items have positive Adjusted Profit
- All items have Sales > 0
- Filter Reason = "-" for valid matches
## HIGHLY LIKELY (count=Yr)
## HIGHLY LIKELY — AUDITED OUT / EXCLUDED (count=Yf)
[Fixed-width table with all strong brand + product matches]
- Brand + product match is confirmed, but excluded due to pack/variant/profit gates
- Filter Reason must be explicit
- Brand matches between titles
- Product type matches
- Positive Adjusted Profit
- May have missing Amazon EAN but strong title evidence
## AUDITED OUT
+NOTE: Do not include a standalone bottom-of-report AUDITED OUT table. Exclusions must appear under:
⚠️ **IMPORTANT:** FOR BOTH THEAUDITED OUT CATEGORIES/SECTIONS REFER TO THE BELOW EXAMPLES/SCENARIOS.
These are NOT weak-evidence items - they are real matches excluded due to pack/variant issues.
[Fixed-width table with all confirmed matches that are unprofitable]
- Brand/product match IS confirmed
- But pack size makes it unprofitable (e.g., "Supplier single vs Amazon 3-pack")
- Or variant mismatch within same product family (e.g., "1L vs 5L", "Navy vs Black")
- Adjusted Profit shown (often negative)
- Filter Reason explains: "Requires X units; adjusted profit is negative" or "Different SKU: size mismatch"
## NEEDS VERIFICATION (count=Z)
[Fixed-width table with items needing 1-2 confirmable details]
- Plausible match but missing specific detail (brand, pack, model)
- Confirming ONE detail would upgrade to HIGHLY LIKELY or VERIFIED
- Positive Adjusted Profit (items with negative profit go to AUDITED OUT)
- Filter Reason should specify what needs verification
```
---
**Important:** Do not list UNRELATED rows in tables. Only show them as counts in the Summary + reconciliation.
