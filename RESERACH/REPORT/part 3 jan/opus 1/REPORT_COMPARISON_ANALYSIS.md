# REPORT COMPARISON ANALYSIS

**Comparing:**
- **Report A (To Be Checked):** `PHASEA_MANUAL_REPORT_20260103_TO BE CEHCKED.md`
- **Report B (Thorough):** `PHASEA_MANUAL_REPORT_20260103_THOROUGH.md`

**Analysis Date:** 2026-01-04

---

## EXECUTIVE SUMMARY

| Metric | Report A (To Be Checked) | Report B (Thorough) | Difference |
|--------|--------------------------|---------------------|------------|
| **VERIFIED REC** | 36 | 37 | +1 |
| **VERIFIED FILTERED** | 5 | 4 | -1 |
| **HIGHLY LIKELY REC** | ~235 | 155 (top 50 shown) | Report A has more |
| **HIGHLY LIKELY FILTERED** | ~83 | 6 | Report A has more |
| **Total VERIFIED** | 41 | 41 | Same |
| **Total Entries** | ~448 | ~517 | Report A more detailed |

---

## KEY FINDING: Report A is More Comprehensive

**Report A ("To Be Checked")** contains significantly MORE product entries and appears to be the more thorough analysis:

1. **VERIFIED — RECOMMENDED:** 36 products (Report A) vs 37 (Report B)
2. **VERIFIED — FILTERED OUT:** 5 products (Report A) vs 4 (Report B) 
3. **HIGHLY LIKELY — RECOMMENDED:** ~235 products (Report A) vs ~155 (Report B)
4. **HIGHLY LIKELY — FILTERED OUT:** ~83 products (Report A) vs 6 (Report B)

---

## PRODUCTS IN REPORT A BUT MISSING FROM REPORT B

### Found in Report A's VERIFIED but Missing in Report B:

| Row | Product | EAN | Profit | Issue |
|-----|---------|-----|--------|-------|
| PPS ROUND 40 DOYLEYS 21CM | 5030481940088 | £0.30 | **In Report B's FILTERED list instead** |
| SAMS SCRUMMY GIANT LEG DOG BONE | 5015302202996 | £0.78 | **In Report B's FILTERED list instead** |

### Found in Report A's VERIFIED but Differently Categorized in Report B:

**Report A correctly identifies some products as VERIFIED-RECOMMENDED that Report B incorrectly FILTERED:**

1. **PPS ROUND 40 DOYLEYS 21CM**
   - Report A: VERIFIED REC (1:1 Match - Items-inside)
   - Report B: FILTERED (Pack 1→40 = -£25.72)
   - **ANALYSIS:** Report A's interpretation is CORRECT. The supplier sells 40 doyleys, Amazon sells 40 - it's a 1:1 match. Report B incorrectly calculated this.

2. **SAMS SCRUMMY GIANT LEG DOG BONE**
   - Report A: VERIFIED REC (Pack 1:1) 
   - Report B: FILTERED (Pack 1→2)
   - **ANALYSIS:** Report A correct if Amazon package matches supplier single.

### HIGHLY LIKELY Products in Report A but Missing in Report B:

Report A includes many more HIGHLY LIKELY products. Key examples missing from Report B:

| Row | Brand | Product | Profit | Sales | Should Include? |
|-----|-------|---------|--------|-------|-----------------|
| - | DUNLOP | DUNLOP BICYCLE MINI PUMP | £16.74 | 900 | ✅ YES - High profit, high volume |
| - | ART | ART SET 24PCE | £20.28 | 800 | ✅ YES - High profit |
| - | ZODIAC | GEL EYE MASK AND FACE ROLLER | £7.83 | 800 | ⚠️ Brand may be questionable |
| - | JAUNTY | PARTYWARE CONFETTI PARTY | £10.42 | 300 | ✅ YES - Brand match |
| - | HOBBY | GRAND STORAGE BOX | £5.73 | 100 | ✅ YES - Brand match |
| - | KINGAVON | 6 LED TORCH | £5.59 | 50 | ✅ YES - Brand match |
| - | CAT | Lead & Harness | £6.02 | 50 | ⚠️ Generic word "CAT" |
| - | MOKATE | Gold Premium Coffee | £7.14 | 50 | ✅ YES - Brand match |

