# Phase A MD Report Audit vs PART3.xlsx

**Reference dataset:** `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx`  
**MD reports audited:**
- `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md`
- `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md`
- `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md`
- `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md`

---

## 1) Executive Summary

**Winner:** `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md` (total score **0.733**)

- PART3 has **1316 rows**; unique ASINs **1032**; exact EAN matches **24** (checksum-valid: **23**).
- PART3 rubric distribution: VALID **23**, LIKELY VALID **0**, NEEDS REVIEW **38**, INVALID **1255**.
- Two reports claim **1240** total rows; this PART3 has **1316** rows.
- Winner parsed recommended rows: **32**; match-back: **100.0%**; unique ASINs: **32**.
- Winner validity (mapped recommendations): VALID **20**, LIKELY VALID **0**, NEEDS REVIEW **12**, INVALID **0**.

---

## 2) PART3.xlsx Baseline Analysis

| Metric | Count |
|:--|--:|
| Total rows | 1316 |
| Rows with SupplierTitle | 1316 |
| Rows with AmazonTitle | 1316 |
| Rows with Supplier EAN present | 1284 |
| Rows with Amazon EAN present | 608 |
| Rows with ASIN present | 1316 |
| Rows with Sales > 0 | 1316 |
| Rows with NetProfit > 0 | 1316 |
| Unique ASINs | 1032 |
| Unique (ASIN, SupplierEAN) keys | 1316 |

**Supplier URL domain (top):**
- www.efghousewares.co.uk: 1316 rows

---

## 3) Rubric (how validity is determined)

- **VALID:** exact EAN match (checksum-valid) + no pack/spec contradiction
- **LIKELY VALID:** similarity >= 0.82 + >=3 shared anchor tokens + no contradiction (non-EAN path)
- **NEEDS REVIEW:** exact EAN but contradiction, or similarity >= 0.60 (>=2 anchors), or similarity >= 0.45 (>=2 anchors)
- **INVALID:** low similarity/anchors, especially with contradiction

| Label | Rows |
|:--|--:|
| VALID | 23 |
| LIKELY VALID | 0 |
| NEEDS REVIEW | 38 |
| INVALID | 1255 |

---

## 4) Per-Report Evaluation

### `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md`

**Stated metrics (as parsed):**
- Total rows: 1257
- VERIFIED (exact EAN, recommended): 20
- HIGH LIKELIHOOD (recommended): 35
- NEEDS VERIFICATION (recommended): 148
- NEW: VERIFIED filtered out (audit): 2
- NEW: HIGH LIKELIHOOD filtered out (audit): 18

**Parsed rows:**
- Total parsed table rows: **101**
- Parsed recommended rows: **80**
- Parsed recommended by verdict: VERIFIED 20, HIGH LIKELIHOOD 30, NEEDS VERIFICATION 30

**Coverage vs PART3:**
- Unique ASINs covered (recommended): **77** / 1032
- Unique (ASIN, SupplierEAN) keys mapped: **80** / 1316
- Recommended rows matched back to PART3: **100.0%**

**Validity rate (recommended, mapped to PART3):**
- VALID 20 (25.0%), LIKELY VALID 0 (0.0%), NEEDS REVIEW 20 (25.0%), INVALID 40 (50.0%)

**Most concerning mismatch patterns (examples):**
- ASIN B08CVK7746 | SupplierEAN 5022822194984 | AmazonEAN 5022822207776 | sim=0.34 | no explicit pack/spec contradiction
  - Supplier: STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM
  - Amazon: STATUS 2 Way Socket \\| 2 USB Port Cable Free Socket \\| S2W2USBCFS12
- ASIN B07R41125W | SupplierEAN 5056295703862 | AmazonEAN - | sim=0.37 | no explicit pack/spec contradiction
  - Supplier: BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK
  - Amazon: BGL Stainless Steel Standing Toilet Brush for Bath Decor (Black)
