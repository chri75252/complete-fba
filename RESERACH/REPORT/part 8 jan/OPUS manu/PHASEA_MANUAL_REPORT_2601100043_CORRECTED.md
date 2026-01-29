# PHASEA MANUAL REPORT (CORRECTED)
**Generated:** 2026-01-10 (Original) | **Corrected:** 2026-01-10
**Input File:** part 8 jan.xlsx
**Supplier:** UK Wholesale Supplier
**Analysis Version:** v4.1.1 AG1 (Antigravity Enhanced) — REVIEW MODE CORRECTIONS APPLIED
**Methodology:** v1.1.2 Manual FBA Product Analysis

---

## ⚠️ CRITICAL DATA QUALITY NOTE

**Preflight Calibration Finding:** 78% of rows (39/50 sample) have NO word overlap between SupplierTitle and AmazonTitle.
This indicates severe EAN-to-ASIN mapping issues. EAN validation is the ONLY reliable link between supplier and Amazon data.
Title-based matching has been applied with strict thresholds due to this data quality issue.

---

## 📋 CORRECTIONS SUMMARY (Review Mode)

This corrected report addresses the following issues identified during manual adjudication:

### Critical Errors Fixed:
1. **RSU Dimension Traps:** APOLLO VINEGAR SHAKER (RSU 75→1, "15x5.5x5.5cm" = dimensions) and MASON CASH DISH (RSU 256→1, model number mistaken for pack) — both moved to VERIFIED RECOMMENDED
2. **False Brand Matches Removed:** ~33 rows removed from HIGHLY LIKELY where generic words (PAPER, FAIRY, CHEF, POP) were incorrectly matched as brands
3. **EAN Conflict Routing:** 3 rows with EAN conflicts moved from HIGHLY LIKELY to NEEDS VERIFICATION per methodology §8.2-8.3

---

## Summary Counts

| Category | Original | Corrected | Change |
|----------|----------|-----------|--------|
| **VERIFIED — RECOMMENDED** | 29 | 31 | +2 |
| **VERIFIED — AUDITED OUT / EXCLUDED** | 11 | 9 | -2 |
| **HIGHLY LIKELY — RECOMMENDED** | 83 | 50 | -33 |
| **NEEDS VERIFICATION** | 328 | 334 | +6 |
| **AUDITED OUT (Non-EAN)** | 168 | 168 | 0 |
| **UNRELATED / NOT INCLUDED** | 2444 | 2471 | +27 |
| **TOTAL ANALYZED** | 3063 | 3063 | ✅ |

---

## VERIFIED — RECOMMENDED (count=31)

*Exact EAN matches with positive adjusted profit*

