# FBA Report Comprehensive Comparison and Validation Report
**Generated:** 2026-01-10 07:09:40

## 1. Executive Summary

This report provides a comprehensive comparison of four AI-generated FBA product analysis reports,
evaluating their classification accuracy against independent ground truth analysis.

### Reports Analyzed:
- **CODEX_NEW**: `PHASEA_MANUAL_REPORT_VALIDATED_2601090352.md`
- **CODEX_MANU**: `PHASEA_MANUAL_REPORT_2601090949.md`
- **OPUS_MANU**: `PHASEA_MANUAL_REPORT_2601100043_CORRECTED.md`
- **CODEX_FINAL**: `PHASEA_REVIEW_VALIDATED_REPORT_0110012511.md`

### Source Data: `part 8 jan.xlsx`
- Total products: **3063**
- Products with classifications: **490**
- Classification disagreements: **100**

## 2. Summary Statistics by Report

| Report | VERIFIED | HIGHLY LIKELY | NEEDS VERIFICATION | AUDITED OUT | Total |
|--------|----------|---------------|---------------------|-------------|-------|
| CODEX_NEW | 32 | 0 | 70 | 34 | 136 |
| CODEX_MANU | 33 | 0 | 181 | 21 | 235 |
| OPUS_MANU | 31 | 0 | 3 | 9 | 43 |
| CODEX_FINAL | 31 | 0 | 42 | 40 | 113 |

## 3. Model Accuracy Statistics

Accuracy is calculated by comparing each report's classifications against our independent ground truth analysis.

### Overall Accuracy

| Report | Correct | Total | Accuracy | Rank |
|--------|---------|-------|----------|------|
| CODEX_FINAL | 66 | 132 | **50.0%** | #1 |
| CODEX_MANU | 134 | 347 | **38.6%** | #2 |
| OPUS_MANU | 33 | 92 | **35.9%** | #3 |
| CODEX_NEW | 51 | 257 | **19.8%** | #4 |

### Model Ranking

🥇 **CODEX_FINAL**: 50.0% accuracy (66/132 correct)
🥈 **CODEX_MANU**: 38.6% accuracy (134/347 correct)
🥉 **OPUS_MANU**: 35.9% accuracy (33/92 correct)
#4 **CODEX_NEW**: 19.8% accuracy (51/257 correct)

### Category-Level Accuracy

**CODEX_NEW:**

| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| VERIFIED | 31 | 39 | 79.5% |
| HIGHLY_LIKELY | 0 | 24 | 0.0% |
| UNRELATED | 0 | 119 | 0.0% |
| NEEDS_VERIFICATION | 20 | 75 | 26.7% |

**CODEX_MANU:**

| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| VERIFIED | 32 | 39 | 82.1% |
| HIGHLY_LIKELY | 0 | 22 | 0.0% |
| NEEDS_VERIFICATION | 102 | 199 | 51.3% |
| UNRELATED | 0 | 87 | 0.0% |

**OPUS_MANU:**

| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| VERIFIED | 30 | 39 | 76.9% |
| HIGHLY_LIKELY | 0 | 6 | 0.0% |
| NEEDS_VERIFICATION | 3 | 42 | 7.1% |
| UNRELATED | 0 | 5 | 0.0% |

**CODEX_FINAL:**

| Category | Correct | Total | Accuracy |
|----------|---------|-------|----------|
| VERIFIED | 30 | 39 | 76.9% |
| HIGHLY_LIKELY | 0 | 12 | 0.0% |
| UNRELATED | 0 | 21 | 0.0% |
| NEEDS_VERIFICATION | 36 | 60 | 60.0% |

## 4. Key Classification Disagreements

The following products had different classifications across reports:

| EAN | Supplier Title | Our Class. | CODEX_NEW | CODEX_MANU | OPUS_MANU | CODEX_FINA |
|-----|----------------|------------|------------|------------|------------|------------|
| 5060357990107 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | VERIFIED | VERIFIED | VERIFIED | VERIFIED | AUDITED_OU |
| 5030481940088 | PPS ROUND 40 DOYLEYS 21CM | VERIFIED | VERIFIED | VERIFIED | VERIFIED | AUDITED_OU |
| 5056175901166 | CRAFT FABRIC GLUE 50ML | VERIFIED | VERIFIED | VERIFIED | AUDITED_OU | VERIFIED |
| 5014749165598 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | VERIFIED | VERIFIED | VERIFIED | AUDITED_OU | VERIFIED |
| 5053249228174 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | VERIFIED | VERIFIED | VERIFIED | AUDITED_OU | VERIFIED |
| 5022704000013 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | VERIFIED | VERIFIED | AUDITED_OU | VERIFIED | NEEDS_VERI |
| 5026180033572 | APOLLO VINEGAR SHAKER | VERIFIED | AUDITED_OU | VERIFIED | VERIFIED | VERIFIED |
| 5010853203508 | MASON CASH CERAMIC RECT DISH 16cm | VERIFIED | AUDITED_OU | VERIFIED | VERIFIED | VERIFIED |
| 5013655218435 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | HIGHLY_LIKELY | OTHER | NEEDS_VERI | NOT LISTED | AUDITED_OU |
| 8710908183812 | ALBERTO BALSAM SHAMPOO TEA TREE 350ML PK | HIGHLY_LIKELY | OTHER | NEEDS_VERI | NOT LISTED | OTHER |
| 29319871000619 | WHITE GLO TOOTHPASTE PROFESSIONAL CHOICE | HIGHLY_LIKELY | OTHER | NEEDS_VERI | NOT LISTED | OTHER |
| 5060066941759 | BALLOONS METALLIC GOLD 12 | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060066942404 | BALLOONS METALLIC ASSORTED 12 | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 8710908154720 | RADOX BATH SOAK FEEL BLISSFUL 500ML PK6 | NEEDS_VERIFICATION | OTHER | NOT LISTED | NOT LISTED | AUDITED_OU |
| 5012904112029 | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 8721037327206 | GARDEN GLOVES LADIES 3 ASSORTED COLOURS | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 8721037328401 | GARDEN GLOVES 3 ASSORTED COLOURS | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5055566999041 | CERAMIC WAX/OIL BURNER | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5015302108809 | RUBBER DUCK FAMILY BATH TOY 3 PACK | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060357992170 | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | NEEDS_VERIFICATION | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5050788011915 | DIE CAST TRACTOR | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060357992217 | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN | NEEDS_VERIFICATION | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060082940699 | HAPPY BIRTHDAY TRI CUT BUNTING | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | OTHER |
| 5055706660626 | BABY PIPKIN NAIL CLIPPERS & SCISSORS SET | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5039306011866 | COLOURED A4 CARD 20 SHEETS | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5053249281827 | CAR PRIDE CAR VENT AIR FRESHENER VANILLA | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5026308197124 | GLOVE LADIES WINTER GLOVES ASSORTED | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5063436122420 | CHRISTMAS WINE BOTTLE HOLDER ASSORTED | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5017403154600 | DOOR MAT COIR WELCOME HEART 40 X 60CM | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060569229804 | BACKPACK STANDARD PAW PATROL SKYE | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5055706660657 | BABY PIPKIN BRUSH & COMB SET | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5024418466734 | WINDOW STYLE WALL MIRROR  70X36 | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060569224021 | BACKPACK DELUXE GLITTER PAW PATROL SKYE | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5024418547327 | INCENSE BOX WITH STICKS WOOD | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5027148067165 | KEELECO HUGGY GIRAFFE 28CM | NEEDS_VERIFICATION | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5010853075914 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | NEEDS_VERIFICATION | OTHER | AUDITED_OU | NOT LISTED | NOT LISTED |
| 5032759006113 | AMTECH PADLOCK BRASS 20MM | NEEDS_VERIFICATION | OTHER | NEEDS_VERI | OTHER | OTHER |
| 5017403154617 | DOOR MAT COIR HOME SWEET HOME 40 X 60CM | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5050838320219 | PEPPA PIG GUITAR | NEEDS_VERIFICATION | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |
| 5060569227619 | BACKPACK DELUXE FROZEN | UNRELATED | OTHER | NEEDS_VERI | NOT LISTED | NOT LISTED |

*...and 60 more disagreements*

## 5. Independent Ground Truth Classification (Sample)

Sample of 30 products with our independent classification:

