# COMPREHENSIVE REPORT: PROBLEMATIC PRODUCTS IN CODEX REPORT

**Generated:** 2026-01-03  
**Report Analyzed:** CODEX `PHASEA_MANUAL_REPORT_20260103.md`  
**Purpose:** Complete list of all problematic product rows in CODEX with explanations and cross-reference to OPUS report

---

## EXECUTIVE SUMMARY

| Problem Type | Count |
|--------------|-------|
| **CLEAR ERRORS** (Wrong Category) | 19 |
| **NEEDS VERIFICATION** (Uncertain) | 18 |
| **TOTAL PROBLEMATIC** | **37** |

---

# PART 1: CLEAR ERRORS IN CODEX REPORT

These products have definitive issues and are incorrectly categorized:

## 1.1 VERIFIED Section Errors (Should NOT be VERIFIED)

### Error #1: 151 ADHESIVE SPRAY HEAVY DUTY 500ML

| Field | Value |
|-------|-------|
| **RowID** | 1940 (line 33 in CODEX) |
| **Category in CODEX** | VERIFIED — RECOMMENDED |
| **EAN** | 5053249215044 (exact match) |
| **Supplier** | 151 ADHESIVE SPRAY HEAVY DUTY 500ML |
| **Amazon** | **3 Spray Glue** Adhesive Contact Glue Heavy Duty... 500ml |
| **CODEX Profit** | £1.42 |

**❌ ERROR:** Amazon title starts with **"3 Spray Glue"** = 3-pack!
- RSU should be: 3
- True Adjusted Profit: £1.42 - (2 × £3.02) = **-£4.62**
- **CORRECT CATEGORY:** VERIFIED — FILTERED OUT

**Was this in OPUS?** ✅ Yes - OPUS listed it as VERIFIED (same error)

---

### Error #2: MIRROR BLUE CANYON SQUARE PLASTIC MIRROR

| Field | Value |
|-------|-------|
| **RowID** | 2404 (line 68 in CODEX) |
| **Category in CODEX** | VERIFIED — FILTERED OUT |
| **EAN** | 5060187173633 (exact match) |
| **Supplier** | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR |
| **Amazon** | Blue Canyon - 18cm Free Standing Square Mirror... **2x Magnification** |
| **CODEX Profit** | £-2.66 (after RSU=2) |

**❌ ERROR:** CODEX interpreted "2x Magnification" as pack indicator
- "2x Magnification" = optical zoom feature, NOT a 2-pack!
- RSU should be: 1
- True Adjusted Profit: **£0.43** (profitable!)
- **CORRECT CATEGORY:** VERIFIED — RECOMMENDED

**Was this in OPUS?** ✅ Yes - OPUS correctly listed it as VERIFIED — RECOMMENDED

---

## 1.2 HIGHLY LIKELY Errors: Pack Mismatch = Negative Profit (Should be FILTERED)

### Error #3: TIDYZ WHEELY BIN LINERS 5 BAGS 300L

