# FBA AI Analysis Report
**Source:** tmpip7wrktb.csv
**Total Rows Analyzed:** 4
**Tiers Included:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Model:** nemotron-3-super-free
**Generated:** 2026-03-17T07:49:49.075560

---

## Batch 1

**Analysis Table**

| Row# | SupplierTitle (truncated) | AmazonTitle (truncated) | Verdict | Confidence (0‑100) | Key Evidence | Flags |
|------|---------------------------|-------------------------|---------|--------------------|--------------|-------|
| 12 | Goodyear Portable Car Vacuum | Goodyear 12V DC Car/Van Cigarette | TRUE | 90 | EAN match; brand **Goodyear**; product **12V car vacuum**; identical description | – |
| 5  | Car Pride Leather Cleaning Spray | 12 x Cans Of Leather cleaning spray | FALSE POSITIVE | 85 | EAN match but **supplier single 250 ml** vs **Amazon 12‑pack 300 ml cans**; pack‑size & volume mismatch; unusually high ROI (≈453 %) | Pack size mismatch, Volume mismatch, High ROI |
| 8  | Auto Extreme Automotive Black Matt | Black Matt Aerosol Spray Cans 250ml | TRUE | 85 | EAN match; brand **Auto Extreme**; product **black matt spray paint 250 ml**; titles align | – |
| 10 | Car Pride Clean & Polish Microfibre | CARPRIDE® Clean and Polish MicroFibre | TRUE | 90 | EAN match; brand **Car Pride**; product **micro‑fibre cloth**; exact match | – |

**Adjusted Profit for Pack‑Size Discrepancy (Row 5)**  
- Supplier price per unit: **$0.97** (single 250 ml can)  
- Amazon price for 12‑pack: **$19.95** → per‑unit revenue = $19.95 ÷ 12 ≈ **$1.66**  - **Adjusted profit per unit** = $1.66 − $0.97 ≈ **$0.69** (ROI ≈ 71 % per unit).

**Summary**  
Three of the four rows represent genuine matches: the Goodyear vacuum, Auto Extreme spray paint, and Car Pride microfiber cloth all share identical EANs, brand names, and product descriptions, with no pack‑size inconsistencies. Row 5, despite an EAN match, is a false positive: the supplier offers a single 250 ml leather‑cleaning spray, whereas the Amazon listing is a 12‑pack of 300 ml cans, creating a clear pack‑size and volume discrepancy that explains the inflated ROI. After adjusting for the multipack, the realistic profit per unit drops to roughly $0.69, far below the reported $6.15. Consequently, rows 12, 8, and 10 are marked **VERIFIED**, while row 5 is **AUDITED OUT**.

---

