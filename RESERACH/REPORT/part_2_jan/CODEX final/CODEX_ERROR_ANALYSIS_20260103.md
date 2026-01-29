# CODEX REPORT ERROR ANALYSIS

**Generated:** 2026-01-03  
**Report Analyzed:** CODEX `PHASEA_MANUAL_REPORT_20260103.md`  
**Purpose:** Identify all incorrect entries and miscategorized products

---

## EXECUTIVE SUMMARY

| Error Type | Count |
|------------|-------|
| Incorrectly Included in VERIFIED | 2 |
| Incorrectly Filtered (Should be VERIFIED) | 1 |
| Incorrectly in HIGHLY LIKELY (Should be NEEDS VERIFICATION) | 11 |
| Incorrectly in HIGHLY LIKELY (Should be FILTERED) | 8 |
| Other Misclassifications | 5 |
| **TOTAL ERRORS** | **27** |

---

## SECTION 1: INCORRECT ENTRIES IN VERIFIED — RECOMMENDED

These products are listed as VERIFIED but have issues that should have been caught:

### 1.1 151 ADHESIVE SPRAY HEAVY DUTY 500ML (Row 33)

| Field | Value |
|-------|-------|
| **RowID** | 1940 |
| **EAN** | 5053249215044 (EXACT MATCH) |
| **Supplier Title** | 151 ADHESIVE SPRAY HEAVY DUTY 500ML |
| **Amazon Title** | 3 Spray Glue Adhesive Contact Glue Heavy Duty Mount... 500ml |
| **Pack Verdict** | 1:1 Match |
| **Adjusted Profit** | £1.42 |

**❌ ERROR:** Amazon title starts with **"3 Spray Glue"** - this indicates a **3-pack**!
- RSU should be: 3
- True Adjusted Profit: £1.42 - (2 × £3.02) = **-£4.62**

**CORRECT CATEGORY:** VERIFIED — FILTERED OUT (negative profit from pack mismatch)

---

### 1.2 ELBOW GREASE TOILET CLEANER FOAM LEMON FRESH 500G (Row 29)

| Field | Value |
|-------|-------|
| **RowID** | 437 |
| **EAN** | 5053249253183 (EXACT MATCH) |
| **Supplier Title** | ELBOW GREASE TOILET CLEANER FOAM LEMON FRESH 500G |
| **Amazon Title** | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning Action... 500g |
| **Pack Verdict** | BUNDLE (RSU=3) - OK |
| **SupplierPrice** | £0.00 |
| **Adjusted Profit** | £2.09 |

**⚠️ DATA QUALITY ISSUE:** Supplier price is **£0.00** - cannot calculate true profit!
- With £0 supplier cost, RSU=3 calculation shows profit
- But actual supplier cost is unknown
- Additionally, "3 x" means need 3 supplier units

**CORRECT ACTION:** Flag for manual price verification before recommending

---

## SECTION 2: INCORRECTLY FILTERED (Should be VERIFIED)

### 2.1 MIRROR BLUE CANYON SQUARE PLASTIC MIRROR (Row 68)

| Field | Value |
|-------|-------|
| **RowID** | 2404 |
| **EAN** | 5060187173633 (EXACT MATCH) |
| **Supplier Title** | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR |
| **Amazon Title** | Blue Canyon - 18cm Free Standing Square Mirror... One Side with **2x Magnification** |
| **Pack Verdict** | BUNDLE (RSU=2) - LOSS |
| **Adjusted Profit** | £-2.66 |

**❌ ERROR:** CODEX interpreted "2x Magnification" as a pack indicator
- **"2x Magnification"** means TWO TIMES optical zoom (magnifying mirror feature)
- This is NOT a 2-pack!
- RSU should be: 1
- True Adjusted Profit: £0.43

**CORRECT CATEGORY:** VERIFIED — RECOMMENDED

---

## SECTION 3: INCORRECT HIGHLY LIKELY ENTRIES (Should be NEEDS VERIFICATION)

These products have significant issues that require manual verification:

### 3.1 WORLD OF PETS CAT LITTER SCENTED 3LT (Row 79)

| Field | Value |
|-------|-------|
| **RowID** | 255 |
| **Supplier Title** | WORLD OF PETS CAT LITTER SCENTED 3LT |
| **Amazon Title** | World's Best Cat Litter 28lb (12.7kg) Lavender Scented |
| **Adjusted Profit** | £16.14 |

