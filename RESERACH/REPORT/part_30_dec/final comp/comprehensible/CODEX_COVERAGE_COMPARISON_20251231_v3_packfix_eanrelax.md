# CODEX COVERAGE COMPARISON (COMPREHENSIBLE REPORTS)

**Generated:** 2025-12-31 08:23:56
**Dataset:** C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx

## Inputs (Verified Existing Files)

- COMPREHENSIBLE_COMBINED_V2: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\final comp\comprehensible\PHASEA_MANUAL_REPORT_FINAL_COMBINED_20251231_v2.md (bytes=45822, mtime=2025-12-31 03:38:03.126242)
- CODEX_STRICT: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\final comp\comprehensible\PHASEA_MANUAL_REPORT_CODEX_FINAL_20251231.md (bytes=68177, mtime=2025-12-31 08:23:34.349193)
- FINAL_MD: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\final comp\comprehensible\PHASEA_MANUAL_REPORT_FINAL.md (bytes=62746, mtime=2025-12-31 04:52:06.191905)
- FINAL_20251231: C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\final comp\comprehensible\PHASEA_MANUAL_REPORT_FINAL_20251231.md (bytes=69659, mtime=2025-12-31 04:48:01.885684)

## Parsed Coverage (RowID-based)

Derived counts are based on mapping report table rows to dataset RowIDs using ASIN/EAN/title tie-breaks.

```text
| Report                     | VERIFIED_REC | VERIFIED_FILT | HL_REC | HL_FILT | NV | FILTERED_AUDIT | TOTAL_UNIQUE |
|----------------------------|--------------|---------------|--------|---------|----|----------------|--------------|
| COMPREHENSIBLE_COMBINED_V2 | 32           | 1             | 10     | 25      | 44 | 0              | 112          |
| CODEX_STRICT               | 26           | 7             | 36     | 6       | 47 | 0              | 122          |
| FINAL_MD                   | 22           | 7             | 49     | 13      | 40 | 40             | 171          |
| FINAL_20251231             | 28           | 0             | 24     | 0       | 12 | 31             | 95           |
```

## Report-Claimed Summary Counts (For Context)

- COMPREHENSIBLE_COMBINED_V2: VERIFIED — RECOMMENDED=32r; VERIFIED — FILTERED OUT / EXCLUDED=1f; HIGHLY LIKELY — RECOMMENDED=10r; HIGHLY LIKELY — FILTERED OUT / EXCLUDED=25f; NEEDS VERIFICATION=44; TOTAL ANALYZED=112; > Scope note=Profit/ROI were NOT used as filters (per your similarity-only instruction).; > Inclusion rule=only rows with (a) exact EAN proof, or (b) similarity score ≥55, or (c) strong-match-but-wrong-variant conflicts are included. Lower-similarity rows from individual model reports are omitted.; > NEEDS VERIFICATION is STRICT=intended to be upgradeable via 1–2 confirmable details.
- CODEX_STRICT: **VERIFIED — RECOMMENDED=** 26; **VERIFIED — FILTERED OUT / EXCLUDED=** 7; **HIGHLY LIKELY — RECOMMENDED=** 36; **HIGHLY LIKELY — FILTERED OUT / EXCLUDED=** 6; **NEEDS VERIFICATION=** 47 (Strict shortlist; score >= 45); **TOTAL ANALYZED=** 2102; Referenced (unique) products across 8 reports=467; Unresolved table rows by report (unable to map to dataset RowID)=Codex HIGH=1, Codex samecha=1, Codex very high=1, Gemini=24, Opus=12, cli=6, opus2=5, webapp gpt=40
- FINAL_MD: **VERIFIED — RECOMMENDED=** 22; **VERIFIED — FILTERED OUT / EXCLUDED=** 7; **HIGHLY LIKELY — RECOMMENDED=** 49; **HIGHLY LIKELY — FILTERED OUT / EXCLUDED=** 13; **NEEDS VERIFICATION (Strict)=** 40; **FILTERED OUT (Audit - Confirmed Unprofitable)=** 41; **TOTAL ANALYZED=** 389
- FINAL_20251231: VERIFIED — RECOMMENDED=28; VERIFIED — FILTERED OUT / EXCLUDED=0; HIGHLY LIKELY — RECOMMENDED=24; HIGHLY LIKELY — FILTERED OUT / EXCLUDED=0; NEEDS VERIFICATION=12; TOTAL ANALYZED=95

