# COMPARISON REPORT: OPUS baseline vs CODEX report
**Generated:** 2026-01-03 09:17:18
**CODEX report:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\PHASEA_MANUAL_REPORT_20260103.md
**CODEX dataset:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\CODEX_REPORT_DATASET_20260103_091506.csv
**OPUS baseline dataset:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\OPUS_BASELINE_DATASET_20260103_091212.csv

## Summary
- CODEX included: 532 rows
- OPUS baseline non-excluded: 1377 rows
- Matched: 215 (match priority: RowID -> ASIN -> EAN pair)
- Disagreements among matched: 76
- OPUS-only (baseline rows CODEX did not include): 1170
- CODEX-only (no baseline match found): 317

## Confusion Matrix (matched rows)
```text
| CODEX                     | OPUS                        | Count |
|---------------------------|-----------------------------|-------|
| HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_RECOMMENDED   | 76    |
| VERIFIED_RECOMMENDED      | VERIFIED_RECOMMENDED        | 28    |
| HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 22    |
| NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 16    |
| HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 15    |
| NEEDS_VERIFICATION        | NEEDS_VERIFICATION          | 15    |
| HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_FILTERED      | 12    |
| VERIFIED_FILTERED         | VERIFIED_FILTERED           | 8     |
| HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 5     |
| HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 4     |
| HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION          | 3     |
| HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 3     |
| HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 3     |
| NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 2     |
| VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 2     |
| VERIFIED_FILTERED         | VERIFIED_RECOMMENDED        | 1     |
```