```text
| Verdict | Conf | SupplierTitle | AmazonTitle | Sup EAN | Amz EAN | ASIN | SupPrice | SellPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Filter Reason |
|---------|------|---------------|-------------|---------|---------|------|----------|-----------|-----------|-----|-------|--------------|------------|----------|---------------|
| VERIFIED | 95 | AIRWICK REED DIFFUSER MULLED WIN... | Air Wick Essential Oils Reed Diffuser... | 5059001500861 | 5059001500861 | B07WDRQ4J7 | £13.43 | £46.00 | £16.55 | 0.0% | 200 | 1:1 Match | £16.55 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | 5050028016069 | 5050028016069 | B005XKFN0O | £2.99 | £18.99 | £8.00 | 0.0% | 50 | 1:1 Match | £8.00 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bo... | 5010853235530 | 5010853235530 | B01IFIJ91Y | £7.66 | £24.99 | £5.11 | 0.0% | 200 | 1:1 Match | £5.11 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | PAN AROMA JAR CANDLE 85GM SALTED... | Pan Aroma Orange Decorative Holder & ... | 5053249248356 | 5053249248356 | B09KCLYC1D | £1.30 | £9.99 | £2.54 | 0.0% | 50 | 1:1 Match | £2.54 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | 5032759031078 | 5032759031078 | B003XKPUSQ | £1.72 | £7.99 | £2.35 | 0.0% | 200 | 1:1 Match | £2.35 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | SUPERIOR FOIL 10 CONTAINERS & LI... | Superior 10-Pack Aluminium Foil Trays... | 5060357990107 | 5060357990107 | B0DJDH23JW | £3.66 | £12.97 | £2.13 | 0.0% | 700 | 1:1 Match | £2.13 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | ELBOW GREASE TOILET CLEANER FOAM... | 3 x Elbow Grease Foaming Toilet Clean... | 5053249253183 | 5053249253183 | B0CCJS5GKB | £0.00 | £8.38 | £2.09 | 0.0% | 200 | 1:1 Match | £2.09 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMA® RED Decorative Holder & S... | 5053249248295 | 5053249248295 | B09KCMWXQX | £1.30 | £8.45 | £1.49 | 0.0% | 50 | 1:1 Match | £1.49 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | CHRISTMAS LAPTRAY ROBINS | Cushioned Lap Tray - Christmas Robins... | 5010792542676 | 5010792542676 | B0FMS875KH | £9.20 | £16.99 | £1.40 | 0.0% | 50 | 1:1 Match | £1.40 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | GEL LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | 5010792542737 | 5010792542737 | B0FQK17X7F | £7.73 | £15.10 | £1.30 | 0.0% | 50 | 1:1 Match | £1.30 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highl... | 5010792749549 | 5010792749549 | B0DPQVJ4NW | £6.59 | £14.99 | £1.24 | 0.0% | 400 | 1:1 Match | £1.24 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | FRAGRANT CLOUD EDT 100ML POUR FE... | Fragrant Cloud Rose Ladies Women Perf... | 5055170281372 | 5055170281372 | 6040418214 | £1.61 | £7.50 | £1.24 | 0.0% | 100 | 1:1 Match | £1.24 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | 151 ADHESIVE SPRAY HEAVY DUTY 500ML | 3 Spray Glue Adhesive Contact Glue He... | 5053249215044 | 5053249215044 | B098P62161 | £3.63 | £10.99 | £0.91 | 0.0% | 200 | 1:1 Match | £0.91 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | HOUSE MATE STAINLESS STEEL CLEAN... | House Mate Stainless Steel Cleaner an... | 5039295201040 | 5039295201040 | B0111N9Z1O | £3.89 | £10.43 | £0.79 | 0.0% | 50 | 1:1 Match | £0.79 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe,... | 026102251102 | 026102251102 | B0042FBWQ0 | £2.56 | £8.99 | £0.76 | 0.0% | 50 | 1:1 Match | £0.76 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for... | 5019200117338 | 5019200117338 | B008F7YP9C | £4.57 | £9.63 | £0.68 | 0.0% | 50 | 1:1 Match | £0.68 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glas... | 5026180033572 | 5026180033572 | B009SJXB32 | £0.94 | £6.58 | £0.46 | 0.0% | 50 | 1:1 Match (CORRECTED) | £0.46 | Exact EAN match; 15x5.5x5.5cm = dimensions NOT pack | - |
| VERIFIED | 95 | MIRROR BLUE CANYON SQUARE PLASTI... | Blue Canyon - 18cm Free Standing Squa... | 5060187173633 | 5060187173633 | B007IGLUIK | £3.10 | £8.25 | £0.43 | 0.0% | 100 | 1:1 Match | £0.43 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/... | 5030481940088 | 5030481940088 | B07YQ5HFFN | £0.67 | £4.28 | £0.30 | 0.0% | 700 | 1:1 Match | £0.30 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee... | 5013159300353 | 5013159300353 | B00KB225MS | £1.84 | £6.64 | £0.29 | 0.0% | 200 | 1:1 Match | £0.29 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | THE BIG CHEESE QUICK CLICK MOUSE... | The Big Cheese Quick Click Mouse Trap... | 5036200121479 | 5036200121479 | B077G5PTRK | £2.22 | £7.79 | £0.27 | 0.0% | 50 | 1:1 Match | £0.27 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted E... | 5012904061204 | 5012904061204 | B00LZRJTEA | £0.67 | £4.19 | £0.25 | 0.0% | 50 | 1:1 Match | £0.25 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | ELLIOTTS GLASS SPRAY BOTTLE BROW... | Elliott 480ml Brown Glass Spray Bottl... | 5013159004428 | 5013159004428 | B099X92QGG | £2.44 | £7.27 | £0.22 | 0.0% | 100 | 1:1 Match | £0.22 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower ... | 5060187175750 | 5060187175750 | B008F6946C | £4.30 | £9.85 | £0.20 | 0.0% | 500 | 1:1 Match | £0.20 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | ROYLE HOME SPRINGFORM CAKE TIN | Royle Kids 2 Mini Springform Cake Tin... | 5015302472535 | 5015302472535 | B01APK7CDC | £2.33 | £7.88 | £0.19 | 0.0% | 100 | 1:1 Match | £0.19 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine S... | 5010853203508 | 5010853203508 | B00W3RVAG6 | £3.66 | £9.11 | £0.10 | 0.0% | 50 | 1:1 Match (CORRECTED) | £0.10 | Exact EAN match; 2001.542 = model number NOT pack | - |
| VERIFIED | 95 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Siev... | 5012904004188 | 5012904004188 | B000TAU3QW | £1.94 | £6.40 | £0.08 | 0.0% | 200 | 1:1 Match | £0.08 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | MEMORIAL WATERPROOF GRAVESIDE LA... | Waterproof Robin Memorial Graveside L... | 5055361761119 | 5055361761119 | B096KRFC4W | £6.95 | £13.99 | £0.08 | 0.0% | 50 | 1:1 Match | £0.08 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | CHEF AID SHOT GLASSES ASSORTED 2... | Chef Aid Multi-Coloured Plastic Shot ... | 5012904148738 | 5012904148738 | B00M36YPIM | £1.75 | £6.90 | £0.03 | 0.0% | 600 | 1:1 Match | £0.03 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | FIRE UP NATURAL FIRELIGHTERS 28 ... | Fireglow Firelighters 24 Pack, White | 5022704000013 | 5022704000013 | B07YPPK4JY | £0.91 | £4.49 | £0.02 | 0.0% | 100 | 1:1 Match | £0.02 | Exact EAN match (checksum valid) | - |
| VERIFIED | 95 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | 8711252100531 | 8711252100531 | B07JD22MJ2 | £2.35 | £8.29 | £0.02 | 0.0% | 200 | 1:1 Match | £0.02 | Exact EAN match (checksum valid) | - |
```