| Field | Value |
|-------|-------|
| **RowID** | 714 (line 82 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | TIDYZ WHEELY BIN LINERS **5 BAGS** 300L |
| **Amazon** | Tidyz **30** Extra Large Wheelie Bin Liners... |
| **CODEX Pack Verdict** | 1:1 Match |
| **CODEX Profit** | £2.77 |

**❌ ERROR:** Pack mismatch not detected!
- Supplier: 5 bags
- Amazon: 30 liners
- RSU = 30 ÷ 5 = **6 units**
- True Adjusted Profit: £2.77 - (5 × £0.74) = **-£0.93**
- **CORRECT CATEGORY:** HIGHLY LIKELY — FILTERED OUT

**Was this in OPUS?** ✅ Yes - OPUS listed it as HIGHLY LIKELY but also detected pack issue

---

### Error #4: KILROCK DAMP CLEAR MOULD REMOVER (Row 154 in OPUS)

| Field | Value |
|-------|-------|
| **RowID** | 1418 in CODEX FILTERED (but similar product at line 154 OPUS) |
| **Category in CODEX** | Listed in HIGHLY LIKELY — RECOMMENDED (Row 154 in data) |
| **Supplier** | KILROCK DAMP CLEAR MOULD REMOVER ACTION 500ML |
| **Amazon** | **3 X** Kilrock Blast Away Mould Spray 500ml |
| **CODEX Profit** | £2.30 |

**❌ ERROR:** Amazon is **"3 X"** = 3-pack
- RSU = 3
- True Adjusted Profit: £2.30 - (2 × £2.14) = **-£1.98**
- **CORRECT CATEGORY:** FILTERED OUT

**Was this in OPUS?** ✅ Yes - Line 154, same product, OPUS listed as HIGHLY LIKELY (same error)

---

### Error #5: WHAM CRYSTAL CD BOX CLEAR

| Field | Value |
|-------|-------|
| **RowID** | 2479 (line 152 in CODEX HIGHLY LIKELY) |
| **Category in CODEX** | HIGHLY LIKELY - RECOMMENDED |
| **Supplier** | WHAM CRYSTAL **CD BOX** CLEAR |
| **Amazon** | Wham Pack 5 Crystal **17L Box** & Lid Clear |
| **CODEX Profit** | £0.35 |

**❌ ERROR:** Product type mismatch!
- Supplier: CD Box (small storage for CDs, ~2L max)
- Amazon: 17L Box (17 Litre storage - completely different size/product!)
- Also Amazon is "Pack 5" = 5-pack
- **CORRECT CATEGORY:** FILTERED OUT (wrong product entirely)

**Was this in OPUS?** ✅ Yes - Line 104, OPUS listed as HIGHLY LIKELY (same error)

---

## 1.3 HIGHLY LIKELY Errors: Brand Mismatch (Should be NEEDS VERIFICATION)

### Error #6: CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE

| Field | Value |
|-------|-------|
| **RowID** | 996 |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | **CHEF AID** |
| **Amazon Brand** | **Navaris** Diamond Knife Sharpener Steel |
| **CODEX Profit** | £4.40 |

**❌ ERROR:** Complete brand mismatch!
- CHEF AID ≠ Navaris
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #7: GREEN BLADE 2PCE GARDEN SHEAR SET

| Field | Value |
|-------|-------|
| **RowID** | 1167 (line 256 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | **GREEN BLADE** |
| **Amazon Brand** | **Darlac** Telescopic Hedge Shear |
| **CODEX Profit** | £8.58 |

**❌ ERROR:** Complete brand mismatch!
- GREEN BLADE ≠ Darlac
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #8: SPICE IT UP CHILLI FLAKES SEASON GRINDER

| Field | Value |
|-------|-------|
| **RowID** | 950 (line 215 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | **SPICE IT UP** |
| **Amazon Brand** | **Silk Route Spice Company** |
| **CODEX Profit** | £2.51 |

**❌ ERROR:** Complete brand mismatch!
- SPICE IT UP ≠ Silk Route
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ⚠️ Similar - OPUS has "SPICE IT UP SEASALT GRINDER" in NEEDS VERIFICATION (line 237)

---

### Error #9: WICKER BASKET RECTANGULAR 26.5X20.5CM

| Field | Value |
|-------|-------|
| **RowID** | 1317 (line 221 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | Generic "WICKER" (material, not brand) |
| **Amazon Brand** | **JVL** Rectangular willow wicker basket |
| **CODEX Profit** | £2.44 |

**❌ ERROR:** No brand match - "WICKER" is not a brand!
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #10: HOODED PONCHO KIDS

| Field | Value |
|-------|-------|
| **RowID** | 1456 (line 223 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | No brand specified |
| **Amazon Brand** | **Brentfords** Kids Poncho Towel |
| **CODEX Profit** | £1.33 |

**❌ ERROR:** No brand match!
- Brand matched on "hooded" which is a descriptor, not a brand
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #11: FLEXIBLE GAS LIGHTER

| Field | Value |
|-------|-------|
| **RowID** | 944 (line 214 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | "FLEXIBLE" (descriptor, not brand) |
| **Amazon Brand** | **VVAY** Flexible Long Reach Lighter |
| **CODEX Profit** | £2.60 |

**❌ ERROR:** "Flexible" is not a brand!
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #12: ALUMINIUM MILK PAN 9 INCH

| Field | Value |
|-------|-------|
| **RowID** | 2530 (line 238 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | "ALUMINIUM" (material, not brand) |
| **Amazon Brand** | **STEELEX** Non-Stick Milk Pan |
| **CODEX Profit** | £0.32 |

**❌ ERROR:** "Aluminium" is not a brand!
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #13: MENS WATERPROOF FLEECE TRAPPER HAT

| Field | Value |
|-------|-------|
| **RowID** | 1294 (line 220 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Brand** | Generic (no specific brand) |
| **Amazon Brand** | **HEAT HOLDERS** Mens Waterproof Trapper Hat |
| **CODEX Profit** | £6.45 |

**❌ ERROR:** No brand match!
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ⚠️ Yes - Line 236, but OPUS put it in NEEDS VERIFICATION (correct)

---

### Error #14: IMPERIAL DEEP DINNER PLATE BLUE 10"

| Field | Value |
|-------|-------|
| **RowID** | 114 (line 244 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier Title** | IMPERIAL DEEP DINNER PLATE BLUE 10" |
| **Amazon Title** | **Denby** - Imperial Blue Dinner Plates **Set of 2** |
| **CODEX Profit** | £23.61 |

**❌ ERROR (TWO ISSUES):**  
1. "Imperial" in supplier is color name, Amazon brand is **Denby**
2. Amazon says "Set of 2" - pack check needed!
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #15: STATUS 3WAY BASIC C/FREE SOCKET

| Field | Value |
|-------|-------|
| **RowID** | 2614 (line 205 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | STATUS **3WAY** BASIC C/FREE SOCKET |
| **Amazon** | STATUS **2 Way** Socket |
| **CODEX Profit** | £0.04 |

**❌ ERROR:** Product specification mismatch!
- 3-Way socket ≠ 2-Way socket (different products)
- **CORRECT CATEGORY:** NEEDS VERIFICATION or FILTERED

**Was this in OPUS?** ✅ Yes - Line 146, OPUS listed as HIGHLY LIKELY (same error)

---

## 1.4 Other Category Errors

### Error #16: PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY

| Field | Value |
|-------|-------|
| **RowID** | 2619 (line 133 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | PRICE & KENSINGTON **2 CUP** TEAPOT **MATT NAVY** |
| **Amazon** | Price & Kensington **Black 6 Cup** Teapot |
| **CODEX Profit** | £0.05 |

**❌ ERROR (TWO ISSUES):**  
1. Size: **2 Cup** vs **6 Cup** (different sizes)
2. Color: **Navy** vs **Black** (different colors)
- **CORRECT CATEGORY:** NEEDS VERIFICATION (variant mismatch)

**Was this in OPUS?** ✅ Yes - Line 226, OPUS put in NEEDS VERIFICATION (correct)

---

### Error #17: CHRISTMAS PIPE CLEANERS 40PC

| Field | Value |
|-------|-------|
| **RowID** | 274 (line 207 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | CHRISTMAS **PIPE CLEANERS** 40PC |
| **Amazon** | PLULON **60 Sets** Christmas Crafts for Kids Christmas **Beaded Ornament Kit**... |
| **CODEX Profit** | £5.67 |

**❌ ERROR:** Product type mismatch!
- Supplier: Pipe Cleaners only (40 pieces)
- Amazon: Complete Craft Kit with 60 Sets (includes beads, ornaments, etc.)
- **CORRECT CATEGORY:** NEEDS VERIFICATION (different products)

**Was this in OPUS?** ❌ No - Not in OPUS report

---

### Error #18: WORLD OF PETS CAT LITTER SCENTED 3LT

| Field | Value |
|-------|-------|
| **RowID** | 255 (in CODEX data) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | WORLD OF PETS CAT LITTER SCENTED **3LT** |
| **Amazon** | World's Best Cat Litter **28lb (12.7kg)** Lavender Scented |
| **CODEX Profit** | £16.14 |

**❌ ERROR:** Massive capacity mismatch!
- Supplier: 3 Litres
- Amazon: 28lb (12.7kg) ≈ 25+ Litres
- Difference: ~800% (far exceeds 15% tolerance)
- **CORRECT CATEGORY:** NEEDS VERIFICATION (different capacities)

**Was this in OPUS?** ✅ Yes - Line 238, OPUS put in NEEDS VERIFICATION (correct)

---

### Error #19: DETTOL POWER & PURE KITCHEN 750ML PK6

| Field | Value |
|-------|-------|
| **RowID** | 2603 (line 283 in CODEX) |
| **Category in CODEX** | HIGHLY LIKELY — RECOMMENDED |
| **Supplier** | DETTOL POWER & PURE KITCHEN **750ML PK6** |
| **Amazon** | Dettol Power and Pure Kitchen **1 Litre, Pack of 4** |
| **CODEX Profit** | £0.19 |

**❌ ERROR (TWO ISSUES):**  
1. Pack: **PK6** vs **Pack of 4** (different pack sizes)
2. Capacity: **750ML** vs **1 Litre** (different bottle sizes)
- **CORRECT CATEGORY:** NEEDS VERIFICATION

**Was this in OPUS?** ✅ Yes - Line 234, OPUS put in NEEDS VERIFICATION (correct)

---

# PART 2: PRODUCTS REQUIRING FURTHER VERIFICATION

## Cross-Reference: Were They in OPUS Report?

| # | Product | RowID | In OPUS? | OPUS Category | Notes |
|---|---------|-------|----------|---------------|-------|
| 1 | FIRST STEPS SAFARI BABY BOTTLE 150ML | 2148 | ❌ No | - | Brand: FIRST STEPS vs NUK |
| 2 | YALE ESSENTIALS DEADLOCK P/BRASS | 2258 | ❌ No | - | Same brand, verify spec |
| 3 | BABY PIPKIN SILICONE PACIFIER | 845 | ❌ No | - | Generic brand matching |
| 4 | BABY PIPKIN FEEDING BOWLS 2PCE | 2536 | ❌ No | - | Pack: 2 vs 4 unclear |
| 5 | BABY PIPKIN NAIL CLIPPERS SET | 2474 | ❌ No | - | Generic brand |
| 6 | BABY PIPKIN FEEDING SPOONS 7PCE | 597 | ❌ No | - | Pack: 7 vs 2 unclear |
| 7 | NIGHTLIGHT DINOSAUR COLOUR CHANGING | 1087 | ❌ No | - | Generic vs branded |
| 8 | PADLOCK LAMINATED 40MM | 1167 | ❌ No | - | SEPOX brand on Amazon |
| 9 | BACOFOIL ZIPPER BAGS 12 PACK | 821 | ⚠️ Similar | Line 252 NEEDS | Pack unclear |
| 10 | BACOFOIL ZIPPER BAGS 15 PACK | 1409 | ⚠️ Similar | Line 261 NEEDS | Pack unclear |
| 11 | HAIR BOBBLES 36PC BROWN BLACK | 1121 | ❌ No | - | Pack: 36 vs 15 |
| 12 | MINKY ANTI BACTERIAL MICROFIBRE 4PC | 2307 | ⚠️ Similar | Line 189 FILTERED | Pack: 4 vs 3 |
| 13 | PLASTIC MAKEUP STORAGE HOLDER | 1539 | ❌ No | - | Generic match |
| 14 | MONEY TIN BOX ASST MEDIUM | 1234 | ❌ No | - | Generic match |
| 15 | FESTIVE MAGIC TINSEL DOOR BOW | 1364 | ❌ No | - | Dimension difference |
| 16 | CHRISTMAS VOTIVES SET OF 3 | 1999 | ❌ No | - | Set of 3 vs 1? |
| 17 | ROUND TRAY ASS DECOR | 662 | ❌ No | - | Generic vs Hanobe brand |
| 18 | CERAMIC WAX/OIL BURNER | 599 | ❌ No | - | Generic match |

### Summary of Verification Status:
- **In OPUS (Any Section):** 4 products
- **Similar Product in OPUS:** 3 products  
- **NOT in OPUS at all:** 11 products

---

# PART 3: FULL LIST OF ROWS REQUIRING VERIFICATION

Below are all product RowIDs from CODEX that require further manual verification before trusting the categorization:

## Products to Verify (with Row IDs):

```
ROW_ID   | PRODUCT                                    | ISSUE
---------|-------------------------------------------|------------------------------------------
2148     | FIRST STEPS SAFARI BABY BOTTLE 150ML      | Brand: FIRST STEPS vs NUK
2258     | YALE ESSENTIALS DEADLOCK P/BRASS 64MM     | Verify product spec matches exactly
845      | BABY PIPKIN SILICONE PACIFIER             | Generic brand "BABY" not specific
2536     | BABY PIPKIN FEEDING BOWLS 2PCE            | Pack 2 vs Pack of 4 on Amazon
2474     | BABY PIPKIN NAIL CLIPPERS SET             | Generic brand match only
597      | BABY PIPKIN FEEDING SPOONS 7PCE           | Pack: 7 vs 2 on Amazon (different)
1087     | NIGHTLIGHT DINOSAUR COLOUR CHANGING       | No brand match
1167     | PADLOCK LAMINATED 40MM                    | Brand: Generic vs SEPOX
821      | BACOFOIL ZIPPER BAGS 12 PACK              | Pack structure unclear (12 vs 3x45)
1409     | BACOFOIL ZIPPER BAGS 15 PACK              | Pack structure unclear (15 vs 3x45)
1121     | HAIR BOBBLES 36PC BROWN BLACK             | Pack: 36PC vs 15 Pcs Amazon
2307     | MINKY ANTI BACTERIAL MICROFIBRE 4PC       | Pack: 4PC vs 3 Pack Amazon
1539     | PLASTIC MAKEUP STORAGE HOLDER             | Generic brand match
1234     | MONEY TIN BOX ASST MEDIUM                 | Generic brand match
1364     | FESTIVE MAGIC TINSEL DOOR BOW             | Dimension difference noted
1999     | CHRISTMAS VOTIVES RED/WHITE SET OF 3      | Set of 3 - verify matches
662      | ROUND TRAY ASS DECOR                      | Generic vs Hanobe brand
599      | CERAMIC WAX/OIL BURNER                    | Generic brand match only
```

---

## SUMMARY TABLE: ALL PROBLEMATIC PRODUCTS

| Error Type | Count | Action Required |
|------------|-------|-----------------|
| Pack Detection Failure | 5 | Recalculate RSU, likely FILTER |
| Brand Mismatch → NEEDS VERIF | 9 | Move to NEEDS VERIFICATION |
| Product Type/Spec Mismatch | 5 | Move to NEEDS VERIF or FILTER |
| Optical Spec Misread as Pack | 1 | Move to VERIFIED (corrected) |
| Requires Manual Verification | 18 | Verify before action |
| **TOTAL PROBLEMATIC** | **37** | - |

---

*Comprehensive Error Report Completed: 2026-01-03*
*Cross-referenced with OPUS Report: PHASEA_MANUAL_REPORT_20260103_002701.md*
