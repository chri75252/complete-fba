# COMPARISON REPORT: OPUS baseline vs CODEX report (fixed table parsing)
**Generated:** 2026-01-03 09:20:10
**CODEX report:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\PHASEA_MANUAL_REPORT_20260103.md
**CODEX dataset:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\CODEX_REPORT_DATASET_FIXED_20260103_091920.csv
**OPUS baseline dataset:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\CODEX final\OPUS_BASELINE_DATASET_20260103_091212.csv

## Summary
- CODEX included: 532 rows
- OPUS baseline non-excluded: 1377 rows
- Matched: 241
- Disagreements among matched: 84
- OPUS-only (baseline rows CODEX did not include): 1144
- CODEX-only (rows baseline would EXCLUDE / or unmatched): 291

## Confusion Matrix (matched rows)
```text
| CODEX                     | OPUS                        | Count |
|---------------------------|-----------------------------|-------|
| HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_RECOMMENDED   | 84    |
| VERIFIED_RECOMMENDED      | VERIFIED_RECOMMENDED        | 31    |
| HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 23    |
| NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 19    |
| HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_FILTERED      | 17    |
| NEEDS_VERIFICATION        | NEEDS_VERIFICATION          | 17    |
| HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 16    |
| VERIFIED_FILTERED         | VERIFIED_FILTERED           | 8     |
| HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 5     |
| HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 5     |
| HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 4     |
| HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION          | 3     |
| HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 3     |
| NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 3     |
| VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 2     |
| VERIFIED_FILTERED         | VERIFIED_RECOMMENDED        | 1     |
```