- ASIN B07F8VJHWF | SupplierEAN 5060605732022 | AmazonEAN 5019041167141 | sim=0.45 | no explicit pack/spec contradiction
  - Supplier: MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK
  - Amazon: HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Thermal Trooper Trapper Hat with Ear Flaps

---

### `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md`


**Parsed rows:**
- Total parsed table rows: **37**
- Parsed recommended rows: **32**
- Parsed recommended by verdict: VERIFIED 20, HIGH LIKELIHOOD 12, NEEDS VERIFICATION 0

**Coverage vs PART3:**
- Unique ASINs covered (recommended): **32** / 1032
- Unique (ASIN, SupplierEAN) keys mapped: **32** / 1316
- Recommended rows matched back to PART3: **100.0%**

**Validity rate (recommended, mapped to PART3):**
- VALID 20 (62.5%), LIKELY VALID 0 (0.0%), NEEDS REVIEW 12 (37.5%), INVALID 0 (0.0%)

---

### `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md`

**Stated metrics (as parsed):**
- Total rows in file: 1240

**Parsed rows:**
- Total parsed table rows: **71**
- Parsed recommended rows: **44**
- Parsed recommended by verdict: VERIFIED 12, HIGH LIKELIHOOD 7, NEEDS VERIFICATION 25

**Coverage vs PART3:**
- Unique ASINs covered (recommended): **42** / 1032
- Unique (ASIN, SupplierEAN) keys mapped: **44** / 1316
- Recommended rows matched back to PART3: **100.0%**

**Validity rate (recommended, mapped to PART3):**
- VALID 12 (27.3%), LIKELY VALID 0 (0.0%), NEEDS REVIEW 22 (50.0%), INVALID 10 (22.7%)

**Most concerning mismatch patterns (examples):**
- ASIN B07F8VJHWF | SupplierEAN 5060605732022 | AmazonEAN 5019041167141 | sim=0.45 | no explicit pack/spec contradiction
  - Supplier: MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK
  - Amazon: HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Thermal Trooper Trapper Hat with Ear Flaps
- ASIN B00HMDJD38 | SupplierEAN 5032759005864 | AmazonEAN - | sim=0.42 | no explicit pack/spec contradiction
  - Supplier: AMTECH TELESCOPIC PICKUP TOOL
  - Amazon: Amtech S8006 3 LED telescopic torch and magnetic pick up tool
- ASIN B0BHSR7XK1 | SupplierEAN 5060605733807 | AmazonEAN - | sim=0.43 | no explicit pack/spec contradiction
  - Supplier: LADIES KNITTED HAT WITH FAUX FUR POM-POM
  - Amazon: Sibba Bobble Hat for Women Winter Beanie Hats Thermal Fleece Lined Hat Ladies Knitted Wooly Hats with Faux Fur Pom Pom

---

### `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md`

**Stated metrics (as parsed):**
- Total rows: 1240
- VERIFIED (exact EAN, recommended): 16
- HIGH LIKELIHOOD (recommended): 18
- NEEDS VERIFICATION (recommended): 37
- VERIFIED filtered out (audit): 4
- HIGH LIKELIHOOD filtered out (audit): 20

**Parsed rows:**
- Total parsed table rows: **118**
- Parsed recommended rows: **64**
- Parsed recommended by verdict: VERIFIED 16, HIGH LIKELIHOOD 18, NEEDS VERIFICATION 30

**Coverage vs PART3:**
- Unique ASINs covered (recommended): **62** / 1032
- Unique (ASIN, SupplierEAN) keys mapped: **64** / 1316
- Recommended rows matched back to PART3: **100.0%**

**Validity rate (recommended, mapped to PART3):**
- VALID 16 (25.0%), LIKELY VALID 0 (0.0%), NEEDS REVIEW 23 (35.9%), INVALID 25 (39.1%)

