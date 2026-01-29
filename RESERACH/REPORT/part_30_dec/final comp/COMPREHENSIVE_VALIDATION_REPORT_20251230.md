# FBA REPORT VALIDATION ANALYSIS

**Generated:** 2025-12-30
**Source Dataset:** part_30_dec.xlsx (2102 rows)
**Reports Analyzed:** 8 folders
**Total Products Validated:** 1215

## Executive Summary

- **Total products analyzed:** 1215
- **Correctly categorized:** 661 (54.4%)
- **Acceptably categorized (adjacent):** 373
- **Incorrectly categorized:** 181
- **Combined accuracy (correct + acceptable):** 85.1%

## 📈 MODEL ACCURACY STATISTICS

### Overall Accuracy by Model/Folder

| Model/Folder | Total | Correct | Acceptable | Incorrect | Accuracy % | Combined % |
|--------------|-------|---------|------------|-----------|------------|------------|
| cli | 83 | 7 | 19 | 57 | 8.4% | 31.3% |
| Codex HIGH | 126 | 90 | 32 | 4 | 71.4% | 96.8% |
| Codex samecha | 73 | 47 | 13 | 13 | 64.4% | 82.2% |
| Codex very high | 74 | 26 | 20 | 28 | 35.1% | 62.2% |
| Gemini | 241 | 152 | 80 | 9 | 63.1% | 96.3% |
| Opus | 182 | 119 | 55 | 8 | 65.4% | 95.6% |
| opus2 | 214 | 133 | 64 | 17 | 62.1% | 92.1% |
| webapp gpt | 222 | 87 | 90 | 45 | 39.2% | 79.7% |

### Category-Level Accuracy

#### VERIFIED

| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |
|-------|---------|------------|-----------------|---------------|----------------|---------|----------|
| cli | 31 | 0 | 0 | 7 | 9 | 15 | 0% |
| Codex HIGH | 23 | 21 | 0 | 1 | 1 | 0 | 91% |
| Codex samecha | 29 | 22 | 0 | 1 | 6 | 0 | 76% |
| Codex very high | 16 | 12 | 0 | 1 | 3 | 0 | 75% |
| Gemini | 31 | 25 | 0 | 1 | 5 | 0 | 81% |
| Opus | 24 | 21 | 0 | 1 | 2 | 0 | 88% |
| opus2 | 28 | 25 | 0 | 1 | 2 | 0 | 89% |
| webapp gpt | 26 | 23 | 0 | 1 | 2 | 0 | 88% |

#### HIGHLY LIKELY

| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |
|-------|---------|------------|-----------------|---------------|----------------|---------|----------|
| cli | 21 | 1 | 1 | 3 | 4 | 12 | 5% |
| Codex HIGH | 31 | 2 | 25 | 4 | 0 | 0 | 81% |
| Codex samecha | 36 | 2 | 24 | 7 | 3 | 0 | 67% |
| Codex very high | 3 | 0 | 3 | 0 | 0 | 0 | 100% |
| Gemini | 70 | 2 | 46 | 22 | 0 | 0 | 66% |
| Opus | 42 | 0 | 22 | 20 | 0 | 0 | 52% |
| opus2 | 99 | 2 | 38 | 47 | 7 | 5 | 38% |
| webapp gpt | 45 | 2 | 30 | 10 | 3 | 0 | 67% |

#### NEEDS VERIFICATION

| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |
|-------|---------|------------|-----------------|---------------|----------------|---------|----------|
| cli | 25 | 0 | 1 | 3 | 6 | 15 | 12% |
| Codex HIGH | 65 | 0 | 14 | 39 | 12 | 0 | 60% |
| Codex samecha | 5 | 1 | 2 | 0 | 2 | 0 | 0% |
| Codex very high | 26 | 4 | 13 | 6 | 3 | 0 | 23% |
| Gemini | 53 | 0 | 1 | 43 | 3 | 6 | 81% |
| Opus | 99 | 2 | 23 | 68 | 5 | 1 | 69% |
| opus2 | 66 | 0 | 0 | 56 | 8 | 2 | 85% |
| webapp gpt | 140 | 0 | 5 | 28 | 18 | 89 | 20% |

#### FILTERED OUT

| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |
|-------|---------|------------|-----------------|---------------|----------------|---------|----------|
| cli | 6 | 0 | 0 | 0 | 3 | 3 | 50% |
| Codex HIGH | 7 | 0 | 2 | 0 | 5 | 0 | 71% |
| Codex samecha | 3 | 0 | 2 | 0 | 1 | 0 | 33% |
| Codex very high | 29 | 0 | 20 | 4 | 5 | 0 | 17% |
| Gemini | 87 | 0 | 3 | 21 | 38 | 25 | 44% |
| Opus | 17 | 0 | 3 | 6 | 8 | 0 | 47% |
| opus2 | 21 | 0 | 2 | 5 | 14 | 0 | 67% |
| webapp gpt | 11 | 0 | 4 | 1 | 6 | 0 | 55% |

### 🏆 Ranking by Accuracy

