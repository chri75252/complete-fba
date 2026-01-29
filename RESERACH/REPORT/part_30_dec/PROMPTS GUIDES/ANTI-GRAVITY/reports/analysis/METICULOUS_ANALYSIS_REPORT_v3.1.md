# METICULOUS FBA ANALYSIS REPORT (v3.1 - Fixed)

**Generated:** 2025-12-26 22:34:20

**Source Data:** PART3.xlsx (1411 rows)

**Fixes in v3.1:**
- Improved pack detection (excludes dimension measurements)
- KILROCK and similar brand matches properly identified
- More accurate adjusted profit calculations

---

## EXECUTIVE SUMMARY

| Category | Count | Description |
|:---|---:|:---|
| **VERIFIED (Exact EAN, 1:1 Pack)** | 18 | Perfect match |
| **VERIFIED (Exact EAN, Pack Mismatch, Profitable)** | 2 | Same product, different pack, still profitable |
| **HIGHLY LIKELY (User Verified)** | 8 | Strong non-EAN match |
| **HIGHLY LIKELY (Brand Match, Pack Diff)** | 6 | Same brand, pack adjustment needed |
| POSSIBLY HIGH LIKELIHOOD | 50 | Strong signals, needs verification |
| VERIFIED - Low Profit | 0 | EAN match but low/no profit |
| VERIFIED - Pack Issue | 4 | EAN match but pack makes unprofitable |
| NEEDS VERIFICATION | 1319 | Uncertain |
| FALSE POSITIVES | 4 | Obvious mismatches |
| **Total Actionable** | 34 | |

---

## 1. VERIFIED (Exact EAN, 1:1 Pack)

**18 products** with exact EAN match AND matching pack sizes.

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 626 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mulled W | 5059001500861 | 5059001500861 | B07WDRQ4J7 | £13.43 | £46.00 | £16.55 | 141.0% | 200 | 1:1 Match | £16.55 | Exact EAN match (5059001500861) |  |
| 370 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | 5050028016069 | 5050028016069 | B005XKFN0O | £2.99 | £18.99 | £8.00 | 263.2% | 50 | 1:1 Match | £8.00 | Exact EAN match (5050028016069) |  |
| 889 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl | 4 Litre Capacity | | 5010853235530 | 5010853235530 | B01IFIJ91Y | £7.66 | £24.99 | £5.11 | 73.8% | 200 | 1:1 Match | £5.11 | Exact EAN match (5010853235530) |  |
| 698 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | 5032759031078 | 5032759031078 | B003XKPUSQ | £1.72 | £7.99 | £2.35 | 118.6% | 200 | 1:1 Match | £2.35 | Exact EAN match (5032759031078) |  |
| 964 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids, Heavy | 5060357990107 | 5060357990107 | B0DJDH23JW | £3.66 | £12.97 | £2.13 | 59.1% | 700 | 1:1 Match | £2.13 | Exact EAN match (5060357990107) |  |
| 1249 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | 5010792542676 | 5010792542676 | B0FMS875KH | £9.20 | £16.99 | £1.40 | 17.1% | 50 | 1:1 Match | £1.40 | Exact EAN match (5010792542676) |  |
| 1236 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | 5010792542737 | 5010792542737 | B0FQK17X7F | £7.73 | £15.10 | £1.30 | 18.5% | 50 | 1:1 Match | £1.30 | Exact EAN match (5010792542737) |  |
| 1215 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Plaque - | 5010792749549 | 5010792749549 | B0DPQVJ4NW | £6.59 | £14.99 | £1.24 | 20.6% | 400 | 1:1 Match | £1.24 | Exact EAN match (5010792749549) |  |
| 1210 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml (Pack  | 5039295201040 | 5039295201040 | B0111N9Z1O | £3.89 | £10.43 | £0.79 | 20.9% | 50 | 1:1 Match | £0.79 | Exact EAN match (5039295201040) |  |
| 1157 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparent, 58 | 26102251102 | 26102251102 | B0042FBWQ0 | £2.56 | £8.99 | £0.76 | 28.4% | 50 | 1:1 Match | £0.76 | Exact EAN match (26102251102) |  |
| 1257 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient Applic | 5019200117338 | 5019200117338 | B008F7YP9C | £4.57 | £9.63 | £0.68 | 15.7% | 50 | 1:1 Match | £0.68 | Exact EAN match (5019200117338) |  |
| 1103 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker, Clear | 5026180033572 | 5026180033572 | B009SJXB32 | £0.94 | £6.58 | £0.46 | 34.8% | 50 | 1:1 Match | £0.46 | Exact EAN match (5026180033572) |  |
| 1277 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for streak fre | 5013159300353 | 5013159300353 | B00KB225MS | £1.84 | £6.64 | £0.29 | 14.1% | 200 | 1:1 Match | £0.29 | Exact EAN match (5013159300353) |  |
| 1331 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured from Re | 5013159004428 | 5013159004428 | B099X92QGG | £2.44 | £7.27 | £0.22 | 8.5% | 100 | 1:1 Match | £0.22 | Exact EAN match (5013159004428) |  |
| 1367 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray| Bathroom Accesso | 5060187175750 | 5060187175750 | B008F6946C | £4.30 | £9.85 | £0.20 | 4.8% | 500 | 1:1 Match | £0.20 | Exact EAN match (5060187175750) |  |
| 1383 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Roastin | 5010853203508 | 5010853203508 | B00W3RVAG6 | £3.66 | £9.11 | £0.10 | 2.8% | 50 | 1:1 Match | £0.10 | Exact EAN match (5010853203508) |  |
| 1398 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEONE SPE | Waterproof Robin Memorial Graveside Lantern with LED Candle  | 5055361761119 | 5055361761119 | B096KRFC4W | £6.95 | £13.99 | £0.08 | 1.2% | 50 | 1:1 Match | £0.08 | Exact EAN match (5055361761119) |  |
| 1405 | VERIFIED (Exact EAN, 1:1 Pack) | 95 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | 8711252100531 | 8711252100531 | B07JD22MJ2 | £2.35 | £8.29 | £0.02 | 0.7% | 200 | 1:1 Match | £0.02 | Exact EAN match (8711252100531) |  |

---

## 2. VERIFIED (Exact EAN, Pack Mismatch) — Profitable After Adjustment

**2 products** with exact EAN match but different pack sizes. *Adjusted Profit shown.*

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 931 | VERIFIED (Exact EAN, Pack Mismatch) | 85 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50),Bla | 5025364001970 | 5025364001970 | B06X9K7NR7 | £0.67 | £6.50 | £0.74 | 66.4% | 500 | Pack Mismatch (50→1) | £4.54 | Exact EAN match (5025364001970) | Supplier pack (50) exceeds Amazon (1) |
| 1395 | VERIFIED (Exact EAN, Pack Mismatch) | 85 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | 5022704000013 | 5022704000013 | B07YPPK4JY | £0.91 | £4.49 | £0.02 | 1.7% | 100 | Pack Mismatch (28→24) | £2.36 | Exact EAN match (5022704000013) | Supplier pack (28) exceeds Amazon (24) |

