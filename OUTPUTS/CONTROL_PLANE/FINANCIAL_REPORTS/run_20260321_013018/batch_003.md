# FBA Analysis Batch 3
**Source:** fba_analysis_2026-03-20 (1).csv
**Rows:** 42-42
**Tiers:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Generated:** 2026-03-21T01:32:15.718805

### Analysis Results

#### **AUDITED OUT** — False positives, excluded

| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| AUDITED OUT | 95 | DOVE APA INVISIBLE DRY MENS 250ML PK6 | Dove Men + Care Invisible Dry Antiperspirant Deodorant Aeros | 8711600555522 | 8711600555522 | B0D47FBD1B | £14.10 | £22.99 | £0.17 | 1.4% | 100 | **DISCREPANCY** (Supplier: 6-pack, Amazon: likely single) | **-£1.95** per unit | Exact EAN match. | **Critical pack size mismatch.** Supplier title clearly states "PK6" (6-pack). Amazon title does not specify pack size, implying a single unit. Recalculation shows a **loss per unit** if Amazon listing is a single. ROI is abnormally low (1.4%), a classic false-positive indicator. "West Africa Only" category suggests potential regional restrictions or listing errors. |

### Summary
Out of 1 product row analyzed, **1 row was audited out** as a false positive. The primary reason was a critical pack size discrepancy (supplier 6-pack vs. likely Amazon single unit), which, when adjusted for, revealed a negative profit per unit. The exact EAN match was overridden by this clear evidence of different products being sold. No rows were verified, highly likely, or needed verification.