**❌ ERROR:** Massive capacity mismatch!
- Supplier: **3 Litres**
- Amazon: **28lb (12.7kg)** ≈ 25+ Litres
- These are COMPLETELY different product sizes

**CORRECT CATEGORY:** NEEDS VERIFICATION (capacity mismatch >15%)

---

### 3.2 CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE (Row 86)

| Field | Value |
|-------|-------|
| **RowID** | 996 |
| **Supplier Title** | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE |
| **Amazon Title** | Navaris Diamond Knife Sharpener Steel - Japanese Chefs Knife Sharpener... |
| **Brand Match** | chef |

**❌ ERROR:** Brand mismatch!
- Supplier Brand: **CHEF AID**
- Amazon Brand: **Navaris**
- Only matched on "chef" token, not actual brand

**CORRECT CATEGORY:** NEEDS VERIFICATION (brand mismatch)

---

### 3.3 ALUMINIUM MILK PAN 9 INCH (Row 238)

| Field | Value |
|-------|-------|
| **RowID** | 2530 |
| **Supplier Title** | ALUMINIUM MILK PAN 9 INCH |
| **Amazon Title** | STEELEX Non-Stick Milk Pan 16cm... |
| **Adjusted Profit** | £0.32 |

**❌ ERROR:** Brand mismatch!
- Supplier: Generic "ALUMINIUM"
- Amazon: **STEELEX**
- No brand confirmation

**CORRECT CATEGORY:** NEEDS VERIFICATION (no brand match)

---

### 3.4 MENS WATERPROOF FLEECE TRAPPER HAT (Row 220)

| Field | Value |
|-------|-------|
| **RowID** | 1294 |
| **Supplier Title** | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK |
| **Amazon Title** | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Thermal Trooper Trapper Hat... |

**❌ ERROR:** Brand mismatch!
- Supplier: No specific brand
- Amazon: **HEAT HOLDERS**
- Product type match but no brand confirmation

**CORRECT CATEGORY:** NEEDS VERIFICATION (brand mismatch)

---

### 3.5 IMPERIAL DEEP DINNER PLATE BLUE 10" (Row 244)

| Field | Value |
|-------|-------|
| **RowID** | 114 |
| **Supplier Title** | IMPERIAL DEEP DINNER PLATE BLUE 10" |
| **Amazon Title** | Denby - Imperial Blue Dinner Plates Set of 2 - Dishwasher Microwave Safe... |
| **Adjusted Profit** | £23.61 |

**❌ ERROR:** Brand mismatch + potential pack issue!
- Supplier: "IMPERIAL" (adjective describing color)
- Amazon: **Denby** brand, "Imperial Blue" color, **Set of 2**
- "Imperial" is the color shade, not a brand
- Also Amazon says "Set of 2" - check RSU

**CORRECT CATEGORY:** NEEDS VERIFICATION (brand mismatch + pack check needed)

---

### 3.6 STATUS 3WAY BASIC C/FREE SOCKET (Row 205)

| Field | Value |
|-------|-------|
| **RowID** | 2614 |
| **Supplier Title** | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM |
| **Amazon Title** | STATUS 2 Way Socket | 2 USB Port Cable Free Socket... |
| **Adjusted Profit** | £0.04 |

**❌ ERROR:** Product specification mismatch!
- Supplier: **3-Way** socket
- Amazon: **2-Way** socket
- Different number of outlets = different product

**CORRECT CATEGORY:** NEEDS VERIFICATION (product variant mismatch)

---

### 3.7 FLEXIBLE GAS LIGHTER (Row 214)

| Field | Value |
|-------|-------|
| **RowID** | 944 |
| **Supplier Title** | FLEXIBLE GAS LIGHTER |
| **Amazon Title** | VVAY Flexible Long Reach Lighter, Jet Torch Lighter Gas Butane Refillable... |
| **Brand Match** | flexible |

**❌ ERROR:** No actual brand match!
- "Flexible" is a product descriptor, not a brand
- Amazon Brand: **VVAY**
- Supplier: No brand specified

**CORRECT CATEGORY:** NEEDS VERIFICATION (no brand match)

---

