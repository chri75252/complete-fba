# V4.0 REPORTS COMPARISON ANALYSIS

**Generated:** 2025-12-29
**Ground Truth Source:** PARTDEC28_1.xlsx (1758 rows)
**Methodology:** v2 Manual Analysis (Brand + Title + EAN)

## Executive Summary

| Metric | Ground Truth | Codex v4.0 | WebApp v4.0 |
|--------|--------------|------------|-------------|
| VERIFIED | 25 | 27 | 24 |
| HIGHLY LIKELY | 29 | 24 | 116 |
| NEEDS VERIFICATION | 124 | 97 | 9 |
| FILTERED OUT | 8 | 32 | 33 |

## Accuracy Breakdown

### Codex v4.0

**VERIFIED:** 1/27 correct (3.7%)
**HIGHLY_LIKELY:** 1/24 correct (4.2%)
**NEEDS_VERIFICATION:** 3/97 correct (3.1%)
**FILTERED_OUT:** 1/32 correct (3.1%)

### WebApp v4.0

**VERIFIED:** 1/24 correct (4.2%)
**HIGHLY_LIKELY:** 4/116 correct (3.4%)
**NEEDS_VERIFICATION:** 0/9 correct (0.0%)
**FILTERED_OUT:** 0/33 correct (0.0%)

## Key Problems Identified

### Problem 1: Codex NEEDS VERIFICATION Overload
- Ground Truth: 124 items
- Codex: 97 items
- Difference: +-27 excess items

### Problem 2: WebApp HIGHLY LIKELY Over-Acceptance
- Ground Truth: 29 items
- WebApp: 116 items
- Difference: +87 excess items
