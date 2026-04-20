# FBA Product Validation Report

Supplier: efghousewares-co-uk
Date: 2026-04-15


Phase 1 summary

| Metric | Value |
|---|---|
| Total rows | 681 |
| Tier distribution | TIER_1_VERIFIED: 548, TIER_4_REJECTED: 64, TIER_2_LIKELY: 44, TIER_3_NEEDS_REVIEW: 25 |
| Top flags | UNPROFITABLE: 286, BRAND_MISMATCH: 103, BRAND_MISMATCH,UNPROFITABLE: 89, (blank): 66, AMAZON_EAN_MISSING,UNPROFITABLE: 59, AMAZON_EAN_MISSING,BRAND_MISMATCH,UNPROFITABLE: 14, AMAZON_EAN_MISSING,BRAND_MISMATCH: 13, AMAZON_EAN_MISSING: 13, EAN_MISMATCH,BRAND_MISMATCH: 13, EAN_MISMATCH,UNPROFITABLE: 9 |
| Profitable count | 220 |
| Items with positive sales | 347 |
| Items with missing sales | 0 |

Phase 2 waterfall

| Step | Rows In | Removed | Rows Out | Notable Removals |
|---|---|---|---|---|
| 2.1 T4 filter | 681 | 64 | 617 | All TIER_4_REJECTED rows removed. |
| 2.2 Price plausibility | 617 | 0 | 617 | Removed 0 extreme-ratio rows; flagged 1 low-price rows. |
| 2.3 False match | 617 | 0 | 617 | None |
| 2.4 Unit qty mismatch | 617 | 13 | 604 | Removed 13 rows; kept 6 adjusted rows; marked 27 UNCLEAR. Examples: LAV TEA GLASS 150CC 6PCS - qty 6; VINERS EVERYDAY KNIFE BLOCK 5PCS - qty 5; RADOX GIFT SET SHOWER GEL BUNDLE 4PCS EACH - qty 4; ELBOW GREASE TOILET CLEANER FOAM LEMON FRESH 500G - qty 3 |
| 2.5 T3 verification | 604 | 6 | 598 | Kept 16 / dropped 6. |
| 2.6 T2 verification | 598 | 0 | 598 | Kept 43 / dropped 0. |

T3 verdicts

| SupplierTitle | Verdict | Reason |
|---|---|---|
| WHAM BEEHIVE ROUND POT NAVY 40CM | DROP | DROP - Amazon is a set of four in cement grey, not one navy pot. |
| LUSCIOUS ROSE EDT 85ML POUR FEMME EACH | DROP | DROP - Pour-femme supplier title conflicts with pour-homme/giftset wording. |
| KINGAVON 5W ELECTRONIC INSECT KILLER WHITE | DROP | DROP - Variant/finish changes to silver. |
| CASA & CASA CLASSICO STAINLESS STEEL SINK ORGANISER WITH TRAY | KEEP | KEEP - Brand, organiser type, stainless steel, and tray descriptors align. |
| ULTRATAPE D/S SIDED CARPET 50MM | DROP | DROP - Supplier is carpet tape while Amazon is PP tape. |
| ANTIQUAX CHAND CRYSTAL CLEANER | KEEP | KEEP - Core title/spec signals align. |
| THE BIG CHEESE ANTI MOUSE REPELLENT BATTERY POWERED | KEEP | KEEP - Core title/spec signals align. |
| UNIBOND ANTI-MOULD KITCHEN & BATHROOM SEALANT WHITE | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS WOOD DYE WALNUT 250ML | KEEP | KEEP - Core title/spec signals align. |
| ADDIS HAND BRUSH STIFF SILVER | KEEP | KEEP - Core title/spec signals align. |
| TALA STAINLESS STEEL SPATULA | KEEP | KEEP - Core title/spec signals align. |
| LORD SHERATON CARETAKER POLISH 300ML | KEEP | KEEP - Core title/spec signals align. |
| UNIBOND NO MORE NAILS ORIGINAL TUBE 175G | KEEP | KEEP - Core title/spec signals align. |
| MASTERPLAST RUB HEAT MASSAGING CREAM | KEEP | KEEP - Core title/spec signals align. |
| KORBOND THREADED NEEDLE KIT 10PCS | KEEP | KEEP - Core title/spec signals align. |
| JUST STATIONERY ELASTIC BANDS ORIGINAL 100GM | KEEP | KEEP - Core title/spec signals align. |
| WHAM CRYSTAL 32LTR LEPRECHAUN GREEN BOX & LID | DROP | DROP - Amazon is an 80L pack of two, not a 32L single box. |
| WHAM CRYSTAL 45LTR LEPRECHAUN GREEN BOX & LID | DROP | DROP - Amazon is an 80L pack of two, not a 45L single box. |
| SMART CHOICE CANVAS PLUSH/ROPE DOG TOY | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS SMALL JOB GLOSS 250ML BLACK | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS SMALL JOB GLOSS 250ML CHOCOLATE | KEEP | KEEP - Core title/spec signals align. |
| TABLEAU DRY LUBE 200ML | KEEP | KEEP - Core title/spec signals align. |

