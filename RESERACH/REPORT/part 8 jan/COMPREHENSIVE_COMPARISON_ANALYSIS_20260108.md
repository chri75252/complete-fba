# FBA REPORT COMPREHENSIVE VALIDATION ANALYSIS

**Generated:** 2026-01-09
**Reference:** Consistent Source Data vs Model Outputs

## 1. Valid Product Opportunities by Model (Global)
Total unique items identified as **Correct Matches**, summing Verified, Highly Likely, AND Valid Needs Verification items. Includes 'Audited Out' correct matches.

| Model | Total Rows in File | **GRAND TOTAL CORRECT** (Ver+HL+NV) | Strong Matches (Ver/HL) | Weak Matches (NV) |
|---|---|---|---|---|
| GEM_1 | 443 | **280** | 215 | 65 |
| AGENT | 367 | **159** | 150 | 9 |
| WEB | 2369 | **419** | 349 | 70 |
| PHASE2 | 129 | **127** | 124 | 3 |
| PHASE3 | 150 | **141** | 135 | 6 |
| PHASE4 | 314 | **219** | 198 | 21 |
| PHASE5 | 335 | **221** | 199 | 22 |

**Winner for Coverage:** WEB (419 correct matches found)

*Note: 'Total Rows in File' refers to the number of tabular rows actually present in the markdown file. This count includes Audited Out/Filtered Out rows if present in the file bodies.* 

## 2. Categorization Accuracy
Percentage of rows where the model's verdict matched independent verification.

| Model | Accuracy % | Correct Rows | Total Rows in File |
|---|---|---|---|
| GEM_1 | 62.1% | 275 | 443 |
| AGENT | 28.6% | 105 | 367 |
| WEB | 21.6% | 511 | 2369 |
| PHASE2 | 67.4% | 87 | 129 |
| PHASE3 | 60.7% | 91 | 150 |
| PHASE4 | 38.5% | 121 | 314 |
| PHASE5 | 36.1% | 121 | 335 |

## 3. Claimed vs Validated Verdicts
Breakdown of what the report *claimed* vs what was validated.

| Model | Claimed VERIFIED | Claimed HL | Claimed NV | **Actual Valid NV Matches** (Strict) |
|---|---|---|---|---|
| GEM_1 | 28 | 109 | 253 | 65 |
| AGENT | 35 | 192 | 98 | 9 |
| WEB | 33 | 313 | 1799 | 70 |
| PHASE2 | 32 | 78 | 2 | 3 |
| PHASE3 | 32 | 86 | 15 | 6 |
| PHASE4 | 32 | 238 | 3 | 21 |
| PHASE5 | 32 | 239 | 18 | 22 |

## 4. Strict 'Needs Verification' Analysis
 Breakdown of items categorized as NV that are potentially upgradeable matches.
 (See Final Report for full list)

## 5. Section-Level Diagnosis (AGENT Report)
Accuracy breakdown by specific report section.

| Report Section | Total Rows | **Valid Opps** (True Positives) | **Invalid/Unrelated** (False Positives) | Accuracy % |
|---|---|---|---|---|
| HIGHLY LIKELY | 192 | 96 | 96 | 50.0% |
| HIGHLY LIKELY (AUDITED OUT) | 36 | 11 | 25 | 30.6% |
| NEEDS VERIFICATION | 98 | 11 | 87 | 11.2% |
| VERIFIED | 35 | 35 | 0 | 100.0% |
| VERIFIED (AUDITED OUT) | 6 | 6 | 0 | 100.0% |