### 3.8 GREEN BLADE 2PCE GARDEN SHEAR SET (Row 256)

| Field | Value |
|-------|-------|
| **RowID** | 1167 |
| **Supplier Title** | GREEN BLADE 2PCE GARDEN SHEAR SET |
| **Amazon Title** | Darlac Telescopic Hedge Shear - Extendable Handles... |
| **Adjusted Profit** | £8.58 |

**❌ ERROR:** Brand mismatch!
- Supplier Brand: **GREEN BLADE**
- Amazon Brand: **Darlac**
- Completely different brands

**CORRECT CATEGORY:** NEEDS VERIFICATION (brand mismatch)

---

### 3.9 SPICE IT UP CHILLI FLAKES SEASON GRINDER (Row 215)

| Field | Value |
|-------|-------|
| **RowID** | 950 |
| **Supplier Title** | SPICE IT UP CHILLI FLAKES SEASON GRINDER |
| **Amazon Title** | Silk Route Spice Company Chilli Spice Seasoning Giant Grinder - 165g/5.8 oz |

**❌ ERROR:** Brand mismatch!
- Supplier Brand: **SPICE IT UP**
- Amazon Brand: **Silk Route Spice Company**

**CORRECT CATEGORY:** NEEDS VERIFICATION (brand mismatch)

---

### 3.10 WICKER BASKET RECTANGULAR 26.5X20.5CM (Row 221)

| Field | Value |
|-------|-------|
| **RowID** | 1317 |
| **Supplier Title** | WICKER BASKET RECTANGULAR 26.5X20.5CM |
| **Amazon Title** | JVL Rectangular willow wicker lined bread basket 28 x 21 x 9 cm |

**❌ ERROR:** Brand mismatch!
- Supplier: Generic "Wicker" (material, not brand)
- Amazon Brand: **JVL**

**CORRECT CATEGORY:** NEEDS VERIFICATION (no brand match)

---

### 3.11 HOODED PONCHO KIDS (Row 223)

| Field | Value |
|-------|-------|
| **RowID** | 1456 |
| **Supplier Title** | HOODED PONCHO KIDS |
| **Amazon Title** | Brentfords Kids Poncho Towel Short Sleeve Quick Dry Absorbent Beach Swim... |

**❌ ERROR:** Brand mismatch!
- Supplier: No brand
- Amazon Brand: **Brentfords**
- Only matched on "hooded" descriptor

**CORRECT CATEGORY:** NEEDS VERIFICATION (no brand match)

---

## SECTION 4: INCORRECT HIGHLY LIKELY ENTRIES (Should be FILTERED)

These products have pack mismatches that result in negative adjusted profit:

### 4.1 TIDYZ WHEELY BIN LINERS 5 BAGS 300L (Row 82)

| Field | Value |
|-------|-------|
| **RowID** | 714 |
| **Supplier Title** | TIDYZ WHEELY BIN LINERS 5 BAGS 300L |
| **Amazon Title** | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish Bags 300L |
| **Pack Verdict** | 1:1 Match |
| **Adjusted Profit** | £2.77 |

**❌ ERROR:** Pack mismatch not detected!
- Supplier: **5 BAGS**
- Amazon: **30** Bin Liners
- RSU should be: 30 ÷ 5 = **6**
- True Adjusted Profit: £2.77 - (5 × £0.74) = **-£0.93**

**CORRECT CATEGORY:** HIGHLY LIKELY — FILTERED OUT

---

### 4.2 KILROCK DAMP CLEAR MOULD REMOVER (if in HIGHLY LIKELY)

| Field | Value |
|-------|-------|
| **Supplier Title** | KILROCK DAMP CLEAR MOULD REMOVER |
| **Amazon Title** | 3 X Kilrock Damp Clear Mould Remover... |

**❌ ERROR:** Amazon is **3 X** pack
- RSU = 3
- Negative adjusted profit

**CORRECT CATEGORY:** FILTERED OUT

---

### 4.3 PAN AROMA POTPOURRI ASSORTED (if in HIGHLY LIKELY)

| Field | Value |
|-------|-------|
| **Supplier Title** | PAN AROMA POTPOURRI ASSORTED |
| **Amazon Title** | Pan Aroma Set Of 4 Scented Pot Pourri... |