## Codex Coverage Gaps vs Union of All Comprehensible Reports

- Union (unique RowIDs across all 4 reports): 219
- Codex strict (unique RowIDs): 122
- Present in other report(s) but missing from Codex strict: 97

### Primary Reasons Missing Rows Were Not Included in Codex Strict

- 38x: Pack mismatch => adjusted profit <= 0
- 37x: EAN mismatch with insufficient title similarity (<65)
- 15x: Not a strong enough match under v4.0 gates (brand/type/sim)
- 1x: Variant mismatch (Scent ['EUCALYPTUS'] vs ['FRESH', 'LEMON'])
- 1x: Variant mismatch (Color ['NAVY'] vs ['BLACK'])
- 1x: Variant mismatch (Scent ['LEMON'] vs ['LAVENDER', 'LEMON'])
- 1x: Variant mismatch (Color ['GREY'] vs ['GREEN'])
- 1x: Variant mismatch (Color ['WHITE'] vs ['GREEN'])
- 1x: Variant mismatch (Scent ['LIME'] vs ['ORANGE'])
- 1x: Variant mismatch (Size ['SMALL'] vs ['LARGE', 'MEDIUM', 'XL'])

### Would-Be Section Breakdown (If Re-evaluated Under Codex v4.0 Gates)

- 97x: EXCLUDED

### Examples (First 40 Missing RowIDs)