T2 verdicts

| SupplierTitle | Verdict | Reason |
|---|---|---|
| PAN AROMA SCENT CRYSTALS LAVEANDER GARDEN 180G | KEEP | KEEP - Core title/spec signals align. |
| KITCH SQUARE CONTAINERS 250ML & 400ML 2PCE SET | KEEP | KEEP - Core title/spec signals align. |
| PAN AROMA AIR FRESHENER SOLID GEL VANILLA BEAN 190G | KEEP | KEEP - Core title/spec signals align. |
| KINGFISHER GOLD SOFT HOSE  CONNECTOR | KEEP | KEEP - Core title/spec signals align. |
| SECURIT 3 LEVER DEAD LOCK NP 63MM | KEEP | KEEP - Core title/spec signals align. |
| ROLSON ALUMINIUM TORCH 3AAA | KEEP | KEEP - Core title/spec signals align. |
| FUNTIME SPINNING POPPING PALS | KEEP | KEEP - Core title/spec signals align. |
| FALCON ENAMEL ROUND PIE DISH  26CM | KEEP | KEEP - Core title/spec signals align. |
| ROLSON COPPER PIPE CUTTER 15MM | KEEP | KEEP - Core title/spec signals align. |
| FALCON ENAMEL OBLONG PIE DISH 30CM | KEEP | KEEP - Core title/spec signals align. |
| PYREX GLASS LOAF DISH 28CM | KEEP | KEEP - Core title/spec signals align. |
| FUNTIME RAINBOW RAINMAKER  6 PLUS  MONTHS | KEEP | KEEP - Core title/spec signals align. |
| VINERS EVERYDAY GLISTEN 16PC CUTLERY SET | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS QD OUTDOOR CLEAR VARNISH 250ML | KEEP | KEEP - Core title/spec signals align. |
| EXTRA SELECT FISH FOOD BLEND BUCKET 5L | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS METAL PAINT WHITE 250ML | KEEP | KEEP - Core title/spec signals align. |
| O'KEEFFE'S LIP REPAIR COOLING STICK 4.2G | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS WOOD DYE BRW MAHOGANAY 250ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS RUST REMOVER 125ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS QD OUTDOOR CLEAR VARNISH 500ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS WOOD DYE ANTIQUE PINE 250ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS WOOD DYE LIGHT TEAK 250ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS WOOD DYE DARK OAK 250ML | KEEP | KEEP - Core title/spec signals align. |
| RUSTINS QD METAL PAINT BLACK 250ML | KEEP | KEEP - Core title/spec signals align. |
| CHEF AID VEGETABLE BRUSH | KEEP | KEEP - Core title/spec signals align. |
| MASTERCLASS SALT/PEPPER MILL BLACK 17CM | KEEP | KEEP - Core title/spec signals align. |
| ROLSON CABLE CLIP ASSORTMENT 390PC | KEEP | KEEP - Core title/spec signals align. |
| BAYLIS & HARDING JOJOBA, VANILLA & ALMOND OIL LUXURY HAND CARE GIFT SET | KEEP | KEEP - Core title/spec signals align. |
| LORD SHERATON LEATHER SHINE | KEEP | KEEP - Core title/spec signals align. |
| DAEWOO 4 GANG EXTENSION LEAD 1M | KEEP | KEEP - Core title/spec signals align. |
| MUNCH & CRUNCH DOG TREAT ROAST KNUCKLE BONE | KEEP | KEEP - Core title/spec signals align. |
| PRIDE & GROOM SPOT ON CATS | KEEP | KEEP - Core title/spec signals align. |
| BAR KEEPERS FRIEND CREAM 350ML(SOLD EACH) | KEEP | KEEP - Core title/spec signals align. |
| JUMP SUEDE HEEL GRIPS PACK OF 4 | KEEP | KEEP - Core title/spec signals align. |
| JUST STATIONERY HOLE REINFORCERS 512 | KEEP | KEEP - Core title/spec signals align. |
| WHAM CASA SILVER LARGE DISH DRAINER | KEEP | KEEP - Core title/spec signals align. |
| ENERGIZER AAA ALKALINE POWER PK4 | KEEP | KEEP - Core title/spec signals align. |
| STERLING TUBULAR MORTICE LATCH 3INCH - NICKLE PLATED | KEEP | KEEP - Core title/spec signals align. |
| HOZELOCK DOUBLE MALE CONNECTOR | KEEP | KEEP - Core title/spec signals align. |
| CHEF AID RUBBER JAR GRIP | KEEP | KEEP - Core title/spec signals align. |
| MASTERPLAST FOOT POWDER 170G | KEEP | KEEP - Core title/spec signals align. |
| GORILLA WOOD GLUE 118ML | KEEP | KEEP - Core title/spec signals align. |
| JUST STATIONERY RULER SHATTERPROOF 12INCH | KEEP | KEEP - Core title/spec signals align. |