**Most concerning mismatch patterns (examples):**
- ASIN B07F8VJHWF | SupplierEAN 5060605732022 | AmazonEAN 5019041167141 | sim=0.45 | no explicit pack/spec contradiction
  - Supplier: MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK
  - Amazon: HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Thermal Trooper Trapper Hat with Ear Flaps
- ASIN B00HMDJD38 | SupplierEAN 5032759005864 | AmazonEAN - | sim=0.42 | no explicit pack/spec contradiction
  - Supplier: AMTECH TELESCOPIC PICKUP TOOL
  - Amazon: Amtech S8006 3 LED telescopic torch and magnetic pick up tool
- ASIN B0DN1HXF9B | SupplierEAN 3426470301268 | AmazonEAN - | sim=0.45 | no explicit pack/spec contradiction
  - Supplier: PYREX AIR FRYER SQUARE DISH 20X17CM
  - Amazon: PYREX PREPWARE – Square Glass Dish 20 x 17 cm – 1 L

---

## 5) Scorecard Table

Weights: Validity 0.55, Completeness 0.25, Pack/Variant 0.15, Clarity 0.05.

| Report | Validity | Completeness | Pack/Variant | Clarity | Total |
|:--|--:|--:|--:|--:|--:|
| `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md` | 0.738 | 0.509 | 1.000 | 1.000 | **0.733** |
| `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240124.md` | 0.423 | 0.564 | 1.000 | 1.000 | **0.573** |
| `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240128.md` | 0.358 | 0.655 | 1.000 | 1.000 | **0.560** |
| `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_20251224.md` | 0.325 | 0.691 | 1.000 | 1.000 | **0.551** |

---

## 6) Winner Deep Dive: Strengths + Weaknesses

**Winner:** `C:\Users\chris\Downloads\PHASEA_MANUAL_REPORT_2512240724.md`

**Strengths:**
- Higher total score driven by validity + high-impact coverage under the rubric.
- VALID 20 and LIKELY VALID 0 among mapped recommendations.

**Weaknesses:**
- Contains 12 mapped recommendations that are NEEDS REVIEW/INVALID under rubric.

---

## 7) Coverage & Missing Items

### Missing-from-winner vs PART3 (Top 10-25)

| ASIN | SupplierEAN | AmazonEAN | Sales | NetProfit | Rubric | Why (rubric) |
|:--|:--|:--|--:|--:|:--|:--|
| B0DRPCJDWW | 5900627061383 | 198153749706 | 300 | 258.24 | INVALID | low similarity (sim=0.08, anchors=0) |
| B0BXLRLC9T | 8006540937594 | 4242003943359 | 200 | 241.01 | INVALID | low similarity (sim=0.09, anchors=0) |
| B0FJ1RGCSP | 5025301737399 | - | 900 | 110.06 | INVALID | low similarity (sim=0.07, anchors=0) |
| B09VPPS96M | 4894158102466 | - | 50 | 106.26 | INVALID | low similarity (sim=0.08, anchors=0) |
| B0FB36DTHD | 5030017011138 | - | 300 | 90.50 | INVALID | low similarity (sim=0.04, anchors=0) |
| B0FGHZB8FM | 5015302477202 | 717710483480 | 50 | 83.45 | INVALID | low similarity (sim=0.04, anchors=0) |
| B0FGHZB8FM | 5055706641151 | 717710483480 | 50 | 82.42 | INVALID | low similarity (sim=0.04, anchors=0) |
| B0FGHZB8FM | 5055297302240 | 717710483480 | 50 | 82.33 | INVALID | low similarity (sim=0.05, anchors=0) |
| B0D3M53JGG | 5010353328800 | 5065018907005 | 100 | 82.14 | INVALID | low similarity (sim=0.05, anchors=0) |
| B0FGHZB8FM | 5055706641182 | 717710483480 | 50 | 81.64 | INVALID | low similarity (sim=0.05, anchors=0) |