```text
| RowID | ASIN       | Supplier EAN  | Amazon EAN    | SeenIn                                           | WouldBe  | Reason                                           | SupplierTitle                                    |
|-------|------------|---------------|---------------|--------------------------------------------------|----------|--------------------------------------------------|--------------------------------------------------|
| 23    | B07R97DV7D | 1072556214803 | 810833027156  | COMPREHENSIBLE_COMBINED_V2,FINAL_MD              | EXCLUDED | EAN mismatch with insufficient title similari... | SMART CHOICE 10 RAWHIDE CHICKEN TREAT            |
| 32    | B0F24X8FY5 | 5025364006876 | 5025364007330 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | TIDYZ FREEZER BAGS 150PCS                        |
| 48    | B07DXP3JVB | 5052516214797 | 5060042470419 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | SMART CHOICE 30 BEEF/CHICKEN STICKS              |
| 72    | B004MM6OSY | 5012904001842 | -             | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | CHEF AID PASTRY CUTTERS  W184                    |
| 113   | B07B656W3B | 5025364002052 | 8800202193607 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | TIDYZ BIN LINER BLACK 10 BAGS 50LTR              |
| 132   | B0DJDH23JW | 5060357990091 | 5060357990107 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR          |
| 140   | B07QQBHTT4 | 5010353329166 | 5010353322822 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4PC        |
| 163   | B09377NPKH | 5024418537410 | -             | COMPREHENSIBLE_COMBINED_V2,FINAL_20251231        | EXCLUDED | Pack mismatch => adjusted profit <= 0            | SIL TOILET ROLL HOLDER STAINLESS STEEL           |
| 259   | B07F2MFZT5 | 5025364000652 | 8800202181437 | FINAL_20251231                                   | EXCLUDED | Pack mismatch => adjusted profit <= 0            | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L   |
| 260   | B07F2MFZT5 | 5025364006043 | 8800202181437 | FINAL_20251231,FINAL_MD                          | EXCLUDED | Pack mismatch => adjusted profit <= 0            | TIDYZ COMPOSTABLE 15 BAGS 10LTR                  |
| 262   | B08FBJ59DR | 5023139862917 | -             | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | Not a strong enough match under v4.0 gates (b... | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (... |
| 287   | B08FBJ59DR | 5023139861019 | -             | FINAL_20251231,FINAL_MD                          | EXCLUDED | Pack mismatch => adjusted profit <= 0            | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMAL... |
| 289   | B01089N3RO | 5010559680023 | 5010559338696 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | DRAPER HEX KEY SET METRIC DIY 8 PC               |
| 293   | B08TCDBQTC | 5023139270705 | 9876553908060 | COMPREHENSIBLE_COMBINED_V2,FINAL_20251231,FIN... | EXCLUDED | Pack mismatch => adjusted profit <= 0            | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M        |
| 358   | B001326TJA | 5029347300029 | -             | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | Not a strong enough match under v4.0 gates (b... | EVERBUILD ONE STRIKE FILLER 250ML                |
| 476   | B0DFH6MH97 | 5025364005572 | 5025364007873 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | TIDYZ FOOD BAG 300PCS                            |
| 490   | B08F7X9Y9Z | 5010789510978 | -             | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | Not a strong enough match under v4.0 gates (b... | BARTOLINE EASIPASTE 1KG                          |
| 499   | B00QM9CG7I | 5014353089983 | -             | FINAL_20251231,FINAL_MD                          | EXCLUDED | Pack mismatch => adjusted profit <= 0            | KILROCK DAMP CLEAR REFILL POUCH 1KG (2x500g)     |
| 517   | B07YQ7BSR4 | 8692952202568 | 5056057687577 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | LAV TUMBLER 3PCS                                 |
| 523   | B0BN8J4WLM | 3426470299985 | -             | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | PYREX BUTTERFLY RECTANGULAR DISH SET OF 2        |
| 564   | B09WHRL5M9 | 5024418379584 | 5060961900127 | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | EAN mismatch with insufficient title similari... | WAX MELTS YOGA 68G 6 PCS                         |
| 576   | B0D9KKTVZK | 8721037402613 | 5060630695699 | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | EAN mismatch with insufficient title similari... | CHAMPAGNE GLASS PLASTIC ASSORTED 177ML           |
| 604   | B08P9TJM2N | 5017403145530 | -             | FINAL_MD                                         | EXCLUDED | Not a strong enough match under v4.0 gates (b... | BLACKSPUR SEL DRILL PLASTERBOARD FIXING 30PC     |
| 627   | B08KJB12RQ | 5010853197838 | 5010853271859 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | MASON CASH MIXING BOWL OWL STONE 26CM            |
| 714   | B0DCGDS6Y5 | 5010303185965 | -             | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | Not a strong enough match under v4.0 gates (b... | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550ML        |
| 726   | B08P8GS8XP | 5038135120701 | 9876553862614 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | WHAM CRYSTAL 160LTR CLEAR BOX & LID              |
| 738   | B0CNCZJLYF | 6923456823471 | -             | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | SQUARE SPICE JAR BLACK/WHITE                     |
| 770   | B003ESK66S | 5052516214834 | 5054591085743 | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | EAN mismatch with insufficient title similari... | SMART CHOICE CHICKEN & RICE BONE DOG TREAT 10... |
| 771   | B095X7QFSN | 5024418552062 | 5060003610953 | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | EAN mismatch with insufficient title similari... | CHRISTMAS TEALIGHTS SPICED CINNAMON 10 PACK      |
| 790   | B07G3673W4 | 5050028108436 | 5055905295872 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | JCB LED BULB WARM WHITE CANDLE BC 6W/40W         |
| 801   | B0D7HTYPTL | 8721037573603 | 5060914443909 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | GLASS BOTTLE 120ML                               |
| 803   | B095X8CDZJ | 5053249251561 | 5060003610809 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | PAN AROMA TEALIGHTS 16PC BERGAMOT MANDARIN       |
| 807   | B0FP2FYNHZ | 5025301757007 | -             | FINAL_MD                                         | EXCLUDED | Not a strong enough match under v4.0 gates (b... | THE CHRISTMAS WORKSHOP 40 FAIRY LIGHTS  CLEAR    |
| 828   | B072KDL23B | 5050796010764 | -             | COMPREHENSIBLE_COMBINED_V2,FINAL_20251231,FIN... | EXCLUDED | Pack mismatch => adjusted profit <= 0            | BRIGHT & HOMELY CITRONELLA TEALIGHT CANDLES L... |
| 835   | B095X7QFSN | 5053249262628 | 5060003610953 | COMPREHENSIBLE_COMBINED_V2                       | EXCLUDED | EAN mismatch with insufficient title similari... | PAN AROMAREINDEER 12PK CHRISTMAS TEALIGHTS -...  |
| 870   | B08X8QVKXD | 8011893819039 | 5060757801119 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | ROYAL MARKET BIN LINER GARDEN 10 BAG             |
| 909   | B07GZGXQYG | 5060357994426 | 5060357992217 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | SUPERIOR FOIL 5 CONTAINERS & LID 4.5LTR          |
| 926   | B095KDP4MN | 5060471890352 | 7427269287653 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | TURBO JET AIR FRESHENER / SANITISER SPRAY FRE... |
| 928   | B08GG7YYSQ | 5053249269016 | 5056291620842 | FINAL_MD                                         | EXCLUDED | Pack mismatch => adjusted profit <= 0            | PAN AROMA POTPOURRI ASSORTED 180G                |
| 945   | B08N713Y2V | 5022822163881 | 5022822202900 | FINAL_MD                                         | EXCLUDED | EAN mismatch with insufficient title similari... | STATUS TV AERIAL LEAD 5M CABLE IN CDU            |
```