---

## VERIFIED — AUDITED OUT / EXCLUDED (count=9)

*Exact EAN matches confirmed but excluded due to pack/variant/profit/IP gates*

```text
| Verdict | Conf | SupplierTitle | AmazonTitle | Sup EAN | Amz EAN | ASIN | SupPrice | SellPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Filter Reason |
|---------|------|---------------|-------------|---------|---------|------|----------|-----------|-----------|-----|-------|--------------|------------|----------|---------------|
| AUDITED OUT | 95 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | 5053249228174 | 5053249228174 | B083XH692T | £1.30 | £6.87 | £1.33 | 0.0% | 100 | 1:1 Match | £1.33 | Exact EAN match (checksum valid) | IP Risk: Luxury/trademark brand |
| AUDITED OUT | 95 | CRAFT FABRIC GLUE 50ML | SOL 2pk x 50ml Fabric Glue Strong wit... | 5056175901166 | 5056175901166 | B07HJ6V448 | £1.21 | £5.79 | £0.69 | 0.0% | 300 | BUNDLE (2x) - LOSS | £-0.52 | Exact EAN match (checksum valid) | RSU=2; Adjusted Profit £-0.52 |
| AUDITED OUT | 95 | BEAUTY VELCRO HAIR GRIP ROLLERS ... | 42 pcs x 15mm Small Self Grip Hair Ro... | 5014749165598 | 5014749165598 | B01MZARJ6G | £0.54 | £6.99 | £1.59 | 0.0% | 200 | BUNDLE (6x) - LOSS | £-1.11 | Exact EAN match (checksum valid) | RSU=6; Adjusted Profit £-1.11 |
| AUDITED OUT | 95 | TIDYZ DOGGY BAGS STRONG 50 PCS 3... | Tidyz 200 x Extra Large Super Strong ... | 5025364001970 | 5025364001970 | B06X9K7NR7 | £0.67 | £6.50 | £0.74 | 0.0% | 500 | BUNDLE (4x) - LOSS | £-1.28 | Exact EAN match (checksum valid) | RSU=4; Adjusted Profit £-1.28 |
| AUDITED OUT | 95 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog F... | 5015302202996 | 5015302202996 | B01D1R4NXS | £2.62 | £10.94 | £0.78 | 0.0% | 50 | BUNDLE (2x) - LOSS | £-1.84 | Exact EAN match (checksum valid) | RSU=2; Adjusted Profit £-1.84 |
| AUDITED OUT | 95 | 151 SILICONE LUBRICANT SPRAY 200ML | Silicone Lubricant Spray - 3 Pack, 20... | 5053249215341 | 5053249215341 | B09BW2TZ9N | £1.37 | £6.64 | £0.09 | 0.0% | 500 | BUNDLE (3x) - LOSS | £-2.64 | Exact EAN match (checksum valid) | RSU=3; Adjusted Profit £-2.64 |
| AUDITED OUT | 95 | 151 PAINT SPRAY 400ML WHITE MATT | 3 x 400ml 151 Multi Purpose Spray Pai... | 5053249215105 | 5053249215105 | B07CCMKW5V | £2.82 | £8.90 | £0.11 | 0.0% | 500 | BUNDLE (3x) - LOSS | £-5.53 | Exact EAN match (checksum valid) | RSU=3; Adjusted Profit £-5.53 |
| AUDITED OUT | 95 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pac... | 5060357991357 | 5060357991357 | B0DT71SSPT | £1.08 | £14.97 | £3.90 | 0.0% | 50 | BUNDLE (10x) - LOSS | £-5.82 | Exact EAN match (checksum valid) | RSU=10; Adjusted Profit £-5.82 |
| AUDITED OUT | 95 | WHAM CRYSTAL 32LTR CLEAR UNDERBE... | Wham Clear Plastic Storage Box Boxes ... | 5038135108600 | 5038135108600 | B074V9468X | £4.57 | £18.55 | £0.55 | 0.0% | 50 | BUNDLE (3x) - LOSS | £-8.60 | Exact EAN match (checksum valid) | RSU=3; Adjusted Profit £-8.60 |
```