| EAN | Supplier Title | Our Classification | Confidence | Reasoning |
|-----|----------------|-------------------|------------|-----------|
| 5060357990107 | SUPERIOR FOIL 10 CONTAINERS & LID 9 | VERIFIED | 95% | Exact EAN match; Brand: Superior; Simila |
| 5030481940088 | PPS ROUND 40 DOYLEYS 21CM | VERIFIED | 95% | Exact EAN match; Similarity: 29% |
| 5012904148738 | CHEF AID SHOT GLASSES ASSORTED 20PC | VERIFIED | 95% | Exact EAN match; Brand: Chef Aid; Simila |
| 5060187175750 | BLUE CANYON VECTOR SHOWER SPRAY | VERIFIED | 95% | Exact EAN match; Brand: Blue Canyon; Sim |
| 5010792749549 | HIGHLAND COW PLAQUE FRIENDS | VERIFIED | 95% | Exact EAN match; Brand: Highland; Simila |
| 5056175901166 | CRAFT FABRIC GLUE 50ML | VERIFIED | 95% | Exact EAN match; Similarity: 14% |
| 5053249253183 | ELBOW GREASE TOILET CLEANER FOAM LE | VERIFIED | 95% | Exact EAN match; Brand: Elbow Grease; Si |
| 5014749165598 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 P | VERIFIED | 95% | Exact EAN match; Brand: Beauty; Similari |
| 5059001500861 | AIRWICK REED DIFFUSER MULLED WINE 3 | VERIFIED | 95% | Exact EAN match; Similarity: 57% |
| 5032759031078 | AMTECH LED MINI TORCH | VERIFIED | 95% | Exact EAN match; Brand: Amtech; Similari |
| 5010853235530 | MASON CASH MIXING BOWL CREAM 29CM | VERIFIED | 95% | Exact EAN match; Brand: Mason Cash; Simi |
| 5053249215044 | 151 ADHESIVE SPRAY HEAVY DUTY 500ML | VERIFIED | 95% | Exact EAN match; Similarity: 50% |
| 5013159300353 | ELLIOTT WINDOW SQUEEGE 20CM | VERIFIED | 95% | Exact EAN match; Brand: Elliott; Similar |
| 5012904004188 | CHEF AID STRAINER DIAMETER 18CM | VERIFIED | 95% | Exact EAN match; Brand: Chef Aid; Simila |
| 8711252100531 | GLASS WHISKEY DECANTER | VERIFIED | 95% | Exact EAN match; Similarity: 69% |
| 5053249228174 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | VERIFIED | 95% | Exact EAN match; Brand: Pan Aroma; Simil |
| 5055170281372 | FRAGRANT CLOUD EDT 100ML POUR FEMME | VERIFIED | 95% | Exact EAN match; Brand: Fragrant; Simila |
| 5060187173633 | MIRROR BLUE CANYON SQUARE PLASTIC M | VERIFIED | 95% | Exact EAN match; Brand: Blue Canyon; Sim |
| 5013159004428 | ELLIOTTS GLASS SPRAY BOTTLE BROWN48 | VERIFIED | 95% | Exact EAN match; Brand: Elliott; Similar |
| 5015302472535 | ROYLE HOME SPRINGFORM CAKE TIN | VERIFIED | 95% | Exact EAN match; Brand: Royle; Similarit |
| 5022704000013 | FIRE UP NATURAL FIRELIGHTERS 28 PAC | VERIFIED | 95% | Exact EAN match; Similarity: 69% |
| 5050028016069 | EVERREADY T8 4FT 36W TUBE LIGHT | VERIFIED | 95% | Exact EAN match; Similarity: 69% |
| 5053249248356 | PAN AROMA JAR CANDLE 85GM SALTED CA | VERIFIED | 95% | Exact EAN match; Brand: Pan Aroma; Simil |
| 5053249248295 | PAN AROMA JAR CANDLE 85GM RED BERRY | VERIFIED | 95% | Exact EAN match; Brand: Pan Aroma; Simil |
| 5012904061204 | TALA COCKTAIL STICKS 200 | VERIFIED | 95% | Exact EAN match; Brand: Tala; Similarity |
| 5039295201040 | HOUSE MATE STAINLESS STEEL CLEANER  | VERIFIED | 95% | Exact EAN match; Brand: House Mate; Simi |
| 5010792542737 | GEL  LED CANDLE FESTIVE ROBIN | VERIFIED | 95% | Exact EAN match; Similarity: 42% |
| 5010792542676 | CHRISTMAS LAPTRAY  ROBINS | VERIFIED | 95% | Exact EAN match; Similarity: 46% |
| 5019200117338 | PRODEC CAULKER 12 INCH | VERIFIED | 95% | Exact EAN match; Brand: Prodec; Similari |

## 6. Problem Patterns Identified

Based on our analysis, the following common issues were identified across reports:

### 6.1 Pack Size Detection Issues
- **Dimension Traps**: Reports incorrectly interpreting measurements (e.g., `15x5.5x5.5cm`) as pack quantities
- **Model Number Confusion**: Numeric model identifiers (e.g., `2001.542`) mistaken for pack sizes
- **Bundle vs Pack**: Inconsistent handling of Amazon bundle listings (e.g., `3 x Product`)

### 6.2 EAN Handling Issues
- **EAN Conflict Routing**: Some reports categorize EAN-conflict products as VERIFIED instead of NEEDS VERIFICATION
- **Missing EAN Handling**: Inconsistent treatment of products where Amazon EAN is missing

### 6.3 Brand Matching Issues
- **Generic Word False Positives**: Words like 'PAPER', 'FAIRY', 'CHEF' incorrectly matched as brands
- **Brand Case Sensitivity**: Some brand matches failed due to case differences

### 6.4 Profit Calculation Issues
- **RSU Inconsistency**: Different RSU (Retail Selling Unit) calculations leading to different adjusted profit figures
- **Negative Profit Routing**: Some products with negative adjusted profit incorrectly left in VERIFIED/HIGHLY LIKELY

## 7. Recommendations

### 7.1 Immediate Fixes
1. **Implement strict dimension shielding** - Pattern match for measurements BEFORE pack detection
2. **Route EAN conflicts to NEEDS VERIFICATION** - Per methodology §8.2-8.3
3. **Enforce strict brand list matching** - Do not use first-word matching for unknown brands
4. **Audit negative profit products** - Any adjusted profit ≤ 0 must be AUDITED OUT

### 7.2 Methodology Improvements
1. Add model number shielding patterns (e.g., `S1532`, `BA2046`, `2001.542`)
2. Implement capacity multipack detection for patterns like `2pk x 50ml`
3. Add stricter title similarity thresholds for low word-overlap datasets

### 7.3 Best Performing Model
**CODEX_FINAL** achieved the highest accuracy at **50.0%**.
This model should be used as the baseline for future improvements.

---
*Report generated: 2026-01-10 07:09:40*