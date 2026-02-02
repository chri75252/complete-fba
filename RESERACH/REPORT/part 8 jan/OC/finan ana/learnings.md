# Financial Analysis Step 2 - Analysis Findings
## Session: 2026-01-31

### Analysis Summary
- **Input File**: part 8 jan.xlsx (efghousewares.co.uk)
- **Total Rows Analyzed**: 3,063
- **Methodology**: FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2 with Preflight Calibration
- **Output Report**: PHASEA_MANUAL_REPORT_2601310829.md

### Key Findings

#### Category Distribution
| Category | Count | Percentage |
|----------|-------|------------|
| VERIFIED — RECOMMENDED | 32 | 1.0% |
| VERIFIED — AUDITED OUT | 8 | 0.3% |
| HIGHLY LIKELY — RECOMMENDED | 81 | 2.6% |
| NEEDS VERIFICATION | 104 | 3.4% |
| AUDITED OUT / EXCLUDED | 24 | 0.8% |
| UNRELATED / NOT INCLUDED | 2,814 | 91.9% |

#### Critical Metrics
- **Strict Exact EAN Matches**: 40 (1.3%)
- **Valid Supplier EANs**: 3,047 (99.5%)
- **Valid Amazon EANs**: 1,337 (43.7%)
- **Mean Title Similarity**: 0.255
- **High Title Similarity (>0.5)**: 131 rows
- **Bundle Opportunities (RSU>1)**: 799 rows
- **Negative Adjusted Profit**: 648 rows

#### Calibration Configuration Applied
- **Explicit Units**: pk, pack
- **Dimension Shield Keywords**: cm, mm, ml, ltr, kg, g, oz, inch, "
- **Brand Position**: start (supplier titles)
- **Brand Sparse Mode**: True
- **Capacity Pattern as RSU**: True
- **Spec X Shield**: magnification, zoom, microscope, scope, times, power

#### Notable Patterns Identified
1. **High UNRELATED Rate (91.9%)**: Most supplier products don't match Amazon listings - this is expected for efghousewares.co.uk which has many unique/novelty items
2. **Pack Size Discrepancies**: 799 items have RSU > 1, indicating multipack opportunities or mismatches
3. **EAN Coverage**: Only 43.7% of Amazon listings have valid EANs on page
4. **Brand Matching**: 81 HIGHLY LIKELY items identified through brand + product matching

#### Validation Checklist Completed
- [x] Dimension Check: No dimension patterns caused incorrect RSU
- [x] Quantity-Inside Check: No quantity-inside patterns treated as pack counts
- [x] Multipack Check: N x M patterns calculated correctly
- [x] EAN Validation: Strict barcode validation with checksum
- [x] Both EANs Shown: All tables include separate columns
- [x] Adjusted Profit: Recalculated for RSU > 1
- [x] Categories Complete: All four categories present
- [x] Table Schema: Exact schema used

### Acceptance Tests Status
- A1-A15: All acceptance tests satisfied
- V1-V12: All verification checks passed

### Next Steps (Step 3)
The PHASEA_MANUAL_REPORT is ready for Step 3 (Manual Guide/Final). The report contains:
- 32 VERIFIED items ready for immediate action
- 81 HIGHLY LIKELY items for priority review
- 104 NEEDS VERIFICATION items requiring 1-2 confirmable details
- 32 AUDITED OUT items for audit trail
