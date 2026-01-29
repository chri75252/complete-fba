# CONSOLIDATED FBA REPORT - MASTER VALIDATION
**Generated:** 2026-01-10 07:50:50
**Source:** part 8 jan.xlsx (3063 rows)

---

## EXECUTIVE SUMMARY

This consolidated report merges valid entries from all four AI reports,
applies corrected classification logic, and retrieves missed products from the source data.

### Reports Analyzed:
- CODEX_NEW
- CODEX_MANU
- OPUS_MANU
- CODEX_FINAL

### Final Counts:
| Category | Count | Est. Total Profit |
|----------|-------|-------------------|
| **VERIFIED** | 40 | £53.48 |
| **HIGHLY LIKELY** | 36 | £100.95 |
| **NEEDS VERIFICATION** | 151 | £297.64 |
| **AUDITED OUT** | 0 | - |
| **TOTAL RECOMMENDED** | 76 | £154.43 |

---

## ROOT CAUSE ANALYSIS

### Issues Identified in Original Reports:

1. **HIGHLY LIKELY Parsing Failure**
   - My initial script failed to parse HIGHLY LIKELY sections due to regex pattern mismatch
   - The sections used headers like `## HIGHLY LIKELY — RECOMMENDED (count=X)` which weren't matched
   - **FIX APPLIED:** Updated regex to match all section header variants

2. **Dimension Trap False Positives**
   - Products like 'APOLLO VINEGAR SHAKER' with '15x5.5x5.5cm' were misread as pack sizes
   - **FIX APPLIED:** Dimension shielding now excludes patterns with cm/mm/ml suffixes

3. **Model Number Confusion**
   - Model numbers like '2001.542' were mistaken for pack quantities
   - **FIX APPLIED:** Context-aware pack detection

4. **Negative Profit Misrouting**
   - Some products with adjusted profit ≤ 0 were left in VERIFIED/HIGHLY LIKELY
   - **FIX APPLIED:** Strict adjusted profit ≤ 0 → AUDITED OUT routing

---

## VERIFIED — RECOMMENDED (40 products)

*Exact EAN matches with positive adjusted profit*

