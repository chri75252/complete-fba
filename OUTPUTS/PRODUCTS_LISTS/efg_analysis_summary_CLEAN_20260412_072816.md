# EFG Housewares — CLEAN Product List Analysis
Generated: 2026-04-12T07:28:17.144059
Source: fba_financial_report_ALL_linking_map_20260108_005639.csv (21,305 raw)

## Decontamination Applied
- Pass 1: Superior brand exclusion (50 removed)
- Pass 1: False-positive T2/T3 ASIN collisions (275 removed)
- Pass 2: Price-ratio + title-similarity gate (250 removed)
  - Catches EAN matches mapped to wrong ASINs (e.g., badge -> phone)

## Final Counts
- **Bucket A**: 2812 (T1=1245, T2=1494, T3=73, Validation=1470)
- **Bucket B**: 3098 (T1=1997, T2=1051, T3=50, Validation=888)
- **Bucket C**: 1798 (T1=1057, T2=713, T3=28, Validation=538)
- **TOTAL**: 7708

## Key Risks
- Jan 8 2026 data snapshot — 3+ months stale
- T2/T3 items marked 'VALIDATION_REQUIRED' need Keepa/Google Trends manual check
- Bucket C items profitable only with small price increase or fee reduction
- No programmatic Keepa/Google Trends pass in this execution