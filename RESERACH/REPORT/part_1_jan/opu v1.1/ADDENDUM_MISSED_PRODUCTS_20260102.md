# ADDENDUM: ADDITIONAL PRODUCTS IDENTIFIED

**Generated:** 2026-01-02  
**Purpose:** Quality check to ensure no products were missed from initial analysis  
**Methodology:** Keyword overlap analysis + title similarity on all 2,402 rows

---

## Summary of Quality Check

| Category | Count | Status |
|----------|-------|--------|
| Products with ≥3 keyword overlap + ≥40% sim | 110 | ⚠️ Reviewed |
| Products with ≥2 key word matches (high profit) | 552 | ⚠️ Reviewed |

---

## ⚠️ KEY FINDING: Many "High Profit" Items are FALSE POSITIVES

The initial sweep found 323 products with >£10 profit that weren't matched. Upon manual review, **most are FALSE POSITIVES** where the Amazon title is completely unrelated:

| Supplier Title | Amazon Title | Issue |
|---------------|--------------|-------|
| AIRWICK CANDLE VANILLA | Lenovo Idea Tab Pro Tablet | ❌ Completely different product |
| FAIRY WASHING UP LIQUID | SIEMENS Coffee Machine | ❌ Completely different product |
| PANASONIC UPRIGHT | ElecKeys Vacuum Cleaner | ❌ EAN/ASIN mismatch |

**Conclusion:** These high profits are artifacts of bad data matching in the source file, NOT missed opportunities.

---

## ✅ GENUINELY MISSED PRODUCTS (To Add to NEEDS VERIFICATION)

The following products SHOULD have been included but were missed by brand/EAN matching:

### 1. QUEST ESPRESSO COFFEE MACHINE (Row 637) ⭐ HIGH VALUE

```
SupplierTitle: QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHER
AmazonTitle:   Quest 36569 Espresso Coffee Machine With Milk Frother
Keyword Overlap: 5 | Title Sim: 41% | Profit: £33.63 | Sales: 500
```

**Reasoning:**
- Brand "QUEST" matches exactly
- Product type "ESPRESSO COFFEE MACHINE" matches
- Feature "MILK FROTHER" matches
- **Should be HIGHLY LIKELY**

**Why Missed:** Brand "QUEST" wasn't in the initial KNOWN_BRANDS list

---

### 2. MOKATE GOLD PREMIUM COFFEE (Row 405) ⭐

```
SupplierTitle: Mokate Gold Premium Coffee Caramel Latte 10pk
AmazonTitle:   Mokate Gold Premium Caramel Latte Coffee Sachets 10 x 18g
Keyword Overlap: 6 | Title Sim: 59% | Profit: £6.78 | Sales: 200
```

**Reasoning:**
- Brand "MOKATE" matches exactly
- Product "GOLD PREMIUM CARAMEL LATTE" matches
- Pack "10pk" = "10 x" matches
- **Should be HIGHLY LIKELY**

---

### 3. SCHOTT ZWIESEL WHITE WINE GLASS (Row 727) ⭐

```
SupplierTitle: SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2
AmazonTitle:   Schott Zwiesel Pure Glassware - White Wine Glasses - Set of 2, 408ml
Keyword Overlap: 5 | Title Sim: 53% | Profit: £7.18 | Sales: 200
```

**Reasoning:**
- Brand "SCHOTT ZWIESEL" matches exactly
- Product "WHITE WINE GLASS" matches
- Pack "SET OF 2" matches
- Capacity 407ml ≈ 408ml (within 1% tolerance)
- **Should be HIGHLY LIKELY**

**Why Missed:** This should have been caught - brand is in list but different EAN

---

### 4. EXTRA SELECT PREMIUM RABBIT FOOD (Row 1008)

```
SupplierTitle: EXTRA SELECT PREMIUM RABBIT FOOD BUCKET 5L
AmazonTitle:   Extra Select Premium Rabbit Mix Bucket 5L - Balanced Nutrition
Keyword Overlap: 6 | Title Sim: 43% | Profit: £4.86 | Sales: 300
```

**Reasoning:**
- Brand "EXTRA SELECT" matches
- Product "PREMIUM RABBIT" + "BUCKET 5L" matches
- **Should be HIGHLY LIKELY**

---

### 5. SOUDAL EXPANDING FOAM 750ML (Row 1302)

```
SupplierTitle: SOUDAL EXPANDING FOAM HANDHELD 750ML
AmazonTitle:   Soudal 750ml Champagne Gap Filler Expanding Foam Handheld
Keyword Overlap: 5 | Title Sim: 52% | Profit: £4.25 | Sales: 400
```

**Reasoning:**
- Brand "SOUDAL" matches exactly
- Product "EXPANDING FOAM" matches
- Capacity "750ML" matches exactly
- **Should be HIGHLY LIKELY**

**Status:** ✅ Already in report (was included)

---

### 6. BACOFOIL EASY CUT KITCHEN FOIL (Row 1317)

```
SupplierTitle: BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M
AmazonTitle:   3 x Easy Cut Refill Kitchen Foil 300mm, 15m
Keyword Overlap: 6 | Title Sim: 64% | Profit: £2.90 | Sales: 500
```

