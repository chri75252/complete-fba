# Browser Agent Product Verification Prompt

## TASK OVERVIEW
You are a product verification agent tasked with verifying whether supplier products match their corresponding Amazon listings. You will visit both the supplier website and Amazon.co.uk to confirm product matches.

---

## WEBSITES TO USE

### Supplier Website
**URL:** https://www.efghousewares.co.uk/
**Search Method:** 
- PRIMARY: Use EAN/barcode to search
- FALLBACK: If EAN is "N/A", "-", or not found, use the product title

### Amazon Website  
**URL:** https://www.amazon.co.uk/
**Search Method:**
- PRIMARY: Use EAN/barcode to search
- FALLBACK: If EAN is "N/A" or "-", navigate directly using: `https://www.amazon.co.uk/dp/{ASIN}`

---

## VERIFICATION WORKFLOW

### For EACH product entry:

**STEP 1: Identify the Supplier Product**
1. Go to https://www.efghousewares.co.uk/
2. Use the search function to search for the **Supplier EAN** (e.g., "5055170251023")
3. If EAN search returns no results or EAN is "N/A"/"-", search using the **SupplierTitle**
4. Record the product found:
   - Product name/title
   - Price (if visible)
   - Pack size/quantity
   - Key specifications (size, weight, color, variant)
   - Image description (briefly describe what the product looks like)

**STEP 2: Identify the Amazon Product**
1. Go to https://www.amazon.co.uk/
2. If **Amazon EAN** exists and is not "-", search for that EAN
3. If Amazon EAN is "-" or not found, navigate directly to: `https://www.amazon.co.uk/dp/{ASIN}`
4. Record the Amazon listing details:
   - Product title
   - Price
   - Pack size/quantity  
   - Key specifications
   - Sold by / Brand
   - Image description

**STEP 3: Compare and Determine Match Status**
Evaluate the match based on:

| Criteria | Match Score |
|----------|-------------|
| Same brand name | +30 |
| Same product type | +25 |
| Same pack size/quantity | +20 |
| Same size/dimensions (if applicable) | +15 |
| Same variant/color/scent | +10 |
| Visual similarity | +10 |

**Match Status Determination:**
- **CONFIRMED MATCH** (Score ≥ 80): Products are clearly the same
- **LIKELY MATCH** (Score 50-79): Products appear similar but have minor differences
- **DIFFERENT PRODUCT** (Score < 50): Products are not the same
- **UNABLE TO VERIFY** (Cannot access one/both products): Record issue

**STEP 4: Document Pack Ratio**
If products match but pack sizes differ:
- Record Supplier pack size
- Record Amazon pack size
- Calculate RSU (Required Supplier Units) = Amazon pack ÷ Supplier pack

---

## PRODUCTS TO VERIFY

### Priority 1: High-Value Needs Verification (verify first)

| # | SupplierTitle | SupplierEAN | AmazonEAN | ASIN | Notes |
|---|---------------|-------------|-----------|------|-------|
| 1 | LONDON FRAGRANCES FOR HIM POMEGRANATE NOIR 100ML | 5055170251023 | 9787426969180 | 7426969185 | EAN conflict - verify brand |
| 2 | QUEST EXPRESSO COFFEE MACHINE WITH MILK FROTHER | 5025301365790 | - | B0B3F548G7 | Verify Quest brand match |
| 3 | EVERBUILD SEALANT STRIPOUT TOOL | 5029347603557 | - | B00IZMVQOO | Verify Everbuild brand |
| 4 | WORLD OF PETS CAT LITTER SCENTED 3LT | 5052516216876 | - | B009S64OI6 | Verify product identity |
| 5 | DRAPER RETRACTABLE KNIFE SET | 5010559086955 | 814744020022 | B01L8Q3J5M | EAN conflict - verify |
| 6 | ORNATE EDT 100ML POUR HOMME EACH | 5055170260117 | - | B001PTFWG2 | High profit - verify brand |
| 7 | EXTRA SELECT PREMIUM RABBIT FOOD BUCKET 5L | 5022245000282 | - | B07DLSHF4Z | Verify Extra Select brand |
| 8 | RUSSELL HOBBS VIENNA CUTLERY SET 16PC | 5054061297706 | - | B07C8V2DJ7 | Verify Russell Hobbs |
| 9 | QUEST TURBO BLENDER 2 IN 1 32129 | 5025301321291 | - | B0DQYT5F9Z | Verify Quest brand |
| 10 | SOUDAL EXPANDING FOAM HANDHELD 750ML | 5411183078956 | - | B07STZLCM6 | Verify Soudal brand + 750ml |

### Priority 2: Brand Match Verification