## Per-Report Differences vs Codex Strict (Why Some Reports Look Larger)

### COMPREHENSIBLE_COMBINED_V2

- Unique RowIDs in this report: 112
- Unique RowIDs missing from Codex strict: 30

Main exclusion reasons for this report's extra rows:
- 12x: EAN mismatch with insufficient title similarity (<65)
- 6x: Not a strong enough match under v4.0 gates (brand/type/sim)
- 5x: Pack mismatch => adjusted profit <= 0
- 1x: Variant mismatch (Scent ['EUCALYPTUS'] vs ['FRESH', 'LEMON'])
- 1x: Variant mismatch (Color ['NAVY'] vs ['BLACK'])
- 1x: Variant mismatch (Scent ['LEMON'] vs ['LAVENDER', 'LEMON'])
- 1x: Variant mismatch (Color ['GREY'] vs ['GREEN'])
- 1x: Variant mismatch (Color ['WHITE'] vs ['GREEN'])

Examples (first 12 extra rows):

```text
| RowID | ASIN       | Supplier EAN  | Amazon EAN    | Reason                                               | SupplierTitle                                        |
|-------|------------|---------------|---------------|------------------------------------------------------|------------------------------------------------------|
| 23    | B07R97DV7D | 1072556214803 | 810833027156  | EAN mismatch with insufficient title similarity (... | SMART CHOICE 10 RAWHIDE CHICKEN TREAT                |
| 163   | B09377NPKH | 5024418537410 | -             | Pack mismatch => adjusted profit <= 0                | SIL TOILET ROLL HOLDER STAINLESS STEEL               |
| 262   | B08FBJ59DR | 5023139862917 | -             | Not a strong enough match under v4.0 gates (brand... | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM Â... |
| 293   | B08TCDBQTC | 5023139270705 | 9876553908060 | Pack mismatch => adjusted profit <= 0                | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M            |
| 358   | B001326TJA | 5029347300029 | -             | Not a strong enough match under v4.0 gates (brand... | EVERBUILD ONE STRIKE FILLER 250ML                    |
| 490   | B08F7X9Y9Z | 5010789510978 | -             | Not a strong enough match under v4.0 gates (brand... | BARTOLINE EASIPASTE 1KG                              |
| 564   | B09WHRL5M9 | 5024418379584 | 5060961900127 | EAN mismatch with insufficient title similarity (... | WAX MELTS YOGA 68G 6 PCS                             |
| 576   | B0D9KKTVZK | 8721037402613 | 5060630695699 | EAN mismatch with insufficient title similarity (... | CHAMPAGNE GLASS PLASTIC ASSORTED 177ML               |
| 714   | B0DCGDS6Y5 | 5010303185965 | -             | Not a strong enough match under v4.0 gates (brand... | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550ML            |
| 770   | B003ESK66S | 5052516214834 | 5054591085743 | EAN mismatch with insufficient title similarity (... | SMART CHOICE CHICKEN & RICE BONE DOG TREAT 10 PK...  |
| 771   | B095X7QFSN | 5024418552062 | 5060003610953 | EAN mismatch with insufficient title similarity (... | CHRISTMAS TEALIGHTS SPICED CINNAMON 10 PACK          |
| 828   | B072KDL23B | 5050796010764 | -             | Pack mismatch => adjusted profit <= 0                | BRIGHT & HOMELY CITRONELLA TEALIGHT CANDLES LARGE... |
```