## Highest-Impact Category Disagreements (matched rows)
```text
| RowID | ASIN       | CODEX_Category            | OPUS_Category               | Sales | NetProfit | AdjProfit | MatchBy              | SupplierTitle                                                          |
|-------|------------|---------------------------|-----------------------------|-------|-----------|-----------|----------------------|------------------------------------------------------------------------|
| 1815  | B0DJDH23JW | VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 700   | £2.13     | £2.13     | RowID                | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN                                |
| 2404  | B007IGLUIK | VERIFIED_FILTERED         | VERIFIED_RECOMMENDED        | 100   | £0.43     | £-2.66    | RowID                | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR                               |
| 2422  | B074V9468X | VERIFIED_RECOMMENDED      | VERIFIED_FILTERED           | 50    | £0.55     | £0.55     | RowID                | WHAM CRYSTAL 32LTR CLEAR UNDERBED BOX&LID                              |
| 2307  | B07QQBHTT4 | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 700   | £0.40     | £0.40     | RowID                | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4PC                              |
| 1414  | B01089N3RO | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 500   | £2.66     | £2.66     | RowID                | DRAPER HEX KEY SET METRIC DIY 8 PC                                     |
| 1008  | B00I1JW98I | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 100   | £2.86     | £2.86     | RowID                | PASABAHCE CIHANGIR TEA GLASS 95 CC 6PC                                 |
| 1095  | B00I1JW98I | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 100   | £2.73     | £2.73     | RowID                | PASABAHCE KANDILLI OPTIC TEA GLASS 90CC 6PC                            |
| 2504  | B004GY24EQ | HIGHLY_LIKELY_RECOMMENDED | HIGHLY_LIKELY_FILTERED      | 50    | £0.21     | £0.21     | RowID                | AMTECH BOX SPANNER /TOMMY BAR                                          |
| 1010  | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £5.00     | £5.00     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML                                |
| 1362  | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £4.16     | £4.16     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 9X13IN                                |
| 1520  | B07GZGXQYG | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION_FILTERED | 200   | £3.06     | £3.06     | ASIN_ambiguous_first | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR                                |
| 255   | B009S64OI6 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 800   | £16.14    | £16.14    | RowID                | WORLD OF PETS CAT LITTER SCENTED 3LT                                   |
| 686   | B0B3F548G7 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £33.63    | £33.63    | RowID                | QUEST EXPRESSO COFFEE EXPRESSO MACHINE WITH MILK FROTHER               |
| 1224  | B00M16SQ8O | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £1.54     | £1.54     | RowID                | SALT & PEPPER SHAKERS                                                  |
| 1599  | B07MGLHMWY | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 500   | £1.09     | £1.09     | RowID                | WASTE SMART EXTRA STRONG WHEELIE BIN 5 BAGS                            |
| 996   | B06Y1L9G65 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 400   | £4.40     | £4.40     | RowID                | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE                               |
| 932   | B08HX852WM | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 300   | £2.44     | £2.44     | RowID                | WASTE SMART STRONG REFUSE SACKS 20 BAGS                                |
| 380   | B0D5HN7W14 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 200   | £12.05    | £12.05    | RowID                | CHEF AID SANTOKU KNIFE SOFT GRIP HANDLE                                |
| 89    | B0FS1K5WQH | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 200   | £24.02    | £24.02    | RowID                | SMART CHOICE RUBBER BALL DOG TOY                                       |
| 890   | B07FYQJXXC | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £7.19     | £7.19     | RowID                | WOODEN INSECT HOUSE METAL ROOF                                         |
| 950   | B00X3Z2RQY | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £2.51     | £2.51     | RowID                | SPICE IT UP CHILLI FLAKES SEASON GRINDER                               |
| 1294  | B07F8VJHWF | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 100   | £6.45     | £6.45     | RowID                | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK                     |
| 444   | B0DHRVB13P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £4.57     | £4.57     | RowID                | WORLD OF PETS TOY TUG WITH BALL                                        |
| 1199  | B0BHSR7XK1 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.47     | £2.47     | RowID                | LADIES KNITTED HAT WITH FAUX FUR POM-POM                               |
| 2429  | B0D8QFWZ7N | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.25     | £0.25     | RowID                | MEMORIAL PLASTIC SPIKE SPECIAL MUM & DAD                               |
| 2532  | B01N7UCP9P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.07     | £0.07     | RowID                | HAPPY 8TH BIRTHDAY BANNER PINK 9FT                                     |
| 2634  | B0CQ4VX6Z5 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.00     | £0.00     | RowID                | FLOW FLOOR & SURFACE CLEANER 5L EACH                                   |
| 782   | B00555EWJU | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £3.06     | £3.06     | RowID                | JUMBO SLIDER STORAGE BAGS 10PC                                         |
| 1057  | B092ZL7VRV | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.71     | £2.71     | RowID                | CURVER RATTAN ROUND LARGE ORGANISER GREY                               |
| 1167  | B0028YPW68 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £8.58     | £8.58     | ASIN                 | GREEN BLADE 2PCE GARDEN SHEAR SET                                      |
| 1299  | B07K1T1N6Y | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £4.45     | £4.45     | RowID                | SEAGRASS FOLDABLE BASKET 32CM                                          |
| 1385  | B0BF5DTF98 | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £2.33     | £2.33     | RowID                | BOWL FLAT GLASS EMBOSSED DROPS 7CM GREEN                               |
| 1611  | B093HHQ7HB | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.99     | £0.99     | RowID                | MEMORIAL GRAVE FLOWER VASE WITH STAKE                                  |
| 2531  | B01N7UCP9P | HIGHLY_LIKELY_RECOMMENDED | NEEDS_VERIFICATION          | 50    | £0.07     | £0.07     | RowID                | HAPPY 8TH BIRTHDAY BANNER 9FT                                          |
| 2065  | B0DL5RW6LV | HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 900   | £0.45     | £-43.06   | ASIN                 | PAPER MOROCCAN DESIGN 8 BOWLS 7.5 INCH                                 |
| 1877  | B0F24X8FY5 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 900   | £0.61     | £0.61     | RowID                | TIDYZ FREEZER BAGS 150PCS                                              |
| 1878  | B0F24X8FY5 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 900   | £0.61     | £0.61     | RowID                | TIDYZ FREEZER BAGS 100 PCS XLLARGE                                     |
| 1142  | B09F31QSQB | HIGHLY_LIKELY_FILTERED    | NEEDS_VERIFICATION_FILTERED | 800   | £1.93     | £-25.29   | ASIN_ambiguous_first | CEDAR WOOD balls 12PK                                                  |
| 2215  | B004MM6OSY | NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 800   | £0.38     | £0.38     | RowID                | CHEF AID PASTRY CUTTERS  W184                                          |
| 1176  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £3.28     | £-17.24   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR                                |
| 1334  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £3.00     | £-20.55   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR                                |
| 2063  | B0DJDH23JW | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 700   | £1.48     | £-38.48   | ASIN                 | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR                                |
| 1375  | B07B656W3B | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 700   | £1.23     | £1.23     | RowID                | TIDYZ BIN LINER BLACK 10 BAGS 50LTR                                    |
| 1613  | B07QQBHTT4 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 700   | £1.01     | £-0.81    | RowID                | MINKY CLOTH GRILL AND PAN SCOURER 2PK                                  |
| 2076  | B07QQBHTT4 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 700   | £0.59     | £0.59     | RowID                | MINKY ALL PURPOSE CLOTH PK10                                           |
| 2222  | B07QQBHTT4 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 700   | £0.47     | £0.47     | RowID                | MINKY BRITES FLAT SCOURING PAD 4PC                                     |
| 769   | B07F2MFZT5 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 500   | £2.73     | £-1.29    | RowID                | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L                         |
| 2327  | B09BW2TZ9N | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 500   | £0.28     | £-2.00    | ASIN                 | SPRAY ON GREASE 200ML                                                  |
| 2407  | B00JITIIQ2 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £0.43     | £-21.08   | RowID                | ROLSON BALL ENDED HEX SCREWDRIVER 7PC BITS                             |
| 934   | B07STZLCM6 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £5.47     | £5.47     | RowID                | SOUDAL EXPANDING FOAM HAND HELD 150ML                                  |
| 2268  | B0C6FQLPV3 | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 400   | £0.30     | £-13.81   | RowID                | JAUNTY PARTYWARE BALLOONS TWIST 15                                     |
| 182   | B00IZMVQOO | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 400   | £28.79    | £28.79    | RowID                | EVERBUILD SEALANT STRIPOUT TOOL                                        |
| 347   | B0933MHLG6 | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 400   | £9.98     | £9.98     | RowID                | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM                              |
| 2554  | B0BN8J4WLM | NEEDS_VERIFICATION        | HIGHLY_LIKELY_FILTERED      | 400   | £0.59     | £0.59     | RowID                | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2                              |
| 166   | B07PMB7PYK | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 300   | £10.42    | £-11.11   | RowID                | JAUNTY PARTYWARE CONFETTI PARTY BOWLS 6" 12PK                          |
| 687   | B0DM9FNQ9R | NEEDS_VERIFICATION        | HIGHLY_LIKELY_RECOMMENDED   | 300   | £4.84     | £4.84     | RowID                | FESTIVE MAGIC SANT SLEIGH FELT BUCKET                                  |
| 435   | B08JQKL34C | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 200   | £6.78     | £-168.86  | RowID                | Mokate Gold Premium Coffee Caramel Latte 10pk                          |
| 1249  | B01MZARJ6G | HIGHLY_LIKELY_FILTERED    | VERIFIED_FILTERED           | 200   | £1.43     | £-4.53    | ASIN                 | BEAUTY HAIR GRIP ROLLERS 5 PACK                                        |
| 1418  | B0791ZQMMZ | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 200   | £2.30     | £-1.97    | RowID                | KILROCK DAMP CLEAR MOULD REMOVER ACTIVE FOAMING ACTION 500ML(SOLD EACH |
| 1604  | B085W8MDLH | HIGHLY_LIKELY_FILTERED    | HIGHLY_LIKELY_RECOMMENDED   | 200   | £1.18     | £-2.24    | RowID                | SWIRL TUMBLE DRYER SHEETS LAVENDER 35PK                                |
```

