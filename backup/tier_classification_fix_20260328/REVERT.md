# Revert: Tier Classification Fix (2026-03-28)

## What was changed
`tools/fba_report_filter.py` — scoring weights and tier gate conditions in `classify_row()`

## Changes made

### Score adjustments
| Signal | Old | New |
|--------|-----|-----|
| EAN match (checksum invalid) | +25 | +30 |
| Strong title (sim>=0.6, shared>=4) | +30 | +35 |
| Moderate title (sim>=0.35, shared>=3) | +15 | +20 |
| Brand match | +5 | +10 |
| Brand mismatch | -5 | -10 |

### Tier gate changes
| Tier | Old gate | New gate |
|------|----------|----------|
| T1 | EAN match + profitable + no cat mismatch | EAN match + no cat mismatch (profitability removed) |
| T2 (non-EAN) | confidence >= 40 (was dead code, unreachable) | confidence >= 40 (now reachable with new scores) |
| T3 | confidence >= 15 + profitable | confidence >= 15 (profitability removed) |
| T4 | fallthrough | fallthrough (no change) |

## How to revert
```bash
copy backup\tier_classification_fix_20260328\fba_report_filter.py tools\fba_report_filter.py
```

## Backup location
`backup/tier_classification_fix_20260328/fba_report_filter.py`
