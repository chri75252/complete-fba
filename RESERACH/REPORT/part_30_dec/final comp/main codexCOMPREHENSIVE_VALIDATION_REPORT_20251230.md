# FBA REPORT VALIDATION ANALYSIS

**Generated:** 2025-12-30
**Source Dataset:** part_30_dec.xlsx (2102 rows)
**Reports Analyzed:** 8 folders

## Executive Summary

- **Total products analyzed:** 1247
- **Correctly categorized:** 624 (50.0%)
- **Acceptably categorized:** 302
- **Incorrectly categorized:** 321

## Methodology

- Load source dataset `part_30_dec.xlsx` as ground truth (titles, EANs, ASIN, NetProfit, ROI, Sales).
- Parse each AI report markdown and extract every table row under VERIFIED / HIGHLY LIKELY / NEEDS VERIFICATION / FILTERED OUT sections.
- Independently reclassify each row using EAN equality (when present), brand matching, title similarity, pack/quantity sanity via adjusted profit, and variant mismatch checks.
- Compare AI category vs independent category and score as CORRECT / ACCEPTABLE (adjacent) / INCORRECT.

## Detailed Product Analysis (By AI Claimed Category)

Each row below is one product entry from one model folder.

### VERIFIED (claimed, n=209)

| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |
|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | Codex very high | VERIFIED | FILTERED OUT | INCORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 552 | TYRE WAX & SHINE SPRAY 500ML | 2 x Tutti Bambini Compatible Organic Crib Sheets â€“ Th | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=16%; NP=9.31; ROI=269.0%; Sales=100; Insufficient evidence |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | Opus | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | cli | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=8.00; ROI=263.2%; Sales=50; Exact EAN match |
| 563 | BROOKSTONE AIR FRESH TINS | Sopito Aluminum Tin Cans, 24pcs 60ml/2oz Metal Round Ti | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=10%; NP=5.27; ROI=262.3%; Sales=100; Pack 24x makes profit negative |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Opus | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | cli | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=61%; NP=2.73; ROI=187.9%; Sales=50; Exact EAN match |
| 751 | STATUS LED ROUND SES PA PEARL W/WHT 1PK BOX | 100Pcs CD DVD Sleeves, Standard Plastic Double-Sided Cl | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=23%; NP=2.73; ROI=187.9%; Sales=50; Pack 100x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | cli | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | Opus | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | cli | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=84%; NP=2.35; ROI=118.6%; Sales=200; Exact EAN match |
| 1041 | AMTECH ANVIL SECATEURS | Spear & Jackson 6758GS Razorsharp Geared Anvil Secateur | Codex samecha | VERIFIED | NEEDS VERIFICATION | INCORRECT | Sim=46%; NP=4.43; ROI=118.1%; Sales=300; Moderate similarity |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | Opus | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | cli | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scented Candle, RED | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=57%; NP=1.67; ROI=115.3%; Sales=50; Exact EAN match |
| 1057 | DEKTON CHISEL WOOD SET 3PC | Libraton Wood Chisel Set - 4PCs Professional Carpenter  | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=8.95; ROI=115.3%; Sales=100; Pack 4x makes profit negative |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | Opus | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | cli | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1131 | ASHLEY OVER THE DOOR HANGER 6 HOOK | Over Door Hanger, 6 Hooks Over The Door Hooks, Bearing  | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=2.00; ROI=104.4%; Sales=300; Insufficient evidence |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | Opus | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | cli | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  4 Litre Capac | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=5.11; ROI=73.8%; Sales=200; Exact EAN match |
| 1333 | PRIMA DESSERT FORK 6PCS | 6 Pcs Dessert Forks, 13.8cm Stainless Steel Fruit Forks | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=1.00; ROI=73.7%; Sales=100; Insufficient evidence |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | Opus | VERIFIED | VERIFIED | CORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | cli | VERIFIED | VERIFIED | CORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Opus | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | cli | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=31%; NP=2.13; ROI=59.1%; Sales=700; Exact EAN match |
| 1458 | FESTIVE MAGIC LED B/O TIMER 200  LIGHTS W/WHT | Sloth Night Light, Cute Squishy Lamp for Bedroom, Silic | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=3.63; ROI=59.1%; Sales=100; Insufficient evidence |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | cli | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1656 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Codex samecha | VERIFIED | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=1.48; ROI=34.8%; Sales=700; Partial match |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | Codex very high | VERIFIED | FILTERED OUT | INCORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | Codex samecha | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | Opus | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | cli | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparen | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=30%; NP=0.76; ROI=28.4%; Sales=50; Exact EAN match |
| 1733 | Tie-Out Cable for Dogs | Dog Tie Out Cable with 360Â° Swivel Lockable Hook and P | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=18%; NP=0.77; ROI=28.3%; Sales=50; Insufficient evidence |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | Opus | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | opus2 | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | webapp gpt | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1759 | PPS ROUND 150  DOYLEYS 11.5CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | Opus | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | cli | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1800 | PPS FOIL CONTAINER & LID DEEP NO.9 235x235x58MM 10 PIEC | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=0.68; ROI=22.6%; Sales=400; Insufficient evidence |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | Opus | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | cli | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1823 | ONYA DINNER SET 16 PIECES 4 MUGS 4 BOWLS 4 DINNER PLATE | ORIENTOOLS Leaf Blower and Vacuum-3000w Garden Corded L | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=1%; NP=3.10; ROI=20.9%; Sales=100; Insufficient evidence |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | Opus | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | cli | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Pla | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=25%; NP=1.24; ROI=20.6%; Sales=400; Exact EAN match |
| 1830 | SOZALI SQUARE FOOD BOX 700ML 2PC | Sistema Ultra Airtight Pantry Storage Container  700 m | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=0.35; ROI=20.3%; Sales=100; Insufficient evidence |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | Opus | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | cli | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=42%; NP=1.30; ROI=18.5%; Sales=50; Exact EAN match |
| 1859 | SECURPAK CUP  HOOK WHITE 38MM | Plastic Coated Shouldered Mug Cup Hooks, 38 mm (1.1/2 i | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=37%; NP=0.22; ROI=18.3%; Sales=50; Pack 20x makes profit negative |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | Opus | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | cli | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=46%; NP=1.40; ROI=17.1%; Sales=50; Exact EAN match |
| 1874 | DEKTON COPING SAW | Eclipse Professional Tools 70-CP1R Coping Saw, Blue | Codex samecha | VERIFIED | NEEDS VERIFICATION | INCORRECT | Sim=41%; NP=0.66; ROI=17.0%; Sales=300; Moderate similarity |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | Codex very high | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | Opus | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | cli | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fast, Efficient A | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=27%; NP=0.68; ROI=15.7%; Sales=50; Exact EAN match |
| 1884 | GLAMOUR CONNECTION DETANGLES HAIR BRUSH/MIRR | Hair Detangling Brush with Bending Bristles, Unique Spi | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=0.22; ROI=15.7%; Sales=100; Insufficient evidence |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | Opus | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | cli | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1911 | PRO USER CLUB HAMMER | OX Club Hammer - Sledgehammer with Fibreglass Handle -  | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=0.78; ROI=14.1%; Sales=500; Insufficient evidence |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | Codex HIGH | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | Opus | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | opus2 | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | webapp gpt | VERIFIED | FILTERED OUT | INCORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | Codex samecha | VERIFIED | HIGHLY LIKELY | ACCEPTABLE | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1935 | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550ML | Addis Clip Tight Food Storage Container Large 4.2 Litre | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=0.24; ROI=12.6%; Sales=300; Weak match |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | Opus | VERIFIED | FILTERED OUT | INCORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | opus2 | VERIFIED | FILTERED OUT | INCORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | webapp gpt | VERIFIED | FILTERED OUT | INCORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1953 | RUSTINS SCRATCH COVER-DARK 125ML | Rustins Scratch Cover Dark â€“ Conceal Surface Scratche | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=0.31; ROI=11.3%; Sales=100; Insufficient evidence |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | Codex HIGH | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | Opus | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | opus2 | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | webapp gpt | VERIFIED | FILTERED OUT | INCORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1991 | CANDLE JAR BOHO 9X19CM | Glass Candle Cylinder Holders â€“ Set of 3 Pillar Candl | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=14%; NP=0.49; ROI=8.4%; Sales=50; Pack 3x makes profit negative |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | Codex HIGH | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | Opus | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | opus2 | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | webapp gpt | VERIFIED | FILTERED OUT | INCORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2041 | APOLLO UTENSIL STAINLESS STEEL MASHER | Stainless Steel Potato Masher, Berglander Heavy Duty Me | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=0.11; ROI=4.7%; Sales=100; Insufficient evidence |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | Opus | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | cli | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2059 | MEMORIAL PLASTIC SPIKE SPECIAL DAD | David Fischhoff Special Dad Verse Graveside Memorial Gr | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=0.08; ROI=3.7%; Sales=100; Insufficient evidence |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | cli | VERIFIED | VERIFIED | CORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | Codex samecha | VERIFIED | HIGHLY LIKELY | ACCEPTABLE | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | Opus | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | Gemini | VERIFIED | FILTERED OUT | INCORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | cli | VERIFIED | FILTERED OUT | INCORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2083 | WHAM MEASURING JUG 2LTR | Wham Cuisine 2L Clear Measuring Jug,JNS_453403 | Codex samecha | VERIFIED | NEEDS VERIFICATION | INCORRECT | Sim=52%; NP=0.02; ROI=1.5%; Sales=100; Moderate similarity |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | Opus | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | cli | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2087 | DOORMAT PVC COIR HELLO 60X40CM | Nicola Spring Coir Door Mat - 60 x 40cm - Hello - Pack  | Codex samecha | VERIFIED | OTHER / LOW PRIORITY | INCORRECT | Sim=7%; NP=0.05; ROI=1.2%; Sales=100; Insufficient evidence |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | Codex HIGH | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | Gemini | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | Opus | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | cli | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | opus2 | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | webapp gpt | VERIFIED | VERIFIED | CORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2095 | HAND BRUSH VARNISH RED | Xtremeauto 5pc Paint Brush Set â€“ Synthetic Bristle Br | Codex samecha | VERIFIED | FILTERED OUT | INCORRECT | Sim=4%; NP=0.01; ROI=0.7%; Sales=50; Pack 5x makes profit negative |

### HIGHLY LIKELY (claimed, n=341)

| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |
|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|
| 162 | EVERBUILD SEALANT STRIPOUT TOOL | Everbuild Super Flow Sealant/Adhesive Cartridge Applica | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=35%; NP=28.79; ROI=725.2%; Sales=400; Partial match |
| 162 | EVERBUILD SEALANT STRIPOUT TOOL | Everbuild Super Flow Sealant/Adhesive Cartridge Applica | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=35%; NP=28.79; ROI=725.2%; Sales=400; Partial match |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 225 | BOWL GLASS FLOWER 15CM 4 ASSORTED COLOURS | YOUEON 4 Pack Small Glass Bubble Bowl Vases, 15 cm Glas | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=9.39; ROI=565.8%; Sales=50; Insufficient evidence |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 253 | DEKTON CABLE TIES BLACK 100PCS 4.8MMX300MM | XINGO Black Cable Ties Pack of 1000, 300mm x 4.8mm, Pre | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=11.39; ROI=525.1%; Sales=50; Insufficient evidence |
| 281 | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | Superior 20-Pack 16oz Microwave Containers With Lids â€ | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=27%; NP=5.30; ROI=477.6%; Sales=100; Partial match |
| 292 | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ | Superior 32oz Food Containers With Lids â€“ 20-Pack Dur | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=26%; NP=5.64; ROI=462.7%; Sales=100; Partial match |
| 302 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | Hobby Gift Sewing Box, Wood/Fabric, Embroidered Bee, Me | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=48%; NP=9.98; ROI=449.8%; Sales=400; Moderate similarity |
| 302 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | Hobby Gift Sewing Box, Wood/Fabric, Embroidered Bee, Me | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=48%; NP=9.98; ROI=449.8%; Sales=400; Moderate similarity |
| 396 | KINGAVON 6 LED TORCH | Kingavon BB-RT380 20-LED Rechargeable Emergency Sensor  | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=5.59; ROI=358.5%; Sales=50; Moderate similarity |
| 396 | KINGAVON 6 LED TORCH | Kingavon BB-RT380 20-LED Rechargeable Emergency Sensor  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=5.59; ROI=358.5%; Sales=50; Moderate similarity |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 514 | DEKTON HOBBY KIT 7PC | Aussel Gundam Model Tools Kit, Model Basic Tools Craft  | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=20%; NP=4.76; ROI=284.9%; Sales=100; Pack 26x makes profit negative |
| 593 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHE | Quest 36569 Espresso Coffee Machine With Milk Frother / | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=33.63; ROI=248.3%; Sales=500; Partial match |
| 593 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHE | Quest 36569 Espresso Coffee Machine With Milk Frother / | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=33.63; ROI=248.3%; Sales=500; Partial match |
| 607 | THE CHRISTMAS WORKSHOP 40 FAIRY LIGHTS  CLEAR | 40M 800 LED Fairy Lights Outdoor Christmas Lights Plug  | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=19%; NP=9.31; ROI=241.9%; Sales=200; Partial match |
| 607 | THE CHRISTMAS WORKSHOP 40 FAIRY LIGHTS  CLEAR | 40M 800 LED Fairy Lights Outdoor Christmas Lights Plug  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=19%; NP=9.31; ROI=241.9%; Sales=200; Partial match |
| 613 | WHAM CRYSTAL 60LTR SMOKE BOX & LID | Wham Crystal 5 x 60L Stackable Plastic Storage Boxes wi | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=13.81; ROI=238.1%; Sales=50; Weak match |
| 613 | WHAM CRYSTAL 60LTR SMOKE BOX & LID | Wham Crystal 5 x 60L Stackable Plastic Storage Boxes wi | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=13.81; ROI=238.1%; Sales=50; Weak match |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 715 | COTTON BUDS IN JAR 12X6CM 50 PCS | Cotton Bud Holder 10 Oz Bathroom Jars with Lids for Cot | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=2.63; ROI=197.6%; Sales=400; Weak match |
| 718 | EXTRASTAR LED FLASHLIGHT BATTERY TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=28%; NP=4.50; ROI=196.6%; Sales=100; Partial match |
| 719 | EXTRASTAR LED FLASHLIGHT TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=27%; NP=4.50; ROI=196.6%; Sales=100; Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 748 | PAN AROMA CANDLE 85G PURE JASMINE | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=38%; NP=2.73; ROI=187.9%; Sales=50; Weak match |
| 749 | PAN AROMA CANDLE 85G LEMONGRASS | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=39%; NP=2.73; ROI=187.9%; Sales=50; Weak match |
| 757 | PAN AROMA JAR CANDLE 85GM APPLE CINNAMON | Luxury Scented Candle â€“ Warm Apple & Cinnamon - 18 Oz | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=2.70; ROI=186.1%; Sales=500; Weak match |
| 778 | DEKTON HIGH POWER TYPE C RECHARGEABLE FLASHLIGHT | WUBEN E7 1800 Lumen Torch Light with Magnet - Super Bri | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=36%; NP=9.77; ROI=178.3%; Sales=200; Weak match |
| 785 | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM | Mason Cash in The Forest Hedgehog Mixing Bowl 1.1 Litre | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=33%; NP=7.96; ROI=175.7%; Sales=100; Partial match |
| 785 | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM | Mason Cash in The Forest Hedgehog Mixing Bowl 1.1 Litre | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=33%; NP=7.96; ROI=175.7%; Sales=100; Partial match |
| 786 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=51%; NP=5.47; ROI=174.9%; Sales=400; Partial match |
| 786 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=51%; NP=5.47; ROI=174.9%; Sales=400; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | cli | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 795 | CANDLE POTS WITH CRYSTALS PK3 | Crystal Scented Candles Gift Set for Women, Meditation  | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=11%; NP=5.81; ROI=173.5%; Sales=400; Insufficient evidence |
| 812 | BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK | BGL Stainless Steel Standing Toilet Brush for Bath Deco | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=56%; NP=7.40; ROI=170.1%; Sales=100; Partial match |
| 844 | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=28%; NP=5.00; ROI=162.7%; Sales=200; Partial match |
| 856 | PAN AROMA CANDLE 85G LIME GINGER | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=38%; NP=2.56; ROI=159.3%; Sales=50; Weak match |
| 867 | PPS FOIL ROAST DISH OVAL 46CM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=31%; NP=1.71; ROI=154.5%; Sales=50; Weak match |
| 878 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Waste Pipe Unblocke | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=2.60; ROI=152.2%; Sales=200; Partial match |
| 878 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Waste Pipe Unblocke | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=2.60; ROI=152.2%; Sales=200; Partial match |
| 883 | CURVER RATTAN ROUND LARGE ORGANISER GREY | CURVER Style Rattan Effect Kitchen, Living room, Bathro | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=2.71; ROI=150.6%; Sales=50; Moderate similarity |
| 883 | CURVER RATTAN ROUND LARGE ORGANISER GREY | CURVER Style Rattan Effect Kitchen, Living room, Bathro | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=2.71; ROI=150.6%; Sales=50; Moderate similarity |
| 919 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET 5L | Extra Select Premium Rabbit Mix Bucket 5L - Balanced Co | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=43%; NP=4.86; ROI=145.0%; Sales=300; Moderate similarity |
| 919 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET 5L | Extra Select Premium Rabbit Mix Bucket 5L - Balanced Co | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=43%; NP=4.86; ROI=145.0%; Sales=300; Moderate similarity |
| 919 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET 5L | Extra Select Premium Rabbit Mix Bucket 5L - Balanced Co | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=43%; NP=4.86; ROI=145.0%; Sales=300; Moderate similarity |
| 977 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=29%; NP=3.28; ROI=133.8%; Sales=700; Partial match |
| 1036 | AMTECH PADLOCK BRASS 20MM | Amtech T0790 Brass Small Padlocks with Keys for Luggage | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=32%; NP=1.99; ROI=119.7%; Sales=50; Partial match |
| 1047 | PREMIER FLICKABRIGHT TEALIGHT CANDLE 7.3X3.5CM | Premier Decorations Red LED Flickabrights Wax Candle Ba | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=40%; NP=2.35; ROI=116.7%; Sales=50; Weak match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1052 | BAUBLE 15CM SILVER | LOLStar Christmas Window Lights, 3 Pack Multicoloured S | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=7%; NP=3.17; ROI=116.0%; Sales=700; Pack 3x makes profit negative |
| 1060 | WHAM CRYSTAL 32LTR SMOKE BOX & LID | Wham Crystal 5 x 32L Stackable Plastic Storage Boxes wi | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=5.02; ROI=115.1%; Sales=100; Weak match |
| 1060 | WHAM CRYSTAL 32LTR SMOKE BOX & LID | Wham Crystal 5 x 32L Stackable Plastic Storage Boxes wi | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=5.02; ROI=115.1%; Sales=100; Weak match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1062 | GRIMALDI LA BELLA OPEN WOK 28CM | Jobin Wok Non Stick with Lid, 28cm Aluminium Wok Frying | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=12%; NP=9.11; ROI=114.9%; Sales=200; Insufficient evidence |
| 1085 | MASON CASH MIXING BOWL OWL STONE 26CM | Mason Cash in The Forest Owl Mixing Bowl 4 Litre  26cm | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=34%; NP=6.54; ROI=110.3%; Sales=300; Partial match |
| 1085 | MASON CASH MIXING BOWL OWL STONE 26CM | Mason Cash in The Forest Owl Mixing Bowl 4 Litre  26cm | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=34%; NP=6.54; ROI=110.3%; Sales=300; Partial match |
| 1088 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=29%; NP=3.00; ROI=109.8%; Sales=700; Partial match |
| 1095 | PRIMA HEART SHAPED BAKE PAN 23CM | Prima Set Of 2 Heart Shaped Cake Tins, Romantic Grey He | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=33%; NP=1.94; ROI=108.8%; Sales=100; Weak match |
| 1109 | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=32%; NP=4.16; ROI=106.3%; Sales=200; Partial match |
| 1122 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | Tidyz 2 X 10 Wheelie Bin Extra Large Liners 300L Black  | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=30%; NP=1.23; ROI=104.7%; Sales=700; Partial match |
| 1122 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | Tidyz 2 X 10 Wheelie Bin Extra Large Liners 300L Black  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=30%; NP=1.23; ROI=104.7%; Sales=700; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | cli | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex samecha | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex samecha | HIGHLY LIKELY | VERIFIED | ACCEPTABLE | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1136 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCKER 1 LITRE(SOLD | Kilrock SLAM - Sink and Plughole Bathroom Drain Unblock | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=4.12; ROI=102.6%; Sales=50; Partial match |
| 1136 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCKER 1 LITRE(SOLD | Kilrock SLAM - Sink and Plughole Bathroom Drain Unblock | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=4.12; ROI=102.6%; Sales=50; Partial match |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Gemini | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=53%; NP=2.17; ROI=100.0%; Sales=500; Pack 3x makes profit negative |
| 1156 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION  | Kilrock 3 X Blast Away Mould Spray 500ml | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=47%; NP=2.30; ROI=98.7%; Sales=200; Partial match |
| 1156 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION  | Kilrock 3 X Blast Away Mould Spray 500ml | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=47%; NP=2.30; ROI=98.7%; Sales=200; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1166 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=52%; NP=4.25; ROI=97.8%; Sales=400; Partial match |
| 1166 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=52%; NP=4.25; ROI=97.8%; Sales=400; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | webapp gpt | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1182 | APOLLO JULIENNE PEELER | Marshland Premium Y-Shape Julienne Vegetable Peeler - N | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=1.23; ROI=96.3%; Sales=200; Insufficient evidence |
| 1197 | SPONTEX QUICK SPRAY MOP DUO | Spontex Quick Spray Duo Flat Spray Mop with Washable Mi | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=30%; NP=12.73; ROI=94.4%; Sales=50; Partial match |
| 1197 | SPONTEX QUICK SPRAY MOP DUO | Spontex Quick Spray Duo Flat Spray Mop with Washable Mi | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=30%; NP=12.73; ROI=94.4%; Sales=50; Partial match |
| 1234 | YOGA ORNAMENT IN BAG 6CM | Yoga Gift for Yoga Instructor Yoga Accessories Women Fu | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=1.47; ROI=89.3%; Sales=200; Insufficient evidence |
| 1357 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 15L | Tidyz 3 Packs Of 40 White Plastic Disposable Pedal Bin  | Gemini | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=48%; NP=0.89; ROI=70.2%; Sales=50; Pack 120x makes profit negative |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1365 | WORLD OF PETS CAT TOY TEASER WITH BELL | Cat Teaser Pet Kitten Toy - Bell, Stick, Feather, Ball  | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=30%; NP=0.97; ROI=69.7%; Sales=50; Insufficient evidence |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1411 | MASTER COOK DIE CAST CASSEROLE 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm,  | Codex samecha | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=50%; NP=11.25; ROI=64.9%; Sales=50; Moderate similarity |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1423 | KINGAVON HEAD BAND WITH MOTION SENSOR & TORCH | Lumi Light Led Headband Ultra Bright 230Â° Adjustable H | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=36%; NP=3.64; ROI=63.0%; Sales=600; Weak match |
| 1464 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas Santa Sack Gift St | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=44%; NP=0.93; ROI=57.8%; Sales=100; Partial match |
| 1464 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas Santa Sack Gift St | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=44%; NP=0.93; ROI=57.8%; Sales=100; Partial match |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | webapp gpt | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1479 | TIDYZ FOOD BAG 300PCS | 600 TidyZ Food Freezer Bags with TIe Handles. Large Kit | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=19%; NP=0.66; ROI=56.3%; Sales=400; Partial match |
| 1479 | TIDYZ FOOD BAG 300PCS | 600 TidyZ Food Freezer Bags with TIe Handles. Large Kit | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=19%; NP=0.66; ROI=56.3%; Sales=400; Partial match |
| 1486 | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Status 15 Metre TV Aerial Cable Extension Kit  White  | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=44%; NP=1.05; ROI=55.8%; Sales=200; Partial match |
| 1486 | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Status 15 Metre TV Aerial Cable Extension Kit  White  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=44%; NP=1.05; ROI=55.8%; Sales=200; Partial match |
| 1505 | EXTRASTAR LED FLASHLIGHT USB REECHARGABLE TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=31%; NP=1.95; ROI=52.0%; Sales=100; Partial match |
| 1506 | TIDYZ FREEZER BAGS 100 PCS XLLARGE | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=26%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1506 | TIDYZ FREEZER BAGS 100 PCS XLLARGE | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=26%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1507 | TIDYZ FREEZER BAGS 150PCS | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=24%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1507 | TIDYZ FREEZER BAGS 150PCS | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=24%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fra | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=54%; NP=0.61; ROI=45.9%; Sales=50; Partial match |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fra | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=54%; NP=0.61; ROI=45.9%; Sales=50; Partial match |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fra | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=54%; NP=0.61; ROI=45.9%; Sales=50; Partial match |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | webapp gpt | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1652 | DEKTON DENT PULLER SUCTION | Car Dent Puller,Dent Removal kit, 2 Pack Dent Puller, P | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=19%; NP=1.08; ROI=35.3%; Sales=500; Pack 2x makes profit negative |
| 1656 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=29%; NP=1.48; ROI=34.8%; Sales=700; Partial match |
| 1664 | TIDYZ RUBBLE BAG HEAVY DUTY 7BAGS 32L | 20 TidyZ Heavy-Duty Rubble Sacks. Made from 100% Recycl | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=25%; NP=0.41; ROI=34.0%; Sales=100; Partial match |
| 1664 | TIDYZ RUBBLE BAG HEAVY DUTY 7BAGS 32L | 20 TidyZ Heavy-Duty Rubble Sacks. Made from 100% Recycl | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=25%; NP=0.41; ROI=34.0%; Sales=100; Partial match |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clip | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=51%; NP=1.26; ROI=33.1%; Sales=100; Partial match |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clip | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=51%; NP=1.26; ROI=33.1%; Sales=100; Partial match |
| 1696 | EXTRASTAR EXTENSION LEAD 6 GANG 1M BLACK | ExtraStar 6 Way Extension Leads with Surge Protection,  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=1.08; ROI=31.3%; Sales=200; Partial match |
| 1697 | EXTRASTAR EXTENSION LEAD 6 GANG 1M WHITE | ExtraStar 6 Way Extension Leads with Surge Protection,  | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=1.08; ROI=31.3%; Sales=500; Partial match |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1708 | TOWER PRESTO 2 TIER STEAMER PT21004WHT | Aigostar 3 Tier Electric Food Steamer 12L, 900W Vegetab | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=19%; NP=5.75; ROI=30.7%; Sales=300; Insufficient evidence |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=53%; NP=0.86; ROI=29.1%; Sales=300; Partial match |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=53%; NP=0.86; ROI=29.1%; Sales=300; Partial match |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=53%; NP=0.86; ROI=29.1%; Sales=300; Partial match |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | Codex samecha | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1742 | BLUE CANYON LED VANITY MIRROR 17CM X 22CM | Blue Canyon 17cm Free Standing Round Swivel Mirror - Ch | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=27%; NP=1.36; ROI=28.0%; Sales=100; Partial match |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | Codex very high | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | cli | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1746 | LIFETIME BATH GLOVE | Temple Spring Exfoliating Glove, Carbonized Rayon Bambo | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=14%; NP=0.33; ROI=27.8%; Sales=500; Insufficient evidence |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | Codex samecha | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1750 | RUBBER RING & BONE DOG TOYS 3 COLOURS | Nerf Dog 3-Ring Rubber Tug Toy, 10.5-Inch Lightweight W | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=0.55; ROI=27.3%; Sales=50; Insufficient evidence |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casseroles high resis | opus2 | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=56%; NP=3.19; ROI=26.9%; Sales=300; Pack 3x makes profit negative |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1763 | TALA SILICONE SPATULA | GMY G9 Halogen Oven Bulb 25W 230V 300â„ƒ Heat Tolerant  | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=18%; NP=0.71; ROI=26.5%; Sales=100; Pack 4x makes profit negative |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1790 | PPS FOIL BBQ DRILL ROUND 2 TRAY 34CM | Large Aluminium Foil Trays Food Large Container with li | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=0.32; ROI=23.9%; Sales=200; Insufficient evidence |
| 1796 | KILNER PRESERVE JAR 0.25LTR SCREW LID | Kilner Preserve Jar 0.25L (250ml) Round Glass Screw Top | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=49%; NP=0.40; ROI=23.0%; Sales=50; Moderate similarity |
| 1796 | KILNER PRESERVE JAR 0.25LTR SCREW LID | Kilner Preserve Jar 0.25L (250ml) Round Glass Screw Top | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=49%; NP=0.40; ROI=23.0%; Sales=50; Moderate similarity |
| 1797 | APOLLO SILICON WHISK SPLASH 25CM | Apollo Whisk Rainbow, silicone, 26cm, 25x6x6 | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=47%; NP=0.37; ROI=22.8%; Sales=200; Moderate similarity |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | Codex very high | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=68%; NP=0.72; ROI=22.2%; Sales=600; Brand match: BAKER & SALT |
| 1805 | YALE ESSENTIALS DEADLOCK P/BRASS 64MM | Yale British Standard 5 Lever Mortice Deadlock, High Se | Codex samecha | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=36%; NP=1.62; ROI=22.1%; Sales=200; Partial match |
| 1808 | BEAUFORT MEASURE ULTIMATE JUG 2LTR | Beaufort - 2 Litre Clear Plastic Measuring Jug | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=50%; NP=0.25; ROI=21.5%; Sales=200; Moderate similarity |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | Codex very high | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml ( | Codex samecha | HIGHLY LIKELY | VERIFIED | ACCEPTABLE | Sim=78%; NP=0.79; ROI=20.9%; Sales=50; Exact EAN match |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1845 | ULTRA FLASHBAND LEAD FINISH 150MMX3M | Bostik Flashband Self Adhesive Flashing Tape Grey - 100 | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=35%; NP=0.95; ROI=19.2%; Sales=500; Weak match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1868 | TALA DISPOSABLE ICING BAGSX10 | Tala Icing Bag Set with 8 Interchangeable Stainless Ste | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=15%; NP=0.27; ROI=17.8%; Sales=200; Insufficient evidence |
| 1878 | KILROCK SERVICE-PRO COFFEE MACHINE DESCALER 150ML(SOLD  | Kilrock Service Pro Coffee Machine Descaler & Cleaner 2 | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=50%; NP=0.63; ROI=16.4%; Sales=100; Partial match |
| 1878 | KILROCK SERVICE-PRO COFFEE MACHINE DESCALER 150ML(SOLD  | Kilrock Service Pro Coffee Machine Descaler & Cleaner 2 | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=50%; NP=0.63; ROI=16.4%; Sales=100; Partial match |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1900 | KILROCK MOULD & MILDEW REMOVER BRUSH ON GEL 250ML(SOLD  | Kilrock Mould Remover Brush-On Gel 2 x 250ml - Eliminat | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=0.43; ROI=15.0%; Sales=200; Insufficient evidence |
| 1900 | KILROCK MOULD & MILDEW REMOVER BRUSH ON GEL 250ML(SOLD  | Kilrock Mould Remover Brush-On Gel 2 x 250ml - Eliminat | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=0.43; ROI=15.0%; Sales=200; Insufficient evidence |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1919 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS | Rolson 51 pc Screwdriver & Bit Set (Chrome Vanadium Ste | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=0.43; ROI=13.8%; Sales=400; Weak match |
| 1919 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS | Rolson 51 pc Screwdriver & Bit Set (Chrome Vanadium Ste | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=0.43; ROI=13.8%; Sales=400; Weak match |
| 1919 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS | Rolson 51 pc Screwdriver & Bit Set (Chrome Vanadium Ste | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=0.43; ROI=13.8%; Sales=400; Weak match |
| 1926 | PREMIER FLICKABRIGHT GLASS SPHERE CANDLE 10CM | Premier Decorations Red LED Flickabrights Wax Candle Ba | Opus | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=40%; NP=0.51; ROI=13.1%; Sales=50; Weak match |
| 1926 | PREMIER FLICKABRIGHT GLASS SPHERE CANDLE 10CM | Premier Decorations Red LED Flickabrights Wax Candle Ba | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=40%; NP=0.51; ROI=13.1%; Sales=50; Weak match |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1944 | WINDOW STYLE WALL MIRROR  70X36 | Window Style Mirror - Living Room Decor Hallway Home Pa | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=1.06; ROI=11.9%; Sales=100; Insufficient evidence |
| 1960 | PPS FOIL ROASTING 3 DISHES | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=39%; NP=0.17; ROI=11.1%; Sales=50; Weak match |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=59%; NP=0.36; ROI=10.1%; Sales=100; Brand match: SMART CHOICE |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=59%; NP=0.36; ROI=10.1%; Sales=100; Brand match: SMART CHOICE |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=59%; NP=0.36; ROI=10.1%; Sales=100; Brand match: SMART CHOICE |
| 1971 | MASTERCLASS SALT/PAPPER MILL BLACK | MasterClass Pepper Mill or Salt Grinder with Interchang | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=50%; NP=0.42; ROI=10.1%; Sales=100; Moderate similarity |
| 1973 | VIVID BIN FRESHENER PK2 | Vivid 6 x Bin Freshener Smelling FRESH Dustbins Swing P | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=0.14; ROI=10.0%; Sales=100; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | cli | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1982 | PPS PLASTIC GLASSES PINT 50PCS | CHEF ROYALE 50 Disposable Clear Plastic Glasses - Recyc | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=32%; NP=0.24; ROI=8.9%; Sales=50; Weak match |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1987 | BRIGHT & HOMELY JUTE TWINE GREEN 50M | KINGLAKE 50m Garden Twine String Green, 2mm Jute Twine  | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=0.09; ROI=8.6%; Sales=100; Insufficient evidence |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 1996 | APOLLO PAPER SMOOTHIE 20 STRAWS | Boba Straws Disposable Bubble Tea Smoothies Straw Jumbo | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=22%; NP=0.10; ROI=8.1%; Sales=300; Pack 50x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | cli | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2004 | LAV TUMBLER 3PCS | Lav Sude Tumbler Glass Set. Drinking Glasses. Pack of 6 | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=35%; NP=0.24; ROI=7.3%; Sales=400; Pack 2x makes profit negative |
| 2025 | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Oaktree UK 9ft Banner Happy 8th Birthday Pink | Codex HIGH | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=58%; NP=0.07; ROI=5.7%; Sales=50; Moderate similarity |
| 2025 | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Oaktree UK 9ft Banner Happy 8th Birthday Pink | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=58%; NP=0.07; ROI=5.7%; Sales=50; Moderate similarity |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2028 | ALBERO BOTTLE 500ML TRANSPARENT PK12 | Volila Glass Bottles with Stoppers 500ml - 6 Pack Clear | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=23%; NP=0.54; ROI=5.5%; Sales=700; Pack 6x makes profit negative |
| 2032 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild â€“ One Strike â€“ Multi-Purpose Quick-Drying | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=0.15; ROI=5.3%; Sales=500; Moderate similarity |
| 2032 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild â€“ One Strike â€“ Multi-Purpose Quick-Drying | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=0.15; ROI=5.3%; Sales=500; Moderate similarity |
| 2032 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild â€“ One Strike â€“ Multi-Purpose Quick-Drying | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=41%; NP=0.15; ROI=5.3%; Sales=500; Moderate similarity |
| 2060 | APOLLO RB CUTTING BOARD 30X20 | Apollo 3245 RB Bread Board 30cm Round, Multi-Colour, 30 | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=0.16; ROI=3.7%; Sales=100; Moderate similarity |
| 2060 | APOLLO RB CUTTING BOARD 30X20 | Apollo 3245 RB Bread Board 30cm Round, Multi-Colour, 30 | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=46%; NP=0.16; ROI=3.7%; Sales=100; Moderate similarity |
| 2062 | WHAM CRYSTAL 80LTR CLEAR BOX & LID | CRYSTAL 80L BOX & LID CLEAR 11315 | webapp gpt | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=63%; NP=0.23; ROI=3.5%; Sales=100; Moderate similarity |
| 2063 | AMTECH TENNON SAW 12INCH | Irwin 10503534 12T/13P XP3055-300 Jack Tenon Saw, 12, B | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=34%; NP=0.11; ROI=3.2%; Sales=300; Weak match |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | cli | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2068 | ASHLEY RECYCLING BAG SET 3PCE | Vinsani Set of 3 Reusable Fabric Recycling Bags â€“ Col | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=25%; NP=0.08; ROI=2.7%; Sales=200; Pack 3x makes profit negative |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | Opus | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | opus2 | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2074 | CABANA ROUND TINS  SET OF 3 | Cooksmart English Meadow Set of 3 Round Cake Tins, Engl | Codex samecha | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=0.14; ROI=2.3%; Sales=100; Insufficient evidence |
| 2079 | AMTECH DOUBLE SIDED STORAGE BOX 34 SECTION | JOREST 59Pcs Small Precision Screwdriver Set with Torx  | Codex samecha | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=15%; NP=0.15; ROI=1.8%; Sales=500; Pack 59x makes profit negative |
| 2083 | WHAM MEASURING JUG 2LTR | Wham Cuisine 2L Clear Measuring Jug,JNS_453403 | Gemini | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=52%; NP=0.02; ROI=1.5%; Sales=100; Moderate similarity |
| 2088 | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM | STATUS 2 Way Socket  2 USB Port Cable Free Socket  S2 | Opus | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=51%; NP=0.04; ROI=1.2%; Sales=200; Moderate similarity |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | Codex HIGH | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | Gemini | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | cli | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | opus2 | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | webapp gpt | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2092 | ULTRATAPE FLASHBAND LEAD 100MMX10M | Bostik Flashband Self Adhesive Flashing Tape for Roofs  | opus2 | HIGHLY LIKELY | OTHER / LOW PRIORITY | INCORRECT | Sim=24%; NP=0.07; ROI=0.9%; Sales=500; Insufficient evidence |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=0.02; ROI=0.8%; Sales=50; Brand match: ROLSON |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=61%; NP=0.02; ROI=0.8%; Sales=50; Brand match: ROLSON |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | Codex samecha | HIGHLY LIKELY | VERIFIED | ACCEPTABLE | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2098 | WHAM CRYSTAL 160LTR CLEAR BOX & LID | Wham Pack of 2 Crystal Storage Boxes with Lids, Plastic | opus2 | HIGHLY LIKELY | FILTERED OUT | INCORRECT | Sim=34%; NP=0.05; ROI=0.4%; Sales=300; Pack 2x makes profit negative |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | Codex HIGH | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=0.01; ROI=0.3%; Sales=100; Brand match: SMART CHOICE |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | Gemini | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=0.01; ROI=0.3%; Sales=100; Brand match: SMART CHOICE |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | webapp gpt | HIGHLY LIKELY | HIGHLY LIKELY | CORRECT | Sim=67%; NP=0.01; ROI=0.3%; Sales=100; Brand match: SMART CHOICE |
| 2102 | FLOW FLOOR & SURFACE CLEANER 5L EACH | Flow Lemon Floor & Surface All Purpose Cleaner  Concen | Codex samecha | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=0.00; ROI=0.0%; Sales=50; Moderate similarity |
| 2102 | FLOW FLOOR & SURFACE CLEANER 5L EACH | Flow Lemon Floor & Surface All Purpose Cleaner  Concen | opus2 | HIGHLY LIKELY | NEEDS VERIFICATION | ACCEPTABLE | Sim=42%; NP=0.00; ROI=0.0%; Sales=50; Moderate similarity |

### NEEDS VERIFICATION (claimed, n=476)

| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |
|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|
| 30 | LYNWOOD MINI ROLLER SET 5PACK | Mould King V8 Engine Building Blocks Set, 2250 PCS Comb | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=65.52; ROI=2259.2%; Sales=50; Insufficient evidence |
| 131 | BRIGHT & HOMELY METAL WATERING CAN ROSE | Woodside Silver 9L Metal Garden and Plant Watering Can  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.53; ROI=863.1%; Sales=50; Moderate similarity |
| 131 | BRIGHT & HOMELY METAL WATERING CAN ROSE | Woodside Silver 9L Metal Garden and Plant Watering Can  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.53; ROI=863.1%; Sales=50; Moderate similarity |
| 131 | BRIGHT & HOMELY METAL WATERING CAN ROSE | Woodside Silver 9L Metal Garden and Plant Watering Can  | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.53; ROI=863.1%; Sales=50; Moderate similarity |
| 142 | PUREBREED KNOTS COLLAGEN MEDIUM PACK OF 2 | Pura Collagen Powdered Supplement Glow+, 10,000mg Hydro | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=14.22; ROI=798.9%; Sales=400; Insufficient evidence |
| 162 | EVERBUILD SEALANT STRIPOUT TOOL | Everbuild Super Flow Sealant/Adhesive Cartridge Applica | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=35%; NP=28.79; ROI=725.2%; Sales=400; Partial match |
| 163 | PPS PLASTIC PLATE 3CPMPARTMENTS WHITE 26CM 3PCS | MATANA 25 Premium White Plastic Dinner Plates with Gold | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=7.97; ROI=718.2%; Sales=600; Insufficient evidence |
| 164 | PPS 26CM PLASTIC WHITE PLATE 6 PCS | MATANA 25 Premium White Plastic Dinner Plates with Gold | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=24%; NP=7.97; ROI=718.2%; Sales=600; Insufficient evidence |
| 168 | WAX WORKS PILLAR CANDLE 30 HOURS | WoodWick Large Hourglass Scented Candle  Linen  with  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=10.16; ROI=700.9%; Sales=200; Weak match |
| 170 | PUREBREED KNOTS COLLAGEN SMALL PACK OF 5 | Pura Collagen Powdered Supplement Glow+, 10,000mg Hydro | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=12.44; ROI=698.8%; Sales=400; Insufficient evidence |
| 172 | AMTECH RECHARGEABLE WORK LIGHT WITH MAGNETIC STAND 3W | T-SUN Rechargeable LED Work Light with Metal Stand,4100 | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=40%; NP=32.02; ROI=684.2%; Sales=100; Weak match |
| 174 | WENKEN FOOD PROCESSOR & BLENDER 2 IN 1 | Kenwood FDP65.180SI 2 in 1 Food Processor Multipro Expr | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=33.44; ROI=681.0%; Sales=300; Moderate similarity |
| 188 | LIFETIME FILE 3pc 6ASS DSGN | File Organiser 24 Pockets Document Organiser Expanding  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=16%; NP=7.42; ROI=651.1%; Sales=300; Insufficient evidence |
| 208 | BRIGHT & HOMELY HANGERS VELVET NON SLIP GREY 5 PACK | 50 Non Slip Velvet Hangers  Heavy Duty Grey Felt Coat  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=9.05; ROI=603.2%; Sales=400; Insufficient evidence |
| 217 | 2 Pack Dog Squeaky Toys | 2-Pack Squeaky Dog Toys, Long Crinkle Tail with Treat D | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=17%; NP=8.76; ROI=584.1%; Sales=100; Insufficient evidence |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) Lavender Scented | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=16.14; ROI=566.3%; Sales=800; Partial match |
| 239 | CHRISTMAS PIPE CLEANERS 40PC | PLULON 60 Sets Christmas Crafts for Kids Christmas Bead | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=5.67; ROI=540.0%; Sales=100; Insufficient evidence |
| 241 | DELICIOUS POUCH MEATY SAUSAGE PK7 | Forthglade Meaty Sausages (4 x 100g Bags) - Hypoallerge | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=7.48; ROI=538.5%; Sales=50; Insufficient evidence |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=76%; NP=10.37; ROI=526.1%; Sales=100; Partial match |
| 253 | DEKTON CABLE TIES BLACK 100PCS 4.8MMX300MM | XINGO Black Cable Ties Pack of 1000, 300mm x 4.8mm, Pre | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=11.39; ROI=525.1%; Sales=50; Insufficient evidence |
| 301 | BRIGHT & HOMELY BYPASS LOPPER | Spear & Jackson 8090RS Razorsharp Telescopic Ratchet By | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=11.62; ROI=452.2%; Sales=300; Moderate similarity |
| 302 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | Hobby Gift Sewing Box, Wood/Fabric, Embroidered Bee, Me | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=9.98; ROI=449.8%; Sales=400; Moderate similarity |
| 302 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | Hobby Gift Sewing Box, Wood/Fabric, Embroidered Bee, Me | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=9.98; ROI=449.8%; Sales=400; Moderate similarity |
| 309 | BRIGHT & HOMELY FOIL PLATTER 14 INCH 355MM X 245MM X 21 | MATANA 20 Large Aluminium Foil Platters, 14" (35x26cm)  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=4%; NP=5.18; ROI=442.6%; Sales=400; Insufficient evidence |
| 313 | DRAPER HSS DRILL BIT 1.5 MM | Draper 18551 Combined HSS and Masonry Drill Bit Set, Bl | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=50%; NP=5.16; ROI=440.6%; Sales=100; Pack 17x makes profit negative |
| 318 | ROLSON DOUBLE OPEN END SPANNER 5PC SET | DURATECH Double Open End Spanner Set, Super-Thin Open E | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=11.85; ROI=434.2%; Sales=100; Insufficient evidence |
| 329 | BRIGHT & HOMELY PILLAR CANDLE IVORY 100 HOUR BURN 20CM  | simpa Unscented Ivory Pillar Candles Smokeless Burn 100 | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.62; ROI=416.3%; Sales=100; Moderate similarity |
| 329 | BRIGHT & HOMELY PILLAR CANDLE IVORY 100 HOUR BURN 20CM  | simpa Unscented Ivory Pillar Candles Smokeless Burn 100 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.62; ROI=416.3%; Sales=100; Moderate similarity |
| 329 | BRIGHT & HOMELY PILLAR CANDLE IVORY 100 HOUR BURN 20CM  | simpa Unscented Ivory Pillar Candles Smokeless Burn 100 | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=10.62; ROI=416.3%; Sales=100; Moderate similarity |
| 330 | BRIGHT & HOMELY FOIL PIE DISHES 215MM X 45MM X 45MM 5 P | 110 mm x 33 mm Round Foil Container - Pie dishes x 100 | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=4.84; ROI=413.5%; Sales=100; Weak match |
| 330 | BRIGHT & HOMELY FOIL PIE DISHES 215MM X 45MM X 45MM 5 P | 110 mm x 33 mm Round Foil Container - Pie dishes x 100 | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=4.84; ROI=413.5%; Sales=100; Weak match |
| 345 | ADORN GLASS STAR TEALIGHT HOLDER | Set of 4 Clear Glass Tealight Holders, Various Shapes,  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=4.86; ROI=398.6%; Sales=50; Weak match |
| 348 | WAX MELTS YOGA 68G 6 PCS | Mixed Perfume Wax Melts: 16 x 6g Heart Shaped Melts in  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=5.42; ROI=398.2%; Sales=300; Insufficient evidence |
| 354 | SMART CHOICE CHICKEN & RICE BONE DOG TREAT 10 PK 125G | Good Boy - Crunchy Chicken and Rice Bones - Dog Treats  | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=7.89; ROI=392.7%; Sales=200; Moderate similarity |
| 366 | CHRISTMAS TEALIGHTS SPICED CINNAMON 10 PACK | St Eval  Orange and Cinnamon Scented Tealights  Warm  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=4.04; ROI=385.2%; Sales=200; Insufficient evidence |
| 388 | PPS PLASTIC SALAD BOWL WHITE 50OZ 5PCS | MATANA 25 Premium White Plastic Bowls with Gold Rim, 36 | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=4.60; ROI=365.2%; Sales=300; Insufficient evidence |
| 396 | KINGAVON 6 LED TORCH | Kingavon BB-RT380 20-LED Rechargeable Emergency Sensor  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=5.59; ROI=358.5%; Sales=50; Moderate similarity |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=5.07; ROI=354.6%; Sales=50; Partial match |
| 404 | FLOWER SHOP INCENSE STICKS PK40 | Natural Incense Sticks Multipack Variants - 5 (90 gms)  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=5.26; ROI=350.8%; Sales=900; Insufficient evidence |
| 415 | SMART CHOICE 30 BEEF/CHICKEN STICKS | Webbox Dog Delight Variety Pack of 12 (6 x Beef 6 x Chi | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=50%; NP=6.85; ROI=340.7%; Sales=800; Pack 12x makes profit negative |
| 428 | MASON HEAVY DUTY SPRING CLAMPS 4" 2 PIECES | 10 Pieces Large Nylon Spring Clamps, 6 Inch and 4 Inch  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=4.62; ROI=332.0%; Sales=50; Weak match |
| 431 | AMTECH FLAT TIP ART B/SET XL 12PC | 5pcs Fuumuui Dual-Layer Synthetic Hair Flat Grainer Bru | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=25%; NP=10.54; ROI=326.5%; Sales=50; Pack 5x makes profit negative |
| 447 | APOLLO STAINLESS STEEL SHARPENING STEEL | Professional Carbon Steel Black Knife Sharpening Steel, | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=6.23; ROI=314.5%; Sales=300; Moderate similarity |
| 447 | APOLLO STAINLESS STEEL SHARPENING STEEL | Professional Carbon Steel Black Knife Sharpening Steel, | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=6.23; ROI=314.5%; Sales=300; Moderate similarity |
| 447 | APOLLO STAINLESS STEEL SHARPENING STEEL | Professional Carbon Steel Black Knife Sharpening Steel, | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=6.23; ROI=314.5%; Sales=300; Moderate similarity |
| 459 | BABY PIPKIN CLASSIC ROUND BABY BOTTLE 5oz | Dr Brown's Natural FlowÂ® Anti-Colic Options+â„¢ Wide-N | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=3.92; ROI=311.4%; Sales=100; Weak match |
| 461 | STEAM PUNK SKULL GOLD/BRONZE10CM ASSORTED | Nemesis Now Steampunk Clockwork Baron Skull Figurine Or | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=9.88; ROI=310.7%; Sales=50; Moderate similarity |
| 464 | APOLLO CHROME TOILET BRUSH & HOLDER | BGL 304 Stainless Steel Toilet Brush Long Bucket Stand  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=12.09; ROI=309.2%; Sales=200; Weak match |
| 471 | JCB LED BULB WARM WHITE CANDLE SBC 6W/40W | 10 X JCB 6w = 40w LED Opal Candles - 3000k - Warm White | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=38%; NP=3.89; ROI=303.8%; Sales=200; Pack 10x makes profit negative |
| 472 | JCB LED BULB WARM WHITE CANDLE BC 6W/40W | 10 X JCB 6w = 40w LED Opal Candles - 3000k - Warm White | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=35%; NP=3.89; ROI=303.8%; Sales=200; Pack 10x makes profit negative |
| 478 | DELICIOUS POUCH MEATY STICKS PK7 | Good Boy Meaty Sticks Variety Pack - Natural Dog Treats | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=4.18; ROI=300.7%; Sales=700; Insufficient evidence |
| 485 | CHAMPAGNE GLASS PLASTIC ASSORTED 177ML | MATANA 24 Premium Plastic Champagne Flutes with Gold Gl | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=3.78; ROI=300.1%; Sales=300; Insufficient evidence |
| 496 | BLOOME OIL FRAGRANCE 2PK | Arabian Oudh Diffuser Oil Set, Essential Oils by Dukhni | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=12%; NP=4.08; ROI=293.6%; Sales=100; Insufficient evidence |
| 497 | PPS SERVING PLATTER REUSABLE PLASTIC WHITE 35x21CM 2 PI | MATANA 6 White Rectangular Serving Platters with Silver | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=3.29; ROI=293.3%; Sales=50; Weak match |
| 511 | LAV NECTAR TUMBLER 3PC 280ML | LAV 12x 280ml Nectar Glass Tumblers - Dishwasher Safe K | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=7.66; ROI=287.0%; Sales=50; Insufficient evidence |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainless Steel, Silv | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=67%; NP=3.97; ROI=285.9%; Sales=600; Partial match |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainless Steel, Silv | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=67%; NP=3.97; ROI=285.9%; Sales=600; Partial match |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainless Steel, Silv | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=67%; NP=3.97; ROI=285.9%; Sales=600; Partial match |
| 515 | ADORN REUSABLE SHOT GLASSES COLORED 20 PACK | Volila Heavy Base Shot Glasses - 25ml (6 Pack) Coloured | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=3.45; ROI=282.5%; Sales=600; Insufficient evidence |
| 538 | SPECIAL OCCASIONS RAINBOW COLOUR HAIR SPRAY 200ML | 6 * 200ml Cans Rainbow Colour Hair Spray - Perfect for  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=40%; NP=4.13; ROI=275.7%; Sales=100; Weak match |
| 553 | PAN AROMA TEALIGHTS 16PC BERGAMOT MANDARIN | St Eval  Bergamot & Nettle Scented Tealights  Uplifti | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=26%; NP=3.89; ROI=268.3%; Sales=200; Pack 9x makes profit negative |
| 557 | APOLLO ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rolling Pin with Revo | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=5.11; ROI=266.0%; Sales=600; Weak match |
| 558 | SECURPLUMB COMPRESSION ELBOW 10X10MM | Radiator Valve Reducer Elbow Compression 15mm x 10mm Pu | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=4.39; ROI=264.7%; Sales=50; Moderate similarity |
| 565 | SIL INCENSE HEX STICKS PK4 FLOWER | Natural Incense Sticks Multipack Variants - 5 (90 gms)  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=4.89; ROI=261.7%; Sales=900; Insufficient evidence |
| 574 | ROLSON DIAGONAL CUTTING PLIER VDE INSULATED 180MM | KNIPEX 70 06 180 Diagonal Cutter chrome plated insulate | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=16.20; ROI=256.3%; Sales=50; Moderate similarity |
| 592 | WOODEN HANGERS 2 PACK | Amazon Basics 20 Bar Wooden Tie Hanger & Belt Rack, 2-P | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=40%; NP=3.88; ROI=248.8%; Sales=50; Moderate similarity |
| 600 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | 6 x Kilner Clip Top Glass Storage Jar - Square 1 Litre | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=8.49; ROI=246.2%; Sales=50; Pack 6x makes profit negative |
| 600 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | 6 x Kilner Clip Top Glass Storage Jar - Square 1 Litre | Opus | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=8.49; ROI=246.2%; Sales=50; Pack 6x makes profit negative |
| 600 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | 6 x Kilner Clip Top Glass Storage Jar - Square 1 Litre | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=8.49; ROI=246.2%; Sales=50; Pack 6x makes profit negative |
| 613 | WHAM CRYSTAL 60LTR SMOKE BOX & LID | Wham Crystal 5 x 60L Stackable Plastic Storage Boxes wi | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=13.81; ROI=238.1%; Sales=50; Weak match |
| 616 | LAV FAME WINE GLASS 40CL PK3 | LAV 12x Clear 400ml Lal Red Wine Glasses - Large Glass  | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=8.11; ROI=237.9%; Sales=400; Weak match |
| 616 | LAV FAME WINE GLASS 40CL PK3 | LAV 12x Clear 400ml Lal Red Wine Glasses - Large Glass  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=8.11; ROI=237.9%; Sales=400; Weak match |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | Codex HIGH | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners Waste Rubbish B | webapp gpt | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=2.77; ROI=236.5%; Sales=500; Brand match: TIDYZ |
| 622 | FOUR SEASONS PLASTIC 4 TONGS | 9â€ Kitchen Tongs, 4 Pcs Stainless Steel Tongs with Si | Codex samecha | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=9%; NP=3.10; ROI=236.3%; Sales=400; Insufficient evidence |
| 628 | SECURPAK DRYWALL SCREWS BLACK 3.5X65MM | TIMCO PH2 Philips Drywall Screws - 3.5 x 32 - Black - B | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=2.83; ROI=234.1%; Sales=50; Moderate similarity |
| 641 | MASON NAIL ASSORTMENT 124 PIECES | Brackit 2,000 Piece Nail Assortment Set with Storage Ca | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=3.19; ROI=229.6%; Sales=100; Insufficient evidence |
| 643 | SPLATTER SCREEN GUARD 2PC SILVER 24/28CM | Snowyee Splatter Screen for Frying Pan, Grease Splatter | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=33%; NP=3.79; ROI=228.4%; Sales=300; Weak match |
| 645 | PPS NAPKINS 1PLY WHITE 30X30CM 100PCS | 500 x White Serviettes Paper Napkins (30 x 30 cm) 1-Ply | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=2.39; ROI=227.8%; Sales=700; Insufficient evidence |
| 651 | THE BIG CHEESE NEO ZAP ELECTRONIC RAT KILLER REFILL | The Big Cheese Ultra Power - Electronic Mouse Killer, Q | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=6.67; ROI=226.3%; Sales=200; Weak match |
| 656 | PPS BAGASSE PLATE 26CM 10 PIECES | Disposable Paper Plate 10 Inch Heavy Duty Strong Bagass | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=2.87; ROI=224.1%; Sales=200; Insufficient evidence |
| 658 | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L | Tidyz 6 Packs Of 40 White Plastic Bin Bags - Fits 15L P | Gemini | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=39%; NP=2.73; ROI=223.5%; Sales=500; Pack 240x makes profit negative |
| 659 | TIDYZ COMPOSTABLE 15 BAGS 10LTR | Tidyz 6 Packs Of 40 White Plastic Bin Bags - Fits 15L P | Gemini | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=32%; NP=2.73; ROI=223.5%; Sales=500; Pack 16x makes profit negative |
| 661 | FESTIVE MAGIC VINTAGE RIBBON 63MM X 2.7M | Christmas Velvet Ribbon - Thick Red Wired 9m Edge 63mm  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=2.85; ROI=222.3%; Sales=500; Insufficient evidence |
| 662 | BRIGHT & HOMELY SAUCEPAN NON STICK COOKWARE SET 6PCS | 11Pcs Pots and Pans Set, Nonstick Cookware Sets, White  | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=18.61; ROI=222.0%; Sales=50; Weak match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | Schott Zwiesel Pure Glassware - White Wine Glasses - Se | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=7.18; ROI=214.9%; Sales=200; Partial match |
| 674 | BRIGHT & HOMELY FOIL ROASTING TRAY SQUARE 205MM X 205MM | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=2.51; ROI=214.4%; Sales=400; Insufficient evidence |
| 675 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS 130MM X 101MM X  | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=2.51; ROI=214.4%; Sales=400; Insufficient evidence |
| 676 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS 148MM X 120MM X  | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=2.51; ROI=214.4%; Sales=400; Insufficient evidence |
| 679 | SPRING FLORAL CANDLE POTS SET OF 3 | Scented Candles Gift Set, Gifts for Women, 12 x 70 g Ca | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=7.17; ROI=214.0%; Sales=200; Insufficient evidence |
| 681 | FESTIVE MAGIC GIFT WRAPPING SET 14PC | 70x50cm Christmas Wrapping Paper Sheets Set with Tags & | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=4.13; ROI=211.9%; Sales=50; Insufficient evidence |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 697 | SIL CRAFT PAINT POTS | Mini Acrylic Paint Set, 10pcs 8Colors Acrylic Paint Str | Codex samecha | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=0%; NP=2.88; ROI=207.3%; Sales=200; Pack 10x makes profit negative |
| 705 | BRIGHT & HOMELY FOIL ROASTING TRAY 320MM X 265MM X 60MM | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=2.46; ROI=201.5%; Sales=400; Insufficient evidence |
| 715 | COTTON BUDS IN JAR 12X6CM 50 PCS | Cotton Bud Holder 10 Oz Bathroom Jars with Lids for Cot | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=2.63; ROI=197.6%; Sales=400; Weak match |
| 715 | COTTON BUDS IN JAR 12X6CM 50 PCS | Cotton Bud Holder 10 Oz Bathroom Jars with Lids for Cot | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=2.63; ROI=197.6%; Sales=400; Weak match |
| 716 | BABY PIPKIN SILICONE PACIFIER | Baby Fruit Feeder Set, Includes 2 Food Dummy Feeders wi | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=2.48; ROI=197.2%; Sales=100; Weak match |
| 720 | BRIGHT & HOMELY CITRONELLA TEALIGHT CANDLES LARGE 4 PAC | Price's Candles Citronella Tealights - 100 Pack | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=62%; NP=2.72; ROI=196.0%; Sales=200; Pack 25x makes profit negative |
| 722 | SANCTUARY TREE OF LIFE MIRROR BRONZE EFFECT 50CM | Inspirational Gifting Beautiful green leaf tree of life | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=18.46; ROI=195.4%; Sales=50; Moderate similarity |
| 723 | SANCTUARY TREE OF LIFE MIRROR GREY EFFECT 50CM | Inspirational Gifting Beautiful green leaf tree of life | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=18.46; ROI=195.4%; Sales=50; Moderate similarity |
| 724 | SANCTUARY TREE OF LIFE MIRROR WHITE EFFECT 50CM | Inspirational Gifting Beautiful green leaf tree of life | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=18.46; ROI=195.4%; Sales=50; Weak match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 748 | PAN AROMA CANDLE 85G PURE JASMINE | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=2.73; ROI=187.9%; Sales=50; Weak match |
| 749 | PAN AROMA CANDLE 85G LEMONGRASS | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=39%; NP=2.73; ROI=187.9%; Sales=50; Weak match |
| 753 | THL DIVIDER PLATE REUSABLE 10INCH 8PCS | 10" Portion Control Plate for Balanced Eating - Healthy | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=17%; NP=2.40; ROI=187.1%; Sales=50; Insufficient evidence |
| 754 | WOODEN INSECT HOUSE METAL ROOF | Garden Life Insect Hotel Wooden Bug House Natural Nest  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=7.19; ROI=186.8%; Sales=100; Moderate similarity |
| 754 | WOODEN INSECT HOUSE METAL ROOF | Garden Life Insect Hotel Wooden Bug House Natural Nest  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=7.19; ROI=186.8%; Sales=100; Moderate similarity |
| 756 | PAN AROMAREINDEER 12PK CHRISTMAS TEALIGHTS - CINNAMON S | St Eval  Orange and Cinnamon Scented Tealights  Warm  | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=26%; NP=3.31; ROI=186.2%; Sales=200; Pack 9x makes profit negative |
| 760 | BRIGHT & HOMELY CITRONELLA CANDLE IN GLASS JAR | ANGIX 4 x Citronella Candles in Glass Jar Holders Ideal | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=2.57; ROI=184.7%; Sales=50; Weak match |
| 761 | CITRONELLA CANDLE IN GLASS POT | ANGIX 4 x Citronella Candles in Glass Jar Holders Ideal | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=2.57; ROI=184.7%; Sales=50; Weak match |
| 762 | VFM  TRADE CONT MATT PAINT WHT 10L | Johnstone'S Trade 10 Litre Covaplus Vinyl Matt Brillian | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=17.82; ROI=184.1%; Sales=100; Moderate similarity |
| 762 | VFM  TRADE CONT MATT PAINT WHT 10L | Johnstone'S Trade 10 Litre Covaplus Vinyl Matt Brillian | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=17.82; ROI=184.1%; Sales=100; Moderate similarity |
| 767 | FIESTA GLASS MUG 245ML PK3 | Fusion Food Double Walled Coffee Glasses Mugs - Pack of | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=14%; NP=3.26; ROI=181.2%; Sales=50; Insufficient evidence |
| 771 | BLACKSPUR FACE MASK WITH VALVE 3PC | Face Masks - Breathable Face Masks with Filter - Cotton | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=4.03; ROI=180.8%; Sales=600; Weak match |
| 781 | GROSVENOR 55CM TROUGH BLACK | 4 Black Gros Trough 55cm | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=5.93; ROI=177.6%; Sales=50; Moderate similarity |
| 781 | GROSVENOR 55CM TROUGH BLACK | 4 Black Gros Trough 55cm | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=5.93; ROI=177.6%; Sales=50; Moderate similarity |
| 781 | GROSVENOR 55CM TROUGH BLACK | 4 Black Gros Trough 55cm | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=5.93; ROI=177.6%; Sales=50; Moderate similarity |
| 784 | VINERS EVERYDAY PURITY 4PC DINNER KNIFE | Viners Everyday Breeze 16 Piece 18/0 Silver Stainless S | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=6.77; ROI=175.9%; Sales=50; Pack 16x makes profit negative |
| 785 | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM | Mason Cash in The Forest Hedgehog Mixing Bowl 1.1 Litre | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=33%; NP=7.96; ROI=175.7%; Sales=100; Partial match |
| 786 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=5.47; ROI=174.9%; Sales=400; Partial match |
| 791 | FAIRY DISH BRUSH 3 REFILLS | Fillable Washing up Brush and Sponge - Easy Grip Dish C | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=2.80; ROI=173.7%; Sales=50; Insufficient evidence |
| 792 | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6PCS | 100 Paper Cups - Disposable Paper Cups for Hot and Cold | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=2.19; ROI=173.7%; Sales=800; Weak match |
| 793 | ECO WISE PAPER CUPS LIDS 8OZ PK25 | 100 Paper Cups - Disposable Paper Cups for Hot and Cold | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=2.19; ROI=173.7%; Sales=800; Weak match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 798 | KINGFISHER PLASTIC 15 HALF PINT GLASSES | Plastic Half Pint Glasses 50 Pack Strong Disposable Bee | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=2.18; ROI=173.1%; Sales=100; Pack 50x makes profit negative |
| 802 | BLACKSPUR CAR HEADLIGHT BULB 12V 60W/55W H4 | Bosch H4 (472) Pure Light Halogen Headlight Bulbs, 12 V | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=3.31; ROI=172.2%; Sales=800; Weak match |
| 804 | ADORN LARGE WIRE FRUIT BOWL 25X10.5CM | Black Fruit Bowl, 25x14cm Large Wire Fruit Bowl, Metal  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=4.26; ROI=171.7%; Sales=200; Moderate similarity |
| 804 | ADORN LARGE WIRE FRUIT BOWL 25X10.5CM | Black Fruit Bowl, 25x14cm Large Wire Fruit Bowl, Metal  | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=4.26; ROI=171.7%; Sales=200; Moderate similarity |
| 807 | BETTINA WASHING UP BRUSH & REFILL | Premium Soap Dispenser Washing Up Brush with 9 X Refill | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=2.72; ROI=171.2%; Sales=50; Weak match |
| 810 | BLACKSPUR SEL DRILL PLASTERBOARD FIXING 30PC | NCaan 20pk Heavy Duty Metal Self-Drill Plasterboard Fix | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=4%; NP=1.99; ROI=170.2%; Sales=300; Pack 20x makes profit negative |
| 812 | BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK | BGL Stainless Steel Standing Toilet Brush for Bath Deco | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=7.40; ROI=170.1%; Sales=100; Partial match |
| 812 | BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK | BGL Stainless Steel Standing Toilet Brush for Bath Deco | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=7.40; ROI=170.1%; Sales=100; Partial match |
| 812 | BLUE CANYON TOILET BRUSH PLASTIC LACE BLACK | BGL Stainless Steel Standing Toilet Brush for Bath Deco | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=7.40; ROI=170.1%; Sales=100; Partial match |
| 813 | PRO USER FLAT DRILL BIT 15PC SET | Bosch 7x EXPERT Self Cut Speed Spade Drill Bit Set (for | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=8.25; ROI=169.8%; Sales=500; Insufficient evidence |
| 831 | RUBBER DUCK FAMILY BATH TOY 3 PACK | Rubber Duck Bath Toy Set â€“ Floating Duck Family by KO | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=2.13; ROI=166.3%; Sales=200; Weak match |
| 831 | RUBBER DUCK FAMILY BATH TOY 3 PACK | Rubber Duck Bath Toy Set â€“ Floating Duck Family by KO | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=2.13; ROI=166.3%; Sales=200; Weak match |
| 841 | ESSCENTS HOME INCENSE SET 30PC STICKS&HOLDER | Incense Sticks Gift Set, 180 Joss Incense Stick and Hol | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=2.73; ROI=163.8%; Sales=100; Weak match |
| 842 | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=51%; NP=2.86; ROI=163.5%; Sales=100; Pack 6x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | cli | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 856 | PAN AROMA CANDLE 85G LIME GINGER | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=2.56; ROI=159.3%; Sales=50; Weak match |
| 859 | APOLLO ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rolling Pin with Revo | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=4.99; ROI=158.5%; Sales=600; Weak match |
| 860 | LUXURY THANK YOU CARDS PK8 | 24 Thank You Cards Pack with Gold Foil Stickers and Kra | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=19%; NP=1.99; ROI=158.1%; Sales=600; Insufficient evidence |
| 861 | DEKTON HSS DRILL 13PC SET 2MM TO 8MM | Bosch Professional 9pc PointTeQ Hex Drill Bit Set (for  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=5.39; ROI=158.0%; Sales=200; Insufficient evidence |
| 867 | PPS FOIL ROAST DISH OVAL 46CM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=1.71; ROI=154.5%; Sales=50; Weak match |
| 869 | MASTER COOK CASSEROLE NON-STICK 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm,  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=45%; NP=17.36; ROI=154.3%; Sales=50; Moderate similarity |
| 869 | MASTER COOK CASSEROLE NON-STICK 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm,  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=45%; NP=17.36; ROI=154.3%; Sales=50; Moderate similarity |
| 878 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Waste Pipe Unblocke | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=2.60; ROI=152.2%; Sales=200; Partial match |
| 881 | WORLD OF PETS SALMON SHAPED DOG TREAT PK12 | Dog Biscuit Treats 2.5L (Salmon Burgers) | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=2.00; ROI=150.8%; Sales=100; Weak match |
| 883 | CURVER RATTAN ROUND LARGE ORGANISER GREY | CURVER Style Rattan Effect Kitchen, Living room, Bathro | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=2.71; ROI=150.6%; Sales=50; Moderate similarity |
| 903 | EASY WASHING POWDER COLOUR 13 WASH PK6 | Persil Non Bio Colour Washing Powder 8.4kg Family Pack  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=10.37; ROI=147.0%; Sales=100; Insufficient evidence |
| 915 | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=2.73; ROI=145.3%; Sales=100; Pack 6x makes profit negative |
| 922 | APOLLO MEGA ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rolling Pin with Revo | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=4.16; ROI=144.8%; Sales=600; Weak match |
| 924 | APOLLO BAMBOO SKEWERS PK100 | Lanjue 200 Paddle Bamboo Skewers 9CM, Flat Burgers Stic | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=1.92; ROI=144.3%; Sales=500; Insufficient evidence |
| 928 | BRIGHT & HOMELY HANGERS VELVET NON SLIP BLACK 10 PACK | 20 Non Slip Velvet Hangers  Heavy Duty Black Felt Coat | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=3.19; ROI=143.6%; Sales=50; Insufficient evidence |
| 931 | BRIGHT & HOMELY LAUNDRY BAG XLARGE 86CM PK10 ASSORTED C | Car Boot Organiser with Cooler Bag, Extra Large Premium | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=15.23; ROI=143.5%; Sales=100; Weak match |
| 932 | BOMBON GLASS MUG 10CL PACK OF 3 | Fusion Food Double Walled Coffee Glasses Mugs - Pack of | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=19%; NP=2.98; ROI=143.3%; Sales=50; Insufficient evidence |
| 937 | HAIR BOBBLES 36PC BROWN BLACK WHITE | 15 Pcs Brown and Black Hair Bobbles, Mixed Color Elasti | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=32%; NP=1.98; ROI=142.3%; Sales=200; Pack 15x makes profit negative |
| 939 | FLORAL CANDLE METAL LID 335G GARDENIA | Luxury Gardenia Candles Gifts for Women & Men Infused w | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=11%; NP=4.98; ROI=142.2%; Sales=100; Insufficient evidence |
| 940 | MUNCH N CRUNCH BIG BONE BISCUITS 3PK 150g | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe  | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=1.89; ROI=142.0%; Sales=50; Weak match |
| 940 | MUNCH N CRUNCH BIG BONE BISCUITS 3PK 150g | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=1.89; ROI=142.0%; Sales=50; Weak match |
| 941 | PPS FOIL PLATTERS 2PCS 352X247X25MM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=1.65; ROI=141.4%; Sales=50; Weak match |
| 941 | PPS FOIL PLATTERS 2PCS 352X247X25MM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=1.65; ROI=141.4%; Sales=50; Weak match |
| 946 | ADORN SHOWER CURTAIN DELUXE | Shower Curtains Mould Proof Resistant, EVA Waterproof H | Codex samecha | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=4.39; ROI=140.3%; Sales=400; Insufficient evidence |
| 965 | ROYAL MARKET PAPER PLATES 9INCH 30 PACK | Strong Paper Plates (9 Inch / 50-Pack) 100% Compostable | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=1.54; ROI=136.7%; Sales=700; Insufficient evidence |
| 968 | APOLLO  GRANITE BOARD 42X29 | Silk Route Home Black Granite Chopping Board 40 x 30cm | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=8.29; ROI=136.2%; Sales=50; Moderate similarity |
| 968 | APOLLO  GRANITE BOARD 42X29 | Silk Route Home Black Granite Chopping Board 40 x 30cm | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=8.29; ROI=136.2%; Sales=50; Moderate similarity |
| 974 | THE PET STORE LONG HANDLED POOP PICKER | 32" XL Dog Pooper Scoopers No Bending Foldable Long Han | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=4.42; ROI=134.4%; Sales=200; Moderate similarity |
| 974 | THE PET STORE LONG HANDLED POOP PICKER | 32" XL Dog Pooper Scoopers No Bending Foldable Long Han | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=4.42; ROI=134.4%; Sales=200; Moderate similarity |
| 979 | PPS FOIL 3 BAKE TRAY RECTANGULAR | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=1.61; ROI=133.4%; Sales=50; Weak match |
| 980 | ROYAL MARKET BIN LINER GARDEN 10 BAG | REQUISITE NEEDS 30PK Heavy Duty Bin Liners, 100 Litre R | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=37%; NP=2.10; ROI=133.2%; Sales=200; Pack 10x makes profit negative |
| 984 | BRIGHT & HOMELY HANGERS WOODEN 2 PACK | HANGERWORLD Box of 10 Wooden 45cm Coat Clothes Garment  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=1.93; ROI=132.8%; Sales=300; Weak match |
| 987 | PRIMA CORKSCREW BOTTLE OPENER CHROME PLATED | Wing Corkscrew Wine Bottle Opener with Bottle Stopper,  | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=2.45; ROI=131.8%; Sales=300; Moderate similarity |
| 990 | LADIES KNITTED HAT WITH FAUX FUR POM-POM | Sibba Bobble Hat for Women Winter Beanie Hats Thermal F | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=2.47; ROI=131.5%; Sales=50; Moderate similarity |
| 990 | LADIES KNITTED HAT WITH FAUX FUR POM-POM | Sibba Bobble Hat for Women Winter Beanie Hats Thermal F | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=2.47; ROI=131.5%; Sales=50; Moderate similarity |
| 993 | DEKTON  PAINT SCRAPER SET 2PC | Heavy Duty Long Handle Scraper Tool â€“ Floor & Wallpap | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=3.42; ROI=130.7%; Sales=100; Insufficient evidence |
| 1003 | PRICES ALADINO JASMINE JAR | Price's Candles - Aladino Jasmine Scented Tea Lights 50 | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=50%; NP=1.97; ROI=128.1%; Sales=50; Pack 50x makes profit negative |
| 1004 | PARTY INVITES UNICORN PK20 | 36 Unicorn Party Invites Kids Party Invitations Kid's P | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=17%; NP=1.63; ROI=127.2%; Sales=100; Insufficient evidence |
| 1009 | SALT & PEPPER SHAKERS | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=1.54; ROI=126.1%; Sales=500; Moderate similarity |
| 1009 | SALT & PEPPER SHAKERS | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=1.54; ROI=126.1%; Sales=500; Moderate similarity |
| 1034 | DEKTON CIRCLIP PLIERS 5PC SET | WISEUP Pliers Set, 170mm 4-Piece Bent/Straight Internal | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=4.62; ROI=120.1%; Sales=200; Insufficient evidence |
| 1036 | AMTECH PADLOCK BRASS 20MM | Amtech T0790 Brass Small Padlocks with Keys for Luggage | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=32%; NP=1.99; ROI=119.7%; Sales=50; Partial match |
| 1041 | AMTECH ANVIL SECATEURS | Spear & Jackson 6758GS Razorsharp Geared Anvil Secateur | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=4.43; ROI=118.1%; Sales=300; Moderate similarity |
| 1041 | AMTECH ANVIL SECATEURS | Spear & Jackson 6758GS Razorsharp Geared Anvil Secateur | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=4.43; ROI=118.1%; Sales=300; Moderate similarity |
| 1042 | DEKTON RAZOR SINGLE EDGE BLADE 10PC | Derby Premium Single Edge (Half) Razor Blades â€“ 100 B | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=30%; NP=1.42; ROI=117.8%; Sales=600; Insufficient evidence |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Free Chew Dog Trea | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=64%; NP=2.33; ROI=116.0%; Sales=900; Partial match |
| 1058 | PPS 1PLY NAPKINS WHITE 250 PIECE | 500 x White Serviettes Paper Napkins (30 x 30 cm) 1-Ply | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=19%; NP=2.12; ROI=115.1%; Sales=700; Insufficient evidence |
| 1060 | WHAM CRYSTAL 32LTR SMOKE BOX & LID | Wham Crystal 5 x 32L Stackable Plastic Storage Boxes wi | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=5.02; ROI=115.1%; Sales=100; Weak match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | HEAT HOLDERS - Mens Waterproof Fleece Lined Winter Ther | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=62%; NP=6.45; ROI=114.9%; Sales=100; Partial match |
| 1073 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS SQUARE 235MM X 2 | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=1.95; ROI=112.6%; Sales=400; Insufficient evidence |
| 1083 | MASON PRECISION SCREWDRIVER SET 6 PIECES | Shall 6-Piece Precision Screwdriver Set w/ Case, 12-Siz | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=33%; NP=1.54; ROI=111.2%; Sales=50; Weak match |
| 1095 | PRIMA HEART SHAPED BAKE PAN 23CM | Prima Set Of 2 Heart Shaped Cake Tins, Romantic Grey He | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=33%; NP=1.94; ROI=108.8%; Sales=100; Weak match |
| 1107 | MUNCH CRUNCH RAWHIDE PRESSED BONE | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe  | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=1.66; ROI=106.3%; Sales=50; Weak match |
| 1108 | MUNCH CRUNCH RAWHIDE BONE NAT JUMBO | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe  | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=39%; NP=1.66; ROI=106.3%; Sales=50; Weak match |
| 1114 | SOZALI KLIPSEAL FOOD CONTAINER RECTANGLAR  500ML | 10 Ã— 500ml Plastic food containers with lids, Microwav | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=1.41; ROI=105.6%; Sales=600; Weak match |
| 1115 | THL BOWL PLASTIC REUSABLE SMALL 36PCS | MATANA 40 Small Clear Plastic Bowls (150 ml / 5 oz) â€“ | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=1.35; ROI=105.6%; Sales=100; Insufficient evidence |
| 1121 | LAV MISKET GIN GLASS 645CC PK3 | 6X Clear 645ml Misket Gin Balloon Glasses - Large Long  | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=27%; NP=4.21; ROI=104.9%; Sales=100; Pack 6x makes profit negative |
| 1122 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | Tidyz 2 X 10 Wheelie Bin Extra Large Liners 300L Black  | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=30%; NP=1.23; ROI=104.7%; Sales=700; Partial match |
| 1122 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | Tidyz 2 X 10 Wheelie Bin Extra Large Liners 300L Black  | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=30%; NP=1.23; ROI=104.7%; Sales=700; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=66%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=68%; NP=1.51; ROI=104.5%; Sales=100; Partial match |
| 1132 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | ArtesÃ  Glass 18 cm Serving Bowl, Green | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=2.33; ROI=104.3%; Sales=50; Moderate similarity |
| 1132 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | ArtesÃ  Glass 18 cm Serving Bowl, Green | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=2.33; ROI=104.3%; Sales=50; Moderate similarity |
| 1132 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | ArtesÃ  Glass 18 cm Serving Bowl, Green | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=2.33; ROI=104.3%; Sales=50; Moderate similarity |
| 1136 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCKER 1 LITRE(SOLD | Kilrock SLAM - Sink and Plughole Bathroom Drain Unblock | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=4.12; ROI=102.6%; Sales=50; Partial match |
| 1140 | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 1.1L | Addis Clip Tight Food Storage Container Large 5.3 Litre | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=35%; NP=2.36; ROI=102.0%; Sales=200; Partial match |
| 1143 | ROLSON BIKE INNER TUBE 27.5X2.1-2-5 | Continental MTB 27.5" x 1.75-2.5 Mountain Bike Inner Tu | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=2.73; ROI=101.8%; Sales=400; Weak match |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=53%; NP=2.17; ROI=100.0%; Sales=500; Pack 3x makes profit negative |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | cli | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=53%; NP=2.17; ROI=100.0%; Sales=500; Pack 3x makes profit negative |
| 1154 | PPS PLASTIC GLASSES HALF PINT 50PCS | Plastic Half Pint Glasses 50 Pack Strong Disposable Bee | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=45%; NP=1.71; ROI=98.9%; Sales=100; Moderate similarity |
| 1154 | PPS PLASTIC GLASSES HALF PINT 50PCS | Plastic Half Pint Glasses 50 Pack Strong Disposable Bee | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=45%; NP=1.71; ROI=98.9%; Sales=100; Moderate similarity |
| 1156 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION  | Kilrock 3 X Blast Away Mould Spray 500ml | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=2.30; ROI=98.7%; Sales=200; Partial match |
| 1156 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION  | Kilrock 3 X Blast Away Mould Spray 500ml | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=2.30; ROI=98.7%; Sales=200; Partial match |
| 1162 | ADORN SALT & PEPPER SHAKER | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=1.37; ROI=98.4%; Sales=500; Moderate similarity |
| 1162 | ADORN SALT & PEPPER SHAKER | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=1.37; ROI=98.4%; Sales=500; Moderate similarity |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measuring Jug | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=59%; NP=1.25; ROI=98.0%; Sales=50; Partial match |
| 1166 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=4.25; ROI=97.8%; Sales=400; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOON 4PC ASSORTED | First Steps 8 Baby Food Freezer Cubes Tray 70ml POTS BP | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=1.29; ROI=97.4%; Sales=50; Partial match |
| 1173 | VFM EMULSION MATT  PAINT WHITE 5L | Dulux Walls & Ceilings Matt Emulsion Paint - Pure Brill | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=5.20; ROI=97.3%; Sales=200; Moderate similarity |
| 1173 | VFM EMULSION MATT  PAINT WHITE 5L | Dulux Walls & Ceilings Matt Emulsion Paint - Pure Brill | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=5.20; ROI=97.3%; Sales=200; Moderate similarity |
| 1173 | VFM EMULSION MATT  PAINT WHITE 5L | Dulux Walls & Ceilings Matt Emulsion Paint - Pure Brill | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=5.20; ROI=97.3%; Sales=200; Moderate similarity |
| 1177 | BLACKSPUR LONG LINK CHAIN 2.5MM X2.5M | Stainless Steel Chains, 5 Metre Heavy Duty Chain Links, | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=1.46; ROI=96.9%; Sales=100; Insufficient evidence |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | Codex very high | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | Opus | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1184 | NAIL DRYING SPRAY | Demert Nail Enamel Dryer Manicurist's Finishing Spra -  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=1.61; ROI=96.2%; Sales=500; Moderate similarity |
| 1188 | STAINLESS STEEL KETTLE 14CM 1L | Swan SK31020N Brushed Stainless Steel Jug Kettle, Cordl | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=4.86; ROI=95.5%; Sales=500; Moderate similarity |
| 1189 | GIFTMAKER NON WOVEN SHOPPING BAGS HIGHLAND COW | ECO CHIC Lightweight Foldable Reusable Shopping Bag Wat | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=43%; NP=1.24; ROI=95.5%; Sales=300; Moderate similarity |
| 1195 | CANDLE PLATE 10CM | Silver Round Metal Spike Candle Holder Pillar Candle Pl | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=40%; NP=1.58; ROI=94.6%; Sales=400; Weak match |
| 1197 | SPONTEX QUICK SPRAY MOP DUO | Spontex Quick Spray Duo Flat Spray Mop with Washable Mi | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=30%; NP=12.73; ROI=94.4%; Sales=50; Partial match |
| 1205 | BETTINA DUSTPAN AND BRUSH LARGE ASSORTED | Newman and Cole Large Garden Dustpan and Brush Set - Ou | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=1.50; ROI=93.3%; Sales=50; Moderate similarity |
| 1207 | WHEELED STORAGE BOX & LID 150LTR | Strata Heavy Duty Large Storage Box with Lid, 190L, Loc | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=13.49; ROI=92.7%; Sales=400; Weak match |
| 1237 | KINGFISHER 3PK SMALL VACUUM BAGS VBS | Vacuum Storage Bags,10 Small Space Saver Sealer Bags, V | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=30%; NP=2.71; ROI=89.0%; Sales=300; Insufficient evidence |
| 1252 | B&CO AIR FRYER HEAT RESISTANT FOOD GRIP | Silicone Oven Mitts for Air Fryer, 1 Pair Thicken Mini  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.42; ROI=86.3%; Sales=400; Moderate similarity |
| 1252 | B&CO AIR FRYER HEAT RESISTANT FOOD GRIP | Silicone Oven Mitts for Air Fryer, 1 Pair Thicken Mini  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.42; ROI=86.3%; Sales=400; Moderate similarity |
| 1263 | ESSENTIAL PLASTIC SERVING TRAY CLEAR REUSABLE 36 X 24 C | MATANA 6 Large Rectangular Serving Platters, 32x24cm -  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=1.61; ROI=83.9%; Sales=300; Weak match |
| 1266 | RCR CRYSTAL MIXOLOGY WHISKY GLASS SET ASSORTED 340ML 4  | KANARS Whiskey Glasses Set, No-Lead Crystal Whisky Glas | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=33%; NP=8.44; ROI=83.8%; Sales=50; Weak match |
| 1277 | GIFTMAKER PENGUIN SANTA SACK | Giftmaker Collection Large Christmas Santa Sack Gift St | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=39%; NP=1.15; ROI=82.8%; Sales=100; Partial match |
| 1289 | SABICHI STAINLESS STEEL 16CM SAUCEPAN | Judge Vista Stainless Steel Medium Saucepan, 16cm, 1L S | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=39%; NP=5.04; ROI=80.5%; Sales=100; Weak match |
| 1299 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower Vase - In Loving | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.99; ROI=77.7%; Sales=50; Moderate similarity |
| 1299 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower Vase - In Loving | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.99; ROI=77.7%; Sales=50; Moderate similarity |
| 1299 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower Vase - In Loving | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.99; ROI=77.7%; Sales=50; Moderate similarity |
| 1299 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower Vase - In Loving | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.99; ROI=77.7%; Sales=50; Moderate similarity |
| 1300 | PPS FOIL CONTAINER & LID SHALLOW NO.9 235x235x48MM 10 P | Large Aluminium Foil Trays Food Large Container with li | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=33%; NP=1.99; ROI=77.6%; Sales=200; Weak match |
| 1306 | APOLLO UTENSIL HOLDER WHITE | Premier Housewares Charm Utensil Jar, White | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=2.08; ROI=76.9%; Sales=100; Moderate similarity |
| 1306 | APOLLO UTENSIL HOLDER WHITE | Premier Housewares Charm Utensil Jar, White | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=2.08; ROI=76.9%; Sales=100; Moderate similarity |
| 1309 | AMTECH PICK-UP TOOL TELE MAG 5LB | Amtech S8006 3 LED telescopic torch and magnetic pick u | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=39%; NP=1.44; ROI=76.6%; Sales=100; Partial match |
| 1311 | BEAU MERMAID 12PK HAIR TIES W/ STARFISH | Hair Scrunchies, 8 Pack Shiny Metallic Scrunchies Elast | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=20%; NP=1.06; ROI=76.4%; Sales=500; Pack 8x makes profit negative |
| 1313 | CHRISTMAS CRACKER 10 X 12" SANTA AND FRIENDS | Aisszhao 6 Pack Christmas Party Crackers,Christmas Crac | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=31%; NP=3.37; ROI=76.3%; Sales=500; Pack 6x makes profit negative |
| 1322 | GLEAMAX SCRUB BRUSH 13.5CM X 8.5CM X 6.6CM | 2 Pack Multifunctional Heavy Duty Scrub Brush  Comfort | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=19%; NP=0.96; ROI=74.7%; Sales=100; Insufficient evidence |
| 1325 | TALA STAINLESS STEEL ESPRESSO SPOONS SET OF 4 | Q&A 12 Pieces 4" Stainless Steel Mini Coffee Spoons Dem | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=54%; NP=2.17; ROI=74.5%; Sales=50; Pack 3x makes profit negative |
| 1328 | SMART CHOICE PUPPY/SMALL DOG ROPE TOY 5PK | XL Dog Rope Toys for Aggressive Chewers - Set of 2 Heav | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=13%; NP=1.60; ROI=74.0%; Sales=50; Pack 2x makes profit negative |
| 1341 | DEKTON UTILTY 50PC BLADES | Heavy Duty Straight Blades | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=2.37; ROI=72.1%; Sales=100; Moderate similarity |
| 1341 | DEKTON UTILTY 50PC BLADES | Heavy Duty Straight Blades | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=2.37; ROI=72.1%; Sales=100; Moderate similarity |
| 1343 | QUEST TURBO BLENDER 2 IN 1 32129 | Quest Food Processor, 6-in-1 Chopper, Blender, Grinder, | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=33%; NP=14.08; ROI=71.9%; Sales=200; Partial match |
| 1344 | TURBO JET AIR FRESHENER / SANITISER SPRAY FRESH LINEN 5 | 4 x Mix Bundle New Scents Sovereign Car Home Office Gym | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=37%; NP=2.21; ROI=71.8%; Sales=200; Pack 4x makes profit negative |
| 1346 | NT TOILET BLOCKS 6 PACK | Power Bleach Toilet Blocks, Cistern Blocks, Bleach Toil | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=0.99; ROI=71.3%; Sales=100; Moderate similarity |
| 1346 | NT TOILET BLOCKS 6 PACK | Power Bleach Toilet Blocks, Cistern Blocks, Bleach Toil | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=0.99; ROI=71.3%; Sales=100; Moderate similarity |
| 1347 | RENTOKIL CLOTHES MOTH GLUE TRAP REFILLS 2PK | 10-Pack Clothes Moth Monitoring Traps â€“ Refill for Ro | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=2.63; ROI=71.3%; Sales=400; Weak match |
| 1355 | AMTECH VICE BABY | Amtech D2600 150mm (6") Woodworking vice | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=39%; NP=3.04; ROI=70.7%; Sales=100; Partial match |
| 1357 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 15L | Tidyz 3 Packs Of 40 White Plastic Disposable Pedal Bin  | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=48%; NP=0.89; ROI=70.2%; Sales=50; Pack 120x makes profit negative |
| 1358 | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | RCR Crystal Melodia Luxion 360 ml Tumbler & 230 ml High | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=25%; NP=7.66; ROI=70.2%; Sales=50; Partial match |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpening Stone | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=61%; NP=1.02; ROI=69.7%; Sales=50; Brand match: AMTECH |
| 1367 | PYREX CLASSIC CASSEROLE 1.3LTR | Pyrex Essentials Glass Round Casserole Dish with Lid 1. | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=47%; NP=3.70; ROI=69.6%; Sales=50; Pack 2x makes profit negative |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK SPECIAL DELIVE | Giftmaker Collection Large Christmas Santa Sack Gift St | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=60%; NP=1.04; ROI=69.4%; Sales=100; Brand match: GIFTMAKER |
| 1372 | HOBBY DIAMOND ROUND PAPER BASKET 12LTR | JVL Natural Round Seagrass Waste Paper Basket | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.74; ROI=69.3%; Sales=100; Moderate similarity |
| 1372 | HOBBY DIAMOND ROUND PAPER BASKET 12LTR | JVL Natural Round Seagrass Waste Paper Basket | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.74; ROI=69.3%; Sales=100; Moderate similarity |
| 1372 | HOBBY DIAMOND ROUND PAPER BASKET 12LTR | JVL Natural Round Seagrass Waste Paper Basket | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.74; ROI=69.3%; Sales=100; Moderate similarity |
| 1382 | STATUS UK VISITOR TRAVEL ADAPTER | Status India to UK Power Adaptor, India to UK Travel Ad | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=40%; NP=1.06; ROI=68.1%; Sales=50; Partial match |
| 1395 | SUNNEX STAINLESS STEEL DESSERT SPOONS PK12 | Spoon Set, 12-Piece Stainless Steel Dessert Spoons Dini | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=1.76; ROI=66.9%; Sales=400; Moderate similarity |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | Codex HIGH | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1411 | MASTER COOK DIE CAST CASSEROLE 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm,  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=11.25; ROI=64.9%; Sales=50; Moderate similarity |
| 1411 | MASTER COOK DIE CAST CASSEROLE 24CM | MasterClass Cast Aluminium Cream Casserole Dish, 24cm,  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=11.25; ROI=64.9%; Sales=50; Moderate similarity |
| 1412 | PANORAMA COFFEE MUG 145ML 6 PIECES | 6X Turkish Glass Tea Cups Stylish Latte Cappuccino and  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=35%; NP=2.13; ROI=64.8%; Sales=50; Weak match |
| 1418 | PRICES PILLAR CANDLE 6 INCH GREEN | Price's Candles - 6" Evergreen Pillar Candles - Smokele | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=1.32; ROI=63.9%; Sales=200; Weak match |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1423 | KINGAVON HEAD BAND WITH MOTION SENSOR & TORCH | Lumi Light Led Headband Ultra Bright 230Â° Adjustable H | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=36%; NP=3.64; ROI=63.0%; Sales=600; Weak match |
| 1426 | PAN AROMA INCENSE STICKS & HOLDER PATCHOULI PACK OF 40 | Original Satya Nag Champa Patchouli Incense Sticks  wi | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=0.91; ROI=62.9%; Sales=200; Weak match |
| 1439 | SUNNEX STAINLESS STEEL DESSERT FORKS PK12 28/03 | 12-Piece (14 cm) Stainless Steel Pastry Fork Set, Mirro | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.63; ROI=61.8%; Sales=200; Moderate similarity |
| 1439 | SUNNEX STAINLESS STEEL DESSERT FORKS PK12 28/03 | 12-Piece (14 cm) Stainless Steel Pastry Fork Set, Mirro | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.63; ROI=61.8%; Sales=200; Moderate similarity |
| 1439 | SUNNEX STAINLESS STEEL DESSERT FORKS PK12 28/03 | 12-Piece (14 cm) Stainless Steel Pastry Fork Set, Mirro | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.63; ROI=61.8%; Sales=200; Moderate similarity |
| 1462 | BRIGHT & HOMELY SCENTED TEALIGHTS 15PCE | 20pc Scented Tealights Night Candle Black Cherry 8hrs B | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=0.81; ROI=58.2%; Sales=500; Weak match |
| 1464 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas Santa Sack Gift St | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=0.93; ROI=57.8%; Sales=100; Partial match |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | Codex very high | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | Opus | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1468 | MONEY TIN BOX ASST LARGE | KAV Jumbo Large Money Tin Box (22 CM) - Multicoluor Coi | Codex samecha | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=1.19; ROI=57.7%; Sales=50; Insufficient evidence |
| 1479 | TIDYZ FOOD BAG 300PCS | 600 TidyZ Food Freezer Bags with TIe Handles. Large Kit | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=19%; NP=0.66; ROI=56.3%; Sales=400; Partial match |
| 1491 | CONCORD CRYSTAL SERIES  HIBALL PK6 | RCR 6X 396ml Crystal Glass Highball Glasses Orchestra R | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=2.63; ROI=54.9%; Sales=300; Insufficient evidence |
| 1495 | PAN AROMA FRAGRANCE OILS JUICY BERRIES / PINK ORCHID PA | MAYJAM Fragrance Oil, 100ML Orchid Blossom Aromatherapy | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=0.79; ROI=54.3%; Sales=100; Weak match |
| 1505 | EXTRASTAR LED FLASHLIGHT USB REECHARGABLE TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=31%; NP=1.95; ROI=52.0%; Sales=100; Partial match |
| 1506 | TIDYZ FREEZER BAGS 100 PCS XLLARGE | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=26%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1507 | TIDYZ FREEZER BAGS 150PCS | 100 TidyZ Large Slide Zip Freezer Bags. Resealable. Zip | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=24%; NP=0.61; ROI=52.0%; Sales=900; Partial match |
| 1514 | APOLLO BALLOON WHISK | Apollo Whisk Rainbow, silicone, 26cm, 25x6x6 | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=38%; NP=0.68; ROI=51.4%; Sales=200; Partial match |
| 1532 | PRICES PILLAR CANDLE 6 INCH RED | Price's Candles - 6" Red Pillar Candles - Smokeless Bur | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=1.01; ROI=49.2%; Sales=200; Weak match |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.90; ROI=48.3%; Sales=500; Moderate similarity |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.90; ROI=48.3%; Sales=500; Moderate similarity |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless Steel and Glas | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.90; ROI=48.3%; Sales=500; Moderate similarity |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless Steel and Glas | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.90; ROI=48.3%; Sales=500; Moderate similarity |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless Steel and Glas | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.90; ROI=48.3%; Sales=500; Moderate similarity |
| 1538 | TIDYZ CARRIERS HANDY BAGS 40 PCS 45CM x 57.5cm | Tidyz 2 Packs Of 40 Handy Bags - Carrier Bags - Fits 15 | Gemini | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=32%; NP=0.59; ROI=48.2%; Sales=200; Pack 2x makes profit negative |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fra | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=0.61; ROI=45.9%; Sales=50; Partial match |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 Orange Juice Fra | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=0.61; ROI=45.9%; Sales=50; Partial match |
| 1565 | CHEF AID STAINLESS STEEL TEA BAG SQUEEZER | Tea Bag Squeezer, Stainless Steel Holder, Tongs, Spoon, | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=0.59; ROI=45.3%; Sales=200; Weak match |
| 1568 | HAPPY BIRTHDAY TRI CUT BUNTING | Happy Birthday Bunting Banner, 6.6 Ft Hessian Cloth Vin | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=0.57; ROI=44.9%; Sales=200; Weak match |
| 1569 | SUNNEX PK4 DESSERT FORKS PLAIN | Silver 10-Piece Stainless Steel Fork Set for Dessert an | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=0.82; ROI=44.8%; Sales=100; Insufficient evidence |
| 1581 | APOLLO STAINLESS STEEL JAR OPENER 11/11 | Manual Can Openers Jar Can Opener,Adjustable Can Opener | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=39%; NP=0.93; ROI=43.6%; Sales=200; Weak match |
| 1582 | TRAVEL MAKEUP BRUSH SET W/POUCH 18PC | 10 Pcs Mini Travel Makeup Brush Set With Pouch Pink Por | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=29%; NP=0.77; ROI=43.6%; Sales=200; Pack 10x makes profit negative |
| 1586 | PPS FOIL CONTAINER & LID 260x188x68MM 10 PIECES | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=24%; NP=1.11; ROI=43.1%; Sales=400; Insufficient evidence |
| 1587 | BRIGHT & HOMELY FOIL ROASTING TRAY 525MM X 330MM X 85MM | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=1.11; ROI=43.1%; Sales=400; Insufficient evidence |
| 1592 | WORLD OF PETS SALMON STICKS DOG TREAT PK18 | SKIPPER'S Salmon Meat Sticks Dog Treats - 100% Natural  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=27%; NP=0.56; ROI=42.0%; Sales=600; Insufficient evidence |
| 1604 | ROLSON DIAGONAL CUTTING PLIERS VDE INSULATED 160MM | S&R VDE Insulated Diagonal Side Cutter 160mm â€“ 1000V  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=43%; NP=2.42; ROI=40.2%; Sales=300; Moderate similarity |
| 1604 | ROLSON DIAGONAL CUTTING PLIERS VDE INSULATED 160MM | S&R VDE Insulated Diagonal Side Cutter 160mm â€“ 1000V  | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=43%; NP=2.42; ROI=40.2%; Sales=300; Moderate similarity |
| 1620 | BEAU MERMAID 4PK PEARL WAVE  HAIR CLIPS 2 ASSTD COL | Pearl Hair Clip - ShiningUU 2-Pack 3.3cm Large Snap Bar | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=22%; NP=0.53; ROI=38.2%; Sales=50; Insufficient evidence |
| 1624 | ROYALFORD STAINLESS STEEL PESTLE AND MORTAR 2.5"X 2.10" | Bekith Mortar and Pestle Sets 18/8 Brushed Stainless St | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=1.58; ROI=38.1%; Sales=200; Weak match |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combination Spanner Set | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=56%; NP=2.15; ROI=37.8%; Sales=100; Brand match: DRAPER |
| 1642 | APOLLO POTATO MASHER STAINLESS STEEL FOLDING | Potato Mashers, Joyoldelf Potato Masher Stainless Steel | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.06; ROI=36.5%; Sales=400; Moderate similarity |
| 1642 | APOLLO POTATO MASHER STAINLESS STEEL FOLDING | Potato Mashers, Joyoldelf Potato Masher Stainless Steel | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.06; ROI=36.5%; Sales=400; Moderate similarity |
| 1642 | APOLLO POTATO MASHER STAINLESS STEEL FOLDING | Potato Mashers, Joyoldelf Potato Masher Stainless Steel | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.06; ROI=36.5%; Sales=400; Moderate similarity |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | Codex very high | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | Opus | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | opus2 | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1648 | BRIGHT & HOMELY PLUNGER WOODEN HANDLE HEAVY DUTY LARGE | Large Black Toilet Plunger 150mm 6 Inch Cup with 430mm  | Codex samecha | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=0.97; ROI=35.7%; Sales=50; Insufficient evidence |
| 1654 | EXPRESS DECANTER SQUARE 1160ML | BarCraft Wine Decanter, Wine Aeration Glass, Wide-Base  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=1.04; ROI=35.3%; Sales=50; Insufficient evidence |
| 1662 | WAX MELT NAGCHAMPA 6PCS | Nag Champa - Highly Scented 100% Soy Wax Snapbar | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=0.47; ROI=34.2%; Sales=50; Weak match |
| 1664 | TIDYZ RUBBLE BAG HEAVY DUTY 7BAGS 32L | 20 TidyZ Heavy-Duty Rubble Sacks. Made from 100% Recycl | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=25%; NP=0.41; ROI=34.0%; Sales=100; Partial match |
| 1668 | MINKY ALL PURPOSE CLOTH PK10 | Minky Anti-Bacterial Cleaing Pad  3 Pack  Reusable Mi | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=21%; NP=0.59; ROI=33.6%; Sales=700; Pack 3x makes profit negative |
| 1670 | CASA & CASA CLASSICO STAINLESS STEEL KNIFE & GADGET HOL | Joeji's Kitchen Universal Knife Block Without Knives wi | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=2.29; ROI=33.6%; Sales=50; Weak match |
| 1672 | PPS FOOD CONTAINERS & LIDS PLASTIC RECTANGULAR 50PC 100 | Superior Takeaway Containers with Lids â€“ 20 Pcs Durab | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=11%; NP=1.77; ROI=33.4%; Sales=100; Pack 20x makes profit negative |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clip | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.26; ROI=33.1%; Sales=100; Partial match |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clip | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.26; ROI=33.1%; Sales=100; Partial match |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Ironing Board Clip | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=1.26; ROI=33.1%; Sales=100; Partial match |
| 1681 | DRAPER SINK PLUNGER 135MM | Draper Drain Rod Plunger Attachment 4''  Heavy Duty Ou | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=37%; NP=0.82; ROI=32.2%; Sales=50; Partial match |
| 1684 | PPS FOIL PLATTERS 550X362X30MM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=0.41; ROI=31.9%; Sales=50; Weak match |
| 1687 | BUTTERFLY AND RAINBOW HAIR CLIPS 4PC | Toddler Girls Butterfly Snap Clips,Lovely Unicorn Rabbi | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=0.44; ROI=31.9%; Sales=300; Weak match |
| 1689 | APOLLO MARBLE BOARD BLACK 46x23CM | Silk Route Home Black Granite Chopping Board 40 x 30cm | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=3.47; ROI=31.8%; Sales=50; Moderate similarity |
| 1694 | BRIGHT & HOMELY REINFORCED GARDEN HOSE PIPE 30M | Faithfull 30M (98ft) Reinforced Hose 12.7 mm (1/2 Inch) | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=2.46; ROI=31.5%; Sales=100; Moderate similarity |
| 1694 | BRIGHT & HOMELY REINFORCED GARDEN HOSE PIPE 30M | Faithfull 30M (98ft) Reinforced Hose 12.7 mm (1/2 Inch) | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=2.46; ROI=31.5%; Sales=100; Moderate similarity |
| 1696 | EXTRASTAR EXTENSION LEAD 6 GANG 1M BLACK | ExtraStar 6 Way Extension Leads with Surge Protection,  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.08; ROI=31.3%; Sales=200; Partial match |
| 1696 | EXTRASTAR EXTENSION LEAD 6 GANG 1M BLACK | ExtraStar 6 Way Extension Leads with Surge Protection,  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.08; ROI=31.3%; Sales=200; Partial match |
| 1697 | EXTRASTAR EXTENSION LEAD 6 GANG 1M WHITE | ExtraStar 6 Way Extension Leads with Surge Protection,  | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.08; ROI=31.3%; Sales=500; Partial match |
| 1697 | EXTRASTAR EXTENSION LEAD 6 GANG 1M WHITE | ExtraStar 6 Way Extension Leads with Surge Protection,  | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=1.08; ROI=31.3%; Sales=500; Partial match |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1711 | MASTERCOOK CASSEROLE SET 20-22-24CM 3 PIECES | Amazon Basics 3-Piece Stainless Steel Space Saving Indu | opus2 | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=5.42; ROI=30.0%; Sales=50; Weak match |
| 1711 | MASTERCOOK CASSEROLE SET 20-22-24CM 3 PIECES | Amazon Basics 3-Piece Stainless Steel Space Saving Indu | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=5.42; ROI=30.0%; Sales=50; Weak match |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.86; ROI=29.1%; Sales=300; Partial match |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.86; ROI=29.1%; Sales=300; Partial match |
| 1727 | INCENSE STICKS SACRED WOOD PACK OF 12 | Natural Incense Sticks Multipack Variants - 5 (90 gms)  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=1.51; ROI=28.8%; Sales=900; Insufficient evidence |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | Codex HIGH | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20 x 17 cm â€“ 1 L | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=64%; NP=1.04; ROI=28.5%; Sales=50; Brand match: PYREX |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | Codex HIGH | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | cli | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=57%; NP=0.91; ROI=27.9%; Sales=50; Brand match: KILNER |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tub, 5 Litre | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=75%; NP=1.71; ROI=27.9%; Sales=50; Partial match |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | webapp gpt | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1754 | CHEF AID BEAN SLICER | Krisk French Style Bean Slicer - HA43 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=53%; NP=0.39; ROI=27.0%; Sales=100; Moderate similarity |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casseroles high resis | Codex HIGH | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=56%; NP=3.19; ROI=26.9%; Sales=300; Pack 3x makes profit negative |
| 1757 | ROYALFORD MORTAR AND PESTLE STAINLESS STEEL 2.6"x2.25" | Bekith Mortar and Pestle Sets 18/8 Brushed Stainless St | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=1.22; ROI=26.8%; Sales=200; Moderate similarity |
| 1757 | ROYALFORD MORTAR AND PESTLE STAINLESS STEEL 2.6"x2.25" | Bekith Mortar and Pestle Sets 18/8 Brushed Stainless St | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=1.22; ROI=26.8%; Sales=200; Moderate similarity |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=70%; NP=0.74; ROI=26.7%; Sales=100; Brand match: ROLSON |
| 1773 | PPS POCKET TISSUES 3PLY 10S PK10 | Handy Pocket 3ply Tissues, Packs of 10 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=0.29; ROI=26.0%; Sales=100; Moderate similarity |
| 1773 | PPS POCKET TISSUES 3PLY 10S PK10 | Handy Pocket 3ply Tissues, Packs of 10 | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=57%; NP=0.29; ROI=26.0%; Sales=100; Moderate similarity |
| 1782 | MINKY BRITES FLAT SCOURING PAD 4PC | Minky Anti-Bacterial Cleaing Pad  3 Pack  Reusable Mi | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=19%; NP=0.47; ROI=25.0%; Sales=700; Pack 3x makes profit negative |
| 1784 | SOFTESSE FAMILY FACIAL TISSUES PK24 | 36 x Boxes Ultra Soft Luxurious 100 White Facial Family | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=26%; NP=3.73; ROI=24.7%; Sales=200; Pack 36x makes profit negative |
| 1785 | ROLSON  ADJUSTABLE WRENCH 3PC SET 6,8,10" | Shall 3-Piece Adjustable Wrench Set, 10/8/6 Inch Cr-V S | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=29%; NP=1.96; ROI=24.7%; Sales=100; Insufficient evidence |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 40x34x4 | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=63%; NP=0.88; ROI=24.0%; Sales=50; Brand match: APOLLO |
| 1796 | KILNER PRESERVE JAR 0.25LTR SCREW LID | Kilner Preserve Jar 0.25L (250ml) Round Glass Screw Top | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=49%; NP=0.40; ROI=23.0%; Sales=50; Moderate similarity |
| 1797 | APOLLO SILICON WHISK SPLASH 25CM | Apollo Whisk Rainbow, silicone, 26cm, 25x6x6 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=47%; NP=0.37; ROI=22.8%; Sales=200; Moderate similarity |
| 1800 | PPS FOIL CONTAINER & LID DEEP NO.9 235x235x58MM 10 PIEC | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=28%; NP=0.68; ROI=22.6%; Sales=400; Insufficient evidence |
| 1805 | YALE ESSENTIALS DEADLOCK P/BRASS 64MM | Yale British Standard 5 Lever Mortice Deadlock, High Se | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=36%; NP=1.62; ROI=22.1%; Sales=200; Partial match |
| 1808 | BEAUFORT MEASURE ULTIMATE JUG 2LTR | Beaufort - 2 Litre Clear Plastic Measuring Jug | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=0.25; ROI=21.5%; Sales=200; Moderate similarity |
| 1810 | BRIGHT & HOMELY HANGERS WOODEN 5 PACK | HANGERWORLD Box of 10 Wooden 45cm Coat Clothes Garment  | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=31%; NP=0.59; ROI=21.4%; Sales=300; Weak match |
| 1813 | SMART CHOICE GLOW IN THE DARK ROPE DOG TOY 6 ASSTD | Zip witn 6 String Toy for Pets, Glow in The Dark Rope L | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=0.46; ROI=21.3%; Sales=50; Moderate similarity |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | Codex HIGH | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=82%; NP=0.89; ROI=20.9%; Sales=50; Brand match: FALCON |
| 1830 | SOZALI SQUARE FOOD BOX 700ML 2PC | Sistema Ultra Airtight Pantry Storage Container  700 m | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=25%; NP=0.35; ROI=20.3%; Sales=100; Insufficient evidence |
| 1838 | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4PC | Minky Anti-Bacterial Cleaing Pad  3 Pack  Reusable Mi | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=31%; NP=0.40; ROI=20.1%; Sales=700; Pack 3x makes profit negative |
| 1839 | ROLSON  CABEL CUTTING PLIERS VDE INSULATED 160MM | S&R VDE Insulated Diagonal Side Cutter 160mm â€“ 1000V  | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=1.40; ROI=19.9%; Sales=300; Moderate similarity |
| 1840 | PPS FOIL PIZZA 2 PLATTERS | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=30%; NP=0.28; ROI=19.7%; Sales=50; Weak match |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | Codex very high | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and magnetic pick u | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=64%; NP=0.54; ROI=19.2%; Sales=100; Brand match: AMTECH |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex very high | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | cli | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=56%; NP=0.51; ROI=18.9%; Sales=200; Partial match |
| 1861 | ROYALFORD STAINLESS STEEL PESTLE AND MORTAR 2.75"X 2.75 | Bekith Mortar and Pestle Sets 18/8 Brushed Stainless St | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=0.89; ROI=18.2%; Sales=200; Weak match |
| 1866 | PPS BAGASSE WHITE PLATE 26CM  50PC | Disposable Paper Plate 10 Inch Heavy Duty Strong Bagass | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=24%; NP=0.63; ROI=17.9%; Sales=200; Insufficient evidence |
| 1867 | PAN AROMA INCENSE STICKS & HOLDER SANDALWOOD PACK OF 40 | Satya Nag Champa Sandalwood Incense Sticks  x3 pack   | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=30%; NP=0.26; ROI=17.8%; Sales=100; Weak match |
| 1872 | ELF ARRIVAL ENVELOPE OUTFIT | Christmas Naughty Elf Arrival Clothes - Plush Snowman O | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=0.37; ROI=17.1%; Sales=50; Moderate similarity |
| 1878 | KILROCK SERVICE-PRO COFFEE MACHINE DESCALER 150ML(SOLD  | Kilrock Service Pro Coffee Machine Descaler & Cleaner 2 | Codex HIGH | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=0.63; ROI=16.4%; Sales=100; Partial match |
| 1878 | KILROCK SERVICE-PRO COFFEE MACHINE DESCALER 150ML(SOLD  | Kilrock Service Pro Coffee Machine Descaler & Cleaner 2 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=0.63; ROI=16.4%; Sales=100; Partial match |
| 1916 | PAN AROMA PLUG-IN REFILL PURE COTTON PACK OF 2 | Febreze Ambi Pur 3Volution Air Freshener Plug-in Diffus | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=43%; NP=0.18; ROI=13.9%; Sales=300; Moderate similarity |
| 1919 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS | Rolson 51 pc Screwdriver & Bit Set (Chrome Vanadium Ste | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=32%; NP=0.43; ROI=13.8%; Sales=400; Weak match |
| 1921 | BLOOME MINI GEL BURST AIR FRESHENER 3PK | Jelly Belly 15710A 3D Gel Mini Vent Air Freshener Duo P | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=0.19; ROI=13.7%; Sales=300; Moderate similarity |
| 1921 | BLOOME MINI GEL BURST AIR FRESHENER 3PK | Jelly Belly 15710A 3D Gel Mini Vent Air Freshener Duo P | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=0.19; ROI=13.7%; Sales=300; Moderate similarity |
| 1921 | BLOOME MINI GEL BURST AIR FRESHENER 3PK | Jelly Belly 15710A 3D Gel Mini Vent Air Freshener Duo P | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=51%; NP=0.19; ROI=13.7%; Sales=300; Moderate similarity |
| 1926 | PREMIER FLICKABRIGHT GLASS SPHERE CANDLE 10CM | Premier Decorations Red LED Flickabrights Wax Candle Ba | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=40%; NP=0.51; ROI=13.1%; Sales=50; Weak match |
| 1927 | PRIMA SALT AND PEPPER SHAKER 8X4.5CM | Juvale Salt and Pepper Shakers Stainless Steel and Glas | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.32; ROI=13.0%; Sales=500; Moderate similarity |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1935 | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550ML | Addis Clip Tight Food Storage Container Large 4.2 Litre | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=34%; NP=0.24; ROI=12.6%; Sales=300; Weak match |
| 1940 | MEMORIAL PLASTIC SPIKE SPECIAL MUM & DAD | Mum And Dad - Plastic Spike Memorial Grave Vase With Bu | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=48%; NP=0.25; ROI=12.4%; Sales=50; Moderate similarity |
| 1946 | HAPPY BIRTHDAY BANNER | Happy Birthday Banner and Decoration - Blue Balloons, R | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=37%; NP=0.15; ROI=11.7%; Sales=600; Weak match |
| 1948 | AIRWICK FRESHMATIC REFILL PINK SWEET PEA PK4 | Air Wick Automatic Air Freshener Freshmatic Spray Refil | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=1.03; ROI=11.5%; Sales=600; Insufficient evidence |
| 1960 | PPS FOIL ROASTING 3 DISHES | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44cm x 29cm dispo | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=39%; NP=0.17; ROI=11.1%; Sales=50; Weak match |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=59%; NP=0.36; ROI=10.1%; Sales=100; Brand match: SMART CHOICE |
| 1971 | MASTERCLASS SALT/PAPPER MILL BLACK | MasterClass Pepper Mill or Salt Grinder with Interchang | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=0.42; ROI=10.1%; Sales=100; Moderate similarity |
| 1972 | CARRIERS BAGS SMALL PK100 | 100 White Plastic Carrier Bags â€“ Vest-Style Bags with | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=23%; NP=0.13; ROI=10.0%; Sales=50; Insufficient evidence |
| 1973 | VIVID BIN FRESHENER PK2 | Vivid 6 x Bin Freshener Smelling FRESH Dustbins Swing P | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=41%; NP=0.14; ROI=10.0%; Sales=100; Moderate similarity |
| 1979 | FALCON ENAMEL ROASTER ROUND 20CM | Barmans BYX0B0A6289 Enamel Roaster with Lid, White, 20c | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=55%; NP=0.86; ROI=9.1%; Sales=50; Moderate similarity |
| 1979 | FALCON ENAMEL ROASTER ROUND 20CM | Barmans BYX0B0A6289 Enamel Roaster with Lid, White, 20c | opus2 | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=55%; NP=0.86; ROI=9.1%; Sales=50; Moderate similarity |
| 1984 | CARRIERS BAGS CHEETAH PK100 | 100 White Plastic Carrier Bags â€“ Vest-Style with Hand | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=21%; NP=0.26; ROI=8.8%; Sales=400; Insufficient evidence |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1989 | KINGFISHER 30M REINFORCED HOSE PIPE | Faithfull 30M (98ft) Reinforced Hose 12.7 mm (1/2 Inch) | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=44%; NP=0.80; ROI=8.5%; Sales=100; Moderate similarity |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 2005 | PPS FOIL CONTAINERS 1/3 GASTRO WITH LIDS 318X178X55MM P | Caterserve 10 Aluminium Foil Trays with Lids - Large Ti | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=26%; NP=0.25; ROI=7.2%; Sales=400; Insufficient evidence |
| 2009 | EXTRASTAR EXTENSION LEAD 2 GANG 2M WHITE | EXTRASTAR 2 Gang Extension Lead, 2 Metre Extension Cabl | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=50%; NP=0.25; ROI=7.0%; Sales=50; Moderate similarity |
| 2012 | MULTI COLOURED HAIR BANDS 8PK | Elastic Hair Bands, 1500 pcs Mini Rubber Bands, Multico | webapp gpt | NEEDS VERIFICATION | OTHER / LOW PRIORITY | INCORRECT | Sim=20%; NP=0.10; ROI=6.8%; Sales=400; Insufficient evidence |
| 2025 | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Oaktree UK 9ft Banner Happy 8th Birthday Pink | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=58%; NP=0.07; ROI=5.7%; Sales=50; Moderate similarity |
| 2026 | HAPPY 8TH BIRTHDAY BANNER 9FT | Oaktree UK 9ft Banner Happy 8th Birthday Pink | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=54%; NP=0.07; ROI=5.7%; Sales=50; Moderate similarity |
| 2042 | SISTEMA TO GO BREAKFAST BOX | Sistema Klip It Colour Accents Breakfast To Go Containe | Gemini | NEEDS VERIFICATION | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=0.18; ROI=4.7%; Sales=100; Weak match |
| 2060 | APOLLO RB CUTTING BOARD 30X20 | Apollo 3245 RB Bread Board 30cm Round, Multi-Colour, 30 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=46%; NP=0.16; ROI=3.7%; Sales=100; Moderate similarity |
| 2062 | WHAM CRYSTAL 80LTR CLEAR BOX & LID | CRYSTAL 80L BOX & LID CLEAR 11315 | Gemini | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=63%; NP=0.23; ROI=3.5%; Sales=100; Moderate similarity |
| 2062 | WHAM CRYSTAL 80LTR CLEAR BOX & LID | CRYSTAL 80L BOX & LID CLEAR 11315 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=63%; NP=0.23; ROI=3.5%; Sales=100; Moderate similarity |
| 2064 | EASY SPRAY 4IN1 MULTI PURPOSE CLEANER 750ML PK6 | Astonish Special Aromatic Edition Multi-Purpose Anti-Ba | webapp gpt | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=42%; NP=0.18; ROI=3.1%; Sales=300; Moderate similarity |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | Codex very high | NEEDS VERIFICATION | VERIFIED | INCORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pa | webapp gpt | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=63%; NP=0.19; ROI=1.9%; Sales=50; Pack 4x makes profit negative |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | Codex very high | NEEDS VERIFICATION | VERIFIED | INCORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | cli | NEEDS VERIFICATION | VERIFIED | INCORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2083 | WHAM MEASURING JUG 2LTR | Wham Cuisine 2L Clear Measuring Jug,JNS_453403 | Opus | NEEDS VERIFICATION | NEEDS VERIFICATION | CORRECT | Sim=52%; NP=0.02; ROI=1.5%; Sales=100; Moderate similarity |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | Opus | NEEDS VERIFICATION | FILTERED OUT | INCORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=61%; NP=0.02; ROI=0.8%; Sales=50; Brand match: ROLSON |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | Opus | NEEDS VERIFICATION | HIGHLY LIKELY | ACCEPTABLE | Sim=67%; NP=0.01; ROI=0.3%; Sales=100; Brand match: SMART CHOICE |

### FILTERED OUT (claimed, n=221)

| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |
|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|
| 127 | SQUARE SPICE JAR BLACK/WHITE | Square Spice Jars Set of 24 with Bamboo Lids, Shaker In | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=25%; NP=10.72; ROI=893.7%; Sales=200; Pack 24x makes profit negative |
| 147 | JAUNTY PARTYWARE CONFETTI PARTY BOWLS 6" 12PK | Jaunty 24pk Bulk Party Flashing Glasses - Neon Rave Acc | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=19%; NP=10.42; ROI=783.4%; Sales=300; Insufficient evidence |
| 281 | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | Superior 20-Pack 16oz Microwave Containers With Lids â€ | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=27%; NP=5.30; ROI=477.6%; Sales=100; Partial match |
| 286 | Cat Lead & Harness | Cat Harness and Lead Set, Escape-Proof Kitten Harness w | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=17%; NP=6.02; ROI=470.4%; Sales=50; Insufficient evidence |
| 292 | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ | Superior 32oz Food Containers With Lids â€“ 20-Pack Dur | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=26%; NP=5.64; ROI=462.7%; Sales=100; Partial match |
| 313 | DRAPER HSS DRILL BIT 1.5 MM | Draper 18551 Combined HSS and Masonry Drill Bit Set, Bl | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=50%; NP=5.16; ROI=440.6%; Sales=100; Pack 17x makes profit negative |
| 313 | DRAPER HSS DRILL BIT 1.5 MM | Draper 18551 Combined HSS and Masonry Drill Bit Set, Bl | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=50%; NP=5.16; ROI=440.6%; Sales=100; Pack 17x makes profit negative |
| 313 | DRAPER HSS DRILL BIT 1.5 MM | Draper 18551 Combined HSS and Masonry Drill Bit Set, Bl | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=50%; NP=5.16; ROI=440.6%; Sales=100; Pack 17x makes profit negative |
| 320 | Cat Litter Tray | Cat Litter Tray Box, Litter Box, Plastic Cat Open Top L | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=19%; NP=7.25; ROI=433.9%; Sales=600; Insufficient evidence |
| 423 | GLASS VASE 13X24CM | Glass Flower Vase, 24cm Hight Modern Minimalist FlowerV | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=12%; NP=12.62; ROI=337.4%; Sales=50; Insufficient evidence |
| 511 | LAV NECTAR TUMBLER 3PC 280ML | LAV 12x 280ml Nectar Glass Tumblers - Dishwasher Safe K | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=28%; NP=7.66; ROI=287.0%; Sales=50; Insufficient evidence |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainless Steel, Silv | cli | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=67%; NP=3.97; ROI=285.9%; Sales=600; Partial match |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainless Steel, Silv | webapp gpt | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=67%; NP=3.97; ROI=285.9%; Sales=600; Partial match |
| 542 | GLASS BOTTLE 120ML | Glass Shot Bottles with Lids - 12 Pack 120ml Empty Mini | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=18%; NP=3.04; ROI=274.3%; Sales=200; Pack 12x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering T | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=3.90; ROI=269.3%; Sales=50; Pack 10x makes profit negative |
| 566 | WICKED STATIONERY BACKPACK | WICKED Backpack, Glinda And Elphaba Girls Backpack, Gir | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=27%; NP=7.72; ROI=260.8%; Sales=400; Insufficient evidence |
| 576 | HEM INCENSE STICKS LEMON | HEM Incense Sticks - 18 unique and premium flavours - S | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=22%; NP=6.41; ROI=255.2%; Sales=50; Variant mismatch: Scent: ['LEMON'] vs ['LEMON', 'LAVENDER'] |
| 579 | Dog Figure '8' Knot Ball Rope Toy(12/48) | Dog Pet Puppy Chew Toys for Teething Boredom Dogs Rope  | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=30%; NP=3.24; ROI=252.9%; Sales=800; Insufficient evidence |
| 595 | FESTIVE MAGIC SANT SLEIGH FELT BUCKET | Festive Childrens Holding DIY Sleigh - Large Xmas Home  | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=26%; NP=4.84; ROI=248.3%; Sales=300; Insufficient evidence |
| 649 | PETS PLAY RUBBER BALLS | Pets & Play Squeaky Dog Ball 6 Pack  Upgraded Durable  | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=20%; NP=4.04; ROI=226.7%; Sales=900; Pack 6x makes profit negative |
| 658 | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L | Tidyz 6 Packs Of 40 White Plastic Bin Bags - Fits 15L P | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=39%; NP=2.73; ROI=223.5%; Sales=500; Pack 240x makes profit negative |
| 659 | TIDYZ COMPOSTABLE 15 BAGS 10LTR | Tidyz 6 Packs Of 40 White Plastic Bin Bags - Fits 15L P | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=32%; NP=2.73; ROI=223.5%; Sales=500; Pack 16x makes profit negative |
| 659 | TIDYZ COMPOSTABLE 15 BAGS 10LTR | Tidyz 6 Packs Of 40 White Plastic Bin Bags - Fits 15L P | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=32%; NP=2.73; ROI=223.5%; Sales=500; Pack 16x makes profit negative |
| 686 | LED FIRE FLAME LIGHT 7.5X9CM | LED Flame Light Fire Effect Light for Indoor Outdoor Si | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=16%; NP=5.43; ROI=211.1%; Sales=50; Insufficient evidence |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Codex HIGH | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â£2.19) | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | webapp gpt | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=55%; NP=2.93; ROI=207.8%; Sales=500; Brand match: BACOFOIL |
| 718 | EXTRASTAR LED FLASHLIGHT BATTERY TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=28%; NP=4.50; ROI=196.6%; Sales=100; Partial match |
| 719 | EXTRASTAR LED FLASHLIGHT TORCH | EXTRASTAR Head Torch Rechargeable, Headlight with 3 Lig | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=27%; NP=4.50; ROI=196.6%; Sales=100; Partial match |
| 720 | BRIGHT & HOMELY CITRONELLA TEALIGHT CANDLES LARGE 4 PAC | Price's Candles Citronella Tealights - 100 Pack | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=62%; NP=2.72; ROI=196.0%; Sales=200; Pack 25x makes profit negative |
| 721 | CITRONELLA GARDEN TORCH ASSORTED | CUQOO 1L Scented Citronella Oil for Garden Burners - 2  | Codex samecha | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=27%; NP=4.49; ROI=195.9%; Sales=100; Insufficient evidence |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=60%; NP=2.09; ROI=190.3%; Sales=200; Partial match |
| 784 | VINERS EVERYDAY PURITY 4PC DINNER KNIFE | Viners Everyday Breeze 16 Piece 18/0 Silver Stainless S | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=6.77; ROI=175.9%; Sales=50; Pack 16x makes profit negative |
| 784 | VINERS EVERYDAY PURITY 4PC DINNER KNIFE | Viners Everyday Breeze 16 Piece 18/0 Silver Stainless S | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=6.77; ROI=175.9%; Sales=50; Pack 16x makes profit negative |
| 786 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=51%; NP=5.47; ROI=174.9%; Sales=400; Partial match |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE CONTAINER WITH | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=62%; NP=2.03; ROI=173.5%; Sales=200; Partial match |
| 797 | LAV GLASS WHISKEY TUMBLER 345ML 3PCE | Lav Coral Tumbler Glasses. Coloured Base (Pack of 6) Wh | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=4.23; ROI=173.4%; Sales=200; Pack 6x makes profit negative |
| 817 | EXFOLIATING GLOVES PAIR | Exfoliating Wash Gloves, Shower Scrub Gloves/Loofah, Na | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=25%; NP=2.35; ROI=169.4%; Sales=400; Insufficient evidence |
| 842 | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=51%; NP=2.86; ROI=163.5%; Sales=100; Pack 6x makes profit negative |
| 842 | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=51%; NP=2.86; ROI=163.5%; Sales=100; Pack 6x makes profit negative |
| 844 | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=28%; NP=5.00; ROI=162.7%; Sales=200; Partial match |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rollers Salon Hairdr | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=1.59; ROI=159.5%; Sales=200; Pack 6x makes profit negative |
| 856 | PAN AROMA CANDLE 85G LIME GINGER | Pan Aroma Orange Decorative Holder & Scented Candle, Sa | Codex samecha | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=38%; NP=2.56; ROI=159.3%; Sales=50; Weak match |
| 915 | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=2.73; ROI=145.3%; Sales=100; Pack 6x makes profit negative |
| 915 | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC 6PC | Pasabahce Istanbul tea glass, set of 6, drinking glasse | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=2.73; ROI=145.3%; Sales=100; Pack 6x makes profit negative |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mul | Opus | FILTERED OUT | VERIFIED | INCORRECT | Sim=57%; NP=16.55; ROI=141.0%; Sales=200; Exact EAN match |
| 977 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=3.28; ROI=133.8%; Sales=700; Partial match |
| 986 | CHRISTMAS GIFT BAG PK3 BURGANDY JOY | Christmas Burgundy Gift Bags Medium for Present,6Pcs Wi | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=25%; NP=2.66; ROI=132.2%; Sales=50; Pack 6x makes profit negative |
| 986 | CHRISTMAS GIFT BAG PK3 BURGANDY JOY | Christmas Burgundy Gift Bags Medium for Present,6Pcs Wi | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=25%; NP=2.66; ROI=132.2%; Sales=50; Pack 6x makes profit negative |
| 1006 | PARTY INVITES BIRTHDAY PK20 | Party Invitations Pack of 36. Blue Starburst Themed Inv | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=25%; NP=1.62; ROI=127.0%; Sales=100; Pack 36x makes profit negative |
| 1020 | BBQ KITCHEN GLOVE 32CM 3ASS | BBQ Gloves, 1472Â°F Heat Resistant Gloves Fireproof Mit | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=20%; NP=4.13; ROI=123.7%; Sales=100; Insufficient evidence |
| 1026 | LAV WHISKEY TUMBLER 3PCS | Lav Coral Tumbler Glasses. Coloured Base (Pack of 6) Wh | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=3.67; ROI=122.3%; Sales=200; Insufficient evidence |
| 1088 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=3.00; ROI=109.8%; Sales=700; Partial match |
| 1100 | CAR ASHTRAY | Car Ashtray, Portable Ashtray with Lid Smell Proof, Aut | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=13%; NP=1.50; ROI=107.8%; Sales=100; Insufficient evidence |
| 1109 | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=32%; NP=4.16; ROI=106.3%; Sales=200; Partial match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | Codex HIGH | FILTERED OUT | VERIFIED | INCORRECT | Sim=75%; NP=1.51; ROI=104.5%; Sales=100; Exact EAN match |
| 1136 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCKER 1 LITRE(SOLD | Kilrock SLAM - Sink and Plughole Bathroom Drain Unblock | Opus | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=46%; NP=4.12; ROI=102.6%; Sales=50; Partial match |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=53%; NP=2.17; ROI=100.0%; Sales=500; Pack 3x makes profit negative |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L | Bacofoil 3 x Zipper Small All Purpose Bags Food Freezin | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=53%; NP=2.17; ROI=100.0%; Sales=500; Pack 3x makes profit negative |
| 1152 | DRAPER HEX KEY SET METRIC DIY 8 PC | Draper 10 Piece T-Handle Hexagon Allen Key Set  Metric | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=24%; NP=2.66; ROI=99.2%; Sales=500; Pack 10x makes profit negative |
| 1166 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expanding Foam Handhe | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=52%; NP=4.25; ROI=97.8%; Sales=400; Partial match |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M | 3 x Easy Cut Refill Kitchen Foil 300mm, 15m | cli | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=2.90; ROI=96.4%; Sales=500; Pack 3x makes profit negative |
| 1234 | YOGA ORNAMENT IN BAG 6CM | Yoga Gift for Yoga Instructor Yoga Accessories Women Fu | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=21%; NP=1.47; ROI=89.3%; Sales=200; Insufficient evidence |
| 1240 | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=3.06; ROI=88.6%; Sales=200; Partial match |
| 1240 | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR | Superior Foil Containers with Lids â€“ 9x13 Inches Stur | opus2 | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=3.06; ROI=88.6%; Sales=200; Partial match |
| 1262 | GLASS MUG DELI 270ML ZB229 6PK | Glass Coffee Mugs Set of 6 Heat Resistant Glass Cups wi | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=18%; NP=3.70; ROI=84.0%; Sales=100; Pack 6x makes profit negative |
| 1303 | CORAL EASY COATER 4" & FREE BRUSH | Coral 10501 Easy Coater Paint Kit with Headlock and Min | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=42%; NP=2.07; ROI=77.1%; Sales=500; Pack 12x makes profit negative |
| 1303 | CORAL EASY COATER 4" & FREE BRUSH | Coral 10501 Easy Coater Paint Kit with Headlock and Min | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=42%; NP=2.07; ROI=77.1%; Sales=500; Pack 12x makes profit negative |
| 1350 | PAN AROMA POTPOURRI ASSORTED | Pan Aroma Set Of 4 Pot Pourri Fragrance - Berries Fluff | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=43%; NP=1.03; ROI=71.0%; Sales=200; Pack 4x makes profit negative |
| 1350 | PAN AROMA POTPOURRI ASSORTED | Pan Aroma Set Of 4 Pot Pourri Fragrance - Berries Fluff | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=43%; NP=1.03; ROI=71.0%; Sales=200; Pack 4x makes profit negative |
| 1351 | PAN AROMA POTPOURRI ASSORTED 180G | Pan Aroma Set Of 4 Pot Pourri Fragrance - Berries Fluff | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=41%; NP=1.03; ROI=71.0%; Sales=200; Pack 4x makes profit negative |
| 1351 | PAN AROMA POTPOURRI ASSORTED 180G | Pan Aroma Set Of 4 Pot Pourri Fragrance - Berries Fluff | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=41%; NP=1.03; ROI=71.0%; Sales=200; Pack 4x makes profit negative |
| 1357 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 15L | Tidyz 3 Packs Of 40 White Plastic Disposable Pedal Bin  | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=48%; NP=0.89; ROI=70.2%; Sales=50; Pack 120x makes profit negative |
| 1357 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 15L | Tidyz 3 Packs Of 40 White Plastic Disposable Pedal Bin  | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=48%; NP=0.89; ROI=70.2%; Sales=50; Pack 120x makes profit negative |
| 1358 | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | RCR Crystal Melodia Luxion 360 ml Tumbler & 230 ml High | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=25%; NP=7.66; ROI=70.2%; Sales=50; Partial match |
| 1367 | PYREX CLASSIC CASSEROLE 1.3LTR | Pyrex Essentials Glass Round Casserole Dish with Lid 1. | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=3.70; ROI=69.6%; Sales=50; Pack 2x makes profit negative |
| 1367 | PYREX CLASSIC CASSEROLE 1.3LTR | Pyrex Essentials Glass Round Casserole Dish with Lid 1. | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=3.70; ROI=69.6%; Sales=50; Pack 2x makes profit negative |
| 1367 | PYREX CLASSIC CASSEROLE 1.3LTR | Pyrex Essentials Glass Round Casserole Dish with Lid 1. | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=47%; NP=3.70; ROI=69.6%; Sales=50; Pack 2x makes profit negative |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | Codex HIGH | FILTERED OUT | VERIFIED | INCORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50 | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=40%; NP=0.74; ROI=66.4%; Sales=500; Exact EAN match |
| 1400 | DEKTON SMOOTHING PLANE | Draper Expert 250mm Smoothing Beech Wood Plane  50mm B | Codex samecha | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=4.06; ROI=66.3%; Sales=400; Insufficient evidence |
| 1406 | FALSE EYELASHES 4 ASSTD DESIGNS. | False Eyelashes 4 Pairs - Professional Reusable Face Ey | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=29%; NP=0.91; ROI=65.3%; Sales=200; Insufficient evidence |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Stone, 6 kg | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=67%; NP=5.34; ROI=64.9%; Sales=50; Brand match: EVERBUILD |
| 1413 | DRAPER WINDOW SQUEEGEE | Draper Telescopic Window Cleaning Equipment  46.55 to  | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=23%; NP=1.91; ROI=64.6%; Sales=100; Partial match |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | Roundup Path Weedkiller, Ready to Use, Refill for Press | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=55%; NP=3.52; ROI=63.2%; Sales=50; Brand match: ROUNDUP |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves - Single Pair ( | cli | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=69%; NP=1.41; ROI=63.2%; Sales=200; Brand match: MARIGOLD |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated Multi-Purpose F | cli | FILTERED OUT | FILTERED OUT | CORRECT | Sim=72%; NP=1.82; ROI=57.8%; Sales=50; Pack 2x makes profit negative |
| 1473 | MINKY SUPER DIAMOND SCRUBBER | Minky Anti-Bacterial Cleaing Pad  3 Pack  Reusable Mi | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=19%; NP=0.84; ROI=57.1%; Sales=700; Pack 3x makes profit negative |
| 1538 | TIDYZ CARRIERS HANDY BAGS 40 PCS 45CM x 57.5cm | Tidyz 2 Packs Of 40 Handy Bags - Carrier Bags - Fits 15 | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=32%; NP=0.59; ROI=48.2%; Sales=200; Pack 2x makes profit negative |
| 1538 | TIDYZ CARRIERS HANDY BAGS 40 PCS 45CM x 57.5cm | Tidyz 2 Packs Of 40 Handy Bags - Carrier Bags - Fits 15 | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=32%; NP=0.59; ROI=48.2%; Sales=200; Pack 2x makes profit negative |
| 1595 | BARTOLINE EASIPASTE 1KG | Bartoline EasipasteÂ® Ready Mixed Wallpaper Adhesive 5k | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=23%; NP=1.38; ROI=41.8%; Sales=400; Insufficient evidence |
| 1606 | FLASH MICROFIBRE MOP HEAD | 6 PCS Reusable Mop Refill Pads for Flash Powermop, Micr | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=27%; NP=0.93; ROI=40.0%; Sales=200; Pack 6x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge S | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=58%; NP=0.49; ROI=37.8%; Sales=100; Pack 6x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge S | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=58%; NP=0.49; ROI=37.8%; Sales=100; Pack 6x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge S | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=58%; NP=0.49; ROI=37.8%; Sales=100; Pack 6x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge S | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=58%; NP=0.49; ROI=37.8%; Sales=100; Pack 6x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS PK2 | Addis Fairy Originals Non Scratch General Dual Sponge S | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=58%; NP=0.49; ROI=37.8%; Sales=100; Pack 6x makes profit negative |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G | 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning  | cli | FILTERED OUT | FILTERED OUT | CORRECT | Sim=66%; NP=0.82; ROI=35.9%; Sales=200; Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | cli | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design cardboard masks | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=70%; NP=0.29; ROI=35.5%; Sales=50; Pack 12x makes profit negative |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker,  | Opus | FILTERED OUT | VERIFIED | INCORRECT | Sim=42%; NP=0.46; ROI=34.8%; Sales=50; Exact EAN match |
| 1656 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR | Superior 10-Pack Aluminium Foil Trays with Paper Lids,  | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=29%; NP=1.48; ROI=34.8%; Sales=700; Partial match |
| 1661 | DLUX PRO KLEEN MICROFIBRE BATHROOM & KITCHEN MOP REFILL | DLUX PRO-KLEEN Super Absorbent Chenille Flat Floor Mop  | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=29%; NP=0.38; ROI=34.4%; Sales=50; Insufficient evidence |
| 1668 | MINKY ALL PURPOSE CLOTH PK10 | Minky Anti-Bacterial Cleaing Pad  3 Pack  Reusable Mi | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=21%; NP=0.59; ROI=33.6%; Sales=700; Pack 3x makes profit negative |
| 1669 | BARBIE DIY FASHION SET | Barbie DIY Fashion Designer Set â€“ Make Your Own Casua | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=1.53; ROI=33.6%; Sales=200; Insufficient evidence |
| 1690 | TALA MEAT THERMOMETER 4106 | Tala Stainless Steel Meat Thermometer, Classic Meat Pro | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=27%; NP=1.31; ROI=31.7%; Sales=50; Partial match |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, W | Opus | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=64%; NP=1.93; ROI=30.9%; Sales=50; Brand match: BLUE CANYON |
| 1710 | KILROCK DAMP CLEAR REFILL POUCH 1KG (2x500g) | Kilrock Damp Clear Moisture Trap Refill - Pack of 5 x 5 | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=40%; NP=0.90; ROI=30.4%; Sales=400; Pack 5x makes profit negative |
| 1716 | RUSSELL HOBBS VIENNA CUTLERY SET 16PC | Russell Hobbs RH00022GP Vienna 16 Piece Cutlery Set - S | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=3.32; ROI=29.2%; Sales=300; Pack 16x makes profit negative |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x 33m | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=85%; NP=0.43; ROI=28.6%; Sales=50; Brand match: ULTRATAPE |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food Dog Feeding Ch | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=36%; NP=0.78; ROI=28.4%; Sales=50; Pack 2x makes profit negative |
| 1742 | BLUE CANYON LED VANITY MIRROR 17CM X 22CM | Blue Canyon 17cm Free Standing Round Swivel Mirror - Ch | Gemini | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=27%; NP=1.36; ROI=28.0%; Sales=100; Partial match |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | Amtech G0230 150mm (6") Pointing trowel with soft grip | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=74%; NP=0.63; ROI=27.6%; Sales=50; Brand match: AMTECH |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3P | Fairy Soap Dispensing Dish Brush | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=72%; NP=0.42; ROI=27.4%; Sales=50; Brand match: FAIRY |
| 1753 | LAV FAME WINE GLASS 30CL PK3 | LAV Stemless Red & White Wine Glasses Tumbler Set of 6  | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=20%; NP=0.86; ROI=27.1%; Sales=200; Pack 6x makes profit negative |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casseroles high resis | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=56%; NP=3.19; ROI=26.9%; Sales=300; Pack 3x makes profit negative |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casseroles high resis | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=56%; NP=3.19; ROI=26.9%; Sales=300; Pack 3x makes profit negative |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casseroles high resis | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=56%; NP=3.19; ROI=26.9%; Sales=300; Pack 3x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5" Quality Dispo | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=0.30; ROI=26.7%; Sales=700; Pack 40x makes profit negative |
| 1773 | PPS POCKET TISSUES 3PLY 10S PK10 | Handy Pocket 3ply Tissues, Packs of 10 | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=57%; NP=0.29; ROI=26.0%; Sales=100; Moderate similarity |
| 1776 | CHEF AID PASTRY CUTTERS  W184 | Chef Aid Pastry Cutters, Set Of 3, Cookie Biscuit Cutte | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=22%; NP=0.38; ROI=25.7%; Sales=800; Pack 3x makes profit negative |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End Cocktails Stick | webapp gpt | FILTERED OUT | VERIFIED | INCORRECT | Sim=24%; NP=0.25; ROI=22.7%; Sales=50; Exact EAN match |
| 1827 | BABY PIPKIN BRUSH & COMB SET | Baby Hair Comb, 3PCS Baby Hair Brush and Comb Set, Baby | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=28%; NP=0.27; ROI=20.7%; Sales=100; Pack 3x makes profit negative |
| 1827 | BABY PIPKIN BRUSH & COMB SET | Baby Hair Comb, 3PCS Baby Hair Brush and Comb Set, Baby | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=28%; NP=0.27; ROI=20.7%; Sales=100; Pack 3x makes profit negative |
| 1846 | SECURPAK NYLON LOCKING NUT ZINC PLATED M12 PACK OF 6 | M12 Nyloc Hex Nut Locking Metal Steel Sheet Zinc Plated | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=56%; NP=0.23; ROI=19.1%; Sales=50; Pack 2x makes profit negative |
| 1846 | SECURPAK NYLON LOCKING NUT ZINC PLATED M12 PACK OF 6 | M12 Nyloc Hex Nut Locking Metal Steel Sheet Zinc Plated | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=56%; NP=0.23; ROI=19.1%; Sales=50; Pack 2x makes profit negative |
| 1868 | TALA DISPOSABLE ICING BAGSX10 | Tala Icing Bag Set with 8 Interchangeable Stainless Ste | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=15%; NP=0.27; ROI=17.8%; Sales=200; Insufficient evidence |
| 1871 | MASON CASH MUG 450ML CREAM | Mason Cash Colour Mix Cream Mixing Bowl  2.7 Litre Cap | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=16%; NP=0.47; ROI=17.3%; Sales=100; Insufficient evidence |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel with soft grip | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=56%; NP=0.35; ROI=15.8%; Sales=50; Brand match: AMTECH |
| 1886 | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY ASSORTE | Nuage Body Powder Set - Talc-Free, Cherry Blossom and W | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=61%; NP=0.25; ROI=15.6%; Sales=200; Pack 2x makes profit negative |
| 1886 | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY ASSORTE | Nuage Body Powder Set - Talc-Free, Cherry Blossom and W | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=61%; NP=0.25; ROI=15.6%; Sales=200; Pack 2x makes profit negative |
| 1886 | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY ASSORTE | Nuage Body Powder Set - Talc-Free, Cherry Blossom and W | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=61%; NP=0.25; ROI=15.6%; Sales=200; Pack 2x makes profit negative |
| 1886 | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY ASSORTE | Nuage Body Powder Set - Talc-Free, Cherry Blossom and W | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=61%; NP=0.25; ROI=15.6%; Sales=200; Pack 2x makes profit negative |
| 1891 | HEM INCENSE STICKS FRANKINCENSE | HEM Frankincense Incense Sticks  Pack of 6 Hexagonal T | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.39; ROI=15.4%; Sales=50; Pack 6x makes profit negative |
| 1900 | KILROCK MOULD & MILDEW REMOVER BRUSH ON GEL 250ML(SOLD  | Kilrock Mould Remover Brush-On Gel 2 x 250ml - Eliminat | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=29%; NP=0.43; ROI=15.0%; Sales=200; Insufficient evidence |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for strea | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=24%; NP=0.29; ROI=14.1%; Sales=200; Exact EAN match |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White  | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=0.43; ROI=13.9%; Sales=100; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beige | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=63%; NP=0.16; ROI=13.9%; Sales=400; Brand match: CHEF AID |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand and Cement, Gre | webapp gpt | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=65%; NP=0.57; ROI=13.0%; Sales=50; Brand match: EVERBUILD |
| 1929 | PASABACHE 6 PC ROYAL SMALL FOOD SAVER 230 M | Bonsenkitchen Precut Vacuum Sealer Bags, 200 Pcs 15 x 2 | Codex samecha | FILTERED OUT | FILTERED OUT | CORRECT | Sim=20%; NP=0.67; ROI=12.9%; Sales=300; Pack 200x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID | Wham Clear Plastic Storage Box Boxes With Lids Home Off | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=37%; NP=0.55; ROI=12.6%; Sales=50; Pack 3x makes profit negative |
| 1944 | WINDOW STYLE WALL MIRROR  70X36 | Window Style Mirror - Living Room Decor Hallway Home Pa | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=27%; NP=1.06; ROI=11.9%; Sales=100; Insufficient evidence |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2PK | The Big Cheese Quick Click Mouse Trap - Twinpack, Kills | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=42%; NP=0.27; ROI=11.3%; Sales=50; Pack 2x makes profit negative |
| 1953 | RUSTINS SCRATCH COVER-DARK 125ML | Rustins Scratch Cover Dark â€“ Conceal Surface Scratche | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=29%; NP=0.31; ROI=11.3%; Sales=100; Insufficient evidence |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=59%; NP=0.36; ROI=10.1%; Sales=100; Brand match: SMART CHOICE |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=72%; NP=0.35; ROI=8.9%; Sales=50; Moderate similarity |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=61%; NP=0.31; ROI=8.8%; Sales=100; Moderate similarity |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured fr | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=28%; NP=0.22; ROI=8.5%; Sales=100; Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin Deep - 09inch | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=73%; NP=0.40; ROI=8.1%; Sales=50; Brand match: BAKER & SALT |
| 2001 | MINKY WASHING LINE PROP SUREGRIP | Minky Retractable Reel Washing Line with 15 m of Drying | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=29%; NP=0.38; ROI=7.8%; Sales=200; Insufficient evidence |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner Set with Tommy | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=64%; NP=0.21; ROI=7.3%; Sales=50; Pack 6x makes profit negative |
| 2004 | LAV TUMBLER 3PCS | Lav Sude Tumbler Glass Set. Drinking Glasses. Pack of 6 | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=35%; NP=0.24; ROI=7.3%; Sales=400; Pack 2x makes profit negative |
| 2010 | COOKER HOOD FILTER CHARCOAL | Cooker Hood Filter Kit 3Pack - 2 Grease Filters for Coo | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=25%; NP=0.32; ROI=7.0%; Sales=500; Pack 3x makes profit negative |
| 2025 | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Oaktree UK 9ft Banner Happy 8th Birthday Pink | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=58%; NP=0.07; ROI=5.7%; Sales=50; Moderate similarity |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=71%; NP=0.13; ROI=5.6%; Sales=50; Brand match: HARRIS |
| 2036 | GEEPAS RICE COOKER 0.6LTR | Geepas Rice Cooker, 0.6L  Electric Rice Cooker with Ke | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=0.74; ROI=5.1%; Sales=200; Insufficient evidence |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray Bathroom Ac | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=27%; NP=0.20; ROI=4.8%; Sales=500; Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 2045 | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2 | Pyrex - Set of 3 Rectangular Oven Dishes - Ideal for 2  | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=31%; NP=0.59; ROI=4.7%; Sales=400; Pack 2x makes profit negative |
| 2045 | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2 | Pyrex - Set of 3 Rectangular Oven Dishes - Ideal for 2  | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=31%; NP=0.59; ROI=4.7%; Sales=400; Pack 2x makes profit negative |
| 2045 | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2 | Pyrex - Set of 3 Rectangular Oven Dishes - Ideal for 2  | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=31%; NP=0.59; ROI=4.7%; Sales=400; Pack 2x makes profit negative |
| 2048 | BG GOLD 2 GANG SWITCH | BG Electrical Double Wall Light Switch, 2 Way, Raised a | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=15%; NP=0.23; ROI=4.6%; Sales=500; Insufficient evidence |
| 2054 | KILROCK PLUGHOLE FRESHENER CITRUS FRESH 500ML(SOLD EACH | Kilrock Plughole Unblocker Bathroom 500ml 2 Pack - Fast | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=0.12; ROI=4.2%; Sales=50; Pack 2x makes profit negative |
| 2054 | KILROCK PLUGHOLE FRESHENER CITRUS FRESH 500ML(SOLD EACH | Kilrock Plughole Unblocker Bathroom 500ml 2 Pack - Fast | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=29%; NP=0.12; ROI=4.2%; Sales=50; Pack 2x makes profit negative |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve, Kitchen Essenti | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=22%; NP=0.08; ROI=3.8%; Sales=200; Exact EAN match |
| 2062 | WHAM CRYSTAL 80LTR CLEAR BOX & LID | CRYSTAL 80L BOX & LID CLEAR 11315 | Codex very high | FILTERED OUT | NEEDS VERIFICATION | INCORRECT | Sim=63%; NP=0.23; ROI=3.5%; Sales=100; Moderate similarity |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Ro | Opus | FILTERED OUT | VERIFIED | INCORRECT | Sim=33%; NP=0.10; ROI=2.8%; Sales=50; Exact EAN match |
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=86%; NP=0.06; ROI=2.8%; Sales=50; Brand match: FAIRY |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole high resistance,  | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=60%; NP=0.21; ROI=2.3%; Sales=100; Brand match: PYREX |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pa | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=63%; NP=0.19; ROI=1.9%; Sales=50; Pack 4x makes profit negative |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pa | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=63%; NP=0.19; ROI=1.9%; Sales=50; Pack 4x makes profit negative |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pa | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=63%; NP=0.19; ROI=1.9%; Sales=50; Pack 4x makes profit negative |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Spray 1 Litre, Pa | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=63%; NP=0.19; ROI=1.9%; Sales=50; Pack 4x makes profit negative |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | Codex HIGH | FILTERED OUT | VERIFIED | INCORRECT | Sim=69%; NP=0.02; ROI=1.7%; Sales=100; Exact EAN match |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | Codex HIGH | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | Codex samecha | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | opus2 | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 2 | webapp gpt | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.03; ROI=1.5%; Sales=600; Pack 20x makes profit negative |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEON | Waterproof Robin Memorial Graveside Lantern with LED Ca | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=72%; NP=0.08; ROI=1.2%; Sales=50; Exact EAN match |
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAVY | Price & Kensington Black 6 Cup Teapot | Codex very high | FILTERED OUT | FILTERED OUT | CORRECT | Sim=77%; NP=0.05; ROI=0.9%; Sales=100; Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 2092 | ULTRATAPE FLASHBAND LEAD 100MMX10M | Bostik Flashband Self Adhesive Flashing Tape for Roofs  | Codex samecha | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=0.07; ROI=0.9%; Sales=500; Insufficient evidence |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=61%; NP=0.02; ROI=0.8%; Sales=50; Brand match: ROLSON |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | webapp gpt | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=61%; NP=0.02; ROI=0.8%; Sales=50; Brand match: ROLSON |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | Codex very high | FILTERED OUT | VERIFIED | INCORRECT | Sim=69%; NP=0.02; ROI=0.7%; Sales=200; Exact EAN match |
| 2097 | WALL CLOCK PP 3 ASSORTED 30CM | Wall Clock 30cm Silent Non-Ticking, Big Numbers Easy to | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=19%; NP=0.02; ROI=0.4%; Sales=200; Insufficient evidence |
| 2098 | WHAM CRYSTAL 160LTR CLEAR BOX & LID | Wham Pack of 2 Crystal Storage Boxes with Lids, Plastic | Gemini | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.05; ROI=0.4%; Sales=300; Pack 2x makes profit negative |
| 2098 | WHAM CRYSTAL 160LTR CLEAR BOX & LID | Wham Pack of 2 Crystal Storage Boxes with Lids, Plastic | Opus | FILTERED OUT | FILTERED OUT | CORRECT | Sim=34%; NP=0.05; ROI=0.4%; Sales=300; Pack 2x makes profit negative |
| 2099 | CHEF AID FLUTED CAKE RING | Chef Aid Non-Stick Fluted Cake Pan with Non-Stick Coati | Gemini | FILTERED OUT | OTHER / LOW PRIORITY | ACCEPTABLE | Sim=24%; NP=0.01; ROI=0.4%; Sales=200; Insufficient evidence |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | Codex very high | FILTERED OUT | HIGHLY LIKELY | INCORRECT | Sim=67%; NP=0.01; ROI=0.3%; Sales=100; Brand match: SMART CHOICE |

## Problem Patterns Identified

- **Weak match evidence**: 108 occurrences (example: Row 1458 / Codex samecha AI=VERIFIED → You=OTHER / LOW PRIORITY)
- **Other threshold/logic drift**: 93 occurrences (example: Row 2081 / cli AI=NEEDS VERIFICATION → You=VERIFIED)
- **Pack/quantity mismatch (bundle vs single)**: 92 occurrences (example: Row 1758 / cli AI=VERIFIED → You=FILTERED OUT)
- **Variant mismatch (scent/color/etc)**: 28 occurrences (example: Row 2040 / cli AI=VERIFIED → You=FILTERED OUT)

## Detailed Product Analysis (Ground Truth)
Products below are categorized based on the INDEPENDENT validation logic (Rules/Guide/Gemini).
Sorted by Match Confidence (Title Similarity) where applicable.

### VERIFIED (23 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | EAN Match | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 1040 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | 2.35 | 84% | Exact EAN match |
| 1822 | HOUSE MATE STAINLESS STEEL CLEANER & POL | House Mate Stainless Steel Cleaner and P | 0.79 | 78% | Exact EAN match |
| 1130 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | 1.51 | 75% | Exact EAN match |
| 2086 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WI | Waterproof Robin Memorial Graveside Lant | 0.08 | 72% | Exact EAN match |
| 2081 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | 0.02 | 69% | Exact EAN match |
| 2094 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | 0.02 | 69% | Exact EAN match |
| 562 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | 8.00 | 69% | Exact EAN match |
| 750 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Sce | 2.73 | 61% | Exact EAN match |
| 1056 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scen | 1.67 | 57% | Exact EAN match |
| 945 | AIRWICK REED DIFFUSER MULLED WINE 33ML P | Air Wick Essential Oils Reed Diffuser Ai | 16.55 | 57% | Exact EAN match |
| 1873 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins De | 1.40 | 46% | Exact EAN match |
| 1655 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass V | 0.46 | 42% | Exact EAN match |
| 1858 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | 1.30 | 42% | Exact EAN match |
| 1399 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36 | Tidyz 200 x Extra Large Super Strong Dog | 0.74 | 40% | Exact EAN match |
| 2066 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Ston | 0.10 | 33% | Exact EAN match |
| 1457 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays wi | 2.13 | 31% | Exact EAN match |
| 1732 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Gl | 0.76 | 30% | Exact EAN match |
| 1332 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  | 5.11 | 27% | Exact EAN match |
| 1883 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fa | 0.68 | 27% | Exact EAN match |
| 1829 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland | 1.24 | 25% | Exact EAN match |
| 1910 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee pe | 0.29 | 24% | Exact EAN match |
| 1799 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End  | 0.25 | 24% | Exact EAN match |
| 2058 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve,  | 0.08 | 22% | Exact EAN match |

### HIGHLY_LIKELY (29 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | Title Sim | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 2067 | FAIRY MAX POWER SOAP DISPENSING DISH BRU | Fairy Soap Dispensing Dish Brush | 0.06 | 86% | Brand match: FAIRY |
| 1729 | ULTRATAPE PICTURE FRAME TAPE 24MMX50M | Ultratape  Picture Frame Tape  48mm x  | 0.43 | 85% | Brand match: ULTRATAPE |
| 1821 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | 0.89 | 82% | Brand match: FALCON |
| 1748 | AMTECH POINTING TROWEL 150M(6") WITH SOF | Amtech G0230 150mm (6") Pointing trowel  | 0.63 | 74% | Brand match: AMTECH |
| 1995 | BAKER & SALT LOOSE CASE CAKE TIN 23CM | Baker & Salt Loose Based Round Cake Tin  | 0.40 | 73% | Brand match: BAKER & SALT |
| 1749 | FAIRY MAX POWER SOAP DISPENSING DISH BRU | Fairy Soap Dispensing Dish Brush | 0.42 | 72% | Brand match: FAIRY |
| 2027 | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife | 0.13 | 71% | Brand match: HARRIS |
| 1762 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, M | 0.74 | 70% | Brand match: ROLSON |
| 1422 | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Marigold 2 x Extra Tough Outdoor Gloves  | 1.41 | 69% | Brand match: MARIGOLD |
| 1804 | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 3 | 0.72 | 68% | Brand match: BAKER & SALT |
| 621 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Tidyz 30 Extra Large Wheelie Bin Liners  | 2.77 | 67% | Brand match: TIDYZ |
| 1410 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Sto | 5.34 | 67% | Brand match: EVERBUILD |
| 2101 | SMART CHOICE TYRE RING DOG TOY | Smart Choice Dog Toy Box, Grey | 0.01 | 67% | Brand match: SMART CHOICE |
| 1928 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand  | 0.57 | 65% | Brand match: EVERBUILD |
| 1730 | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE â€“ Square Glass Dish 20  | 1.04 | 64% | Brand match: PYREX |
| 1844 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and  | 0.54 | 64% | Brand match: AMTECH |
| 1707 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x | 1.93 | 64% | Brand match: BLUE CANYON |
| 1918 | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Chef Aid Pure Bristle Pastry Brush, Beig | 0.16 | 63% | Brand match: CHEF AID |
| 1789 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 4 | 0.88 | 63% | Brand match: APOLLO |
| 1364 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpenin | 1.02 | 61% | Brand match: AMTECH |
| 2093 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | 0.02 | 61% | Brand match: ROLSON |
| 2073 | PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | Pyrex Essentials Glass oval Casserole hi | 0.21 | 60% | Brand match: PYREX |
| 1370 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK | Giftmaker Collection Large Christmas San | 1.04 | 60% | Brand match: GIFTMAKER |
| 1970 | SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | Smart Choice Dog Toy Box, Grey | 0.36 | 59% | Brand match: SMART CHOICE |
| 1744 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | 0.91 | 57% | Brand match: KILNER |
| 1630 | DRAPER SPANNER SET METRIC COMBINATION | Draper 1 x Redline 68481 Metric Combinat | 2.15 | 56% | Brand match: DRAPER |
| 1881 | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | Amtech G0230 150mm (6") Pointing trowel  | 0.35 | 56% | Brand match: AMTECH |
| 696 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK | Bacofoil 3 x Zipper Small All Purpose Ba | 2.93 | 55% | Brand match: BACOFOIL |
| 1421 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FRE | Roundup Path Weedkiller, Ready to Use, R | 3.52 | 55% | Brand match: ROUNDUP |

### NEEDS_VERIFICATION (145 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | Title Sim | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 252 | PRIMA MULTI SHOWERHEAD CHROME | Lara  Multi Spray Shower Head - Chrome | 10.37 | 76% | Partial match |
| 1745 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tu | 1.71 | 75% | Partial match |
| 1981 | WHAM CRYSTAL CD BOX CLEAR | Wham Pack 5 Crystal 17L Box & Lid Clear | 0.35 | 72% | Moderate similarity |
| 1129 | PAN AROMA CANDLE TALL APPLE&CINN EACH | Pan Aroma 16 Tea Lights Apple & Cinnamon | 1.51 | 68% | Partial match |
| 513 | SIL TOILET ROLL HOLDER STAINLESS STEEL | Free-Standing Toilet Roll Holder, Stainl | 3.97 | 67% | Partial match |
| 1128 | PAN AROMA CANDLE ROUND APPLE CINNAMON EA | Pan Aroma 16 Tea Lights Apple & Cinnamon | 1.51 | 66% | Partial match |
| 1051 | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Smartbones 10 Chicken Sticks Rawhide Fre | 2.33 | 64% | Partial match |
| 2062 | WHAM CRYSTAL 80LTR CLEAR BOX & LID | CRYSTAL 80L BOX & LID CLEAR 11315 | 0.23 | 63% | Moderate similarity |
| 794 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE | 2.03 | 62% | Partial match |
| 1061 | MENS WATERPROOF FLEECE TRAPPER HAT WITH  | HEAT HOLDERS - Mens Waterproof Fleece Li | 6.45 | 62% | Partial match |
| 1986 | ASHLEY CASH BOX 4.5 INCH | Ashley - Metal Cash Box - 20.5cm - Red | 0.31 | 61% | Moderate similarity |
| 224 | WORLD OF PETS CAT LITTER SCENTED 3LT | World's Best Cat Litter 28lb (12.7kg) La | 16.14 | 60% | Partial match |
| 743 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE | 2.09 | 60% | Partial match |
| 1165 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measur | 1.25 | 59% | Partial match |
| 2025 | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Oaktree UK 9ft Banner Happy 8th Birthday | 0.07 | 58% | Moderate similarity |
| 399 | PENDEFORD POTATO BAKER | Microwave Potato Baker, Red | 5.07 | 57% | Partial match |
| 1773 | PPS POCKET TISSUES 3PLY 10S PK10 | Handy Pocket 3ply Tissues, Packs of 10 | 0.29 | 57% | Moderate similarity |
| 812 | BLUE CANYON TOILET BRUSH PLASTIC LACE BL | BGL Stainless Steel Standing Toilet Brus | 7.40 | 56% | Partial match |
| 1852 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE | 0.51 | 56% | Partial match |
| 1979 | FALCON ENAMEL ROASTER ROUND 20CM | Barmans BYX0B0A6289 Enamel Roaster with  | 0.86 | 55% | Moderate similarity |
| 1813 | SMART CHOICE GLOW IN THE DARK ROPE DOG T | Zip witn 6 String Toy for Pets, Glow in  | 0.46 | 54% | Moderate similarity |
| 1560 | LITTLE TREES CAR FRESHENER ORANGE JUICE | Little Trees Air Freshener Tree LTZ084 O | 0.61 | 54% | Partial match |
| 2026 | HAPPY 8TH BIRTHDAY BANNER 9FT | Oaktree UK 9ft Banner Happy 8th Birthday | 0.07 | 54% | Moderate similarity |
| 1172 | FIRST STEPS  FOOD STORAGE POTS WITH SPOO | First Steps 8 Baby Food Freezer Cubes Tr | 1.29 | 54% | Partial match |
| 1718 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Rolson 11201 8oz Stubby Claw Hammer | 0.86 | 53% | Partial match |
| 672 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SE | Schott Zwiesel Pure Glassware - White Wi | 7.18 | 53% | Partial match |
| 1754 | CHEF AID BEAN SLICER | Krisk French Style Bean Slicer - HA43 | 0.39 | 53% | Moderate similarity |
| 1299 | MEMORIAL GRAVE FLOWER VASE WITH STAKE | Black Graveside Memorial Spiked Flower V | 0.99 | 53% | Moderate similarity |
| 131 | BRIGHT & HOMELY METAL WATERING CAN ROSE | Woodside Silver 9L Metal Garden and Plan | 10.53 | 52% | Moderate similarity |
| 2083 | WHAM MEASURING JUG 2LTR | Wham Cuisine 2L Clear Measuring Jug,JNS_ | 0.02 | 52% | Moderate similarity |
| 1927 | PRIMA SALT AND PEPPER SHAKER 8X4.5CM | Juvale Salt and Pepper Shakers Stainless | 0.32 | 52% | Moderate similarity |
| 1537 | PRIMA SALT AND PEPPER SHAKER 6.3X4CM 2PC | Juvale Salt and Pepper Shakers Stainless | 0.90 | 52% | Moderate similarity |
| 329 | BRIGHT & HOMELY PILLAR CANDLE IVORY 100  | simpa Unscented Ivory Pillar Candles Smo | 10.62 | 52% | Moderate similarity |
| 447 | APOLLO STAINLESS STEEL SHARPENING STEEL | Professional Carbon Steel Black Knife Sh | 6.23 | 52% | Moderate similarity |
| 1166 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expand | 4.25 | 52% | Partial match |
| 1674 | MINKY IRONING BOARD CLIPS PK3 | Minky Easy Fit Ironing board cover + Iro | 1.26 | 51% | Partial match |
| 1921 | BLOOME MINI GEL BURST AIR FRESHENER 3PK | Jelly Belly 15710A 3D Gel Mini Vent Air  | 0.19 | 51% | Moderate similarity |
| 2088 | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK  | STATUS 2 Way Socket  2 USB Port Cable F | 0.04 | 51% | Moderate similarity |
| 786 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expand | 5.47 | 51% | Partial match |
| 781 | GROSVENOR 55CM TROUGH BLACK | 4 Black Gros Trough 55cm | 5.93 | 51% | Moderate similarity |
| 1372 | HOBBY DIAMOND ROUND PAPER BASKET 12LTR | JVL Natural Round Seagrass Waste Paper B | 1.74 | 51% | Moderate similarity |
| 1872 | ELF ARRIVAL ENVELOPE OUTFIT | Christmas Naughty Elf Arrival Clothes -  | 0.37 | 51% | Moderate similarity |
| 1971 | MASTERCLASS SALT/PAPPER MILL BLACK | MasterClass Pepper Mill or Salt Grinder  | 0.42 | 50% | Moderate similarity |
| 1808 | BEAUFORT MEASURE ULTIMATE JUG 2LTR | Beaufort - 2 Litre Clear Plastic Measuri | 0.25 | 50% | Moderate similarity |
| 2009 | EXTRASTAR EXTENSION LEAD 2 GANG 2M WHITE | EXTRASTAR 2 Gang Extension Lead, 2 Metre | 0.25 | 50% | Moderate similarity |
| 1878 | KILROCK SERVICE-PRO COFFEE MACHINE DESCA | Kilrock Service Pro Coffee Machine Desca | 0.63 | 50% | Partial match |
| 1411 | MASTER COOK DIE CAST CASSEROLE 24CM | MasterClass Cast Aluminium Cream Cassero | 11.25 | 50% | Moderate similarity |
| 1009 | SALT & PEPPER SHAKERS | Juvale Salt and Pepper Shakers Stainless | 1.54 | 49% | Moderate similarity |
| 990 | LADIES KNITTED HAT WITH FAUX FUR POM-POM | Sibba Bobble Hat for Women Winter Beanie | 2.47 | 49% | Moderate similarity |
| 1796 | KILNER PRESERVE JAR 0.25LTR SCREW LID | Kilner Preserve Jar 0.25L (250ml) Round  | 0.40 | 49% | Moderate similarity |
| 1162 | ADORN SALT & PEPPER SHAKER | Juvale Salt and Pepper Shakers Stainless | 1.37 | 49% | Moderate similarity |
| 1306 | APOLLO UTENSIL HOLDER WHITE | Premier Housewares Charm Utensil Jar, Wh | 2.08 | 49% | Moderate similarity |
| 1173 | VFM EMULSION MATT  PAINT WHITE 5L | Dulux Walls & Ceilings Matt Emulsion Pai | 5.20 | 49% | Moderate similarity |
| 302 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIU | Hobby Gift Sewing Box, Wood/Fabric, Embr | 9.98 | 48% | Moderate similarity |
| 762 | VFM  TRADE CONT MATT PAINT WHT 10L | Johnstone'S Trade 10 Litre Covaplus Viny | 17.82 | 48% | Moderate similarity |
| 754 | WOODEN INSECT HOUSE METAL ROOF | Garden Life Insect Hotel Wooden Bug Hous | 7.19 | 48% | Moderate similarity |
| 1940 | MEMORIAL PLASTIC SPIKE SPECIAL MUM & DAD | Mum And Dad - Plastic Spike Memorial Gra | 0.25 | 48% | Moderate similarity |
| 1797 | APOLLO SILICON WHISK SPLASH 25CM | Apollo Whisk Rainbow, silicone, 26cm, 25 | 0.37 | 47% | Moderate similarity |
| 1341 | DEKTON UTILTY 50PC BLADES | Heavy Duty Straight Blades | 2.37 | 47% | Moderate similarity |
| 1156 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE  | Kilrock 3 X Blast Away Mould Spray 500ml | 2.30 | 47% | Partial match |
| 628 | SECURPAK DRYWALL SCREWS BLACK 3.5X65MM | TIMCO PH2 Philips Drywall Screws - 3.5 x | 2.83 | 47% | Moderate similarity |
| 461 | STEAM PUNK SKULL GOLD/BRONZE10CM ASSORTE | Nemesis Now Steampunk Clockwork Baron Sk | 9.88 | 47% | Moderate similarity |
| 1642 | APOLLO POTATO MASHER STAINLESS STEEL FOL | Potato Mashers, Joyoldelf Potato Masher  | 1.06 | 46% | Moderate similarity |
| 1136 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCK | Kilrock SLAM - Sink and Plughole Bathroo | 4.12 | 46% | Partial match |
| 1041 | AMTECH ANVIL SECATEURS | Spear & Jackson 6758GS Razorsharp Geared | 4.43 | 46% | Moderate similarity |
| 1252 | B&CO AIR FRYER HEAT RESISTANT FOOD GRIP | Silicone Oven Mitts for Air Fryer, 1 Pai | 1.42 | 46% | Moderate similarity |
| 1697 | EXTRASTAR EXTENSION LEAD 6 GANG 1M WHITE | ExtraStar 6 Way Extension Leads with Sur | 1.08 | 46% | Partial match |
| 1696 | EXTRASTAR EXTENSION LEAD 6 GANG 1M BLACK | ExtraStar 6 Way Extension Leads with Sur | 1.08 | 46% | Partial match |
| 2060 | APOLLO RB CUTTING BOARD 30X20 | Apollo 3245 RB Bread Board 30cm Round, M | 0.16 | 46% | Moderate similarity |
| 1439 | SUNNEX STAINLESS STEEL DESSERT FORKS PK1 | 12-Piece (14 cm) Stainless Steel Pastry  | 1.63 | 46% | Moderate similarity |
| 974 | THE PET STORE LONG HANDLED POOP PICKER | 32" XL Dog Pooper Scoopers No Bending Fo | 4.42 | 46% | Moderate similarity |
| 1694 | BRIGHT & HOMELY REINFORCED GARDEN HOSE P | Faithfull 30M (98ft) Reinforced Hose 12. | 2.46 | 46% | Moderate similarity |
| 1132 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | ArtesÃ  Glass 18 cm Serving Bowl, Green | 2.33 | 46% | Moderate similarity |
| 869 | MASTER COOK CASSEROLE NON-STICK 24CM | MasterClass Cast Aluminium Cream Cassero | 17.36 | 45% | Moderate similarity |
| 1154 | PPS PLASTIC GLASSES HALF PINT 50PCS | Plastic Half Pint Glasses 50 Pack Strong | 1.71 | 45% | Moderate similarity |
| 968 | APOLLO  GRANITE BOARD 42X29 | Silk Route Home Black Granite Chopping B | 8.29 | 44% | Moderate similarity |
| 1486 | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Status 15 Metre TV Aerial Cable Extensio | 1.05 | 44% | Partial match |
| 174 | WENKEN FOOD PROCESSOR & BLENDER 2 IN 1 | Kenwood FDP65.180SI 2 in 1 Food Processo | 33.44 | 44% | Moderate similarity |
| 301 | BRIGHT & HOMELY BYPASS LOPPER | Spear & Jackson 8090RS Razorsharp Telesc | 11.62 | 44% | Moderate similarity |
| 1464 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas San | 0.93 | 44% | Partial match |
| 1757 | ROYALFORD MORTAR AND PESTLE STAINLESS ST | Bekith Mortar and Pestle Sets 18/8 Brush | 1.22 | 44% | Moderate similarity |
| 1188 | STAINLESS STEEL KETTLE 14CM 1L | Swan SK31020N Brushed Stainless Steel Ju | 4.86 | 44% | Moderate similarity |
| 804 | ADORN LARGE WIRE FRUIT BOWL 25X10.5CM | Black Fruit Bowl, 25x14cm Large Wire Fru | 4.26 | 44% | Moderate similarity |
| 574 | ROLSON DIAGONAL CUTTING PLIER VDE INSULA | KNIPEX 70 06 180 Diagonal Cutter chrome  | 16.20 | 44% | Moderate similarity |
| 1989 | KINGFISHER 30M REINFORCED HOSE PIPE | Faithfull 30M (98ft) Reinforced Hose 12. | 0.80 | 44% | Moderate similarity |
| 1916 | PAN AROMA PLUG-IN REFILL PURE COTTON PAC | Febreze Ambi Pur 3Volution Air Freshener | 0.18 | 43% | Moderate similarity |
| 919 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET  | Extra Select Premium Rabbit Mix Bucket 5 | 4.86 | 43% | Moderate similarity |
| 1604 | ROLSON DIAGONAL CUTTING PLIERS VDE INSUL | S&R VDE Insulated Diagonal Side Cutter 1 | 2.42 | 43% | Moderate similarity |
| 1189 | GIFTMAKER NON WOVEN SHOPPING BAGS HIGHLA | ECO CHIC Lightweight Foldable Reusable S | 1.24 | 43% | Moderate similarity |
| 396 | KINGAVON 6 LED TORCH | Kingavon BB-RT380 20-LED Rechargeable Em | 5.59 | 42% | Moderate similarity |
| 558 | SECURPLUMB COMPRESSION ELBOW 10X10MM | Radiator Valve Reducer Elbow Compression | 4.39 | 42% | Moderate similarity |
| 883 | CURVER RATTAN ROUND LARGE ORGANISER GREY | CURVER Style Rattan Effect Kitchen, Livi | 2.71 | 42% | Moderate similarity |
| 1346 | NT TOILET BLOCKS 6 PACK | Power Bleach Toilet Blocks, Cistern Bloc | 0.99 | 42% | Moderate similarity |
| 878 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Wast | 2.60 | 42% | Partial match |
| 1184 | NAIL DRYING SPRAY | Demert Nail Enamel Dryer Manicurist's Fi | 1.61 | 42% | Moderate similarity |
| 2064 | EASY SPRAY 4IN1 MULTI PURPOSE CLEANER 75 | Astonish Special Aromatic Edition Multi- | 0.18 | 42% | Moderate similarity |
| 722 | SANCTUARY TREE OF LIFE MIRROR BRONZE EFF | Inspirational Gifting Beautiful green le | 18.46 | 42% | Moderate similarity |
| 1395 | SUNNEX STAINLESS STEEL DESSERT SPOONS PK | Spoon Set, 12-Piece Stainless Steel Dess | 1.76 | 42% | Moderate similarity |
| 2102 | FLOW FLOOR & SURFACE CLEANER 5L EACH | Flow Lemon Floor & Surface All Purpose C | 0.00 | 42% | Moderate similarity |
| 1689 | APOLLO MARBLE BOARD BLACK 46x23CM | Silk Route Home Black Granite Chopping B | 3.47 | 41% | Moderate similarity |
| 987 | PRIMA CORKSCREW BOTTLE OPENER CHROME PLA | Wing Corkscrew Wine Bottle Opener with B | 2.45 | 41% | Moderate similarity |
| 1874 | DEKTON COPING SAW | Eclipse Professional Tools 70-CP1R Copin | 0.66 | 41% | Moderate similarity |
| 2032 | EVERBUILD ONE STRIKE FILLER 250ML | Everbuild â€“ One Strike â€“ Multi-Purpo | 0.15 | 41% | Moderate similarity |
| 1839 | ROLSON  CABEL CUTTING PLIERS VDE INSULAT | S&R VDE Insulated Diagonal Side Cutter 1 | 1.40 | 41% | Moderate similarity |
| 723 | SANCTUARY TREE OF LIFE MIRROR GREY EFFEC | Inspirational Gifting Beautiful green le | 18.46 | 41% | Moderate similarity |
| 593 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE W | Quest 36569 Espresso Coffee Machine With | 33.63 | 41% | Partial match |
| 1205 | BETTINA DUSTPAN AND BRUSH LARGE ASSORTED | Newman and Cole Large Garden Dustpan and | 1.50 | 41% | Moderate similarity |
| 1973 | VIVID BIN FRESHENER PK2 | Vivid 6 x Bin Freshener Smelling FRESH D | 0.14 | 41% | Moderate similarity |
| 354 | SMART CHOICE CHICKEN & RICE BONE DOG TRE | Good Boy - Crunchy Chicken and Rice Bone | 7.89 | 41% | Moderate similarity |
| 592 | WOODEN HANGERS 2 PACK | Amazon Basics 20 Bar Wooden Tie Hanger & | 3.88 | 40% | Moderate similarity |
| 1382 | STATUS UK VISITOR TRAVEL ADAPTER | Status India to UK Power Adaptor, India  | 1.06 | 40% | Partial match |
| 1355 | AMTECH VICE BABY | Amtech D2600 150mm (6") Woodworking vice | 3.04 | 39% | Partial match |
| 1277 | GIFTMAKER PENGUIN SANTA SACK | Giftmaker Collection Large Christmas San | 1.15 | 39% | Partial match |
| 1309 | AMTECH PICK-UP TOOL TELE MAG 5LB | Amtech S8006 3 LED telescopic torch and  | 1.44 | 39% | Partial match |
| 1514 | APOLLO BALLOON WHISK | Apollo Whisk Rainbow, silicone, 26cm, 25 | 0.68 | 38% | Partial match |
| 1681 | DRAPER SINK PLUNGER 135MM | Draper Drain Rod Plunger Attachment 4''  | 0.82 | 37% | Partial match |
| 1805 | YALE ESSENTIALS DEADLOCK P/BRASS 64MM | Yale British Standard 5 Lever Mortice De | 1.62 | 36% | Partial match |
| 1140 | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 1.1L | Addis Clip Tight Food Storage Container  | 2.36 | 35% | Partial match |
| 162 | EVERBUILD SEALANT STRIPOUT TOOL | Everbuild Super Flow Sealant/Adhesive Ca | 28.79 | 35% | Partial match |
| 1085 | MASON CASH MIXING BOWL OWL STONE 26CM | Mason Cash in The Forest Owl Mixing Bowl | 6.54 | 34% | Partial match |
| 785 | MASON CASH MIXING BOWL IN THE MEADOW DAF | Mason Cash in The Forest Hedgehog Mixing | 7.96 | 33% | Partial match |
| 1343 | QUEST TURBO BLENDER 2 IN 1 32129 | Quest Food Processor, 6-in-1 Chopper, Bl | 14.08 | 33% | Partial match |
| 1036 | AMTECH PADLOCK BRASS 20MM | Amtech T0790 Brass Small Padlocks with K | 1.99 | 32% | Partial match |
| 1109 | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN | Superior Foil Containers with Lids â€“ 9 | 4.16 | 32% | Partial match |
| 1505 | EXTRASTAR LED FLASHLIGHT USB REECHARGABL | EXTRASTAR Head Torch Rechargeable, Headl | 1.95 | 31% | Partial match |
| 1122 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | Tidyz 2 X 10 Wheelie Bin Extra Large Lin | 1.23 | 30% | Partial match |
| 1197 | SPONTEX QUICK SPRAY MOP DUO | Spontex Quick Spray Duo Flat Spray Mop w | 12.73 | 30% | Partial match |
| 977 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays wi | 3.28 | 29% | Partial match |
| 1088 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | Superior 10-Pack Aluminium Foil Trays wi | 3.00 | 29% | Partial match |
| 1656 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR | Superior 10-Pack Aluminium Foil Trays wi | 1.48 | 29% | Partial match |
| 1240 | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR | Superior Foil Containers with Lids â€“ 9 | 3.06 | 29% | Partial match |
| 844 | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | Superior Foil Containers with Lids â€“ 9 | 5.00 | 28% | Partial match |
| 718 | EXTRASTAR LED FLASHLIGHT BATTERY TORCH | EXTRASTAR Head Torch Rechargeable, Headl | 4.50 | 28% | Partial match |
| 1690 | TALA MEAT THERMOMETER 4106 | Tala Stainless Steel Meat Thermometer, C | 1.31 | 27% | Partial match |
| 719 | EXTRASTAR LED FLASHLIGHT TORCH | EXTRASTAR Head Torch Rechargeable, Headl | 4.50 | 27% | Partial match |
| 281 | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | Superior 20-Pack 16oz Microwave Containe | 5.30 | 27% | Partial match |
| 1742 | BLUE CANYON LED VANITY MIRROR 17CM X 22C | Blue Canyon 17cm Free Standing Round Swi | 1.36 | 27% | Partial match |
| 1506 | TIDYZ FREEZER BAGS 100 PCS XLLARGE | 100 TidyZ Large Slide Zip Freezer Bags.  | 0.61 | 26% | Partial match |
| 292 | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ | Superior 32oz Food Containers With Lids  | 5.64 | 26% | Partial match |
| 1358 | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | RCR Crystal Melodia Luxion 360 ml Tumble | 7.66 | 25% | Partial match |
| 1664 | TIDYZ RUBBLE BAG HEAVY DUTY 7BAGS 32L | 20 TidyZ Heavy-Duty Rubble Sacks. Made f | 0.41 | 25% | Partial match |
| 1507 | TIDYZ FREEZER BAGS 150PCS | 100 TidyZ Large Slide Zip Freezer Bags.  | 0.61 | 24% | Partial match |
| 1413 | DRAPER WINDOW SQUEEGEE | Draper Telescopic Window Cleaning Equipm | 1.91 | 23% | Partial match |
| 1479 | TIDYZ FOOD BAG 300PCS | 600 TidyZ Food Freezer Bags with TIe Han | 0.66 | 19% | Partial match |
| 607 | THE CHRISTMAS WORKSHOP 40 FAIRY LIGHTS   | 40M 800 LED Fairy Lights Outdoor Christm | 9.31 | 19% | Partial match |

### FILTERED_OUT (98 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | Title Sim | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 2091 | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Price & Kensington Black 6 Cup Teapot | 0.05 | 77% | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 1467 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated  | 1.82 | 72% | Pack 2x makes profit negative |
| 1651 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design ca | 0.29 | 70% | Pack 12x makes profit negative |
| 1647 | ELBOW GREASE FOAMING TOILET CLEANER EUCA | 3 x Elbow Grease Foaming Toilet Cleaner, | 0.82 | 66% | Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1181 | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15 | 3 x Easy Cut Refill Kitchen Foil 300mm,  | 2.90 | 64% | Pack 3x makes profit negative |
| 2003 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner | 0.21 | 64% | Pack 6x makes profit negative |
| 2078 | DETTOL POWER & PURE KITCHEN 750ML PK6 | Dettol Power and Pure Kitchen Cleaner Sp | 0.19 | 63% | Pack 4x makes profit negative |
| 720 | BRIGHT & HOMELY CITRONELLA TEALIGHT CAND | Price's Candles Citronella Tealights - 1 | 2.72 | 62% | Pack 25x makes profit negative |
| 1886 | NUAGE BODY POWDER TALC-FREE CHERRY / WAT | Nuage Body Powder Set - Talc-Free, Cherr | 0.25 | 61% | Pack 2x makes profit negative |
| 1629 | FAIRY DUAL SPONGE SCOURER WITH CRYSTALS  | Addis Fairy Originals Non Scratch Genera | 0.49 | 58% | Pack 6x makes profit negative |
| 1756 | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pyrex Essentials - Set of 3 glass casser | 3.19 | 56% | Pack 3x makes profit negative |
| 1846 | SECURPAK NYLON LOCKING NUT ZINC PLATED M | M12 Nyloc Hex Nut Locking Metal Steel Sh | 0.23 | 56% | Pack 2x makes profit negative |
| 1325 | TALA STAINLESS STEEL ESPRESSO SPOONS SET | Q&A 12 Pieces 4" Stainless Steel Mini Co | 2.17 | 54% | Pack 3x makes profit negative |
| 1148 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK | Bacofoil 3 x Zipper Small All Purpose Ba | 2.17 | 53% | Pack 3x makes profit negative |
| 842 | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC | Pasabahce Istanbul tea glass, set of 6,  | 2.86 | 51% | Pack 6x makes profit negative |
| 313 | DRAPER HSS DRILL BIT 1.5 MM | Draper 18551 Combined HSS and Masonry Dr | 5.16 | 50% | Pack 17x makes profit negative |
| 1003 | PRICES ALADINO JASMINE JAR | Price's Candles - Aladino Jasmine Scente | 1.97 | 50% | Pack 50x makes profit negative |
| 415 | SMART CHOICE 30 BEEF/CHICKEN STICKS | Webbox Dog Delight Variety Pack of 12 (6 | 6.85 | 50% | Pack 12x makes profit negative |
| 1357 | TIDYZ 50 WHITE PEDAL BIN LINERS+HANDLE 1 | Tidyz 3 Packs Of 40 White Plastic Dispos | 0.89 | 48% | Pack 120x makes profit negative |
| 784 | VINERS EVERYDAY PURITY 4PC DINNER KNIFE | Viners Everyday Breeze 16 Piece 18/0 Sil | 6.77 | 47% | Pack 16x makes profit negative |
| 798 | KINGFISHER PLASTIC 15 HALF PINT GLASSES | Plastic Half Pint Glasses 50 Pack Strong | 2.18 | 47% | Pack 50x makes profit negative |
| 1367 | PYREX CLASSIC CASSEROLE 1.3LTR | Pyrex Essentials Glass Round Casserole D | 3.70 | 47% | Pack 2x makes profit negative |
| 915 | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC  | Pasabahce Istanbul tea glass, set of 6,  | 2.73 | 47% | Pack 6x makes profit negative |
| 600 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | 6 x Kilner Clip Top Glass Storage Jar -  | 8.49 | 47% | Pack 6x makes profit negative |
| 1350 | PAN AROMA POTPOURRI ASSORTED | Pan Aroma Set Of 4 Pot Pourri Fragrance  | 1.03 | 43% | Pack 4x makes profit negative |
| 1303 | CORAL EASY COATER 4" & FREE BRUSH | Coral 10501 Easy Coater Paint Kit with H | 2.07 | 42% | Pack 12x makes profit negative |
| 1952 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | The Big Cheese Quick Click Mouse Trap -  | 0.27 | 42% | Pack 2x makes profit negative |
| 1351 | PAN AROMA POTPOURRI ASSORTED 180G | Pan Aroma Set Of 4 Pot Pourri Fragrance  | 1.03 | 41% | Pack 4x makes profit negative |
| 1710 | KILROCK DAMP CLEAR REFILL POUCH 1KG (2x5 | Kilrock Damp Clear Moisture Trap Refill  | 0.90 | 40% | Pack 5x makes profit negative |
| 658 | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HAND | Tidyz 6 Packs Of 40 White Plastic Bin Ba | 2.73 | 39% | Pack 240x makes profit negative |
| 471 | JCB LED BULB WARM WHITE CANDLE SBC 6W/40 | 10 X JCB 6w = 40w LED Opal Candles - 300 | 3.89 | 38% | Pack 10x makes profit negative |
| 1859 | SECURPAK CUP  HOOK WHITE 38MM | Plastic Coated Shouldered Mug Cup Hooks, | 0.22 | 37% | Pack 20x makes profit negative |
| 980 | ROYAL MARKET BIN LINER GARDEN 10 BAG | REQUISITE NEEDS 30PK Heavy Duty Bin Line | 2.10 | 37% | Pack 10x makes profit negative |
| 1934 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LI | Wham Clear Plastic Storage Box Boxes Wit | 0.55 | 37% | Pack 3x makes profit negative |
| 1344 | TURBO JET AIR FRESHENER / SANITISER SPRA | 4 x Mix Bundle New Scents Sovereign Car  | 2.21 | 37% | Pack 4x makes profit negative |
| 1731 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food | 0.78 | 36% | Pack 2x makes profit negative |
| 855 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rolle | 1.59 | 35% | Pack 6x makes profit negative |
| 472 | JCB LED BULB WARM WHITE CANDLE BC 6W/40W | 10 X JCB 6w = 40w LED Opal Candles - 300 | 3.89 | 35% | Pack 10x makes profit negative |
| 2004 | LAV TUMBLER 3PCS | Lav Sude Tumbler Glass Set. Drinking Gla | 0.24 | 35% | Pack 2x makes profit negative |
| 1891 | HEM INCENSE STICKS FRANKINCENSE | HEM Frankincense Incense Sticks  Pack o | 0.39 | 34% | Pack 6x makes profit negative |
| 2098 | WHAM CRYSTAL 160LTR CLEAR BOX & LID | Wham Pack of 2 Crystal Storage Boxes wit | 0.05 | 34% | Pack 2x makes profit negative |
| 2082 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Gla | 0.03 | 34% | Pack 20x makes profit negative |
| 1538 | TIDYZ CARRIERS HANDY BAGS 40 PCS 45CM x  | Tidyz 2 Packs Of 40 Handy Bags - Carrier | 0.59 | 32% | Pack 2x makes profit negative |
| 659 | TIDYZ COMPOSTABLE 15 BAGS 10LTR | Tidyz 6 Packs Of 40 White Plastic Bin Ba | 2.73 | 32% | Pack 16x makes profit negative |
| 937 | HAIR BOBBLES 36PC BROWN BLACK WHITE | 15 Pcs Brown and Black Hair Bobbles, Mix | 1.98 | 32% | Pack 15x makes profit negative |
| 1838 | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4P | Minky Anti-Bacterial Cleaing Pad  3 Pac | 0.40 | 31% | Pack 3x makes profit negative |
| 1313 | CHRISTMAS CRACKER 10 X 12" SANTA AND FRI | Aisszhao 6 Pack Christmas Party Crackers | 3.37 | 31% | Pack 6x makes profit negative |
| 2045 | PYREX BUTTERFLY RECTANGULAR DISH SET OF  | Pyrex - Set of 3 Rectangular Oven Dishes | 0.59 | 31% | Pack 2x makes profit negative |
| 797 | LAV GLASS WHISKEY TUMBLER 345ML 3PCE | Lav Coral Tumbler Glasses. Coloured Base | 4.23 | 29% | Pack 6x makes profit negative |
| 1716 | RUSSELL HOBBS VIENNA CUTLERY SET 16PC | Russell Hobbs RH00022GP Vienna 16 Piece  | 3.32 | 29% | Pack 16x makes profit negative |
| 1057 | DEKTON CHISEL WOOD SET 3PC | Libraton Wood Chisel Set - 4PCs Professi | 8.95 | 29% | Pack 4x makes profit negative |
| 2054 | KILROCK PLUGHOLE FRESHENER CITRUS FRESH  | Kilrock Plughole Unblocker Bathroom 500m | 0.12 | 29% | Pack 2x makes profit negative |
| 1917 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square  | 0.43 | 29% | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1758 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5 | 0.30 | 29% | Pack 40x makes profit negative |
| 1582 | TRAVEL MAKEUP BRUSH SET W/POUCH 18PC | 10 Pcs Mini Travel Makeup Brush Set With | 0.77 | 29% | Pack 10x makes profit negative |
| 1759 | PPS ROUND 150  DOYLEYS 11.5CM | 40 X White Round LACE DOYLEYS - 22cm/8.5 | 0.30 | 28% | Pack 40x makes profit negative |
| 1990 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle,  | 0.22 | 28% | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1827 | BABY PIPKIN BRUSH & COMB SET | Baby Hair Comb, 3PCS Baby Hair Brush and | 0.27 | 28% | Pack 3x makes profit negative |
| 1606 | FLASH MICROFIBRE MOP HEAD | 6 PCS Reusable Mop Refill Pads for Flash | 0.93 | 27% | Pack 6x makes profit negative |
| 2040 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spr | 0.20 | 27% | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1121 | LAV MISKET GIN GLASS 645CC PK3 | 6X Clear 645ml Misket Gin Balloon Glasse | 4.21 | 27% | Pack 6x makes profit negative |
| 553 | PAN AROMA TEALIGHTS 16PC BERGAMOT MANDAR | St Eval  Bergamot & Nettle Scented Teal | 3.89 | 26% | Pack 9x makes profit negative |
| 756 | PAN AROMAREINDEER 12PK CHRISTMAS TEALIGH | St Eval  Orange and Cinnamon Scented Te | 3.31 | 26% | Pack 9x makes profit negative |
| 1784 | SOFTESSE FAMILY FACIAL TISSUES PK24 | 36 x Boxes Ultra Soft Luxurious 100 Whit | 3.73 | 26% | Pack 36x makes profit negative |
| 127 | SQUARE SPICE JAR BLACK/WHITE | Square Spice Jars Set of 24 with Bamboo  | 10.72 | 25% | Pack 24x makes profit negative |
| 986 | CHRISTMAS GIFT BAG PK3 BURGANDY JOY | Christmas Burgundy Gift Bags Medium for  | 2.66 | 25% | Pack 6x makes profit negative |
| 2010 | COOKER HOOD FILTER CHARCOAL | Cooker Hood Filter Kit 3Pack - 2 Grease  | 0.32 | 25% | Pack 3x makes profit negative |
| 1006 | PARTY INVITES BIRTHDAY PK20 | Party Invitations Pack of 36. Blue Starb | 1.62 | 25% | Pack 36x makes profit negative |
| 2068 | ASHLEY RECYCLING BAG SET 3PCE | Vinsani Set of 3 Reusable Fabric Recycli | 0.08 | 25% | Pack 3x makes profit negative |
| 431 | AMTECH FLAT TIP ART B/SET XL 12PC | 5pcs Fuumuui Dual-Layer Synthetic Hair F | 10.54 | 25% | Pack 5x makes profit negative |
| 1152 | DRAPER HEX KEY SET METRIC DIY 8 PC | Draper 10 Piece T-Handle Hexagon Allen K | 2.66 | 24% | Pack 10x makes profit negative |
| 2028 | ALBERO BOTTLE 500ML TRANSPARENT PK12 | Volila Glass Bottles with Stoppers 500ml | 0.54 | 23% | Pack 6x makes profit negative |
| 751 | STATUS LED ROUND SES PA PEARL W/WHT 1PK  | 100Pcs CD DVD Sleeves, Standard Plastic  | 2.73 | 23% | Pack 100x makes profit negative |
| 1776 | CHEF AID PASTRY CUTTERS  W184 | Chef Aid Pastry Cutters, Set Of 3, Cooki | 0.38 | 22% | Pack 3x makes profit negative |
| 576 | HEM INCENSE STICKS LEMON | HEM Incense Sticks - 18 unique and premi | 6.41 | 22% | Variant mismatch: Scent: ['LEMON'] vs ['LEMON', 'LAVENDER'] |
| 1996 | APOLLO PAPER SMOOTHIE 20 STRAWS | Boba Straws Disposable Bubble Tea Smooth | 0.10 | 22% | Pack 50x makes profit negative |
| 1668 | MINKY ALL PURPOSE CLOTH PK10 | Minky Anti-Bacterial Cleaing Pad  3 Pac | 0.59 | 21% | Pack 3x makes profit negative |
| 1311 | BEAU MERMAID 12PK HAIR TIES W/ STARFISH | Hair Scrunchies, 8 Pack Shiny Metallic S | 1.06 | 20% | Pack 8x makes profit negative |
| 514 | DEKTON HOBBY KIT 7PC | Aussel Gundam Model Tools Kit, Model Bas | 4.76 | 20% | Pack 26x makes profit negative |
| 649 | PETS PLAY RUBBER BALLS | Pets & Play Squeaky Dog Ball 6 Pack  Up | 4.04 | 20% | Pack 6x makes profit negative |
| 1753 | LAV FAME WINE GLASS 30CL PK3 | LAV Stemless Red & White Wine Glasses Tu | 0.86 | 20% | Pack 6x makes profit negative |
| 1929 | PASABACHE 6 PC ROYAL SMALL FOOD SAVER 23 | Bonsenkitchen Precut Vacuum Sealer Bags, | 0.67 | 20% | Pack 200x makes profit negative |
| 1473 | MINKY SUPER DIAMOND SCRUBBER | Minky Anti-Bacterial Cleaing Pad  3 Pac | 0.84 | 19% | Pack 3x makes profit negative |
| 551 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack o | 3.90 | 19% | Pack 10x makes profit negative |
| 1782 | MINKY BRITES FLAT SCOURING PAD 4PC | Minky Anti-Bacterial Cleaing Pad  3 Pac | 0.47 | 19% | Pack 3x makes profit negative |
| 1652 | DEKTON DENT PULLER SUCTION | Car Dent Puller,Dent Removal kit, 2 Pack | 1.08 | 19% | Pack 2x makes profit negative |
| 542 | GLASS BOTTLE 120ML | Glass Shot Bottles with Lids - 12 Pack 1 | 3.04 | 18% | Pack 12x makes profit negative |
| 1262 | GLASS MUG DELI 270ML ZB229 6PK | Glass Coffee Mugs Set of 6 Heat Resistan | 3.70 | 18% | Pack 6x makes profit negative |
| 1763 | TALA SILICONE SPATULA | GMY G9 Halogen Oven Bulb 25W 230V 300â„ƒ | 0.71 | 18% | Pack 4x makes profit negative |
| 2079 | AMTECH DOUBLE SIDED STORAGE BOX 34 SECTI | JOREST 59Pcs Small Precision Screwdriver | 0.15 | 15% | Pack 59x makes profit negative |
| 1991 | CANDLE JAR BOHO 9X19CM | Glass Candle Cylinder Holders â€“ Set of | 0.49 | 14% | Pack 3x makes profit negative |
| 1328 | SMART CHOICE PUPPY/SMALL DOG ROPE TOY 5P | XL Dog Rope Toys for Aggressive Chewers  | 1.60 | 13% | Pack 2x makes profit negative |
| 1672 | PPS FOOD CONTAINERS & LIDS PLASTIC RECTA | Superior Takeaway Containers with Lids â | 1.77 | 11% | Pack 20x makes profit negative |
| 563 | BROOKSTONE AIR FRESH TINS | Sopito Aluminum Tin Cans, 24pcs 60ml/2oz | 5.27 | 10% | Pack 24x makes profit negative |
| 1052 | BAUBLE 15CM SILVER | LOLStar Christmas Window Lights, 3 Pack  | 3.17 | 7% | Pack 3x makes profit negative |
| 2095 | HAND BRUSH VARNISH RED | Xtremeauto 5pc Paint Brush Set â€“ Synth | 0.01 | 4% | Pack 5x makes profit negative |
| 810 | BLACKSPUR SEL DRILL PLASTERBOARD FIXING  | NCaan 20pk Heavy Duty Metal Self-Drill P | 1.99 | 4% | Pack 20x makes profit negative |
| 697 | SIL CRAFT PAINT POTS | Mini Acrylic Paint Set, 10pcs 8Colors Ac | 2.88 | 0% | Pack 10x makes profit negative |

### LOW_PRIORITY (85 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | Title Sim | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 172 | AMTECH RECHARGEABLE WORK LIGHT WITH MAGN | T-SUN Rechargeable LED Work Light with M | 32.02 | 40% | Weak match |
| 1926 | PREMIER FLICKABRIGHT GLASS SPHERE CANDLE | Premier Decorations Red LED Flickabright | 0.51 | 40% | Weak match |
| 538 | SPECIAL OCCASIONS RAINBOW COLOUR HAIR SP | 6 * 200ml Cans Rainbow Colour Hair Spray | 4.13 | 40% | Weak match |
| 1195 | CANDLE PLATE 10CM | Silver Round Metal Spike Candle Holder P | 1.58 | 40% | Weak match |
| 1047 | PREMIER FLICKABRIGHT TEALIGHT CANDLE 7.3 | Premier Decorations Red LED Flickabright | 2.35 | 40% | Weak match |
| 1581 | APOLLO STAINLESS STEEL JAR OPENER 11/11 | Manual Can Openers Jar Can Opener,Adjust | 0.93 | 39% | Weak match |
| 1289 | SABICHI STAINLESS STEEL 16CM SAUCEPAN | Judge Vista Stainless Steel Medium Sauce | 5.04 | 39% | Weak match |
| 1960 | PPS FOIL ROASTING 3 DISHES | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 0.17 | 39% | Weak match |
| 1108 | MUNCH CRUNCH RAWHIDE BONE NAT JUMBO | Munch & Crunch Bone Chews for Dogs Multi | 1.66 | 39% | Weak match |
| 749 | PAN AROMA CANDLE 85G LEMONGRASS | Pan Aroma Orange Decorative Holder & Sce | 2.73 | 39% | Weak match |
| 856 | PAN AROMA CANDLE 85G LIME GINGER | Pan Aroma Orange Decorative Holder & Sce | 2.56 | 38% | Weak match |
| 2042 | SISTEMA TO GO BREAKFAST BOX | Sistema Klip It Colour Accents Breakfast | 0.18 | 38% | Weak match |
| 1532 | PRICES PILLAR CANDLE 6 INCH RED | Price's Candles - 6" Red Pillar Candles  | 1.01 | 38% | Weak match |
| 748 | PAN AROMA CANDLE 85G PURE JASMINE | Pan Aroma Orange Decorative Holder & Sce | 2.73 | 38% | Weak match |
| 464 | APOLLO CHROME TOILET BRUSH & HOLDER | BGL 304 Stainless Steel Toilet Brush Lon | 12.09 | 38% | Weak match |
| 497 | PPS SERVING PLATTER REUSABLE PLASTIC WHI | MATANA 6 White Rectangular Serving Platt | 3.29 | 38% | Weak match |
| 1624 | ROYALFORD STAINLESS STEEL PESTLE AND MOR | Bekith Mortar and Pestle Sets 18/8 Brush | 1.58 | 38% | Weak match |
| 1687 | BUTTERFLY AND RAINBOW HAIR CLIPS 4PC | Toddler Girls Butterfly Snap Clips,Lovel | 0.44 | 37% | Weak match |
| 1861 | ROYALFORD STAINLESS STEEL PESTLE AND MOR | Bekith Mortar and Pestle Sets 18/8 Brush | 0.89 | 37% | Weak match |
| 1946 | HAPPY BIRTHDAY BANNER | Happy Birthday Banner and Decoration - B | 0.15 | 37% | Weak match |
| 1565 | CHEF AID STAINLESS STEEL TEA BAG SQUEEZE | Tea Bag Squeezer, Stainless Steel Holder | 0.59 | 37% | Weak match |
| 724 | SANCTUARY TREE OF LIFE MIRROR WHITE EFFE | Inspirational Gifting Beautiful green le | 18.46 | 37% | Weak match |
| 1670 | CASA & CASA CLASSICO STAINLESS STEEL KNI | Joeji's Kitchen Universal Knife Block Wi | 2.29 | 37% | Weak match |
| 1711 | MASTERCOOK CASSEROLE SET 20-22-24CM 3 PI | Amazon Basics 3-Piece Stainless Steel Sp | 5.42 | 37% | Weak match |
| 428 | MASON HEAVY DUTY SPRING CLAMPS 4" 2 PIEC | 10 Pieces Large Nylon Spring Clamps, 6 I | 4.62 | 37% | Weak match |
| 330 | BRIGHT & HOMELY FOIL PIE DISHES 215MM X  | 110 mm x 33 mm Round Foil Container - Pi | 4.84 | 37% | Weak match |
| 1114 | SOZALI KLIPSEAL FOOD CONTAINER RECTANGLA | 10 Ã— 500ml Plastic food containers with | 1.41 | 37% | Weak match |
| 1107 | MUNCH CRUNCH RAWHIDE PRESSED BONE | Munch & Crunch Bone Chews for Dogs Multi | 1.66 | 37% | Weak match |
| 1462 | BRIGHT & HOMELY SCENTED TEALIGHTS 15PCE | 20pc Scented Tealights Night Candle Blac | 0.81 | 37% | Weak match |
| 760 | BRIGHT & HOMELY CITRONELLA CANDLE IN GLA | ANGIX 4 x Citronella Candles in Glass Ja | 2.57 | 36% | Weak match |
| 1418 | PRICES PILLAR CANDLE 6 INCH GREEN | Price's Candles - 6" Evergreen Pillar Ca | 1.32 | 36% | Weak match |
| 1347 | RENTOKIL CLOTHES MOTH GLUE TRAP REFILLS  | 10-Pack Clothes Moth Monitoring Traps â€ | 2.63 | 36% | Weak match |
| 1207 | WHEELED STORAGE BOX & LID 150LTR | Strata Heavy Duty Large Storage Box with | 13.49 | 36% | Weak match |
| 941 | PPS FOIL PLATTERS 2PCS 352X247X25MM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 1.65 | 36% | Weak match |
| 807 | BETTINA WASHING UP BRUSH & REFILL | Premium Soap Dispenser Washing Up Brush  | 2.72 | 36% | Weak match |
| 793 | ECO WISE PAPER CUPS LIDS 8OZ PK25 | 100 Paper Cups - Disposable Paper Cups f | 2.19 | 36% | Weak match |
| 778 | DEKTON HIGH POWER TYPE C RECHARGEABLE FL | WUBEN E7 1800 Lumen Torch Light with Mag | 9.77 | 36% | Weak match |
| 1263 | ESSENTIAL PLASTIC SERVING TRAY CLEAR REU | MATANA 6 Large Rectangular Serving Platt | 1.61 | 36% | Weak match |
| 1143 | ROLSON BIKE INNER TUBE 27.5X2.1-2-5 | Continental MTB 27.5" x 1.75-2.5 Mountai | 2.73 | 36% | Weak match |
| 802 | BLACKSPUR CAR HEADLIGHT BULB 12V 60W/55W | Bosch H4 (472) Pure Light Halogen Headli | 3.31 | 36% | Weak match |
| 922 | APOLLO MEGA ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rollin | 4.16 | 36% | Weak match |
| 1423 | KINGAVON HEAD BAND WITH MOTION SENSOR &  | Lumi Light Led Headband Ultra Bright 230 | 3.64 | 36% | Weak match |
| 168 | WAX WORKS PILLAR CANDLE 30 HOURS | WoodWick Large Hourglass Scented Candle  | 10.16 | 35% | Weak match |
| 662 | BRIGHT & HOMELY SAUCEPAN NON STICK COOKW | 11Pcs Pots and Pans Set, Nonstick Cookwa | 18.61 | 35% | Weak match |
| 557 | APOLLO ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rollin | 5.11 | 35% | Weak match |
| 859 | APOLLO ROLLING PIN EACH | Tuuli Kitchen Professional Wooden Rollin | 4.99 | 35% | Weak match |
| 979 | PPS FOIL 3 BAKE TRAY RECTANGULAR | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 1.61 | 35% | Weak match |
| 792 | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6P | 100 Paper Cups - Disposable Paper Cups f | 2.19 | 35% | Weak match |
| 761 | CITRONELLA CANDLE IN GLASS POT | ANGIX 4 x Citronella Candles in Glass Ja | 2.57 | 35% | Weak match |
| 345 | ADORN GLASS STAR TEALIGHT HOLDER | Set of 4 Clear Glass Tealight Holders, V | 4.86 | 35% | Weak match |
| 459 | BABY PIPKIN CLASSIC ROUND BABY BOTTLE 5o | Dr Brown's Natural FlowÂ® Anti-Colic Opt | 3.92 | 35% | Weak match |
| 651 | THE BIG CHEESE NEO ZAP ELECTRONIC RAT KI | The Big Cheese Ultra Power - Electronic  | 6.67 | 35% | Weak match |
| 1845 | ULTRA FLASHBAND LEAD FINISH 150MMX3M | Bostik Flashband Self Adhesive Flashing  | 0.95 | 35% | Weak match |
| 1412 | PANORAMA COFFEE MUG 145ML 6 PIECES | 6X Turkish Glass Tea Cups Stylish Latte  | 2.13 | 35% | Weak match |
| 2063 | AMTECH TENNON SAW 12INCH | Irwin 10503534 12T/13P XP3055-300 Jack T | 0.11 | 34% | Weak match |
| 613 | WHAM CRYSTAL 60LTR SMOKE BOX & LID | Wham Crystal 5 x 60L Stackable Plastic S | 13.81 | 34% | Weak match |
| 831 | RUBBER DUCK FAMILY BATH TOY 3 PACK | Rubber Duck Bath Toy Set â€“ Floating Du | 2.13 | 34% | Weak match |
| 881 | WORLD OF PETS SALMON SHAPED DOG TREAT PK | Dog Biscuit Treats 2.5L (Salmon Burgers) | 2.00 | 34% | Weak match |
| 1060 | WHAM CRYSTAL 32LTR SMOKE BOX & LID | Wham Crystal 5 x 32L Stackable Plastic S | 5.02 | 34% | Weak match |
| 1935 | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550M | Addis Clip Tight Food Storage Container  | 0.24 | 34% | Weak match |
| 616 | LAV FAME WINE GLASS 40CL PK3 | LAV 12x Clear 400ml Lal Red Wine Glasses | 8.11 | 34% | Weak match |
| 940 | MUNCH N CRUNCH BIG BONE BISCUITS 3PK 150 | Munch & Crunch Bone Chews for Dogs Multi | 1.89 | 34% | Weak match |
| 1300 | PPS FOIL CONTAINER & LID SHALLOW NO.9 23 | Large Aluminium Foil Trays Food Large Co | 1.99 | 33% | Weak match |
| 1083 | MASON PRECISION SCREWDRIVER SET 6 PIECES | Shall 6-Piece Precision Screwdriver Set  | 1.54 | 33% | Weak match |
| 1095 | PRIMA HEART SHAPED BAKE PAN 23CM | Prima Set Of 2 Heart Shaped Cake Tins, R | 1.94 | 33% | Weak match |
| 1266 | RCR CRYSTAL MIXOLOGY WHISKY GLASS SET AS | KANARS Whiskey Glasses Set, No-Lead Crys | 8.44 | 33% | Weak match |
| 643 | SPLATTER SCREEN GUARD 2PC SILVER 24/28CM | Snowyee Splatter Screen for Frying Pan,  | 3.79 | 33% | Weak match |
| 1426 | PAN AROMA INCENSE STICKS & HOLDER PATCHO | Original Satya Nag Champa Patchouli Ince | 0.91 | 32% | Weak match |
| 1919 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BI | Rolson 51 pc Screwdriver & Bit Set (Chro | 0.43 | 32% | Weak match |
| 715 | COTTON BUDS IN JAR 12X6CM 50 PCS | Cotton Bud Holder 10 Oz Bathroom Jars wi | 2.63 | 32% | Weak match |
| 1568 | HAPPY BIRTHDAY TRI CUT BUNTING | Happy Birthday Bunting Banner, 6.6 Ft He | 0.57 | 32% | Weak match |
| 757 | PAN AROMA JAR CANDLE 85GM APPLE CINNAMON | Luxury Scented Candle â€“ Warm Apple & C | 2.70 | 32% | Weak match |
| 931 | BRIGHT & HOMELY LAUNDRY BAG XLARGE 86CM  | Car Boot Organiser with Cooler Bag, Extr | 15.23 | 32% | Weak match |
| 1982 | PPS PLASTIC GLASSES PINT 50PCS | CHEF ROYALE 50 Disposable Clear Plastic  | 0.24 | 32% | Weak match |
| 1495 | PAN AROMA FRAGRANCE OILS JUICY BERRIES / | MAYJAM Fragrance Oil, 100ML Orchid Bloss | 0.79 | 31% | Weak match |
| 984 | BRIGHT & HOMELY HANGERS WOODEN 2 PACK | HANGERWORLD Box of 10 Wooden 45cm Coat C | 1.93 | 31% | Weak match |
| 1810 | BRIGHT & HOMELY HANGERS WOODEN 5 PACK | HANGERWORLD Box of 10 Wooden 45cm Coat C | 0.59 | 31% | Weak match |
| 716 | BABY PIPKIN SILICONE PACIFIER | Baby Fruit Feeder Set, Includes 2 Food D | 2.48 | 31% | Weak match |
| 841 | ESSCENTS HOME INCENSE SET 30PC STICKS&HO | Incense Sticks Gift Set, 180 Joss Incens | 2.73 | 31% | Weak match |
| 867 | PPS FOIL ROAST DISH OVAL 46CM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 1.71 | 31% | Weak match |
| 1662 | WAX MELT NAGCHAMPA 6PCS | Nag Champa - Highly Scented 100% Soy Wax | 0.47 | 31% | Weak match |
| 771 | BLACKSPUR FACE MASK WITH VALVE 3PC | Face Masks - Breathable Face Masks with  | 4.03 | 31% | Weak match |
| 1684 | PPS FOIL PLATTERS 550X362X30MM | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 0.41 | 31% | Weak match |
| 1867 | PAN AROMA INCENSE STICKS & HOLDER SANDAL | Satya Nag Champa Sandalwood Incense Stic | 0.26 | 30% | Weak match |
| 1840 | PPS FOIL PIZZA 2 PLATTERS | PPS 3 x ALUMINIUM FOIL PLATTER TRAY - 44 | 0.28 | 30% | Weak match |

### OTHER (128 products)
| Row ID | SupplierTitle (Truncated) | AmazonTitle (Truncated) | Profit | Title Sim | Reason |
|--------|---------------------------|-------------------------|--------|---|--------|
| 579 | Dog Figure '8' Knot Ball Rope Toy(12/48) | Dog Pet Puppy Chew Toys for Teething Bor | 3.24 | 30% | Insufficient evidence |
| 1237 | KINGFISHER 3PK SMALL VACUUM BAGS VBS | Vacuum Storage Bags,10 Small Space Saver | 2.71 | 30% | Insufficient evidence |
| 1042 | DEKTON RAZOR SINGLE EDGE BLADE 10PC | Derby Premium Single Edge (Half) Razor B | 1.42 | 30% | Insufficient evidence |
| 1365 | WORLD OF PETS CAT TOY TEASER WITH BELL | Cat Teaser Pet Kitten Toy - Bell, Stick, | 0.97 | 30% | Insufficient evidence |
| 1900 | KILROCK MOULD & MILDEW REMOVER BRUSH ON  | Kilrock Mould Remover Brush-On Gel 2 x 2 | 0.43 | 29% | Insufficient evidence |
| 1654 | EXPRESS DECANTER SQUARE 1160ML | BarCraft Wine Decanter, Wine Aeration Gl | 1.04 | 29% | Insufficient evidence |
| 1785 | ROLSON  ADJUSTABLE WRENCH 3PC SET 6,8,10 | Shall 3-Piece Adjustable Wrench Set, 10/ | 1.96 | 29% | Insufficient evidence |
| 1115 | THL BOWL PLASTIC REUSABLE SMALL 36PCS | MATANA 40 Small Clear Plastic Bowls (150 | 1.35 | 29% | Insufficient evidence |
| 1131 | ASHLEY OVER THE DOOR HANGER 6 HOOK | Over Door Hanger, 6 Hooks Over The Door  | 2.00 | 29% | Insufficient evidence |
| 366 | CHRISTMAS TEALIGHTS SPICED CINNAMON 10 P | St Eval  Orange and Cinnamon Scented Te | 4.04 | 29% | Insufficient evidence |
| 1406 | FALSE EYELASHES 4 ASSTD DESIGNS. | False Eyelashes 4 Pairs - Professional R | 0.91 | 29% | Insufficient evidence |
| 2001 | MINKY WASHING LINE PROP SUREGRIP | Minky Retractable Reel Washing Line with | 0.38 | 29% | Insufficient evidence |
| 1953 | RUSTINS SCRATCH COVER-DARK 125ML | Rustins Scratch Cover Dark â€“ Conceal S | 0.31 | 29% | Insufficient evidence |
| 163 | PPS PLASTIC PLATE 3CPMPARTMENTS WHITE 26 | MATANA 25 Premium White Plastic Dinner P | 7.97 | 29% | Insufficient evidence |
| 318 | ROLSON DOUBLE OPEN END SPANNER 5PC SET | DURATECH Double Open End Spanner Set, Su | 11.85 | 29% | Insufficient evidence |
| 1661 | DLUX PRO KLEEN MICROFIBRE BATHROOM & KIT | DLUX PRO-KLEEN Super Absorbent Chenille  | 0.38 | 29% | Insufficient evidence |
| 485 | CHAMPAGNE GLASS PLASTIC ASSORTED 177ML | MATANA 24 Premium Plastic Champagne Flut | 3.78 | 28% | Insufficient evidence |
| 1800 | PPS FOIL CONTAINER & LID DEEP NO.9 235x2 | Caterserve 10 Aluminium Foil Trays with  | 0.68 | 28% | Insufficient evidence |
| 478 | DELICIOUS POUCH MEATY STICKS PK7 | Good Boy Meaty Sticks Variety Pack - Nat | 4.18 | 28% | Insufficient evidence |
| 253 | DEKTON CABLE TIES BLACK 100PCS 4.8MMX300 | XINGO Black Cable Ties Pack of 1000, 300 | 11.39 | 28% | Insufficient evidence |
| 511 | LAV NECTAR TUMBLER 3PC 280ML | LAV 12x 280ml Nectar Glass Tumblers - Di | 7.66 | 28% | Insufficient evidence |
| 2074 | CABANA ROUND TINS  SET OF 3 | Cooksmart English Meadow Set of 3 Round  | 0.14 | 28% | Insufficient evidence |
| 1569 | SUNNEX PK4 DESSERT FORKS PLAIN | Silver 10-Piece Stainless Steel Fork Set | 0.82 | 28% | Insufficient evidence |
| 1944 | WINDOW STYLE WALL MIRROR  70X36 | Window Style Mirror - Living Room Decor  | 1.06 | 27% | Insufficient evidence |
| 142 | PUREBREED KNOTS COLLAGEN MEDIUM PACK OF  | Pura Collagen Powdered Supplement Glow+, | 14.22 | 27% | Insufficient evidence |
| 1592 | WORLD OF PETS SALMON STICKS DOG TREAT PK | SKIPPER'S Salmon Meat Sticks Dog Treats  | 0.56 | 27% | Insufficient evidence |
| 791 | FAIRY DISH BRUSH 3 REFILLS | Fillable Washing up Brush and Sponge - E | 2.80 | 27% | Insufficient evidence |
| 676 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS 1 | Caterserve 10 Aluminium Foil Trays with  | 2.51 | 27% | Insufficient evidence |
| 675 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS 1 | Caterserve 10 Aluminium Foil Trays with  | 2.51 | 27% | Insufficient evidence |
| 566 | WICKED STATIONERY BACKPACK | WICKED Backpack, Glinda And Elphaba Girl | 7.72 | 27% | Insufficient evidence |
| 641 | MASON NAIL ASSORTMENT 124 PIECES | Brackit 2,000 Piece Nail Assortment Set  | 3.19 | 27% | Insufficient evidence |
| 1458 | FESTIVE MAGIC LED B/O TIMER 200  LIGHTS  | Sloth Night Light, Cute Squishy Lamp for | 3.63 | 27% | Insufficient evidence |
| 721 | CITRONELLA GARDEN TORCH ASSORTED | CUQOO 1L Scented Citronella Oil for Gard | 4.49 | 27% | Insufficient evidence |
| 515 | ADORN REUSABLE SHOT GLASSES COLORED 20 P | Volila Heavy Base Shot Glasses - 25ml (6 | 3.45 | 27% | Insufficient evidence |
| 903 | EASY WASHING POWDER COLOUR 13 WASH PK6 | Persil Non Bio Colour Washing Powder 8.4 | 10.37 | 27% | Insufficient evidence |
| 1987 | BRIGHT & HOMELY JUTE TWINE GREEN 50M | KINGLAKE 50m Garden Twine String Green,  | 0.09 | 26% | Insufficient evidence |
| 924 | APOLLO BAMBOO SKEWERS PK100 | Lanjue 200 Paddle Bamboo Skewers 9CM, Fl | 1.92 | 26% | Insufficient evidence |
| 1073 | BRIGHT & HOMELY FOIL CONTAINERS & LIDS S | Caterserve 10 Aluminium Foil Trays with  | 1.95 | 26% | Insufficient evidence |
| 170 | PUREBREED KNOTS COLLAGEN SMALL PACK OF 5 | Pura Collagen Powdered Supplement Glow+, | 12.44 | 26% | Insufficient evidence |
| 388 | PPS PLASTIC SALAD BOWL WHITE 50OZ 5PCS | MATANA 25 Premium White Plastic Bowls wi | 4.60 | 26% | Insufficient evidence |
| 1648 | BRIGHT & HOMELY PLUNGER WOODEN HANDLE HE | Large Black Toilet Plunger 150mm 6 Inch  | 0.97 | 26% | Insufficient evidence |
| 595 | FESTIVE MAGIC SANT SLEIGH FELT BUCKET | Festive Childrens Holding DIY Sleigh - L | 4.84 | 26% | Insufficient evidence |
| 1727 | INCENSE STICKS SACRED WOOD PACK OF 12 | Natural Incense Sticks Multipack Variant | 1.51 | 26% | Insufficient evidence |
| 2005 | PPS FOIL CONTAINERS 1/3 GASTRO WITH LIDS | Caterserve 10 Aluminium Foil Trays with  | 0.25 | 26% | Insufficient evidence |
| 861 | DEKTON HSS DRILL 13PC SET 2MM TO 8MM | Bosch Professional 9pc PointTeQ Hex Dril | 5.39 | 26% | Insufficient evidence |
| 965 | ROYAL MARKET PAPER PLATES 9INCH 30 PACK | Strong Paper Plates (9 Inch / 50-Pack) 1 | 1.54 | 26% | Insufficient evidence |
| 1491 | CONCORD CRYSTAL SERIES  HIBALL PK6 | RCR 6X 396ml Crystal Glass Highball Glas | 2.63 | 26% | Insufficient evidence |
| 239 | CHRISTMAS PIPE CLEANERS 40PC | PLULON 60 Sets Christmas Crafts for Kids | 5.67 | 25% | Insufficient evidence |
| 1830 | SOZALI SQUARE FOOD BOX 700ML 2PC | Sistema Ultra Airtight Pantry Storage Co | 0.35 | 25% | Insufficient evidence |
| 1750 | RUBBER RING & BONE DOG TOYS 3 COLOURS | Nerf Dog 3-Ring Rubber Tug Toy, 10.5-Inc | 0.55 | 25% | Insufficient evidence |
| 225 | BOWL GLASS FLOWER 15CM 4 ASSORTED COLOUR | YOUEON 4 Pack Small Glass Bubble Bowl Va | 9.39 | 25% | Insufficient evidence |
| 946 | ADORN SHOWER CURTAIN DELUXE | Shower Curtains Mould Proof Resistant, E | 4.39 | 25% | Insufficient evidence |
| 817 | EXFOLIATING GLOVES PAIR | Exfoliating Wash Gloves, Shower Scrub Gl | 2.35 | 25% | Insufficient evidence |
| 813 | PRO USER FLAT DRILL BIT 15PC SET | Bosch 7x EXPERT Self Cut Speed Spade Dri | 8.25 | 25% | Insufficient evidence |
| 928 | BRIGHT & HOMELY HANGERS VELVET NON SLIP  | 20 Non Slip Velvet Hangers  Heavy Duty  | 3.19 | 25% | Insufficient evidence |
| 164 | PPS 26CM PLASTIC WHITE PLATE 6 PCS | MATANA 25 Premium White Plastic Dinner P | 7.97 | 24% | Insufficient evidence |
| 1586 | PPS FOIL CONTAINER & LID 260x188x68MM 10 | Caterserve 10 Aluminium Foil Trays with  | 1.11 | 24% | Insufficient evidence |
| 2036 | GEEPAS RICE COOKER 0.6LTR | Geepas Rice Cooker, 0.6L  Electric Rice | 0.74 | 24% | Insufficient evidence |
| 1400 | DEKTON SMOOTHING PLANE | Draper Expert 250mm Smoothing Beech Wood | 4.06 | 24% | Insufficient evidence |
| 1866 | PPS BAGASSE WHITE PLATE 26CM  50PC | Disposable Paper Plate 10 Inch Heavy Dut | 0.63 | 24% | Insufficient evidence |
| 2092 | ULTRATAPE FLASHBAND LEAD 100MMX10M | Bostik Flashband Self Adhesive Flashing  | 0.07 | 24% | Insufficient evidence |
| 1669 | BARBIE DIY FASHION SET | Barbie DIY Fashion Designer Set â€“ Make | 1.53 | 24% | Insufficient evidence |
| 2099 | CHEF AID FLUTED CAKE RING | Chef Aid Non-Stick Fluted Cake Pan with  | 0.01 | 24% | Insufficient evidence |
| 1026 | LAV WHISKEY TUMBLER 3PCS | Lav Coral Tumbler Glasses. Coloured Base | 3.67 | 24% | Insufficient evidence |
| 705 | BRIGHT & HOMELY FOIL ROASTING TRAY 320MM | Caterserve 10 Aluminium Foil Trays with  | 2.46 | 23% | Insufficient evidence |
| 1587 | BRIGHT & HOMELY FOIL ROASTING TRAY 525MM | Caterserve 10 Aluminium Foil Trays with  | 1.11 | 23% | Insufficient evidence |
| 2059 | MEMORIAL PLASTIC SPIKE SPECIAL DAD | David Fischhoff Special Dad Verse Graves | 0.08 | 23% | Insufficient evidence |
| 1948 | AIRWICK FRESHMATIC REFILL PINK SWEET PEA | Air Wick Automatic Air Freshener Freshma | 1.03 | 23% | Insufficient evidence |
| 1972 | CARRIERS BAGS SMALL PK100 | 100 White Plastic Carrier Bags â€“ Vest- | 0.13 | 23% | Insufficient evidence |
| 674 | BRIGHT & HOMELY FOIL ROASTING TRAY SQUAR | Caterserve 10 Aluminium Foil Trays with  | 2.51 | 23% | Insufficient evidence |
| 208 | BRIGHT & HOMELY HANGERS VELVET NON SLIP  | 50 Non Slip Velvet Hangers  Heavy Duty  | 9.05 | 23% | Insufficient evidence |
| 1595 | BARTOLINE EASIPASTE 1KG | Bartoline EasipasteÂ® Ready Mixed Wallpa | 1.38 | 23% | Insufficient evidence |
| 1620 | BEAU MERMAID 4PK PEARL WAVE  HAIR CLIPS  | Pearl Hair Clip - ShiningUU 2-Pack 3.3cm | 0.53 | 22% | Insufficient evidence |
| 1884 | GLAMOUR CONNECTION DETANGLES HAIR BRUSH/ | Hair Detangling Brush with Bending Brist | 0.22 | 22% | Insufficient evidence |
| 348 | WAX MELTS YOGA 68G 6 PCS | Mixed Perfume Wax Melts: 16 x 6g Heart S | 5.42 | 22% | Insufficient evidence |
| 645 | PPS NAPKINS 1PLY WHITE 30X30CM 100PCS | 500 x White Serviettes Paper Napkins (30 | 2.39 | 22% | Insufficient evidence |
| 1034 | DEKTON CIRCLIP PLIERS 5PC SET | WISEUP Pliers Set, 170mm 4-Piece Bent/St | 4.62 | 22% | Insufficient evidence |
| 656 | PPS BAGASSE PLATE 26CM 10 PIECES | Disposable Paper Plate 10 Inch Heavy Dut | 2.87 | 22% | Insufficient evidence |
| 1333 | PRIMA DESSERT FORK 6PCS | 6 Pcs Dessert Forks, 13.8cm Stainless St | 1.00 | 21% | Insufficient evidence |
| 661 | FESTIVE MAGIC VINTAGE RIBBON 63MM X 2.7M | Christmas Velvet Ribbon - Thick Red Wire | 2.85 | 21% | Insufficient evidence |
| 1234 | YOGA ORNAMENT IN BAG 6CM | Yoga Gift for Yoga Instructor Yoga Acces | 1.47 | 21% | Insufficient evidence |
| 1790 | PPS FOIL BBQ DRILL ROUND 2 TRAY 34CM | Large Aluminium Foil Trays Food Large Co | 0.32 | 21% | Insufficient evidence |
| 1468 | MONEY TIN BOX ASST LARGE | KAV Jumbo Large Money Tin Box (22 CM) -  | 1.19 | 21% | Insufficient evidence |
| 679 | SPRING FLORAL CANDLE POTS SET OF 3 | Scented Candles Gift Set, Gifts for Wome | 7.17 | 21% | Insufficient evidence |
| 681 | FESTIVE MAGIC GIFT WRAPPING SET 14PC | 70x50cm Christmas Wrapping Paper Sheets  | 4.13 | 21% | Insufficient evidence |
| 565 | SIL INCENSE HEX STICKS PK4 FLOWER | Natural Incense Sticks Multipack Variant | 4.89 | 21% | Insufficient evidence |
| 1984 | CARRIERS BAGS CHEETAH PK100 | 100 White Plastic Carrier Bags â€“ Vest- | 0.26 | 21% | Insufficient evidence |
| 1182 | APOLLO JULIENNE PEELER | Marshland Premium Y-Shape Julienne Veget | 1.23 | 21% | Insufficient evidence |
| 993 | DEKTON  PAINT SCRAPER SET 2PC | Heavy Duty Long Handle Scraper Tool â€“  | 3.42 | 20% | Insufficient evidence |
| 1177 | BLACKSPUR LONG LINK CHAIN 2.5MM X2.5M | Stainless Steel Chains, 5 Metre Heavy Du | 1.46 | 20% | Insufficient evidence |
| 1020 | BBQ KITCHEN GLOVE 32CM 3ASS | BBQ Gloves, 1472Â°F Heat Resistant Glove | 4.13 | 20% | Insufficient evidence |
| 404 | FLOWER SHOP INCENSE STICKS PK40 | Natural Incense Sticks Multipack Variant | 5.26 | 20% | Insufficient evidence |
| 2012 | MULTI COLOURED HAIR BANDS 8PK | Elastic Hair Bands, 1500 pcs Mini Rubber | 0.10 | 20% | Insufficient evidence |
| 241 | DELICIOUS POUCH MEATY SAUSAGE PK7 | Forthglade Meaty Sausages (4 x 100g Bags | 7.48 | 20% | Insufficient evidence |
| 30 | LYNWOOD MINI ROLLER SET 5PACK | Mould King V8 Engine Building Blocks Set | 65.52 | 20% | Insufficient evidence |
| 2041 | APOLLO UTENSIL STAINLESS STEEL MASHER | Stainless Steel Potato Masher, Berglande | 0.11 | 20% | Insufficient evidence |
| 1911 | PRO USER CLUB HAMMER | OX Club Hammer - Sledgehammer with Fibre | 0.78 | 20% | Insufficient evidence |
| 860 | LUXURY THANK YOU CARDS PK8 | 24 Thank You Cards Pack with Gold Foil S | 1.99 | 19% | Insufficient evidence |
| 1708 | TOWER PRESTO 2 TIER STEAMER PT21004WHT | Aigostar 3 Tier Electric Food Steamer 12 | 5.75 | 19% | Insufficient evidence |
| 932 | BOMBON GLASS MUG 10CL PACK OF 3 | Fusion Food Double Walled Coffee Glasses | 2.98 | 19% | Insufficient evidence |
| 320 | Cat Litter Tray | Cat Litter Tray Box, Litter Box, Plastic | 7.25 | 19% | Insufficient evidence |
| 2097 | WALL CLOCK PP 3 ASSORTED 30CM | Wall Clock 30cm Silent Non-Ticking, Big  | 0.02 | 19% | Insufficient evidence |
| 147 | JAUNTY PARTYWARE CONFETTI PARTY BOWLS 6" | Jaunty 24pk Bulk Party Flashing Glasses  | 10.42 | 19% | Insufficient evidence |
| 1322 | GLEAMAX SCRUB BRUSH 13.5CM X 8.5CM X 6.6 | 2 Pack Multifunctional Heavy Duty Scrub  | 0.96 | 19% | Insufficient evidence |
| 1058 | PPS 1PLY NAPKINS WHITE 250 PIECE | 500 x White Serviettes Paper Napkins (30 | 2.12 | 19% | Insufficient evidence |
| 1733 | Tie-Out Cable for Dogs | Dog Tie Out Cable with 360Â° Swivel Lock | 0.77 | 18% | Insufficient evidence |
| 753 | THL DIVIDER PLATE REUSABLE 10INCH 8PCS | 10" Portion Control Plate for Balanced E | 2.40 | 17% | Insufficient evidence |
| 1004 | PARTY INVITES UNICORN PK20 | 36 Unicorn Party Invites Kids Party Invi | 1.63 | 17% | Insufficient evidence |
| 286 | Cat Lead & Harness | Cat Harness and Lead Set, Escape-Proof K | 6.02 | 17% | Insufficient evidence |
| 217 | 2 Pack Dog Squeaky Toys | 2-Pack Squeaky Dog Toys, Long Crinkle Ta | 8.76 | 17% | Insufficient evidence |
| 686 | LED FIRE FLAME LIGHT 7.5X9CM | LED Flame Light Fire Effect Light for In | 5.43 | 16% | Insufficient evidence |
| 1871 | MASON CASH MUG 450ML CREAM | Mason Cash Colour Mix Cream Mixing Bowl  | 0.47 | 16% | Insufficient evidence |
| 552 | TYRE WAX & SHINE SPRAY 500ML | 2 x Tutti Bambini Compatible Organic Cri | 9.31 | 16% | Insufficient evidence |
| 188 | LIFETIME FILE 3pc 6ASS DSGN | File Organiser 24 Pockets Document Organ | 7.42 | 16% | Insufficient evidence |
| 1868 | TALA DISPOSABLE ICING BAGSX10 | Tala Icing Bag Set with 8 Interchangeabl | 0.27 | 15% | Insufficient evidence |
| 2048 | BG GOLD 2 GANG SWITCH | BG Electrical Double Wall Light Switch,  | 0.23 | 15% | Insufficient evidence |
| 1746 | LIFETIME BATH GLOVE | Temple Spring Exfoliating Glove, Carboni | 0.33 | 14% | Insufficient evidence |
| 767 | FIESTA GLASS MUG 245ML PK3 | Fusion Food Double Walled Coffee Glasses | 3.26 | 14% | Insufficient evidence |
| 1100 | CAR ASHTRAY | Car Ashtray, Portable Ashtray with Lid S | 1.50 | 13% | Insufficient evidence |
| 1062 | GRIMALDI LA BELLA OPEN WOK 28CM | Jobin Wok Non Stick with Lid, 28cm Alumi | 9.11 | 12% | Insufficient evidence |
| 496 | BLOOME OIL FRAGRANCE 2PK | Arabian Oudh Diffuser Oil Set, Essential | 4.08 | 12% | Insufficient evidence |
| 423 | GLASS VASE 13X24CM | Glass Flower Vase, 24cm Hight Modern Min | 12.62 | 12% | Insufficient evidence |
| 795 | CANDLE POTS WITH CRYSTALS PK3 | Crystal Scented Candles Gift Set for Wom | 5.81 | 11% | Insufficient evidence |
| 939 | FLORAL CANDLE METAL LID 335G GARDENIA | Luxury Gardenia Candles Gifts for Women  | 4.98 | 11% | Insufficient evidence |
| 622 | FOUR SEASONS PLASTIC 4 TONGS | 9â€ Kitchen Tongs, 4 Pcs Stainless Stee | 3.10 | 9% | Insufficient evidence |
| 2087 | DOORMAT PVC COIR HELLO 60X40CM | Nicola Spring Coir Door Mat - 60 x 40cm  | 0.05 | 7% | Insufficient evidence |
| 309 | BRIGHT & HOMELY FOIL PLATTER 14 INCH 355 | MATANA 20 Large Aluminium Foil Platters, | 5.18 | 4% | Insufficient evidence |
| 1823 | ONYA DINNER SET 16 PIECES 4 MUGS 4 BOWLS | ORIENTOOLS Leaf Blower and Vacuum-3000w  | 3.10 | 1% | Insufficient evidence |

## MODEL ACCURACY STATISTICS

### Overall Accuracy by Model/Folder

| Model/Folder | Total | Correct | Acceptable | Incorrect | Accuracy % | Combined % |
|--------------|-------|---------|------------|-----------|------------|------------|
| cli | 83 | 56 | 11 | 16 | 67.5% | 80.7% |
| Codex HIGH | 136 | 98 | 15 | 23 | 72.1% | 83.1% |
| Codex samecha | 76 | 5 | 13 | 58 | 6.6% | 23.7% |
| Codex very high | 89 | 40 | 13 | 36 | 44.9% | 59.6% |
| Gemini | 222 | 106 | 86 | 30 | 47.7% | 86.5% |
| Opus | 193 | 140 | 31 | 22 | 72.5% | 88.6% |
| opus2 | 219 | 101 | 84 | 34 | 46.1% | 84.5% |
| webapp gpt | 229 | 78 | 49 | 102 | 34.1% | 55.5% |

### Category-Level Accuracy by Model

#### VERIFIED

| Model/Folder | Claimed | Actually VERIFIED | Actually HIGHLY LIKELY | Actually NEEDS VERIFICATION | Actually FILTERED OUT | Actually OTHER | Accuracy |
|--------------|---------|------------------|------------------------|----------------------------|-----------------------|---------------|----------|
| cli | 31 | 22 | 0 | 0 | 9 | 0 | 71.0% |
| Codex HIGH | 23 | 20 | 0 | 0 | 3 | 0 | 87.0% |
| Codex samecha | 29 | 1 | 2 | 4 | 7 | 15 | 3.4% |
| Codex very high | 16 | 14 | 0 | 0 | 2 | 0 | 87.5% |
| Gemini | 30 | 22 | 0 | 0 | 8 | 0 | 73.3% |
| Opus | 25 | 20 | 0 | 0 | 5 | 0 | 80.0% |
| opus2 | 28 | 23 | 0 | 0 | 5 | 0 | 82.1% |
| webapp gpt | 27 | 22 | 0 | 0 | 5 | 0 | 81.5% |

#### HIGHLY LIKELY

| Model/Folder | Claimed | Actually VERIFIED | Actually HIGHLY LIKELY | Actually NEEDS VERIFICATION | Actually FILTERED OUT | Actually OTHER | Accuracy |
|--------------|---------|------------------|------------------------|----------------------------|-----------------------|---------------|----------|
| cli | 21 | 0 | 15 | 4 | 2 | 0 | 71.4% |
| Codex HIGH | 31 | 0 | 20 | 10 | 1 | 0 | 64.5% |
| Codex samecha | 36 | 3 | 2 | 4 | 10 | 17 | 5.6% |
| Codex very high | 3 | 0 | 2 | 1 | 0 | 0 | 66.7% |
| Gemini | 63 | 0 | 28 | 32 | 3 | 0 | 44.4% |
| Opus | 43 | 0 | 16 | 20 | 0 | 7 | 37.2% |
| opus2 | 99 | 0 | 25 | 54 | 3 | 17 | 25.3% |
| webapp gpt | 45 | 0 | 24 | 17 | 4 | 0 | 53.3% |

#### NEEDS VERIFICATION

| Model/Folder | Claimed | Actually VERIFIED | Actually HIGHLY LIKELY | Actually NEEDS VERIFICATION | Actually FILTERED OUT | Actually OTHER | Accuracy |
|--------------|---------|------------------|------------------------|----------------------------|-----------------------|---------------|----------|
| cli | 25 | 1 | 7 | 15 | 2 | 0 | 60.0% |
| Codex HIGH | 65 | 0 | 5 | 45 | 15 | 0 | 69.2% |
| Codex samecha | 5 | 0 | 0 | 0 | 1 | 4 | 0.0% |
| Codex very high | 26 | 2 | 12 | 9 | 3 | 0 | 34.6% |
| Gemini | 49 | 0 | 0 | 20 | 3 | 26 | 40.8% |
| Opus | 100 | 0 | 11 | 84 | 5 | 0 | 84.0% |
| opus2 | 66 | 0 | 0 | 28 | 8 | 30 | 42.4% |
| webapp gpt | 140 | 0 | 2 | 20 | 16 | 102 | 14.3% |

#### FILTERED OUT

| Model/Folder | Claimed | Actually VERIFIED | Actually HIGHLY LIKELY | Actually NEEDS VERIFICATION | Actually FILTERED OUT | Actually OTHER | Accuracy |
|--------------|---------|------------------|------------------------|----------------------------|-----------------------|---------------|----------|
| cli | 6 | 0 | 1 | 1 | 4 | 0 | 66.7% |
| Codex HIGH | 17 | 3 | 1 | 0 | 13 | 0 | 76.5% |
| Codex samecha | 6 | 0 | 0 | 0 | 2 | 4 | 33.3% |
| Codex very high | 44 | 7 | 15 | 7 | 15 | 0 | 34.1% |
| Gemini | 80 | 0 | 0 | 16 | 36 | 28 | 45.0% |
| Opus | 25 | 3 | 1 | 1 | 20 | 0 | 80.0% |
| opus2 | 26 | 0 | 0 | 1 | 25 | 0 | 96.2% |
| webapp gpt | 17 | 1 | 3 | 1 | 12 | 0 | 70.6% |

### Ranking of Models by Accuracy

| Rank | Model/Folder | Accuracy | Combined | Total Products | Correct |
|------|--------------|----------|----------|----------------|---------|
| 1 | Opus | 72.5% | 88.6% | 193 | 140 |
| 2 | Codex HIGH | 72.1% | 83.1% | 136 | 98 |
| 3 | cli | 67.5% | 80.7% | 83 | 56 |
| 4 | Gemini | 47.7% | 86.5% | 222 | 106 |
| 5 | opus2 | 46.1% | 84.5% | 219 | 101 |
| 6 | Codex very high | 44.9% | 59.6% | 89 | 40 |
| 7 | webapp gpt | 34.1% | 55.5% | 229 | 78 |
| 8 | Codex samecha | 6.6% | 23.7% | 76 | 5 |

## Detailed Incorrect Classifications (By Model)

### cli (27 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1758 | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x makes profit negative |
| 2082 | VERIFIED | FILTERED_OUT | CHEF AID SHOT GLASSES ASSORTED 20PCE | Pack 20x makes profit negative |
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 551 | VERIFIED | FILTERED_OUT | PHOODS FOIL TRAY ROASTER | Pack 10x makes profit negative |
| 1731 | VERIFIED | FILTERED_OUT | SAMS SCRUMMY GIANT LEG DOG BONE | Pack 2x makes profit negative |
| 1934 | VERIFIED | FILTERED_OUT | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LI | Pack 3x makes profit negative |
| 1952 | VERIFIED | FILTERED_OUT | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | Pack 2x makes profit negative |
| 2091 | HIGHLY LIKELY | FILTERED_OUT | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 1981 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL CD BOX CLEAR | Moderate similarity |
| 1745 | HIGHLY LIKELY | NEEDS_VERIFICATION | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Partial match |
| 2003 | HIGHLY LIKELY | FILTERED_OUT | AMTECH BOX SPANNER /TOMMY BAR | Pack 6x makes profit negative |
| 1128 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE ROUND APPLE CINNAMON EA | Partial match |
| 794 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Partial match |
| 855 | NEEDS VERIFICATION | FILTERED_OUT | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | Pack 6x makes profit negative |
| 2081 | NEEDS VERIFICATION | VERIFIED | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Exact EAN match |
| 1630 | NEEDS VERIFICATION | HIGHLY_LIKELY | DRAPER SPANNER SET METRIC COMBINATION | Brand match: DRAPER |
| 621 | NEEDS VERIFICATION | HIGHLY_LIKELY | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Brand match: TIDYZ |
| 1148 | NEEDS VERIFICATION | FILTERED_OUT | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK | Pack 3x makes profit negative |
| ... | ... | ... | ... | ... |

### Codex HIGH (38 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 743 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 600ML | Partial match |
| 794 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Partial match |
| 1061 | HIGHLY LIKELY | NEEDS_VERIFICATION | MENS WATERPROOF FLEECE TRAPPER HAT WITH  | Partial match |
| 1128 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE ROUND APPLE CINNAMON EA | Partial match |
| 1129 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE TALL APPLE&CINN EACH | Partial match |
| 1986 | HIGHLY LIKELY | NEEDS_VERIFICATION | ASHLEY CASH BOX 4.5 INCH | Moderate similarity |
| 2091 | HIGHLY LIKELY | FILTERED_OUT | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 1745 | HIGHLY LIKELY | NEEDS_VERIFICATION | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Partial match |
| 1981 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL CD BOX CLEAR | Moderate similarity |
| 2025 | HIGHLY LIKELY | NEEDS_VERIFICATION | HAPPY 8TH BIRTHDAY BANNER PINK 9FT | Moderate similarity |
| 1852 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQ FOOD CONTAINER 13 LTR | Partial match |
| 1821 | NEEDS VERIFICATION | HIGHLY_LIKELY | FALCON ENAMEL ROUND PIE DISH  26CM | Brand match: FALCON |
| 621 | NEEDS VERIFICATION | HIGHLY_LIKELY | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Brand match: TIDYZ |
| 1410 | NEEDS VERIFICATION | HIGHLY_LIKELY | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Brand match: EVERBUILD |
| 1730 | NEEDS VERIFICATION | HIGHLY_LIKELY | PYREX AIR FRYER SQUARE DISH 20X17CM | Brand match: PYREX |
| 1148 | NEEDS VERIFICATION | FILTERED_OUT | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK | Pack 3x makes profit negative |
| 1744 | NEEDS VERIFICATION | HIGHLY_LIKELY | KILNER BOTTLE SQUARE 1LTR | Brand match: KILNER |
| ... | ... | ... | ... | ... |

### Codex samecha (71 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1458 | VERIFIED | OTHER | FESTIVE MAGIC LED B/O TIMER 200  LIGHTS  | Insufficient evidence |
| 1759 | VERIFIED | FILTERED_OUT | PPS ROUND 150  DOYLEYS 11.5CM | Pack 40x makes profit negative |
| 2083 | VERIFIED | NEEDS_VERIFICATION | WHAM MEASURING JUG 2LTR | Moderate similarity |
| 2041 | VERIFIED | OTHER | APOLLO UTENSIL STAINLESS STEEL MASHER | Insufficient evidence |
| 1830 | VERIFIED | OTHER | SOZALI SQUARE FOOD BOX 700ML 2PC | Insufficient evidence |
| 1041 | VERIFIED | NEEDS_VERIFICATION | AMTECH ANVIL SECATEURS | Moderate similarity |
| 1333 | VERIFIED | OTHER | PRIMA DESSERT FORK 6PCS | Insufficient evidence |
| 1911 | VERIFIED | OTHER | PRO USER CLUB HAMMER | Insufficient evidence |
| 2059 | VERIFIED | OTHER | MEMORIAL PLASTIC SPIKE SPECIAL DAD | Insufficient evidence |
| 2095 | VERIFIED | FILTERED_OUT | HAND BRUSH VARNISH RED | Pack 5x makes profit negative |
| 1131 | VERIFIED | OTHER | ASHLEY OVER THE DOOR HANGER 6 HOOK | Insufficient evidence |
| 1918 | VERIFIED | HIGHLY_LIKELY | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | Brand match: CHEF AID |
| 1991 | VERIFIED | FILTERED_OUT | CANDLE JAR BOHO 9X19CM | Pack 3x makes profit negative |
| 552 | VERIFIED | OTHER | TYRE WAX & SHINE SPRAY 500ML | Insufficient evidence |
| 563 | VERIFIED | FILTERED_OUT | BROOKSTONE AIR FRESH TINS | Pack 24x makes profit negative |
| 751 | VERIFIED | FILTERED_OUT | STATUS LED ROUND SES PA PEARL W/WHT 1PK  | Pack 100x makes profit negative |
| 1057 | VERIFIED | FILTERED_OUT | DEKTON CHISEL WOOD SET 3PC | Pack 4x makes profit negative |
| 1656 | VERIFIED | NEEDS_VERIFICATION | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR | Partial match |
| 1733 | VERIFIED | OTHER | Tie-Out Cable for Dogs | Insufficient evidence |
| 1800 | VERIFIED | OTHER | PPS FOIL CONTAINER & LID DEEP NO.9 235x2 | Insufficient evidence |
| ... | ... | ... | ... | ... |

### Codex very high (49 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 551 | VERIFIED | FILTERED_OUT | PHOODS FOIL TRAY ROASTER | Pack 10x makes profit negative |
| 1731 | VERIFIED | FILTERED_OUT | SAMS SCRUMMY GIANT LEG DOG BONE | Pack 2x makes profit negative |
| 1745 | HIGHLY LIKELY | NEEDS_VERIFICATION | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Partial match |
| 2081 | NEEDS VERIFICATION | VERIFIED | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Exact EAN match |
| 1707 | NEEDS VERIFICATION | HIGHLY_LIKELY | BLUE CANYON ROUND WALL MIRROR WHITE | Brand match: BLUE CANYON |
| 2066 | NEEDS VERIFICATION | VERIFIED | MASON CASH CERAMIC RECT DISH 16cm | Exact EAN match |
| 1762 | NEEDS VERIFICATION | HIGHLY_LIKELY | ROLSON PLASTERING TROWEL 280X115MM | Brand match: ROLSON |
| 1730 | NEEDS VERIFICATION | HIGHLY_LIKELY | PYREX AIR FRYER SQUARE DISH 20X17CM | Brand match: PYREX |
| 1364 | NEEDS VERIFICATION | HIGHLY_LIKELY | AMTECH SHARPENING STONE 2000 | Brand match: AMTECH |
| 1844 | NEEDS VERIFICATION | HIGHLY_LIKELY | AMTECH TELESCOPIC PICKUP TOOL | Brand match: AMTECH |
| 1789 | NEEDS VERIFICATION | HIGHLY_LIKELY | APOLLO WOODEN DISH STAND | Brand match: APOLLO |
| 1370 | NEEDS VERIFICATION | HIGHLY_LIKELY | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK | Brand match: GIFTMAKER |
| 1467 | NEEDS VERIFICATION | FILTERED_OUT | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | Pack 2x makes profit negative |
| 1422 | NEEDS VERIFICATION | HIGHLY_LIKELY | MARIGOLD OUTDOOR GLOVES EXTRA LARGE | Brand match: MARIGOLD |
| 621 | NEEDS VERIFICATION | HIGHLY_LIKELY | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | Brand match: TIDYZ |
| 1647 | NEEDS VERIFICATION | FILTERED_OUT | ELBOW GREASE FOAMING TOILET CLEANER EUCA | Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1181 | NEEDS VERIFICATION | FILTERED_OUT | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15 | Pack 3x makes profit negative |
| 1744 | NEEDS VERIFICATION | HIGHLY_LIKELY | KILNER BOTTLE SQUARE 1LTR | Brand match: KILNER |
| 1630 | NEEDS VERIFICATION | HIGHLY_LIKELY | DRAPER SPANNER SET METRIC COMBINATION | Brand match: DRAPER |
| 696 | NEEDS VERIFICATION | HIGHLY_LIKELY | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK | Brand match: BACOFOIL |
| ... | ... | ... | ... | ... |

### Gemini (116 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1758 | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x makes profit negative |
| 2082 | VERIFIED | FILTERED_OUT | CHEF AID SHOT GLASSES ASSORTED 20PCE | Pack 20x makes profit negative |
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 855 | VERIFIED | FILTERED_OUT | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | Pack 6x makes profit negative |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1934 | VERIFIED | FILTERED_OUT | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LI | Pack 3x makes profit negative |
| 1952 | VERIFIED | FILTERED_OUT | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | Pack 2x makes profit negative |
| 2091 | HIGHLY LIKELY | FILTERED_OUT | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 1745 | HIGHLY LIKELY | NEEDS_VERIFICATION | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Partial match |
| 1981 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL CD BOX CLEAR | Moderate similarity |
| 794 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Partial match |
| 1128 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE ROUND APPLE CINNAMON EA | Partial match |
| 1129 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE TALL APPLE&CINN EACH | Partial match |
| 1986 | HIGHLY LIKELY | NEEDS_VERIFICATION | ASHLEY CASH BOX 4.5 INCH | Moderate similarity |
| 1148 | HIGHLY LIKELY | FILTERED_OUT | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK | Pack 3x makes profit negative |
| 1718 | HIGHLY LIKELY | NEEDS_VERIFICATION | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Partial match |
| 672 | HIGHLY LIKELY | NEEDS_VERIFICATION | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SE | Partial match |
| 743 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 600ML | Partial match |
| 1808 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT MEASURE ULTIMATE JUG 2LTR | Moderate similarity |
| ... | ... | ... | ... | ... |

### Opus (53 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1758 | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x makes profit negative |
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1952 | VERIFIED | FILTERED_OUT | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | Pack 2x makes profit negative |
| 1981 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL CD BOX CLEAR | Moderate similarity |
| 1560 | HIGHLY LIKELY | NEEDS_VERIFICATION | LITTLE TREES CAR FRESHENER ORANGE JUICE | Partial match |
| 1718 | HIGHLY LIKELY | NEEDS_VERIFICATION | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Partial match |
| 1166 | HIGHLY LIKELY | NEEDS_VERIFICATION | SOUDAL EXPANDING FOAM HANDHELD 750ML | Partial match |
| 2088 | HIGHLY LIKELY | NEEDS_VERIFICATION | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK  | Moderate similarity |
| 786 | HIGHLY LIKELY | NEEDS_VERIFICATION | SOUDAL EXPANDING FOAM HAND HELD 150ML | Partial match |
| 1486 | HIGHLY LIKELY | NEEDS_VERIFICATION | STATUS TV AERIAL LEAD 5M CABLE IN CDU | Partial match |
| 919 | HIGHLY LIKELY | NEEDS_VERIFICATION | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET  | Moderate similarity |
| 2032 | HIGHLY LIKELY | NEEDS_VERIFICATION | EVERBUILD ONE STRIKE FILLER 250ML | Moderate similarity |
| 1926 | HIGHLY LIKELY | LOW_PRIORITY | PREMIER FLICKABRIGHT GLASS SPHERE CANDLE | Weak match |
| 1047 | HIGHLY LIKELY | LOW_PRIORITY | PREMIER FLICKABRIGHT TEALIGHT CANDLE 7.3 | Weak match |
| 778 | HIGHLY LIKELY | LOW_PRIORITY | DEKTON HIGH POWER TYPE C RECHARGEABLE FL | Weak match |
| 162 | HIGHLY LIKELY | NEEDS_VERIFICATION | EVERBUILD SEALANT STRIPOUT TOOL | Partial match |
| 613 | HIGHLY LIKELY | LOW_PRIORITY | WHAM CRYSTAL 60LTR SMOKE BOX & LID | Weak match |
| 1060 | HIGHLY LIKELY | LOW_PRIORITY | WHAM CRYSTAL 32LTR SMOKE BOX & LID | Weak match |
| ... | ... | ... | ... | ... |

### opus2 (118 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1758 | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x makes profit negative |
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1952 | VERIFIED | FILTERED_OUT | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | Pack 2x makes profit negative |
| 2091 | HIGHLY LIKELY | FILTERED_OUT | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 1981 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL CD BOX CLEAR | Moderate similarity |
| 794 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Partial match |
| 1986 | HIGHLY LIKELY | NEEDS_VERIFICATION | ASHLEY CASH BOX 4.5 INCH | Moderate similarity |
| 1756 | HIGHLY LIKELY | FILTERED_OUT | PYREX ESSENTIALS CASSEROLE 6.7LTR RECT | Pack 3x makes profit negative |
| 743 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 600ML | Partial match |
| 1852 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQ FOOD CONTAINER 13 LTR | Partial match |
| 1165 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Partial match |
| 1718 | HIGHLY LIKELY | NEEDS_VERIFICATION | ROLSON CLAW HAMMER FIBREGLASS 8OZ | Partial match |
| 1674 | HIGHLY LIKELY | NEEDS_VERIFICATION | MINKY IRONING BOARD CLIPS PK3 | Partial match |
| 1172 | HIGHLY LIKELY | NEEDS_VERIFICATION | FIRST STEPS  FOOD STORAGE POTS WITH SPOO | Partial match |
| 2060 | HIGHLY LIKELY | NEEDS_VERIFICATION | APOLLO RB CUTTING BOARD 30X20 | Moderate similarity |
| 1136 | HIGHLY LIKELY | NEEDS_VERIFICATION | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCK | Partial match |
| 1796 | HIGHLY LIKELY | NEEDS_VERIFICATION | KILNER PRESERVE JAR 0.25LTR SCREW LID | Moderate similarity |
| 2032 | HIGHLY LIKELY | NEEDS_VERIFICATION | EVERBUILD ONE STRIKE FILLER 250ML | Moderate similarity |
| ... | ... | ... | ... | ... |

### webapp gpt (151 errors)
| Row ID | AI Said | Should Be | SupplierTitle | Reason |
|--------|---------|-----------|---------------|--------|
| 1758 | VERIFIED | FILTERED_OUT | PPS ROUND 40 DOYLEYS 21CM | Pack 40x makes profit negative |
| 2040 | VERIFIED | FILTERED_OUT | BLUE CANYON VECTOR SHOWER SPRAY | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1917 | VERIFIED | FILTERED_OUT | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Variant mismatch: Color: ['BLUE'] vs ['WHITE', 'BLUE'] |
| 1990 | VERIFIED | FILTERED_OUT | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Variant mismatch: Color: ['BROWN'] vs ['RED', 'BROWN'] |
| 1952 | VERIFIED | FILTERED_OUT | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | Pack 2x makes profit negative |
| 1051 | HIGHLY LIKELY | NEEDS_VERIFICATION | SMART CHOICE 10 RAWHIDE CHICKEN TREAT | Partial match |
| 224 | HIGHLY LIKELY | NEEDS_VERIFICATION | WORLD OF PETS CAT LITTER SCENTED 3LT | Partial match |
| 1181 | HIGHLY LIKELY | FILTERED_OUT | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15 | Pack 3x makes profit negative |
| 743 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 600ML | Partial match |
| 794 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Partial match |
| 1647 | HIGHLY LIKELY | FILTERED_OUT | ELBOW GREASE FOAMING TOILET CLEANER EUCA | Variant mismatch: Scent: ['EUCALYPTUS'] vs ['LEMON', 'FRESH'] |
| 1852 | HIGHLY LIKELY | NEEDS_VERIFICATION | BEAUFORT SQ FOOD CONTAINER 13 LTR | Partial match |
| 252 | HIGHLY LIKELY | NEEDS_VERIFICATION | PRIMA MULTI SHOWERHEAD CHROME | Partial match |
| 1061 | HIGHLY LIKELY | NEEDS_VERIFICATION | MENS WATERPROOF FLEECE TRAPPER HAT WITH  | Partial match |
| 1128 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE ROUND APPLE CINNAMON EA | Partial match |
| 1129 | HIGHLY LIKELY | NEEDS_VERIFICATION | PAN AROMA CANDLE TALL APPLE&CINN EACH | Partial match |
| 1986 | HIGHLY LIKELY | NEEDS_VERIFICATION | ASHLEY CASH BOX 4.5 INCH | Moderate similarity |
| 2062 | HIGHLY LIKELY | NEEDS_VERIFICATION | WHAM CRYSTAL 80LTR CLEAR BOX & LID | Moderate similarity |
| 2091 | HIGHLY LIKELY | FILTERED_OUT | PRICE & KENSINGTON 2 CUP TEAPOT MATT NAV | Variant mismatch: Color: ['NAVY'] vs ['BLACK'] |
| 399 | HIGHLY LIKELY | NEEDS_VERIFICATION | PENDEFORD POTATO BAKER | Partial match |
| ... | ... | ... | ... | ... |

## Recommendations

1. **Best Performing Model:** Opus with 72.5% accuracy
2. **Needs Improvement:** Codex samecha with 6.6% accuracy
