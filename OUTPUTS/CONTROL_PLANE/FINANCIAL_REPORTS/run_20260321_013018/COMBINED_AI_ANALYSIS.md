# FBA AI Analysis Report
**Source:** fba_analysis_2026-03-20 (1).csv
**Total Rows Analyzed:** 41
**Tiers Included:** ['TIER_1_VERIFIED', 'TIER_2_LIKELY', 'TIER_3_NEEDS_REVIEW']
**Model:** mimo-v2-pro-free
**Generated:** 2026-03-21T01:32:17.284928

---

## Batch 1

# Amazon FBA Arbitrage Analysis Report

## VERIFIED
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| VERIFIED | 95 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | 5.03276E+12 | 5.03276E+12 | B003XKPUSQ | £1.72 | £7.99 | £2.35 | 118.6% | 200 | Same (1 unit) | £2.35 | Exact EAN match, brand (Amtech) and product type (LED mini torch) match. | Low risk. |
| VERIFIED | 90 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush; Beige | 5.0129E+12 | 5.0129E+12 | B008CY80YY | £0.77 | £3.75 | £0.17 | 13.9% | 400 | Same (1 unit) | £0.17 | Exact EAN match, brand (Chef Aid) and core product (Pastry Brush) match. "3 in 1" vs "Pure Bristle" is a minor variant descriptor. | Low risk. |
| VERIFIED | 85 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml (Pack | 5.0393E+12 | 5.0393E+12 | B0111N9Z1O | £3.89 | £10.43 | £0.79 | 20.9% | 50 | Same (1 unit) | £0.79 | Exact EAN match, brand (House Mate) and product (Stainless Steel Cleaner) match. Amazon title specifies 400ml, supplier title is generic. | Low risk. |

## HIGH LIKELIHOOD
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| HIGH LIKELIHOOD | 80 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle; Salted | 5.05325E+12 | 5.05325E+12 | B09KCLYC1D | £1.30 | £9.99 | £2.55 | 156.1% | 50 | Same (1 unit) | £2.55 | Exact EAN match. Core brand (Pan Aroma) and scent (Salted Caramel) match. Supplier specifies "Jar Candle 85GM", Amazon specifies "Decorative Holder". | **Variant Trap Risk:** Amazon title includes "Orange Decorative Holder". Product form may differ (jar vs holder). |
| HIGH LIKELIHOOD | 80 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | 5.05325E+12 | 5.05325E+12 | B083XH692T | £1.30 | £6.87 | £1.34 | 81.9% | 100 | Same (16pk) | £1.34 | Exact EAN match. Brand, product type (Tea Lights), count (16pk), and scent (Apple & Cinnamon) match perfectly. | Low risk. |
| HIGH LIKELIHOOD | 75 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | 5.05325E+12 | 5.05325E+12 | B083XH692T | £1.30 | £6.87 | £1.34 | 81.9% | 100 | Likely Same (16pk) | £1.34 | Exact EAN match. Brand and scent match. Supplier title "ROUND APPLE CINNAMON EACH" is ambiguous but likely refers to the same 16pk tea lights. | **Pack Ambiguity:** Supplier title says "EACH" which could imply a single unit, but EAN and Amazon title confirm 16pk. |
| HIGH LIKELIHOOD | 70 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape \| Picture Frame Tape \| 48mm x 33m | 5.02779E+12 | 5.02779E+12 | B073VPL2VQ | £1.15 | £6.53 | £0.43 | 28.6% | 50 | Different Dimensions | £0.43 | Exact EAN match. Brand (Ultratape) and product type (Picture Frame Tape) match. | **Size Mismatch:** Supplier: 24mm x 50m. Amazon: 48mm x 33m. Different dimensions. Likely a variant or updated product. Profit calculation may be invalid. |
| HIGH LIKELIHOOD | 70 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS | Fairy Soap Dispensing Dish Brush | 5.0103E+12 | 5.0103E+12 | B0BYKDX25N | £1.20 | £6.57 | £0.43 | 27.4% | 50 | Likely Different (Supplier has refills) | £0.43 | Exact EAN match. Brand (Fairy) and core product (Soap Dispensing Dish Brush) match. | **Pack Contents Mismatch:** Supplier title includes "& REFILLS 3PCS". Amazon title is just the brush. Supplier likely sells a bundle. |
| HIGH LIKELIHOOD | 70 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | 5.0103E+12 | 5.0103E+12 | B0BYKDX25N | £1.73 | £6.57 | £0.06 | 2.8% | 50 | Likely Same (1 unit) | £0.06 | Exact EAN match. Brand and product name match exactly. | **Price Anomaly:** Supplier price (£1.73) is higher than Row 8 (£1.20) for the same EAN. May indicate a different pack or cost change. |
| HIGH LIKELIHOOD | 65 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre; Pack of | 5.01142E+12 | 5.01142E+12 | B09NCVWKD6 | £11.41 | £18.98 | £0.19 | 1.9% | 50 | Different Size & Pack | £0.03 | Exact EAN match. Brand (Dettol) and product line (Power & Pure Kitchen) match. | **Major Size/Pack Mismatch:** Supplier: 750ml, Pack of 6. Amazon: 1 Litre, Pack of ?. Different volumes. Profit per unit is likely much lower. |
| HIGH LIKELIHOOD | 65 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | 5.01085E+12 | 5.01085E+12 | B0013IUIPA | £5.45 | £14.78 | £0.05 | 0.9% | 100 | Different Size | £0.02 | Exact EAN match. Brand (Price & Kensington) and product (Teapot) match. | **Size Mismatch:** Supplier: 2 Cup. Amazon: 6 Cup. Different capacities. Profit calculation invalid. |
| HIGH LIKELIHOOD | 65 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box; Grey | 5.05252E+12 | 5.05252E+12 | B0B8T9L8RY | £2.89 | £8.95 | £0.01 | 0.3% | 100 | Likely Different Product | £0.01 | Exact EAN match. Brand (Smart Choice) matches. | **Product Mismatch:** Supplier: "Tyre Ring Dog Toy". Amazon: "Dog Toy Box". Different items. |
| HIGH LIKELIHOOD | 60 | SWIRL TUMBLE DRYER SHEETS LAVENDER 35PK | 4X Swirl Lavender Tumble Dryer Sheets - 40 per Pack | 5.05325E+12 | 5.05325E+12 | B085W8MDLH | £1.37 | £7.64 | £0.99 | 58.4% | 200 | Different Pack Count | £0.25 | Exact EAN match. Brand (Swirl) and product (Lavender Tumble Dryer Sheets) match. | **Pack Size Mismatch:** Supplier: 35pk. Amazon: 4x40pk (160 sheets). Amazon is a multipack. Adjusted profit per single pack is ~£0.25. |
| HIGH LIKELIHOOD | 60 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEONE SPE | Waterproof Robin Memorial Graveside Lantern with LED Candle | 5.05536E+12 | 5.05536E+12 | B096KRFC4W | £6.95 | £13.99 | £0.08 | 1.2% | 50 | Same (1 unit) | £0.08 | Exact EAN match. Brand and product description (Memorial Graveside Lantern with Robin) match closely. | Low risk. |

## NEEDS VERIFICATION
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| NEEDS VERIFICATION | 55 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMA® RED Decorative Holder & Scented Candle; RED Berry | 5.05325E+12 | 5.05325E+12 | B09KCMWXQX | £1.30 | £8.45 | £1.49 | 91.5% | 50 | Same (1 unit) | £1.49 | Exact EAN match. Brand and scent (Red Berry) match. | **Variant Trap Risk:** Supplier: "Jar Candle 85GM". Amazon: "RED Decorative Holder". Form factor may differ. Requires visual check. |
| NEEDS VERIFICATION | 50 | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY ASSORTED 25 | Nuage Body Powder Set - Talc-Free; Cherry Blossom and Water | 5.05325E+12 | 5.05325E+12 | B0FH524WXP | £1.27 | £5.99 | £0.25 | 15.6% | 200 | Likely Different (Supplier is assorted 25) | £0.25 | Exact EAN match. Brand (Nuage) and product type (Talc-Free Body Powder) match. | **Pack/Variant Mismatch:** Supplier: "ASSORTED 25". Amazon: "Set". Likely a bulk/multi-unit pack vs a set. Needs verification of contents. |
| NEEDS VERIFICATION | 45 | ELBOW GREASE TOILET CLEANER FOAM LEMON FRESH 500G | 3 x Elbow Grease Foaming Toilet Cleaner; Deep Cleaning Actio | 5.05325E+12 | 5.05325E+12 | B0CCJS5GKB | £0.00* | £8.38 | £2.09 | 380.6% | 200 | Supplier is 1 unit, Amazon is 3-pack | £0.70 | Exact EAN match. Brand (Elbow Grease) and product (Foaming Toilet Cleaner) match. | **CRITICAL: Supplier price is £0.00 (data error). Pack size mismatch: Supplier is single 500g, Amazon is 3-pack. Adjusted profit is estimated.** |
| NEEDS VERIFICATION | 45 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner; Deep Cleaning Actio | 5.05325E+12 | 5.05325E+12 | B0CCJS5GKB | £2.09 | £9.17 | £0.82 | 35.9% | 200 | Supplier is 1 unit, Amazon is 3-pack | £0.27 | Exact EAN match. Brand and product type match. | **Pack Size Mismatch:** Supplier is single 500g (Eucalyptus), Amazon is a 3-pack (scent unspecified). Scent variant risk. |

*Note: Row 16 SupplierPrice_incVAT is £0.00, which is likely a data error. Profit/ROI calculations are based on NetProfit figure provided.*

## AUDITED OUT
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| AUDITED OUT | 90 | PAN AROMA CANDLE 85G PURE JASMINE | Pan Aroma Orange Decorative Holder & Scented Candle; Salted | 5.05325E+12 | 5.05325E+12 | B09KCLYC1D | £1.30 | £9.99 | £2.55 | 156.1% | 50 | N/A | N/A | Exact EAN match, but **titles describe completely different products**. Supplier: "Pure Jasmine". Amazon: "Orange... Salted Caramel". | **FALSE POSITIVE:** Different scent variants. EAN likely reused for multiple SKUs. |
| AUDITED OUT | 90 | PAN AROMA CANDLE 85G LEMONGRASS | Pan Aroma Orange Decorative Holder & Scented Candle; Salted | 5.05325E+12 | 5.05325E+12 | B09KCLYC1D | £1.30 | £9.99 | £2.55 | 156.1% | 50 | N/A | N/A | Exact EAN match, but **titles describe completely different products**. Supplier: "Lemongrass". Amazon: "Orange... Salted Caramel". | **FALSE POSITIVE:** Different scent variants. EAN likely reused for multiple SKUs. |

## Summary

Analysis of the 20 product rows reveals a high incidence of data mismatches and variant traps, particularly within the Pan Aroma candle range.

- **VERIFIED (3 rows):** Strong, unambiguous matches with exact EAN and product alignment. Recommended for sourcing.
- **HIGH LIKELIHOOD (11 rows):** Strong evidence but with one or more discrepancies (pack size, dimensions, variant descriptors). These require manual verification of the physical product before purchasing. Several have significant pack size mismatches that drastically affect unit profitability.
- **NEEDS VERIFICATION (4 rows):** Moderate evidence with clear risks like assorted packs, data errors (£0.00 price), or ambiguous scent/variant information. Manual check is essential.
- **AUDITED OUT (2 rows):** Confirmed false positives. The same EAN is used for different product variants (scents), making them unmatchable.

**Key Findings:**
1.  **EAN Reuse is a Major Trap:** The Pan Aroma EAN `5.05325E+12` is used for multiple distinct candle scents, leading to false matches.
2.  **Pack Size Discrepancies are Common:** Many supplier listings are for single units while Amazon listings are for multipacks (e.g., Elbow Grease, Swirl, Dettol). This makes the reported NetProfit and ROI figures misleading; adjusted per-unit profit is often much lower.
3.  **High ROI is a Red Flag:** The highest ROI items (Pan Aroma candles, Elbow Grease) are either false positives or have critical data/pack size issues, confirming the need for skepticism.

**Recommendation:** Prioritize sourcing from the **VERIFIED** list. For the **HIGH LIKELIHOOD** and **NEEDS VERIFICATION** lists, conduct a manual product and listing check to resolve pack size and variant discrepancies before any investment. Discard all **AUDITED OUT** items.

---

## Batch 2

# Amazon FBA Arbitrage Analysis Report

## VERIFIED
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| VERIFIED | 95 | CURVER RATTAN ROUND LARGE ORGANISER GREY | CURVER Style Rattan Effect Kitchen; Living room; Bathroom; B | 3.25392E+12 | 3.25392E+12 | B092ZL7VRV | £1.50 | £15.00 | £2.71 | 150.6% | 50 | Same | £2.71 | Exact EAN match, brand "CURVER" matches, product type "Rattan Organiser" consistent. | Minor title variation but describes same product. |
| VERIFIED | 90 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller; Ready to Use; Refill for Pressure S | 5.01768E+12 | 5.01768E+12 | B01MYBH3SU | £6.02 | £21.12 | £3.52 | 63.2% | 50 | Same | £3.52 | Exact EAN match, brand "Roundup" matches, "Path Weedkiller RTU" consistent. | Amazon title truncated but clearly same product. |
| VERIFIED | 90 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set (11- | 5.01056E+12 | 5.01056E+12 | B0114IPMS6 | £6.18 | £15.10 | £2.15 | 37.8% | 100 | Same | £2.15 | Exact EAN match, brand "Draper" matches, "Metric Combination Spanner Set" consistent. | None significant. |
| VERIFIED | 85 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | 5.02959E+12 | 5.02959E+12 | B00JITHXRM | £2.89 | £8.09 | £0.86 | 29.1% | 300 | Same | £0.86 | Exact EAN match, brand "Rolson" matches, "8oz Claw Hammer" consistent. | Supplier says "Fibreglass", Amazon says "Stubby" - likely same variant. |
| VERIFIED | 85 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel; Multi; 280 x 120 mm | 5.02959E+12 | 5.02959E+12 | B006A7D1O4 | £2.68 | £9.29 | £0.74 | 26.7% | 100 | Same | £0.74 | Exact EAN match, brand "Rolson" matches, "Plastering Trowel 280x..." consistent. | Minor dimension difference (115mm vs 120mm width) - likely measurement variance. |
| VERIFIED | 85 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | 5.03276E+12 | 5.03276E+12 | B00ABJQTPU | £2.00 | £7.49 | £0.35 | 15.8% | 50 | Same | £0.35 | Exact EAN match, brand "Amtech" matches, "Trowel Soft Grip" consistent. | Supplier title "5X2" unclear but likely refers to size. |
| VERIFIED | 85 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack; Kills Mice | 5.03814E+12 | 5.03814E+12 | B074V9468X | £2.22 | £7.79 | £0.27 | 11.3% | 50 | Same | £0.27 | Exact EAN match, brand "The Big Cheese" matches, "Quick Click Mouse Trap 2PK" consistent. | None significant. |
| VERIFIED | 85 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | 5.0174E+12 | 5.0174E+12 | B000OTPWNC | £3.56 | £10.15 | £0.31 | 8.8% | 100 | Same | £0.31 | Exact EAN match, brand "Ashley" matches, "Cash Box" consistent. | Supplier says "4.5 Inch", Amazon says "20.5cm" - same size (4.5" ≈ 11.4cm, discrepancy). **Verify size.** |

## HIGH LIKELIHOOD
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| HIGH LIKELIHOOD | 75 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Office S | 5.0362E+12 | 5.0362E+12 | B077G5PTRK | £4.57 | £18.55 | £0.55 | 12.6% | 50 | Likely Same | £0.55 | Exact EAN match, brand "Wham" matches, "Clear Storage Box with Lid" consistent. | Amazon title doesn't specify "32LTR" or "Underbed". **Verify capacity.** |

## NEEDS VERIFICATION
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| NEEDS VERIFICATION | 60 | PAN AROMA CANDLE 85G LIME GINGER | Pan Aroma Orange Decorative Holder & Scented Candle; Salted | 5.05325E+12 | 5.05325E+12 | B09KCLYC1D | £1.53 | £9.99 | £2.35 | 129.1% | 50 | Likely Same | £2.35 | Exact EAN match, brand "Pan Aroma" matches. | **Major scent mismatch:** Supplier "Lime Ginger" vs Amazon "Orange... Salted". Likely different variants. |
| NEEDS VERIFICATION | 60 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | 5.05325E+12 | 5.05325E+12 | B083XH692T | £1.30 | £6.87 | £1.34 | 81.9% | 100 | Likely Same | £1.34 | Exact EAN match, brand "Pan Aroma" matches, "Apple & Cinnamon" consistent. | **Format mismatch:** Supplier "TALL CANDLE EACH" vs Amazon "16 Tea Lights". Likely different product forms. |
| NEEDS VERIFICATION | 55 | STATUS UK VISITOR TRAVEL ADAPTER | Status India to UK Power Adaptor; India to UK Travel Adapter | 5.02282E+12 | 5.02282E+12 | B0F44SLX44 | £1.21 | £7.49 | £1.06 | 68.1% | 50 | Likely Same | £1.06 | Exact EAN match, brand "Status" matches, "Travel Adapter" consistent. | Supplier generic "UK Visitor", Amazon specific "India to UK". **Verify compatibility.** |
| NEEDS VERIFICATION | 55 | MASTERCLASS SALT/PAPPER MILL BLACK | MasterClass Pepper Mill or Salt Grinder with Interchangeable | 5.02825E+12 | 5.02825E+12 | B07MC8YD65 | £4.37 | £10.49 | £0.42 | 10.1% | 100 | Likely Same | £0.42 | Exact EAN match, brand "MasterClass" matches, "Salt/Pepper Mill" consistent. | Supplier says "SALT/PAPPER MILL BLACK", Amazon says "Pepper Mill or Salt Grinder with Interchangeable". **Verify if black and if includes both functions.** |
| NEEDS VERIFICATION | 50 | FRAGRANT CLOUD EDT 100ML POUR FEMME EACH | Fragrant Cloud Rose Ladies Women Perfume Eau De Parfum Spray | 5.05517E+12 | 5.05517E+12 | 6040418214 | £1.61 | £7.50 | £1.24 | 65.3% | 100 | Likely Same | £1.24 | Exact EAN match, brand "Fragrant Cloud" matches, "100ML Pour Femme" consistent. | **Product type mismatch:** Supplier "EDT" (Eau de Toilette) vs Amazon "Eau De Parfum". Different concentrations. |
| NEEDS VERIFICATION | 50 | ROYLE HOME SPRINGFORM CAKE TIN | Royle Kids 2 Mini Springform Cake Tin Kids Round 5Inch Non S | 5.0153E+12 | 5.0153E+12 | B01APK7CDC | £2.33 | £7.88 | £0.19 | 7.7% | 100 | **Pack Size Diff** | £0.10 per tin | Exact EAN match, brand "Royle" matches, "Springform Cake Tin" consistent. | **Pack size mismatch:** Supplier implies single tin, Amazon "2 Mini... 5Inch". **Recalculate profit per unit.** |

## AUDITED OUT
| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| AUDITED OUT | 90 | MUNCH CRUNCH RAWHIDE BONE NAT JUMBO | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe Fille | 5.05038E+12 | 5.05038E+12 | B08MVDCSJQ | £1.21 | £8.59 | £1.66 | 106.3% | 50 | Different Product | N/A | EAN matches but titles describe different products. | **Product mismatch:** Supplier "Rawhide Bone Nat Jumbo" vs Amazon "8 Tripe Filled" chews. Different materials/contents. |
| AUDITED OUT | 85 | FIRST STEPS FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BPA Fre | 5.0153E+12 | 5.0153E+12 | B08CY3F21W | £0.94 | £6.99 | £1.30 | 97.4% | 50 | Different Product | N/A | EAN matches but titles describe different products. | **Product mismatch:** Supplier "Food Storage Pots with Spoon 4PC" vs Amazon "8 Baby Food Freezer Cubes Tray". Different items. |
| AUDITED OUT | 85 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50);Bla | 5.02536E+12 | 5.02536E+12 | B06X9K7NR7 | £0.67 | £6.50 | £0.74 | 66.4% | 500 | **Pack Size Diff** | £0.18 per 50 bags | EAN matches but pack sizes differ significantly. | **Pack size mismatch:** Supplier "50 PCS" vs Amazon "200 x (4 x 50)". Amazon is 4x quantity. **Recalculate profit per unit.** |
| AUDITED OUT | 80 | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Status 15 Metre TV Aerial Cable Extension Kit | 5.02282E+12 | 5.02282E+12 | B08N713Y2V | £1.61 | £7.95 | £1.06 | 55.8% | 200 | Different Product | N/A | EAN matches but lengths differ. | **Length mismatch:** Supplier "5M CABLE" vs Amazon "15 Metre". Different product lengths. |
| AUDITED OUT | 75 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clips Bun | 5.01035E+12 | 5.01035E+12 | B096K1WR72 | £3.90 | £11.77 | £1.26 | 33.1% | 100 | Different Product | N/A | EAN matches but products differ. | **Product mismatch:** Supplier "Clips PK3" only vs Amazon "cover + Clips Bundle". Different bundle. |

## Summary
- **VERIFIED**: 8 rows (40%) — Strong EAN and title matches, recommended for sourcing.
- **HIGH LIKELIHOOD**: 1 row (5%) — Good match but missing key specification; manual verification recommended.
- **NEEDS VERIFICATION**: 6 rows (30%) — EAN matches but title discrepancies (variants, formats, scents) require manual check before purchase.
- **AUDITED OUT**: 5 rows (25%) — False positives due to product mismatches or significant pack size differences; excluded from arbitrage.

**Total rows analyzed: 20.** The majority (75%) have EAN matches, but only 40% are verified true matches. Title analysis is critical to avoid false positives, especially with variant traps and pack size discrepancies.

---

## Batch 3

### Analysis Results

#### **AUDITED OUT** — False positives, excluded

| Verdict | Confidence (0-100) | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice_incVAT | SellingPrice_incVAT | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit (approx) | Key Match Evidence | Key Risks / Notes |
|---------|-------------------|---------------|-------------|--------------|------------|------|----------------------|---------------------|-----------|-----|-------|--------------|--------------------------|-------------------|-------------------|
| AUDITED OUT | 95 | DOVE APA INVISIBLE DRY MENS 250ML PK6 | Dove Men + Care Invisible Dry Antiperspirant Deodorant Aeros | 8711600555522 | 8711600555522 | B0D47FBD1B | £14.10 | £22.99 | £0.17 | 1.4% | 100 | **DISCREPANCY** (Supplier: 6-pack, Amazon: likely single) | **-£1.95** per unit | Exact EAN match. | **Critical pack size mismatch.** Supplier title clearly states "PK6" (6-pack). Amazon title does not specify pack size, implying a single unit. Recalculation shows a **loss per unit** if Amazon listing is a single. ROI is abnormally low (1.4%), a classic false-positive indicator. "West Africa Only" category suggests potential regional restrictions or listing errors. |

### Summary
Out of 1 product row analyzed, **1 row was audited out** as a false positive. The primary reason was a critical pack size discrepancy (supplier 6-pack vs. likely Amazon single unit), which, when adjusted for, revealed a negative profit per unit. The exact EAN match was overridden by this clear evidence of different products being sold. No rows were verified, highly likely, or needed verification.

---