### FINAL_MD

- Unique RowIDs in this report: 171
- Unique RowIDs missing from Codex strict: 76

Main exclusion reasons for this report's extra rows:
- 36x: Pack mismatch => adjusted profit <= 0
- 26x: EAN mismatch with insufficient title similarity (<65)
- 9x: Not a strong enough match under v4.0 gates (brand/type/sim)
- 1x: Variant mismatch (Scent ['EUCALYPTUS'] vs ['FRESH', 'LEMON'])
- 1x: Variant mismatch (Color ['NAVY'] vs ['BLACK'])
- 1x: Variant mismatch (Scent ['LEMON'] vs ['LAVENDER', 'LEMON'])
- 1x: Variant mismatch (Scent ['LIME'] vs ['ORANGE'])
- 1x: Variant mismatch (Size ['SMALL'] vs ['LARGE', 'MEDIUM', 'XL'])

Examples (first 12 extra rows):

```text
| RowID | ASIN       | Supplier EAN  | Amazon EAN    | Reason                                               | SupplierTitle                                     |
|-------|------------|---------------|---------------|------------------------------------------------------|---------------------------------------------------|
| 23    | B07R97DV7D | 1072556214803 | 810833027156  | EAN mismatch with insufficient title similarity (... | SMART CHOICE 10 RAWHIDE CHICKEN TREAT             |
| 32    | B0F24X8FY5 | 5025364006876 | 5025364007330 | EAN mismatch with insufficient title similarity (... | TIDYZ FREEZER BAGS 150PCS                         |
| 48    | B07DXP3JVB | 5052516214797 | 5060042470419 | Pack mismatch => adjusted profit <= 0                | SMART CHOICE 30 BEEF/CHICKEN STICKS               |
| 72    | B004MM6OSY | 5012904001842 | -             | Pack mismatch => adjusted profit <= 0                | CHEF AID PASTRY CUTTERS  W184                     |
| 113   | B07B656W3B | 5025364002052 | 8800202193607 | EAN mismatch with insufficient title similarity (... | TIDYZ BIN LINER BLACK 10 BAGS 50LTR               |
| 132   | B0DJDH23JW | 5060357990091 | 5060357990107 | EAN mismatch with insufficient title similarity (... | SUPERIOR FOIL 10 CONTAINERS & LID 2 LTR           |
| 140   | B07QQBHTT4 | 5010353329166 | 5010353322822 | EAN mismatch with insufficient title similarity (... | MINKY ANTI BACTERIAL MICROFIBRE ROLLS 4PC         |
| 260   | B07F2MFZT5 | 5025364006043 | 8800202181437 | Pack mismatch => adjusted profit <= 0                | TIDYZ COMPOSTABLE 15 BAGS 10LTR                   |
| 287   | B08FBJ59DR | 5023139861019 | -             | Pack mismatch => adjusted profit <= 0                | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L |
| 289   | B01089N3RO | 5010559680023 | 5010559338696 | EAN mismatch with insufficient title similarity (... | DRAPER HEX KEY SET METRIC DIY 8 PC                |
| 293   | B08TCDBQTC | 5023139270705 | 9876553908060 | Pack mismatch => adjusted profit <= 0                | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M         |
| 476   | B0DFH6MH97 | 5025364005572 | 5025364007873 | EAN mismatch with insufficient title similarity (... | TIDYZ FOOD BAG 300PCS                             |
```

