"""
Generate CSV outputs for TRUE Manual Verification results
Output to opu1 folder
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\opu1")
DATE_STAMP = datetime.now().strftime("%Y%m%d")

# Manual verification results from TRUE Stage 6 analysis
# These are the results from my manual title-by-title review

manual_verified_data = [
    # CONFIRMED MATCHES
    {
        "Row": 913,
        "Manual_Verdict": "CONFIRMED_MATCH",
        "Confidence": 95,
        "SupplierTitle": "AMTECH POINTING TROWEL 150M(6\") WITH SOFT GRIP",
        "AmazonTitle": "Amtech G0230 150mm (6\") Pointing trowel with soft grip",
        "Supplier_EAN": "5032759027644",
        "Amazon_EAN": "-",
        "ASIN": "B00ABJQTPU",
        "SupplierPrice": 1.71,
        "NetProfit": 0.63,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.63,
        "Sales": 50,
        "Exclusion_Reason": "",
        "Evidence": "Brand (Amtech), size (150mm/6\"), feature (soft grip) all match exactly"
    },
    {
        "Row": 727,
        "Manual_Verdict": "CONFIRMED_MATCH",
        "Confidence": 90,
        "SupplierTitle": "GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVERY",
        "AmazonTitle": "Giftmaker Collection Large Christmas Santa Sack Special Delivery Bag",
        "Supplier_EAN": "5012128616778",
        "Amazon_EAN": "-",
        "ASIN": "B09HCS9QM2",
        "SupplierPrice": 2.28,
        "NetProfit": 1.04,
        "RSU": 1,
        "Manual_Adjusted_Profit": 1.04,
        "Sales": 100,
        "Exclusion_Reason": "",
        "Evidence": "Brand (Giftmaker), product (Santa Sack), feature (Special Delivery) all match"
    },
    {
        "Row": 1050,
        "Manual_Verdict": "CONFIRMED_MATCH",
        "Confidence": 85,
        "SupplierTitle": "HARRIS PUTTY KNIFE",
        "AmazonTitle": "Harris Seriously Good Putty Knife",
        "Supplier_EAN": "5056287402902",
        "Amazon_EAN": "-",
        "ASIN": "B0815B7FBY",
        "SupplierPrice": 1.08,
        "NetProfit": 0.13,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.13,
        "Sales": 50,
        "Exclusion_Reason": "",
        "Evidence": "Brand (Harris), product (Putty Knife) match. Verify Seriously Good line."
    },
    {
        "Row": 725,
        "Manual_Verdict": "CONFIRMED_MATCH",
        "Confidence": 85,
        "SupplierTitle": "AMTECH SHARPENING STONE 2000",
        "AmazonTitle": "Amtech E2300 300mm (12\") Cigar Sharpening Stone",
        "Supplier_EAN": "5032759001675",
        "Amazon_EAN": "-",
        "ASIN": "B004TRT3K8",
        "SupplierPrice": 2.56,
        "NetProfit": 1.02,
        "RSU": 1,
        "Manual_Adjusted_Profit": 1.02,
        "Sales": 50,
        "Exclusion_Reason": "",
        "Evidence": "Brand (Amtech), product (Sharpening Stone) match. Model numbers related."
    },
    {
        "Row": 852,
        "Manual_Verdict": "CONFIRMED_MATCH",
        "Confidence": 80,
        "SupplierTitle": "DRAPER SPANNER SET METRIC COMBINATION",
        "AmazonTitle": "Draper 1 x Redline 68481 Metric Combination Spanner Set (11-Piece)",
        "Supplier_EAN": "5010559684793",
        "Amazon_EAN": "5010559684816",
        "ASIN": "B0114IPMS6",
        "SupplierPrice": 9.12,
        "NetProfit": 2.15,
        "RSU": 1,
        "Manual_Adjusted_Profit": 2.15,
        "Sales": 100,
        "Exclusion_Reason": "",
        "Evidence": "Brand (Draper), product type (Metric Combination Spanner Set) match. EANs similar. Verify piece count."
    },
    # NEEDS VERIFICATION
    {
        "Row": 974,
        "Manual_Verdict": "NEEDS_VERIFICATION",
        "Confidence": 60,
        "SupplierTitle": "ELF ARRIVAL ENVELOPE OUTFIT",
        "AmazonTitle": "Christmas Naughty Elf Arrival Clothes - Plush Snowman Outfit",
        "Supplier_EAN": "5050565795922",
        "Amazon_EAN": "-",
        "ASIN": "B09J3T86D8",
        "SupplierPrice": 1.65,
        "NetProfit": 0.37,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.37,
        "Sales": 50,
        "Exclusion_Reason": "Possible variant mismatch (envelope vs snowman)",
        "Evidence": "Same product category but different style names in titles"
    },
    # FALSE MATCHES - PACK MISMATCH
    {
        "Row": 332,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "TIDYZ WHEELY BIN LINERS 5 BAGS 300L",
        "AmazonTitle": "Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish Bags 300L",
        "Supplier_EAN": "5025364005824",
        "Amazon_EAN": "5025762919174",
        "ASIN": "B07MGLHMWY",
        "SupplierPrice": 1.19,
        "NetProfit": 2.77,
        "RSU": 6,
        "Manual_Adjusted_Profit": -3.18,
        "Sales": 500,
        "Exclusion_Reason": "PACK MISMATCH: Supplier 5 bags vs Amazon 30 bags. RSU=6. Profit turns negative.",
        "Evidence": "Titles explicitly show: Supplier '5 BAGS', Amazon '30' bags"
    },
    {
        "Row": 628,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M",
        "AmazonTitle": "3 x Easy Cut Refill Kitchen Foil 300mm, 15m",
        "Supplier_EAN": "5023139270705",
        "Amazon_EAN": "9876553908060",
        "ASIN": "B08TCDBQTC",
        "SupplierPrice": 2.85,
        "NetProfit": 2.90,
        "RSU": 3,
        "Manual_Adjusted_Profit": -2.80,
        "Sales": 500,
        "Exclusion_Reason": "PACK MISMATCH: Amazon '3 x' = 3 rolls. RSU=3. Profit turns negative.",
        "Evidence": "Amazon title starts with '3 x' indicating 3-pack"
    },
    {
        "Row": 369,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L",
        "AmazonTitle": "Bacofoil 3 x Zipper Small All Purpose Bags (45 Bags)",
        "Supplier_EAN": "5023139862917",
        "Amazon_EAN": "-",
        "ASIN": "B08FBJ59DR",
        "SupplierPrice": 1.42,
        "NetProfit": 2.93,
        "RSU": 3.75,
        "Manual_Adjusted_Profit": -0.98,
        "Sales": 500,
        "Exclusion_Reason": "PACK MISMATCH: Supplier 12 bags vs Amazon 45 bags. RSU=3.75 (not clean multiple).",
        "Evidence": "Supplier '12 PACK', Amazon '45 Bags' = ambiguous pack math"
    },
    {
        "Row": 420,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "SOUDAL EXPANDING FOAM HAND HELD 150ML",
        "AmazonTitle": "Soudal 750ml Champagne Gap Filler Expanding Foam Handheld (3)",
        "Supplier_EAN": "5411183131217",
        "Amazon_EAN": "-",
        "ASIN": "B07STZLCM6",
        "SupplierPrice": 2.28,
        "NetProfit": 5.47,
        "RSU": 15,
        "Manual_Adjusted_Profit": -26.45,
        "Sales": 400,
        "Exclusion_Reason": "SIZE + PACK MISMATCH: Supplier 150ml single vs Amazon 750ml x 3. Completely different products.",
        "Evidence": "Supplier '150ML', Amazon '750ml' + '(3)' = 15x total volume difference"
    },
    {
        "Row": 618,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "SOUDAL EXPANDING FOAM HANDHELD 750ML",
        "AmazonTitle": "Soudal 750ml Champagne Gap Filler Expanding Foam Handheld (3)",
        "Supplier_EAN": "5411183078956",
        "Amazon_EAN": "-",
        "ASIN": "B07STZLCM6",
        "SupplierPrice": 4.56,
        "NetProfit": 4.25,
        "RSU": 3,
        "Manual_Adjusted_Profit": -4.87,
        "Sales": 400,
        "Exclusion_Reason": "PACK MISMATCH: Amazon '(3)' = 3-pack. RSU=3. Profit turns negative.",
        "Evidence": "Web search confirms B07STZLCM6 is 3-pack of 750ml cans"
    },
    {
        "Row": 752,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "MARIGOLD OUTDOOR GLOVES EXTRA LARGE",
        "AmazonTitle": "Marigold 2 x Extra Tough Outdoor Gloves - Single Pair (Extra Large)",
        "Supplier_EAN": "5010232988019",
        "Amazon_EAN": "9790504074621",
        "ASIN": "B08XWB7JW9",
        "SupplierPrice": 2.28,
        "NetProfit": 1.41,
        "RSU": 2,
        "Manual_Adjusted_Profit": -0.87,
        "Sales": 200,
        "Exclusion_Reason": "PACK MISMATCH: Amazon '2 x' = 2 pairs. RSU=2. Profit turns negative.",
        "Evidence": "Amazon title shows '2 x' = 2 pairs"
    },
    {
        "Row": 771,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "DOFF CONCENTRATED MULTI PURPOSE FEED 1L",
        "AmazonTitle": "2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose Feed",
        "Supplier_EAN": "5013655218435",
        "Amazon_EAN": "-",
        "ASIN": "B073TZKMK9",
        "SupplierPrice": 3.70,
        "NetProfit": 1.82,
        "RSU": 2,
        "Manual_Adjusted_Profit": -1.88,
        "Sales": 50,
        "Exclusion_Reason": "PACK MISMATCH: Amazon '2 X' = 2 bottles. RSU=2. Profit turns negative.",
        "Evidence": "Amazon title starts with '2 X' = 2-pack"
    },
    {
        "Row": 418,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "GROSVENOR 55CM TROUGH BLACK",
        "AmazonTitle": "4 Black Gros Trough 55cm",
        "Supplier_EAN": "5014348297157",
        "Amazon_EAN": "-",
        "ASIN": "B0723GK5V9",
        "SupplierPrice": 6.27,
        "NetProfit": 5.93,
        "RSU": 4,
        "Manual_Adjusted_Profit": -12.88,
        "Sales": 50,
        "Exclusion_Reason": "PACK MISMATCH: Amazon '4' = 4-pack. RSU=4. Deeply unprofitable.",
        "Evidence": "Amazon title starts with '4' = 4 troughs"
    },
    # FALSE MATCHES - DIFFERENT PRODUCTS
    {
        "Row": 900,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "ROLSON CLAW HAMMER FIBREGLASS 8OZ",
        "AmazonTitle": "Rolson 11201 8oz Stubby Claw Hammer",
        "Supplier_EAN": "5029594103718",
        "Amazon_EAN": "5029594112017",
        "ASIN": "B00JITHXRM",
        "SupplierPrice": 2.85,
        "NetProfit": 0.86,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.86,
        "Sales": 300,
        "Exclusion_Reason": "DIFFERENT PRODUCT: Fibreglass (standard length) vs Stubby (compact hammer)",
        "Evidence": "Web research: Fibreglass ~270mm standard hammer. Stubby ~165mm compact hammer. Different products."
    },
    {
        "Row": 1080,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK",
        "AmazonTitle": "STATUS 2 Way Socket 2 USB Port Cable Free Socket",
        "Supplier_EAN": "5022822194984",
        "Amazon_EAN": "5022822207776",
        "ASIN": "B08CVK7746",
        "SupplierPrice": 3.99,
        "NetProfit": 0.04,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.04,
        "Sales": 200,
        "Exclusion_Reason": "DIFFERENT PRODUCT: Supplier 3-way vs Amazon 2-way socket",
        "Evidence": "Supplier '3WAY', Amazon '2 Way' = different specifications"
    },
    {
        "Row": 1081,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY",
        "AmazonTitle": "Price & Kensington Black 6 Cup Teapot",
        "Supplier_EAN": "5010853210520",
        "Amazon_EAN": "5010853110851",
        "ASIN": "B0013IUIPA",
        "SupplierPrice": 7.41,
        "NetProfit": 0.05,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.05,
        "Sales": 100,
        "Exclusion_Reason": "DIFFERENT PRODUCT: Supplier 2-cup Navy vs Amazon 6-cup Black",
        "Evidence": "Size (2 vs 6 cup) and color (navy vs black) both differ"
    },
    {
        "Row": 751,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE",
        "AmazonTitle": "Roundup Path Weedkiller, Ready to Use, Refill, 5 Litre",
        "Supplier_EAN": "5017676016919",
        "Amazon_EAN": "5017676016964",
        "ASIN": "B01MYBH3SU",
        "SupplierPrice": 4.56,
        "NetProfit": 3.52,
        "RSU": 1,
        "Manual_Adjusted_Profit": 3.52,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT SIZE: Supplier 1L vs Amazon 5L",
        "Evidence": "Supplier '1LTR', Amazon '5 Litre' = completely different sizes"
    },
    {
        "Row": 746,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE",
        "AmazonTitle": "Everbuild 103 Premium Trowel Mastic, Stone, 6 kg",
        "Supplier_EAN": "5029347009311",
        "Amazon_EAN": "-",
        "ASIN": "B0070U64RG",
        "SupplierPrice": 5.70,
        "NetProfit": 5.34,
        "RSU": 1,
        "Manual_Adjusted_Profit": 5.34,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT SIZE + PRODUCT: Supplier 1L Bitumen vs Amazon 6kg Premium",
        "Evidence": "Size (1L vs 6kg) and product line (Bitumen vs Premium) differ"
    },
    # FALSE MATCHES - DIFFERENT BRANDS
    {
        "Row": 437,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK",
        "AmazonTitle": "BGL Stainless Steel Standing Toilet Brush (Black)",
        "Supplier_EAN": "5056295703862",
        "Amazon_EAN": "-",
        "ASIN": "B07R41125W",
        "SupplierPrice": 2.28,
        "NetProfit": 7.40,
        "RSU": 1,
        "Manual_Adjusted_Profit": 7.40,
        "Sales": 100,
        "Exclusion_Reason": "DIFFERENT BRAND + MATERIAL: Blue Canyon Plastic vs BGL Stainless Steel",
        "Evidence": "Brand (Blue Canyon vs BGL) and material (plastic vs stainless steel) both differ"
    },
    {
        "Row": 138,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "PRIMA MULTI SHOWERHEAD CHROME",
        "AmazonTitle": "Lara Multi Spray Shower Head - Chrome",
        "Supplier_EAN": "5038673230474",
        "Amazon_EAN": "-",
        "ASIN": "B00569FG1S",
        "SupplierPrice": 4.56,
        "NetProfit": 10.37,
        "RSU": 1,
        "Manual_Adjusted_Profit": 10.37,
        "Sales": 100,
        "Exclusion_Reason": "DIFFERENT BRAND: Prima (Prima Housewares) vs Lara (Triton Showers)",
        "Evidence": "Web research: Prima and Lara are different manufacturers"
    },
    {
        "Row": 78,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "BRIGHT & HOMELY METAL WATERING CAN ROSE",
        "AmazonTitle": "Woodside Silver 9L Metal Garden Watering Can with Rose",
        "Supplier_EAN": "5050796010788",
        "Amazon_EAN": "5055864219438",
        "ASIN": "B07WMYF37Z",
        "SupplierPrice": 7.41,
        "NetProfit": 10.53,
        "RSU": 1,
        "Manual_Adjusted_Profit": 10.53,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT BRAND: Bright & Homely vs Woodside",
        "Evidence": "Different brands, EANs differ, capacity unspecified vs 9L"
    },
    {
        "Row": 925,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "PPS POCKET TISSUES 3PLY 10S PK10",
        "AmazonTitle": "Handy Pocket 3ply Tissues, Packs of 10",
        "Supplier_EAN": "5030481970238",
        "Amazon_EAN": "5028635004045",
        "ASIN": "B073H7GJ13",
        "SupplierPrice": 1.08,
        "NetProfit": 0.29,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.29,
        "Sales": 100,
        "Exclusion_Reason": "DIFFERENT BRAND: PPS vs Handy",
        "Evidence": "Different brands (PPS vs Handy), different EANs"
    },
    # Additional rapid assessments
    {
        "Row": 906,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "ULTRATAPE PICTURE FRAME TAPE 24MMX50M",
        "AmazonTitle": "Ultratape Picture Frame Tape 48mm x 33m",
        "Supplier_EAN": "5027785817369",
        "Amazon_EAN": "5027785811817",
        "ASIN": "B073VPL2VQ",
        "SupplierPrice": 2.05,
        "NetProfit": 0.43,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.43,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT SPECIFICATION: 24mm x 50m vs 48mm x 33m",
        "Evidence": "Different width (24mm vs 48mm) and length (50m vs 33m)"
    },
    {
        "Row": 978,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "AMTECH TROWEL MARGIN - SOFT GRIP 5X2",
        "AmazonTitle": "Amtech G0230 150mm (6\") Pointing trowel with soft grip",
        "Supplier_EAN": "5032759038138",
        "Amazon_EAN": "5032759027644",
        "ASIN": "B00ABJQTPU",
        "SupplierPrice": 2.05,
        "NetProfit": 0.35,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.35,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT PRODUCT: Margin trowel vs Pointing trowel",
        "Evidence": "Different trowel types (margin for corners vs pointing for filling)"
    },
    {
        "Row": 1028,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "ASHLEY CASH BOX 4.5 INCH",
        "AmazonTitle": "Ashley - Metal Cash Box - 20.5cm - Red",
        "Supplier_EAN": "5017403013167",
        "Amazon_EAN": "5017403013181",
        "ASIN": "B000OTPWNC",
        "SupplierPrice": 4.56,
        "NetProfit": 0.31,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.31,
        "Sales": 100,
        "Exclusion_Reason": "DIFFERENT SIZE: 4.5 inch (~11cm) vs 20.5cm",
        "Evidence": "Size mismatch: 4.5\" ≈ 11.4cm vs 20.5cm = different products"
    },
    {
        "Row": 1001,
        "Manual_Verdict": "FALSE_MATCH",
        "Confidence": 0,
        "SupplierTitle": "EVERBUILD JET RAPID SET CEMENT 3KG",
        "AmazonTitle": "Everbuild Jetcem Deep Rapid Repair Sand and Cement, Grey, 6 kg",
        "Supplier_EAN": "5010618043103",
        "Amazon_EAN": "-",
        "ASIN": "B001V9T690",
        "SupplierPrice": 4.56,
        "NetProfit": 0.57,
        "RSU": 1,
        "Manual_Adjusted_Profit": 0.57,
        "Sales": 50,
        "Exclusion_Reason": "DIFFERENT SIZE: 3kg vs 6kg",
        "Evidence": "Supplier '3KG', Amazon '6 kg' = different sizes"
    },
]

# Create DataFrame
df = pd.DataFrame(manual_verified_data)

# Save to CSV
output_csv = OUTPUT_DIR / f"manual_verification_results_{DATE_STAMP}.csv"
df.to_csv(output_csv, index=False)
print(f"Saved: {output_csv}")

# Create summary of CONFIRMED matches only
confirmed_df = df[df['Manual_Verdict'] == 'CONFIRMED_MATCH'].copy()
confirmed_csv = OUTPUT_DIR / f"confirmed_matches_{DATE_STAMP}.csv"
confirmed_df.to_csv(confirmed_csv, index=False)
print(f"Saved: {confirmed_csv}")

# Create summary of FALSE matches with reasons
false_df = df[df['Manual_Verdict'] == 'FALSE_MATCH'].copy()
false_csv = OUTPUT_DIR / f"false_matches_filtered_out_{DATE_STAMP}.csv"
false_df.to_csv(false_csv, index=False)
print(f"Saved: {false_csv}")

# Print summary
print("\n" + "=" * 80)
print("MANUAL VERIFICATION SUMMARY")
print("=" * 80)
print(f"Total products reviewed: {len(df)}")
print(f"CONFIRMED MATCHES: {len(df[df['Manual_Verdict'] == 'CONFIRMED_MATCH'])}")
print(f"NEEDS VERIFICATION: {len(df[df['Manual_Verdict'] == 'NEEDS_VERIFICATION'])}")
print(f"FALSE MATCHES: {len(df[df['Manual_Verdict'] == 'FALSE_MATCH'])}")

print("\n📊 FALSE MATCH BREAKDOWN:")
pack_mismatch = df[df['Exclusion_Reason'].str.contains('PACK MISMATCH', na=False)]
size_mismatch = df[df['Exclusion_Reason'].str.contains('SIZE', na=False) & ~df['Exclusion_Reason'].str.contains('PACK', na=False)]
brand_mismatch = df[df['Exclusion_Reason'].str.contains('BRAND', na=False)]
product_diff = df[df['Exclusion_Reason'].str.contains('DIFFERENT PRODUCT|DIFFERENT SPECIFICATION', na=False, regex=True)]

print(f"  Pack mismatches (unprofitable after RSU): {len(pack_mismatch)}")
print(f"  Size mismatches: {len(size_mismatch)}")
print(f"  Brand mismatches: {len(brand_mismatch)}")
print(f"  Different product types: {len(product_diff)}")

print("\n✅ CONFIRMED MATCHES:")
for _, row in confirmed_df.iterrows():
    print(f"  Row {row['Row']}: {row['SupplierTitle'][:50]}... | Profit: £{row['Manual_Adjusted_Profit']:.2f} | Sales: {row['Sales']}")

print("\n" + "=" * 80)
print("FILES GENERATED IN opu1 FOLDER:")
print("=" * 80)
print(f"1. {output_csv.name}")
print(f"2. {confirmed_csv.name}")
print(f"3. {false_csv.name}")
