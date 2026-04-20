# Stale Data Analysis - Final Report

Supplier: `poundwholesale-co-uk`
Generated: `2026-04-14T19:35:00Z`
Source analysis export: `temp/fba_analysis_2026-poundhwolesale-14.csv`
Source financial report: `OUTPUTS/FBA_ANALYSIS/financial_reports/poundwholesale-co-uk/fba_financial_report_poundwholesale-co-uk_20260414_082856.csv`
Backed-up snapshot: `backup/stale_data_phase6_20260414/poundwholesale-co-uk_clean_snapshot_20260414_232258.csv`

## Cleansing Summary

| Step | Removed / Flagged |
|---|---:|
| T4 filter | 4904 removed |
| Superior brand | 0 removed |
| Price plausibility | 2 removed |
| Underpriced suspicious | 3 flagged |
| False-match detection | 114 removed |
| Unit-qty negative recalc | 92 removed |
| T3 quarantine | 278 removed |
| Final clean rows | 1714 |

## Bucket Summary

| Bucket | Count |
|---|---:|
| A | 12 |
| B | 365 |
| C | 132 |
| Total classified | 509 |

## Category Sandbox Targets

1. `https://www.poundwholesale.co.uk/health-beauty/wholesale-skin-care` - 12 products - rank score 182893.81
2. `https://www.poundwholesale.co.uk/pound-lines/stationery-pound-lines` - 15 products - rank score 50402.46
3. `https://www.poundwholesale.co.uk/diy/wholesale-sealants-paints` - 12 products - rank score 44486.75
4. `https://www.poundwholesale.co.uk/wholesale-cleaning/cleaning-wipes-sprays/kitchen-cleaners` - 6 products - rank score 30845.00
5. `https://www.poundwholesale.co.uk/diy/wholesale-car-care` - 5 products - rank score 20611.67

## External Research Overlay

- `Kitchen Cleaners` - strongest current sandbox candidate; evergreen demand and FBA-friendly.
- `Wholesale Skin Care` - attractive but higher compliance / authenticity risk.
- `Wholesale Car Care` - conditional candidate; viable only if automotive gating / expertise is acceptable.
- `Stationery Pound Lines` - structurally weak FBA economics despite stale score.
- `Wholesale Sealants Paints` - structurally weaker Amazon fit; more trade-oriented than consumer-FBA friendly.

## Browser Spot-Check Summary

- Checked candidates: 25
- Keep: 23
- Keep with caution: 1
- Deprioritize: 1
- Visible current prices captured in browser pass: 0

### Material validation outcomes

- `Elmer's Colour Changing Liquid Glue 147ml` - deprioritize; supplier page live but Amazon ASIN returned 404.
- `Prima Magnetic Can Opener CDU` - keep with caution; supplier page returned 200 and matching title, but browser text heuristic was noisy.
- All other checked products remained live and plausibly matched on both supplier and Amazon pages.

## Product-List Targets

- Orphan ASIN count: 94
- Orphan file: `OUTPUTS/CONTROL_PLANE/inputs/poundwholesale-co-uk_orphan_asins_20260414_232258.json`

## Deliverables

- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_VALIDATED_master_20260414_232258.csv`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_VALIDATED_bucketA_20260414_232258.csv`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_VALIDATED_bucketBC_20260414_232258.csv`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_validated_ranked_products_20260414_232258.json`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_category_sandbox_targets_20260414_232258.json`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_validation_candidates_20260414_232258.json`
- `OUTPUTS/PRODUCTS_LISTS/poundwholesale-co-uk_phase5_validation_results_20260414_232258.json`

## Verification Notes

- `Unit_Qty_Flag` column exists in final CSV outputs.
- No `Superior` rows survived.
- No `T3` rows remain in Bucket A or Bucket C.
- Category target JSON contains 5 non-blank category URLs.
- Output files were copied to `backup/stale_data_phase6_20260414/` for audit traceability.
