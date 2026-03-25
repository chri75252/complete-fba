# FBA Analysis Batch 1
**Source:** tmptlyyl342.csv
**Rows:** 30-25
**Tiers:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Generated:** 2026-03-20T22:19:01.647675

# Amazon FBA Arbitrage Product Matching Analysis

## Methodology Notes
- EAN format: `5.0103E+12` = 5010365000000, `5.01035E+12` = 5010350000000 (different products)
- Same ASIN can have multiple products (via variations) but supplier titles must match the specific variant
- Pack size discrepancies require profit recalculation per unit

---

## VERIFIED

*No products met exact title/EAN/title match criteria*

---

## HIGH LIKELIHOOD

| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks |
|---------|------------|---------------|-------------|--------------|------------|------|---------------|--------------|-----------|-----|-------|--------------|------------------|-------------------|-----------|
| TRUE MATCH | 60 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS | Fairy Soap Dispensing Dish Brush | 5010365000000 | 5010365000000 | B0BYKDX25N | £1.20 | £6.57 | £0.43 | 27.4% | 50 | SUPPLIER BUNDLE (brush+3 refills) vs SINGLE on Amazon | £0.40/unit | Same EAN/ASIN; both Fairy branded; core product match | Pack mismatch; refills inflate perceived value; Row 33 is pure single unit comparison |
| TRUE MATCH | 60 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | 5010365000000 | 5010365000000 | B0BYKDX25N | £1.73 | £6.57 | £0.06 | 2.8% | 50 | PACK SIZE MATCH (1:1) | £0.06/unit | Exact title alignment; same EAN/ASIN; no pack size discrepancy | Very low ROI (2.8%); supplier price too high |

---

## NEEDS VERIFICATION

*No products in this category*

---

## AUDITED OUT

| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks |
|---------|------------|---------------|-------------|--------------|------------|------|---------------|--------------|-----------|-----|-------|--------------|------------------|-------------------|-----------|
| FALSE POSITIVE | 35 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge Scoure | 5010365000000 | 5010365000000 | B09P1G3YJ5 | £0.90 | £5.99 | £0.49 | 37.8% | 100 | Pack mismatch (2PK vs single) | £0.25/unit | Same EAN/ASIN | **TITLE VARIANT CONFLICT**: Row 25 lists "TEARDROP SCOURER" as same product - different variants CANNOT share ASIN |
| FALSE POSITIVE | 20 | FAIRY MAX POWER TEARDROP SCOURER | Addis Fairy Originals Non Scratch General Dual Sponge Scoure | 5010365000000 | 5010365000000 | B09P1G3YJ5 | £0.90 | £5.99 | £0.49 | 37.8% | 100 | Pack mismatch (2PK vs single) | £0.25/unit | None - title mismatch | **CLEAR MISMATCH**: "Teardrop" ≠ "Dual Sponge" - different physical products |
| FALSE POSITIVE | 30 | MINKY ANTIBACTERIAL 4 SPONGE SCOURERS HD | Minky Anti-Bacterial Cleaning Pad 3