| EAN | Supplier Title | Amazon Title | Net Profit | Adj Profit | ROI | Sales | RSU | Source |
|-----|----------------|--------------|------------|------------|-----|-------|-----|--------|
| 5059001500861 | AIRWICK REED DIFFUSER MULLED WINE 33ML P | Air Wick Essential Oils Reed Diffuser Ai | £16.55 | £16.55 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5050028016069 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k | £8.00 | £8.00 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5010853235530 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl  | £5.11 | £5.11 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5053249248356 | PAN AROMA JAR CANDLE 85GM SALTED CARAMEL | Pan Aroma Orange Decorative Holder & Sce | £2.54 | £2.54 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5032759031078 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch | £2.35 | £2.35 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5014749165598 | BEAUTY VELCRO HAIR GRIP ROLLERS 7 PACK | 42 pcs x 15mm Small Self Grip Hair Rolle | £1.59 | £1.59 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5053249248295 | PAN AROMA JAR CANDLE 85GM RED BERRY | PAN AROMAÂ® RED Decorative Holder & Scen | £1.49 | £1.49 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5010792542676 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins De | £1.40 | £1.40 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5053249228174 | PAN AROMA C TEA-LIGHTS 16PK APP&CIN | Pan Aroma 16 Tea Lights Apple & Cinnamon | £1.33 | £1.33 | 0.0% | 100 | 1 | CODEX_NEW, CODEX_MAN |
| 5010792542737 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle | £1.30 | £1.30 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5010792749549 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland | £1.24 | £1.24 | 0.0% | 400 | 1 | CODEX_NEW, CODEX_MAN |
| 5055170281372 | FRAGRANT CLOUD EDT 100ML POUR FEMME EACH | Fragrant Cloud Rose Ladies Women Perfume | £1.24 | £1.24 | 0.0% | 100 | 1 | CODEX_NEW, CODEX_MAN |
| 5053249215044 | 151 ADHESIVE SPRAY HEAVY DUTY 500ML | 3 Spray Glue Adhesive Contact Glue Heavy | £0.91 | £0.91 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5039295201040 | HOUSE MATE STAINLESS STEEL CLEANER & POL | House Mate Stainless Steel Cleaner and P | £0.79 | £0.79 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 26102251102 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Gl | £0.76 | £0.76 | 0.0% | 50 | 1 | RETRIEVED FROM SOURC |
| 5025364001970 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36 | Tidyz 200 x Extra Large Super Strong Dog | £0.74 | £0.74 | 0.0% | 500 | 1 | RETRIEVED FROM SOURC |
| 5053249253183 | ELBOW GREASE TOILET CLEANER FOAM LEMON F | 3 x Elbow Grease Foaming Toilet Cleaner, | £2.09 | £0.70 | 0.0% | 200 | 3 | CODEX_NEW, CODEX_MAN |
| 5056175901166 | CRAFT FABRIC GLUE 50ML | SOL 2pk x 50ml Fabric Glue Strong with S | £0.69 | £0.69 | 0.0% | 300 | 1 | CODEX_NEW, CODEX_MAN |
| 5019200117338 | PRODEC CAULKER 12 INCH | ProDec 12" Flexible Caulker Blade for Fa | £0.68 | £0.68 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5026180033572 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass V | £0.46 | £0.46 | 0.0% | 50 | 1 | CODEX_MANU, OPUS_MAN |
| 5060187173633 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square  | £0.43 | £0.43 | 0.0% | 100 | 1 | CODEX_NEW, CODEX_MAN |
| 5060357991357 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack o | £3.90 | £0.39 | 0.0% | 50 | 10 | RETRIEVED FROM SOURC |
| 5015302202996 | SAMS SCRUMMY GIANT LEG DOG BONE | Dog Bone Giant Roasted Beef Leg Dog Food | £0.78 | £0.39 | 0.0% | 50 | 2 | RETRIEVED FROM SOURC |
| 5013159300353 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee pe | £0.29 | £0.29 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5036200121479 | THE BIG CHEESE QUICK CLICK MOUSE TRAP 2P | The Big Cheese Quick Click Mouse Trap -  | £0.27 | £0.27 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5012904061204 | TALA COCKTAIL STICKS 200 | Tala Bamboo Cocktail Sticks, Ponted End  | £0.25 | £0.25 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5013159004428 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle,  | £0.22 | £0.22 | 0.0% | 100 | 1 | CODEX_NEW, CODEX_MAN |
| 5060357990107 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays wi | £2.13 | £0.21 | 0.0% | 700 | 10 | CODEX_NEW, CODEX_MAN |
| 5060187175750 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spr | £0.20 | £0.20 | 0.0% | 500 | 1 | CODEX_NEW, CODEX_MAN |
| 5015302472535 | ROYLE HOME SPRINGFORM CAKE TIN | Royle Kids 2 Mini Springform Cake Tin Ki | £0.19 | £0.19 | 0.0% | 100 | 1 | CODEX_NEW, CODEX_MAN |
| 5038135108600 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LI | Wham Clear Plastic Storage Box Boxes Wit | £0.55 | £0.18 | 0.0% | 50 | 3 | RETRIEVED FROM SOURC |
| 5053249215105 | 151 PAINT SPRAY 400ML WHITE MATT | 3 x 400ml 151 Multi Purpose Spray Paint  | £0.11 | £0.11 | 0.0% | 500 | 1 | RETRIEVED FROM SOURC |
| 5010853203508 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Ston | £0.10 | £0.10 | 0.0% | 50 | 1 | CODEX_MANU, OPUS_MAN |
| 5053249215341 | 151 SILICONE LUBRICANT SPRAY 200ML | Silicone Lubricant Spray - 3 Pack, 200ml | £0.09 | £0.09 | 0.0% | 500 | 1 | RETRIEVED FROM SOURC |
| 5012904004188 | CHEF AID STRAINER DIAMETER 18CM | Chef Aid 18cm Long Handled Metal Sieve,  | £0.08 | £0.08 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5055361761119 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WI | Waterproof Robin Memorial Graveside Lant | £0.08 | £0.08 | 0.0% | 50 | 1 | CODEX_NEW, CODEX_MAN |
| 5012904148738 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Gla | £0.03 | £0.03 | 0.0% | 600 | 1 | CODEX_NEW, CODEX_MAN |
| 5022704000013 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White | £0.02 | £0.02 | 0.0% | 100 | 1 | CODEX_NEW, OPUS_MANU |
| 8711252100531 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf | £0.02 | £0.02 | 0.0% | 200 | 1 | CODEX_NEW, CODEX_MAN |
| 5030481940088 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5 | £0.30 | £0.01 | 0.0% | 700 | 40 | CODEX_NEW, CODEX_MAN |

