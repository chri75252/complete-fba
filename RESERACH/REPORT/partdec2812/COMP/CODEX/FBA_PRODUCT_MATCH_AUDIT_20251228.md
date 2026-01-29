# FBA PRODUCT MATCH AUDIT — PHASE A (Manual Row Review)

**Reference date:** 2025-12-28 (Asia/Dubai, UTC+4)  
**Supplier observed in dataset:** `www.efghousewares.co.uk`  
**Input dataset (reference):**  
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx`  
CSV used for inspection:  
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.csv`

**Reports audited (4):**
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\CODEX\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\FLASH\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\GEMINI\PHASEA_MANUAL_REPORT_20251228.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\opus\PHASEA_MANUAL_REPORT_20251228.md`

**Audit artifacts created (for reproducibility):**
- Worksheet of all **recommended** rows (union across the 4 reports):  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\COMP\CODEX\AUDIT_WORKSHEET_20251228.tsv`
- Manual verdicts for those worksheet rows:  
  `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\COMP\CODEX\AUDIT_VERDICTS_20251228.tsv`

---

## 1) Executive Summary (Winner + counts)

- **Primary-goal winner (most correct entries): CODEX** — **57 VALID** out of **98 recommended** (validity rate **58.2%**).
- **Accuracy winner (highest validity rate): FLASH** — **24 VALID** out of **26 recommended** (validity rate **92.3%**).
- **Key tradeoff:** CODEX recommends far more items, but includes many false positives (pack/variant/type mismatches); FLASH is much more conservative and cleaner.
- **Most common failure mode across reports:** **pack-size mismatch** (single vs multipack) even when the *product name* matches.
- **Most damaging failure mode (observed in CODEX):** **product-type mismatch** (completely different items) being treated as recommended.
- **Highest-risk “looks-valid-but-isn’t” pattern:** dimensions like `15 x 5.5 x 5.5 cm` or `9 x 9 inch` being treated like pack count (needs explicit dimension shield + sanity checks).

---

## 2) Dataset Baseline Analysis (from Excel/CSV)

From `PARTDEC28_1.csv` (same rows as `PARTDEC28_1.xlsx`):

- Total rows: **1758**
- Rows with `SupplierTitle` present: **1758**
- Rows with `AmazonTitle` present: **1758**
- Rows with Supplier EAN (`EAN`) present: **1724**
- Rows with Amazon EAN (`EAN_OnPage`) present: **807**
- Rows with `ASIN` present: **1758**
- Rows with `bought_in_past_month` > 0: **1758**
- Rows with `NetProfit` > 0: **1758**

---

## 3) Manual Validity Rubric (brief)

For each audited row:

1. **EAN check:** `EAN` vs `EAN_OnPage` must match exactly for “Exact-EAN VALID”, but EAN match alone is not sufficient.
2. **Title verification:** brand + product type + size/variant + pack quantity must align.
3. **Pack-size detection:** treat `X x Y cm/inch/ml/g/L/kg` as dimensions/specs, not pack size.
4. **Contradiction detection:** scent/color, capacity, pack-size, size, or product-type mismatches → INVALID or NEEDS REVIEW.
5. **Verdict mapping used here:**
   - **VALID:** exact EAN match and no contradictions.
   - **LIKELY VALID:** no exact EAN match, but titles/specs align strongly (no contradiction found).
   - **NEEDS REVIEW:** plausible match, but one blocking uncertainty (usually multipack vs single, or variant ambiguity).
   - **INVALID:** clear contradiction confirmed.

Note: For “VALID counts” in scorecards, **VALID = (VALID + LIKELY VALID)**.

---

## 4) Per-Report Evaluation (Recommended rows)

### 4.1 CODEX — Recommended row audit

**Recommended rows audited:** 98  
**Manual results:** 57 VALID (22 exact-EAN + 35 likely), 20 NEEDS REVIEW, 21 INVALID