### FINAL_20251231

- Unique RowIDs in this report: 95
- Unique RowIDs missing from Codex strict: 20

Main exclusion reasons for this report's extra rows:
- 18x: Pack mismatch => adjusted profit <= 0
- 1x: Variant mismatch (Scent ['EUCALYPTUS'] vs ['FRESH', 'LEMON'])
- 1x: Variant mismatch (Color ['NAVY'] vs ['BLACK'])

Examples (first 12 extra rows):

```text
| RowID | ASIN       | Supplier EAN  | Amazon EAN    | Reason                                               | SupplierTitle                                        |
|-------|------------|---------------|---------------|------------------------------------------------------|------------------------------------------------------|
| 163   | B09377NPKH | 5024418537410 | -             | Pack mismatch => adjusted profit <= 0                | SIL TOILET ROLL HOLDER STAINLESS STEEL               |
| 259   | B07F2MFZT5 | 5025364000652 | 8800202181437 | Pack mismatch => adjusted profit <= 0                | TIDYZ PEDAL BIN LINERS 40 WHITE TIE HANDLE 15L       |
| 260   | B07F2MFZT5 | 5025364006043 | 8800202181437 | Pack mismatch => adjusted profit <= 0                | TIDYZ COMPOSTABLE 15 BAGS 10LTR                      |
| 287   | B08FBJ59DR | 5023139861019 | -             | Pack mismatch => adjusted profit <= 0                | BACOFOIL ZIPPER BAGS ALL PURPOSE 15 PACK SMALL 1L    |
| 293   | B08TCDBQTC | 5023139270705 | 9876553908060 | Pack mismatch => adjusted profit <= 0                | BACOFOIL EASY CUT KITCHEN FOIL REFILL 15M            |
| 499   | B00QM9CG7I | 5014353089983 | -             | Pack mismatch => adjusted profit <= 0                | KILROCK DAMP CLEAR REFILL POUCH 1KG (2x500g)         |
| 828   | B072KDL23B | 5050796010764 | -             | Pack mismatch => adjusted profit <= 0                | BRIGHT & HOMELY CITRONELLA TEALIGHT CANDLES LARGE... |
| 952   | B07F2P9ZXR | 5025364000003 | 8800202181697 | Pack mismatch => adjusted profit <= 0                | TIDYZ CARRIERS HANDY BAGS 40 PCS 45CM x 57.5cm       |
| 976   | B0CCJS5GKB | 5053249277943 | 5053249253183 | Variant mismatch (Scent ['EUCALYPTUS'] vs ['FRESH... | ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G  |
| 1008  | B0FH524WXP | 5053249279756 | 5053249279770 | Pack mismatch => adjusted profit <= 0                | NUAGE BODY POWDER TALC-FREE CHERRY / WATER LILY A... |
| 1115  | B07MZ2Z9GL | 5060357992750 | 5060357992415 | Pack mismatch => adjusted profit <= 0                | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ               |
| 1116  | B0DKD8V7F6 | 5060357992767 | 5060357992422 | Pack mismatch => adjusted profit <= 0                | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ               |
```

## Notes on Disagreements / Larger Section Counts in Other Reports

When other reports show larger counts, the dominant causes (confirmed by Row-level re-evaluation) are: pack/quantity mismatches that make adjusted profit <= 0, variant mismatches (scent/color/size), EAN mismatches without sufficient similarity, and lower-quality NV items that do not meet the strict shortlist.