---

## 3. HIGHLY LIKELY (Non-EAN, User Verified)

**8 products** verified as strong matches.

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 1137 | HIGHLY LIKELY | 80 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, White | 5060386422662 | - | B01CMHNDKC | £6.84 | £14.95 | £1.93 | 30.9% | 50 | 1:1 Match | £1.93 | Similarity=0.64; Brand aligned | Verify variant before purchasing |
| 1156 | HIGHLY LIKELY | 80 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | 3426470301268 | - | B0DN1HXF9B | £3.70 | £9.99 | £1.04 | 28.5% | 50 | 1:1 Match | £1.04 | Similarity=0.64; Brand aligned | Verify variant before purchasing |
| 1209 | HIGHLY LIKELY | 80 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | 5012823030916 | - | B07NNY768K | £4.46 | £10.69 | £0.89 | 20.9% | 50 | 1:1 Match | £0.89 | Similarity=0.82; Brand aligned | Verify variant before purchasing |
| 1175 | HIGHLY LIKELY | 80 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 mm | 5029594522380 | 5029594522458 | B006A7D1O4 | £2.68 | £9.29 | £0.74 | 26.7% | 100 | 1:1 Match | £0.74 | Similarity=0.70; Brand aligned | Verify variant before purchasing |
| 1198 | HIGHLY LIKELY | 80 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | 5038135558504 | - | B08G1Q1L46 | £3.23 | £8.99 | £0.72 | 22.2% | 600 | 1:1 Match | £0.72 | Similarity=0.68; Brand aligned | Verify variant before purchasing |
| 1168 | HIGHLY LIKELY | 80 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS | Fairy Soap Dispensing Dish Brush | 5010303194424 | 5010303180588 | B0BYKDX25N | £1.20 | £6.57 | £0.42 | 27.4% | 50 | Pack Mismatch (3→1) | £4.20 | Similarity=0.72; Brand aligned | Verify variant before purchasing |
| 1357 | HIGHLY LIKELY | 80 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | 5056287402902 | - | B0815B7FBY | £2.22 | £6.98 | £0.13 | 5.6% | 50 | 1:1 Match | £0.13 | Similarity=0.71; Brand aligned | Verify variant before purchasing |
| 1384 | HIGHLY LIKELY | 80 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | 5010303194387 | 5010303180588 | B0BYKDX25N | £1.73 | £6.57 | £0.06 | 2.8% | 50 | 1:1 Match | £0.06 | Similarity=0.86; Brand aligned | Verify variant before purchasing |