---

## PRODUCTS THAT SHOULD BE REMOVED/RECATEGORIZED

### From Report A - Questionable HIGHLY LIKELY Entries:

These products use **generic words as "brands"** and should NOT be in HIGHLY LIKELY:

| Product Match | "Brand" Used | Issue | Recommendation |
|--------------|--------------|-------|----------------|
| WATER BOTTLE WITH HANDLE | WATER | Generic word, not brand | **REMOVE** |
| WALL CLOCK PP | WALL | Generic word, not brand | **REMOVE** |
| RUBBER DUCK FAMILY BATH TOY | RUBBER | Generic word, not brand | **REMOVE** |
| CHOPPING BOARD MEDIUM | CHOPPING | Generic word, not brand | **REMOVE** |
| CAR ASHTRAY | CAR | Generic word, not brand | **REMOVE** |
| COTTON BUDS IN JAR | COTTON | Generic word, not brand | **REMOVE** |
| READING GLASSES | READING | Generic word, not brand | **REMOVE** |
| GLASS MUG/BOWL/VASE (many) | GLASS | Generic material, not brand | **REVIEW EACH** |
| GEL TOE PROTECTORS | GEL | Generic material, not brand | **REMOVE** |
| FOIL PLATTER LARGE | FOIL | Generic material, not brand | **REMOVE** |
| HAPPY BIRTHDAY BANNER | HAPPY | Generic word, not brand | **REMOVE** |
| METALLIC BALLOONS | METALLIC | Generic adjective, not brand | **REMOVE** |
| ROTARY LINE COVER | ROTARY | Generic word, not brand | **REMOVE** |
| EXFOLIATING GLOVES | EXFOLIATING | Generic adjective, not brand | **REMOVE** |
| FALSE EYELASHES | FALSE | Generic word, not brand | **REMOVE** |
| MEMORIAL PLASTIC SPIKE | MEMORIAL | Generic word, not brand | **REMOVE** |

**Estimated incorrectly included:** ~50 products using generic words as "brands"

### From Report A - Correctly Included (Should Keep):

These products have ACTUAL brand matches:

| Brand | Product Examples | Status |
|-------|-----------------|--------|
| QUEST | Espresso Machine, Blender | ✅ KEEP |
| MASON CASH | Mixing Bowls | ✅ KEEP |
| PYREX | Casseroles, Dishes | ✅ KEEP |
| DRAPER | Tools | ✅ KEEP |
| ROLSON | Tools | ✅ KEEP |
| AMTECH | Tools | ✅ KEEP |
| MINKY | Cleaning products | ✅ KEEP |
| TIDYZ | Bin liners, bags | ✅ KEEP |
| BACOFOIL | Zipper bags | ✅ KEEP |
| KILROCK/KILNER | Cleaning/Jars | ✅ KEEP |
| EVERBUILD | Sealants, fillers | ✅ KEEP |
| SOUDAL | Expanding foam | ✅ KEEP |
| PAN AROMA | Candles | ✅ KEEP |
| SCHOTT ZWIESEL | Wine glasses | ✅ KEEP |
| CLIPPER | Lighters | ✅ KEEP |
| FAIRY | Cleaning products | ✅ KEEP |
| BEAUFORT | Food containers | ✅ KEEP |
| CHEF AID | Kitchen utensils | ✅ KEEP |
| TALA | Kitchen accessories | ✅ KEEP |
| SPONTEX | Cleaning products | ✅ KEEP |
| CURVER | Storage | ✅ KEEP |
| VINERS | Cutlery | ✅ KEEP |
| PASABAHCE | Glassware | ✅ KEEP |
| EXTRASTAR | LED products | ✅ KEEP |
| SISTEMA | Food containers | ✅ KEEP |
| THERMOS | Cool bags | ✅ KEEP |
| YALE | Locks | ✅ KEEP |
| MARIGOLD | Gloves | ✅ KEEP |
| RCR | Crystalware | ✅ KEEP |
| HARRIS | Putty knives | ✅ KEEP |
| GIFTMAKER | Gift items | ✅ KEEP |

---

## FILTERED OUT SECTION ANALYSIS

