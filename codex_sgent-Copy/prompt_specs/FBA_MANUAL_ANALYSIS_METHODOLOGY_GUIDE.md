# MANUAL FBA PRODUCT ANALYSIS - COMPLETE METHODOLOGY GUIDE

**Version:** v1.1  
**Last Updated:** 2026-01-04  

## Purpose
This guide documents the complete step-by-step methodology for manually analyzing FBA product data to identify profitable arbitrage opportunities. Follow this guide exactly to replicate the analysis process.

---

## TABLE OF CONTENTS

1. [Overview & Inputs](#1-overview--inputs)
2. [Phase 1: Data Extraction & Initial Filtering](#2-phase-1-data-extraction--initial-filtering)
3. [Phase 2: EAN Match Analysis](#3-phase-2-ean-match-analysis)
4. [Phase 3: Title-Based Verification](#4-phase-3-title-based-verification)
5. [Phase 4: Pack Size Detection & Analysis](#5-phase-4-pack-size-detection--analysis)
6. [Phase 5: Browser Verification](#6-phase-5-browser-verification)
7. [Phase 6: Adjusted Profit Calculation](#7-phase-6-adjusted-profit-calculation)
8. [Phase 7: Final Categorization](#8-phase-7-final-categorization)
9. [Phase 8: Report Comparison (Optional)](#9-phase-8-report-comparison-optional)
10. [Decision Trees & Flowcharts](#10-decision-trees--flowcharts)
11. [Common Pitfalls to Avoid](#11-common-pitfalls-to-avoid)
12. [Quick Reference Checklists](#12-quick-reference-checklists)

---

## 1. OVERVIEW & INPUTS

### 1.1 Required Input Files

| File Type | Description | Example |
|:----------|:------------|:--------|
| **Financial Report** | Excel/CSV with supplier products matched to Amazon | `PART3.xlsx` |
| **LLM Reports** (optional) | Pre-analyzed reports from other AI agents | `PHASEA_MANUAL_REPORT_*.md` |

### 1.2 Expected Columns in Financial Report

| Column Name | Description | Required |
|:------------|:------------|:--------:|
| `RowID` | Unique row identifier (or use index+1) | ✅ |
| `ASIN` | Amazon Standard Identification Number | ✅ |
| `EAN` | Supplier product barcode (13 digits typically) | ✅ |
| `EAN_OnPage` | Amazon listing barcode | ✅ |
| `SupplierTitle` | Product title from supplier | ✅ |
| `AmazonTitle` | Product title from Amazon | ✅ |
| `SupplierPrice_incVAT` | Supplier cost including VAT | ✅ |
| `SellingPrice_incVAT` | Amazon selling price | ✅ |
| `NetProfit` | Pre-calculated profit | ✅ |
| `ROI` | Return on Investment percentage | Optional |
| `Sales` | Estimated monthly sales | Optional |

### 1.3 Output Categories

| Category | Definition |
|:---------|:-----------|
| **VERIFIED** | Exact EAN match + pack/size confirmed + profitable |
| **HIGHLY LIKELY** | Strong brand/title match but no EAN confirmation + profitable |
| **NEEDS VERIFICATION** | High potential match with 1-2 blocking details |
| **FILTERED OUT** | **Confirmed match**, but excluded due to pack/variant/profit gates (audit trail) |
| **UNRELATED / NOT INCLUDED** | Not a confirmed match (weak/contradictory evidence); **do not list in report tables** (count only) |

**Critical distinction (do not mix):**
- **UNRELATED / NOT INCLUDED** is the large majority of rows in noisy reports; these are **not** shown in report tables.
- **FILTERED OUT** is reserved for **confirmed matches** that are excluded for specific reasons (e.g., adjusted profit ≤ 0 after pack correction, explicit variant mismatch).

---

## 2. PHASE 1: DATA EXTRACTION & INITIAL FILTERING

### Step 2.0: Coverage & Reconciliation Contract (MANDATORY)

To prevent “missed rows” and silent omissions:

1. **Read every row** in the financial report (RowID 1..N).
2. Assign each row to **exactly one** bucket:
   - VERIFIED / HIGHLY LIKELY / NEEDS VERIFICATION / FILTERED OUT / UNRELATED (NOT INCLUDED)
3. **Do not cap** categories (especially NEEDS VERIFICATION). If output length is an issue, split across multiple outputs/files.
4. End with a reconciliation check:
   - `VERIFIED + HIGHLY LIKELY + NEEDS VERIFICATION + FILTERED OUT + UNRELATED = TOTAL ROWS`
   - No duplicate RowIDs across buckets.

### Step 2.1: Load and Normalize Data

```python
# Pseudocode for data loading
import pandas as pd

df = pd.read_excel('PART3.xlsx')
df['RowID'] = df.index + 1  # Create RowID if not present

# Normalize EAN columns (remove .0 from Excel float conversion)
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()
```

### Step 2.2: Validate EAN Format

A valid barcode for “Exact EAN match” classification must be **strict-valid**:
- Digits-only after cleaning (remove spaces, hyphens, “.0”, etc.)
- Length is a plausible GTIN length: 8 / 12 / 13 / 14
- **Checksum-valid** for its length (where applicable)
- If shorter than 12/13/14, attempt **left-padding** (zero-fill) and re-validate checksum
- Reject suspicious placeholders/corruption (e.g., long trailing-zero runs)

```python
import re

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():  # Excel/scientific notation → treat as corrupted
        return ''
    return re.sub(r'\\D', '', s)

def gtin_checksum_ok(digits: str) -> bool:
    if not digits.isdigit() or len(digits) not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_gtin(digits: str) -> str:
    if not digits.isdigit():
        return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in (12, 13, 14):
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits: str) -> bool:
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_gtin(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):  # suspicious trailing zeros
        return False
    return gtin_checksum_ok(normalized)
```

### Step 2.3: Extract Exact EAN Matches

```python
ean_matches = []
for idx, row in df.iterrows():
    ean1 = normalize_gtin(clean_to_digits(row['EAN_clean']))
    ean2 = normalize_gtin(clean_to_digits(row['EAN_OnPage_clean']))
    if is_strict_valid_barcode(ean1) and is_strict_valid_barcode(ean2) and ean1 == ean2:
        ean_matches.append(row)
```

**Expected Result:** A list of all rows where supplier EAN exactly matches Amazon EAN.

---

## 3. PHASE 2: EAN MATCH ANALYSIS

### Step 3.1: Initial EAN Match ≠ Automatic VERIFIED

> **CRITICAL RULE:** An exact EAN match is necessary but NOT sufficient for VERIFIED status.
> The EAN only confirms the barcode matches. You must still verify:
> 1. Pack sizes match (supplier 1x vs Amazon 10x = NOT a match)
> 2. Product variant matches (size, color, scent)
> 3. Profit is positive after pack adjustment

### Step 3.2: Create EAN Match Working List

For each EAN match, extract:
- RowID, ASIN, EAN
- SupplierTitle (full text)
- AmazonTitle (full text)
- SupplierPrice, SellingPrice, NetProfit
- ROI, Sales

### Step 3.3: Flag Potential Pack Discrepancies

Scan titles for pack indicators:
- Numbers followed by "pack", "pk", "x", "pcs", "pieces"
- Phrases like "Pack of X", "Set of X", "X count"
- **BUT NOT** dimensions like "15cm", "9x9 inch", "280x115mm"

---

## 4. PHASE 3: TITLE-BASED VERIFICATION

### Step 4.1: Parse Supplier Title

For each product, manually read the supplier title and extract:

| Element | What to Look For | Example |
|:--------|:-----------------|:--------|
| **Brand** | First word(s), often in CAPS | "EVERREADY", "MASON CASH" |
| **Product Type** | Core product description | "T8 TUBE LIGHT", "MIXING BOWL" |
| **Size/Variant** | Dimensions, capacity, color | "4FT 36W", "29CM", "CREAM" |
| **Pack Quantity** | Explicit pack indicators | "PK5", "28 PACK", "20PCE" |

### Step 4.2: Parse Amazon Title

Apply the same extraction to the Amazon title.

### Step 4.3: Compare Extracted Elements

| Element | Supplier | Amazon | Match? |
|:--------|:---------|:-------|:------:|
| Brand | EVERREADY | Eveready | ✅ Yes (case variant) |
| Product | T8 4FT 36W TUBE LIGHT | T8 Tube 4ft 36w White 3500k | ✅ Yes |
| Size | 4FT 36W | 4ft 36w | ✅ Yes |
| Pack | (none stated) | (none stated) | ✅ Yes (both single) |

### Step 4.4: Identify Numbers That Are NOT Pack Quantities

**CRITICAL:** These numbers are specifications, NOT pack sizes:

| Pattern | Meaning | Example |
|:--------|:--------|:--------|
| `Xcm`, `Xmm`, `Xinch` | Dimension | "15 x 5.5 x 5.5 cm" = size |
| `XL`, `Xlitre`, `Xml` | Capacity | "4 Litre", "580ml" |
| `XW` | Wattage | "36W" |
| `X LED` | LED count | "9 LED" = spec |
| `Xx magnification` | Optical zoom | "2x magnification" = feature |
| `XxX` followed by unit | Dimensions | "9x9 inch", "280x115mm" |

### Step 4.5: Decision Matrix for Title Analysis

```
IF (Brand matches) AND (Product type matches) AND (Size/variant matches):
    → Proceed to Pack Size Analysis
ELSE IF (Brand matches) AND (Product type matches) BUT (Size differs):
    → FILTERED OUT (different SKU)
ELSE IF (Brand differs) BUT (Product type + specs match closely):
    → Check if same manufacturer, different brand name
    → If likely same: NEEDS VERIFICATION
    → If clearly different: FILTERED OUT
ELSE:
    → FILTERED OUT (mismatch)
```

---

## 5. PHASE 4: PACK SIZE DETECTION & ANALYSIS

### Step 5.1: Extract Pack Quantity from Supplier Title

Read the supplier title manually. Look for:

| Pattern | Example | Pack Size |
|:--------|:--------|----------:|
| `PK5`, `PK 5` | "AIRWICK DIFFUSER PK5" | 5 |
| `28 PACK` | "FIRELIGHTERS 28 PACK" | 28 |
| `20PCE`, `20 PCS` | "SHOT GLASSES 20PCE" | 20 |
| `40 DOYLEYS` | "PPS ROUND 40 DOYLEYS" | 40 |
| `(SOLD EACH)` | "KILROCK MOULD REMOVER (SOLD EACH)" | 1 |
| No indicator | "APOLLO VINEGAR SHAKER" | 1 (default) |

### Step 5.2: Extract Pack Quantity from Amazon Title

| Pattern | Example | Pack Size |
|:--------|:--------|----------:|
| `Pack of X` | "Pack of 10 Trays" | 10 |
| `X x Product` | "3 x Easy Cut Refill" | 3 |
| `X Bottles` | "5 Bottles X 30ml" | 5 |
| `(X x Y)` | "(4 x 50)" | Multipack: total items = 4×50 (if 50 is quantity-inside) |
| `Set of X` | "Set of 2 Glasses" | 2 |

**Multipack interpretation rules (CRITICAL):**
1. If Amazon shows **`N x [capacity]`** (e.g., `3 x 400ml`, `6 x 33g`, `2 x 1L`), then:
   - `N` is the **pack count** (RSU = N)
   - The capacity describes size of each unit (do **not** compute 3×400=1200 as “units”)
2. If Amazon shows **`N x [dimension]`** (e.g., `9 x 9 inch`, `30cm x 36cm`, `280 x 115mm`), treat as **dimensions**, not pack.
3. If Amazon shows `(N x M)` with no measurement units, treat as a **quantity-inside multipack** (total items = N×M) and compare against the supplier’s quantity-inside.

### Step 5.3: Calculate Pack Ratio

```
Pack Ratio = Amazon Pack / Supplier Pack

Examples:
- Supplier 50 bags, Amazon 200 bags → Ratio = 4 (need 4x supplier units)
- Supplier 5-pack, Amazon 5-pack → Ratio = 1 (1:1 match)
- Supplier 28-pack, Amazon 24-pack → Ratio = 0.86 (supplier has MORE)
```

### Step 5.4: Pack Analysis Decision Tree

```
IF Supplier Pack == Amazon Pack:
    → 1:1 Match → Continue to profit check
ELSE IF Amazon Pack > Supplier Pack:
    → Calculate Adjusted Profit (need multiple supplier units)
    → IF Adjusted Profit > 0: VERIFIED (Pack Adjustment)
    → ELSE: FILTERED OUT (unprofitable after adjustment)
ELSE IF Supplier Pack > Amazon Pack:
    → Supplier has more per unit (favorable)
    → VERIFIED (note: supplier provides extra)
```

**Critical correction (SPLIT is not automatic):**
- If **Supplier Pack > Amazon Pack**, do **not** label as VERIFIED by default.
- This is a **SPLIT CANDIDATE** and must be routed to **NEEDS VERIFICATION** unless you have explicit evidence that:
  - Amazon listing unit count matches what you can supply, and
  - splitting/repackaging is compliant and practical for your workflow.

---

## 6. PHASE 5: BROWSER VERIFICATION

### Step 6.1: When to Use Browser Verification

Use browser verification when:
- Pack size is ambiguous from titles alone
- Numbers in title could be dimensions OR pack size
- EAN missing on Amazon side
- Need to confirm product variant (color, scent, size)

### Step 6.2: Browser Verification Steps

1. **Navigate to Amazon Product Page**
   ```
   URL: https://www.amazon.co.uk/dp/{ASIN}
   ```

2. **Extract and Verify**
   - Full product title
   - Selected size/variant (dropdown value)
   - "About this item" bullet points
   - Technical details table
   - Unit count
   - Customer review mentions of pack contents

3. **Look for Pack Indicators On Page**
   - Size Name: "Pack of 10", "500 ml (Pack of 3)"
   - Unit Count: "3.0 count"
   - Title includes "X x" or "Pack of X"

4. **Take Screenshot Evidence**
   - Capture the product page showing title and price
   - Save for documentation

### Step 6.3: Browser Verification Checklist

```
☐ Product title matches supplier description
☐ Pack size explicitly stated or confirmed
☐ No variant differences (color, size, scent)
☐ Price matches expected selling price
☐ Product is in stock / available
```

### Step 6.4: Recording Verification Results

Document each verification:
```
| ASIN       | URL                           | Finding                          | Date       |
|------------|-------------------------------|----------------------------------|------------|
| B0DJDH23JW | amazon.co.uk/dp/B0DJDH23JW    | 10-Pack confirmed (9x9 = size)   | 2025-12-27 |
| B07WDRQ4J7 | amazon.co.uk/dp/B07WDRQ4J7    | 5 Bottles confirmed              | 2025-12-27 |
```

---

## 7. PHASE 6: ADJUSTED PROFIT CALCULATION

### Step 7.1: When Pack Sizes Differ

If Amazon requires more units than supplier sells individually:

```
Pack Ratio = Amazon Pack Size / Supplier Pack Size
Adjusted Cost = Supplier Price × Pack Ratio
FBA Fees ≈ Selling Price × 0.30 (estimate)
Adjusted Profit = Selling Price - Adjusted Cost - FBA Fees
```

### Step 7.2: Worked Example: TIDYZ DOGGY BAGS

| Field | Value |
|:------|:------|
| Supplier Title | TIDYZ DOGGY BAGS STRONG 50 PCS |
| Amazon Title | Tidyz 200 x Extra Large Doggy bags (4 x 50) |
| Supplier Pack | 50 bags |
| Amazon Pack | 200 bags |
| Pack Ratio | 200 ÷ 50 = **4** |
| Supplier Price | £0.67 |
| Selling Price | £6.50 |
| Adjusted Cost | £0.67 × 4 = **£2.68** |
| FBA Fees (30%) | £6.50 × 0.30 = **£1.95** |
| **Adjusted Profit** | £6.50 - £2.68 - £1.95 = **£1.87** |
| **Result** | ✅ PROFITABLE after adjustment |

### Step 7.3: Worked Example: PHOODS FOIL TRAY (Unprofitable)

| Field | Value |
|:------|:------|
| Supplier Title | PHOODS FOIL TRAY ROASTER |
| Amazon Title | Superior Sandwich Platter Trays - Pack of 10 |
| Supplier Pack | 1 tray |
| Amazon Pack | 10 trays |
| Pack Ratio | 10 ÷ 1 = **10** |
| Supplier Price | £1.08 |
| Selling Price | £14.97 |
| Adjusted Cost | £1.08 × 10 = **£10.80** |
| FBA Fees (30%) | £14.97 × 0.30 = **£4.49** |
| **Adjusted Profit** | £14.97 - £10.80 - £4.49 = **-£0.32** |
| **Result** | ❌ LOSS - FILTERED OUT |

### Step 7.4: Alternative Calculation Method

Some reports use:
```
Adjusted Profit = NetProfit - (SupplierPrice × (Pack Ratio - 1))
```

Choose one method and apply consistently.

---

## 8. PHASE 7: FINAL CATEGORIZATION

### Step 8.1: VERIFIED Criteria

A product is **VERIFIED** if ALL of the following are true:
- ☐ Exact EAN match (Supplier EAN == Amazon EAN)
- ☐ Pack sizes match (or supplier has more)
- ☐ Brand/product/variant confirmed via title analysis
- ☐ Adjusted profit > £0

### Step 8.2: HIGHLY LIKELY Criteria

A product is **HIGHLY LIKELY** if:
- ☐ EAN does NOT match (or Amazon EAN missing)
- ☐ BUT brand name matches exactly
- ☐ AND product type matches exactly
- ☐ AND size/variant is identical or within tolerance
- ☐ AND adjusted profit > £0
- ☐ Optionally: Browser verified

### Step 8.3: NEEDS VERIFICATION Criteria

A product is **NEEDS VERIFICATION** if:
- ☐ Strong brand match exists
- ☐ BUT 1-2 blocking details prevent categorization:
  - Pack size unclear from titles
  - Variant difference possible (scent, color)
  - EAN mismatch requires confirmation
  - Dimensions could be interpreted as pack size

### Step 8.4: FILTERED OUT Criteria

**Critical correction (FILTERED OUT is NOT “everything that didn’t match”):**
- Use **FILTERED OUT** only for **confirmed matches** that are excluded due to pack/variant/profit gates (audit trail).
- Completely unrelated / weak-evidence mismatches are **UNRELATED / NOT INCLUDED** and must not appear in report tables.

A product is **FILTERED OUT** if ANY of the following:
- ☐ Product type clearly different
- ☐ Size/variant mismatch confirmed
- ☐ Adjusted profit ≤ £0 after pack adjustment
- ☐ Scent/color/model mismatch confirmed
- ☐ Completely unrelated products

---

## 9. PHASE 8: REPORT COMPARISON (OPTIONAL)

### Step 9.1: Load Comparison Reports

If comparing against other LLM-generated reports:
1. Extract RowIDs from each report
2. Map RowIDs to product details
3. Compare categorizations

### Step 9.2: Identify Agreements

| Comparison | Action |
|:-----------|:-------|
| Both VERIFIED | ✅ Agree |
| Both HIGHLY LIKELY | ✅ Agree |
| Both FILTERED OUT | ✅ Agree |
| Both NEEDS VERIFICATION | ✅ Agree |

### Step 9.3: Identify Disagreements

| Comparison | Action |
|:-----------|:-------|
| Report A: VERIFIED, Report B: FILTERED | Investigate pack calculation |
| Report A: HIGHLY LIKELY, Report B: NEEDS VERIFICATION | Check confidence threshold |
| Different adjusted profit | Check fee calculation method |

### Step 9.4: Document Differences

For each disagreement:
1. State both positions
2. Provide reasoning for your position
3. Cite evidence (browser verification, title analysis)

---

## 10. DECISION TREES & FLOWCHARTS

### 10.1: Master Decision Tree

```
START
  │
  ▼
┌─────────────────────────────┐
│ Load Financial Report       │
│ Extract all rows            │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ For each row:               │
│ Check EAN Match?            │
└─────────────┬───────────────┘
              │
     ┌────────┴────────┐
     │                 │
     ▼                 ▼
  EAN MATCH        NO EAN MATCH
     │                 │
     ▼                 ▼
┌───────────┐    ┌───────────────┐
│ Analyze   │    │ Strong Brand  │
│ Titles    │    │ Match?        │
└─────┬─────┘    └───────┬───────┘
      │                  │
      ▼           ┌──────┴──────┐
  Titles Match?   │             │
      │           ▼             ▼
 ┌────┴────┐    YES           NO
 │         │      │             │
 ▼         ▼      ▼             ▼
YES       NO   HIGHLY      FILTERED
 │         │   LIKELY         OUT
 ▼         ▼
Pack     FILTERED
Match?     OUT
 │
 ▼
┌────────────┐
│ Calculate  │
│ Adj Profit │
└─────┬──────┘
      │
 ┌────┴────┐
 │         │
 ▼         ▼
> £0      ≤ £0
 │         │
 ▼         ▼
VERIFIED  FILTERED
           OUT
```

### 10.2: Pack Size Detection Flowchart

```
READ TITLE
    │
    ▼
Contains "Pack of X"? ──YES──► Pack = X
    │ NO
    ▼
Contains "X PACK"? ──YES──► Pack = X
    │ NO
    ▼
Contains "XPCE" or "X PCS"? ──YES──► Pack = X
    │ NO
    ▼
Contains "X x Y" before unit? ──YES──► Dimensions, Pack = 1
    │ NO
    ▼
Contains "X x Product"? ──YES──► Pack = X
    │ NO
    ▼
Default: Pack = 1
```

---

## 11. COMMON PITFALLS TO AVOID

### 11.1: Dimension Misreading

| ❌ WRONG | ✅ CORRECT |
|:---------|:-----------|
| "15 x 5.5 x 5.5 cm" = Pack of 15 | "15 x 5.5 x 5.5 cm" = Dimensions (15cm height) |
| "9x9 inch" = Pack of 9 | "9x9 inch" = Tray size (9" × 9") |
| "2x magnification" = Pack of 2 | "2x magnification" = Optical feature |
| "9 LED" = Pack of 9 | "9 LED" = Number of LEDs in torch |

### 11.2: Pack Size in Supplier Title

Always check the SUPPLIER title for pack indicators:
- "DOYLEYS 40" = 40-pack (not Amazon mismatch)
- "SHOT GLASSES 20PCE" = 20-pack
- "(SOLD EACH)" = Single unit

### 11.3: EAN Match ≠ Automatic Match

An exact EAN ensures same barcode, but:
- Amazon may sell multipacks of the EAN product
- Supplier may sell singles of the same EAN
- Always verify pack sizes independently

### 11.4: Fee Calculation Consistency

Use one method throughout:
```
Method A: Adjusted Profit = Selling Price - (Supplier Price × Ratio) - (Selling Price × 0.30)
Method B: Adjusted Profit = NetProfit - (Supplier Price × (Ratio - 1))
```

---

## 12. QUICK REFERENCE CHECKLISTS

### 12.1: Pre-Analysis Checklist

```
☐ Financial report loaded
☐ EAN columns normalized
☐ RowID column created
☐ Valid EAN filter applied
☐ Working list of EAN matches extracted
```

### 12.2: Per-Product Analysis Checklist

```
☐ Supplier title parsed (brand, product, size, pack)
☐ Amazon title parsed (brand, product, size, pack)
☐ Pack sizes identified (not dimensions)
☐ Pack ratio calculated
☐ Adjusted profit calculated (if ratio ≠ 1)
☐ Browser verification (if ambiguous)
☐ Final category assigned
```

### 12.3: Browser Verification Checklist

```
☐ Navigate to correct ASIN URL
☐ Verify product title matches
☐ Check size/variant selector
☐ Read "About this item" for pack info
☐ Check technical details for unit count
☐ Take screenshot for documentation
☐ Record finding in verification log
```

### 12.4: Report Generation Checklist

```
☐ VERIFIED products listed with all columns
☐ HIGHLY LIKELY products listed with evidence
☐ NEEDS VERIFICATION products with blocking details
☐ FILTERED OUT products with exclusion reason
☐ Tables formatted correctly
☐ Profit summary included
☐ Pack corrections documented
☐ UNRELATED / NOT INCLUDED is count-only (no table)
☐ Reconciliation: buckets sum to TOTAL ROWS; no duplicate RowIDs
☐ Sanitize titles: replace '|' with '/' and remove newlines
```

---

## APPENDIX A: COLUMN DEFINITIONS FOR OUTPUT TABLES

| Column | Description | Example |
|:-------|:------------|:--------|
| Verdict | Final category | VERIFIED, HIGHLY LIKELY, etc. |
| Confidence | 0-100 score | 95 |
| SupplierTitle | Full supplier product name | MASON CASH MIXING BOWL CREAM 29CM |
| AmazonTitle | Full Amazon product name (truncated) | Mason Cash Colour Mix Cream... |
| Supplier EAN | Barcode from supplier | 5010853235530 |
| Amazon EAN | Barcode from Amazon | 5010853235530 |
| ASIN | Amazon product ID | B01IFIJ91Y |
| SupplierPrice | Cost inc VAT | £7.66 |
| SellingPrice | Amazon price inc VAT | £24.99 |
| NetProfit | Original profit before adjustment | £5.11 |
| ROI | Return on investment % | 73.8% |
| Sales | Estimated monthly sales | 200 |
| Pack Verdict | Pack analysis result | 1:1, Pack mismatch 1→4, etc. |
| Adjusted Profit | Profit after pack adjustment | £5.11 or -£1.28 |
| Key Match Evidence | Why this is a match | Exact EAN match, Brand match |
| Filter Reason | Why filtered (if applicable) | Different SKU, Unprofitable |

---

## APPENDIX B: SAMPLE WORKFLOW EXECUTION

### Example: Analyzing Row 964 (SUPERIOR FOIL)

**Step 1: Extract Data**
```
RowID: 964
ASIN: B0DJDH23JW
Supplier EAN: 5060357990107
Amazon EAN: 5060357990107
SupplierTitle: SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN
AmazonTitle: Superior 10-Pack Aluminium Foil Trays...9x9 inch
```

**Step 2: EAN Match Check**
- Supplier EAN: 5060357990107
- Amazon EAN: 5060357990107
- Result: ✅ EXACT MATCH

**Step 3: Title Analysis**
- Supplier: "10 CONTAINERS" → 10-pack
- Supplier: "9X9IN" → Tray size (9 inches × 9 inches)
- Amazon: "10-Pack" → 10-pack
- Amazon: "9x9 inch" → Tray size

**Step 4: Pack Size Determination**
- Supplier Pack: 10
- Amazon Pack: 10
- Ratio: 10/10 = 1 (1:1 match)
- **CRITICAL:** "9X9" is tray SIZE, not pack count!

**Step 5: Profit Check**
- NetProfit: £2.13
- No adjustment needed (ratio = 1)

**Step 6: Final Category**
- EAN matches: ✅
- Pack matches: ✅
- Profit positive: ✅
- **VERDICT: VERIFIED**

---

## APPENDIX C: DETAILED REASONING EXAMPLES (15+ Products)

This section provides the exact thought process and logic chains used when classifying each product. Study these examples to understand the reasoning methodology.

---

### C.1: VERIFIED PRODUCT EXAMPLES

#### Example C.1.1: EVERREADY T8 4FT 36W TUBE LIGHT (Row 370)

**Raw Data:**
```
Supplier EAN: 5050028016069
Amazon EAN: 5050028016069
SupplierTitle: EVERREADY T8 4FT 36W TUBE LIGHT
AmazonTitle: Eveready T8 Tube 4ft 36w White 3500k
SupplierPrice: £2.99
SellingPrice: £18.99
NetProfit: £8.00
```

**Step-by-Step Reasoning:**

1. **EAN Check:**
   - Supplier: 5050028016069
   - Amazon: 5050028016069
   - **EXACT MATCH** ✅
   - *Reasoning: Both are valid 13-digit EAN codes and they match exactly*

2. **Brand Extraction:**
   - Supplier: "EVERREADY" (first word, uppercase)
   - Amazon: "Eveready" (first word, title case)
   - **MATCH** ✅
   - *Reasoning: Same brand, different capitalization is acceptable*

3. **Product Type Analysis:**
   - Supplier: "T8 TUBE LIGHT"
   - Amazon: "T8 Tube"
   - **MATCH** ✅
   - *Reasoning: Both describe the same fluorescent tube type (T8)*

4. **Size/Spec Analysis:**
   - Supplier: "4FT 36W" (4 feet length, 36 watts)
   - Amazon: "4ft 36w" (4 feet length, 36 watts)
   - **MATCH** ✅
   - *Reasoning: Identical specifications, case difference irrelevant*

5. **Pack Size Detection:**
   - Supplier: No pack indicator → Single unit
   - Amazon: No pack indicator → Single unit
   - **1:1 MATCH** ✅
   - *Reasoning: Neither title contains "pack", "pcs", or quantity indicators*

6. **Number Interpretation Check:**
   - "4FT" → Length (4 feet) → NOT pack size
   - "36W" → Wattage (36 watts) → NOT pack size
   - "3500k" → Color temperature (3500 Kelvin) → NOT pack size
   - *Reasoning: All numbers are product specifications, not quantities*

7. **Profit Verification:**
   - NetProfit: £8.00 > £0
   - No pack adjustment needed
   - **PROFITABLE** ✅

8. **Final Classification:**
   ```
   EAN Match: ✅
   Title Match: ✅
   Pack Match: ✅ (1:1)
   Profit: ✅ (£8.00)
   
   VERDICT: VERIFIED
   Confidence: 95
   ```

---

#### Example C.1.2: SUPERIOR FOIL 10 CONTAINERS (Row 964) - Dimension Pitfall Avoided

**Raw Data:**
```
Supplier EAN: 5060357990107
Amazon EAN: 5060357990107
SupplierTitle: SUPERIOR FOIL 10 CONTAINERS & LID 9X9IN
AmazonTitle: Superior 10-Pack Aluminium Foil Trays with Paper Lids...9x9 inch
```

**Critical Reasoning - Why "9X9" is NOT Pack Size:**

1. **Initial Scan - Potential Pack Indicators:**
   - Supplier: "10 CONTAINERS" ← PACK SIZE (10)
   - Supplier: "9X9IN" ← COULD BE misread as pack
   - Amazon: "10-Pack" ← PACK SIZE (10)
   - Amazon: "9x9 inch" ← COULD BE misread as pack

2. **Context Analysis for "9X9":**
   - Question: What comes AFTER "9X9"?
   - Answer: "IN" (inches) or "inch"
   - *Conclusion: "9X9IN" means 9 inches × 9 inches = TRAY DIMENSIONS*

3. **Verification Logic:**
   ```
   IF number followed by unit (inch, cm, mm):
       → It's a DIMENSION, not pack size
   ELSE IF number followed by "pack", "pcs", "containers":
       → It's a PACK SIZE
   ```

4. **Correct Pack Extraction:**
   - Supplier Pack: 10 (from "10 CONTAINERS")
   - Amazon Pack: 10 (from "10-Pack")
   - Ratio: 1:1

5. **Why This Matters:**
   - A regex script incorrectly read "9" as pack size
   - Manual analysis correctly identifies context
   - "9x9" ALWAYS refers to tray dimensions in food container context

**Final Classification:**
```
VERDICT: VERIFIED
Pack Verdict: 1:1 (10-pack; 9x9 is tray SIZE, not pack count)
Confidence: 95
```

---

#### Example C.1.3: APOLLO VINEGAR SHAKER (Row 1103) - Another Dimension Pitfall

**Raw Data:**
```
SupplierTitle: APOLLO VINEGAR SHAKER
AmazonTitle: apollo THE HOUSEWARES BRAND 3357 Glass Vinegar Shaker, Clear 15 x 5.5 x 5.5 cm
```

**Critical Reasoning - Why "15" is NOT Pack Size:**

1. **Suspicious Element Identified:**
   - Amazon has: "15 x 5.5 x 5.5 cm"
   - Script might extract "15" as pack size

2. **Context Analysis:**
   - Question: What is "15 x 5.5 x 5.5"?
   - Answer: Three numbers followed by "cm"
   - Pattern: Length × Width × Height
   - *Conclusion: These are DIMENSIONS in centimeters*

3. **Physical Reasoning:**
   - 15cm = ~6 inches (reasonable shaker height)
   - 5.5cm = ~2.2 inches (reasonable diameter)
   - A "pack of 15" shakers for £6.58 would be ~£0.44 each (unrealistic)

4. **Final Check:**
   - Supplier: No pack indicator → Single unit
   - Amazon: "15 x 5.5 x 5.5 cm" = Dimensions → Single unit
   - **1:1 MATCH**

**Key Learning:**
```
RULE: When you see "X x Y x Z" followed by a unit (cm, mm, inch):
      → These are ALWAYS dimensions (L×W×H)
      → NEVER interpret as pack size
```

---

### C.2: HIGHLY LIKELY PRODUCT EXAMPLES

#### Example C.2.1: SCHOTT ZWIESEL WINE GLASS (Row 444) - EAN Mismatch but Strong Match

**Raw Data:**
```
Supplier EAN: 4001836065665
Amazon EAN: 5023041541245  ← DIFFERENT!
SupplierTitle: SCHOTT ZWIESEL WHITE WINE GLASS 407ML SET OF 2
AmazonTitle: Schott Zwiesel Pure Glassware - White Wine Glasses - Set of 2, 408ml Capacity
```

**Reasoning Chain:**

1. **EAN Check:**
   - Supplier: 4001836065665
   - Amazon: 5023041541245
   - **NO MATCH** ❌
   - *Reasoning: Different barcodes → Cannot be VERIFIED*

2. **Brand Analysis:**
   - Supplier: "SCHOTT ZWIESEL" (premium German glassware)
   - Amazon: "Schott Zwiesel" (same brand)
   - **EXACT BRAND MATCH** ✅

3. **Product Type:**
   - Supplier: "WHITE WINE GLASS"
   - Amazon: "White Wine Glasses"
   - **MATCH** ✅

4. **Pack/Set Analysis:**
   - Supplier: "SET OF 2"
   - Amazon: "Set of 2"
   - **MATCH** ✅

5. **Capacity Analysis:**
   - Supplier: "407ML"
   - Amazon: "408ml"
   - Difference: 1ml (0.24%)
   - **ACCEPTABLE TOLERANCE** ✅
   - *Reasoning: 1ml difference is rounding variation, same product*

6. **Why Not VERIFIED?**
   - EAN doesn't match
   - Could be different product variants with same specs
   - Need physical barcode verification to confirm

7. **Why Not NEEDS VERIFICATION?**
   - Brand match is exact
   - Product type is exact
   - Pack size is exact
   - Capacity within tolerance
   - Too many matching factors to require verification

**Final Classification:**
```
VERDICT: HIGHLY LIKELY
Confidence: 85
Evidence: Brand match + Set of 2 + 407ml≈408ml
Risk: EAN mismatch - verify barcode on physical product
```

---

#### Example C.2.2: AMTECH POINTING TROWEL (Row 1167) - Browser Verified

**Raw Data:**
```
Supplier EAN: 5032759027644
Amazon EAN: (missing)
SupplierTitle: AMTECH POINTING TROWEL 150M(6") WITH SOFT GRIP
AmazonTitle: Amtech G0230 150mm (6") Pointing trowel with soft grip
```

**Reasoning Chain:**

1. **EAN Check:**
   - Supplier: 5032759027644 (valid)
   - Amazon: Missing/blank
   - **NO EAN AVAILABLE** → Cannot be VERIFIED via EAN alone

2. **Brand Analysis:**
   - Supplier: "AMTECH" (UK tool brand)
   - Amazon: "Amtech" (same)
   - **EXACT MATCH** ✅

3. **Product Type:**
   - Supplier: "POINTING TROWEL"
   - Amazon: "Pointing trowel"
   - **EXACT MATCH** ✅

4. **Size Analysis:**
   - Supplier: "150M(6")" = 150mm = 6 inches
   - Amazon: "150mm (6")" = 150mm = 6 inches
   - **EXACT MATCH** ✅

5. **Feature Analysis:**
   - Supplier: "WITH SOFT GRIP"
   - Amazon: "with soft grip"
   - **EXACT MATCH** ✅

6. **Model Number Check:**
   - Amazon includes: "G0230"
   - Supplier: Not mentioned
   - *This doesn't disqualify - supplier just omitted model*

7. **Browser Verification Performed:**
   - Navigated to amazon.co.uk/dp/B00ABJQTPU
   - Confirmed: 150mm (6") Pointing trowel
   - Confirmed: Soft grip feature
   - Confirmed: Single unit (not multi-pack)

**Why HIGHLY LIKELY instead of VERIFIED:**
- No Amazon EAN to compare
- Strong match confirmed via browser, but barcode unverified

**Final Classification:**
```
VERDICT: HIGHLY LIKELY
Confidence: 90
Evidence: Exact title match + Browser verified
Risk: Amazon EAN missing - confirm barcode at purchase
```

---

### C.3: NEEDS VERIFICATION EXAMPLES

#### Example C.3.1: FAIRY DISH BRUSH & REFILLS 3PCS (Row 1168) - Pack Ambiguity

**Raw Data:**
```
SupplierTitle: FAIRY MAX POWER SOAP DISPENSING DISH BRUSH & REFILLS 3PCS
AmazonTitle: Fairy Soap Dispensing Dish Brush
ASIN: B0BYKDX25N
```

**Reasoning Chain:**

1. **Brand Match:**
   - Supplier: "FAIRY"
   - Amazon: "Fairy"
   - **MATCH** ✅

2. **Product Type Match:**
   - Both: "Soap Dispensing Dish Brush"
   - **MATCH** ✅

3. **Pack/Contents Analysis:**
   - Supplier: "& REFILLS 3PCS"
   - Amazon: No mention of refills
   - **MISMATCH** ⚠️

4. **Interpretation of "3PCS":**
   - Option A: 1 brush + 2 refills = 3 pieces
   - Option B: 3 brushes total
   - **AMBIGUOUS** → Need verification

5. **Browser Verification Performed:**
   - Amazon page shows: Single brush handle only
   - No refills included in this ASIN
   - Refills sold separately (B0BYKDLJ5Z)

6. **Blocking Details:**
   - Supplier includes refills, Amazon doesn't
   - If "3PCS" = 1 brush + 2 refills, then it's a different bundle

**Why NEEDS VERIFICATION instead of FILTERED:**
- Base product (brush) matches
- Could be supplier bundling their own set
- Need to confirm what supplier actually ships

**Final Classification:**
```
VERDICT: NEEDS VERIFICATION
Blocking Detail: Amazon = single brush, Supplier = 3-piece set
Action Needed: Verify if "3PCS" means brush+2 refills or 3 brushes
```

---

#### Example C.3.2: PRIMA vs LARA SHOWERHEAD (Row 157) - Brand Mismatch

**Raw Data:**
```
SupplierTitle: PRIMA MULTI SHOWERHEAD CHROME
AmazonTitle: Lara | Multi Spray Shower Head - Chrome
ASIN: B00569FG1S
```

**Reasoning Chain:**

1. **Brand Analysis:**
   - Supplier: "PRIMA"
   - Amazon: "Lara"
   - **DIFFERENT BRANDS** ⚠️

2. **Product Type:**
   - Supplier: "MULTI SHOWERHEAD"
   - Amazon: "Multi Spray Shower Head"
   - **MATCH** ✅

3. **Feature Analysis:**
   - Both: "CHROME" color
   - **MATCH** ✅

4. **Why Different Brands Might Still Match:**
   - Some manufacturers sell under multiple brand names
   - "Prima" and "Lara" could be same factory
   - White-label products common in this category

5. **Why NEEDS VERIFICATION:**
   - Cannot confirm same manufacturer
   - Brand is a core identifying feature
   - Risk of completely different products

6. **Potential HIGH PROFIT:**
   - NetProfit: £10.37 (526% ROI)
   - Worth investigating further

**Final Classification:**
```
VERDICT: NEEDS VERIFICATION
Blocking Detail: Brand name different (Prima vs Lara)
Why Close: Same product type + Same finish (Chrome)
Action Needed: Verify if same manufacturer or unrelated products
```

---

### C.4: FILTERED OUT EXAMPLES

#### Example C.4.1: ULTRATAPE 24MM vs 48MM (Row 1155) - Size Mismatch

**Raw Data:**
```
SupplierTitle: ULTRATAPE PICTURE FRAME TAPE 24MMX50M
AmazonTitle: Ultratape | Picture Frame Tape | 48mm x 33m
```

**Reasoning Chain:**

1. **Brand Match:**
   - Both: "ULTRATAPE" / "Ultratape"
   - **MATCH** ✅

2. **Product Type Match:**
   - Both: "PICTURE FRAME TAPE"
   - **MATCH** ✅

3. **Size Analysis:**
   - Supplier WIDTH: 24mm
   - Amazon WIDTH: 48mm
   - **MISMATCH** ❌ (2x difference!)

4. **Length Analysis:**
   - Supplier LENGTH: 50m
   - Amazon LENGTH: 33m
   - **MISMATCH** ❌ (different)

5. **Browser Verification:**
   - Confirmed Amazon is 48mm × 33m
   - No 24mm variant available on this listing

6. **Why This Cannot Match:**
   - 24mm tape ≠ 48mm tape (physically different)
   - Different SKU entirely
   - Customer expecting 48mm would receive 24mm

**Final Classification:**
```
VERDICT: FILTERED OUT
Filter Reason: Width mismatch (24mm supplier vs 48mm Amazon)
This is NOT a pack size difference - it's a different product
```

---

#### Example C.4.2: ELBOW GREASE EUCALYPTUS vs LEMON (Row 1095) - Scent + Pack Mismatch

**Raw Data:**
```
SupplierTitle: ELBOW GREASE FOAMING TOILET CLEANER EUCALYPTUS 500G
AmazonTitle: 3 x Elbow Grease Foaming Toilet Cleaner, Deep Cleaning Action, Lemon Fresh
```

**Reasoning Chain:**

1. **Brand Match:**
   - Both: "ELBOW GREASE"
   - **MATCH** ✅

2. **Product Type:**
   - Both: "FOAMING TOILET CLEANER"
   - **MATCH** ✅

3. **Scent Analysis:**
   - Supplier: "EUCALYPTUS"
   - Amazon: "Lemon Fresh"
   - **MISMATCH** ❌

4. **Pack Analysis:**
   - Supplier: (single) 500G
   - Amazon: "3 x" (3-pack)
   - **MISMATCH** ❌

5. **Double Disqualification:**
   - Problem 1: Wrong scent (Eucalyptus ≠ Lemon)
   - Problem 2: Need 3 units (pack adjustment)

6. **Even if we ignored scent:**
   - Adjusted Profit = £0.82 - (£2.09 × 2) = -£3.35
   - **UNPROFITABLE** ❌

**Final Classification:**
```
VERDICT: FILTERED OUT
Filter Reason: Scent mismatch (Eucalyptus vs Lemon) + Pack mismatch (1 vs 3)
Note: Even without scent issue, adjusted profit is negative
```

---

#### Example C.4.3: PHOODS FOIL TRAY 1x vs 10-Pack (Row 363) - Unprofitable After Adjustment

**Raw Data:**
```
Supplier EAN: 5060357991357
Amazon EAN: 5060357991357  ← EXACT MATCH!
SupplierTitle: PHOODS FOIL TRAY ROASTER
AmazonTitle: Superior Sandwich Platter Trays - Pack of 10
SupplierPrice: £1.08
SellingPrice: £14.97
NetProfit: £3.90
```

**Reasoning Chain:**

1. **EAN Check:**
   - **EXACT MATCH** ✅
   - *Initial thought: This should be VERIFIED...*

2. **Pack Analysis:**
   - Supplier: No pack indicator → 1 unit
   - Amazon: "Pack of 10" → 10 units
   - **MISMATCH: Need 10 supplier units!**

3. **Browser Verification:**
   - Confirmed Amazon listing is Pack of 10 trays
   - £14.97 for 10 trays = £1.50 each

4. **Adjusted Profit Calculation:**
   ```
   Adjusted Cost = £1.08 × 10 = £10.80
   FBA Fees = £14.97 × 0.30 = £4.49
   Adjusted Profit = £14.97 - £10.80 - £4.49 = -£0.32
   ```

5. **Why FILTERED despite EAN Match:**
   - EAN confirms same product barcode
   - BUT Amazon bundles 10 units of this product
   - Supplier sells individually
   - After buying 10 and paying fees, we LOSE money

**Key Learning:**
```
RULE: EAN match is NOT enough!
      Always verify pack sizes.
      Calculate adjusted profit when ratios differ.
      Filter if adjusted profit ≤ £0
```

**Final Classification:**
```
VERDICT: FILTERED OUT
Filter Reason: Pack 1→10 requires 10 units = Unprofitable (-£0.32)
Note: Despite exact EAN match, this is a LOSS after adjustment
```

---

### C.5: REASONING SUMMARY TABLE

| Scenario | Key Question | Answer → Action |
|:---------|:-------------|:----------------|
| EAN matches | Pack sizes same? | YES → Check profit → VERIFIED |
| EAN matches | Pack sizes differ | Calculate adjusted profit → VERIFIED or FILTERED |
| EAN missing | Brand exact match? | YES → Check all specs → HIGHLY LIKELY |
| EAN mismatch | Brand exact match? | YES → Check all specs → HIGHLY LIKELY |
| Brand differs | Same manufacturer? | UNKNOWN → NEEDS VERIFICATION |
| Size differs | Same product? | NO → FILTERED OUT |
| Scent differs | Same product? | NO → FILTERED OUT |
| Numbers in title | Followed by unit? | YES → Dimension, not pack |
| "X x Y" format | Followed by unit? | YES → Dimensions |
| "2x magnification" | Pack of 2? | NO → Optical feature |
| Adjusted profit <0 | Keep product? | NO → FILTERED OUT |

---

### C.6: BROWSER VERIFICATION REASONING EXAMPLES

#### When Browser Verification Confirmed VERIFIED:

**Product: AIR WICK REED DIFFUSER PK5 (Row 626)**
```
Initial State:
- SupplierTitle says "PK5" (5-pack)
- AmazonTitle says "5 Bottles X 30ml"
- Could "5 Bottles" be 5 separate units or 1 pack of 5?

Browser Action:
- Navigate to amazon.co.uk/dp/B07WDRQ4J7
- Check size selector: "5 Bottles x 30ml" selected
- Check product images: Shows 5 boxes of diffuser
- Check "About this item": Confirms 5 individual bottles

Conclusion:
- Supplier sells 5-pack
- Amazon sells 5-pack (5 × 30ml bottles)
- 1:1 Match → VERIFIED
```

#### When Browser Verification Caused EXCLUSION:

**Product: PRICE & KENSINGTON TEAPOT (Row 1402)**
```
Initial State:
- SupplierTitle: "2 CUP TEAPOT MATT NAVY"
- AmazonTitle: "Black 6 Cup Teapot"
- Two potential issues: cup size + color

Browser Action:
- Navigate to amazon.co.uk/dp/B0013IUIPA
- Check title: "Price & Kensington Black 6 Cup Teapot"
- Check color: Gloss Black (not Matt Navy)
- Check size: 6 Cup (not 2 Cup)
- Check variations: No 2-cup or Navy options available

Conclusion:
- Size mismatch: 2 cup ≠ 6 cup
- Color mismatch: Matt Navy ≠ Black
- Different SKU entirely → FILTERED OUT
```

---

*End of Detailed Reasoning Appendix*

---

*End of Methodology Guide*
*Version: 1.1 (Enhanced with Detailed Reasoning)*
*Last Updated: 2025-12-28*