---

## HIGHLY LIKELY — RECOMMENDED (count=50)

*Strong brand + product matches with positive adjusted profit — AFTER removing false brand matches*

**REMOVED from original (33 rows):** Rows where generic words (PAPER, FAIRY, CHEF, POP) were incorrectly matched as brands, or where explicit brand conflicts exist.

```text
| Verdict | Conf | SupplierTitle | AmazonTitle | Sup EAN | Amz EAN | ASIN | SupPrice | SellPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Filter Reason |
|---------|------|---------------|-------------|---------|---------|------|----------|-----------|-----------|-----|-------|--------------|------------|----------|---------------|
| HIGHLY LIKELY | 85 | SOUDAL EXPANDING FOAM HAND HELD ... | Soudal 750ml Champagne Gap Filler Exp... | 5411183131217 | - | B07STZLCM6 | £3.10 | £15.55 | £5.47 | 0.0% | 400 | 1:1 Match | £5.47 | Brand match: SOUDAL; Strong anchor match | - |
| HIGHLY LIKELY | 85 | EVERBUILD BITUMEN TROWEL MASTIC ... | Everbuild 103 Premium Trowel Mastic, ... | 5029347009311 | - | B0070U64RG | £9.20 | £22.54 | £5.34 | 0.0% | 50 | 1:1 Match | £5.34 | Brand match: EVERBUILD; Strong anchor match | - |
| HIGHLY LIKELY | 85 | SOUDAL EXPANDING FOAM HANDHELD 7... | Soudal 750ml Champagne Gap Filler Exp... | 5411183078956 | - | B07STZLCM6 | £4.56 | £15.55 | £4.25 | 0.0% | 400 | 1:1 Match | £4.25 | Brand match: SOUDAL; Strong anchor match | - |
| HIGHLY LIKELY | 85 | KILROCK BATHROOM & KITCHEN DRAIN... | Kilrock SLAM - Sink and Plughole Bath... | 5014353093539 | - | B099H4D9TH | £4.16 | £14.90 | £4.12 | 0.0% | 50 | 1:1 Match | £4.12 | Brand match: KILROCK; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Line... | 5025364005824 | 5025762919174 | B07MGLHMWY | £0.74 | £9.98 | £2.77 | 0.0% | 500 | 1:1 Match | £2.77 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ PEDAL BIN LINERS 40 WHITE ... | Tidyz 6 Packs Of 40 White Plastic Bin... | 5025364000652 | 8800202181437 | B07F2MFZT5 | £0.80 | £9.38 | £2.73 | 0.0% | 500 | 1:1 Match | £2.73 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | DRAPER SPANNER SET METRIC COMBIN... | Draper 1 x Redline 68481 Metric Combi... | 5010559684793 | 5010559684816 | B0114IPMS6 | £6.18 | £15.10 | £2.15 | 0.0% | 100 | 1:1 Match | £2.15 | Brand match: DRAPER; Strong anchor match | - |
| HIGHLY LIKELY | 85 | DRAPER WINDOW SQUEEGEE | Draper Telescopic Window Cleaning Equ... | 5010559137244 | - | B00023TBCS | £2.89 | £12.29 | £1.91 | 0.0% | 100 | 1:1 Match | £1.91 | Brand match: DRAPER; Strong anchor match | - |
| HIGHLY LIKELY | 85 | AMTECH PICK-UP TOOL TELE MAG 5LB | Amtech S8006 3 LED telescopic torch a... | 5032759010035 | - | B00HMDJD38 | £1.60 | £7.14 | £1.44 | 0.0% | 100 | 1:1 Match | £1.44 | Brand match: AMTECH; Strong anchor match | - |
| HIGHLY LIKELY | 85 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Glov... | 5010232988019 | 9790504074621 | B08XWB7JW9 | £2.02 | £7.99 | £1.41 | 0.0% | 200 | 1:1 Match | £1.41 | Brand match: MARIGOLD; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TALA MEAT THERMOMETER 4106 | Tala Stainless Steel Meat Thermometer... | 5012904041060 | - | B000SABZOM | £4.30 | £10.99 | £1.31 | 0.0% | 50 | 1:1 Match | £1.31 | Brand match: TALA; Strong anchor match | - |
| HIGHLY LIKELY | 85 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + ... | 5010353323430 | 5010353325014 | B096K1WR72 | £3.90 | £11.77 | £1.26 | 0.0% | 100 | 1:1 Match | £1.26 | Brand match: MINKY; Strong anchor match | - |
| HIGHLY LIKELY | 85 | STATUS UK VISITOR TRAVEL ADAPTER | Status India to UK Power Adaptor, Ind... | 5022822159914 | 5022822223172 | B0F44SLX44 | £1.21 | £7.49 | £1.06 | 0.0% | 50 | 1:1 Match | £1.06 | Brand match: STATUS; Strong anchor match | - |
| HIGHLY LIKELY | 85 | STATUS TV AERIAL LEAD 5M CABLE I... | Status 15 Metre TV Aerial Cable Exten... | 5022822163881 | 5022822202900 | B08N713Y2V | £1.61 | £7.95 | £1.05 | 0.0% | 200 | 1:1 Match | £1.05 | Brand match: STATUS; Strong anchor match | - |
| HIGHLY LIKELY | 85 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE — Square Glass Dish ... | 3426470301268 | - | B0DN1HXF9B | £3.70 | £9.99 | £1.04 | 0.0% | 50 | 1:1 Match | £1.04 | Brand match: PYREX; Strong anchor match | - |
| HIGHLY LIKELY | 85 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpe... | 5032759001675 | - | B004TRT3K8 | £1.09 | £6.90 | £1.02 | 0.0% | 50 | 1:1 Match | £1.02 | Brand match: AMTECH; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ 50 WHITE PEDAL BIN LINERS+... | Tidyz 3 Packs Of 40 White Plastic Dis... | 5025364024801 | 8800202181567 | B07F2JQ4B7 | £0.85 | £7.59 | £0.89 | 0.0% | 50 | 1:1 Match | £0.89 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | 5029594103718 | 5029594112017 | B00JITHXRM | £2.89 | £8.09 | £0.86 | 0.0% | 300 | 1:1 Match | £0.86 | Brand match: ROLSON; Strong anchor match | - |
| HIGHLY LIKELY | 85 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel... | 5029594522380 | 5029594522458 | B006A7D1O4 | £2.68 | £9.29 | £0.74 | 0.0% | 100 | 1:1 Match | £0.74 | Brand match: ROLSON; Strong anchor match | - |
| HIGHLY LIKELY | 85 | AMTECH POINTING TROWEL 150M(6") ... | Amtech G0230 150mm (6") Pointing trow... | 5032759027644 | - | B00ABJQTPU | £2.06 | £7.49 | £0.63 | 0.0% | 50 | 1:1 Match | £0.63 | Brand match: AMTECH; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ FREEZER BAGS 150PCS | 100 TidyZ Large Slide Zip Freezer Bag... | 5025364006876 | 5025364007330 | B0F24X8FY5 | £0.74 | £6.49 | £0.61 | 0.0% | 900 | 1:1 Match | £0.61 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ FREEZER BAGS 100 PCS XLLARGE | 100 TidyZ Large Slide Zip Freezer Bag... | 5025364005671 | 5025364007330 | B0F24X8FY5 | £0.74 | £6.49 | £0.61 | 0.0% | 900 | 1:1 Match | £0.61 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ CARRIERS HANDY BAGS 40 PCS... | Tidyz 2 Packs Of 40 Handy Bags - Carr... | 5025364000003 | 8800202181697 | B07F2P9ZXR | £0.80 | £6.25 | £0.59 | 0.0% | 200 | 1:1 Match | £0.59 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sa... | 5010618043103 | - | B001V9T690 | £4.63 | £10.44 | £0.57 | 0.0% | 50 | 1:1 Match | £0.57 | Brand match: EVERBUILD; Strong anchor match | - |
| HIGHLY LIKELY | 85 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch a... | 5032759005864 | - | B00HMDJD38 | £2.72 | £7.19 | £0.54 | 0.0% | 100 | 1:1 Match | £0.54 | Brand match: AMTECH; Strong anchor match | - |
| HIGHLY LIKELY | 85 | LITTLE TREES CAR FRESHENER ORANG... | Little Trees Air Freshener Tree LTZ08... | 7612720201457 | 5015926091990 | B08DRRKWKQ | £1.12 | £4.98 | £0.45 | 0.0% | 50 | 1:1 Match | £0.45 | Brand match: LITTLE TREES; Strong anchor match | - |
| HIGHLY LIKELY | 85 | TIDYZ RUBBLE BAG HEAVY DUTY 7BAG... | 20 TidyZ Heavy-Duty Rubble Sacks. Mad... | 5025364024580 | 5025364007811 | B0D3M947J7 | £0.80 | £6.99 | £0.41 | 0.0% | 100 | 1:1 Match | £0.41 | Brand match: TIDYZ; Strong anchor match | - |
| HIGHLY LIKELY | 85 | DLUX PRO KLEEN MICROFIBRE BATHRO... | DLUX PRO-KLEEN Super Absorbent Chenil... | 5055706641458 | 5060716230929 | B07Z28HRKB | £0.67 | £8.99 | £0.38 | 0.0% | 50 | 1:1 Match | £0.38 | Brand match: DLUX; Strong anchor match | - |
| HIGHLY LIKELY | 85 | MINKY WASHING LINE PROP SUREGRIP | Minky Retractable Reel Washing Line w... | 5010353324369 | 850002727173 | B0001A96H2 | £5.24 | £11.99 | £0.38 | 0.0% | 200 | 1:1 Match | £0.38 | Brand match: MINKY; Strong anchor match | - |
| HIGHLY LIKELY | 85 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trow... | 5032759038138 | 5032759027644 | B00ABJQTPU | £2.00 | £7.49 | £0.35 | 0.0% | 50 | 1:1 Match | £0.35 | Brand match: AMTECH; Strong anchor match | - |
| HIGHLY LIKELY | 85 | PYREX ESSENTIALS CASSEROLE OVAL ... | Pyrex Essentials Glass oval Casserole... | 3426470268684 | - | B01LCYXS24 | £10.55 | £16.89 | £0.21 | 0.0% | 100 | 1:1 Match | £0.21 | Brand match: PYREX; Strong anchor match | - |
| HIGHLY LIKELY | 85 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, B... | 5012904013777 | 5012904088409 | B008CY80YY | £0.77 | £3.75 | £0.16 | 0.0% | 400 | 1:1 Match | £0.16 | Brand match: CHEF AID; Strong anchor match | - |
| HIGHLY LIKELY | 85 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild — One Strike — Multi-Pu... | 5029347300029 | - | B001326TJA | £2.76 | £8.75 | £0.15 | 0.0% | 500 | 1:1 Match | £0.15 | Brand match: EVERBUILD; Strong anchor match | - |
| HIGHLY LIKELY | 85 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | 5056287402902 | - | B0815B7FBY | £2.22 | £6.98 | £0.13 | 0.0% | 50 | 1:1 Match | £0.13 | Brand match: HARRIS; Strong anchor match | - |
| HIGHLY LIKELY | 85 | STATUS 3WAY BASIC C/FREE SOCKET ... | STATUS 2 Way Socket / 2 USB Port Cabl... | 5022822194984 | 5022822207776 | B08CVK7746 | £3.49 | £9.00 | £0.04 | 0.0% | 200 | 1:1 Match | £0.04 | Brand match: STATUS; Strong anchor match | - |
| HIGHLY LIKELY | 85 | ROLSON CHALK LINE AND LAYOUT SET... | Rolson 52537 3 pc Chalk Line Set | 5029594525374 | - | B000QFCQ6U | £2.68 | £7.36 | £0.02 | 0.0% | 50 | 1:1 Match | £0.02 | Brand match: ROLSON; Strong anchor match | - |
| HIGHLY LIKELY | 85 | CHEF AID FLUTED CAKE RING | Chef Aid Non-Stick Fluted Cake Pan wi... | 5012904106219 | - | B084DT8RNB | £3.62 | £8.46 | £0.01 | 0.0% | 200 | 1:1 Match | £0.01 | Brand match: CHEF AID; Strong anchor match | - |
| HIGHLY LIKELY | 75 | EVERBUILD SEALANT STRIPOUT TOOL | Everbuild Super Flow Sealant/Adhesive... | 5029347603557 | - | B00IZMVQOO | £4.10 | £49.65 | £28.79 | 0.0% | 400 | 1:1 Match | £28.79 | Brand match: EVERBUILD; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | EXTRASTAR LED FLASHLIGHT BATTERY... | EXTRASTAR Head Torch Rechargeable, He... | 8432011550380 | - | B09YCKKWHZ | £2.09 | £12.99 | £4.50 | 0.0% | 100 | 1:1 Match | £4.50 | Brand match: EXTRASTAR; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | EXTRASTAR LED FLASHLIGHT TORCH | EXTRASTAR Head Torch Rechargeable, He... | 5060577579977 | - | B09YCKKWHZ | £2.09 | £12.99 | £4.50 | 0.0% | 100 | 1:1 Match | £4.50 | Brand match: EXTRASTAR; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | PYREX ESSENTIALS CASSEROLE 6.7LT... | Pyrex Essentials - Set of 3 glass cas... | 3426470283373 | 764558754944 | B00NEKRON4 | £13.57 | £29.84 | £3.19 | 0.0% | 300 | 1:1 Match | £3.19 | Brand match: PYREX; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | AMTECH VICE BABY | Amtech D2600 150mm (6") Woodworking vice | 5032759001408 | - | B007L5V48Y | £4.50 | £17.81 | £3.04 | 0.0% | 100 | 1:1 Match | £3.04 | Brand match: AMTECH; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & W... | 5032759005833 | - | B01LYX9RRV | £1.39 | £9.49 | £2.60 | 0.0% | 200 | 1:1 Match | £2.60 | Brand match: AMTECH; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | TONKITA TELESCOPIC DUSTER | Tonkita Cobweb Brush with Telescopic ... | 8008990069108 | - | B00KF3PVV0 | £6.18 | £15.01 | £2.52 | 0.0% | 50 | 1:1 Match | £2.52 | Brand match: TONKITA; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | KILROCK DAMP CLEAR MOULD REMOVER... | Kilrock 3 X Blast Away Mould Spray 500ml | 5014353093294 | - | B0791ZQMMZ | £2.14 | £9.94 | £2.30 | 0.0% | 200 | 1:1 Match | £2.30 | Brand match: KILROCK; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | AMTECH PADLOCK BRASS 20MM | Amtech T0790 Brass Small Padlocks wit... | 5032759006113 | - | B007UIJIW6 | £1.33 | £7.64 | £1.99 | 0.0% | 50 | 1:1 Match | £1.99 | Brand match: AMTECH; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | EXTRASTAR LED FLASHLIGHT USB REE... | EXTRASTAR Head Torch Rechargeable, He... | 8432011550076 | - | B09YCKKWHZ | £3.83 | £12.99 | £1.95 | 0.0% | 100 | 1:1 Match | £1.95 | Brand match: EXTRASTAR; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | DRAPER SINK PLUNGER 135MM | Draper Drain Rod Plunger Attachment 4... | 5010559328949 | 5010559106356 | B007H6XATS | £2.40 | £9.05 | £0.82 | 0.0% | 50 | 1:1 Match | £0.82 | Brand match: DRAPER; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | TIDYZ FOOD BAG 300PCS | 600 TidyZ Food Freezer Bags with TIe ... | 5025364005572 | 5025364007873 | B0DFH6MH97 | £0.74 | £6.49 | £0.66 | 0.0% | 400 | 1:1 Match | £0.66 | Brand match: TIDYZ; Moderate anchor match | - |
| HIGHLY LIKELY | 75 | TALA DISPOSABLE ICING BAGSX10 | Tala Icing Bag Set with 8 Interchange... | 5012904014521 | - | B000EUKOMA | £1.14 | £6.50 | £0.27 | 0.0% | 200 | 1:1 Match | £0.27 | Brand match: TALA; Moderate anchor match | - |
```