---

## 4. HIGHLY LIKELY (Brand Match, Pack Difference)

**6 products** with same brand but different pack sizes. *Including KILROCK, BACOFOIL, SOUDAL, etc.*

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 522 | HIGHLY LIKELY (Brand Match, Pack Diff) | 75 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handheld Sp | 5411183131217 | - | B07STZLCM6 | £3.10 | £15.55 | £5.47 | 174.9% | 400 | Pack Mismatch (1→3) | £1.60 | Similarity=0.51; Same brand: SOUDAL | Amazon sells 3x, need 3 supplier units; Verify pack/variant |
| 458 | HIGHLY LIKELY (Brand Match, Pack Diff) | 75 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezing Sto | 5023139862917 | - | B08FBJ59DR | £1.03 | £9.96 | £2.93 | 207.8% | 500 | Pack Mismatch (12→3) | £6.71 | Similarity=0.55; Same brand: BACOFOIL | Supplier pack (12) exceeds Amazon (3); Verify pack/variant |
| 764 | HIGHLY LIKELY (Brand + Pack Diff) | 78 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION 500ML | Kilrock 3 X Blast Away Mould Spray 500ml | 5014353093294 | - | B0791ZQMMZ | £2.14 | £9.94 | £2.30 | 98.7% | 200 | Pack Mismatch (1→3) | £0.55 | Similarity=0.47; Same brand: KILROCK | Amazon sells 3x, need 3 supplier units; Verify pack/variant |
| 757 | HIGHLY LIKELY (Brand Match, Pack Diff) | 75 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezing Sto | 5023139861019 | - | B08FBJ59DR | £1.94 | £9.96 | £2.17 | 100.0% | 500 | Pack Mismatch (15→3) | £6.58 | Similarity=0.53; Same brand: BACOFOIL | Supplier pack (15) exceeds Amazon (3); Verify pack/variant |
| 947 | HIGHLY LIKELY (Brand Match, Pack Diff) | 75 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair (Extra | 5010232988019 | 9790504074621 | B08XWB7JW9 | £2.02 | £7.99 | £1.41 | 63.2% | 200 | Pack Mismatch (1→2) | £1.56 | Similarity=0.69; Same brand: MARIGOLD | Amazon sells 2x, need 2 supplier units; Verify pack/variant |
| 1227 | HIGHLY LIKELY (Brand Match, Pack Diff) | 75 | SECURPAK NYLON LOCKING NUT ZINC PLATED M12 PACK OF 6 | M12 Nyloc Hex Nut Locking Metal Steel Sheet Zinc Plated 12mm | 5019923004670 | 5060589914773 | B0B3X8VCQ5 | £0.79 | £4.49 | £0.23 | 19.1% | 50 | Pack Mismatch (6→10) | £1.82 | Similarity=0.56; Same brand: SECURPAK | Amazon sells 10x, need 10 supplier units; Verify pack/variant |

---

## 5. POSSIBLY HIGH LIKELIHOOD

**50 products** with strong brand/type match.

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 392 | POSSIBLY HIGH LIKELIHOOD | 70 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHER | Quest 36569 Espresso Coffee Machine With Milk Frother / 1.2L | 5025301365790 | - | B0B3F548G7 | £15.59 | £69.99 | £33.63 | 248.3% | 500 | 1:1 Match | £33.63 | Similarity=0.41; Brand: QUEST | Manual verification recommended |
| 582 | POSSIBLY HIGH LIKELIHOOD | 70 | MASTER COOK CASSEROLE NON-STICK 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm, 4 Lit | 742288758937 | 5057982093273 | B0BT51TC8X | £12.84 | £48.99 | £17.36 | 154.3% | 50 | 1:1 Match | £17.36 | Similarity=0.45; Brand: MASTER | Manual verification recommended |
| 938 | POSSIBLY HIGH LIKELIHOOD | 70 | MASTER COOK DIE CAST CASSEROLE 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm, 4 Lit | 6945702110326 | 5057982093273 | B0BT51TC8X | £20.16 | £48.99 | £11.25 | 64.9% | 50 | 1:1 Match | £11.25 | Similarity=0.50; Brand: MASTER | Manual verification recommended |
| 300 | POSSIBLY HIGH LIKELIHOOD | 70 | STEAM PUNK SKULL GOLD/BRONZE10CM ASSORTED | Nemesis Now Steampunk Clockwork Baron Skull Figurine Ornamen | 5037241304548 | 801269136529 | B083ZR2KMN | £3.16 | £23.70 | £9.88 | 310.7% | 50 | 1:1 Match | £9.88 | Similarity=0.47; Brand: STEAM | Manual verification recommended |
| 499 | POSSIBLY HIGH LIKELIHOOD | 70 | WOODEN INSECT HOUSE METAL ROOF | Garden Life Insect Hotel Wooden Bug House Natural Nest Shelt | 8720573129206 | - | B07FYQJXXC | £3.96 | £18.99 | £7.19 | 186.8% | 100 | 1:1 Match | £7.19 | Similarity=0.48; Brand: WOODEN | Manual verification recommended |
| 444 | POSSIBLY HIGH LIKELIHOOD | 70 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Set of  | 4001836065665 | 5023041541245 | B073XQYNQT | £3.35 | £19.99 | £7.18 | 214.9% | 200 | 1:1 Match | £7.18 | Similarity=0.53; Brand: SCHOTT ZWIESEL | Manual verification recommended |
| 709 | POSSIBLY HIGH LIKELIHOOD | 70 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Thermal T | 5060605732022 | 5019041167141 | B07F8VJHWF | £6.07 | £21.98 | £6.45 | 114.9% | 100 | 1:1 Match | £6.45 | Similarity=0.62; Brand: MENS | Manual verification recommended |
| 258 | POSSIBLY HIGH LIKELIHOOD | 70 | KINGAVON 6 LED TORCH | Kingavon BB-RT380 20-LED Rechargeable Emergency Sensor Light | 5017403046660 | - | B00BZ33FDU | £1.21 | £13.50 | £5.59 | 358.5% | 50 | 1:1 Match | £5.59 | Similarity=0.42; Brand: KINGAVON | Manual verification recommended |
| 937 | POSSIBLY HIGH LIKELIHOOD | 70 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | 5029347009311 | - | B0070U64RG | £9.20 | £22.54 | £5.34 | 64.9% | 50 | 1:1 Match | £5.34 | Similarity=0.67; Brand: EVERBUILD | Manual verification recommended |
| 788 | POSSIBLY HIGH LIKELIHOOD | 70 | STAINLESS STEEL KETTLE 14CM 1L | Swan SK31020N Brushed Stainless Steel Jug Kettle, Cordless D | 6974295210014 | 5055322509507 | B00KLGPNUK | £5.45 | £20.40 | £4.86 | 95.5% | 500 | 1:1 Match | £4.86 | Similarity=0.44; Brand: STAINLESS | Manual verification recommended |
| 751 | POSSIBLY HIGH LIKELIHOOD | 70 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCKER 1 LITRE(SOLD EACH | Kilrock SLAM - Sink and Plughole Bathroom Drain Unblocker -  | 5014353093539 | - | B099H4D9TH | £4.16 | £14.90 | £4.12 | 102.6% | 50 | 1:1 Match | £4.12 | Similarity=0.46; Brand: KILROCK | Manual verification recommended |
| 946 | POSSIBLY HIGH LIKELIHOOD | 70 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Pressure S | 5017676016919 | 5017676016964 | B01MYBH3SU | £6.02 | £21.12 | £3.52 | 63.2% | 50 | 1:1 Match | £3.52 | Similarity=0.55; Brand: ROUNDUP | Manual verification recommended |
| 410 | POSSIBLY HIGH LIKELIHOOD | 70 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish Bags 3 | 5025364005824 | 5025762919174 | B07MGLHMWY | £0.74 | £9.98 | £2.77 | 236.5% | 500 | 1:1 Match | £2.77 | Similarity=0.67; Brand: TIDYZ | Manual verification recommended |
| 589 | POSSIBLY HIGH LIKELIHOOD | 70 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Waste Pipe Unblocker | 5032759005833 | - | B01LYX9RRV | £1.39 | £9.49 | £2.60 | 152.2% | 200 | 1:1 Match | £2.60 | Similarity=0.42; Brand: AMTECH | Manual verification recommended |
| 660 | POSSIBLY HIGH LIKELIHOOD | 70 | LADIES KNITTED HAT WITH FAUX FUR POM-POM | Sibba Bobble Hat for Women Winter Beanie Hats Thermal Fleece | 5060605733807 | - | B0BHSR7XK1 | £1.60 | £8.99 | £2.47 | 131.5% | 50 | 1:1 Match | £2.47 | Similarity=0.49; Brand: LADIES | Manual verification recommended |
| 748 | POSSIBLY HIGH LIKELIHOOD | 70 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | ArtesÃ  Glass 18 cm Serving Bowl, Green | 8720573247917 | 5057982086312 | B0BF5DTF98 | £2.02 | £11.06 | £2.33 | 104.3% | 50 | 1:1 Match | £2.33 | Similarity=0.46; Brand: BOWL | Manual verification recommended |
| 1085 | POSSIBLY HIGH LIKELIHOOD | 70 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set (11- | 5010559684793 | 5010559684816 | B0114IPMS6 | £6.18 | £15.10 | £2.15 | 37.8% | 100 | 1:1 Match | £2.15 | Similarity=0.56; Brand: DRAPER | Manual verification recommended |
| 929 | POSSIBLY HIGH LIKELIHOOD | 70 | SUNNEX STAINLESS STEEL DESSERT SPOONS PK12 | Spoon Set, 12-Piece Stainless Steel Dessert Spoons Dining Sp | 4891342311062 | 616054388478 | B09NZMX5S2 | £2.51 | £9.99 | £1.76 | 66.9% | 400 | 1:1 Match | £1.76 | Similarity=0.42; Brand: SUNNEX | Manual verification recommended |
| 762 | POSSIBLY HIGH LIKELIHOOD | 70 | PPS PLASTIC GLASSES HALF PINT 50PCS | Plastic Half Pint Glasses 50 Pack Strong Disposable Beer Cup | 5030481970276 | - | B0C37Z88WM | £1.42 | £8.99 | £1.71 | 98.9% | 100 | 1:1 Match | £1.71 | Similarity=0.45; Brand: PPS | Manual verification recommended |
| 778 | POSSIBLY HIGH LIKELIHOOD | 70 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BPA Fre | 5015302109141 | 5015302106799 | B08CY3F21W | £0.94 | £6.99 | £1.29 | 97.4% | 50 | 1:1 Match | £1.29 | Similarity=0.54; Brand: FIRST STEPS | Manual verification recommended |
| 1025 | POSSIBLY HIGH LIKELIHOOD | 70 | MENS WATERPROOF TURN UP HAT ASSORTED | RockJock STORMACTIVE Mens Waterproof Windproof Classic Warm  | 5060605733418 | 5055928637062 | B08F5GHC9P | £2.27 | £7.99 | £1.16 | 47.5% | 50 | 1:1 Match | £1.16 | Similarity=0.42; Brand: MENS | Manual verification recommended |
| 1129 | POSSIBLY HIGH LIKELIHOOD | 70 | EXTRASTAR EXTENSION LEAD 6 GANG 1M WHITE | ExtraStar 6 Way Extension Leads with Surge Protection, Wall  | - | 791348432249 | B084Z492PW | £3.49 | £11.99 | £1.08 | 31.3% | 500 | 1:1 Match | £1.08 | Similarity=0.46; Brand: EXTRASTAR | Manual verification recommended |
| 1130 | POSSIBLY HIGH LIKELIHOOD | 70 | EXTRASTAR EXTENSION LEAD 6 GANG 1M BLACK | ExtraStar 6 Way Extension Leads with Surge Protection, Wall  | - | - | B08VMRHP2B | £3.49 | £11.99 | £1.08 | 31.3% | 200 | 1:1 Match | £1.08 | Similarity=0.46; Brand: EXTRASTAR | Manual verification recommended |
| 986 | POSSIBLY HIGH LIKELIHOOD | 70 | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Status 15 Metre TV Aerial Cable Extension Kit | White | Exte | 5022822163881 | 5022822202900 | B08N713Y2V | £1.61 | £7.95 | £1.05 | 55.8% | 200 | 1:1 Match | £1.05 | Similarity=0.44; Brand: STATUS | Manual verification recommended |
| 913 | POSSIBLY HIGH LIKELIHOOD | 70 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVERY | Giftmaker Collection Large Christmas Santa Sack Gift Stockin | 5012128616778 | - | B09HCS9QM2 | £1.14 | £6.99 | £1.04 | 69.4% | 100 | 1:1 Match | £1.04 | Similarity=0.60; Brand: GIFTMAKER | Manual verification recommended |
| 910 | POSSIBLY HIGH LIKELIHOOD | 70 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | 5032759001675 | - | B004TRT3K8 | £1.09 | £6.90 | £1.02 | 69.7% | 50 | 1:1 Match | £1.02 | Similarity=0.61; Brand: AMTECH | Manual verification recommended |
| 866 | POSSIBLY HIGH LIKELIHOOD | 70 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower Vase - In Loving Memo | 5050565833143 | 5017224926998 | B093HHQ7HB | £0.88 | £7.23 | £0.99 | 77.7% | 50 | 1:1 Match | £0.99 | Similarity=0.53; Brand: MEMORIAL | Manual verification recommended |
| 968 | POSSIBLY HIGH LIKELIHOOD | 70 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas Santa Sack Gift Stockin | 5012128616761 | - | B09HCS9QM2 | £1.27 | £6.99 | £0.93 | 57.8% | 100 | 1:1 Match | £0.93 | Similarity=0.44; Brand: GIFTMAKER | Manual verification recommended |
| 1165 | POSSIBLY HIGH LIKELIHOOD | 70 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | 5010853253428 | - | B07VC8TFB8 | £3.25 | £9.29 | £0.91 | 27.9% | 50 | 1:1 Match | £0.91 | Similarity=0.57; Brand: KILNER | Manual verification recommended |
| 905 | POSSIBLY HIGH LIKELIHOOD | 70 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 15L | Tidyz 3 Packs Of 40 White Plastic Disposable Pedal Bin Liner | 5025364024801 | 8800202181567 | B07F2JQ4B7 | £0.85 | £7.59 | £0.89 | 70.2% | 50 | 1:1 Match | £0.89 | Similarity=0.48; Brand: TIDYZ | Manual verification recommended |
| 1147 | POSSIBLY HIGH LIKELIHOOD | 70 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | 5029594103718 | 5029594112017 | B00JITHXRM | £2.89 | £8.09 | £0.86 | 29.1% | 300 | 1:1 Match | £0.86 | Similarity=0.53; Brand: ROLSON | Manual verification recommended |
| 1252 | POSSIBLY HIGH LIKELIHOOD | 70 | KILROCK SERVICE-PRO COFFEE MACHINE DESCALER 150ML(SOLD EACH) | Kilrock Service Pro Coffee Machine Descaler & Cleaner 2 x 15 | 5014353089266 | - | B008FNVJEU | £3.96 | £9.73 | £0.63 | 16.4% | 100 | 1:1 Match | £0.63 | Similarity=0.50; Brand: KILROCK | Manual verification recommended |
| 1167 | POSSIBLY HIGH LIKELIHOOD | 70 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | 5032759027644 | - | B00ABJQTPU | £2.06 | £7.49 | £0.63 | 27.6% | 50 | 1:1 Match | £0.63 | Similarity=0.74; Brand: AMTECH | Manual verification recommended |
| 1038 | POSSIBLY HIGH LIKELIHOOD | 70 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fragranc | 7612720201457 | 5015926091990 | B08DRRKWKQ | £0.94 | £4.98 | £0.61 | 45.9% | 50 | 1:1 Match | £0.61 | Similarity=0.54; Brand: LITTLE TREES | Manual verification recommended |
| 1290 | POSSIBLY HIGH LIKELIHOOD | 70 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Grey, 6  | 5010618043103 | - | B001V9T690 | £4.63 | £10.44 | £0.57 | 13.0% | 50 | 1:1 Match | £0.57 | Similarity=0.65; Brand: EVERBUILD | Manual verification recommended |
| 1251 | POSSIBLY HIGH LIKELIHOOD | 70 | INCENSE STICKS SANDLEWOOD PK6 | STAMFORD INC. 37107 Sandalwood Incense Sticks, 20 Sticks x 6 | 5028691371075 | - | B00533VVB6 | £3.35 | £8.90 | £0.55 | 16.6% | 300 | 1:1 Match | £0.55 | Similarity=0.40; Brand: INCENSE | Manual verification recommended |
| 1225 | POSSIBLY HIGH LIKELIHOOD | 70 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick up too | 5032759005864 | - | B00HMDJD38 | £2.72 | £7.19 | £0.54 | 19.2% | 100 | 1:1 Match | £0.54 | Similarity=0.64; Brand: AMTECH | Manual verification recommended |
| 1336 | POSSIBLY HIGH LIKELIHOOD | 70 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | 5038135559808 | - | B082Q34WLQ | £5.30 | £10.99 | £0.40 | 8.1% | 50 | 1:1 Match | £0.40 | Similarity=0.73; Brand: BAKER & SALT | Manual verification recommended |
| 1193 | POSSIBLY HIGH LIKELIHOOD | 70 | KILNER PRESERVE JAR 0.25LTR SCREW LID | Kilner Preserve Jar 0.25L (250ml) Round Glass Screw Top Lid  | 5010853173566 | - | B007MO0FIO | £1.44 | £7.12 | £0.40 | 23.0% | 50 | 1:1 Match | £0.40 | Similarity=0.49; Brand: KILNER | Manual verification recommended |
| 1248 | POSSIBLY HIGH LIKELIHOOD | 70 | ELF ARRIVAL ENVELOPE OUTFIT | Christmas Naughty Elf Arrival Clothes - Plush Snowman Outfit | 5050565795922 | - | B09J3T86D8 | £1.94 | £6.99 | £0.37 | 17.1% | 50 | 1:1 Match | £0.37 | Similarity=0.51; Brand: ELF | Manual verification recommended |
| 1255 | POSSIBLY HIGH LIKELIHOOD | 70 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | 5032759038138 | 5032759027644 | B00ABJQTPU | £2.00 | £7.49 | £0.35 | 15.8% | 50 | 1:1 Match | £0.35 | Similarity=0.56; Brand: AMTECH | Manual verification recommended |
| 1286 | POSSIBLY HIGH LIKELIHOOD | 70 | HEM INCENSE STICKS SANDLEWOOD | Incense Sandalwood, 120 Sticks in a Six Pack. HEM Brand, Han | 8901810016231 | - | B00KBZXPRE | £2.35 | £7.43 | £0.34 | 13.7% | 100 | 1:1 Match | £0.34 | Similarity=0.41; Brand: HEM | Manual verification recommended |
| 1327 | POSSIBLY HIGH LIKELIHOOD | 70 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | 5017403013167 | 5017403013181 | B000OTPWNC | £3.56 | £10.15 | £0.31 | 8.8% | 100 | 1:1 Match | £0.31 | Similarity=0.61; Brand: ASHLEY | Manual verification recommended |
| 1300 | POSSIBLY HIGH LIKELIHOOD | 70 | MEMORIAL PLASTIC SPIKE SPECIAL MUM & DAD | Mum And Dad - Plastic Spike Memorial Grave Vase With Butterf | 5055361711091 | 5056699407144 | B0D8QFWZ7N | £1.78 | £7.25 | £0.25 | 12.4% | 50 | 1:1 Match | £0.25 | Similarity=0.48; Brand: MEMORIAL | Manual verification recommended |
| 1347 | POSSIBLY HIGH LIKELIHOOD | 70 | EXTRASTAR EXTENSION LEAD 2 GANG 2M WHITE | EXTRASTAR 2 Gang Extension Lead, 2 Metre Extension Cable, Do | - | 5060999035297 | B0FG23ZTX7 | £3.59 | £9.49 | £0.25 | 7.0% | 50 | 1:1 Match | £0.25 | Similarity=0.50; Brand: EXTRASTAR | Manual verification recommended |
| 1388 | POSSIBLY HIGH LIKELIHOOD | 70 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance, 3 L | 3426470268684 | - | B01LCYXS24 | £10.55 | £16.89 | £0.21 | 2.3% | 100 | 1:1 Match | £0.21 | Similarity=0.60; Brand: PYREX | Manual verification recommended |
| 1361 | POSSIBLY HIGH LIKELIHOOD | 70 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild â€“ One Strike â€“ Multi-Purpose Quick-Drying Fill | 5029347300029 | - | B001326TJA | £2.76 | £8.75 | £0.15 | 5.3% | 500 | 1:1 Match | £0.15 | Similarity=0.41; Brand: EVERBUILD | Manual verification recommended |
| 1400 | POSSIBLY HIGH LIKELIHOOD | 70 | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM | STATUS 2 Way Socket | 2 USB Port Cable Free Socket | S2W2USB | 5022822194984 | 5022822207776 | B08CVK7746 | £3.49 | £9.00 | £0.04 | 1.2% | 200 | 1:1 Match | £0.04 | Similarity=0.51; Brand: STATUS | Manual verification recommended |
| 1404 | POSSIBLY HIGH LIKELIHOOD | 70 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | 5029594525374 | - | B000QFCQ6U | £2.68 | £7.36 | £0.02 | 0.8% | 50 | 1:1 Match | £0.02 | Similarity=0.61; Brand: ROLSON | Manual verification recommended |
| 1411 | POSSIBLY HIGH LIKELIHOOD | 70 | FLOW FLOOR & SURFACE CLEANER 5L EACH | Flow Lemon Floor & Surface All Purpose Cleaner | Concentrate | 5061029210899 | - | B0CQ4VX6Z5 | £4.69 | £9.70 | £0.00 | 0.0% | 50 | 1:1 Match | £0.00 | Similarity=0.42; Brand: FLOW | Manual verification recommended |

---

## FILTERED OUT: VERIFIED (Low/Negative Profit or Pack Issue)

**4 products** with exact EAN but not profitable after pack adjustment.

| RowID | Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Key Risks / Notes |
| ----: | :--- | ---: | :--- | :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | :--- | ---: | :--- | :--- |
| 363 | VERIFIED (Exact EAN) - Pack Issue | 75 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering Trays  | 5060357991357 | 5060357991357 | B0DT71SSPT | £1.08 | £14.97 | £3.90 | 269.3% | 50 | Pack Mismatch (1→10) | £-0.32 | Exact EAN match (5060357991357) | Amazon sells 10x, need 10 supplier units; Adj. Profit=£-0.32 |
| 1282 | VERIFIED (Exact EAN) - Pack Issue | 75 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White Colou | 5060187173633 | 5060187173633 | B007IGLUIK | £3.10 | £8.25 | £0.43 | 13.9% | 100 | Pack Mismatch (1→2) | £-0.42 | Exact EAN match (5060187173633) | Amazon sells 2x, need 2 supplier units; Adj. Profit=£-0.42 |
| 1173 | VERIFIED (Exact EAN) - Pack Issue | 75 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Disposable | 5030481940088 | 5030481940088 | B07YQ5HFFN | £0.67 | £4.28 | £0.30 | 26.7% | 700 | Pack Mismatch (1→40) | £-23.88 | Exact EAN match (5030481940088) | Amazon sells 40x, need 40 supplier units; Adj. Profit=£-23.88 |
| 1396 | VERIFIED (Exact EAN) - Pack Issue | 75 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 20 Reu | 5012904148738 | 5012904148738 | B00M36YPIM | £1.75 | £6.90 | £0.03 | 1.5% | 600 | Pack Mismatch (1→20) | £-30.21 | Exact EAN match (5012904148738) | Amazon sells 20x, need 20 supplier units; Adj. Profit=£-30.21 |

---

## FILTERED OUT: FALSE POSITIVES

**4 products** flagged as obvious mismatches.

| RowID | SupplierTitle | AmazonTitle | ASIN | Reason |
| ---: | :--- | :--- | :--- | :--- |
| 350 | SPONTEX HANDY TOUGH SCOURER | 6 Packs Case for 40mm Apple Watch SE 3rd Gen(2025) | B0DHY5WLM3 | Completely unrelated products |
| 861 | MARIGOLD OUTDOOR GLOVES LARGE | Aimtel 4 Pack Screen Protector Compatible with Sam | B0FDKKKWZ3 | Completely unrelated products |
| 1243 | CHAMOIS 2.25sq ft WASH LEATHER | 40mm Case for Apple Watch SE 3(2025)/SE 2/SE/Serie | B0D849PC16 | Completely unrelated products |
| 1386 | SPRAY GREASE 400ML | Aimtel 4 Pack Screen Protector Compatible with Sam | B0FDKKKWZ3 | Completely unrelated products |

---

## RECONCILIATION PROOF

| Category | Count |
|:---|---:|
| Total Input Rows | 1411 |
| VERIFIED (1:1 Pack) | 18 |
| VERIFIED (Pack Mismatch, Profitable) | 2 |
| VERIFIED (Low Profit) | 0 |
| VERIFIED (Pack Issue) | 4 |
| HIGHLY LIKELY (User Verified) | 8 |
| HIGHLY LIKELY (Brand, Pack Diff) | 6 |
| POSSIBLY HIGH LIKELIHOOD | 50 |
| NEEDS VERIFICATION | 1319 |
| FALSE POSITIVES | 4 |
| **TOTAL** | **1411** |
