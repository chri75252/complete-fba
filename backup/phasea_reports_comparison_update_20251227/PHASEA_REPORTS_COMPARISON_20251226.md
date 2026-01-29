# PHASEA Manual Reports vs PART3.xlsx — Independent Cross-Check (2025-12-26)

## Inputs (verified paths)

- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gemini PHASEA_MANUAL_REPORT_20251225.md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gpt PHASEA_MANUAL_REPORT_20251225 (1).md`
- `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\codex PHASEA_MANUAL_REPORT_20251225.md`

`PART3.xlsx` contains **1411** rows; `SupplierURL` domain is **www.efghousewares.co.uk** for all rows.

## Independent classification rules (not using report labels)

I classified matches using only the data present in `PART3.xlsx` (no web browsing):

1. **CONFIRMED (Exact ID match)**  
   `EAN` and `EAN_OnPage` match exactly (digit-normalized). This includes 23 valid GTIN-13 matches plus one non-13-digit exact match (RowID 1157).

2. **HIGHLY LIKELY (Non‑EAN match)**  
   No exact EAN match, but titles strongly align and there is no obvious contradiction from pack cues or measurement cues (e.g., “2 cup vs 6 cup”, “24mm vs 48mm”, “2 x …”).

3. **NEEDS USER VERIFICATION**  
   Everything else (ambiguous, contradictory, or clearly wrong).

## Headline results

### PART3.xlsx overall quality (1411 rows)

- Confirmed: **24**
- Highly likely: **7**
- Needs verification: **1380**

### Per-report counts (based on rows actually listed in each report)

| Report | Rows Listed | Confirmed | Highly Likely | Needs Verification | (Confirmed+Likely)/Total |
|---|---:|---:|---:|---:|---:|
| Gemini | 75 | 24 | 7 | 44 | 41.33% |
| GPT | 192 | 24 | 7 | 161 | 16.15% |
| Codex | 235 | 24 | 7 | 204 | 13.19% |

### Cross-report coverage and “missed entries”

- Union of all rows listed across the 3 manual reports: **280** row IDs.
- Rows present in **all 3** reports: **70** row IDs.
- **No** “good” rows (Confirmed+Highly Likely = 31) were missed by all three reports.
- Gemini is a strict subset of Codex (Gemini ⊂ Codex).
- Gemini omits 122 rows that GPT lists and 160 rows that Codex lists — **all** of those omissions are in **Needs Verification** (i.e., Gemini does not lose any of the 31 high-confidence rows).

## Which report is “best” (highest validity/correctness)

All three reports surface the same 31 high-confidence rows (24 confirmed + 7 highly likely).  
The difference is **noise**:

- **Gemini** has the highest precision (fewest “Needs Verification” rows for the same good-row coverage).
- **GPT** includes many more “Needs Verification” candidates but avoids obviously wrong matches.
- **Codex** is most recall-maximized and includes several **clearly wrong** rows among its listed entries (examples below).

## High-confidence rows (actionable shortlist)

## CONFIRMED (Exact ID match) (count=24)
| RowID | ASIN | EAN | EAN_OnPage | SupplierTitle | AmazonTitle |
|---:|---|---|---|---|---|
| 363 | B0DT71SSPT | 5060357991357 | 5060357991357 | PHOODS FOIL TRAY ROASTER | Superior Sandwich Platter Trays - Pack of 10 Catering Trays for Parti… |
| 370 | B005XKFN0O | 5050028016069 | 5050028016069 | EVERREADY T8 4FT 36W TUBE LIGHT | Eveready T8 Tube 4ft 36w White 3500k |
| 626 | B07WDRQ4J7 | 5059001500861 | 5059001500861 | AIRWICK REED DIFFUSER MULLED WINE 33ML PK5 | Air Wick Essential Oils Reed Diffuser Air Freshener Mulled Wine Scent… |
| 698 | B003XKPUSQ | 5032759031078 | 5032759031078 | AMTECH LED MINI TORCH | Amtech S1532 9 LED mini Torch |
| 889 | B01IFIJ91Y | 5010853235530 | 5010853235530 | MASON CASH MIXING BOWL CREAM 29CM | Mason Cash Colour Mix Cream Mixing Bowl \| 4 Litre Capacity \| 29cm Ear… |
| 931 | B06X9K7NR7 | 5025364001970 | 5025364001970 | TIDYZ DOGGY BAGS STRONG 50 PCS 30cm x 36cm | Tidyz 200 x Extra Large Super Strong Doggy bags (4 x 50),Black |
| 964 | B0DJDH23JW | 5060357990107 | 5060357990107 | SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN | Superior 10-Pack Aluminium Foil Trays with Paper Lids, Heavy Duty Alu… |
| 1103 | B009SJXB32 | 5026180033572 | 5026180033572 | APOLLO VINEGAR SHAKER | apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker, Clear 15 x 5.5… |
| 1157 | B0042FBWQ0 | 26102251102 | 26102251102 | CARAFE .5LT GLASS | Arcoroc ARC C0199 Carafon Vin Carafe, Glass, transparent, 580 ml |
| 1173 | B07YQ5HFFN | 5030481940088 | 5030481940088 | PPS ROUND 40 DOYLEYS 21CM | 40 X White Round LACE DOYLEYS - 22cm/8.5\" Quality Disposable Paper ma… |
| 1210 | B0111N9Z1O | 5039295201040 | 5039295201040 | HOUSE MATE STAINLESS STEEL CLEANER & POLISH | House Mate Stainless Steel Cleaner and Polisher 400ml (Pack of 1) |
| 1215 | B0DPQVJ4NW | 5010792749549 | 5010792749549 | HIGHLAND COW PLAQUE FRIENDS | Lesser & Pavey Love & Affection Highland Cow Wooden Plaque - Friends … |
| 1236 | B0FQK17X7F | 5010792542737 | 5010792542737 | GEL  LED CANDLE FESTIVE ROBIN | Macneil Christmas Robin LED Gel Candle |
| 1249 | B0FMS875KH | 5010792542676 | 5010792542676 | CHRISTMAS LAPTRAY  ROBINS | Cushioned Lap Tray - Christmas Robins Design |
| 1257 | B008F7YP9C | 5019200117338 | 5019200117338 | PRODEC CAULKER 12 INCH | ProDec 12\" Flexible Caulker Blade for Fast, Efficient Application of … |
| 1277 | B00KB225MS | 5013159300353 | 5013159300353 | ELLIOTT WINDOW SQUEEGE 20CM | Elliott Multi-Purpose Window Squeegee perfect for streak free cleanin… |
| 1282 | B007IGLUIK | 5060187173633 | 5060187173633 | MIRROR BLUE CANYON SQUARE PLASTIC MIRROR | Blue Canyon - 18cm Free Standing Square Mirror - White Colour - Perfe… |
| 1331 | B099X92QGG | 5013159004428 | 5013159004428 | ELLIOTTS GLASS SPRAY BOTTLE BROWN480ML | Elliott 480ml Brown Glass Spray Bottle, Manufactured from Recycled Gl… |
| 1367 | B008F6946C | 5060187175750 | 5060187175750 | BLUE CANYON VECTOR SHOWER SPRAY | Blue Canyon Vector Double Tap Shower Spray\| Bathroom Accessory\| Premi… |
| 1383 | B00W3RVAG6 | 5010853203508 | 5010853203508 | MASON CASH CERAMIC RECT DISH 16cm | Mason Cash 2001.542 Collection Fine Stoneware Square Roasting Baking … |
| 1395 | B07YPPK4JY | 5022704000013 | 5022704000013 | FIRE UP NATURAL FIRELIGHTERS 28 PACK | Fireglow Firelighters 24 Pack, White |
| 1396 | B00M36YPIM | 5012904148738 | 5012904148738 | CHEF AID SHOT GLASSES ASSORTED 20PCE | Chef Aid Multi-Coloured Plastic Shot Glasses, Pack of 20 Reusable 30m… |
| 1398 | B096KRFC4W | 5055361761119 | 5055361761119 | MEMORIAL WATERPROOF GRAVESIDE LANTERN WITH ROBIN SOMEONE SP… | Waterproof Robin Memorial Graveside Lantern with LED Candle (Someone … |
| 1405 | B07JD22MJ2 | 8711252100531 | 8711252100531 | GLASS WHISKEY DECANTER | alpina Whiskey Decanter and Caraf |

## HIGHLY LIKELY (No EAN match, strong title/attribute match) (count=7)
| RowID | ASIN | EAN | EAN_OnPage | SupplierTitle | AmazonTitle |
|---:|---|---|---|---|---|
| 1137 | B01CMHNDKC | 5060386422662 |  | BLUE CANYON ROUND WALL MIRROR WHITE | Blue Canyon Round Mirror, 40 cm Length x 40 cm Width, White |
| 1156 | B0DN1HXF9B | 3426470301268 |  | PYREX AIR FRYER SQUARE DISH 20X17CM | PYREX PREPWARE – Square Glass Dish 20 x 17 cm – 1 L |
| 1175 | B006A7D1O4 | 5029594522380 | 5029594522458 | ROLSON PLASTERING TROWEL 280X115MM | Rolson 52245 Smooth Plastering Trowel, Multi, 280 x 120 mm |
| 1198 | B08G1Q1L46 | 5038135558504 |  | BAKER & SALT SWISS ROLL TRAY | Baker & Salt Non-Stick Swiss Roll Tray 32 x 23.5 x 1cm |
| 1209 | B07NNY768K | 5012823030916 |  | FALCON ENAMEL ROUND PIE DISH  26CM | FALCON Round Pie Dish White 26CM |
| 1357 | B0815B7FBY | 5056287402902 |  | HARRIS PUTTY KNIFE | Harris Seriously Good Putty Knife |
| 1384 | B0BYKDX25N | 5010303194387 | 5010303180588 | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | Fairy Soap Dispensing Dish Brush |

## Notes on report categorization (optional)

- All three reports’ **VERIFIED (Exact EAN)** sections are consistent with the “Confirmed” definition above.
- “HIGH LIKELIHOOD” sections include some rows that appear to require manual verification due to pack/measurement mismatch cues. Examples:
  - Row 1155 (tape dimensions differ: 24mm×50m vs 48mm×33m)
  - Row 1402 (teapot capacity differs: 2 cup vs 6 cup)
  - Row 971 (explicit “2 x …” multipack cue)

## Codex: clearly wrong examples (to de-prioritize)

These appear in the Codex report’s listed rows and look like obvious mismatches (supplier item vs unrelated watch accessories):

| RowID | SupplierTitle | AmazonTitle (truncated) |
|---:|---|---|
| 350 | SPONTEX HANDY TOUGH SCOURER | 6 Packs Case for 40mm Apple Watch… |
| 861 | MARIGOLD OUTDOOR GLOVES LARGE | Aimtel 4 Pack Screen Protector Compatible with Samsung Galaxy Watch8… |
| 1243 | CHAMOIS 2.25sq ft WASH LEATHER | 40mm Case for Apple Watch SE… |
| 1386 | SPRAY GREASE 400ML | Aimtel 4 Pack Screen Protector Compatible with Samsung Galaxy Watch8… |