| # | SupplierTitle | SupplierEAN | AmazonEAN | ASIN | Notes |
|---|---------------|-------------|-----------|------|-------|
| 11 | KILROCK DAMP CLEAR MOULD REMOVER 500ML | 5014353093294 | - | B0791ZQMMZ | Verify Kilrock brand |
| 12 | MASON CASH MIXING BOWL OWL STONE 26CM | 5010853197838 | 5010853271859 | B08KJB12RQ | EAN conflict |
| 13 | SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2 | 4001836065665 | 5023041541245 | B073XQYNQT | Verify brand |
| 14 | LAV FAME WINE GLASS 40CL PK3 | 8692952100840 | 5055512159437 | B087RLGF1Y | Verify LAV brand |
| 15 | BLUE CANYON LED VANITY MIRROR 17CM | 5056295702346 | - | B007IGLU12 | Verify Blue Canyon |
| 16 | AMTECH DRAIN CLEANER | 5032759005833 | - | B01LYX9RRV | Verify Amtech brand |
| 17 | AMTECH VICE BABY | 5032759001408 | - | B007L5V48Y | Verify Amtech brand |
| 18 | AMTECH PICK-UP TOOL TELE MAG 5LB | 5032759010035 | - | B00HMDJD38 | Verify Amtech brand |
| 19 | GIFTMAKER PENGUIN SANTA SACK | 5012128584411 | - | B09HCS9QM2 | Verify Giftmaker brand |
| 20 | BEAUFORT SQ FOOD CONTAINER 13 LTR | 5014348241525 | - | B0046MHRMM | Verify Beaufort brand |

### Priority 3: Pack/Quantity Verification

| # | SupplierTitle | SupplierEAN | AmazonEAN | ASIN | Notes |
|---|---------------|-------------|-----------|------|-------|
| 21 | RYSONS CLOTHES HANGER TROUSERS 3 BAR | 5056239423184 | - | B001INKFV2 | Verify 3-pack vs single |
| 22 | PADDED ENVELOPES SIZE E PK3 | 5056239403346 | - | B0017KKJLM | Verify pack size |
| 23 | PADDED ENVELOPES SIZE G 240X340MM PK10 | 5039306005711 | 3316843997368 | B015UJDMFK | Verify pack size |
| 24 | PUZZLE FAIRY 45PCE | 5015934701171 | - | B007R482V6 | Verify piece count |
| 25 | PUZZLE PIRATE | 5015934700969 | - | B007ST0MCM | Verify piece count |

### Priority 4: EAN Conflict Resolution

| # | SupplierTitle | SupplierEAN | AmazonEAN | ASIN | Notes |
|---|---------------|-------------|-----------|------|-------|
| 26 | YALE ESSENTIALS DEADLOCK P/BRASS 64MM | 5011802242111 | 5010608056250 | B000TAUFFG | Different EANs - verify same product |
| 27 | SABICHI STAINLESS STEEL 16CM SAUCEPAN | - | 5010763003274 | B00022BNVG | No supplier EAN |
| 28 | BLACKMOOR SAUCEPAN WITH LID 18CM | 5025301698294 | 5010763071327 | B000VE9WG8 | EAN conflict |
| 29 | SABICHI STAINLESS STEEL 18CM SAUCEPAN | 5021961093745 | 5010763071327 | B000VE9WG8 | EAN conflict |
| 30 | STAINLESS STEEL KETTLE 14CM 1L | 6974295210014 | 5055322509507 | B00KLGPNUK | EAN conflict |
| 31 | BIKE SADDLE COVER CUSHIONED | 5017403096191 | 714953981896 | B01H4OL8QE | EAN conflict |
| 32 | ROLSON CLAW HAMMER FIBREGLASS 8OZ | 5029594103718 | 5029594112017 | B00JITHXRM | Different EANs |
| 33 | ROYALFORD STAINLESS STEEL PESTLE AND MORTAR | 6294016436500 | 685450202350 | B00XMKCAXK | EAN conflict |
| 34 | ROLSON DIAGONAL CUTTING PLIERS VDE 160MM | 5029594210768 | 4045315131601 | B013URC1GU | EAN conflict |
| 35 | LONDON MUG 10CM | 6923456816312 | 5055071655654 | B008EXEVG4 | EAN conflict |

### Priority 5: General Verification (Sample)

