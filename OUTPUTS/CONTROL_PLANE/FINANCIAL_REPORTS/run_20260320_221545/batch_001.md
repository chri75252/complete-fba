# FBA Analysis Batch 1
**Source:** tmpnm0lb5v4.csv
**Rows:** 34-34
**Tiers:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Generated:** 2026-03-20T22:16:13.668485

## Amazon FBA Arbitrage Analysis

### AUDITED OUT — False Positives / Excluded

| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|---------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|---------------------------|---------------------|-------------------|
| AUDITED OUT | 20 | JAUNTY GIANT CONFTTI CANNON 2PK | SOL 2pk Confetti Cannons Large - Giant Party Poppers Paper C | 5056180000000 | 5056180000000 | B09YMBWX7N | £1.37 | £6.99 | £0.44 | 25.7% | 700 | Match (2pk) | N/A | Same EAN, both 2pk | **BRAND MISMATCH**: JAUNTY vs SOL (different manufacturers). Category "Disposables Party Bin Liners" is WRONG for confetti cannons. High ROI suspicion confirmed. Excluded. |

---

### Summary

| Verdict | Count |
|---------|-------|
| VERIFIED | 0 |
| HIGH LIKELIHOOD | 0 |
| NEEDS VERIFICATION | 0 |
| **AUDITED OUT** | **1** |

**Analysis Complete:** Of the 1 product row reviewed, **1 product (100%) was AUDITED OUT**.

**Critical Findings for Row #34:**
- **Brand Mismatch (Critical):** Supplier title specifies "JAUNTY" brand; Amazon listing shows "SOL" brand — these are distinct party product manufacturers with no affiliation
- **Category Mismatch:** The assigned category "Disposables Party Bin Liners" is entirely incorrect for confetti cannons, indicating likely data entry error or misattribution
- **EAN Match Insufficient:** While EANs match, the conflicting brand information confirms these are different physical products from different suppliers/manufacturers
- **Verdict Rationale:** The 25.7% ROI combined with 700 sales and low 20% confidence score aligns with the pattern rule: high ROI with low confidence should be treated as false positive until proven otherwise

**Recommendation:** Exclude from sourcing. Do not purchase "JAUNTY" branded confetti cannons expecting to sell on the "SOL" ASIN — this would constitute listing misrepresentation and potential IP/trademark violation.