**Patterns observed (CODEX):**
- High recall, but many false positives in “HIGH LIKELIHOOD”.
- Multiple **hard type mismatches** slipped into recommended.
- Multiple **variant/size mismatches** within the same ASIN (foil trays: “1 LTR/2 LTR/4.5LTR” mapping onto `9 x 9 inch` listings).

**Manual reasoning examples (CODEX):**

**Example A — VALID (dimensions correctly treated as dimensions)**  
RowID **1382**  
SupplierTitle: `APOLLO VINEGAR SHAKER`  
AmazonTitle: `... Glass Vinegar Shaker, Clear 15 x 5.5 x 5.5 cm`  
Supplier EAN / Amazon EAN: `5026180033572` == `5026180033572`  
Reasoning:
1) EAN exact match ✅  
2) Product type: vinegar shaker ✅  
3) `15 x 5.5 x 5.5 cm` = **dimensions**, not “15-pack” ✅  
Verdict: **VALID**

**Example B — INVALID (scent + pack mismatch)**  
RowID **1374**  
SupplierTitle: `ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G`  
AmazonTitle: `3 x ... Foaming Toilet Cleaner ... Lemon Fresh ... 500g`  
Reasoning:
1) EAN mismatch / absent for exact match ❌  
2) Scent contradiction: `EUCALYPTUS` vs `Lemon Fresh` ❌  
3) Pack contradiction: single vs `3 x` ❌  
Verdict: **INVALID**

**Example C — NEEDS REVIEW (exact EAN but pack contradiction)**  
RowID **1165**  
SupplierTitle: `TIDYZ DOGGY BAGS STRONG 50 PCS ...`  
AmazonTitle: `Tidyz 200 x ... (4 x 50)`  
EAN: exact match (`5025364001970` == `5025364001970`) ✅  
Reasoning:
1) EAN exact match ✅  
2) Pack contradiction in titles: supplier says `50 PCS`, Amazon says `200 x (4 x 50)` ❌  
3) Possible explanation: supplier title is incomplete, or Amazon listing is multipack. Needs confirmation for profitability (pack ratio 1→4).  
Verdict: **NEEDS REVIEW**

**Example D — INVALID (product type mismatch)**  
RowID **745**  
SupplierTitle: `EXTRASTAR 3 WAY WALL ADAPTOR WHITE`  
AmazonTitle: `ExtraStar 4 Way Extension Lead ... 3M Extension Cord`  
Reasoning:
1) Product type mismatch: wall adaptor vs extension lead + cable ❌  
Verdict: **INVALID**

### 4.2 FLASH — Recommended row audit

**Recommended rows audited:** 26 (manual reconciliation added 2 rows whose titles contain `|`, breaking simple table parsing)  
**Manual results:** 24 VALID (23 exact-EAN + 1 likely), 1 NEEDS REVIEW, 1 INVALID

**Patterns observed (FLASH):**
- Strong precision: almost all recommended rows are exact-EAN matches and correct.
- One clear false positive: firelighter brand/pack mismatch.
- Markdown formatting risk: Amazon titles contain literal `|` which can break table parsing.

**Example — INVALID (brand/pack mismatch):**  
RowID **1742**  
SupplierTitle: `FIRE UP NATURAL FIRELIGHTERS 28 PACK`  
AmazonTitle: `Fireglow Firelighters 24 Pack`  
Contradiction tokens: `FIRE UP` vs `Fireglow`, `28` vs `24` → **INVALID**

### 4.3 GEMINI — Recommended row audit

**Recommended rows audited:** 26  
**Manual results:** 22 VALID (20 exact-EAN + 2 likely), 2 NEEDS REVIEW, 2 INVALID

**Example — INVALID (size mismatch):**  
RowID **1445**  
SupplierTitle: `ULTRATAPE PICTURE FRAME TAPE 24MMX50M`  
AmazonTitle: `... Picture Frame Tape | 48mm x 33m`  
Contradiction tokens: `24mm x 50m` vs `48mm x 33m` → **INVALID**