Phase 3 bucket summary

| Bucket | Count | Avg Profit | Avg Sales | T1 | T2 | T3 |
|---|---|---|---|---|---|---|
| A | 10 | 0.83 | 150.0 | 10 | 0 | 0 |
| B | 159 | 2.63 | 0.0 | 150 | 8 | 1 |
| C | 198 | -1.57 | 364.65 | 180 | 18 | 0 |

Phase 4 cross reference

| SupplierTitle | Analysis_NetProfit | FinReport_NetProfit | Analysis_ROI | FinReport_ROI | Analysis_Sales | FinReport_bought_in_past_month | Flags |
|---|---|---|---|---|---|---|---|
| WHAM CASA BLACK HIPSTER BASKET | 2.62 | 2.62 | 75.6 | 75.6 | 50 |  | OK |
| ADDIS CUTLERY DRAINER LINEN | 1.11 | -0.74 | 26.2 | -20.33 | 50 | 50.0 | PROFIT_DISCREPANCY |
| EXTRA SELECT SWAN AND DUCK FEED 5L | 0.77 | -2.06 | 13.6 | -36.37 | 1000 | 900.0 | PROFIT_DISCREPANCY |
| ROYLE HOME SPRINGFORM CAKE TIN | 0.61 | 0.19 | 28.03 | 7.73 | 50 | 100.0 | SALES_DISCREPANCY |
| PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | 0.63 | 0.21 | 6.73 | 2.29 | 100 | 100.0 | OK |
| RYSONS PLASTIC BOWLS W/STRAW 4PCE | 1.12 | -0.1 | 75.0 | -6.67 | 50 | 50.0 | PROFIT_DISCREPANCY |
| COOPER & PALS SQUEAKY CHIKEN | 0.49 | -0.72 | 39.02 | -57.28 | 50 | 700.0 | PROFIT_DISCREPANCY, SALES_DISCREPANCY |
| SIMMER RING | 0.15 | -0.04 | 10.33 | -2.07 | 50 | 100.0 | PROFIT_DISCREPANCY, SALES_DISCREPANCY |
| ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | 0.65 | 0.22 | 31.72 | 8.46 | 50 | 100.0 | SALES_DISCREPANCY |
| SUPER DREAMER FITTED SHEET DOUBLE  BLACK | 0.1 | -1.4 | 2.96 | -40.86 | 50 | 300.0 | PROFIT_DISCREPANCY, SALES_DISCREPANCY |

