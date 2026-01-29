# Browser Agent Verification Prompt (EFG Housewares → Amazon.co.uk)

## Objective
Verify whether supplier products from `efghousewares.co.uk` truly match the corresponding Amazon.co.uk listings, focusing first on the highest-probability + highest-upside candidates.

## Important Safety / Integrity Rules
- Do not assume matches from titles alone; confirm with on-page identifiers (EAN/GTIN) and pack/unit count.
- Treat dimension patterns (e.g., `40x34x4`, `9x9 inch`, `150mm`) as measurements, not pack counts.
- If you cannot find an EAN/GTIN on Amazon, record `Amazon EAN = -` and rely on ASIN + unit-count + variant confirmation.
- If the supplier site requires login, use credentials provided separately (DO NOT paste passwords into the final report).

## Websites
- Supplier: https://www.efghousewares.co.uk/
- Amazon: https://www.amazon.co.uk/

## Supplier Login (if prompted)
- Username: `{{EFG_USERNAME}}`
- Password: `{{EFG_PASSWORD}}`

## Amazon Setup (MANDATORY BEFORE START)
1) Ensure delivery location is UK: set postcode to `NW10 7PQ`.
2) Ensure currency is `GBP (£)` (use the UK flag / currency setting at top-right if needed).
3) Record once in the report that setup is confirmed.

## Search Order Per Product
### A) Supplier side (efghousewares.co.uk)
1) Search by **Supplier EAN** if present and not `-`.
2) If Supplier EAN is `-` or search fails: search by **SupplierTitle** (shorten to key tokens if needed).
3) Open the best matching product page and capture: title, brand, pack/unit count, variant (size/scent/color), price, product code/SKU, and EAN/GTIN if shown.

### B) Amazon side (amazon.co.uk)
1) If **Amazon EAN** present and not `-`: search by Amazon EAN.
2) Otherwise: open `https://www.amazon.co.uk/dp/{ASIN}`.
3) Capture: title, brand, unit-count/pack size, selected variation (size/scent/color), GTIN/EAN if present in Product details, and price.

## Match Decision Rules (use these exact labels)
- `CONFIRMED MATCH` = same product + same variant + same unit/pack count (or pack ratio is clearly determinable).
- `LIKELY MATCH` = strong match but one minor detail missing on-page (e.g., EAN not shown).
- `MISMATCH` = different variant/size/capacity, different product, or pack/unit count materially different with no way to reconcile.
- `UNABLE TO VERIFY` = cannot find one side / blocked / captcha.

## Pack / RSU Handling (critical)
- If Amazon is a multipack and supplier is single: compute `RSU = Amazon units / Supplier units` (round up if needed).
- If supplier pack > Amazon pack: mark as `SPLIT CANDIDATE` and do not assume it is workable; note what would be required operationally.

## Output: Verification Report Template (repeat per product, then summary)
Use this template for each product, then a final summary table.

```markdown
## Product #[Rank]: [SupplierTitle]
**Input Verdict (from report):** [HIGHLY LIKELY / HIGHLY LIKELY - AUDITED OUT / NEEDS VERIFICATION]
**Supplier EAN:** [value or -]  | **Amazon EAN:** [value or -]  | **ASIN:** [value]

### Supplier (efghousewares.co.uk)
- Search used: [EAN or Title]
- Found: [Yes/No]
- Product page URL: [url]
- Title (as shown): [...]
- Brand: [...]
- Pack/unit count: [...]
- Variant: [size/scent/color/etc]
- EAN/GTIN shown on page: [...]
- Price: [...]

### Amazon (amazon.co.uk)
- Search used: [EAN or ASIN]
- Found: [Yes/No]
- Product page URL: https://www.amazon.co.uk/dp/[ASIN]
- Title (as shown): [...]
- Brand: [...]
- Unit-count / pack size: [...]
- Variant selected: [...]
- EAN/GTIN shown in Product details: [...]
- Price: [...]

### Result
- Match Status: [CONFIRMED MATCH / LIKELY MATCH / MISMATCH / UNABLE TO VERIFY]
- Pack Verdict: [1:1 / Multipack / Split Candidate / Unknown]
- RSU (if applicable): [...]
- Key evidence (2-4 bullets):
  - [...]
- Recommendation: [PROMOTE / KEEP / MOVE TO AUDITED OUT / MARK UNRELATED]
```

## Worklist (highest priority first)
Full queue CSV (all candidates, ranked): `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX final\BROWSER_AGENT_QUEUE_EFG_AMZ_RELAXEDHL_20260111_093245.csv`
Overlaps excluded (already being verified by running agent): `C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\CODEX final\BROWSER_AGENT_QUEUE_OVERLAPS_WITH_RUNNING_AGENT_20260111_093245.csv`