### 4.4 OPUS — Recommended row audit

**Recommended rows audited:** 25  
**Manual results:** 22 VALID (20 exact-EAN + 2 likely), 1 NEEDS REVIEW, 2 INVALID

Notes:
- Same two invalids as GEMINI (Ultratape tape sizing; Firelighter brand/pack mismatch).
- One pack ambiguity (Tidyz doggy bags) treated as recommended; should be downgraded to NEEDS REVIEW.

---

## 5) Scorecard Table (Recommended rows only)

| Report | Recommended Rows Audited | VALID (Exact EAN) | VALID (Likely) | NEEDS REVIEW | INVALID | VALIDITY RATE (VALID/Total) |
|:--|--:|--:|--:|--:|--:|--:|
| CODEX | 98 | 22 | 35 | 20 | 21 | 58.2% |
| FLASH | 26 | 23 | 1 | 1 | 1 | 92.3% |
| GEMINI | 26 | 20 | 2 | 2 | 2 | 84.6% |
| OPUS | 25 | 20 | 2 | 1 | 2 | 88.0% |

**Winner (most correct entries): CODEX** (57 VALID).  
**Best accuracy rate: FLASH** (92.3%).

---

## 6) Winner Deep Dive (CODEX)

### Strengths
- Finds the largest number of valid matches (**57**) within its recommended list.
- Includes many plausible non-EAN matches that other reports omit (adds recall).

### Weaknesses
- High false-positive rate in recommended list (**21 INVALID + 20 NEEDS REVIEW**).
- Several recommended items are **clearly different products** (type mismatch), not just pack ambiguity.

### Top 10 questionable entries (from CODEX recommended)

These are highest-impact issues (clear contradictions or blocked on pack/variant):

1. RowID **191** — cat litter 3LT vs “World’s Best Cat Litter 28lb Lavender” (type/size mismatch) → INVALID  
2. RowID **745** — wall adaptor vs extension lead with cord → INVALID  
3. RowID **544** — “rat killer refill” vs “electronic mouse trap device” → INVALID  
4. RowID **1374** — `EUCALYPTUS` vs `Lemon Fresh` + `3 x` → INVALID  
5. RowID **1749** — `2 CUP` navy teapot vs `6 Cup` black teapot → INVALID  
6. RowID **1445** — `24mm x 50m` vs `48mm x 33m` tape → INVALID  
7. RowID **1237** — `5M` vs `15 Metre` aerial cable → INVALID  
8. RowID **935** — `50LTR` vs `300L` bin liners → INVALID  
9. RowID **1165** — exact EAN but `50 PCS` vs `200 x (4 x 50)` → NEEDS REVIEW  
10. RowID **503** — Kilner jar vs `6 x` multipack listing → NEEDS REVIEW

### Top 10 rows missing from CODEX report (by NetProfit, dataset-driven)

These are **not included anywhere** in the CODEX report’s listed rows (CODEX covers 227/1758).  
Important note: in this dataset, many high “NetProfit” rows are clearly nonsense matches (likely correctly excluded).

1. RowID **23** — `AIRWICK CANDLE ... PK6` mapped to `Lenovo ... Tablet`  
2. RowID **47** — `FAIRY ... 440ML PK8` mapped to `SIEMENS ... Coffee Machine`  
3. RowID **1** — `EUROWRAP ... BADGE` mapped to `Motorola ... Smartphone`  
4. RowID **68** — `CHRISTMAS ... SNOW GLOBE` mapped to `Cordless Vacuum Cleaner ...`  
5. RowID **115** — `LED LIGHTS 500` mapped to `Digital Microscope ...`  
6. RowID **19** — `PANASONIC UPRIGHT` mapped to `Cordless Vacuum Cleaner ...`  
7. RowID **4** — `TOY BALL LAUNCHER` mapped to `PetSafe Automatic Ball Launcher` (this one looks plausible, but still excluded)  
8. RowID **2** — `CUPCAKE 100 CASES` mapped to `Turbo Dryer Blower ...`  
9. RowID **15** — `FLOOR MOP & HANDLE` mapped to `Turbo Dryer Blower ...`  
10. RowID **17** — `MINI PLUNGER` mapped to `Turbo Dryer Blower ...`

