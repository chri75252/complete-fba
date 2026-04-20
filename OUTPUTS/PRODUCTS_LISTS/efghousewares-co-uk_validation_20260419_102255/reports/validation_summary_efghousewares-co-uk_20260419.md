# FBA Product Validation — Final Report
**Supplier:** efghousewares-co-uk
**Analysis Export:** fba_analysis_2026-04-18.csv
**Financial Report:** fba_financial_report_efghousewares-co-uk_20260413_003445.csv
**Date Executed:** 2026-04-19 10:22

## INPUT SUMMARY
- Total rows loaded: 3205
- T1_A_VERIFIED: 786 | T1_B_AUDIT_OUT: 233 | T2_LIKELY: 394 | T3_NEEDS_REVIEW: 1170 | T4_REJECTED: 622

## CLEANSING SUMMARY
| Step | Removed | Notable |
|------|---------|---------|
| T4 filter | 622 | Dashboard rejected |
| Price plausibility | 1 | >20x ratio |
| False match | 24 | <2 word overlap (non-EAN) |
| Unit qty mismatch | 575 | Pack vs single removed |
| T3 verification | 216 | Low overlap dropped |
| T2 verification | 0 | All T2 kept |
| Unprofitable/no bucket | 1078 | No qualifying bucket |

## BUCKET RESULTS
| Bucket | Count | Avg Profit | Avg Sales | T1 | T2 | T3 |
|--------|-------|------------|-----------|----|----|-----|
| A | 7 | £3.81 | 64/mo | 0 | 7 | 0 |
| B | 569 | £2.78 | — | 172 | 77 | 320 |
| C | 113 | £-1.51 | 281/mo | 74 | 39 | 0 |

## CROSS-REFERENCE RESULTS
- Products matching both reports: 593
- Profit discrepancies found: 194
- Profitable in analysis but unprofitable in fin report: 61

## TOP 10 HIGHEST-CONVICTION OPPORTUNITIES
| # | Product | Bucket | Profit | Sales | ROI% | Unit Qty | Fin Report Confirms? |
|---|---------|--------|--------|-------|------|----------|---------------------|
| 1 | MASON CASH MIXING BOWL CREAM 29CM | A | £14.743333333333336 | 50 | 212.7465127465128% | MATCH | NO |
| 2 | MASON CASH MIXING BOWL OWL STONE 26CM | A | £3.694583333333334 | 100 | 62.30326025857224% | MATCH | YES |
| 3 | MASON CASH MIXING BOWL IN THE MEADOW DAF | A | £4.386250000000001 | 50 | 96.82671081677708% | MATCH | YES |
| 4 | MASON CASH ORIGINAL PUDDING BASIN WHITE  | A | £1.6433333333333342 | 50 | 57.66081871345033% | MATCH | N/A |
| 5 | MASON CASH ORIGINAL PUDDING BASIN WHITE  | A | £1.1624999999999996 | 50 | 55.88942307692306% | MATCH | NO |
| 6 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 1 | A | £0.9250000000000004 | 50 | 75.81967213114757% | MATCH | NO |
| 7 | PYREX MEASURE & MIX BEAKER 250ML (PM) | A | £0.1291666666666662 | 100 | 3.354978354978343% | MATCH | NO |

## ITEMS REQUIRING MANUAL REVIEW
- Unit qty unclear: 1 items
- Profit discrepancy: 194 items
- T3 in Bucket B (low confidence): 320 items

## OUTPUT FILES
- Verified CSV: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_validation_20260419_102255\csvs\verified_profitable_efghousewares-co-uk_20260419.csv` (689 rows)
- Excluded CSV: `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efghousewares-co-uk_validation_20260419_102255\csvs\excluded_rows_audit_efghousewares-co-uk_20260419.csv` (2516 rows)

## HONEST ASSESSMENT
- Genuinely actionable products: 7 (Bucket A) out of 3205 original
- Bucket B (569) are opportunities requiring sales validation
- Bucket C (113) are margin-flip candidates requiring price re-check
- Confidence level: MEDIUM — data is stale (6+ days), unit qty adjustments applied to 66 rows
