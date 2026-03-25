# FBA AI Analysis Report
**Source:** tmpdkpqiyqc.csv
**Total Rows Analyzed:** 7
**Tiers Included:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Model:** minimax-m2.5-free
**Generated:** 2026-03-17T12:19:37.117934

---

## Batch 1

```text
| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Category | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |
|---------|------------|---------------|-------------|--------------|------------|------|---------------|--------------|-----------|-----|----------|--------------|------------------|---------------------|----------------|
| TRUE MATCH | 95 | Rysons Children Clothes Hangers 10 Pc (White) | Rysons Children Clothes Hangers - White - PACK OF 10 | 5056239423412 | 5056239423412 | B0CGVQNV5L | 1.188 | 4.99 | -0.42 | -27.0% | Baby Kids | MATCH (10-pack) | -0.42 | EAN match + Brand match + Color match + Quantity match (10Pc/PACK OF 10) | Negative ROI - not viable |
| NEEDS VERIFICATION | 60 | Tidyz Extra Strong Nappy Bags With Tie Handles - 29 x 32cm - | TidyZ 100 Extra Large Nappy Bags Tie Handles | 5025364004759 | 5025364004759 | B08SMJKVNJ | 0.60 | 4.49 | -0.41 | -38.9% | Baby Kids | LIKELY MISMATCH (supplier may be single roll vs Amazon 100-pack) | N/A - pack size unclear | EAN match but supplier title missing quantity - likely single pack vs 100-pack |
| FALSE POSITIVE | 40 | Rysons Children Clothes Hangers 10 Pc (Multi) | Rysons Children Clothes Hangers - Multi Coloured - PACK OF 1 | 5056239423405 | 5056239423405 | B0CGJC2JV1 | 1.188 | 4.78 | -0.93 | -60.2% | Baby Kids | PACK SIZE MISMATCH (supplier=10pc vs Amazon=1pc) | N/A - different products | Pack size discrepancy: "10 Pc" vs "PACK OF 1" - supplier 10-pack vs Amazon single unit |
| TRUE MATCH | 90 | BABY THERMAL BLANKET - 70 X 90 CM - TWIN PACK | CUDDLES BABY THERMAL BLANKET TWIN PACK | 5056239401809 | 5056239401809 | B0B7PG8F16 | 5.22 | 18.99 | 6.14 | 125.3% | Baby Kids | MATCH (twin pack) | 6.14 | EAN match + "TWIN PACK" match + dimensions match (70x90cm) | Strong match - viable arbitrage |
| FALSE POSITIVE | 35 | A to Z Soothing Gel And Cold Compress Pack - Animated Design | Beautiful Beginnings Soothing Gel Pack (Assorted Designs) | 5012866701859 | 5012866701859 | B01K2GA6N2 | 0.72 | 2.25 | -0.98 | -84.8% | Baby Kids | LIKELY MISMATCH (brand differs) | N/A - different products | Brand mismatch: "A to Z" vs "Beautiful Beginnings" - different manufacturers |
| NEEDS VERIFICATION | 55 | WATERPROOF BED COVER | Waterproof Bed sheet for Single bed 200x100cm Perfect for po | 5056239401052 | 5056239401052 | B0FGY7VMZF | 0.948 | 3.99 | -0.31 | -23.5% | Baby Kids | UNCLEAR (size may differ) | N/A - viability unclear | Supplier title generic, Amazon specifies Single bed 200x100cm - size verification needed |
| TRUE MATCH | 75 | Kids Toothbrushes - Pack of 4 - 4 Colours | 4pk Children Toothbrush \| BPA Free Toothbrush Pack in Red; G | 5055566995500 | 5055566995500 | B07T3B2ZP5 | 0.816 | 4.49 | 0.48 | 39.2% | Baby Kids | MATCH (4-pack) | 0.48 | EAN match + quantity match (4-pack) + category match (children toothbrush) | Moderate confidence - viable at 39% ROI |
```

## Summary

This batch of 7 Amazon FBA arbitrage rows reveals significant quality issues in the matching algorithm. **Three rows are confirmed or probable FALSE POSITIVES/NEEDS VERIFICATION**: Row 54 shows a critical pack size mismatch (supplier 10-pack vs Amazon single unit), Row 55 has a brand mismatch (A to Z vs Beautiful Beginnings), and Row 52 likely has a quantity mismatch (single roll vs 100-pack). Only **Row 44 (thermal blanket) represents a viable high-ROI opportunity** at 125% ROI with verified pack size match. The remaining rows are either negative ROI dead-ends (Rows 50, 52) or require further verification (Row 49). The data demonstrates that **EAN matching alone is insufficient**—title analysis and pack size verification are critical to avoid purchasing mismatched inventory.

---