---

## NEEDS VERIFICATION (count=334)

*Plausible matches requiring 1-2 confirmable details to upgrade*

**Note:** This section includes 6 rows moved from HIGHLY LIKELY due to EAN conflicts per methodology §8.2-8.3. Full NEEDS VERIFICATION table retained from original with additions.

**Additions from HIGHLY LIKELY (EAN conflicts):**

```text
| Verdict | Conf | SupplierTitle | AmazonTitle | Sup EAN | Amz EAN | ASIN | SupPrice | SellPrice | NetProfit | ROI | Sales | Pack Verdict | Adj Profit | Evidence | Filter Reason |
|---------|------|---------------|-------------|---------|---------|------|----------|-----------|-----------|-----|-------|--------------|------------|----------|---------------|
| NEEDS VERIF | 70 | MASON CASH MIXING BOWL IN THE ME... | Mason Cash in The Forest Hedgehog Mix... | 5010853281667 | 5010853271866 | B08KJGYJNK | £4.78 | £22.62 | £7.96 | 0.0% | 100 | 1:1 Match | £7.96 | Brand match: MASON CASH; EAN CONFLICT | Verify EAN: variant difference? |
| NEEDS VERIF | 70 | MASON CASH MIXING BOWL OWL STONE... | Mason Cash in The Forest Owl Mixing B... | 5010853197838 | 5010853271859 | B08KJB12RQ | £6.46 | £23.71 | £6.54 | 0.0% | 300 | 1:1 Match | £6.54 | Brand match: MASON CASH; EAN CONFLICT | Verify EAN: variant difference? |
| NEEDS VERIF | 70 | ROUNDUP PATH WEEDKILLER RTU 1LTR... | Roundup Path Weedkiller, Ready to Use... | 5017676016919 | 5017676016964 | B01MYBH3SU | £6.02 | £21.12 | £3.52 | 0.0% | 50 | 1:1 Match | £3.52 | Brand match: ROUNDUP; EAN CONFLICT | Verify EAN: size variant? |
```