### Report A's HIGHLY LIKELY FILTERED - Correctly Filtered:

These were correctly filtered due to pack mismatches making them unprofitable:

| Product | Pack Issue | Adj Profit | Status |
|---------|------------|------------|--------|
| WHAM CRYSTAL 60LTR | Bundle 1→5 | -£11.39 | ✅ Correct |
| WHAM CRYSTAL 32LTR SMOKE | Bundle 1→5 | -£13.27 | ✅ Correct |
| KILNER 1LTR SQUARE CLIP TOP | Bundle 1→6 | -£8.91 | ✅ Correct |
| SUPERIOR FOIL containers (multiple) | Various packs | Negative | ✅ Correct |
| CHRISTMAS CRACKER entries | Large pack mismatches | Very negative | ✅ Correct |
| ART BOX COLOURING KIT | Bundle 1→106 | -£72.36 | ✅ Correct |
| CORAL EASY COATER | Bundle 1→12 | -£26.05 | ✅ Correct |

### Report A's VERIFIED FILTERED - Needs Review:

| Product | Report A Status | Report B Status | Recommendation |
|---------|-----------------|-----------------|----------------|
| PHOODS FOIL TRAY ROASTER | VERIFIED FILT (RSU=10, -£5.82) | FILTERED (-£0.93) | ✅ Correctly filtered |
| BEAUTY VELCRO HAIR ROLLERS 7PK | VERIFIED FILT (RSU=6, -£1.11) | Not in filtered | ⚠️ Review - Report A has it, Report B marked as REC |
| SUPERIOR FOIL 10 CONTAINERS 9X9 | VERIFIED FILT (RSU=10, -£30.81) | VERIFIED REC | **DISCREPANCY** |
| APOLLO VINEGAR SHAKER | VERIFIED FILT (RSU=15, -£12.64) | VERIFIED REC | **DISCREPANCY** |
| MASON CASH CERAMIC DISH 16cm | VERIFIED FILT (RSU=16, -£54.80) | VERIFIED REC | **DISCREPANCY** |

**CRITICAL DISCREPANCIES:**
- Report A filters SUPERIOR FOIL 9X9 as unprofitable (calculates different pack)
- Report B includes it as VERIFIED REC
- Report A's pack interpretation may be wrong (using 9x9 incorrectly as pack)

---

## DIMENSION TRAP ANALYSIS

### Report A Potential Issues:

1. **APOLLO VINEGAR SHAKER (5026180033572)**
   - Amazon title includes: "15 x 5.5 x 5.5 cm"
   - Report A: Calculated RSU=15 (WRONG - this is dimensions!)
   - Report B: Correctly identified as 1:1 match
   - **VERDICT: Report B is correct. 15 x 5.5 x 5.5 cm = product dimensions, NOT pack**

2. **MASON CASH CERAMIC DISH 16cm**
   - Amazon title mentions "16 x 16 x 4.5 cm"
   - Report A: Calculated RSU=16 (WRONG - this is dimensions!)
   - Report B: Correctly identified as 1:1 match
   - **VERDICT: Report B is correct. 16cm = dish size, NOT pack**

3. **ROLSON PLASTERING TROWEL 280X115MM**
   - Report A: BUNDLE (RSU=280) - LOSS of -£745.86
   - **ANALYSIS:** 280x115mm is clearly DIMENSIONS of trowel, not pack count!
   - **VERDICT: Report A WRONG. Should be 1:1 match.**

---

## FINAL RECOMMENDATIONS

### Products to ADD to Report B (Missing Valid Matches):

| Product | Brand | Profit | Sales | Action |
|---------|-------|--------|-------|--------|
| DUNLOP BICYCLE MINI PUMP | DUNLOP | £16.74 | 900 | **ADD** to HIGHLY LIKELY |
| ART SET 24PCE | ART | £20.28 | 800 | **ADD** (but verify brand) |
| JAUNTY PARTYWARE | JAUNTY | £10.42 | 300 | **ADD** to HIGHLY LIKELY |
| HOBBY STORAGE BOX | HOBBY | £5.73 | 100 | **ADD** to HIGHLY LIKELY |
| KINGAVON LED TORCH | KINGAVON | £5.59 | 50 | **ADD** to HIGHLY LIKELY |
| MOKATE Gold Coffee | MOKATE | £7.14 | 50 | **ADD** to HIGHLY LIKELY |
| LAV MISKET GIN GLASS | LAV | £4.21 | 100 | **ADD** (verify pack) |
| RCR MELODIA TUMBLER | RCR | £7.66 | 50 | **ADD** to HIGHLY LIKELY |
| FALCON ENAMEL PIE DISH | FALCON | £0.89 | 50 | **ADD** to HIGHLY LIKELY |
| SISTEMA boxes | SISTEMA | Various | Various | **ADD** multiple items |