## OPUS-only (baseline): Top by Sales/NetProfit that CODEX did not include
```text
| RowID | ASIN       | CategoryNorm                | Sales | NetProfit         | AdjustedProfit       | SupplierTitle                                            |
|-------|------------|-----------------------------|-------|-------------------|----------------------|----------------------------------------------------------|
| 558   | B0D7BHB64L | NEEDS_VERIFICATION          | 900   | 7.39499999999999  | 7.39499999999999     | ASHLEY CERAMIC HUMIDIFIER                                |
| 269   | B09QMCPGVL | NEEDS_VERIFICATION          | 900   | 6.67833333333333  | 2.6583333333333297   | ADORN PLACEMAT 37CM ASSORTED                             |
| 422   | B06WWQXHMS | NEEDS_VERIFICATION          | 900   | 5.385             | 5.385                | PRIMA STAINLESS STEEL CHEESE KNIFE                       |
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
| 2255  | B0B2QVPP6S | NEEDS_VERIFICATION_FILTERED | 800   | 0.332916666666666 | -27.027083333333334  | FESTIVE MAGIC CHRISTMAS RIBBON CANDT CANE 50MM X 2.7M    |
| 2461  | B0CNTP5KL8 | NEEDS_VERIFICATION          | 800   | 0.214999999999999 | 0.214999999999999    | DLUX MULTI PURPOSE MICROFIBRE CLOTHS 7PCE                |
```