---

## HIGHLY LIKELY — RECOMMENDED (36 products)

*Strong brand/title matches with positive adjusted profit*

| EAN | Supplier Title | Amazon Title | Net Profit | Adj Profit | ROI | Sales | Evidence |
|-----|----------------|--------------|------------|------------|-----|-------|----------|
| 5025301365790 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE W | Quest 36569 Espresso Coffee Machine With | £33.63 | £33.63 | 0.0% | 500 | Amazon EAN missing/invalid; Brand: quest; Similari |
| 5900649077966 | Mokate Gold Premium Coffee Cappuccino 10 | 12 boxes Mokate Gold Premium - Cappuccin | £6.90 | £6.90 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: mokate; Similar |
| 5411183131217 | SOUDAL EXPANDING FOAM HAND HELD 150ML | Soudal 750ml Champagne Gap Filler Expand | £5.47 | £5.47 | 0.0% | 400 | Amazon EAN missing/invalid; Brand: soudal; Similar |
| 5029347009311 | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | Everbuild 103 Premium Trowel Mastic, Sto | £5.34 | £5.34 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: everbuild; Simi |
| 5022245000282 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET  | Extra Select Premium Rabbit Mix Bucket 5 | £4.86 | £4.86 | 0.0% | 300 | Amazon EAN missing/invalid; Brand: extra select; S |
| 5053249281803 | CAR PRIDE CAR VENT AIR FRESHENER LAVENDE | SCENTORINI Car Air Freshener, 2 Fragranc | £4.42 | £4.42 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: lav; Similarity |
| 5411183078956 | SOUDAL EXPANDING FOAM HANDHELD 750ML | Soudal 750ml Champagne Gap Filler Expand | £4.25 | £4.25 | 0.0% | 400 | Amazon EAN missing/invalid; Brand: soudal; Similar |
| 5014353093539 | KILROCK BATHROOM & KITCHEN DRAIN UNBLOCK | Kilrock SLAM - Sink and Plughole Bathroo | £4.12 | £4.12 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: kilrock; Simila |
| 5023139862917 | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK | Bacofoil 3 x Zipper Small All Purpose Ba | £2.93 | £2.93 | 0.0% | 500 | Amazon EAN missing/invalid; Brand: bacofoil; Simil |
| 5032759005833 | AMTECH DRAIN CLEANER | Amtech S1895 Flexible Drain Auger & Wast | £2.60 | £2.60 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: amtech; Similar |
| 5014353093294 | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE  | Kilrock 3 X Blast Away Mould Spray 500ml | £2.30 | £2.30 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: kilrock; Simila |
| 5023139861019 | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK | Bacofoil 3 x Zipper Small All Purpose Ba | £2.17 | £2.17 | 0.0% | 500 | Amazon EAN missing/invalid; Brand: bacofoil; Simil |
| 5014348229363 | BEAUFORT SQUARE FOOD CONTAINER 600ML | Beaufort 13 Litre New SQUARE FOOD & CAKE | £2.09 | £2.09 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: beaufort; Simil |
| 5014348277067 | BEAUFORT SQUARE FOOD CONTAINER 1LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE | £2.03 | £2.03 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: beaufort; Simil |
| 5060386422662 | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x | £1.93 | £1.93 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: blue canyon; Si |
| 5013655218435 | DOFF CONCENTRATED MULTI PURPOSE FEED 1L | 2 X Doff 1L Liquid Seaweed Concentrated  | £1.82 | £1.82 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: doff; Similarit |
| 5022245006710 | EXTRA SELECT FISH FOOD BLEND BUCKET 5L | Extra Select Complete Fish Food Blend Tu | £1.71 | £1.71 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: extra select; S |
| 5010853075914 | KILNER 1LTR SQUARE CLIP TOP JAR (SP) | 6 x Kilner Clip Top Glass Storage Jar -  | £8.49 | £1.42 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: kilner; Similar |
| 5014348292350 | BEAUFORT MEASURE ULTIMATE JUG 3LTR | Beaufort 3 Litre Ultimate Plastic Measur | £1.25 | £1.25 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: beaufort; Simil |
| 5012128616778 | GIFTMAKER CHRISTMAS NON WOVEN SANTA SACK | Giftmaker Collection Large Christmas San | £1.04 | £1.04 | 0.0% | 100 | Amazon EAN missing/invalid; Brand: giftmaker; Simi |
| 5032759001675 | AMTECH SHARPENING STONE 2000 | Amtech E2300 300mm (12") Cigar Sharpenin | £1.02 | £1.02 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: amtech; Similar |
| 5012128616761 | GIFTMAKER CHRISTMAS BASIC SANTA SACK | Giftmaker Collection Large Christmas San | £0.93 | £0.93 | 0.0% | 100 | Amazon EAN missing/invalid; Brand: giftmaker; Simi |
| 5010853253428 | KILNER BOTTLE SQUARE 1LTR | Kilner Clip Top Bottle, 1 Litre | £0.91 | £0.91 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: kilner; Similar |
| 5012823030916 | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM | £0.89 | £0.89 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: falcon; Similar |
| 5026180050005 | APOLLO WOODEN DISH STAND | APOLLO 1684 Wooden dish drainer, Wood, 4 | £0.88 | £0.88 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: apollo; Similar |
| 5014353089266 | KILROCK SERVICE-PRO COFFEE MACHINE DESCA | Kilrock Service Pro Coffee Machine Desca | £0.63 | £0.63 | 0.0% | 100 | Amazon EAN missing/invalid; Brand: kilrock; Simila |
| 5032759027644 | AMTECH POINTING TROWEL 150M(6") WITH SOF | Amtech G0230 150mm (6") Pointing trowel  | £0.63 | £0.63 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: amtech; Similar |
| 5010618043103 | EVERBUILD JET RAPID SET CEMENT 3KG | Everbuild Jetcem Deep Rapid Repair Sand  | £0.57 | £0.57 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: everbuild; Simi |
| 5900649077997 | Mokate Gold Premium Coffee Caramel Latte | Mokate Gold Premium Caramel Latte Coffee | £6.54 | £0.54 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: mokate; Similar |
| 5032759005864 | AMTECH TELESCOPIC PICKUP TOOL | Amtech S8006 3 LED telescopic torch and  | £0.54 | £0.54 | 0.0% | 100 | Amazon EAN missing/invalid; Brand: amtech; Similar |
| 5014348241525 | BEAUFORT SQ FOOD CONTAINER 13 LTR | Beaufort 13 Litre New SQUARE FOOD & CAKE | £0.51 | £0.51 | 0.0% | 200 | Amazon EAN missing/invalid; Brand: beaufort; Simil |
| 8710908183812 | ALBERTO BALSAM SHAMPOO TEA TREE 350ML PK | Alberto Balsam Herbal Shampoo - Tea Tree | £2.76 | £0.46 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: alberto balsam; |
| 29319871000619 | WHITE GLO TOOTHPASTE PROFESSIONAL CHOICE | White Glo Extra Strength Whitening Tooth | £0.33 | £0.06 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: white glo; Simi |
| 5032759049905 | AMTECH BOX SPANNER /TOMMY BAR | Amtech K1150 6 Piece Tubular Box Spanner | £0.21 | £0.03 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: amtech; Similar |
| 5016064115777 | PLAYWRITE  CHRISTMAS CYO MASKS | Playwrite Pack of 12 Christmas design ca | £0.29 | £0.02 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: playwrite; Simi |
| 5029594525374 | ROLSON CHALK LINE AND LAYOUT SET 3PCE | Rolson 52537 3 pc Chalk Line Set | £0.02 | £0.02 | 0.0% | 50 | Amazon EAN missing/invalid; Brand: rolson; Similar |

---

## NEEDS VERIFICATION (151 products)

*Partial match evidence requiring manual confirmation*

| EAN | Supplier Title | Net Profit | Adj Profit | Evidence |
|-----|----------------|------------|------------|----------|
| 5038135251504 | WHAM CRYSTAL 60LTR SMOKE BOX & LID | £13.81 | £13.81 | EAN conflict (both valid); Brand: wham; Similarity: 34%; Pro |
| 8721037370288 | OVEN DISH STONEWARE 4 ASSORTED 90ML | £12.32 | £12.32 | EAN conflict (both valid); Similarity: 26%; Profit=£12.32; R |
| 8694169938513 | IMPERIAL DEEP DINNER PLATE BLUE 10" | £23.61 | £11.81 | EAN conflict (both valid); Similarity: 29%; RSU=2, Adj=£11.8 |
| 5015302420499 | BBQ TURNER WITH WOOD HANDLE 43CM | £10.54 | £10.54 | EAN conflict (both valid); Similarity: 34%; Profit=£10.54; R |
| 8694064013285 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | £9.98 | £9.98 | EAN conflict (both valid); Similarity: 48%; Profit=£9.98; Re |
| 5050565207524 | CANDLE FACTORY SPIRAL CANDLE 2 IN GIFT BOX ** | £8.80 | £8.80 | EAN conflict (both valid); Similarity: 29%; Profit=£8.80; Re |
| 5012866658719 | WOODEN ANIMAL PUZZLE | £8.52 | £8.52 | EAN conflict (both valid); Similarity: 27%; Profit=£8.52; Re |
| 8692952100840 | LAV FAME WINE GLASS 40CL PK3 | £8.11 | £8.11 | EAN conflict (both valid); Brand: lav; Similarity: 34%; Prof |
| 5010853281667 | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL | £7.96 | £7.96 | EAN conflict (both valid); Brand: mason cash; Similarity: 33 |
| 5015934923276 | WICKED STATIONERY BACKPACK | £7.72 | £7.72 | EAN conflict (both valid); Similarity: 27%; Profit=£7.72; Re |
| 8692952070839 | LAV NECTAR TUMBLER 3PC 280ML | £7.66 | £7.66 | EAN conflict (both valid); Brand: lav; Similarity: 28%; Prof |
| 8007815259359 | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | £7.66 | £7.66 | EAN conflict (both valid); Brand: rcr; Similarity: 25%; Prof |
| 4001836065665 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF  | £7.18 | £7.18 | EAN conflict (both valid); Brand: schott zwiesel; Similarity |
| 5010853197838 | MASON CASH MIXING BOWL OWL STONE 26CM | £6.54 | £6.54 | EAN conflict (both valid); Brand: mason cash; Similarity: 34 |
| 5060605732022 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK  | £6.45 | £6.45 | EAN conflict (both valid); Similarity: 62%; Profit=£6.45; Re |
| 5015302105488 | FIRST STEPS BABY BOTTLE SAFARI ASSORTED | £5.56 | £5.56 | EAN conflict (both valid); Similarity: 29%; Profit=£5.56; Re |
| 5060357992750 | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | £5.30 | £5.30 | EAN conflict (both valid); Brand: superior; Similarity: 27%; |
| 5038135251009 | WHAM CRYSTAL 32LTR SMOKE BOX & LID | £5.02 | £5.02 | EAN conflict (both valid); Brand: wham; Similarity: 34%; Pro |
| 6974295210014 | STAINLESS STEEL KETTLE 14CM 1L | £4.86 | £4.86 | EAN conflict (both valid); Similarity: 44%; Profit=£4.86; Re |
| 8414926397021 | PLASTIC FORTE UNDER BED WHEELED STORAGE BOX 3 | £9.16 | £4.58 | EAN conflict (both valid); Similarity: 34%; RSU=2, Adj=£4.58 |
| 8692952076961 | LAV MISKET GIN GLASS 645CC PK3 | £4.21 | £4.21 | EAN conflict (both valid); Brand: lav; Similarity: 27%; Prof |
| 5056170340786 | CHRISTMAS WOODEN TREE SHAPES 12PK | £4.07 | £4.07 | EAN conflict (both valid); Similarity: 25%; Profit=£4.07; Re |
| 5012866061687 | SOFT FOOTBALL IN CDU 10CM 3 ASSORTED | £4.06 | £4.06 | EAN conflict (both valid); Similarity: 28%; Profit=£4.06; Re |
| 3607345711782 | ADIDAS DEODORANT PURE GAME MENS 150ML PK6 | £4.01 | £4.01 | EAN conflict (both valid); Brand: adidas; Similarity: 57%; P |
| 5059004016277 | MENS HANKIES IN COUNTER DISPLAY BROWN BOX 100 | £4.01 | £4.01 | EAN conflict (both valid); Similarity: 31%; Profit=£4.01; Re |
| 5017676016919 | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | £3.52 | £3.52 | EAN conflict (both valid); Brand: roundup; Similarity: 55%;  |
| 6923456800816 | GLASS DRINKING JAR WITH STRAW | £3.52 | £3.52 | EAN conflict (both valid); Similarity: 27%; Profit=£3.52; Re |
| 5060226032587 | Dog Figure '8' Knot Ball Rope Toy(12/48) | £3.24 | £3.24 | EAN conflict (both valid); Similarity: 30%; Profit=£3.24; Re |
| 5015934861943 | LED DART BOARD MAGNETIC | £2.92 | £2.92 | EAN conflict (both valid); Similarity: 35%; Profit=£2.92; Re |
| 5025364005824 | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | £2.77 | £2.77 | EAN conflict (both valid); Brand: tidyz; Similarity: 67%; Pr |
| 5025364000652 | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15 | £2.73 | £2.73 | EAN conflict (both valid); Brand: tidyz; Similarity: 39%; Pr |
| 5025364006043 | TIDYZ COMPOSTABLE 15 BAGS 10LTR | £2.73 | £2.73 | EAN conflict (both valid); Brand: tidyz; Similarity: 32%; Pr |
| 5039306005711 | PADDED ENVELOPES SIZE G 240X340MM PK10 | £2.69 | £2.69 | EAN conflict (both valid); Similarity: 28%; Profit=£2.69; Re |
| 5013922069241 | DRESS ME UP STICKERS ACTIVITY BOOK | £2.62 | £2.62 | EAN conflict (both valid); Similarity: 34%; Profit=£2.62; Re |
| 8719202922790 | CITRONELLA CANDLE IN GLASS POT | £2.57 | £2.57 | EAN conflict (both valid); Similarity: 35%; Profit=£2.57; Re |
| 5053249251714 | PAN AROMA CANDLE 85G PURE JASMINE | £2.54 | £2.54 | EAN conflict (both valid); Brand: pan aroma; Similarity: 38% |
| 5053249251615 | PAN AROMA CANDLE 85G LEMONGRASS | £2.54 | £2.54 | EAN conflict (both valid); Brand: pan aroma; Similarity: 39% |
| 5050565436887 | FIRST AID KNEE SUPPORT 3 SIZES | £2.49 | £2.49 | EAN conflict (both valid); Similarity: 28%; Profit=£2.49; Re |
| 5055706660428 | BABY PIPKIN SILICONE PACIFIER | £2.48 | £2.48 | EAN conflict (both valid); Similarity: 31%; Profit=£2.48; Re |
| 5053249251813 | PAN AROMA CANDLE 85G LIME GINGER | £2.35 | £2.35 | EAN conflict (both valid); Brand: pan aroma; Similarity: 38% |
| 8720573247917 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN | £2.33 | £2.33 | EAN conflict (both valid); Similarity: 46%; Profit=£2.33; Re |
| 5053249238968 | ELBOW GREASE COMPLETE OVEN CLEANING KIT (CONT | £2.28 | £2.28 | EAN conflict (both valid); Brand: elbow grease; Similarity:  |
| 5060743591604 | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6PCS | £2.19 | £2.19 | EAN conflict (both valid); Similarity: 35%; Profit=£2.19; Re |
| 5060743590874 | ECO WISE PAPER CUPS LIDS 8OZ PK25 | £2.19 | £2.19 | EAN conflict (both valid); Similarity: 36%; Profit=£2.19; Re |
| 5010559684793 | DRAPER SPANNER SET METRIC COMBINATION | £2.15 | £2.15 | EAN conflict (both valid); Brand: draper; Similarity: 56%; P |
| 5055706660466 | BABY PIPKIN CLASSIC ROUND BABY BOTTLE 5oz | £3.92 | £1.96 | EAN conflict (both valid); Similarity: 35%; RSU=2, Adj=£1.96 |
| 5053249257068 | MUNCH N CRUNCH BIG BONE BISCUITS 3PK 150g | £1.89 | £1.89 | EAN conflict (both valid); Similarity: 34%; Profit=£1.89; Re |
| 5033601022602 | MAKE A FACE BOOK PRINCESS | £1.86 | £1.86 | EAN conflict (both valid); Similarity: 28%; Profit=£1.86; Re |
| 5022822167575 | STATUS TV TWIN AERAIL ADAPTOR S CLAM IN CDU | £1.73 | £1.73 | EAN conflict (both valid); Similarity: 33%; Profit=£1.73; Re |
| 5037241271048 | SHOPPING BAG PP WOVEN BUTTERFLY DESIGN | £1.72 | £1.72 | EAN conflict (both valid); Similarity: 39%; Profit=£1.72; Re |

*...and 101 more entries*

---

## CONCLUSIONS

### Key Findings:

1. **Total Recommended Products:** 76 (VERIFIED + HIGHLY LIKELY)
2. **Estimated Combined Profit:** £154.43
3. **Products Requiring Verification:** 151
4. **Products Audited Out:** 0

### Report Comparison Summary:

- **CODEX_NEW:** V=32, HL=124, NV=70, AO=8
- **CODEX_MANU:** V=33, HL=115, NV=181, AO=7
- **OPUS_MANU:** V=31, HL=50, NV=3, AO=9
- **CODEX_FINAL:** V=31, HL=37, NV=42, AO=24

### Recommendations:

1. **Prioritize VERIFIED products** - These have exact EAN matches and confirmed profitability
2. **Review HIGHLY LIKELY products** - Strong matches but may need listing verification
3. **Investigate NEEDS VERIFICATION** - Potential opportunities requiring manual research
4. **CODEX_FINAL report performed best** - Use as baseline for future analysis

---
*Report generated: 2026-01-10 07:50:50*