## Highest-Impact Category Disagreements (matched rows)
```text
| RowID | ASIN       | CODEX_Category            | OPUS_Category               | Sales | NetProfit | AdjProfit | MatchBy              | SupplierTitle                                            |
|-------|------------|---------------------------|-----------------------------|-------|-----------|-----------|----------------------|----------------------------------------------------------|
| 1815  | B0DJDH23JW | VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 700   | £2.13     | £2.13     | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN                  |
| 2404  | B007IGLUIK | VERIFIED_FILTERED         | VERIFIED_RECOMMENDED        | 100   | £0.43     | £-2.66    | ASIN                 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR                 |
| 2422  | B074V9468X | VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 50    | £0.55     | £0.55     | ASIN                 | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID                |
| 1008  | B00I1JW98I | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 100   | £2.86     | £2.86     | ASIN+sig             | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC                   |
| 1095  | B00I1JW98I | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 100   | £2.73     | £2.73     | ASIN+sig             | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC 6PC              |
| 2504  | B004GY24EQ | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 50    | £0.21     | £0.21     | ASIN                 | AMTECH BOX SPANNER /TOMMY BAR                            |
| 519   | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £5.00     | £5.00     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML                  |
| 519   | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £4.16     | £4.16     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN                  |
| 519   | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £3.06     | £3.06     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR                  |
| 255   | B009S64OI6 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 800   | £16.14    | £16.14    | ASIN                 | WORLD OF PETS CAT LITTER SCENTED 3LT                     |
| 686   | B0B3F548G7 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £33.63    | £33.63    | ASIN                 | QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHER |
| 1224  | B00M16SQ8O | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £1.54     | £1.54     | ASIN+sig             | SALT & PEPPER SHAKERS                                    |
| 1599  | B07MGLHMWY | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £1.09     | £1.09     | ASIN+sig             | WASTE SMART EXTRA STRONG WHEELIE BIN 5 BAGS              |
| 996   | B06Y1L9G65 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 400   | £4.40     | £4.40     | ASIN                 | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE                 |
| 932   | B08HX852WM | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 300   | £2.44     | £2.44     | ASIN                 | WASTE SMART STRONG REFUSE SACKS 20 BAGS                  |
| 380   | B0D5HN7W14 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 200   | £12.05    | £12.05    | ASIN                 | CHEF AID SANTOKU KNIFE SOFT GRIP HANDLE                  |
| 89    | B0FS1K5WQH | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 200   | £24.02    | £24.02    | ASIN                 | SMART CHOICE RUBBER BALL DOG TOY                         |
| 890   | B07FYQJXXC | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £7.19     | £7.19     | ASIN                 | WOODEN INSECT HOUSE METAL ROOF                           |
| 950   | B00X3Z2RQY | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £2.51     | £2.51     | ASIN                 | SPICE IT UP CHILLI FLAKES SEASON GRINDER                 |
| 1294  | B07F8VJHWF | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £6.45     | £6.45     | ASIN                 | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK       |
| 444   | B0DHRVB13P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £4.57     | £4.57     | ASIN                 | WORLD OF PETS TOY TUG WITH BALL                          |
| 1199  | B0BHSR7XK1 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.47     | £2.47     | ASIN                 | LADIES KNITTED HAT WITH FAUX FUR POM-POM                 |
| 2429  | B0D8QFWZ7N | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.25     | £0.25     | ASIN                 | MEMORIAL PLASTIC SPIKE SPECIAL MUM & DAD                 |
| 2532  | B01N7UCP9P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.07     | £0.07     | ASIN+sig             | HAPPY 8TH BIRTHDAY BANNER PINK 9FT                       |
| 782   | B00555EWJU | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £3.06     | £3.06     | ASIN                 | JUMBO SLIDER STORAGE BAGS 10PC                           |
| 1057  | B092ZL7VRV | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.71     | £2.71     | ASIN                 | CURVER RATTAN ROUND LARGE ORGANISER GREY                 |
| 615   | B0028YPW68 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £8.58     | £8.58     | ASIN                 | GREEN BLADE 2PCE GARDEN SHEAR SET                        |
| 1299  | B07K1T1N6Y | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £4.45     | £4.45     | ASIN                 | SEAGRASS FOLDABLE BASKET 32CM                            |
| 1385  | B0BF5DTF98 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.33     | £2.33     | ASIN                 | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN                 |
| 1611  | B093HHQ7HB | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.99     | £0.99     | ASIN                 | MEMORIAL GRAVE FLOWER VASE WITH STAKE                    |
| 2531  | B01N7UCP9P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.07     | £0.07     | ASIN+sig             | HAPPY 8TH BIRTHDAY BANNER 9FT                            |
| 2027  | B0DL5RW6LV | HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 900   | £0.45     | £-43.06   | ASIN                 | PAPER MOROCCAN DESIGN 8 BOWLS 7.5 INCH                   |
| 1877  | B0F24X8FY5 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 900   | £0.61     | £0.61     | ASIN+sig             | TIDYZ FREEZER BAGS 150PCS                                |
| 1878  | B0F24X8FY5 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 900   | £0.61     | £0.61     | ASIN+sig             | TIDYZ FREEZER BAGS 100 PCS XLLARGE                       |
| 1523  | B09F31QSQB | HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 800   | £1.93     | £-25.29   | ASIN_ambiguous_first | CEDAR WOOD balls 12PK                                    |
| 2215  | B004MM6OSY | NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 800   | £0.38     | £0.38     | ASIN                 | CHEF AID PASTRY CUTTERS  W184                            |
| 1815  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £3.28     | £-17.24   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR                  |
| 1815  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £3.00     | £-20.55   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR                  |
| 1815  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £1.48     | £-38.48   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR                  |
| 1375  | B07B656W3B | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 700   | £1.23     | £1.23     | ASIN                 | TIDYZ BIN LINER BLACK 10 BAGS 50LTR                      |
| 769   | B07F2MFZT5 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 500   | £2.73     | £-1.29    | ASIN+sig             | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L           |
| 2326  | B09BW2TZ9N | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 500   | £0.28     | £-2.00    | ASIN                 | SPRAY ON GREASE 200ML                                    |
| 2407  | B00JITIIQ2 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £0.43     | £-21.08   | ASIN                 | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS               |
| 934   | B07STZLCM6 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £5.47     | £5.47     | ASIN+sig             | SOUDAL EXPANDING FOAM HAND HELD 150ML                    |
| 2268  | B0C6FQLPV3 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £0.30     | £-13.81   | ASIN                 | JAUNTY PARTYWARE BALLOONS TWIST 15                       |
| 182   | B00IZMVQOO | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 400   | £28.79    | £28.79    | ASIN                 | EVERBUILD SEALANT STRIPOUT TOOL                          |
| 347   | B0933MHLG6 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 400   | £9.98     | £9.98     | ASIN                 | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM                |
| 2554  | B0BN8J4WLM | NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 400   | £0.59     | £0.59     | ASIN                 | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2                |
| 166   | B07PMB7PYK | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 300   | £10.42    | £-11.11   | ASIN                 | JAUNTY PARTYWARE CONFETTI PARTY BOWLS 6" 12PK            |
| 687   | B0DM9FNQ9R | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 300   | £4.84     | £4.84     | ASIN                 | FESTIVE MAGIC SANT SLEIGH FELT BUCKET                    |
```