| Rank | Model/Folder | Accuracy | Combined | Total |
|------|--------------|----------|----------|-------|
| 1 | **Codex HIGH** | 71.4% | 96.8% | 126 |
| 2 | **Opus** | 65.4% | 95.6% | 182 |
| 3 | **Codex samecha** | 64.4% | 82.2% | 73 |
| 4 | **Gemini** | 63.1% | 96.3% | 241 |
| 5 | **opus2** | 62.1% | 92.1% | 214 |
| 6 | **webapp gpt** | 39.2% | 79.7% | 222 |
| 7 | **Codex very high** | 35.1% | 62.2% | 74 |
| 8 | **cli** | 8.4% | 31.3% | 83 |

## Sample Misclassifications

Showing 30 examples of incorrect categorizations:

| Folder | ASIN | AI Said | Should Be | Title | Reason |
|--------|------|---------|-----------|-------|--------|
| cli | B0DJDH23JW | VERIFIED | FILTERED_OUT | SOZALI CONTAINERS EASY PA | Pack 5x neg profit |
| cli | B07YQ5HFFN | VERIFIED | FILTERED_OUT | PAN AROMA CANDLE 85G LEMO | Variant: Scent: ['LEMON'] vs ['ORANGE'] |
| cli | B00M36YPIM | VERIFIED | OTHER | SEBO UPRIGHT  SDB249 | Insufficient evidence |
| cli | B06X9K7NR7 | VERIFIED | FILTERED_OUT | ECO WASH UP BRUSH | Pack 4x neg profit |
| cli | B008F6946C | VERIFIED | NEEDS_VERIFICATION | ELF ARRIVAL ENVELOPE OUTF | Partial match |
| cli | B0DPQVJ4NW | VERIFIED | NEEDS_VERIFICATION | AMTECH PADLOCK BRASS 20MM | Partial match |
| cli | B07WDRQ4J7 | VERIFIED | NEEDS_VERIFICATION | STATUS TV AERIAL LEAD 5M  | Partial match |
| cli | B003XKPUSQ | VERIFIED | OTHER | EASY STORAGE VACUUM BAG 7 | Insufficient evidence |
| cli | B01IFIJ91Y | VERIFIED | FILTERED_OUT | KITCHEN KING ALUMINIUM PO | Pack 17x neg profit |
| cli | B00KB225MS | VERIFIED | FILTERED_OUT | VILEDA CORDOMATIC CLOTHES | Pack 4x neg profit |
| cli | B000TAU3QW | VERIFIED | NEEDS_VERIFICATION | PREMIER FLICKABRIGHT GLAS | Title similarity |
| cli | B07JD22MJ2 | VERIFIED | OTHER | EXTRASTAR TYPE C CABLE 1. | Insufficient evidence |
| cli | B083XH692T | VERIFIED | OTHER | PAN AROMA AIR FRESHENER B | Insufficient evidence |
| cli | B007IGLUIK | VERIFIED | FILTERED_OUT | LED TEALIGHTS 3PK | Pack 3x neg profit |
| cli | BROWN480ML | VERIFIED | OTHER | DIFFUSER 500ML PEONY & BL | Insufficient evidence |
| cli | B0DT71SSPT | VERIFIED | OTHER | THL BABY BATH SEAT | Insufficient evidence |
| cli | B005XKFN0O | VERIFIED | OTHER | APOLLO ECO BOTTLE BRUSH | Insufficient evidence |
| cli | B09KCLYC1D | VERIFIED | OTHER | WOODEN CHRISTMAS TREE DEC | Insufficient evidence |
| cli | B09KCMWXQX | VERIFIED | OTHER | EUROWRAP TISSUE PAPER 6SH | Insufficient evidence |
| cli | B009SJXB32 | VERIFIED | LOW_PRIORITY | PPS RECTANGLE 20 DOYLEYS  | Weak match |
| cli | B01D1R4NXS | VERIFIED | LOW_PRIORITY | PPS PLASTIC KNIVES HEAVY  | Weak match |
| cli | B0042FBWQ0 | VERIFIED | OTHER | FLORAL FABRIC REFRESHER 5 | Insufficient evidence |
| cli | B00LZRJTEA | VERIFIED | FILTERED_OUT | COASTER CORK MAGNETIC 21C | Pack 8x neg profit |
| cli | B0111N9Z1O | VERIFIED | OTHER | MASON SPIRAL METAL DRAIN  | Insufficient evidence |
| cli | B0FQK17X7F | VERIFIED | NEEDS_VERIFICATION | SECURPLUMB FIBER TAP CONN | Title similarity |
| cli | B0FMS875KH | VERIFIED | NEEDS_VERIFICATION | SECURIT LITERAL ARROW SIG | Title similarity |
| cli | B008F7YP9C | VERIFIED | FILTERED_OUT | MARIGOLD OUTDOOR GLOVES L | Pack 4x neg profit |
| cli | B074V9468X | VERIFIED | LOW_PRIORITY | PET STORE K9 CUP CAKES | Weak match |
| cli | B077G5PTRK | VERIFIED | FILTERED_OUT | SILICONE SPATULA WITH WOO | Pack 2x neg profit |
| cli | B00W3RVAG6 | VERIFIED | NEEDS_VERIFICATION | PPS FOIL ROASTING 3 DISHE | Title similarity |

## Recommendations

1. **Best Model:** `Codex HIGH` with 71.4% accuracy
2. **Worst Model:** `cli` with 8.4% accuracy