### Missing-from-winner but present in other MDs (Top 10-25)

| ASIN | SupplierEAN | Sales | NetProfit | Present in reports |
|:--|:--|--:|--:|:--|
| B085MQZCLY | 6923456822900 | 800 | 4.43 | PHASEA_MANUAL_REPORT_20251224.md |
| B0FJ74WBPQ | 5017403134572 | 600 | 3.64 | PHASEA_MANUAL_REPORT_20251224.md |
| B0B3F548G7 | 5025301365790 | 500 | 33.63 | PHASEA_MANUAL_REPORT_20251224.md |
| B0773HXND3 | 871125223930 | 500 | 11.96 | PHASEA_MANUAL_REPORT_20251224.md |
| B0DFBMPLSS | 5029594282000 | 500 | 6.82 | PHASEA_MANUAL_REPORT_20251224.md |
| B00KLGPNUK | 5055203813228 | 500 | 3.94 | PHASEA_MANUAL_REPORT_20251224.md |
| B07MGLHMWY | 5025364005824 | 500 | 2.77 | PHASEA_MANUAL_REPORT_2512240124.md |
| B084Z492PW | - | 500 | 1.08 | PHASEA_MANUAL_REPORT_20251224.md, PHASEA_MANUAL_REPORT_2512240128.md |
| B0001P03O2 | 5027785811329 | 500 | 0.95 | PHASEA_MANUAL_REPORT_20251224.md |
| B0C3JTR3NM | 5060240212231 | 500 | 0.78 | PHASEA_MANUAL_REPORT_20251224.md |

### Questionable-in-winner items (Top 10-25)

| ASIN | SupplierEAN | AmazonEAN | Sales | NetProfit | Rubric | What to verify |
|:--|:--|:--|--:|--:|:--|:--|
| B08TCDBQTC | 5023139270705 | 9876553908060 | 500 | 2.90 | NEEDS REVIEW | title match weak (sim=0.66, anchors=6) |
| B08XWB7JW9 | 5010232988019 | 9790504074621 | 200 | 1.41 | NEEDS REVIEW | title match weak (sim=0.62, anchors=5) |
| B0CCJS5GKB | 5053249277943 | 5053249253183 | 200 | 0.82 | NEEDS REVIEW | title match weak (sim=0.52, anchors=6) |
| B0114IPMS6 | 5010559684793 | 5010559684816 | 100 | 2.15 | NEEDS REVIEW | title match weak (sim=0.53, anchors=4) |
| B01LCYXS24 | 3426470268684 | - | 100 | 0.21 | NEEDS REVIEW | title match weak (sim=0.48, anchors=4) |
| B0013IUIPA | 5010853210520 | 5010853110851 | 100 | 0.05 | NEEDS REVIEW | title match weak (sim=0.57, anchors=4) |
| B01CMHNDKC | 5060386422662 | - | 50 | 1.93 | NEEDS REVIEW | title match weak (sim=0.59, anchors=5) |
| B073TZKMK9 | 5013655218435 | - | 50 | 1.82 | NEEDS REVIEW | title match weak (sim=0.70, anchors=6) |
| B00ABJQTPU | 5032759027644 | - | 50 | 0.63 | NEEDS REVIEW | title match weak (sim=0.71, anchors=6) |
| B073VPL2VQ | 5027785817369 | 5027785811817 | 50 | 0.43 | NEEDS REVIEW | title match weak (sim=0.70, anchors=4) |

---

## 8) What to fix next (prioritized)

1. Enforce a **hard floor** for title-only matches (e.g., similarity < 0.45 => never recommended).
2. Make pack/variant parity mandatory for non-EAN rows (qty/spec mismatch => exclude or NEEDS REVIEW).
3. Standardize report keys as `(ASIN, SupplierEAN)` to avoid silent ASIN-level collapsing.
4. Standardize summary-count definitions so totals/recommended/audit counts reconcile from one filter set.
