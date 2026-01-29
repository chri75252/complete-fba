# DETAILED METHODOLOGY REPORT: Manual FBA Product Analysis

**Date:** 2025-12-27  
**Analyst:** Gemini 3 Pro AI Agent  
**Source Data:** PART3.xlsx (1411 rows from efghousewares.co.uk supplier)

---

## TABLE OF CONTENTS

1. [Introduction & Objectives](#1-introduction--objectives)
2. [Data Extraction Phase](#2-data-extraction-phase)
3. [Initial Script-Based Analysis (Failed Approach)](#3-initial-script-based-analysis-failed-approach)
4. [Manual Verification Methodology](#4-manual-verification-methodology)
5. [Step-by-Step Analysis for Each EAN Match](#5-step-by-step-analysis-for-each-ean-match)
6. [HIGHLY LIKELY Product Verification](#6-highly-likely-product-verification)
7. [Pack Size Detection & Adjusted Profit Calculation](#7-pack-size-detection--adjusted-profit-calculation)
8. [Corrections Made from Script Analysis](#8-corrections-made-from-script-analysis)
9. [Final Categorization Logic](#9-final-categorization-logic)
10. [Lessons Learned](#10-lessons-learned)

---

## 1. Introduction & Objectives

### Primary Objective
Conduct a **meticulous, manual analysis** of all products in PART3.xlsx to identify:
- **VERIFIED** products (exact EAN match, profitable, correct pack size)
- **HIGHLY LIKELY** products (strong brand/title match without EAN confirmation)
- **FILTERED OUT** products (matches that fail profitability or pack size tests)

### Why Manual Analysis Was Required
The user explicitly rejected script-based analysis after discovering critical errors:
1. The script misread "15 x 5.5 x 5.5 cm" (dimensions) as "Pack of 15"
2. The script misread "9X9IN" (tray size in inches) as "Pack of 9"
3. These automated regex patterns were too naive to distinguish dimensions from pack quantities

### Scope
- **Total rows analyzed:** 1411
- **Exact EAN matches found:** 24
- **User-verified HIGHLY LIKELY products:** 7
- **Products requiring browser verification:** 12+

---

## 2. Data Extraction Phase

### Step 2.1: Load Source Data
I loaded the Excel file using pandas:
```
File: PART3.xlsx
Location: RESERACH/REPORT/PART3/PART3.xlsx
Total Rows: 1411
Supplier: efghousewares.co.uk
```

### Step 2.2: Identify Exact EAN Matches
I extracted all rows where:
- `EAN` column contains a valid barcode (8+ digits)
- `EAN_OnPage` column contains a valid barcode
- Both values match exactly

**Result:** 24 exact EAN matches found

### Step 2.3: Extract Product Details
For each EAN match, I extracted:
- RowID
- ASIN
- EAN
- SupplierTitle (full text)
- AmazonTitle (full text)
- SupplierPrice_incVAT
- SellingPrice_incVAT
- NetProfit
- ROI
- Sales

---

## 3. Initial Script-Based Analysis (Failed Approach)

### What the Script Did
I initially created a Python script (`meticulous_analysis_v3.py`) that used regex patterns to extract pack quantities:

```python
# Example patterns (FLAWED)
patterns = [
    r'(\d+)\s*x\s*(\d+)',  # Matches "4 x 50" BUT ALSO "9x9"
    r'pack\s*of\s*(\d+)',   # Matches "Pack of 10"
    r'(\d+)\s*pack',        # Matches "28 PACK"
]
```

### Critical Errors Found

**Error 1: APOLLO VINEGAR SHAKER**
- Script extracted: "Pack of 15" from "15 x 5.5 x 5.5 cm"
- Reality: These are **dimensions** (15cm height × 5.5cm width × 5.5cm depth)
- Impact: Incorrectly flagged as 1→15 pack mismatch

**Error 2: SUPERIOR FOIL 10 CONTAINERS**
- Script extracted: "Pack of 9" from "9 x 9 inch"
- Reality: These are **tray dimensions** (9 inches × 9 inches)
- Impact: Incorrectly flagged as 1→9 pack mismatch

**Error 3: BAKER & SALT SWISS ROLL TRAY**
- Script extracted: "Pack of 736" from "32 x 23.5 x 1cm"
- Reality: These are **dimensions** (32cm × 23.5cm × 1cm thickness)
- Impact: Completely wrong adjusted profit calculation

### Why Script Analysis Failed
1. Regex cannot understand semantic context
2. Numbers followed by "cm", "mm", "inch" could be dimensions OR quantities
3. Product knowledge is required to distinguish "9x9 inch tray" from "4x50 bags"

---

## 4. Manual Verification Methodology

### Step 4.1: Title-Based Analysis
For each product, I manually read both titles and asked:
1. What is the supplier selling? (single item, pack, bundle?)
2. What is Amazon selling? (single item, pack, bundle?)
3. Are there any explicit quantity indicators? (e.g., "Pack of X", "X pcs", "Xpc")
4. Are numbers dimensions/sizes or quantities?

### Step 4.2: Amazon Browser Verification
For ambiguous products, I used the browser subagent to:
1. Navigate to the exact Amazon product page (https://www.amazon.co.uk/dp/[ASIN])
2. Read the full product title
3. Check the "Quantity" or "Size Name" selector
4. Look for "Unit Count" in technical details
5. Read "About this item" bullet points for pack information

### Step 4.3: Evidence Collection
For each browser verification, I:
1. Captured the verification findings
2. Recorded the exact product title from Amazon
3. Noted any pack size selectors or variations
4. Saved screenshots where needed

---

## 5. Step-by-Step Analysis for Each EAN Match

### Row 363 — PHOODS FOIL TRAY ROASTER
**Supplier Title:** "PHOODS FOIL TRAY ROASTER"
**Amazon Title:** "Superior Sandwich Platter Trays - Pack of 10 Catering Trays..."

**Manual Analysis:**
1. Supplier title mentions no quantity → likely single item
2. Amazon title explicitly says "Pack of 10"
3. **Browser Verification:** Visited https://www.amazon.co.uk/dp/B0DT71SSPT
4. **Confirmed:** Amazon sells 10 trays at £14.97 (£1.50 each)

**Calculation:**
- Supplier cost for 10 trays: £1.08 × 10 = £10.80
- Amazon selling price: £14.97
- FBA fees (~30%): £4.49
- **Adjusted Profit:** £14.97 - £10.80 - £4.49 = **-£0.32**

**Verdict:** ❌ FILTERED OUT (unprofitable after pack adjustment)

---

### Row 370 — EVERREADY T8 4FT 36W TUBE LIGHT
**Supplier Title:** "EVERREADY T8 4FT 36W TUBE LIGHT"
**Amazon Title:** "Eveready T8 Tube 4ft 36w White 3500k"

**Manual Analysis:**
1. Both titles describe a single fluorescent tube
2. No pack indicators in either title
3. "4FT" and "4ft" = length (4 feet)
4. "36W" = wattage (36 watts)

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £8.00)

---

### Row 626 — AIRWICK REED DIFFUSER MULLED WINE
**Supplier Title:** "AIRWICK REED DIFFUSER MULLED WINE 33ML **PK5**"
**Amazon Title:** "Air Wick Essential Oils Reed Diffuser... **5 Bottles X 30ml**"

**Manual Analysis:**
1. Supplier says "PK5" = Pack of 5
2. Amazon says "5 Bottles X 30ml" = 5 bottles
3. Volume difference (33ml vs 30ml) is minor packaging variation

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B07WDRQ4J7
- Confirmed: 5 bottles × 30ml = 150ml total
- Product images show 5 individual boxes

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £16.55)

---

### Row 698 — AMTECH LED MINI TORCH
**Supplier Title:** "AMTECH LED MINI TORCH"
**Amazon Title:** "Amtech S1532 9 LED mini Torch"

**Manual Analysis:**
1. Both describe a single torch
2. "9 LED" = number of LED bulbs, NOT pack quantity
3. No pack indicators

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £2.35)

---

### Row 889 — MASON CASH MIXING BOWL CREAM 29CM
**Supplier Title:** "MASON CASH MIXING BOWL CREAM 29CM"
**Amazon Title:** "Mason Cash Colour Mix Cream Mixing Bowl | 4 Litre Capacity | 29cm..."

**Manual Analysis:**
1. Both describe a single 29cm mixing bowl
2. "4 Litre" = capacity, not pack size
3. Same brand (Mason Cash), same size (29cm)

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £5.11)

---

### Row 931 — TIDYZ DOGGY BAGS STRONG 50 PCS
**Supplier Title:** "TIDYZ DOGGY BAGS STRONG **50 PCS** 30cm x 36cm"
**Amazon Title:** "Tidyz **200** x Extra Large Super Strong Doggy bags **(4 x 50)**,Black"

**Manual Analysis:**
1. Supplier sells 50 bags
2. Amazon sells 200 bags (4 rolls of 50)
3. Clear 1→4 pack mismatch

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B06X9K7NR7
- Confirmed: "50 pcs per roll x 4"
- Size Name selected: "1 count (Pack of 200)"

**Calculation:**
- Supplier cost for 200 bags: £0.67 × 4 = £2.68
- Amazon selling price: £6.50
- FBA fees (~30%): £1.95
- **Adjusted Profit:** £6.50 - £2.68 - £1.95 = **£1.87**

**Verdict:** ⚠️ VERIFIED (Pack Mismatch, but profitable after adjustment)

---

### Row 964 — SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN
**Supplier Title:** "SUPERIOR FOIL **10 CONTAINERS** & LID **9X9IN**"
**Amazon Title:** "Superior **10-Pack** Aluminium Foil Trays... **9 x 9 inch**"

**Manual Analysis:**
1. Supplier says "10 CONTAINERS" = 10-pack
2. Amazon says "10-Pack" = 10-pack
3. "9X9IN" and "9 x 9 inch" = tray SIZE (9 inches × 9 inches), NOT pack quantity

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B0DJDH23JW
- Confirmed: "Pack of 10" selected
- Unit price: £12.97 / 10 = £1.30 each

**CRITICAL CORRECTION:** The script incorrectly read "9X9" as pack size 9. This is the tray dimension!

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £2.13)

---

### Row 1103 — APOLLO VINEGAR SHAKER
**Supplier Title:** "APOLLO VINEGAR SHAKER"
**Amazon Title:** "apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker, Clear **15 x 5.5 x 5.5 cm**"

**Manual Analysis:**
1. Supplier sells single shaker
2. Amazon sells single shaker
3. "15 x 5.5 x 5.5 cm" = DIMENSIONS (Length × Width × Height in cm)

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B009SJXB32
- Product description: "It measures 155x55x55mm" (same as 15.5cm × 5.5cm × 5.5cm)
- Diameter listed as "5.5 Centimetres"
- Weight: 200g (consistent with single glass item)

**CRITICAL CORRECTION:** The script incorrectly read "15" as pack size. This is the HEIGHT in centimeters!

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £0.46)

---

### Row 1173 — PPS ROUND 40 DOYLEYS 21CM
**Supplier Title:** "PPS ROUND **40** DOYLEYS 21CM"
**Amazon Title:** "**40 X** White Round LACE DOYLEYS - 22cm/8.5\"..."

**Manual Analysis:**
1. Supplier says "40 DOYLEYS" = 40 pieces
2. Amazon says "40 X" = 40 pieces
3. Size difference (21cm vs 22cm) is negligible

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B07YQ5HFFN
- Confirmed: "40 Round Placemats"
- Package shows "PACK OF 40" badge

**CRITICAL CORRECTION:** The script incorrectly assumed supplier sells 1 and Amazon sells 40. BOTH sell 40!

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £0.30)

---

### Row 1282 — MIRROR BLUE CANYON SQUARE PLASTIC MIRROR
**Supplier Title:** "MIRROR BLUE CANYON SQUARE PLASTIC MIRROR"
**Amazon Title:** "Blue Canyon - 18cm Free Standing Square Mirror... One Side with **2x Magnification**..."

**Manual Analysis:**
1. Both describe a single mirror
2. "2x Magnification" = optical feature (one side magnifies 2 times), NOT pack quantity

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B007IGLUIK
- Confirmed: Single double-sided mirror
- Price: £8.25 for one mirror

**CRITICAL CORRECTION:** The script incorrectly read "2x" as pack size. This is the magnification factor!

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £0.43)

---

### Row 1395 — FIRE UP NATURAL FIRELIGHTERS 28 PACK
**Supplier Title:** "FIRE UP NATURAL FIRELIGHTERS **28 PACK**"
**Amazon Title:** "Fireglow Firelighters **24 Pack**, White"

**Manual Analysis:**
1. Supplier sells 28 firelighters
2. Amazon sells 24 firelighters
3. Same EAN, but different pack counts

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B07YPPK4JY
- Confirmed: "24 CUBES" displayed on packaging
- Brand shown as "Tiger" (Fireglow is a product line)

**Verdict:** ⚠️ VERIFIED (Pack difference, but supplier has MORE - favorable)

---

### Row 1396 — CHEF AID SHOT GLASSES ASSORTED 20PCE
**Supplier Title:** "CHEF AID SHOT GLASSES ASSORTED **20PCE**"
**Amazon Title:** "Chef Aid Multi-Coloured Plastic Shot Glasses, **Pack of 20**..."

**Manual Analysis:**
1. Supplier says "20PCE" = 20 pieces
2. Amazon says "Pack of 20" = 20 pieces
3. Both sell 20 shot glasses

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B00M36YPIM
- Confirmed: "PACK OF 20" stated in "About this item"

**CRITICAL CORRECTION:** The script incorrectly assumed supplier sells 1 and Amazon sells 20. BOTH sell 20!

**Verdict:** ✅ VERIFIED (1:1 Match, Profit £0.03)

---

## 6. HIGHLY LIKELY Product Verification

These products were identified by the user as strong matches despite no EAN confirmation.

### Row 764 — KILROCK MOULD REMOVER (SOLD EACH)
**Supplier Title:** "KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION 500ML **(SOLD EACH)**"
**Amazon Title:** "Kilrock **3 X** Blast Away Mould Spray 500ml"

**Manual Analysis:**
1. Supplier explicitly says "SOLD EACH" = single 500ml bottle
2. Amazon says "3 X" = 3 bottles
3. Same brand (Kilrock), same product type

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B0791ZQMMZ
- Confirmed: "500 ml (Pack of 3)"
- Unit Count: 3.0 count

**Calculation:**
- Supplier cost for 3 bottles: £2.14 × 3 = £6.42
- Amazon selling price: £9.94
- FBA fees (~30%): £2.98
- **Adjusted Profit:** £9.94 - £6.42 - £2.98 = **£0.54**

**Verdict:** ✅ HIGHLY LIKELY (Brand match, profitable after pack adjustment)

---

### Row 1137 — BLUE CANYON ROUND WALL MIRROR WHITE
**Supplier Title:** "BLUE CANYON ROUND WALL MIRROR WHITE"
**Amazon Title:** "Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, White"

**Manual Analysis:**
1. Same brand (Blue Canyon)
2. Same product type (Round Wall Mirror)
3. Same color (White)
4. "40 cm" = dimensions, not pack

**Browser Verification:** Visited https://www.amazon.co.uk/dp/B01CMHNDKC
- Confirmed: Single 40cm round mirror

**Verdict:** ✅ HIGHLY LIKELY (Strong brand/title match)

---

## 7. Pack Size Detection & Adjusted Profit Calculation

### Pack Detection Rules (Manual)

| Pattern | Interpretation | Example |
|:---|:---|:---|
| "Pack of X" | Pack quantity | "Pack of 10 Trays" = 10 |
| "X PACK" | Pack quantity | "28 PACK" = 28 |
| "XPCE" or "X PCS" | Piece count | "20PCE" = 20 |
| "X x Y" before unit | Dimensions | "9x9 inch" = size |
| "X x Y" with nothing | Could be pack OR dimensions | Requires context |
| "X x Yml" | Total volume | "5 Bottles x 30ml" = 5 bottles |
| "Xcm" or "Xmm" | Dimension | "15cm" = length |

### Adjusted Profit Formula

When pack sizes differ:
```
Adjusted Cost = Supplier Price × (Amazon Pack ÷ Supplier Pack)
FBA Fees ≈ Amazon Selling Price × 0.30
Adjusted Profit = Amazon Selling Price - Adjusted Cost - FBA Fees
```

**Example: TIDYZ DOGGY BAGS**
- Supplier Pack: 50 bags at £0.67
- Amazon Pack: 200 bags at £6.50
- Ratio: 200 ÷ 50 = 4
- Adjusted Cost: £0.67 × 4 = £2.68
- FBA Fees: £6.50 × 0.30 = £1.95
- Adjusted Profit: £6.50 - £2.68 - £1.95 = **£1.87**

---

## 8. Corrections Made from Script Analysis

| RowID | ASIN | Script Said | Manual Finding | Root Cause |
|---:|:---|:---|:---|:---|
| 1103 | B009SJXB32 | "Pack 1→15" | 1:1 Match | "15" is HEIGHT in cm |
| 964 | B0DJDH23JW | "Pack 1→9" | 1:1 Match (both 10-pack) | "9x9" is TRAY SIZE in inches |
| 1173 | B07YQ5HFFN | "Pack 1→40" | 1:1 Match (both 40-pack) | "40" appears in SUPPLIER title too |
| 1396 | B00M36YPIM | "Pack 1→20" | 1:1 Match (both 20-pack) | "20PCE" in supplier title |
| 1282 | B007IGLUIK | "Pack 1→2" | 1:1 Match | "2x" is MAGNIFICATION feature |
| 1198 | B08G1Q1L46 | "Pack 1→736" | 1:1 Match | "32x23.5x1" are TRAY dimensions |
| 1383 | B00W3RVAG6 | "Pack 1→256" | 1:1 Match | "16cm" is DISH SIZE |

---

## 9. Final Categorization Logic

### VERIFIED (Exact EAN, 1:1 Pack)
Criteria:
- EAN matches exactly
- Pack sizes match exactly (or supplier has MORE)
- Profit > £0 after fees

### VERIFIED (Exact EAN, Pack Mismatch)
Criteria:
- EAN matches exactly
- Pack sizes differ
- Adjusted profit > £0 after pack adjustment

### VERIFIED - FILTERED
Criteria:
- EAN matches exactly
- Pack sizes differ
- Adjusted profit ≤ £0 (unprofitable after adjustment)

### HIGHLY LIKELY
Criteria:
- No EAN match
- Same brand name in both titles
- Same product type
- Strong title similarity (>60%)
- No obvious contradictions (pack, size, variant)

### FALSE POSITIVE
Criteria:
- Completely different product categories
- Low title similarity (<20%)
- Examples: Household cleaning product matched to Apple Watch accessories

---

## 10. Lessons Learned

### 1. Never Trust Automated Regex for Pack Detection
Numbers in product titles can mean:
- Pack quantity ("Pack of 10")
- Product capacity ("4 Litre")
- Dimensions ("15 x 5.5 x 5.5 cm")
- Features ("9 LED", "2x Magnification")
- Model numbers ("S1532")

### 2. Always Read Both Full Titles
The supplier title "PPS ROUND **40** DOYLEYS" clearly shows 40 pack, but the script only looked at Amazon title.

### 3. Amazon Browser Verification is Essential
For any ambiguous product, visiting the actual Amazon page provides:
- Selected variation (e.g., "Pack of 10")
- Unit count in technical details
- Images showing packaging
- "About this item" bullet points

### 4. Unit Indicators Matter
- "cm", "mm", "inch", "ft" = DIMENSIONS
- "ml", "L", "ltr" = VOLUME/CAPACITY
- "g", "kg", "oz" = WEIGHT
- "pcs", "pack", "count" = QUANTITY

### 5. Context is King
"4 x 50" in dog bags = 4 rolls of 50 (quantity)
"9 x 9 in" for trays = 9 inches by 9 inches (dimensions)

Human language understanding > Regex patterns

---

## Appendix: Browser Verification Sessions

All browser verifications were recorded with screenshots:
- `verify_b0dt71sspt` - Superior Sandwich Platter Trays
- `verify_b06x9k7nr7` - Tidyz Doggy Bags
- `verify_b07wdrq4j7` - Air Wick Reed Diffuser
- `verify_fire_up` - Fireglow Firelighters
- `verify_chef_aid` - Chef Aid Shot Glasses
- `verify_doyleys` - PPS Doyleys
- `verify_kilrock` - Kilrock Mould Remover
- `verify_superior_foil_10` - Superior Foil 10-Pack
- `verify_mirror_retry` - Blue Canyon Square Mirror
- `verify_vinegar_shaker` - Apollo Vinegar Shaker
- `verify_remaining_1` - Blue Canyon Round Mirror

---

*End of Methodology Report*