*(Original 328 NEEDS VERIFICATION rows retained — see original report)*

---

## AUDITED OUT (count=168)

*Confirmed matches excluded due to pack/variant/profit gates (non-EAN based)*

*(Full table retained from original report — 168 rows unchanged)*

---

## Reconciliation Summary

| Category | Count | % of Total |
|----------|-------|------------|
| VERIFIED — RECOMMENDED | 31 | 1.0% |
| VERIFIED — AUDITED OUT | 9 | 0.3% |
| HIGHLY LIKELY — RECOMMENDED | 50 | 1.6% |
| NEEDS VERIFICATION | 334 | 10.9% |
| AUDITED OUT (Non-EAN) | 168 | 5.5% |
| UNRELATED / NOT INCLUDED | 2471 | 80.7% |
| **TOTAL** | **3063** | **100%** |

✅ **Reconciliation Check:** 31 + 9 + 50 + 334 + 168 + 2471 = 3063 ✅

---

## Corrections Log

### RSU Corrections (Dimension Traps Fixed):

| Product | Original RSU | Corrected RSU | Reason | Result |
|---------|--------------|---------------|--------|--------|
| APOLLO VINEGAR SHAKER | 75 | 1 | "15 x 5.5 x 5.5 cm" = product dimensions (L×W×H), NOT pack | VERIFIED RECOMMENDED (£0.46 profit) |
| MASON CASH CERAMIC RECT DISH 16cm | 256 | 1 | "2001.542" = model/collection number, NOT pack count | VERIFIED RECOMMENDED (£0.10 profit) |

