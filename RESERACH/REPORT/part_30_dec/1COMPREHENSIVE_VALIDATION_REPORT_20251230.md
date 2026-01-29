# FBA REPORT VALIDATION ANALYSIS

**Generated:** 2025-12-30
**Source Dataset:** part_30_dec.xlsx (2102 rows)
**Reports Analyzed:** 8 folders
**Total Products Validated:** 1215

## Executive Summary

- **Total products analyzed:** 1215
- **Correctly categorized:** 712 (58.6%)
- **Acceptably categorized (adjacent):** 371
- **Incorrectly categorized:** 132
- **Combined accuracy (correct + acceptable):** 89.1%

## 📈 MODEL ACCURACY STATISTICS

### Overall Accuracy by Model/Folder

| Model/Folder | Total | Correct | Acceptable | Incorrect | Accuracy % | Combined % |
|--------------|-------|---------|------------|-----------|------------|------------|
| cli | 83 | 58 | 18 | 7 | 69.9% | 91.6% |
| Codex HIGH | 126 | 90 | 32 | 4 | 71.4% | 96.8% |
| Codex samecha | 73 | 47 | 13 | 13 | 64.4% | 82.2% |
| Codex very high | 74 | 26 | 20 | 28 | 35.1% | 62.2% |
| Gemini | 241 | 152 | 80 | 9 | 63.1% | 96.3% |
| Opus | 182 | 119 | 55 | 8 | 65.4% | 95.6% |
| opus2 | 214 | 133 | 64 | 17 | 62.1% | 92.1% |
| webapp gpt | 222 | 87 | 89 | 46 | 39.2% | 79.3% |

### Category-Level Accuracy

#### VERIFIED

| Model | Claimed | → VERIFIED | → HIGHLY_LIKELY | → NEEDS_VERIF | → FILTERED_OUT | → OTHER | Accuracy |
|-------|---------|------------|-----------------|---------------|----------------|---------|----------|
| cli | 31 | 26 | 0 | 0 | 5 | 0 | 84% |
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
| cli | 21 | 0 | 21 | 0 | 0 | 0 | 100% |
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
| cli | 25 | 1 | 16 | 7 | 1 | 0 | 28% |
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
| cli | 6 | 0 | 1 | 1 | 4 | 0 | 67% |
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
| 2 | **cli** | 69.9% | 91.6% | 83 |
| 3 | **Opus** | 65.4% | 95.6% | 182 |
| 4 | **Codex samecha** | 64.4% | 82.2% | 73 |
| 5 | **Gemini** | 63.1% | 96.3% | 241 |
| 6 | **opus2** | 62.1% | 92.1% | 214 |
| 7 | **webapp gpt** | 39.2% | 79.3% | 222 |
| 8 | **Codex very high** | 35.1% | 62.2% | 74 |

## Sample Misclassifications

Showing 30 examples of incorrect categorizations:

| Folder | ASIN | AI Said | Should Be | Title | Reason |
|--------|------|---------|-----------|-------|--------|
| cli | B07YQ5HFFN | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x neg profit |
| cli | B00M36YPIM | VERIFIED | FILTERED_OUT | CHEF AID SHOT GLASSES ASS | Pack 20x neg profit |
| cli | B0DT71SSPT | VERIFIED | FILTERED_OUT | PHOODS FOIL TRAY ROASTER | Pack 10x neg profit |
| cli | B01D1R4NXS | VERIFIED | FILTERED_OUT | SAMS SCRUMMY GIANT LEG DO | Pack 2x neg profit |
| cli | B074V9468X | VERIFIED | FILTERED_OUT | WHAM CRYSTAL 32LTR CLEAR  | Pack 3x neg profit |
| cli | B07YPPK4JY | NEEDS VERIFICATION | VERIFIED | FIRE UP NATURAL FIRELIGHT | Exact EAN |
| cli | B08XWB7JW9 | FILTERED OUT | HIGHLY_LIKELY | MARIGOLD OUTDOOR GLOVES E | Brand: MARIGOLD |
| Codex HIGH | B0DJDH23JW | VERIFIED | NEEDS_VERIFICATION | SUPERIOR FOIL 10 CONTAINE | Partial match |
| Codex HIGH | B09KCLYC1D | VERIFIED | FILTERED_OUT | PAN AROMA CANDLE 85G LIME | Variant: Scent: ['LIME'] vs ['ORANGE'] |
| Codex HIGH | B004GY24EQ | FILTERED OUT | HIGHLY_LIKELY | AMTECH BOX SPANNER /TOMMY | Brand: AMTECH |
| Codex HIGH | B08FBJ59DR | FILTERED OUT | HIGHLY_LIKELY | BACOFOIL ZIPPER BAGS ALL  | Brand: BACOFOIL |
| Codex samecha | B0DJDH23JW | VERIFIED | NEEDS_VERIFICATION | SUPERIOR FOIL 10 CONTAINE | Partial match |
| Codex samecha | B07YQ5HFFN | VERIFIED | FILTERED_OUT | PPS ROUND 150  DOYLEYS 11 | Pack 40x neg profit |
| Codex samecha | B00M36YPIM | VERIFIED | FILTERED_OUT | CHEF AID SHOT GLASSES ASS | Pack 20x neg profit |
| Codex samecha | B0DT71SSPT | VERIFIED | FILTERED_OUT | PHOODS FOIL TRAY ROASTER | Pack 10x neg profit |
| Codex samecha | B09KCLYC1D | VERIFIED | FILTERED_OUT | PAN AROMA CANDLE 85G LIME | Variant: Scent: ['LIME'] vs ['ORANGE'] |
| Codex samecha | B01D1R4NXS | VERIFIED | FILTERED_OUT | SAMS SCRUMMY GIANT LEG DO | Pack 2x neg profit |
| Codex samecha | B074V9468X | VERIFIED | FILTERED_OUT | WHAM CRYSTAL 32LTR CLEAR  | Pack 3x neg profit |
| Codex samecha | B08TCDBQTC | HIGHLY LIKELY | FILTERED_OUT | BACOFOIL EASY CUT KITCHEN | Pack 3x neg profit |
| Codex samecha | B07R99H8KK | HIGHLY LIKELY | FILTERED_OUT | PLAYWRITE  CHRISTMAS CYO  | Pack 12x neg profit |
| Codex samecha | B09NCVWKD6 | HIGHLY LIKELY | FILTERED_OUT | DETTOL POWER & PURE KITCH | Pack 4x neg profit |
| Codex samecha | B07WDRQ4J7 | NEEDS VERIFICATION | VERIFIED | AIRWICK REED DIFFUSER MUL | Exact EAN |
| Codex samecha | B0013IUIPA | FILTERED OUT | HIGHLY_LIKELY | PRICE & KENSINGTON 2 CUP  | Brand: PRICE & KENSINGTON |
| Codex samecha | B001V9T690 | FILTERED OUT | HIGHLY_LIKELY | EVERBUILD JET RAPID SET C | Brand: EVERBUILD |
| Codex very high | B0DJDH23JW | VERIFIED | NEEDS_VERIFICATION | SUPERIOR FOIL 10 CONTAINE | Partial match |
| Codex very high | B0DT71SSPT | VERIFIED | FILTERED_OUT | PHOODS FOIL TRAY ROASTER | Pack 10x neg profit |
| Codex very high | B09KCLYC1D | VERIFIED | FILTERED_OUT | PAN AROMA CANDLE 85G LIME | Variant: Scent: ['LIME'] vs ['ORANGE'] |
| Codex very high | B01D1R4NXS | VERIFIED | FILTERED_OUT | SAMS SCRUMMY GIANT LEG DO | Pack 2x neg profit |
| Codex very high | B07YPPK4JY | NEEDS VERIFICATION | VERIFIED | FIRE UP NATURAL FIRELIGHT | Exact EAN |
| Codex very high | B00W3RVAG6 | NEEDS VERIFICATION | VERIFIED | MASON CASH CERAMIC RECT D | Exact EAN |

## Recommendations

1. **Best Model:** `Codex HIGH` with 71.4% accuracy
2. **Worst Model:** `Codex very high` with 35.1% accuracy