### Top Priority Slice (first 150 from queue)
| # | Verdict | SupplierTitle | Supplier EAN | Amazon EAN | ASIN | Sales | NetProfit | Adjusted Profit | Pack Verdict | Filter Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | NEEDS VERIFICATION | AMTECH RECHARGEABLE WORK LIGHT WITH MAGNETIC STAND 3W | 5032759051380 | - | B0FGJ9JGSB | 100 | £32.02 | £32.02 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 2 | NEEDS VERIFICATION | IMPERIAL DEEP DINNER PLATE BLUE 10" | 8694169938513 | 745606660523 | B07SG6C3BR | 50 | £23.61 | £21.70 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 3 | NEEDS VERIFICATION | PORCELAIN MUG 12OZ COLOURED | 742288768073 | - | B0FN3TVZVL | 300 | £14.86 | £11.14 | Pack mismatch 1→6.00 (need 6 units) | Confirm brand/pack/variant (1–2 details) |
| 4 | NEEDS VERIFICATION | FISHING ROD EXTENDABLE WITH FLOAT AND HOOKS | 5033849985301 | - | B01N6WDNN8 | 50 | £18.18 | £18.18 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 5 | NEEDS VERIFICATION | OVEN DISH STONEWARE 4 ASSORTED 90ML | 8721037370288 | 5056075652052 | B074TJP5M3 | 300 | £12.32 | £12.32 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 6 | NEEDS VERIFICATION | TRIPLY CASSEROLE STAINLESS STEEL 20CM | 8906106597876 | 5060913008826 | B0FDL5S7FC | 50 | £20.85 | £20.85 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 7 | NEEDS VERIFICATION | BBQ TURNER WITH WOOD HANDLE 43CM | 5015302420499 | 785691190925 | B0B7KWWNFD | 600 | £10.54 | £10.54 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 8 | NEEDS VERIFICATION | GRIMALDI LA BELLA CASSEROLE POT WITH LID 24CM | 5060923590717 | 5060913000158 | B09KHJM848 | 900 | £14.04 | £14.04 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 9 | HIGHLY LIKELY | CHRISTMAS CRACKER 8 X 12.5" PREMIUM GOLD FOLIAGE | 5015302170172 | 4897097960630 | B0BCHSG3LN | 100 | £6.31 | £10.72 | Split candidate (0.52) | - |
| 10 | NEEDS VERIFICATION | THL 4 TIER VEGETABLE RACK ASSORTED | 8697722501834 | 605660957369 | B0936QF6C5 | 50 | £15.88 | £15.88 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 11 | NEEDS VERIFICATION | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | 8007815259359 | 5054061262513 | B07F446GQD | 50 | £7.66 | £18.02 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 12 | NEEDS VERIFICATION | GRIMALDI MAXISTONE FRYING PAN 28CM | 5060748076878 | - | B0FL27L2T8 | 100 | £16.30 | £16.30 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 13 | NEEDS VERIFICATION | APOLLO CANDY THERMOMETER | 5026180093552 | 4897099884620 | B0CSJTFLBW | 100 | £12.57 | £12.57 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 14 | HIGHLY LIKELY | CHRISTMAS CRACKER 10 X 12" SANTA AND FRIENDS | 5015302170288 | - | B0DDCFRKB4 | 500 | £3.37 | £7.77 | Split candidate (0.05) | - |
| 15 | HIGHLY LIKELY | HOBBY GRAND STORAGE BOX & LID 0.5LTR | 8694064017993 | - | B01M7V2PYL | 100 | £5.73 | £5.73 | 1:1 Match | - |
| 16 | NEEDS VERIFICATION | EXTRASTAR SOLAR SMART STRING LIGHT 15 CANDLE 6M WITH REMOTE | 8435730660361 | - | B0CDXCTQP1 | 100 | £16.07 | £16.07 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 17 | NEEDS VERIFICATION | Water Dispenser for dogs | 5060226063598 | - | B06ZZC83MG | 100 | £12.12 | £10.65 | Pack mismatch 1→2.00 (need 2 units) | Verify unit-count/pack on Amazon listing |
| 18 | HIGHLY LIKELY | SILVER METALLIC MAILERS PK3 120X215MM SIZE B | 5061024360230 | 5061007791051 | B0CKRWZHRN | 50 | £5.92 | £5.92 | 1:1 (3x1 vs 100x1) | - |
| 19 | NEEDS VERIFICATION | AIR STORM SLING SHOT WITH 4 BALLS ASSORTED | 5012866012962 | - | B0FL7SG5TG | 500 | £9.92 | £9.92 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 20 | NEEDS VERIFICATION | CHEF AID SANTOKU KNIFE SOFT GRIP HANDLE | 5012904112753 | - | B0D5HN7W14 | 200 | £12.05 | £12.05 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 21 | NEEDS VERIFICATION | TERRACOTTA HALF POT 20CM | 5021346493092 | - | B0FFHJKPF5 | 50 | £13.00 | £10.91 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 22 | NEEDS VERIFICATION | PAN AROMA COLOUR TEALIGHTS PURE COTTON PACK OF 12 | 5053249265216 | - | B08HZ9GZ6K | 50 | £10.48 | £10.15 | Pack mismatch 1→1.25 (need 2 units) | Verify product identity/variant/pack on Amazon listing |
| 23 | NEEDS VERIFICATION | SUPER FAST CLOTHES AND SHIRT LAUNDRY FOLDER | 5060345240085 | - | B077MKGHXN | 500 | £7.37 | £7.37 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 24 | NEEDS VERIFICATION | EOTIA FOOD CHOPPER 400ML | 6923456815483 | 5025301315504 | B0FMHLFTYX | 50 | £11.38 | £11.38 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 25 | NEEDS VERIFICATION | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | 8694064013285 | 5029784903364 | B0933MHLG6 | 400 | £9.98 | £9.98 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 26 | NEEDS VERIFICATION | REXONA ROLL ON INVISIBLE PURE WOMEN 50ML PK6 | 8717644322451 | 810159161138 | B0DQ5GDC7R | 50 | £8.42 | £14.90 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 27 | NEEDS VERIFICATION | ARENA GLASS TUMBLERS 360ML 3PCE | 8964000624418 | 612508278739 | B07P9G321R | 50 | £11.01 | £9.44 | Pack mismatch 1→2.00 (need 2 units) | EAN conflict — verify barcode/variant/pack |
| 28 | NEEDS VERIFICATION | ADIDAS DEODORANT PURE GAME MENS 150ML PK6 | 3607345711782 | 7432509764764 | B07DCXX17M | 50 | £4.01 | £14.75 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 29 | NEEDS VERIFICATION | CANDLE FACTORY SPIRAL CANDLE 2 IN GIFT BOX ** | 5050565207524 | 886767808215 | B0DPCNV6LK | 50 | £8.80 | £8.80 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 30 | NEEDS VERIFICATION | PPS PLASTIC 4 CONTAINERS & LID RECT 650ML | 50304811930217 | 5060659231885 | B0BTZDR9GD | 300 | £5.99 | £6.49 | Split candidate (0.25) | EAN conflict — verify barcode/variant/pack |
| 31 | NEEDS VERIFICATION | BRIGHT & HOMELY SAUCEPAN NON STICK COOKWARE SET 6PCS | 5050796010283 | - | B0FCBVZXPB | 50 | £18.61 | £10.78 | Pack mismatch 1→1.83 (need 2 units) | Verify unit-count/pack on Amazon listing |
| 32 | NEEDS VERIFICATION | GRIMALDI LA BELLA SAUCE PAN WITH LID 20CM | 5060923590700 | - | B0DM82JXB8 | 100 | £11.23 | £11.23 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 33 | NEEDS VERIFICATION | PPS PLASTIC 5 CONTAINERS & LID ROUND 650ML | 5030481930232 | 5060659231885 | B0BTZDR9GD | 300 | £5.92 | £6.52 | Split candidate (0.20) | EAN conflict — verify barcode/variant/pack |
| 34 | NEEDS VERIFICATION | WOODEN ANIMAL PUZZLE | 5012866658719 | 194735295890 | B0DLH93L1J | 50 | £8.52 | £8.52 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 35 | NEEDS VERIFICATION | CAROLINE 5 PLASTIC TUBS W/LIDS 650ML | 5012145000710 | - | B0BTZDR9GD | 300 | £6.72 | £6.72 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 36 | NEEDS VERIFICATION | ALUMINIUM FRYING PAN 26CM | 742288762521 | 3168430325869 | B09K82CDFB | 400 | £9.26 | £9.26 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 37 | HIGHLY LIKELY | TEA TOWELS TERRY 3 PACK ASSORTED | 5026705064579 | 727266768184 | B0798S43LM | 800 | £1.10 | £0.59 | Pack mismatch 1→1.33 (need 2 units) | - |
| 38 | HIGHLY LIKELY | TIDYZ BIN LINER BLACK 10 BAGS 50LTR | 5025364002052 | 8800202193607 | B07B656W3B | 700 | £1.23 | £0.48 | Pack mismatch 1→2.00 (need 2 units) | - |
| 39 | NEEDS VERIFICATION | WICKED STATIONERY BACKPACK | 5015934923276 | 5056814619636 | B0FKH5GWYL | 400 | £7.72 | £7.72 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 40 | NEEDS VERIFICATION | BLOCK TECH 50 BRICKS AND FIGURE | 5015934639801 | - | B0FY6CSD9Q | 100 | £6.82 | £6.82 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 41 | HIGHLY LIKELY | SQUARE CONTAINER 500ML | 5050565759573 | - | B0F9Y9J3XV | 50 | £5.37 | £1.27 | Pack mismatch 1→4.00 (need 4 units) | Confirm brand/pack/variant (1–2 details) |
| 42 | HIGHLY LIKELY | BACOFOIL ZIPPER BAGS ALL PURPOSE 12 PACK 1L (PM £2.19) | 5023139862917 | - | B08FBJ59DR | 500 | £2.93 | £0.09 | Pack mismatch 1→3.75 (need 4 units) | confirm unit-count math (“3 x … (45 bags)”) and size equivalence (“1L” vs “Small”). |
| 43 | NEEDS VERIFICATION | CHRISTMAS PIPE CLEANERS 40PC | 5056170340526 | - | B0CLCBL6DT | 100 | £5.67 | £6.26 | Split candidate (0.03) | Verify split/repack feasibility + unit-count |
| 44 | NEEDS VERIFICATION | MASTER COOK DIE CAST CASSEROLE 24CM | 6945702110326 | 5057982093273 | B0BT51TC8X | 50 | £11.26 | £11.26 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 45 | NEEDS VERIFICATION | BLOCK TECH MINI BUILDZ ASSORTED | 5015934804230 | - | B0FY6CSD9Q | 100 | £6.78 | £6.78 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 46 | HIGHLY LIKELY | CAR PRIDE CAR VENT AIR FRESHENER VANILLA COCOA 4ML PACK OF 2 | 5053249281827 | - | B0DRNZ7P94 | 100 | £4.18 | £1.44 | Pack mismatch 1→3.00 (need 3 units) | - |
| 47 | HIGHLY LIKELY | ALL PURPOSE CLEANING PET WIPES 40 PACK | - | - | B08LML3X1N | 200 | £2.15 | £1.71 | Pack mismatch 1→1.50 (need 2 units) | - |
| 48 | HIGHLY LIKELY | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 1.1L | 5010303186269 | - | B0DCGHNZQS | 200 | £2.36 | £2.36 | 1:1 Match | - |
| 49 | NEEDS VERIFICATION | GREENFIELDS 20CM PLANT POT | 5014348229004 | - | B0DJ38DJ6D | 50 | £7.59 | £5.71 | Pack mismatch 1→3.00 (need 3 units) | Verify unit-count/pack on Amazon listing |
| 50 | NEEDS VERIFICATION | GRIMALDI MAXISTONE WOK 28CM | 5060748076922 | 5060659231212 | B08WH6TVYL | 500 | £8.09 | £8.09 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 51 | NEEDS VERIFICATION | INCENSE STICKS SACRED WOOD PACK OF 12 | 5024418660859 | - | B0CN2XTXX1 | 900 | £1.51 | £6.68 | Split candidate (0.08) | Verify split/repack feasibility + unit-count |
| 52 | HIGHLY LIKELY | STORAGE BASKET 25X15X12CM | 5024418520788 | 5060414800899 | B0CRM6PJGQ | 50 | £1.31 | £3.06 | Split candidate (0.00) | - |
| 53 | NEEDS VERIFICATION | BOWL GLASS FLOWER 15CM 4 ASSORTED COLOURS | 8721037513562 | - | B094QZQXS4 | 50 | £9.39 | £5.40 | Pack mismatch 1→4.00 (need 4 units) | Verify unit-count/pack on Amazon listing |
| 54 | NEEDS VERIFICATION | BLACKSPUR WINDOW INSULATION KIT | 5017403135388 | - | B0FCBVT881 | 300 | £5.94 | £5.94 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 55 | NEEDS VERIFICATION | BLUE CANYON FLATLINE TOWEL BAR 60CM | 5056295710518 | 737879468401 | B0DHYTRRLV | 300 | £9.05 | £9.05 | 1:1 Match | Verify product identity/variant/pack on Amazon listing |
| 56 | HIGHLY LIKELY | BRIGHT & HOMELY TEALIGHT CANDLES 30 PACK 5 HOUR BURN TIME | 5050796010023 | - | B0DPXJL1B9 | 50 | £4.84 | £0.92 | Pack mismatch 1→3.33 (need 4 units) | - |
| 57 | NEEDS VERIFICATION | FIRST STEPS BABY BOTTLE JUNGLE ASSORTED | 5015302105495 | 4008600367994 | B088S8BXN9 | 300 | £5.63 | £5.63 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 58 | HIGHLY LIKELY | GEL TOE PROTECTORS | 5060345207798 | - | B09JLTP2ZY | 700 | £0.05 | £0.05 | 1:1 Match | - |
| 59 | NEEDS VERIFICATION | PET PLAY & SNUFFLE BLANKET 40X40CM | 5052516213073 | - | B0DNJYVCG7 | 900 | £2.00 | £6.03 | Split candidate (0.00) | Verify split/repack feasibility + unit-count |
| 60 | NEEDS VERIFICATION | FIRST STEPS BABY BOTTLE SAFARI ASSORTED | 5015302105488 | 4008600405535 | B09BD2D4VW | 300 | £5.56 | £5.56 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 61 | NEEDS VERIFICATION | Cat Lead & Harness | 5060226010059 | - | B0C8JDVRRF | 50 | £6.02 | £6.02 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 62 | HIGHLY LIKELY | AMTECH PADLOCK BRASS 20MM | 5032759006113 | - | B007UIJIW6 | 50 | £1.99 | £1.99 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 63 | HIGHLY LIKELY | ALBERTO BALSAM SHAMPOO TEA TREE 350ML PK6 | 8710908183812 | - | B0126CHB24 | 50 | £2.76 | £2.76 | 1:1 (6x1 vs 6x1) | Confirm brand/pack/variant (1–2 details) |
| 64 | NEEDS VERIFICATION | PAINT YOUR OWN FRENCHIE AND SAUSAGE DOG | 5015934835593 | - | B0DCYQBDP6 | 600 | £5.80 | £5.80 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 65 | HIGHLY LIKELY | HAPPY BIRTHDAY BANNER | 5060082940637 | - | B0D59HCW1X | 600 | £0.15 | £0.15 | 1:1 Match | - |
| 66 | NEEDS VERIFICATION | DENIM FACE WASH CAHRCOAL DETOX 100ML PK6 | 18717278898176 | 850010101309 | B07XVJR8W7 | 800 | £2.70 | £6.05 | Split candidate (0.17) | EAN conflict — verify barcode/variant/pack |
| 67 | NEEDS VERIFICATION | GL DECORATE YOUR OWN TRINKET BOX | 5015934770986 | 4897078491399 | B0C4FK3Y5S | 900 | £4.33 | £4.33 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 68 | HIGHLY LIKELY | BAMBOO BATH TOWELS SILVER 70x120CM PACK OF 2 | 5051346799535 | 6972403931424 | B08D38T3JW | 300 | £1.44 | £1.44 | 1:1 (2x1 vs 2x1) | - |
| 69 | NEEDS VERIFICATION | THL BOWL PLASTIC REUSABLE 12OZ 20PCS | 8681873025066 | - | B0FPG5XMWV | 50 | £5.85 | £5.64 | Pack mismatch 1→1.25 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 70 | HIGHLY LIKELY | DRAPER SPANNER SET METRIC COMBINATION | 5010559684793 | 5010559684816 | B0114IPMS6 | 100 | £2.15 | £2.15 | 1:1 Match | strong title match, but BOTH EANs present and different => default NV. |
| 71 | NEEDS VERIFICATION | ECO WISE PAPER CUPS LIDS 12OZ PK25 | 5060743590881 | - | B07M7FF42H | 50 | £6.10 | £5.25 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 72 | HIGHLY LIKELY | SCENTED PET BUBBLE WANDS 2 PACK | 5052516313780 | 5056657508678 | B0C1HG192H | 200 | £1.50 | £0.84 | Pack mismatch 1→1.50 (need 2 units) | - |
| 73 | NEEDS VERIFICATION | IMPERIAL GLASS FLUTE 200ML 3 PACK | 8964044321045 | 5057982099916 | B0CH135XNH | 100 | £7.35 | £6.63 | Pack mismatch 1→1.33 (need 2 units) | EAN conflict — verify barcode/variant/pack |
| 74 | NEEDS VERIFICATION | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM | 5010853281667 | 5010853271866 | B08KJGYJNK | 100 | £7.96 | £7.96 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 75 | HIGHLY LIKELY | EVERBUILD ONE STRIKE FILLER 250ML | 5029347300029 | - | B001326TJA | 500 | £0.15 | £0.15 | 1:1 Match | - |
| 76 | NEEDS VERIFICATION | MENS HANKIES IN COUNTER DISPLAY BROWN BOX 100% COTTON WHITE PACK OF 3 | 5059004016277 | 5060668180303 | B0DJ1MVT97 | 600 | £4.01 | £5.25 | Split candidate (0.33) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 77 | NEEDS VERIFICATION | EMPIRE FRYING PAN INDUCTION 26CM | 8903138075037 | 3168430325869 | B09K82CDFB | 300 | £7.64 | £7.64 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 78 | HIGHLY LIKELY | AMTECH TROWEL MARGIN - SOFT GRIP5X2 | 5032759038138 | 5032759027644 | B00ABJQTPU | 50 | £0.35 | £2.16 | Split candidate (0.10) | - |
| 79 | NEEDS VERIFICATION | APOLLO KITCHEN TIMERS | 5026180050197 | - | B0DGH36J1F | 900 | £3.82 | £3.82 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 80 | HIGHLY LIKELY | BLUE CANYON ROUND WALL MIRROR WHITE | 5060386422662 | - | B01CMHNDKC | 50 | £1.93 | £1.93 | 1:1 Match | - |
| 81 | HIGHLY LIKELY | BEAUFORT MEASURE ULTIMATE JUG 3LTR | 5014348292350 | - | B008ES6SLU | 50 | £1.25 | £1.25 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 82 | NEEDS VERIFICATION | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ | 5060357992767 | 5060357992422 | B0DKD8V7F6 | 100 | £5.64 | £4.84 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 83 | HIGHLY LIKELY | GARDEN KNEELING PAD 40CM | 5024418546085 | - | B08YX52F4T | 100 | £1.36 | £0.69 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 84 | NEEDS VERIFICATION | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | 5060357992750 | 5060357992415 | B07MZ2Z9GL | 100 | £5.30 | £4.63 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 85 | NEEDS VERIFICATION | SIL TOILET ROLL HOLDER STAINLESS STEEL | 5024418537410 | - | B09377NPKH | 600 | £3.97 | £3.97 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 86 | HIGHLY LIKELY | CHEF AID PASTRY BRUSH 3 IN 1 CARDED | 5012904013777 | 5012904088409 | B008CY80YY | 400 | £0.16 | £0.16 | 1:1 Match | “3 in 1” could be bundle/contents difference + EAN conflict. |
| 87 | NEEDS VERIFICATION | Dog Figure '8' Knot Ball Rope Toy(12/48) | 5060226032587 | 729792886936 | B0725XC6BS | 800 | £3.24 | £3.24 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 88 | HIGHLY LIKELY - AUDITED OUT | EVERBUILD BITUMEN TROWEL MASTIC 1 LITRE | 5029347009311 | - | B0070U64RG | 50 | £5.34 | - | Variant mismatch (format/size) | Different pack/format (1L vs 6kg) |
| 89 | HIGHLY LIKELY | BIN BRITE STICK ON OUTDOOR BIN FRESHENER WITH CITRONELLA PACK OF 2 | 5053249270890 | 5020042027075 | B0BVLTKB3W | 300 | £0.45 | £0.45 | 1:1 (2x1 vs 2x1) | - |
| 90 | NEEDS VERIFICATION | LADIES TRAINER 3 SOCKS WITH ARCH SUPPORT AND MESH PASTEL PACK OF 4 | 5059004013405 | - | B0DRVQ6ZQD | 300 | £3.97 | £7.12 | Split candidate (0.25) | Verify split/repack feasibility + unit-count |
| 91 | NEEDS VERIFICATION | LADIES TRAINER 3 SOCKS WITH ARCH SUPPORT AND MESH TOP WHITE PACK OF 4 | 5020133112727 | - | B0DRVQ6ZQD | 300 | £3.97 | £7.12 | Split candidate (0.25) | Verify split/repack feasibility + unit-count |
| 92 | NEEDS VERIFICATION | ASHLEY PEVA DRESS BAG 60 X 120CM | 5017403099918 | - | B0DT6NY7VW | 100 | £6.32 | £6.32 | 1:1 (1x1 vs 12x1) | Confirm brand/pack/variant (1–2 details) |
| 93 | HIGHLY LIKELY | BIN BRITE STICK ON BIN FRESHENER ASSORTED PACK OF 2 | 5053249270975 | 5020042027075 | B0BVLTKB3W | 200 | £0.65 | £0.65 | 1:1 (2x1 vs 2x1) | - |
| 94 | HIGHLY LIKELY | AMTECH SHARPENING STONE 2000 | 5032759001675 | - | B004TRT3K8 | 50 | £1.02 | £1.02 | 1:1 Match | verify grit/format (“2000”) matches Amazon “E2300 … 300mm cigar stone”. |
| 95 | NEEDS VERIFICATION | DRESS UP CHILD FAIRY WINGS | 5026619372548 | 6425496666907 | B07KG16PJ2 | 100 | £5.92 | £5.92 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 96 | NEEDS VERIFICATION | NY COFFEE 3IN1 12PC 170G | 5900649084339 | 5060980497837 | B0FYQXKFGS | 50 | £5.04 | £6.66 | Split candidate (0.08) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 97 | HIGHLY LIKELY | TALA MEAT THERMOMETER 4106 | 5012904041060 | - | B000SABZOM | 50 | £1.31 | £1.31 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 98 | HIGHLY LIKELY | ADDIS CLIP TIGHT RECTANGLE FOOD BOX 550ML | 5010303185965 | - | B0DCGDS6Y5 | 300 | £0.24 | £0.24 | 1:1 Match | - |
| 99 | HIGHLY LIKELY | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS | 5010303194424 | 5010303180588 | B0BYKDX25N | 50 | £0.42 | £1.23 | Split candidate (0.33) | - |
| 100 | HIGHLY LIKELY | PYREX AIR FRYER SQUARE DISH 20X17CM | 3426470301268 | - | B0DN1HXF9B | 50 | £1.04 | £1.04 | 1:1 Match (20x17cm are dimensions) | - |
| 101 | HIGHLY LIKELY | ROLSON PLASTERING TROWEL 280X115MM | 5029594522380 | 5029594522458 | B006A7D1O4 | 100 | £0.74 | £0.74 | 1:1 Match | strong title+size match, but BOTH EANs present and different => default NV. |
| 102 | HIGHLY LIKELY | KILNER BOTTLE SQUARE 1LTR | 5010853253428 | - | B07VC8TFB8 | 50 | £0.91 | £0.91 | 1:1 Match | - |
| 103 | HIGHLY LIKELY | APOLLO WOODEN DISH STAND | 5026180050005 | - | B0095RXTHA | 50 | £0.88 | £0.88 | 1:1 Match (40x34x4 are dimensions) | - |
| 104 | NEEDS VERIFICATION | PUZZLE FARM 45PCE | 5015934701034 | - | B09SVJQ49Q | 100 | £4.24 | £5.14 | Split candidate (0.02) | Verify split/repack feasibility + unit-count |
| 105 | HIGHLY LIKELY | FALCON ENAMEL ROUND PIE DISH 26CM | 5012823030916 | - | B07NNY768K | 50 | £0.89 | £0.89 | 1:1 Match | - |
| 106 | NEEDS VERIFICATION | FESTIVE MAGIC SANT SLEIGH FELT BUCKET | 9333527629203 | - | B0DM9FNQ9R | 300 | £4.84 | £4.84 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 107 | NEEDS VERIFICATION | ECO WISE PAPER CUPS LIDS 8OZ PK25 | 5060743590874 | 5060659230154 | B07XLNJDY9 | 800 | £2.19 | £3.01 | Split candidate (0.04) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 108 | HIGHLY LIKELY | COLGATE TOOTHPASTE FRESH GEL 100ML PK12 | 8714789436098 | - | B00X67O3NY | 100 | £0.68 | £0.68 | 1:1 Match | - |
| 109 | HIGHLY LIKELY | AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP | 5032759027644 | - | B00ABJQTPU | 50 | £0.63 | £0.63 | 1:1 Match | - |
| 110 | HIGHLY LIKELY | MASON CASH MUG 450ML CREAM | 5010853236766 | 5010853244365 | B01N4QV65Y | 100 | £0.47 | £0.47 | 1:1 Match | - |
| 111 | NEEDS VERIFICATION | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6PCS | 5060743591604 | 5060659230154 | B07XLNJDY9 | 800 | £2.19 | £2.90 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 112 | NEEDS VERIFICATION | LAUNDRY BASKET TALL | 6291101152840 | - | B0DG4Y9R97 | 500 | £5.00 | £5.00 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 113 | NEEDS VERIFICATION | SECURPLUMB COMPRESSION ELBOW 10X10MM | 5019923196337 | - | B0CM3WKZ97 | 50 | £4.39 | £5.71 | Split candidate (0.01) | Verify split/repack feasibility + unit-count |
| 114 | NEEDS VERIFICATION | SILVER METALLIC MAILERS PK3 180X265MM SIZE D | 5061024360179 | 5061007790856 | B0CKLXPPMX | 50 | £5.24 | £5.24 | 1:1 (3x1 vs 100x1) | Verify product identity/variant/pack on Amazon listing |
| 115 | HIGHLY LIKELY | FARM TRACTOR AND TRAILER SET | 5012866019213 | - | B0BMW4T2T7 | 200 | £0.05 | £0.05 | 1:1 Match | - |
| 116 | HIGHLY LIKELY | STATUS 3WAY BASIC C/FREE SOCKET WHT 1PK CLAM | 5022822194984 | 5022822207776 | B08CVK7746 | 200 | £0.04 | £0.04 | 1:1 Match | - |
| 117 | NEEDS VERIFICATION | LAV MISKET GIN GLASS 645CC PK3 | 8692952076961 | 5056057686778 | B082YH5WZB | 100 | £4.21 | £6.97 | Split candidate (0.33) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 118 | HIGHLY LIKELY | CHEF AID FLUTED CAKE RING | 5012904106219 | - | B084DT8RNB | 200 | £0.01 | £0.01 | 1:1 Match | - |
| 119 | HIGHLY LIKELY | KILNER PRESERVE JAR 0.25LTR SCREW LID | 5010853173566 | - | B007MO0FIO | 50 | £0.40 | £0.40 | 1:1 Match | - |
| 120 | HIGHLY LIKELY | SISTEMA TO GO BREAKFAST BOX | 9414202213556 | - | B005HNXFJS | 100 | £0.18 | £0.18 | 1:1 Match | - |
| 121 | HIGHLY LIKELY | DOVE STICK 40ML ORIGINAL WOMEN PK6 | 5000228975901 | - | B00LNC810U | 100 | £0.16 | £0.16 | 1:1 (6x1 vs 6x1) | Confirm brand/pack/variant (1–2 details) |
| 122 | NEEDS VERIFICATION | CHRISTMAS DIFFUSERS GINGERBREAD 30ML SET OF 3 | 5024418634232 | - | B0D97LYYDY | 900 | £0.82 | £3.46 | Split candidate (0.33) | Verify split/repack feasibility + unit-count |
| 123 | NEEDS VERIFICATION | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | 5060357990077 | 5060357990107 | B0DJDH23JW | 700 | £3.28 | £3.28 | 1:1 (1x10 vs 10x1) | EAN mismatch (verify which barcode/variant applies) |
| 124 | HIGHLY LIKELY | WHITE GLO TOOTHPASTE PROFESSIONAL CHOICE 100ML PK6 | 29319871000619 | - | B0122ZMXYQ | 50 | £0.33 | £0.33 | 1:1 (6x1 vs 6x1) | Confirm brand/pack/variant (1–2 details) |
| 125 | NEEDS VERIFICATION | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | 5060605732022 | 5019041167141 | B07F8VJHWF | 100 | £6.45 | £6.45 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 126 | NEEDS VERIFICATION | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE | 5012904112029 | - | B06Y1L9G65 | 400 | £4.40 | £4.40 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 127 | NEEDS VERIFICATION | APOLLO STAINLESS STEEL BREAD KNIFE | 5026180053938 | 6953087007568 | B0D83Z7HYQ | 200 | £4.75 | £4.75 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 128 | NEEDS VERIFICATION | KETTLE FLOWER GLASS 1800ML | 6985412547883 | 810019871610 | B0B15K9Y5F | 200 | £5.90 | £5.90 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 129 | NEEDS VERIFICATION | GROSVENOR 55CM TROUGH BLACK | 5014348297157 | - | B0723GK5V9 | 50 | £5.93 | £5.93 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 130 | NEEDS VERIFICATION | CHRISTMAS GIFT BAG X LARGE 3PC FUN CHARACTER | 5015934919279 | - | B0CDQH4DHQ | 700 | £6.93 | £-0.96 | Pack mismatch 1→10.00 (need 10 units) | Verify unit-count/pack on Amazon listing; If pack assumption holds, becomes AUDITED OUT (AdjProfit<=0) |
| 131 | HIGHLY LIKELY | HARRIS PUTTY KNIFE | 5056287402902 | - | B0815B7FBY | 50 | £0.13 | £0.13 | 1:1 Match | - |
| 132 | NEEDS VERIFICATION | VASE GLASS CYLINDER 20X10X10CM | 5055141626904 | - | B09MTP248R | 200 | £5.68 | £5.68 | 1:1 (20x10 vs 20x10) | Verify product identity/variant on Amazon listing |
| 133 | NEEDS VERIFICATION | BLOCK TECH ASTRONAUGHT | 5015934804544 | - | B0F677FLKK | 300 | £4.92 | £4.92 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 134 | HIGHLY LIKELY - AUDITED OUT | ROUNDUP PATH WEEDKILLER RTU 1LTR 20% FREE | 5017676016919 | 5017676016964 | B01MYBH3SU | 50 | £3.52 | - | Variant mismatch (1L vs 5L) | Different size (1L vs 5L) => different SKU |
| 135 | HIGHLY LIKELY | FAIRY MAX POWER SOAP DISPENSING DISH BRUSH | 5010303194387 | 5010303180588 | B0BYKDX25N | 50 | £0.06 | £0.06 | 1:1 Match | bundle/contents ambiguity. |
| 136 | HIGHLY LIKELY | ROLSON CHALK LINE AND LAYOUT SET 3PCE | 5029594525374 | - | B000QFCQ6U | 50 | £0.02 | £0.02 | 1:1 Match (3pc vs 3pc) | - |
| 137 | HIGHLY LIKELY | ROYAL MARKET PLASTIC PINT 50 GLASSES | 5010326063745 | - | B0CGKRQGM4 | 50 | £0.01 | £0.01 | 1:1 (1x50 vs 50x1) | - |
| 138 | NEEDS VERIFICATION | LAGHMANIS OUD 100ML FOR HER GOLD EACH | 5055170283031 | 5060919410012 | B097QC3CH6 | 100 | £4.74 | £4.74 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 139 | NEEDS VERIFICATION | ASHLEY SUCTION SOAP DISH | 5017403119524 | - | B07J5GHTY6 | 400 | £3.28 | £3.28 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 140 | NEEDS VERIFICATION | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | 5060357992170 | - | B07GZGXQYG | 200 | £5.00 | £5.00 | 1:1 (1x5 vs 5x1) | Verify product identity/variant on Amazon listing |
| 141 | NEEDS VERIFICATION | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | 5060357990060 | 5060357990107 | B0DJDH23JW | 700 | £3.00 | £3.00 | 1:1 (1x10 vs 10x1) | EAN mismatch (verify which barcode/variant applies) |
| 142 | NEEDS VERIFICATION | SILVER METALLIC MAILERS PK3 230X340MM SIZE F | 5061024360247 | 5061007790856 | B0CKLXPPMX | 50 | £4.90 | £4.90 | 1:1 (3x1 vs 100x1) | Verify product identity/variant/pack on Amazon listing |
| 143 | NEEDS VERIFICATION | DINOSAUR PLASTIC DRINKING BOTTLE 500ML ASSORTED | 5050565421586 | 619098088793 | B0BS6VWFK5 | 100 | £4.59 | £4.59 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 144 | NEEDS VERIFICATION | CHRISTMAS WOODEN TREE SHAPES 12PK | 5056170340786 | 650728196198 | B07XR9RQHG | 50 | £4.07 | £4.07 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 145 | NEEDS VERIFICATION | SOFT FOOTBALL IN CDU 10CM 3 ASSORTED | 5012866061687 | 5060947842878 | B0FTSFB34M | 200 | £4.06 | £4.06 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 146 | NEEDS VERIFICATION | PPS PLASTIC DRINK SHOT 30 GLASSES 30ML | 5030481960178 | 5060659230123 | B07T68VD2Y | 300 | £2.84 | £3.56 | Split candidate (0.03) | EAN conflict — verify barcode/variant/pack |
| 147 | NEEDS VERIFICATION | WORLD OF PETS DOG COLLAR CLASSIC SMALL | 5015302203962 | 6902210335238 | B075D4XNFV | 300 | £3.29 | £3.29 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 148 | HIGHLY LIKELY - AUDITED OUT | TIDYZ WHEELY BIN LINERS 5 BAGS 300L | 5025364005824 | 5025762919174 | B07MGLHMWY | 500 | £2.77 | £-0.93 | Pack mismatch: supplier 5 bags vs Amazon 30 bags (RSU=6) | RSU=6 makes Adjusted Profit <= 0 |
| 149 | NEEDS VERIFICATION | FIRST STEPS WIND UP BATH TOY | 5015302106324 | - | B08ZHNDFDD | 600 | £2.62 | £2.62 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 150 | NEEDS VERIFICATION | CANDLE PILLAR CANDLE GLITTER GOLD 7X7.5M | 5024418433538 | 8717847150677 | B0B8D1MP1X | 200 | £3.17 | £4.83 | Split candidate (0.08) | Verify product identity/variant/pack on Amazon listing |