| # | SupplierTitle | SupplierEAN | AmazonEAN | ASIN | Notes |
|---|---------------|-------------|-----------|------|-------|
| 36 | PAN AROMA CANDLE RND JUICY BERRIES | 5053249217680 | - | B004RPZG8U | Verify Pan Aroma |
| 37 | SQUEAKY FOX DOG TOY | 5056283844614 | - | B00R19BNMC | Verify product |
| 38 | SPICE IT UP SEASALT GRINDER | 5055257877078 | - | B00GLAHZUG | Verify brand |
| 39 | SPICE IT UP CHILLI FLAKES SEASON GRINDER | 5055257877085 | - | B00X3Z2RQY | Verify brand |
| 40 | FIRST STEPS BABY BLANKET CREAM 70X70CM | 5015302106874 | - | B00EXPGYOE | Size mismatch (70x70 vs 75x100) |
| 41 | BIN & LID 50LTR ASSORTED | 8694313001339 | - | B01DP0PAPG | Verify 50L match |
| 42 | PEPPA PIG GUITAR | 5050838320219 | - | B00BG6MTFG | Verify Peppa Pig license |
| 43 | METAL POLICE HANDCUFFS | 5033849985325 | - | B0826Q2TVQ | Verify product |
| 44 | CERAMIC WAX/OIL BURNER | 5055566999041 | - | B0CKLQ3G62 | Verify product |
| 45 | WOODEN INSECT HOUSE METAL ROOF | 8720573129206 | - | B07FYQJXXC | Verify product |
| 46 | FLEXIBLE GAS LIGHTER | 5056239441034 | 798610262269 | B0FCFHX3F6 | EAN conflict |
| 47 | DEKTON KEYCHAIN COB LIGHT | 5055441450919 | - | B0DWFTT23P | Verify Dekton |
| 48 | DIE CAST TRACTOR | 5050788011915 | - | B08W2K41J2 | Verify product |
| 49 | CITRONELLA GARDEN TORCH ASSORTED | 8711252951201 | - | B092FLZ886 | Verify pack |
| 50 | HAPPY BIRTHDAY TRI CUT BUNTING | 5060082940699 | - | B0C3HJ3WLX | Verify product |

---

## OUTPUT REPORT FORMAT

Generate a verification report in the following format for each product:

```
## Product #[NUMBER]: [SUPPLIER TITLE]

### Supplier Details (efghousewares.co.uk)
- **Search Term Used:** [EAN or Title]
- **Product Found:** [Yes/No]
- **Product Name:** [name from website]
- **Price:** [price if visible]
- **Pack Size:** [quantity]
- **Key Specs:** [size, color, variant, etc.]
- **Image Description:** [brief description]

### Amazon Details (amazon.co.uk)
- **Search Term Used:** [EAN or ASIN]
- **Product Found:** [Yes/No]
- **ASIN:** [ASIN]
- **Product Title:** [full Amazon title]
- **Price:** [current price]
- **Pack Size:** [quantity]
- **Brand:** [brand name]
- **Key Specs:** [size, color, variant]
- **Image Description:** [brief description]

### Verification Result
- **Match Status:** [CONFIRMED MATCH / LIKELY MATCH / DIFFERENT PRODUCT / UNABLE TO VERIFY]
- **Match Score:** [0-100]
- **Brand Match:** [Yes/No/Partial]
- **Pack Size Match:** [Yes/No - if no, state RSU]
- **Size/Variant Match:** [Yes/No]
- **Key Differences:** [list any differences found]
- **Recommendation:** [PROMOTE TO VERIFIED / KEEP AS HIGHLY LIKELY / MOVE TO AUDITED OUT / MARK AS UNRELATED]

---
```

## SUMMARY SECTION

After verifying all products, generate a summary:

```
# VERIFICATION SUMMARY

## Statistics
- Total Products Verified: [X]
- Confirmed Matches: [X]
- Likely Matches: [X]
- Different Products: [X]
- Unable to Verify: [X]

## Category Recommendations

### Promote to VERIFIED (Confirmed Matches)
[List products that should be promoted]

### Keep as HIGHLY LIKELY
[List products with likely matches]

### Move to AUDITED OUT
[List products that don't match or have issues]

### Mark as UNRELATED
[List products that are completely different]

## Common Issues Found
[List recurring issues like EAN conflicts, pack mismatches, etc.]
```

---

## IMPORTANT NOTES

1. **Be thorough** - Take screenshots or detailed notes of each product page
2. **Check pack sizes carefully** - Many mismatches are due to multipack differences
3. **Verify brand names** - Some products may have similar names but different brands
4. **Note any access issues** - If a product page is unavailable, record this
5. **Check for variants** - Colors, sizes, scents may differ
6. **Record prices** - This helps validate profitability calculations
7. **Time limit** - Spend no more than 3-5 minutes per product verification
8. **If the supplier website requires login** - Note this and skip to Amazon verification only
9. **Save your progress** - The report should be saved incrementally

---

## START VERIFICATION

Begin with Priority 1 products (high-value items) and work through the list systematically.

**Output file:** Save the verification report to:
`C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\VERIFICATION_RESULTS_REPORT.md`