### Products to REMOVE from Report A (Incorrect Matches):

| Product | "Brand" | Reason | Action |
|---------|---------|--------|--------|
| WATER BOTTLE WITH HANDLE | WATER | Generic word | **REMOVE** |
| WALL CLOCK PP | WALL | Generic word | **REMOVE** |
| CHOPPING BOARD MEDIUM | CHOPPING | Generic word | **REMOVE** |
| CAR ASHTRAY | CAR | Generic word | **REMOVE** |
| All entries where "GLASS" is the brand | GLASS | Generic material | **REVIEW each - some valid, some not** |
| GEL TOE PROTECTORS | GEL | Generic material | **REMOVE** |
| HAPPY BIRTHDAY BANNER | HAPPY | Generic word | **REMOVE** |
| METALLIC BALLOONS | METALLIC | Generic adjective | **REMOVE** |
| EXFOLIATING GLOVES | EXFOLIATING | Generic adjective | **REMOVE** |
| FALSE EYELASHES | FALSE | Generic word | **REMOVE** |
| DOG Figure 8 Knot Ball | DOG | Generic word | **REMOVE** |

### Products to RECATEGORIZE:

| Product | Current (Report A) | Should Be | Reason |
|---------|-------------------|-----------|--------|
| APOLLO VINEGAR SHAKER | VERIFIED FILTERED (RSU=15) | VERIFIED REC | 15x5.5x5.5cm = dimensions |
| MASON CASH DISH 16cm | VERIFIED FILTERED (RSU=16) | VERIFIED REC | 16cm = dish size |
| ROLSON PLASTERING TROWEL | HIGHLY LIKELY FILTERED (RSU=280) | HIGHLY LIKELY REC | 280x115mm = dimensions |
| PYREX AIR FRYER 20X17CM | HIGHLY LIKELY FILTERED (RSU=20) | HIGHLY LIKELY REC | 20x17cm = dish size |

---

## SUMMARY OF ISSUES

### Report A ("To Be Checked") Issues:
1. ❌ **Dimension Traps:** Incorrectly interprets dimensions (15cm, 16cm, 280mm) as pack counts
2. ❌ **Generic Words as Brands:** Accepts GLASS, WATER, WALL, CAR, GEL etc. as brand matches
3. ✅ **More comprehensive:** Has more products overall
4. ✅ **Detailed filtering reasons:** Shows pack calculations clearly

### Report B ("Thorough") Issues:
1. ❌ **Missing products:** Fewer HIGHLY LIKELY entries than Report A
2. ❌ **Missing some valid brand matches:** DUNLOP, JAUNTY, KINGAVON, etc.
3. ✅ **Better dimension handling:** Correctly treats 9x9in, 15cm as sizes
4. ✅ **Stricter brand matching:** Avoids generic word matches

---

## CONCLUSION

**Best approach: Merge the strengths of both reports:**

1. Use Report A's comprehensive product list as baseline
2. Remove ~50 products that use generic words as "brands"
3. Fix dimension trap errors (APOLLO, MASON CASH, ROLSON, PYREX)
4. Keep Report A's detailed pack calculations and filtering reasons

**Estimated Final Counts after corrections:**
- VERIFIED REC: 38 (+2 from correcting dimension traps)
- VERIFIED FILTERED: 3 (-2 from correcting dimension traps)
- HIGHLY LIKELY REC: ~185 (after removing ~50 generic matches)
- HIGHLY LIKELY FILTERED: ~75 (legitimate pack issues)
- **TOTAL ACTIONABLE: ~223**

---

*Comparison analysis completed: 2026-01-04*