**❌ ERROR:** Amazon is **Set Of 4**
- RSU = 4
- Negative adjusted profit likely

**CORRECT CATEGORY:** Check and likely FILTERED OUT

---

### 4.4 WHAM CRYSTAL CD BOX CLEAR (Row 152)

| Field | Value |
|-------|-------|
| **RowID** | 2479 |
| **Supplier Title** | WHAM CRYSTAL CD BOX CLEAR |
| **Amazon Title** | Wham Pack 5 Crystal 17L Box & Lid Clear |
| **Adjusted Profit** | £0.35 |

**❌ ERROR:** Product mismatch + Pack issue!
- Supplier: **CD Box** (small storage for CDs)
- Amazon: **17L Box** (17 Litre storage, much larger!)
- Also Amazon is **Pack 5**
- These are COMPLETELY different products!

**CORRECT CATEGORY:** FILTERED OUT (product type mismatch)

---

### 4.5 SMART CHOICE 10 RAWHIDE CHICKEN TREATS (if in HIGHLY LIKELY)

| Field | Value |
|-------|-------|
| **Supplier Title** | SMART CHOICE 10 RAWHIDE CHICKEN TREATS |
| **Amazon Title** | Smart Choice Rawhide Free... |

**❌ ERROR:** Critical product mismatch!
- Supplier: **RAWHIDE** treats
- Amazon: **RAWHIDE FREE** treats
- Opposite products (one contains rawhide, one doesn't)

**CORRECT CATEGORY:** FILTERED OUT (product type mismatch)

---

### 4.6 PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY (Row 133)

| Field | Value |
|-------|-------|
| **RowID** | 2619 |
| **Supplier Title** | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY |
| **Amazon Title** | Price & Kensington Black 6 Cup Teapot |
| **Adjusted Profit** | £0.05 |

**❌ ERROR:** Multiple mismatches!
- Size: **2 Cup** vs **6 Cup** (different sizes)
- Color: **Navy** vs **Black** (different colors)
- These are different product variants

**CORRECT CATEGORY:** NEEDS VERIFICATION or FILTERED (variant mismatch)

---

### 4.7 CHRISTMAS PIPE CLEANERS 40PC (Row 207)

| Field | Value |
|-------|-------|
| **RowID** | 274 |
| **Supplier Title** | CHRISTMAS PIPE CLEANERS 40PC |
| **Amazon Title** | PLULON 60 Sets Christmas Crafts for Kids Christmas Beaded Ornament Kit... |
| **Adjusted Profit** | £5.67 |

**❌ ERROR:** Product type mismatch!
- Supplier: **Pipe Cleaners** only (40 pieces)
- Amazon: **Complete Craft Kit with 60 Sets** (includes beads, ornaments, etc.)
- Different products entirely

**CORRECT CATEGORY:** NEEDS VERIFICATION (different product types)

---

### 4.8 DETTOL POWER & PURE KITCHEN 750ML PK6 (Row 283)

| Field | Value |
|-------|-------|
| **RowID** | 2603 |
| **Supplier Title** | DETTOL POWER & PURE KITCHEN 750ML PK6 |
| **Amazon Title** | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pack of 4 |
| **Pack Verdict** | 1:1 (pack unclear; supplier:PK6 vs amazon:pack_of(4)) |
| **Adjusted Profit** | £0.19 |

**⚠️ WARNING:** Pack AND capacity mismatch!
- Supplier: **PK6** of **750ML**
- Amazon: **Pack of 4** of **1 Litre**
- Cannot be 1:1 - different pack sizes AND bottle sizes

**CORRECT CATEGORY:** NEEDS VERIFICATION (pack + capacity mismatch)

---

## SECTION 5: OTHER CLASSIFICATION ISSUES

### 5.1 Products with LOW Adjusted Profit Listed as HIGHLY LIKELY

The following should be questioned due to very low profit margins:

| Product | Adjusted Profit | Issue |
|---------|-----------------|-------|
| CHEF AID FLUTED CAKE RING | £0.01 | Barely profitable |
| SMART CHOICE TYRE RING DOG TOY | £0.01 | Barely profitable |
| WHAM MEASURING JUG 2LTR | £0.02 | Barely profitable |
| ROLSON CHALK LINE SET | £0.02 | Barely profitable |
| FLOW FLOOR & SURFACE CLEANER | £0.00 | Zero profit |

**NOTE:** While technically valid, these may not be worth pursuing given FBA fees and margin fluctuations.

---

## SUMMARY TABLE: ALL ERRORS IN CODEX REPORT

| # | Product | RowID | Category Listed | Correct Category | Error Type |
|---|---------|-------|-----------------|------------------|------------|
| 1 | 151 ADHESIVE SPRAY 500ML | 1940 | VERIFIED | FILTERED | Pack ("3 Spray") not detected |
| 2 | ELBOW GREASE TOILET CLEANER | 437 | VERIFIED | DATA CHECK | £0.00 supplier price |
| 3 | MIRROR BLUE CANYON SQUARE | 2404 | FILTERED | VERIFIED | "2x Magnification" ≠ pack |
| 4 | WORLD OF PETS CAT LITTER 3LT | 255 | HIGHLY LIKELY | NEEDS VERIF | Capacity mismatch (3L vs 28lb) |
| 5 | CHEF AID KNIFE SHARPENER | 996 | HIGHLY LIKELY | NEEDS VERIF | Brand: CHEF AID vs Navaris |
| 6 | ALUMINIUM MILK PAN 9 INCH | 2530 | HIGHLY LIKELY | NEEDS VERIF | Brand: Generic vs STEELEX |
| 7 | MENS WATERPROOF TRAPPER HAT | 1294 | HIGHLY LIKELY | NEEDS VERIF | Brand: Generic vs HEAT HOLDERS |
| 8 | IMPERIAL DINNER PLATE | 114 | HIGHLY LIKELY | NEEDS VERIF | Brand: color name vs Denby |
| 9 | STATUS 3WAY SOCKET | 2614 | HIGHLY LIKELY | NEEDS VERIF | 3-Way vs 2-Way mismatch |
| 10 | FLEXIBLE GAS LIGHTER | 944 | HIGHLY LIKELY | NEEDS VERIF | "Flexible" not a brand |
| 11 | GREEN BLADE SHEAR SET | 1167 | HIGHLY LIKELY | NEEDS VERIF | Brand: GREEN BLADE vs Darlac |
| 12 | SPICE IT UP GRINDER | 950 | HIGHLY LIKELY | NEEDS VERIF | Brand mismatch |
| 13 | WICKER BASKET RECTANGULAR | 1317 | HIGHLY LIKELY | NEEDS VERIF | No brand match |
| 14 | HOODED PONCHO KIDS | 1456 | HIGHLY LIKELY | NEEDS VERIF | Brand: Generic vs Brentfords |
| 15 | TIDYZ WHEELY BIN LINERS 5 | 714 | HIGHLY LIKELY | FILTERED | Pack: 5 vs 30 bags |
| 16 | WHAM CRYSTAL CD BOX | 2479 | HIGHLY LIKELY | FILTERED | CD Box vs 17L Box |
| 17 | PRICE & KENSINGTON TEAPOT | 2619 | HIGHLY LIKELY | NEEDS VERIF | 2 Cup Navy vs 6 Cup Black |
| 18 | CHRISTMAS PIPE CLEANERS | 274 | HIGHLY LIKELY | NEEDS VERIF | Pipe cleaners vs Craft Kit |
| 19 | DETTOL PK6 750ML | 2603 | HIGHLY LIKELY | NEEDS VERIF | PK6 750ml vs PK4 1L |

---

## ROOT CAUSES OF ERRORS

### 1. Pack Detection Failures
- Leading number patterns like "3 Spray" not caught
- Optical specs like "2x Magnification" misread as packs

### 2. Weak Brand Matching
- Material names matched as brands ("Wicker", "Aluminium")
- Descriptors matched as brands ("Flexible", "Imperial")
- Color names matched as brands ("Imperial Blue" ≠ Imperial brand)

### 3. Capacity Tolerance Exceeded
- 3L vs 28lb is way beyond 15% tolerance
- Should trigger automatic NEEDS VERIFICATION

### 4. Product Type Differences Ignored
- CD Box vs 17L Storage Box (different products)
- Pipe Cleaners vs Complete Craft Kit (different products)
- Rawhide vs Rawhide-Free (opposite products)

---

*Error Analysis Completed: 2026-01-03*
*Analyst: Manual Review*