Phase 5 skipped: no live browser or API validation requested.

Phase 6 output file

C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\FINAL STALE\verified_profitable_efghousewares-co-uk_20260415.csv

Output rows: 367

Phase 7 verification

| Check | Result |
|---|---|
| row_count_matches | PASS |
| zero_t4 | PASS |
| zero_t3_in_a_or_c | PASS |
| unit_qty_flag_present | PASS |
| bucket_present | PASS |
| no_mismatch_removed_rows | PASS |

Verification sample rows

| SupplierTitle | AmazonTitle | Bucket | Unit_Qty_Flag |
|---|---|---|---|
| GABBYS DOLLHOUSE STICKER BOOK | ALLIGATOR - Gabby's Dollhouse Sticker Book, Sticker Book, Sticker Books, Gabbys Dollhouse Toys UK, Gabby's Dollhouse Book,Sticker Activity Book, Reusable Sticker Book | C | MATCH |
| SECURIT CHAIN PRE-CUT 3MMX16MMX1M | 3mmx 1m Zinc Plated Oval Link Chain | B | MATCH |
| TIGER CLEAR PENCIL CASE 8X5INCH | Tiger Pencil case - Clear See Through - Short 20x12.5cm x 1 Single | C | MATCH |

Phase 8 final summary

Products matching both reports: 10

Profit discrepancies found: 8

T3 in Bucket B: 1

Genuinely actionable products: 367 out of 681

Top 10 highest-conviction opportunities

| SupplierTitle | Bucket | NetProfit | sales_value | ROI | Unit_Qty_Flag | Profit_Discrepancy |
|---|---|---|---|---|---|---|
| EXTRA SELECT SWAN AND DUCK FEED 5L | A | 0.7683333333333351 | 1000 | 13.598820058997084 | MATCH | YES |
| WHAM CASA BLACK HIPSTER BASKET | A | 2.6158333333333337 | 50 | 75.60211946050097 | MATCH | NO |
| PYREX ESSENTIALS CASSEROLE OVAL 4.1LTR | A | 0.6283333333333363 | 100 | 6.727337615988612 | MATCH | NO |
| RYSONS PLASTIC BOWLS W/STRAW 4PCE | A | 1.125 | 50 | 75.0 | MATCH | YES |
| ADDIS CUTLERY DRAINER LINEN | A | 1.1123333333333325 | 50 | 26.197205212749225 | MATCH | YES |
| ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | A | 0.6533333333333329 | 50 | 31.715210355987036 | MATCH | YES |
| ROYLE HOME SPRINGFORM CAKE TIN | A | 0.6083333333333341 | 50 | 28.033794162826453 | MATCH | YES |
| COOPER & PALS SQUEAKY CHIKEN | A | 0.4916666666666669 | 50 | 39.02116402116404 | MATCH | YES |
| SIMMER RING | A | 0.1549999999999998 | 50 | 10.33333333333332 | MATCH | YES |
| SUPER DREAMER FITTED SHEET DOUBLE  BLACK | A | 0.1016666666666676 | 50 | 2.964042759961157 | MATCH | YES |