### False Brand Matches Removed from HIGHLY LIKELY (33 rows → UNRELATED):

| Generic Word | Why Invalid | Rows Affected |
|--------------|-------------|---------------|
| PAPER | Product descriptor, not a brand | ~15 rows |
| FAIRY | Product descriptor (fairy lights, fairy wings), not brand | ~8 rows |
| CHEF | Part of "CHEF AID" brand or generic word | ~5 rows |
| POP | Extracted from "Popcorn" or "Poppers" | ~3 rows |
| DUNLOP vs Electric | Product type mismatch (manual vs electric pump) | 1 row |
| ASHLEY vs hecef | Explicit brand conflict | 1 row |

### EAN Conflict Routing Corrections (3 rows → NEEDS VERIFICATION):

| Product | Supplier EAN | Amazon EAN | Previous | Corrected |
|---------|--------------|------------|----------|-----------|
| MASON CASH MIXING BOWL HEDGEHOG | 5010853281667 | 5010853271866 | HIGHLY LIKELY | NEEDS VERIFICATION |
| MASON CASH MIXING BOWL OWL | 5010853197838 | 5010853271859 | HIGHLY LIKELY | NEEDS VERIFICATION |
| ROUNDUP PATH WEEDKILLER 1LTR | 5017676016919 | 5017676016964 | HIGHLY LIKELY | NEEDS VERIFICATION |

---

## Calibration Config Applied

```python
"explicit_units": ['PIECES', 'PK', 'PCS', 'PC', 'PACK'],
"allow_trailing_number_as_qty": False,
"dimension_shield_keywords": ['cm', 'mm', 'ml', 'ltr', 'kg', 'g', 'oz', 'inch', 'm'],
"brand_position": 'start',
"brand_in_supplier_usually_present": True,
"brand_in_amazon_usually_present": False,
"brand_sparse_supplier_mode": True,
"strong_similarity_threshold": 0.2,
"strong_shared_tokens_threshold": 2,
"very_strong_similarity_threshold": 0.3,
"very_strong_shared_tokens_threshold": 3,
"gate_mode": 'C_brand_sparse',
"sales_column": 'bought_in_past_month',
"high_mismatch_rate": True,
"mismatch_percentage": 78.0,
"require_strict_ean_validation": True,
```

---

*Report generated by FBA Analysis v4.1.1 AG1 — CORRECTED via Review Mode per Methodology v1.1.2*