## OPUS-only (baseline): Top by Sales/NetProfit that CODEX did not include
```text
| RowID | ASIN       | CategoryNorm                | Sales | NetProfit         | AdjustedProfit       | SupplierTitle                                            |
|-------|------------|-----------------------------|-------|-------------------|----------------------|----------------------------------------------------------|
| 558   | B0D7BHB64L | NEEDS_VERIFICATION          | 900   | 7.39499999999999  | 7.39499999999999     | ASHLEY CERAMIC HUMIDIFIER                                |
| 289   | B09KSB6DZG | NEEDS_VERIFICATION          | 900   | 7.32166666666666  | 2.28166666666666     | JAUNTY TUMBLERS PINT                                     |
| 269   | B09QMCPGVL | NEEDS_VERIFICATION          | 900   | 6.67833333333333  | 2.6583333333333297   | ADORN PLACEMAT 37CM ASSORTED                             |
| 422   | B06WWQXHMS | NEEDS_VERIFICATION          | 900   | 5.385             | 5.385                | PRIMA STAINLESS STEEL CHEESE KNIFE                       |
| 657   | B0CN2XTXX1 | NEEDS_VERIFICATION          | 900   | 4.89291666666666  | 4.89291666666666     | SIL INCENSE HEX STICKS PK4 FLOWER                        |
| 975   | B0DGH36J1F | NEEDS_VERIFICATION          | 900   | 3.82291666666666  | 3.82291666666666     | APOLLO KITCHEN TIMERS                                    |
| 1118  | B0DGH36J1F | NEEDS_VERIFICATION          | 900   | 3.05166666666666  | 3.05166666666666     | PRIMA KITCHEN TIMER                                      |
| 1337  | B0DGH36J1F | NEEDS_VERIFICATION          | 900   | 2.71166666666666  | 2.71166666666666     | APOLLO MECHANICAL KITCHEN TIMER                          |
| 1282  | B07R97DV7D | NEEDS_VERIFICATION          | 900   | 2.33166666666666  | 2.33166666666666     | SMART CHOICE 10 RAWHIDE CHICKEN TREAT                    |
| 1254  | B0C8TKT76M | NEEDS_VERIFICATION_FILTERED | 900   | 2.13833333333333  | -3.76566666666667    | MARKSMAN DRILL SET MASONRY 5PC                           |
| 1152  | B07L6W57XH | NEEDS_VERIFICATION_FILTERED | 900   | 1.915             | -0.10099999999999998 | ASHLEY ROUND  DISH WASING UP BRUSH                       |
| 1018  | B0C8JB8SK1 | NEEDS_VERIFICATION          | 900   | 1.875             | 1.875                | PPS PLASTIC 2 TABLECLOTHS RED                            |
| 1177  | B09GV96C33 | NEEDS_VERIFICATION_FILTERED | 900   | 1.85958333333333  | -37.452416666666664  | BLACKSPUR MINI CAR BIN                                   |
| 1264  | B0DNYTZH29 | NEEDS_VERIFICATION          | 900   | 1.49833333333333  | 0.64633333333333     | FESTIVE MAGIC RIBBON 16MMX2.7M ASST.                     |
| 1285  | B0DNYTZH29 | NEEDS_VERIFICATION          | 900   | 1.47833333333333  | 0.60233333333333     | OPAL ROUND SHALLOW CEREAL BOWL WHITE                     |
| 1270  | B08HGPVVXZ | NEEDS_VERIFICATION_FILTERED | 900   | 1.37124999999999  | -0.8607500000000101  | APOLLO STAINLESS STEEL SOLID SERVING SPOONS SML          |
| 1734  | B0926YFF4H | NEEDS_VERIFICATION_FILTERED | 900   | 1.15166666666666  | -32.83233333333334   | BLACKSPUR RUBBLE SACKS 3PC                               |
| 1917  | B09MQ24Y71 | NEEDS_VERIFICATION_FILTERED | 900   | 0.506666666666666 | -0.09333333333333393 | BRIGHT & HOMELY SHOE HORN 45CM BLACK                     |
| 1955  | B0D1YN3XQJ | NEEDS_VERIFICATION_FILTERED | 900   | 0.451666666666667 | -1.168333333333333   | BLACKSPUR GLUE SUPER 3G UP                               |
| 2159  | B0F24X8FY5 | NEEDS_VERIFICATION          | 900   | 0.398333333333334 | 0.398333333333334    | KEEP IT HANDY ZIP SEAL FOOD & FREEZER 8 LARGE BAGS       |
| 366   | B01L8Q3J5M | NEEDS_VERIFICATION          | 800   | 8.98833333333333  | 8.98833333333333     | DRAPER RETRACTABLE KNIFE SET                             |
| 490   | B07DXP3JVB | NEEDS_VERIFICATION_FILTERED | 800   | 6.84833333333333  | -12.42366666666667   | SMART CHOICE 30 BEEF/CHICKEN STICKS                      |
| 310   | B01F9QB8I2 | NEEDS_VERIFICATION          | 800   | 6.81791666666666  | 6.81791666666666     | SIL BATHROOM SUCTION MIRROR                              |
| 1715  | B0FSXQP8SR | NEEDS_VERIFICATION          | 800   | 5.50499999999999  | 5.50499999999999     | PRICE & KENSINGTON 6 CUP TEAPOT WHITE                    |
| 617   | B085MQZCLY | NEEDS_VERIFICATION          | 800   | 4.43208333333333  | 4.43208333333333     | ADORN PATTERN MANICURE SET WITH CASE                     |
| 650   | B079TY981C | NEEDS_VERIFICATION          | 800   | 4.42              | 4.42                 | SIL SHOE TREE SHAPER                                     |
| 921   | B09X2WZJDV | NEEDS_VERIFICATION          | 800   | 3.42833333333333  | 3.42833333333333     | APOLLO ZEUS 10 INCH SCISSORS                             |
| 954   | B0924XVD1J | NEEDS_VERIFICATION          | 800   | 3.30583333333333  | 1.6618333333333302   | BLACKSPUR CAR HEADLIGHT BULB 12V 60W/55W H4              |
| 656   | B07HJ3S675 | NEEDS_VERIFICATION          | 800   | 3.19833333333333  | 2.3943333333333303   | WORLD OF PETS TOY TEETH BALL                             |
| 1551  | B0CQRR8NLX | NEEDS_VERIFICATION          | 800   | 3.17833333333333  | 3.17833333333333     | EXTRA SELECT COMPLETE TURTLE & TERRAPIN FOOD 60G         |
| 994   | B0BNHYW67S | NEEDS_VERIFICATION          | 800   | 2.90625           | 2.90625              | HOBBY BUTTER DISH 031229                                 |
| 1020  | B089YD9C3L | NEEDS_VERIFICATION          | 800   | 2.86166666666666  | 2.86166666666666     | AMTECH TILE SPACERS 300PC 4MM                            |
| 1000  | B0749KYFXX | NEEDS_VERIFICATION          | 800   | 2.565             | 1.353                | APOLLO TONGS METAL 9IN                                   |
| 942   | B07XLNJDY9 | HIGHLY_LIKELY_RECOMMENDED   | 800   | 2.18833333333333  | 2.18833333333333     | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6PCS               |
| 943   | B07XLNJDY9 | HIGHLY_LIKELY_RECOMMENDED   | 800   | 2.18833333333333  | 2.18833333333333     | ECO WISE PAPER CUPS LIDS 8OZ PK25                        |
| 1474  | B08XMMXLCF | NEEDS_VERIFICATION          | 800   | 1.84166666666666  | 1.84166666666666     | HOBBY ROUND BOWL NO3 5LT                                 |
| 1536  | B09F31QSQB | NEEDS_VERIFICATION_FILTERED | 800   | 1.53833333333333  | -38.31366666666667   | PRIMA CEDAR WOOD BALL                                    |
| 1513  | B0BQMNWSL6 | NEEDS_VERIFICATION          | 800   | 1.39666666666666  | 1.39666666666666     | DEKTON HEAVY DUTY BUNGEE CORD 52INCHX10MM                |
| 1634  | B07GC81HVV | NEEDS_VERIFICATION_FILTERED | 800   | 0.898333333333334 | -2.2216666666666662  | BRIGHT & HOMELY HANGERS METAL RUBBER COATED BLACK 4 PACK |
| 1897  | B0FL7BLX8P | NEEDS_VERIFICATION          | 800   | 0.612916666666666 | 0.612916666666666    | FESTIVE MAGIC MINI GIFT BOWS 30PC                        |
```