## CODEX-only (unmatched): Sample
```text
| RowID | ASIN       | Category                  | Sales | NetProfit | SupplierTitle                                        |
|-------|------------|---------------------------|-------|-----------|------------------------------------------------------|
| 1616  | B07DHMR1L6 | HIGHLY_LIKELY_RECOMMENDED | 500   | £2.07     | CORAL EASY COATER 4" & FREE BRUSH                    |
| 1022  | B0DP24V73R | HIGHLY_LIKELY_RECOMMENDED | 400   | £6.79     | WOOD FRAME 1INCH OAK 8X10                            |
| 1136  | B09YRC9SXW | HIGHLY_LIKELY_RECOMMENDED | 400   | £2.88     | MINI GLASS JAR 120ML PK6                             |
| 1716  | B08T8JR6YL | HIGHLY_LIKELY_RECOMMENDED | 300   | £0.68     | SILICONE HEAT RESISTANT POT HOLDER                   |
| 2109  | B07L872VYN | HIGHLY_LIKELY_RECOMMENDED | 300   | £0.44     | BUTTERFLY AND RAINBOW HAIR CLIPS 4PC                 |
| 569   | B09X7JR23L | HIGHLY_LIKELY_RECOMMENDED | 200   | £5.34     | Plastic Food Containers 1000ml 4pk                   |
| 991   | B09X78TC7Q | HIGHLY_LIKELY_RECOMMENDED | 200   | £2.13     | RUBBER DUCK FAMILY BATH TOY 3 PACK                   |
| 1234  | B0B51H18ZK | HIGHLY_LIKELY_RECOMMENDED | 200   | £1.80     | MONEY TIN BOX ASST MEDIUM (2022)                     |
| 1500  | B0DKC45N71 | HIGHLY_LIKELY_RECOMMENDED | 200   | £1.78     | CHRISTMAS TAPER CANDLES SILVER SET OF 4              |
| 1539  | B0BSMPFTTZ | HIGHLY_LIKELY_RECOMMENDED | 200   | £2.44     | PLASTIC MAKEUP STORAGE HOLDER                        |
| 2474  | B0DPMTK6GJ | HIGHLY_LIKELY_RECOMMENDED | 200   | £0.12     | BABY PIPKIN NAIL CLIPPERS & SCISSORS SET             |
| 138   | B0D876QQH4 | HIGHLY_LIKELY_RECOMMENDED | 100   | £15.19    | OVEN LOVE BAKING DISH OVAL RED 0.19L                 |
| 247   | B0FL7M9TBG | HIGHLY_LIKELY_RECOMMENDED | 100   | £8.76     | 2 Pack Dog Squeaky Toys                              |
| 570   | B0F28RTFV4 | HIGHLY_LIKELY_RECOMMENDED | 100   | £4.73     | PLASTIC CLEAR 4 SECTION TRAY                         |
| 574   | B0DJ34RG3C | HIGHLY_LIKELY_RECOMMENDED | 100   | £9.46     | WOOD FRAME 1INCH OAK 5X7                             |
| 628   | B0CV12HTJ9 | HIGHLY_LIKELY_RECOMMENDED | 100   | £4.13     | SPECIAL OCCASIONS RAINBOW COLOUR HAIR SPRAY 200ML    |
| 1240  | B0DCP6NBYX | HIGHLY_LIKELY_RECOMMENDED | 100   | £5.58     | INDOOR & OUTDOOR DOORMAT 60CM X 90CM                 |
| 1325  | B089YPV5SG | HIGHLY_LIKELY_RECOMMENDED | 100   | £2.09     | GREEN HABITATS CLAW GARDEN DIGGING GLOVES            |
| 1610  | B0BQWCQ2WK | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.95     | BANNER BRIGHT CONFETTI HAPPY BIRTHDAY ROSE GOLD 9FT  |
| 1721  | B01MUGGPCZ | HIGHLY_LIKELY_RECOMMENDED | 100   | £2.45     | BACKPACK STANDARD PAW PATROL SKYE                    |
| 1786  | B0BRV3BLL7 | HIGHLY_LIKELY_RECOMMENDED | 100   | £1.73     | GROUND SPIKE HEAVY-DUTY METAL                        |
| 2002  | B0BF184H2G | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.56     | SEWING THREAD BLACK/WHITE 4PC                        |
| 2016  | B09SHKQTSZ | HIGHLY_LIKELY_RECOMMENDED | 100   | £1.22     | COLANDER STAINLESS STEEL 22CM                        |
| 2028  | B0B8SNGDBZ | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.44     | FISH TANK NET - 25CM HANDLE                          |
| 2119  | B0DCW45WNH | HIGHLY_LIKELY_RECOMMENDED | 100   | £2.64     | DUVET SET MICROFIBER GREEK DOUBLE GREY               |
| 2421  | B07MKPCXJ1 | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.15     | HAND SCRUBBING BRUSH WOODEN BILLUR                   |
| 2483  | B01MUGGPCZ | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.49     | BACKPACK DELUXE GLITTER PAW PATROL SKYE              |
| 2497  | B01600WDY4 | HIGHLY_LIKELY_RECOMMENDED | 100   | £0.24     | INCENSE BOX WITH STICKS WOOD                         |
| 1225  | B00QSAZATW | HIGHLY_LIKELY_RECOMMENDED | 50    | £6.55     | WOOD FRAME 1INCH BLACK 12X10                         |
| 1332  | B0D1KX7XKK | HIGHLY_LIKELY_RECOMMENDED | 50    | £4.30     | ALUMINIUM OVEN TRAY 30CM                             |
| 1360  | B08MVDCSJQ | HIGHLY_LIKELY_RECOMMENDED | 50    | £1.66     | MUNCH CRUNCH RAWHIDE PRESSED BONE                    |
| 1361  | B08MVDCSJQ | HIGHLY_LIKELY_RECOMMENDED | 50    | £1.66     | MUNCH CRUNCH RAWHIDE BONE NAT JUMBO                  |
| 1554  | B0DXQ56JTB | HIGHLY_LIKELY_RECOMMENDED | 50    | £4.06     | ALUMINIUM OVEN TRAY 36CM                             |
| 1643  | B0FJ65M42D | HIGHLY_LIKELY_RECOMMENDED | 50    | £2.44     | DOOR MAT COIR HOME SWEET HOME 40 X 60CM              |
| 1939  | B0FZCN5J5F | HIGHLY_LIKELY_RECOMMENDED | 50    | £5.96     | FRAMED ART - TOTTENHAM HOTSPUR F.C KITS 40CM X 40CM  |
| 2360  | B0FZCN5J5F | HIGHLY_LIKELY_RECOMMENDED | 50    | £2.60     | FRAMED ART - TOTTENHAM HOTSPUR F.C SHIRT 50CM X 40CM |
| 2593  | B0F4RS323K | HIGHLY_LIKELY_RECOMMENDED | 50    | £0.30     | FRAMED ART - MANCHESTER UNITED KITS 40CM X 40CM      |
| 1261  | B08FDH654K | HIGHLY_LIKELY_RECOMMENDED | 900   | £2.35     | LADIES FASHION GLOVES WITH FUR INSIDE                |
| 868   | B07MM3DYKP | HIGHLY_LIKELY_RECOMMENDED | 800   | £2.68     | BABY FACE CLOTH PK3                                  |
| 577   | B081WQLR5S | HIGHLY_LIKELY_RECOMMENDED | 700   | £12.74    | MENS LEATHER WALLET 1148                             |
| 597   | B01GEOZEVU | HIGHLY_LIKELY_RECOMMENDED | 700   | £4.46     | BABY PIPKIN FEEDING SPOONS 7PCE                      |
| 1087  | B0D4JNBKP1 | HIGHLY_LIKELY_RECOMMENDED | 500   | £3.43     | NIGHTLIGHT DINOSAUR COLOUR CHANGING                  |
| 1185  | B074QKHZ94 | HIGHLY_LIKELY_RECOMMENDED | 500   | £2.43     | PADLOCK LAMINATED 40MM                               |
| 531   | B0CHBGWTH9 | HIGHLY_LIKELY_RECOMMENDED | 400   | £4.36     | AIR FRYER PAPER LINER ROUND 16X4.4.5CM 50PCE         |
| 681   | B0CHBGWTH9 | HIGHLY_LIKELY_RECOMMENDED | 400   | £4.11     | AIR FRYER PAPER LINER  ROUND 20X4.5CM 50PCE          |
| 1999  | B0D9FFVTB7 | HIGHLY_LIKELY_RECOMMENDED | 400   | £1.10     | CHRISTMAS VOTIVES RED/WHITE BERRY SET OF 3           |
| 90    | B0FN3TVZVL | HIGHLY_LIKELY_RECOMMENDED | 300   | £14.86    | PORCELAIN MUG 12OZ COLOURED                          |
| 926   | B0CHP4MZTM | HIGHLY_LIKELY_RECOMMENDED | 300   | £2.47     | FIRST AID ELBOW SUPPORT BANDAGE 3 SIZES              |
| 1328  | B087YZWHG6 | HIGHLY_LIKELY_RECOMMENDED | 300   | £1.98     | ROTARY LINE COVER                                    |
| 1872  | B08616GDRJ | HIGHLY_LIKELY_RECOMMENDED | 300   | £0.73     | SALT & PEPPER POTS GLASS                             |
| 2145  | B07C8V2DJ7 | HIGHLY_LIKELY_RECOMMENDED | 300   | £3.32     | RUSSELL HOBBS VIENNA CUTLERY SET 16PC                |
| 143   | B0CNCZJLYF | HIGHLY_LIKELY_RECOMMENDED | 200   | £10.72    | SQUARE SPICE JAR BLACK/WHITE                         |
| 599   | B0CKLQ3G62 | HIGHLY_LIKELY_RECOMMENDED | 200   | £3.98     | CERAMIC WAX/OIL BURNER                               |
| 662   | B09Q558B4M | HIGHLY_LIKELY_RECOMMENDED | 200   | £3.58     | ROUND TRAY ASS DECOR                                 |
| 837   | B008EXEVG4 | HIGHLY_LIKELY_RECOMMENDED | 200   | £2.77     | LONDON MUG 10CM                                      |
| 1121  | B0FB2VXH8H | HIGHLY_LIKELY_RECOMMENDED | 200   | £1.98     | HAIR BOBBLES 36PC BROWN BLACK WHITE                  |
| 1229  | B09MTP248R | HIGHLY_LIKELY_RECOMMENDED | 200   | £5.68     | VASE GLASS CYLINDER 20X10X10CM                       |
| 1723  | B0DJC89421 | HIGHLY_LIKELY_RECOMMENDED | 200   | £0.94     | FREEZER & FOOD BAGS 500 ROLL                         |
| 2148  | B09MWPSLQF | HIGHLY_LIKELY_RECOMMENDED | 200   | £0.41     | FIRST STEPS SAFARI BABY FEEDING BOTTLE 150ML         |
| 2258  | B000TAUFFG | HIGHLY_LIKELY_RECOMMENDED | 200   | £1.62     | YALE ESSENTIALS DEADLOCK P/BRASS 64MM                |
```

## Context
- OPUS baseline comes from executing `manual_analysis_review.py` against the full XLSX and exporting non-EXCLUDE rows; the user-provided OPUS markdown shortlist is not machine-diffable due to placeholders.