**Reasoning:**
- Brand "BACOFOIL" in supplier, "Easy Cut" in Amazon
- Product "KITCHEN FOIL REFILL 15M" matches
- **BUT:** Amazon is "3 x" = 3-pack
- RSU = 3, need to check adjusted profit

**Pack Analysis:**
- Supplier: 1 roll
- Amazon: 3 rolls
- RSU = 3
- Adjusted Profit = £2.90 - (cost × 2) - need supplier price

**Category:** NEEDS VERIFICATION (pack verification needed)

---

### 7. ELBOW GREASE TOILET CLEANER (Row 406)

```
SupplierTitle: ELBOW GREASE TOILET CLEANER FOAM LEMON FRESH
AmazonTitle:   3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning Action
Keyword Overlap: 6 | Title Sim: 67% | Profit: £2.09 | Sales: 200
```

**Reasoning:**
- Brand "ELBOW GREASE" matches
- Product "TOILET CLEANER" matches
- **BUT:** Amazon is "3 x" = 3-pack

**Status:** Package mismatch likely causes loss - verify

---

### 8. BAKER & SALT SWISS ROLL TRAY (Row 2055)

```
SupplierTitle: BAKER & SALT SWISS ROLL TRAY
AmazonTitle:   Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1.5cm
Keyword Overlap: 6 | Title Sim: 68% | Profit: £0.72 | Sales: 600
```

**Status:** ✅ Already in NEEDS VERIFICATION (dimensions to verify)

---

### 9. FALCON ENAMEL ROUND PIE DISH (Row 2079)

```
SupplierTitle: FALCON ENAMEL ROUND PIE DISH 26CM
AmazonTitle:   FALCON Round Pie Dish White 26CM
Keyword Overlap: 5 | Title Sim: 82% | Profit: £0.89 | Sales: 50
```

**Reasoning:**
- Brand "FALCON" matches
- Product "ROUND PIE DISH" matches
- Size "26CM" matches
- **Should be HIGHLY LIKELY**

---

### 10. AMTECH POINTING TROWEL (Row 1989)

```
SupplierTitle: AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP
AmazonTitle:   Amtech G0230 150mm (6") Pointing trowel with soft grip
Keyword Overlap: 5 | Title Sim: 74% | Profit: £0.63 | Sales: 50
```

**Status:** ✅ Classic HIGHLY LIKELY example - matches perfectly

---

## 📊 REVISED COUNTS

Based on this quality check, the following products should be ADDED:

| Product | Category | Profit | Action |
|---------|----------|--------|--------|
| QUEST ESPRESSO MACHINE | HIGHLY LIKELY | £33.63 | **ADD** |
| MOKATE GOLD COFFEE | HIGHLY LIKELY | £6.78 | **ADD** |
| SCHOTT ZWIESEL WINE GLASS | HIGHLY LIKELY | £7.18 | Already present |
| EXTRA SELECT RABBIT FOOD | HIGHLY LIKELY | £4.86 | **ADD** |
| FALCON ENAMEL PIE DISH | HIGHLY LIKELY | £0.89 | **ADD** |
| BACOFOIL KITCHEN FOIL | NEEDS VERIFICATION | £2.90 | **ADD** (pack check) |
| ELBOW GREASE CLEANER | NEEDS VERIFICATION | £2.09 | **ADD** (scent/pack) |

### Updated HIGHLY LIKELY Count: 68 → **72** (+4 additions)
### Updated NEEDS VERIFICATION Count: 42 → **44** (+2 additions)

---

## 🔍 Brands to Add to Detection List

The following brands were found in genuine matches but weren't in KNOWN_BRANDS:

| Brand | Products Found | Action |
|-------|---------------|--------|
| QUEST | Espresso machines, blenders | **ADD** |
| MOKATE | Coffee products | **ADD** |
| FALCON | Enamelware | **ADD** |
| EXTRA SELECT | Pet food | **ADD** |
| LITTLE TREES | Car fresheners | **ADD** |
| SWIRL | Dryer sheets | **ADD** |
| HEAT HOLDERS | Winter accessories | **ADD** |
| VFM | Paint products | **ADD** |
| URBAN LIVING | Furniture | **ADD** |
| PRO COOK | Cookware | **ADD** |
| KILNER | Glass jars | **ADD** |

---

## 📋 FALSE POSITIVE ANALYSIS

The £258 "AIRWICK CANDLE" matched to "Lenovo Tablet" demonstrates a **fundamental data quality issue** in the source report:

- The EAN matching in the original financial report appears to have errors
- Some rows have mismatched Amazon products entirely
- These are NOT missed opportunities - they're bad data

**Recommendation:** Source data quality should be reviewed upstream.

---

## ✅ CONCLUSION

1. **No major categories missed** - the analysis correctly identified EAN matches and brand matches
2. **4 additional HIGHLY LIKELY products** identified via keyword analysis
3. **2 additional NEEDS VERIFICATION products** identified (pack size concerns)
4. **11 brands** should be added to detection list for future analyses
5. **Many "high profit" rows are FALSE POSITIVES** due to source data quality issues

---

*Quality check completed: 2026-01-02*  
*This addendum supplements PHASEA_MANUAL_REPORT_20260102_THOROUGH.md*