## CODEX-only: Rows in CODEX report not found in OPUS baseline
```text
| RowID | ASIN                                                                                    | Category                  | Sales             | NetProfit          | SupplierTitle                                        | AmazonTitle                                                            |
|-------|-----------------------------------------------------------------------------------------|---------------------------|-------------------|--------------------|------------------------------------------------------|------------------------------------------------------------------------|
| None  | Push-on-Fitting                                                                         | VERIFIED_RECOMMENDED      | 5060187175750     | ~1.5 Meters        | BLUE CANYON VECTOR SHOWER SPRAY                      | Blue Canyon Vector Double Tap Shower Spray                             |
| None  | 5010792749549                                                                           | VERIFIED_RECOMMENDED      | £1.24             | £6.59              | HIGHLAND COW PLAQUE FRIENDS                          | Lesser & Pavey Love & Affection Highland Cow Wooden Plaque - Friends F |
| None  | Lightweight & Dishwasher Safe                                                           | VERIFIED_RECOMMENDED      | £7.66             | 5010853235530      | MASON CASH MIXING BOWL CREAM 29CM                    | Mason Cash Colour Mix Cream Mixing Bowl                                |
| None  | Long Arm Chrome Vanadium Steel Kit                                                      | HIGHLY_LIKELY_RECOMMENDED | B01089N3RO        | 5010559680023      | DRAPER HEX KEY SET METRIC DIY 8 PC                   | Draper 10 Piece T-Handle Hexagon Allen Key Set                         |
| None  | B07DHMR1L6                                                                              | HIGHLY_LIKELY_RECOMMENDED | 500               | £2.07              | CORAL EASY COATER 4" & FREE BRUSH                    | Coral 10501 Easy Coater Paint Kit with Headlock and Mini Roller Frame  |
| None  | B0DP24V73R                                                                              | HIGHLY_LIKELY_RECOMMENDED | 400               | £6.79              | WOOD FRAME 1INCH OAK 8X10                            | 8x10 Picture Frame, Solid Oak Wood 8x10 inch Natural Wood Photo Frame  |
| None  | 60cm Large Xmas Fireplace Hanging                                                       | HIGHLY_LIKELY_RECOMMENDED | £9.99             | B0FTMP3GYP         | FESTIVE MAGIC CHRISTMAS STOCKING PLUSH FOIL          | evelay Highland Cow Christmas Stocking                                 |
| None  | B09YRC9SXW                                                                              | HIGHLY_LIKELY_RECOMMENDED | 400               | £2.88              | MINI GLASS JAR 120ML PK6                             | ComSaf Mini Mason Jars 120mL/4oz - 8 Pack, Small Glass Jars with Lids  |
| None  | 5010853271859                                                                           | HIGHLY_LIKELY_RECOMMENDED | 110.3%            | £23.71             | MASON CASH MIXING BOWL OWL STONE 26CM                | Mason Cash in The Forest Owl Mixing Bowl 4 Litre                       |
| None  | B08T8JR6YL                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £0.68              | SILICONE HEAT RESISTANT POT HOLDER                   | Oven Glove Thicken Silicone Pot Holder Mini Oven Mitt Heat Resistant P |
| None  | B07L872VYN                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £0.44              | BUTTERFLY AND RAINBOW HAIR CLIPS 4PC                 | Toddler Girls Butterfly Snap Clips,Lovely Unicorn Rabbit Hair Clip for |
| None  | Glass Meal Prep Lunch Box Takeaway Containers                                           | HIGHLY_LIKELY_RECOMMENDED | £17.95            | B09X7JR23L         | Plastic Food Containers 1000ml 4pk                   | ZENO Glass Food Storage with Lids 4 Pack                               |
| None  | B09X78TC7Q                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £2.13              | RUBBER DUCK FAMILY BATH TOY 3 PACK                   | Rubber Duck Bath Toy Set â€“ Floating Duck Family by KOKSI â€“ 4-Piece |
| None  | B0B51H18ZK                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £1.80              | MONEY TIN BOX ASST MEDIUM (2022)                     | Best House Money Box - Piggy Bank, Cash Coin Box Tin, Tinplate, Saving |
| None  | B0DKC45N71                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £1.78              | CHRISTMAS TAPER CANDLES SILVER SET OF 4              | Silver Candles, 10'' Silver Taper Candles, Set of 4 Spiral Twisted Din |
| None  | B0BSMPFTTZ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £2.44              | PLASTIC MAKEUP STORAGE HOLDER                        | Makeup Organiser Cosmetic Storage Box, Make up Organizer Dressing Tabl |
| None  | S15MTVAEKX12                                                                            | HIGHLY_LIKELY_RECOMMENDED | £7.95             | B08N713Y2V         | STATUS TV AERIAL LEAD 5M CABLE IN CDU                | Status 15 Metre TV Aerial Cable Extension Kit                          |
| None  | B0DPMTK6GJ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £0.12              | BABY PIPKIN NAIL CLIPPERS & SCISSORS SET             | Vicloon Baby Nail Kit, 4-in-1 Baby Nail Care Set, Baby Nail Care Tool, |
| None  | B0D876QQH4                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £15.19             | OVEN LOVE BAKING DISH OVAL RED 0.19L                 | MALACASA Oval Ceramic Oven Baking Dishes, Ideal for Lasagne, Shepherds |
| None  | B0FL7M9TBG                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £8.76              | 2 Pack Dog Squeaky Toys                              | 2-Pack Squeaky Dog Toys, Long Crinkle Tail with Treat Dispenser Pocket |
| None  | B0F28RTFV4                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £4.73              | PLASTIC CLEAR 4 SECTION TRAY                         | Junw 4 pack Clear Compartment Trays with 6 Section, Reusable Plastic T |
| None  | B0DJ34RG3C                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £9.46              | WOOD FRAME 1INCH OAK 5X7                             | Photo Frame 5x7, 3 Pack Solid Oak Wood 5x7 inch Picture Frame, 5x7 Fra |
| None  | B0CV12HTJ9                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £4.13              | SPECIAL OCCASIONS RAINBOW COLOUR HAIR SPRAY 200ML    | 6 * 200ml Cans Rainbow Colour Hair Spray - Perfect for fun and Special |
| None  | 5010853271866                                                                           | HIGHLY_LIKELY_RECOMMENDED | 175.7%            | £22.62             | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM   | Mason Cash in The Forest Hedgehog Mixing Bowl 1.1 Litre                |
| None  | B0DCP6NBYX                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £5.58              | INDOOR & OUTDOOR DOORMAT 60CM X 90CM                 | BLADO Washable Door Mats - Non-Slippery Heavy Duty Doormats - Stylish  |
| None  | B089YPV5SG                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £2.09              | GREEN HABITATS CLAW GARDEN DIGGING GLOVES            | Oranlife Garden Genie Gloves with Claws Waterproof Gardening Gloves Fo |
| None  | B0BQWCQ2WK                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £0.95              | BANNER BRIGHT CONFETTI HAPPY BIRTHDAY ROSE GOLD 9FT  | Rose Gold Happy Birthday Banner, Bunting Birthday Decorations for Girl |
| None  | 5060569229804                                                                           | HIGHLY_LIKELY_RECOMMENDED | £2.45             | £3.70              | BACKPACK STANDARD PAW PATROL SKYE                    | Paw Patrol Skye Girls Backpack                                         |
| None  | B0BRV3BLL7                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £1.73              | GROUND SPIKE HEAVY-DUTY METAL                        | Rotary Washing Line Spike - Heavy Duty Powder Coated Metal Ground Spik |
| None  | B0BF184H2G                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £0.56              | SEWING THREAD BLACK/WHITE 4PC                        | 500m Sewing Thread, Strong Multipurpose General Application Thread, fo |
| None  | B09SHKQTSZ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £1.22              | COLANDER STAINLESS STEEL 22CM                        | Stainless Steel Colander 22cm, Herogo Metal Kitchen Colanders with Han |
| None  | B0B8SNGDBZ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £0.44              | FISH TANK NET - 25CM HANDLE                          | Aquarium Fishing Net,25cm Handle Fish Tank Quick Catch Mesh for Catchi |
| None  | B0DCW45WNH                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £2.64              | DUVET SET MICROFIBER GREEK DOUBLE GREY               | Oxford Homeware Double Duvet Set Grey Brushed Microfiber 4 Piece Doubl |
| None  | B07MKPCXJ1                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £0.15              | HAND SCRUBBING BRUSH WOODEN BILLUR                   | Wooden Scrubbing Brush Heavy Duty Hand Scrubber with Wood Stock and St |
| None  | 5060569224021                                                                           | HIGHLY_LIKELY_RECOMMENDED | £0.49             | £6.05              | BACKPACK DELUXE GLITTER PAW PATROL SKYE              | Paw Patrol Skye Girls Backpack                                         |
| None  | B01600WDY4                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £0.24              | INCENSE BOX WITH STICKS WOOD                         | Bramble & Jones LEAF - Solid Wood Wooden Incense Joss Sticks Storage B |
| None  | All Wooden 10x12 Black Picture Frames are made from SOLID WOOD and come with REAL GLASS | HIGHLY_LIKELY_RECOMMENDED | £19.99            | B00QSAZATW         | WOOD FRAME 1INCH BLACK 12X10                         | Wall Space 12x10 Thin Black Frame                                      |
| None  | B0D1KX7XKK                                                                              | HIGHLY_LIKELY_RECOMMENDED | 50                | £4.30              | ALUMINIUM OVEN TRAY 30CM                             | Scoville Expert NEVERSTICK+ 30cm Deep Baking Tray, Non Stick Baking Tr |
| None  | B08MVDCSJQ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 50                | £1.66              | MUNCH CRUNCH RAWHIDE PRESSED BONE                    | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe Filled Rawhide  |
| None  | B08MVDCSJQ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 50                | £1.66              | MUNCH CRUNCH RAWHIDE BONE NAT JUMBO                  | Munch & Crunch Bone Chews for Dogs Multipack - 8 Tripe Filled Rawhide  |
| None  | B0DXQ56JTB                                                                              | HIGHLY_LIKELY_RECOMMENDED | 50                | £4.06              | ALUMINIUM OVEN TRAY 36CM                             | Scoville Xtra 36cm Roasting Tray, Non Stick Roasting Tray for Oven, NE |
| None  | 5017403154617                                                                           | HIGHLY_LIKELY_RECOMMENDED | £2.44             | £3.29              | DOOR MAT COIR HOME SWEET HOME 40 X 60CM              | Coir Outdoor Door Mat                                                  |
| None  | Spurs Collectible Wall Art No184                                                        | HIGHLY_LIKELY_RECOMMENDED | £29.99            | B0FZCN5J5F         | FRAMED ART - TOTTENHAM HOTSPUR F.C KITS 40CM X 40CM  | Tottenham Hotspur UEFA Europa League Winners 2025 Signed Shirt A3 Post |
| None  | 5027785817369                                                                           | HIGHLY_LIKELY_RECOMMENDED | £0.43             | £1.15              | ULTRATAPE PICTURE FRAME TAPE 24MMX50M                | Ultratape                                                              |
| None  | Spurs Collectible Wall Art No184                                                        | HIGHLY_LIKELY_RECOMMENDED | £29.99            | B0FZCN5J5F         | FRAMED ART - TOTTENHAM HOTSPUR F.C SHIRT 50CM X 40CM | Tottenham Hotspur UEFA Europa League Winners 2025 Signed Shirt A3 Post |
| None  | B0F4RS323K                                                                              | HIGHLY_LIKELY_RECOMMENDED | 50                | £0.30              | FRAMED ART - MANCHESTER UNITED KITS 40CM X 40CM      | A4 Framed Manchester United FC Legends, Repro Signed Wall Art Print, P |
| None  | Safe On All Surfaces (5 Litre)                                                          | HIGHLY_LIKELY_RECOMMENDED | £9.70             | B0CQ4VX6Z5         | FLOW FLOOR & SURFACE CLEANER 5L EACH                 | Flow Lemon Floor & Surface All Purpose Cleaner                         |
| None  | B08FDH654K                                                                              | HIGHLY_LIKELY_RECOMMENDED | 900               | £2.35              | LADIES FASHION GLOVES WITH FUR INSIDE                | Vagasi Women Touch Screen Gloves - Winter Warm Fleece Lined Touchscree |
| None  | B07MM3DYKP                                                                              | HIGHLY_LIKELY_RECOMMENDED | 800               | £2.68              | BABY FACE CLOTH PK3                                  | Flannel face cloth (6-Pack) - Bamboo face cloth Ultra-Soft & Baby Wash |
| None  | B081WQLR5S                                                                              | HIGHLY_LIKELY_RECOMMENDED | 700               | £12.74             | MENS LEATHER WALLET 1148                             | Soft Leather Wallets for Men UK - RFID Blocking - Stylish Mens Wallet  |
| None  | B01GEOZEVU                                                                              | HIGHLY_LIKELY_RECOMMENDED | 700               | £4.46              | BABY PIPKIN FEEDING SPOONS 7PCE                      | NumNum GOOtensil Pre-Spoons - Baby Spoons Set for 6+ Months - Silicone |
| None  | Minky Pad                                                                               | HIGHLY_LIKELY_RECOMMENDED | Cleaning Supplies | Non Scratch Sponge | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4PC            | Minky Anti-Bacterial Cleaing Pad                                       |
| None  | B0D4JNBKP1                                                                              | HIGHLY_LIKELY_RECOMMENDED | 500               | £3.43              | NIGHTLIGHT DINOSAUR COLOUR CHANGING                  | Kids Night Light Squishy Dinosaur Nightlight for Kids Room 7 Color Cha |
| None  | B074QKHZ94                                                                              | HIGHLY_LIKELY_RECOMMENDED | 500               | £2.43              | PADLOCK LAMINATED 40MM                               | SEPOXÂ® 2Pack Heavy Duty Padlock Keyed Alike, 40MM Laminated Steel Loc |
| None  | 604565842879                                                                            | HIGHLY_LIKELY_RECOMMENDED | 313.3%            | £12.99             | AIR FRYER PAPER LINER ROUND 16X4.4.5CM 50PCE         | Round Air Fryer Liners Disposable 100Pcs - Air Fryer Liners Round 8 in |
| None  | 604565842879                                                                            | HIGHLY_LIKELY_RECOMMENDED | 250.3%            | £12.99             | AIR FRYER PAPER LINER  ROUND 20X4.5CM 50PCE          | Round Air Fryer Liners Disposable 100Pcs - Air Fryer Liners Round 8 in |
| None  | B0D9FFVTB7                                                                              | HIGHLY_LIKELY_RECOMMENDED | 400               | £1.10              | CHRISTMAS VOTIVES RED/WHITE BERRY SET OF 3           | Glasseam Christmas Candle Holder Glass: Set of 3 Tea Light Candle Hold |
| None  | School Lunch Box                                                                        | HIGHLY_LIKELY_RECOMMENDED | B002ARYB8I        | 9414202017000      | SISTEMA CLEAR RECT FOOD BOX 2 LTR                    | Sistema KLIP IT Food Storage Container                                 |
| None  | B0FN3TVZVL                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £14.86             | PORCELAIN MUG 12OZ COLOURED                          | vancasso SIMI Mugs Set, 12oz/360ml Porcelain Coffee Mug Set of 6, Bohe |
| None  | B0CHP4MZTM                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £2.47              | FIRST AID ELBOW SUPPORT BANDAGE 3 SIZES              | Tubular Bandage 3in X 26ft Elasticated Support for Arm, Stretch Roll F |
| None  | B087YZWHG6                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £1.98              | ROTARY LINE COVER                                    | Rotary Washing Line Cover Waterproof - Universal Fit with Zip and Draw |
| None  | B08616GDRJ                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £0.73              | SALT & PEPPER POTS GLASS                             | Glass Salt and Pepper Shaker Pot Set of 2 Classic Clear Glass Traditio |
| None  | B07C8V2DJ7                                                                              | HIGHLY_LIKELY_RECOMMENDED | 300               | £3.32              | RUSSELL HOBBS VIENNA CUTLERY SET 16PC                | Russell Hobbs RH00022GP Vienna 16 Piece Cutlery Set - Stainless Steel  |
| None  | B0CNCZJLYF                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £10.72             | SQUARE SPICE JAR BLACK/WHITE                         | Square Spice Jars Set of 24 with Bamboo Lids, Shaker Inserts, Pre-Prin |
| None  | 5055566999041                                                                           | HIGHLY_LIKELY_RECOMMENDED | £3.98             | £1.01              | CERAMIC WAX/OIL BURNER                               | Grey Ombre Glaze Tea Light Essential Oil Burner                        |
| None  | B09Q558B4M                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £3.58              | ROUND TRAY ASS DECOR                                 | Hanobe Rustic Wooden Serving Tray: Round Wood Decorative Candle Holder |
| None  | B008EXEVG4                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £2.77              | LONDON MUG 10CM                                      | Puckator London Red Routemaster Bus Ceramic Shaped Mug, Tea Coffee Hot |
| None  | B0FB2VXH8H                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £1.98              | HAIR BOBBLES 36PC BROWN BLACK WHITE                  | 15 Pcs Brown and Black Hair Bobbles, Mixed Color Elastic Hair Ties for |
| None  | B09MTP248R                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £5.68              | VASE GLASS CYLINDER 20X10X10CM                       | YOUEON Wide Glass Cylinder Vase (20x10cm), Decorative Terrarium for Fl |
| None  | 5056239405098                                                                           | HIGHLY_LIKELY_RECOMMENDED | £0.94             | £1.01              | FREEZER & FOOD BAGS 500 ROLL                         | 500 x Clear Plastic Freezer Bags on Roll                               |
| None  | Anti Colic Vent                                                                         | HIGHLY_LIKELY_RECOMMENDED | 5015302106713     | Silicone Teat      | FIRST STEPS SAFARI BABY FEEDING BOTTLE 150ML         | NUK First Choice+ Baby Bottle                                          |
| None  | B000TAUFFG                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £1.62              | YALE ESSENTIALS DEADLOCK P/BRASS 64MM                | Yale British Standard 5 Lever Mortice Deadlock, High Security, Visi Pa |
| None  | B09K42Z3JN                                                                              | HIGHLY_LIKELY_RECOMMENDED | 200               | £0.42              | TRAVEL CARD HOLDER 1500                              | Genuine Leather Oyster Card Holder Bus Travel Pass Holders - Black     |
| None  | 5022822194984                                                                           | HIGHLY_LIKELY_RECOMMENDED | £0.04             | £3.49              | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM         | STATUS 2 Way Socket                                                    |
| None  | B0CLCBL6DT                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £5.67              | CHRISTMAS PIPE CLEANERS 40PC                         | PLULON 60 Sets Christmas Crafts for Kids Christmas Beaded Ornament Kit |
| None  | B08V4Y13M3                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £4.58              | TABLE TOP TRASH CAN                                  | Small desk bin mini waste bin with lid kids dustbin trash can for clas |
| None  | B0DT4NPX7D                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £2.48              | BABY PIPKIN SILICONE PACIFIER                        | Baby Fruit Feeder Set, Includes 2 Food Dummy Feeders with 3 Size Nippl |
| None  | B0FCFHX3F6                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £2.60              | FLEXIBLE GAS LIGHTER                                 | VVAY Flexible Long Reach Lighter, Jet Torch Lighter Gas Butane Refilla |
| None  | B0FLDN8K1Q                                                                              | HIGHLY_LIKELY_RECOMMENDED | 100               | £4.49              | TINSEL STAR 20CM  LED WHITE IRIDESCENT               | LAWOHO Christmas Tree Topper Tinsel Star, Exquisite Christmas Decor, 1 |
| None  | Soft and Durable Gradening Kneeling Pad                                                 | HIGHLY_LIKELY_RECOMMENDED | £0.67             | -                  | GARDEN KNEELING PAD 40CM                             | AKHÂ® Garden Kneeling Mat                                              |
```

## Important Context
- The OPUS baseline comes from executing `manual_analysis_review.py` against the full XLSX and exporting all rows it labeled as non-EXCLUDE; this is broader than the summarized OPUS `FINAL_UPDATED_REPORT_20260103.md` (which does not enumerate all 2,635 rows).
- If you want the comparison strictly against OPUS’s 433-row corrected shortlist, we need a machine-readable export (RowID/ASIN + verdict) for that shortlist (the markdown report contains placeholders).