---

## 7) Missing Rows Analysis (coverage vs dataset)

### 7.1 Coverage counts (rows listed in each report, any section)

| Report | Rows Listed (Covered) | Rows Not Listed (Missing) |
|:--|--:|--:|
| CODEX | 227 | 1531 |
| FLASH | 96 | 1662 |
| GEMINI | 102 | 1656 |
| OPUS | 144 | 1614 |

**Union coverage (listed by at least one report):** 294 / 1758  
**Missed by all 4 reports:** 1464 / 1758

### 7.2 “Missed-by-all-4” list (Top 15 by NetProfit)

These top entries are high “NetProfit” but frequently look like obvious mismatches (suggesting exclusion is correct):

1. RowID **23** — AIRWICK candle → Lenovo tablet  
2. RowID **47** — Fairy washing up liquid → Siemens coffee machine  
3. RowID **68** — Christmas snow globe → Cordless vacuum  
4. RowID **115** — Festive lights → Digital microscope  
5. RowID **19** — Panasonic upright → Cordless vacuum  
6. RowID **4** — World of Pets ball launcher → PetSafe ball launcher  
7. RowID **2** — Cupcake cases → Turbo dryer blower  
8. RowID **15** — Floor mop → Turbo dryer blower  
9. RowID **17** — Mini plunger → Turbo dryer blower  
10. RowID **6** — Minky scourer → Garment steamer  
11. RowID **140** — Addis dustpan & brush → Garment steamer  
12. RowID **170** — Apollo nail brush → Turbo dryer blower  
13. RowID **241** — Dinner set 16pc → Turbo dryer blower  
14. RowID **20** — Christmas cards → Pressure washer  
15. RowID **165** — Straightener brush → LEGO set

**Diagnosis (why missed):**
- Reports intentionally list only small subsets (recommended + a limited sample of uncertain rows).
- Many omitted rows appear to be **obvious cross-category mismatches**, so omission is often a good sign (precision over recall).

---

## 8) Secondary Accuracy Summary (1 paragraph)

If “accuracy” means the cleanest recommended list (fewest contradictions per recommended row), **FLASH is best**: it delivers **24/26 valid** with only one hard false positive and one pack-ambiguity case. **GEMINI and OPUS** are close behind (both ~85–88% validity) but each still includes the same two clear invalids (Ultratape sizing; Firelighter brand/pack mismatch). **CODEX** finds the most valid matches overall, but with a materially higher false-positive burden, making it riskier to execute automatically without extra verification logic.

---

## 9) Recommendations (prioritized fixes)

1. **Enforce pack sanity checks on recommended rows:** detect `pack of`, `x`, `PK`, `pcs` and require supplier-vs-Amazon pack alignment; otherwise downgrade to NEEDS REVIEW.
2. **Explicit variant guards:** if supplier has scent/color (e.g., `EUCALYPTUS`) and Amazon has different variant tokens (e.g., `Lemon`) → mark INVALID.
3. **Dimension shield (must-have):** treat `15 x 5.5 x 5.5 cm`, `9 x 9 inch`, etc as dimensions; do not let them be used as pack evidence.
4. **Reject hard product-type mismatches early:** a “wall adaptor” cannot match an “extension lead with cord” without an explicit evidence override.
5. **Fix markdown table robustness (especially FLASH):** escape/replace literal `|` in titles or use CSV/TSV blocks so parsing doesn’t break.
6. **Standardize the “Recommended” output contract:** include RowID in every report and keep titles free of delimiter characters; this makes audits deterministic.