### Needs Verification: High-Opportunity Subset (for quick wins)
| # | Verdict | SupplierTitle | Supplier EAN | Amazon EAN | ASIN | Sales | NetProfit | Adjusted Profit | Pack Verdict | Filter Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | NEEDS VERIFICATION | AMTECH RECHARGEABLE WORK LIGHT WITH MAGNETIC STAND 3W | 5032759051380 | - | B0FGJ9JGSB | 100 | £32.02 | £32.02 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 2 | NEEDS VERIFICATION | IMPERIAL DEEP DINNER PLATE BLUE 10" | 8694169938513 | 745606660523 | B07SG6C3BR | 50 | £23.61 | £21.70 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 3 | NEEDS VERIFICATION | PORCELAIN MUG 12OZ COLOURED | 742288768073 | - | B0FN3TVZVL | 300 | £14.86 | £11.14 | Pack mismatch 1→6.00 (need 6 units) | Confirm brand/pack/variant (1–2 details) |
| 4 | NEEDS VERIFICATION | FISHING ROD EXTENDABLE WITH FLOAT AND HOOKS | 5033849985301 | - | B01N6WDNN8 | 50 | £18.18 | £18.18 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 5 | NEEDS VERIFICATION | OVEN DISH STONEWARE 4 ASSORTED 90ML | 8721037370288 | 5056075652052 | B074TJP5M3 | 300 | £12.32 | £12.32 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 6 | NEEDS VERIFICATION | TRIPLY CASSEROLE STAINLESS STEEL 20CM | 8906106597876 | 5060913008826 | B0FDL5S7FC | 50 | £20.85 | £20.85 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 7 | NEEDS VERIFICATION | BBQ TURNER WITH WOOD HANDLE 43CM | 5015302420499 | 785691190925 | B0B7KWWNFD | 600 | £10.54 | £10.54 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 8 | NEEDS VERIFICATION | GRIMALDI LA BELLA CASSEROLE POT WITH LID 24CM | 5060923590717 | 5060913000158 | B09KHJM848 | 900 | £14.04 | £14.04 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 9 | NEEDS VERIFICATION | THL 4 TIER VEGETABLE RACK ASSORTED | 8697722501834 | 605660957369 | B0936QF6C5 | 50 | £15.88 | £15.88 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 10 | NEEDS VERIFICATION | RCR MELODIA BICCHIERI TUMBLER 24CL 6PC | 8007815259359 | 5054061262513 | B07F446GQD | 50 | £7.66 | £18.02 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 11 | NEEDS VERIFICATION | GRIMALDI MAXISTONE FRYING PAN 28CM | 5060748076878 | - | B0FL27L2T8 | 100 | £16.30 | £16.30 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 12 | NEEDS VERIFICATION | APOLLO CANDY THERMOMETER | 5026180093552 | 4897099884620 | B0CSJTFLBW | 100 | £12.57 | £12.57 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 13 | NEEDS VERIFICATION | EXTRASTAR SOLAR SMART STRING LIGHT 15 CANDLE 6M WITH REMOTE | 8435730660361 | - | B0CDXCTQP1 | 100 | £16.07 | £16.07 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 14 | NEEDS VERIFICATION | Water Dispenser for dogs | 5060226063598 | - | B06ZZC83MG | 100 | £12.12 | £10.65 | Pack mismatch 1→2.00 (need 2 units) | Verify unit-count/pack on Amazon listing |
| 15 | NEEDS VERIFICATION | AIR STORM SLING SHOT WITH 4 BALLS ASSORTED | 5012866012962 | - | B0FL7SG5TG | 500 | £9.92 | £9.92 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 16 | NEEDS VERIFICATION | CHEF AID SANTOKU KNIFE SOFT GRIP HANDLE | 5012904112753 | - | B0D5HN7W14 | 200 | £12.05 | £12.05 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 17 | NEEDS VERIFICATION | TERRACOTTA HALF POT 20CM | 5021346493092 | - | B0FFHJKPF5 | 50 | £13.00 | £10.91 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 18 | NEEDS VERIFICATION | PAN AROMA COLOUR TEALIGHTS PURE COTTON PACK OF 12 | 5053249265216 | - | B08HZ9GZ6K | 50 | £10.48 | £10.15 | Pack mismatch 1→1.25 (need 2 units) | Verify product identity/variant/pack on Amazon listing |
| 19 | NEEDS VERIFICATION | SUPER FAST CLOTHES AND SHIRT LAUNDRY FOLDER | 5060345240085 | - | B077MKGHXN | 500 | £7.37 | £7.37 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 20 | NEEDS VERIFICATION | EOTIA FOOD CHOPPER 400ML | 6923456815483 | 5025301315504 | B0FMHLFTYX | 50 | £11.38 | £11.38 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 21 | NEEDS VERIFICATION | HOBBY FLORIA LACE PRACTICAL BASKET MEDIUM | 8694064013285 | 5029784903364 | B0933MHLG6 | 400 | £9.98 | £9.98 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 22 | NEEDS VERIFICATION | REXONA ROLL ON INVISIBLE PURE WOMEN 50ML PK6 | 8717644322451 | 810159161138 | B0DQ5GDC7R | 50 | £8.42 | £14.90 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 23 | NEEDS VERIFICATION | ARENA GLASS TUMBLERS 360ML 3PCE | 8964000624418 | 612508278739 | B07P9G321R | 50 | £11.01 | £9.44 | Pack mismatch 1→2.00 (need 2 units) | EAN conflict — verify barcode/variant/pack |
| 24 | NEEDS VERIFICATION | ADIDAS DEODORANT PURE GAME MENS 150ML PK6 | 3607345711782 | 7432509764764 | B07DCXX17M | 50 | £4.01 | £14.75 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 25 | NEEDS VERIFICATION | CANDLE FACTORY SPIRAL CANDLE 2 IN GIFT BOX ** | 5050565207524 | 886767808215 | B0DPCNV6LK | 50 | £8.80 | £8.80 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 26 | NEEDS VERIFICATION | PPS PLASTIC 4 CONTAINERS & LID RECT 650ML | 50304811930217 | 5060659231885 | B0BTZDR9GD | 300 | £5.99 | £6.49 | Split candidate (0.25) | EAN conflict — verify barcode/variant/pack |
| 27 | NEEDS VERIFICATION | BRIGHT & HOMELY SAUCEPAN NON STICK COOKWARE SET 6PCS | 5050796010283 | - | B0FCBVZXPB | 50 | £18.61 | £10.78 | Pack mismatch 1→1.83 (need 2 units) | Verify unit-count/pack on Amazon listing |
| 28 | NEEDS VERIFICATION | GRIMALDI LA BELLA SAUCE PAN WITH LID 20CM | 5060923590700 | - | B0DM82JXB8 | 100 | £11.23 | £11.23 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 29 | NEEDS VERIFICATION | PPS PLASTIC 5 CONTAINERS & LID ROUND 650ML | 5030481930232 | 5060659231885 | B0BTZDR9GD | 300 | £5.92 | £6.52 | Split candidate (0.20) | EAN conflict — verify barcode/variant/pack |
| 30 | NEEDS VERIFICATION | WOODEN ANIMAL PUZZLE | 5012866658719 | 194735295890 | B0DLH93L1J | 50 | £8.52 | £8.52 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 31 | NEEDS VERIFICATION | CAROLINE 5 PLASTIC TUBS W/LIDS 650ML | 5012145000710 | - | B0BTZDR9GD | 300 | £6.72 | £6.72 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 32 | NEEDS VERIFICATION | ALUMINIUM FRYING PAN 26CM | 742288762521 | 3168430325869 | B09K82CDFB | 400 | £9.26 | £9.26 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 33 | NEEDS VERIFICATION | WICKED STATIONERY BACKPACK | 5015934923276 | 5056814619636 | B0FKH5GWYL | 400 | £7.72 | £7.72 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 34 | NEEDS VERIFICATION | BLOCK TECH 50 BRICKS AND FIGURE | 5015934639801 | - | B0FY6CSD9Q | 100 | £6.82 | £6.82 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 35 | NEEDS VERIFICATION | CHRISTMAS PIPE CLEANERS 40PC | 5056170340526 | - | B0CLCBL6DT | 100 | £5.67 | £6.26 | Split candidate (0.03) | Verify split/repack feasibility + unit-count |
| 36 | NEEDS VERIFICATION | MASTER COOK DIE CAST CASSEROLE 24CM | 6945702110326 | 5057982093273 | B0BT51TC8X | 50 | £11.26 | £11.26 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 37 | NEEDS VERIFICATION | BLOCK TECH MINI BUILDZ ASSORTED | 5015934804230 | - | B0FY6CSD9Q | 100 | £6.78 | £6.78 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 38 | NEEDS VERIFICATION | GREENFIELDS 20CM PLANT POT | 5014348229004 | - | B0DJ38DJ6D | 50 | £7.59 | £5.71 | Pack mismatch 1→3.00 (need 3 units) | Verify unit-count/pack on Amazon listing |
| 39 | NEEDS VERIFICATION | GRIMALDI MAXISTONE WOK 28CM | 5060748076922 | 5060659231212 | B08WH6TVYL | 500 | £8.09 | £8.09 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 40 | NEEDS VERIFICATION | INCENSE STICKS SACRED WOOD PACK OF 12 | 5024418660859 | - | B0CN2XTXX1 | 900 | £1.51 | £6.68 | Split candidate (0.08) | Verify split/repack feasibility + unit-count |
| 41 | NEEDS VERIFICATION | BOWL GLASS FLOWER 15CM 4 ASSORTED COLOURS | 8721037513562 | - | B094QZQXS4 | 50 | £9.39 | £5.40 | Pack mismatch 1→4.00 (need 4 units) | Verify unit-count/pack on Amazon listing |
| 42 | NEEDS VERIFICATION | BLACKSPUR WINDOW INSULATION KIT | 5017403135388 | - | B0FCBVT881 | 300 | £5.94 | £5.94 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 43 | NEEDS VERIFICATION | BLUE CANYON FLATLINE TOWEL BAR 60CM | 5056295710518 | 737879468401 | B0DHYTRRLV | 300 | £9.05 | £9.05 | 1:1 Match | Verify product identity/variant/pack on Amazon listing |
| 44 | NEEDS VERIFICATION | FIRST STEPS BABY BOTTLE JUNGLE ASSORTED | 5015302105495 | 4008600367994 | B088S8BXN9 | 300 | £5.63 | £5.63 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 45 | NEEDS VERIFICATION | PET PLAY & SNUFFLE BLANKET 40X40CM | 5052516213073 | - | B0DNJYVCG7 | 900 | £2.00 | £6.03 | Split candidate (0.00) | Verify split/repack feasibility + unit-count |
| 46 | NEEDS VERIFICATION | FIRST STEPS BABY BOTTLE SAFARI ASSORTED | 5015302105488 | 4008600405535 | B09BD2D4VW | 300 | £5.56 | £5.56 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 47 | NEEDS VERIFICATION | Cat Lead & Harness | 5060226010059 | - | B0C8JDVRRF | 50 | £6.02 | £6.02 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 48 | NEEDS VERIFICATION | PAINT YOUR OWN FRENCHIE AND SAUSAGE DOG | 5015934835593 | - | B0DCYQBDP6 | 600 | £5.80 | £5.80 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 49 | NEEDS VERIFICATION | DENIM FACE WASH CAHRCOAL DETOX 100ML PK6 | 18717278898176 | 850010101309 | B07XVJR8W7 | 800 | £2.70 | £6.05 | Split candidate (0.17) | EAN conflict — verify barcode/variant/pack |
| 50 | NEEDS VERIFICATION | GL DECORATE YOUR OWN TRINKET BOX | 5015934770986 | 4897078491399 | B0C4FK3Y5S | 900 | £4.33 | £4.33 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 51 | NEEDS VERIFICATION | THL BOWL PLASTIC REUSABLE 12OZ 20PCS | 8681873025066 | - | B0FPG5XMWV | 50 | £5.85 | £5.64 | Pack mismatch 1→1.25 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 52 | NEEDS VERIFICATION | ECO WISE PAPER CUPS LIDS 12OZ PK25 | 5060743590881 | - | B07M7FF42H | 50 | £6.10 | £5.25 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 53 | NEEDS VERIFICATION | IMPERIAL GLASS FLUTE 200ML 3 PACK | 8964044321045 | 5057982099916 | B0CH135XNH | 100 | £7.35 | £6.63 | Pack mismatch 1→1.33 (need 2 units) | EAN conflict — verify barcode/variant/pack |
| 54 | NEEDS VERIFICATION | MASON CASH MIXING BOWL IN THE MEADOW DAFFODIL 21CM | 5010853281667 | 5010853271866 | B08KJGYJNK | 100 | £7.96 | £7.96 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 55 | NEEDS VERIFICATION | MENS HANKIES IN COUNTER DISPLAY BROWN BOX 100% COTTON WHITE PACK OF 3 | 5059004016277 | 5060668180303 | B0DJ1MVT97 | 600 | £4.01 | £5.25 | Split candidate (0.33) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 56 | NEEDS VERIFICATION | EMPIRE FRYING PAN INDUCTION 26CM | 8903138075037 | 3168430325869 | B09K82CDFB | 300 | £7.64 | £7.64 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 57 | NEEDS VERIFICATION | APOLLO KITCHEN TIMERS | 5026180050197 | - | B0DGH36J1F | 900 | £3.82 | £3.82 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 58 | NEEDS VERIFICATION | SUPERIOR ROUND 10 CONTAINER & LID 4 OZ | 5060357992767 | 5060357992422 | B0DKD8V7F6 | 100 | £5.64 | £4.84 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 59 | NEEDS VERIFICATION | SUPERIOR ROUND 10 CONTAINER & LID 2 OZ | 5060357992750 | 5060357992415 | B07MZ2Z9GL | 100 | £5.30 | £4.63 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 60 | NEEDS VERIFICATION | SIL TOILET ROLL HOLDER STAINLESS STEEL | 5024418537410 | - | B09377NPKH | 600 | £3.97 | £3.97 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 61 | NEEDS VERIFICATION | Dog Figure '8' Knot Ball Rope Toy(12/48) | 5060226032587 | 729792886936 | B0725XC6BS | 800 | £3.24 | £3.24 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 62 | NEEDS VERIFICATION | LADIES TRAINER 3 SOCKS WITH ARCH SUPPORT AND MESH PASTEL PACK OF 4 | 5059004013405 | - | B0DRVQ6ZQD | 300 | £3.97 | £7.12 | Split candidate (0.25) | Verify split/repack feasibility + unit-count |
| 63 | NEEDS VERIFICATION | LADIES TRAINER 3 SOCKS WITH ARCH SUPPORT AND MESH TOP WHITE PACK OF 4 | 5020133112727 | - | B0DRVQ6ZQD | 300 | £3.97 | £7.12 | Split candidate (0.25) | Verify split/repack feasibility + unit-count |
| 64 | NEEDS VERIFICATION | ASHLEY PEVA DRESS BAG 60 X 120CM | 5017403099918 | - | B0DT6NY7VW | 100 | £6.32 | £6.32 | 1:1 (1x1 vs 12x1) | Confirm brand/pack/variant (1–2 details) |
| 65 | NEEDS VERIFICATION | DRESS UP CHILD FAIRY WINGS | 5026619372548 | 6425496666907 | B07KG16PJ2 | 100 | £5.92 | £5.92 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 66 | NEEDS VERIFICATION | NY COFFEE 3IN1 12PC 170G | 5900649084339 | 5060980497837 | B0FYQXKFGS | 50 | £5.04 | £6.66 | Split candidate (0.08) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 67 | NEEDS VERIFICATION | PUZZLE FARM 45PCE | 5015934701034 | - | B09SVJQ49Q | 100 | £4.24 | £5.14 | Split candidate (0.02) | Verify split/repack feasibility + unit-count |
| 68 | NEEDS VERIFICATION | FESTIVE MAGIC SANT SLEIGH FELT BUCKET | 9333527629203 | - | B0DM9FNQ9R | 300 | £4.84 | £4.84 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 69 | NEEDS VERIFICATION | ECO WISE PAPER CUPS LIDS 8OZ PK25 | 5060743590874 | 5060659230154 | B07XLNJDY9 | 800 | £2.19 | £3.01 | Split candidate (0.04) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 70 | NEEDS VERIFICATION | ECO WISE PAPER CUPS RIPPLE DOTTED12OZ 6PCS | 5060743591604 | 5060659230154 | B07XLNJDY9 | 800 | £2.19 | £2.90 | Split candidate (0.17) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 71 | NEEDS VERIFICATION | LAUNDRY BASKET TALL | 6291101152840 | - | B0DG4Y9R97 | 500 | £5.00 | £5.00 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 72 | NEEDS VERIFICATION | SECURPLUMB COMPRESSION ELBOW 10X10MM | 5019923196337 | - | B0CM3WKZ97 | 50 | £4.39 | £5.71 | Split candidate (0.01) | Verify split/repack feasibility + unit-count |
| 73 | NEEDS VERIFICATION | SILVER METALLIC MAILERS PK3 180X265MM SIZE D | 5061024360179 | 5061007790856 | B0CKLXPPMX | 50 | £5.24 | £5.24 | 1:1 (3x1 vs 100x1) | Verify product identity/variant/pack on Amazon listing |
| 74 | NEEDS VERIFICATION | LAV MISKET GIN GLASS 645CC PK3 | 8692952076961 | 5056057686778 | B082YH5WZB | 100 | £4.21 | £6.97 | Split candidate (0.33) | EAN mismatch (verify which barcode/variant applies); Verify split/repack feasibility + unit-count |
| 75 | NEEDS VERIFICATION | CHRISTMAS DIFFUSERS GINGERBREAD 30ML SET OF 3 | 5024418634232 | - | B0D97LYYDY | 900 | £0.82 | £3.46 | Split candidate (0.33) | Verify split/repack feasibility + unit-count |
| 76 | NEEDS VERIFICATION | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | 5060357990077 | 5060357990107 | B0DJDH23JW | 700 | £3.28 | £3.28 | 1:1 (1x10 vs 10x1) | EAN mismatch (verify which barcode/variant applies) |
| 77 | NEEDS VERIFICATION | MENS WATERPROOF FLEECE TRAPPER HAT WITH MASK BLACK | 5060605732022 | 5019041167141 | B07F8VJHWF | 100 | £6.45 | £6.45 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 78 | NEEDS VERIFICATION | CHEF AID KNIFE SHARPENER SOFTGRIP HANDLE | 5012904112029 | - | B06Y1L9G65 | 400 | £4.40 | £4.40 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 79 | NEEDS VERIFICATION | APOLLO STAINLESS STEEL BREAD KNIFE | 5026180053938 | 6953087007568 | B0D83Z7HYQ | 200 | £4.75 | £4.75 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 80 | NEEDS VERIFICATION | KETTLE FLOWER GLASS 1800ML | 6985412547883 | 810019871610 | B0B15K9Y5F | 200 | £5.90 | £5.90 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 81 | NEEDS VERIFICATION | GROSVENOR 55CM TROUGH BLACK | 5014348297157 | - | B0723GK5V9 | 50 | £5.93 | £5.93 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 82 | NEEDS VERIFICATION | CHRISTMAS GIFT BAG X LARGE 3PC FUN CHARACTER | 5015934919279 | - | B0CDQH4DHQ | 700 | £6.93 | £-0.96 | Pack mismatch 1→10.00 (need 10 units) | Verify unit-count/pack on Amazon listing; If pack assumption holds, becomes AUDITED OUT (AdjProfit<=0) |
| 83 | NEEDS VERIFICATION | VASE GLASS CYLINDER 20X10X10CM | 5055141626904 | - | B09MTP248R | 200 | £5.68 | £5.68 | 1:1 (20x10 vs 20x10) | Verify product identity/variant on Amazon listing |
| 84 | NEEDS VERIFICATION | BLOCK TECH ASTRONAUGHT | 5015934804544 | - | B0F677FLKK | 300 | £4.92 | £4.92 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 85 | NEEDS VERIFICATION | LAGHMANIS OUD 100ML FOR HER GOLD EACH | 5055170283031 | 5060919410012 | B097QC3CH6 | 100 | £4.74 | £4.74 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 86 | NEEDS VERIFICATION | ASHLEY SUCTION SOAP DISH | 5017403119524 | - | B07J5GHTY6 | 400 | £3.28 | £3.28 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 87 | NEEDS VERIFICATION | SUPERIOR FOIL 5 CONTAINERS & LID 2400ML | 5060357992170 | - | B07GZGXQYG | 200 | £5.00 | £5.00 | 1:1 (1x5 vs 5x1) | Verify product identity/variant on Amazon listing |
| 88 | NEEDS VERIFICATION | SUPERIOR FOIL 10 CONTAINERS & LID 1 LTR | 5060357990060 | 5060357990107 | B0DJDH23JW | 700 | £3.00 | £3.00 | 1:1 (1x10 vs 10x1) | EAN mismatch (verify which barcode/variant applies) |
| 89 | NEEDS VERIFICATION | SILVER METALLIC MAILERS PK3 230X340MM SIZE F | 5061024360247 | 5061007790856 | B0CKLXPPMX | 50 | £4.90 | £4.90 | 1:1 (3x1 vs 100x1) | Verify product identity/variant/pack on Amazon listing |
| 90 | NEEDS VERIFICATION | DINOSAUR PLASTIC DRINKING BOTTLE 500ML ASSORTED | 5050565421586 | 619098088793 | B0BS6VWFK5 | 100 | £4.59 | £4.59 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 91 | NEEDS VERIFICATION | CHRISTMAS WOODEN TREE SHAPES 12PK | 5056170340786 | 650728196198 | B07XR9RQHG | 50 | £4.07 | £4.07 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 92 | NEEDS VERIFICATION | SOFT FOOTBALL IN CDU 10CM 3 ASSORTED | 5012866061687 | 5060947842878 | B0FTSFB34M | 200 | £4.06 | £4.06 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 93 | NEEDS VERIFICATION | PPS PLASTIC DRINK SHOT 30 GLASSES 30ML | 5030481960178 | 5060659230123 | B07T68VD2Y | 300 | £2.84 | £3.56 | Split candidate (0.03) | EAN conflict — verify barcode/variant/pack |
| 94 | NEEDS VERIFICATION | WORLD OF PETS DOG COLLAR CLASSIC SMALL | 5015302203962 | 6902210335238 | B075D4XNFV | 300 | £3.29 | £3.29 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 95 | NEEDS VERIFICATION | FIRST STEPS WIND UP BATH TOY | 5015302106324 | - | B08ZHNDFDD | 600 | £2.62 | £2.62 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 96 | NEEDS VERIFICATION | CANDLE PILLAR CANDLE GLITTER GOLD 7X7.5M | 5024418433538 | 8717847150677 | B0B8D1MP1X | 200 | £3.17 | £4.83 | Split candidate (0.08) | Verify product identity/variant/pack on Amazon listing |
| 97 | NEEDS VERIFICATION | INDOOR & OUTDOOR DOORMAT 60CM X 90CM | 6991934168086 | - | B0DCP6NBYX | 100 | £5.58 | £5.58 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 98 | NEEDS VERIFICATION | EUROWRAP NAVY OMBRE PERFUME BAG PK6 | 5033601104438 | - | B0BW8RZWRF | 100 | £3.09 | £5.78 | Split candidate (0.17) | Verify product identity/variant/pack on Amazon listing |
| 99 | NEEDS VERIFICATION | FOIL PLATTERS LARGE PK2 | 5056239412201 | - | B0D3NZVMNQ | 700 | £1.91 | £2.60 | Split candidate (0.50) | Verify split/repack feasibility + unit-count |
| 100 | NEEDS VERIFICATION | CRAFT PAINT 200ML NEON | 5056170314992 | - | B071KL5K2C | 200 | £3.77 | £3.77 | 1:1 Match | Confirm brand/pack/variant (1–2 details) |
| 101 | NEEDS VERIFICATION | EXTRASTAR LED FLASHLIGHT BATTERY TORCH | 8432011550380 | - | B09YCKKWHZ | 100 | £4.50 | £4.50 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 102 | NEEDS VERIFICATION | EXTRASTAR LED FLASHLIGHT TORCH | 5060577579977 | - | B09YCKKWHZ | 100 | £4.50 | £4.50 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 103 | NEEDS VERIFICATION | FAST FOOD PLAY SET | 5012866311256 | 703363804352 | B07KWRZG3W | 800 | £1.95 | £1.95 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 104 | NEEDS VERIFICATION | PUZZLE UNICORN KINGDOM 45PCE | 5015934709320 | - | B0CWHHNG9P | 200 | £2.60 | £4.90 | Split candidate (0.02) | Verify split/repack feasibility + unit-count |
| 105 | NEEDS VERIFICATION | DOOR MAT COIR WELCOME HEART 40 X 60CM | 5017403154600 | - | B0FJ6698SB | 100 | £2.41 | £5.70 | Split candidate (0.00) | Verify split/repack feasibility + unit-count |
| 106 | NEEDS VERIFICATION | PRIMA STAINLESS STEEL PEELER SWIVEL | 5038673131511 | 719812052175 | B09BW19KZ9 | 100 | £3.86 | £3.86 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 107 | NEEDS VERIFICATION | SPECIAL OCCASIONS RAINBOW COLOUR HAIR SPRAY 200ML | 5055319512060 | 5056558637415 | B0CV12HTJ9 | 100 | £3.94 | £3.94 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 108 | NEEDS VERIFICATION | SECURPLUMB PS STOP ENDS 15MM | 5019923196283 | 5065022550105 | B0FCXZNPQC | 100 | £3.34 | £3.34 | 1:1 Match | EAN conflict — verify barcode/variant/pack |
| 109 | NEEDS VERIFICATION | CRYSTALS WITH FRAGRANCE 30G | 5024418538127 | 735810454254 | B079T9RH57 | 100 | £3.56 | £3.56 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 110 | NEEDS VERIFICATION | DOOR MAT COIR HOME SWEET HOME 40 X 60CM | 5017403154617 | - | B0FJ65M42D | 50 | £2.44 | £5.73 | Split candidate (0.00) | Verify split/repack feasibility + unit-count |
| 111 | NEEDS VERIFICATION | BABY PIPKIN CLASSIC ROUND BABY BOTTLE 5oz | 5055706660466 | 072239328477 | B0CHWHM4BX | 100 | £3.92 | £3.07 | Pack mismatch 1→2.00 (need 2 units) | EAN mismatch (verify which barcode/variant applies); Verify unit-count/pack on Amazon listing |
| 112 | NEEDS VERIFICATION | BLUE CANYON FOLDABLE BAMBOO LAUNDRY HAMPER BLACK | 5056295710525 | 8710755232725 | B0CKTKRC86 | 50 | £5.76 | £5.76 | 1:1 Match | EAN mismatch (verify which barcode/variant applies) |
| 113 | NEEDS VERIFICATION | FRAMED ART - TOTTENHAM HOTSPUR F.C KITS 40CM X 40CM | 5060899568178 | - | B0FZCN5J5F | 50 | £5.96 | £5.96 | 1:1 (1x1 vs 46x34) | Verify product identity/variant on Amazon listing |
| 114 | NEEDS VERIFICATION | SPACE GUN ASSORTED | 5012866069331 | - | B09KS3Q55Q | 50 | £5.19 | £5.19 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 115 | NEEDS VERIFICATION | HOBBY UNICORN 32INCH ASSORTED | 5050788080881 | - | B0DHW3Z4CJ | 200 | £4.82 | £4.82 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 116 | NEEDS VERIFICATION | RSW NON-STICK PIZZA TRAY 33CM | 5015302478421 | - | B07DQNZT2D | 400 | £3.70 | £2.36 | Pack mismatch 1→2.00 (need 2 units) | Confirm brand/pack/variant (1–2 details) |
| 117 | NEEDS VERIFICATION | FOIL PLATTER LARGE | 5056239412195 | - | B0D3NZVMNQ | 700 | £1.91 | £1.91 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 118 | NEEDS VERIFICATION | FASHION DOLL IN BOX | 5033849075781 | - | B0D4DH28QS | 50 | £3.91 | £3.91 | 1:1 Match | Verify product identity/variant on Amazon listing |
| 119 | NEEDS VERIFICATION | PPS MICRO 6 ROUND CONTAINER+LIDS 300ML | 5030481930331 | - | B0DPFV1FXJ | 200 | £4.91 | £1.19 | Pack mismatch 1→6.00 (need 6 units) | Confirm brand/pack/variant (1–2 details) |
| 120 | NEEDS VERIFICATION | BLOCK TECH POLICE FORCE 254 PCES | 5015934804599 | - | B0F677FLKK | 300 | £3.95 | £3.95 | 1:1 Match | Verify product identity/variant on Amazon listing |

## Stop Condition
- Work down the queue in rank order. If time-limited, complete all HIGHLY LIKELY first, then NV by rank.