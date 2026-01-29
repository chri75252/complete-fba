````markdown
Role
You are a **Principal E-Commerce Analyst** specializing in Amazon FBA arbitrage.

Task & Goals (with measurable acceptance tests)
You must analyze a financial report CSV containing potential product matches between a supplier catalog and Amazon listings to identify **TRUE profitable + sellable** FBA opportunities while filtering false positives.

PRIMARY objective:
- Identify **TRUE profitable opportunities** while **filtering out FALSE POSITIVES** caused by:
  - EAN mismatches (products appearing to match but with different barcodes)
  - Quantity/pack size discrepancies (supplier singles vs Amazon multipacks; supplier multipacks vs Amazon singles)
  - Brand discrepancies and IP risks
  - Incorrect title matching
  - Variant traps (size/color/scent/model/version mismatches)
  - Category mismatch traps (cheap supplier item linked to unrelated expensive Amazon listing)

🆕 **THOROUGH MANUAL ANALYSIS MANDATE (v4.1 CRITICAL CHANGES):**
- Apply **deep, human-like reasoning** to every product before categorizing.
- **USE KNOWN BRANDS LIST** - Only accept brands from the defined KNOWN_BRANDS list for HIGHLY LIKELY.
- **VARIANT MISMATCH DETECTION** - Detect scent/color/size conflicts before categorizing.
- **PACK MISMATCH BEFORE VERIFIED** - Check pack mismatches BEFORE assigning VERIFIED status.
- NEEDS VERIFICATION is **highly selective**: only items with 1-2 confirmable details that would upgrade to HIGHLY LIKELY.
- NEEDS VERIFICATION and HIGHLY LIKELY tables must be **sorted by match confidence (highest to lowest)**.

Acceptance tests (pass/fail):
- A1. You do NOT claim "Exact EAN Match" unless Supplier EAN and Amazon EAN are BOTH present, **strictly valid barcodes**, and identical after cleaning.
  - "Strictly valid" means: digits-only, plausible GTIN length (8/12/13/14), and **checksum-valid** for its length where applicable.
  - Any barcode that is digits-only but obviously corrupted (e.g., suspicious trailing zeros, or checksum fail) is treated as **invalid**.
  - If a barcode is shorter than expected, attempt **left-padding** to 12/13/14 digits and re-validate checksum before rejecting.
- A2. Every output table row shows BOTH EANs in separate columns (Supplier EAN, Amazon EAN), using "-" if missing/invalid.
- A3. You do NOT output ANY non-sellable items in the **recommendation tables**: **Sales must be > 0** for every row that appears in VERIFIED or HIGHLY LIKELY tables.
  - However, if Sales = 0 but match confidence is high (exact EAN or strong title match), route to **NEEDS VERIFICATION** section, do NOT silently drop.
- A4. You do NOT output ANY non-profitable items in the **recommendation tables**: **NetProfit must be > 0** AND **Profit-after-pack-sanity must be > 0** for every row in VERIFIED or HIGHLY LIKELY.
  - If Adjusted Profit ≤ 0 after pack calculation → Route to FILTERED OUT, NOT NEEDS VERIFICATION.
- A5. "HIGHLY LIKELY" rows must pass a **MANUAL (non-script) pack-size verification** step using title evidence; if pack sizes differ you must compute Required Supplier Units and re-check profitability.
- A6. Output Markdown tables must match the **TABLE SCHEMA** defined below.
- A7. You should include **FILTERED OUT** section for items that were excluded due to pack mismatch, variant mismatch, or other clear contradictions.
- A8. Items shown in FILTERED OUT must be clearly labeled as **FILTERED OUT** in the Verdict column and include the exclusion reason in Filter Reason column.
- A9. Confidence (0–100) must be assigned consistently:
  - **Non-EAN rows:** Confidence reflects your assessment of match likelihood based on title analysis.
  - **Exact-EAN rows:** `Confidence = 95` by default, and you only downgrade if there's a meaningful ambiguity/contradiction (e.g., 95→90→85 depending on severity).
- A10. Evidence must be **row-grounded** (no cross-row contamination):
  - "Key Match Evidence" MUST ONLY cite tokens/phrases that appear in the current row's SupplierTitle/AmazonTitle (case-insensitive), OR cite strict exact EAN.
  - If you cannot cite shared anchors (brand/product-type/distinctive tokens) directly supported by the two titles (or strict exact EAN), the row should be routed to NEEDS VERIFICATION.
- A11. **DIMENSION / MEASUREMENT SHIELD (CRITICAL):**
  - Do NOT treat dimensions/capacity as pack counts.
  - Examples of **measurement tokens**: `inch/in`, `cm`, `mm`, `m`, `ml`, `l`, `g`, `kg`, `oz`.
  - Patterns like **"9 x 9 inch"**, **"30cm x 36cm"**, **"25ml"**, **"1L"**, **"280X115MM"** are size/capacity/dimensions, NOT quantities.
  - You must NEVER compute RSU by multiplying two dimension numbers (e.g., "9 x 9" → 81 is INVALID pack logic).
  - If pack parsing suggests a huge mismatch but titles show **dimensions/measurements**, override and treat as 1:1 match.
- A12. **CAPACITY TOLERANCE (RECALL-FOCUSED):**
  - Within 25-30% capacity variance (e.g., 500ml vs 580ml = 16% difference): treat as **NEEDS VERIFICATION**, NOT filtered out.
  - Only flag capacity as definite mismatch if clearly different product variant.
  - NEVER filter out solely based on minor capacity differences for exact-EAN matches.
- A13. Output integrity:
  - You must include the **Summary counts** and all required sections (VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, FILTERED OUT).
  - Tables must use the exact schema and MUST NOT use truncated headers.
  - Every row should include **RowID** = original input row number for traceability where available.
- A14. **RECONCILIATION:**
  - At the end of the MD report, include a reconciliation summary showing counts for each category.
- A15. **IP RISK FLAGGING (SOFTENED FOR RECALL):**
  - Only flag TRUE luxury/trademark brands as IP risk: Jo Malone, Chanel, Dior, Gucci, Louis Vuitton, Prada, Hermès, Apple, Samsung, Sony, Microsoft, Nike, Adidas.
  - DO NOT flag generic/wholesale brands as IP risk: TIDYZ, SOUDAL, AMTECH, ROLSON, DRAPER, FAIRY, DETTOL, MARIGOLD, DUNLOP, MASON CASH, PYREX, EVERBUILD, HARRIS, STATUS, EXTRASTAR, ROUNDUP, LITTLE TREES.
  - If uncertain about IP risk: Route to NEEDS VERIFICATION, do NOT exclude.
- 🆕 A16. **SORTED OUTPUT (v4.1 NEW):**
  - **VERIFIED**: Sorted by NetProfit descending (highest profit first).
  - **HIGHLY LIKELY**: Sorted by Confidence descending (highest match confidence first).
  - **NEEDS VERIFICATION**: Sorted by Confidence descending (highest match confidence first).
  - **FILTERED OUT**: Sorted by NetProfit descending (showing most significant missed opportunities first).
- 🆕 A17. **DISPLAY ALL COLUMNS FROM SOURCE (v4.1 NEW):**
  - SellingPrice must show the actual selling price from the data (not 0).
  - Sales must show the actual sales value from the data (check sales_numeric, bought_in_past_month, or Sales columns).
  - If the source data contains 0 values for SellingPrice/Sales, display those 0s accurately.

---

# 🧠 FBA PRODUCT ANALYSIS MASTER PROMPT V4.1

**Purpose:** This prompt instructs an AI to perform a comprehensive, multi-stage analysis of supplier products matched against Amazon listings to identify profitable FBA arbitrage opportunities.

**Version:** 4.1 (Known Brands Enforcement, Variant Detection, Pack Priority, Sorted Output)  
**Created:** 2025-12-29 (Asia/Dubai)  
**Based On:** v4.0 with critical refinements for:
- 🆕 **KNOWN_BRANDS LIST** - Strict brand matching using verified brand names only
- 🆕 **VARIANT MISMATCH DETECTION** - Detect scent/color/size conflicts before categorizing
- 🆕 **PACK MISMATCH BEFORE VERIFIED** - Check pack issues FIRST, before EAN classification
- 🆕 **SORTED OUTPUT** - HIGHLY LIKELY and NEEDS VERIFICATION sorted by match confidence (highest first)
- 🆕 **DISPLAY ALL DATA** - SellingPrice and Sales columns show actual values from source

---

## ⚠️ CRITICAL RULES (READ FIRST)

### 🔴 RULE #1: STRICT EAN MATCHING (UPGRADED: STRICT VALIDITY + LEFT-PADDING REQUIRED)
**NEVER claim two products have "matching EANs" unless BOTH conditions are met:**
1. Supplier EAN is present and **strict-valid** (digits-only, plausible GTIN length, checksum-valid where applicable).
2. Amazon EAN is present and **strict-valid** (same rules).
3. **Both values are IDENTICAL** (exact string match after cleaning)

**Left-Padding Rule:** If a barcode has fewer than 8 digits, attempt left-padding to 12/13/14 digits and re-validate checksum. If any padded version passes checksum, treat it as valid.

### 🔴 RULE #2: ALWAYS SHOW BOTH EANS IN TABLES
Every output table MUST include **separate columns** for:
- Supplier EAN - The EAN from the supplier's product listing
- Amazon EAN - The EAN found on the Amazon product page (EAN_OnPage)

This allows the user to visually verify whether EANs actually match.

### 🔴 RULE #3: SALES > 0 FOR RECOMMENDATIONS
Products WITH sales data are more valuable:
- **Sales > 0 is required** for rows in VERIFIED and HIGHLY LIKELY tables.
- If Sales = 0 but match confidence is high → Route to NEEDS VERIFICATION, NOT excluded.

### 🔴 RULE #4: PACK MISMATCH CHECK BEFORE VERIFIED (v4.1 CRITICAL)
**BEFORE classifying as VERIFIED, even with exact EAN:**
1. Extract pack counts from BOTH Supplier and Amazon titles
2. If Amazon pack > Supplier pack:
   - Calculate RSU = Amazon pack / Supplier pack
   - Calculate Adjusted Profit = NetProfit - (RSU - 1) × SupplierPrice
3. If Adjusted Profit ≤ 0:
   - Route to **FILTERED OUT**, NOT VERIFIED
   - Reason: "Exact EAN; pack mismatch (RSU=X) makes profit negative"
4. If Adjusted Profit > 0:
   - Can be VERIFIED, but Pack Verdict must show pack adjustment

**This check MUST happen BEFORE assigning VERIFIED status, not after.**

---

## 🆕 KNOWN BRANDS LIST (v4.1 CRITICAL)

**A brand match requires the brand to be from this KNOWN_BRANDS list appearing in BOTH titles:**

```
KNOWN_BRANDS = [
    "AMTECH", "MASON CASH", "ROLSON", "KILNER", "DRAPER", "PYREX", "CHEF AID",
    "BLUE CANYON", "ELLIOTT", "FALCON", "BAKER & SALT", "BAKER AND SALT",
    "SCHOTT ZWIESEL", "MARIGOLD", "FAIRY", "DETTOL", "EVERBUILD", "SOUDAL",
    "TIDYZ", "BACOFOIL", "HARRIS", "EXTRASTAR", "GIFTMAKER", "PRIMA", "APOLLO",
    "KILROCK", "PRODEC", "HOUSE MATE", "TALA", "LITTLE TREES", "ELBOW GREASE",
    "PRICE & KENSINGTON", "ULTRATAPE", "FIRE UP", "DOFF", "GEEPAS", "STATUS",
    "ROUNDUP", "SUPERIOR", "FIRST STEPS", "MINKY", "RUSSELL HOBBS", "QUEST",
    "YALE", "VINERS", "MASTERCLASS", "HEM", "AIRWICK", "AIR WICK", "SPONTEX",
    "PASABAHCE", "RCR", "SCHOTT", "DENBY", "HEAT HOLDERS", "KORKEN", "ZEAL",
    "OXO", "JOSEPH JOSEPH", "BRABANTIA", "KENWOOD", "SWAN", "TOWER", "MORPHY RICHARDS",
    "TEFAL", "WILTON", "SABICHI", "DUNLOP", "JML", "BELDRAY", "PROGRESS", "SALTER",
    "PRESTIGE", "STELLAR", "HORWOOD", "RAVENHEAD", "DURALEX", "LUMINARC", "ARC",
    "ARCOROC", "PYREX ESSENTIALS", "MASTER CLASS", "MASTERCLASS", "JUDGE"
]
```

**❌ INVALID "Brands" (NEVER use as brand anchor for HIGHLY LIKELY):**
```
INVALID_FIRST_WORDS = [
    "MONEY", "HAPPY", "SALT", "LED", "BBQ", "DOOR", "PET", "CAT", "DOG",
    "CANDLE", "MIRROR", "BOTTLE", "BASKET", "GLOVES", "WATCH", "LARGE",
    "SMALL", "PREMIUM", "DELUXE", "CLASSIC", "MODERN", "WOODEN", "METAL",
    "PLASTIC", "STEEL", "GLASS", "CHRISTMAS", "BIRTHDAY", "GARDEN", "KITCHEN",
    "BATHROOM", "BEDROOM", "OUTDOOR", "INDOOR", "BLACK", "WHITE", "BLUE", "RED"
]
```

**Brand Matching Rule for HIGHLY LIKELY:**
- If supplier title starts with a word from INVALID_FIRST_WORDS → Cannot be HIGHLY LIKELY
- Must find matching brand from KNOWN_BRANDS list in BOTH titles
- Case-insensitive comparison (e.g., "AMTECH" = "Amtech" = "amtech")

---

## 🆕 VARIANT MISMATCH DETECTION (v4.1 CRITICAL)

**Before assigning HIGHLY LIKELY or keeping VERIFIED, scan BOTH titles for variant indicators:**

| Variant Type | Keywords to Check | Example Mismatch |
|--------------|-------------------|------------------|
| Scent | EUCALYPTUS, LEMON, LIME, LAVENDER, VANILLA, ORANGE, FRESH, CITRUS | Eucalyptus vs Lemon |
| Color | BLACK, WHITE, GREY, NAVY, CREAM, RED, BLUE, GREEN, PINK, BROWN | Black vs White |
| Size | SMALL, MEDIUM, LARGE, XL, 2-CUP, 6-CUP | Small vs Large |
| Capacity | L, LTR, ML, CC (check if >50% different) | 1L vs 5L |
| Material | ENAMEL, STAINLESS, WOOD, PLASTIC, CERAMIC, GLASS | Enamel vs Stainless |

**Variant Mismatch Decision:**
- IF Brand matches AND Product type matches BUT variant clearly differs:
  - → Route to **FILTERED OUT**
  - → Reason: "Same product family, variant mismatch: [Supplier variant] vs [Amazon variant]"

**Examples:**
| Supplier | Amazon | Decision | Reason |
|----------|--------|----------|--------|
| ELBOW GREASE EUCALYPTUS | Elbow Grease Lemon Fresh | FILTERED OUT | Variant mismatch: scent |
| MASON CASH BLACK 16CM | Mason Cash Cream 16cm | FILTERED OUT | Variant mismatch: color |
| PYREX AIR FRYER 2L | Pyrex Air Fryer 4L | FILTERED OUT | Variant mismatch: capacity >50% |

---

## 🆕 CATEGORY DEFINITIONS (v4.1 REFINED)

### **VERIFIED (Exact EAN + Passed Pack Check)**
Requirements:
1. Supplier EAN and Amazon EAN are identical AND strictly valid
2. **Pack mismatch check PASSED** (Adjusted Profit > 0 after pack calculation)
3. No variant mismatch detected
4. Default confidence = 95

### **HIGHLY LIKELY (v4.1 STRICT BRAND MATCHING)**
Requirements - ALL must be TRUE:
1. **Brand from KNOWN_BRANDS list appears in BOTH titles** (case-insensitive)
2. **Product type matches** (e.g., both are "trowel", "hammer", "bowl", "candle")
3. **No pack count word mismatch** detected
4. **No variant mismatch** detected (scent, color, size)
5. **Adjusted Profit > £0.10**
6. **Sales > 0**

**If ANY condition fails:**
- If brand matches but pack/variant issue → FILTERED OUT
- If brand does NOT match → NEEDS VERIFICATION (if similarity > 55%) or exclude

**Supplier title starting with INVALID_FIRST_WORDS → Cannot be HIGHLY LIKELY**

### **NEEDS VERIFICATION (v4.1 HIGHLY SELECTIVE)**

**Include ONLY if ALL of the following are TRUE:**
1. **Brand visible in Amazon title** (from KNOWN_BRANDS list) OR Title similarity >= 55%
2. **Product type matches** (same category)
3. **Only 1-2 specific details need confirmation:**
   - Pack count needs verification
   - Variant confirmation needed
   - Size/capacity tolerance check needed
4. **Adjusted Profit > £0.50**
5. **ROI > 15%**

**DO NOT include if:**
- Brand NOT visible in Amazon title AND similarity < 55%
- Product types clearly differ (e.g., "plates" vs "bowl")
- More than 2 details need verification
- Profit margin too thin (< £0.50)
- Adjusted Profit negative (goes to FILTERED OUT)

### **FILTERED OUT (Confirmed Matches - Unprofitable for Audit)**

⚠️ **CRITICAL:** FILTERED OUT contains **CONFIRMED product matches** that cannot be actioned profitably.

**Include in FILTERED OUT when:**
- Match IS confirmed (brand matches, product type matches, possibly even EAN match)
- BUT pack mismatch makes it unprofitable
- OR Adjusted profit becomes negative after pack calculation
- OR Clear variant mismatch with same brand/product family
- OR Size/capacity difference makes it a different SKU

---

## 📂 INPUT FILES

You will be provided with:
1. **Financial Report CSV/XLSX:** Located at [USER WILL SPECIFY PATH]
    * Key columns: EAN, EAN_OnPage (Amazon EAN), ASIN, SupplierTitle, AmazonTitle, SupplierPrice_incVAT, SellingPrice_incVAT, NetProfit, ROI
    * Sales column: Check for `sales_numeric`, `bought_in_past_month`, or `Sales` (use whichever exists; otherwise Sales=0)
    * **IMPORTANT:** Display actual SellingPrice and Sales values from the source data, not hardcoded zeros.

---

## 🎯 ANALYSIS STAGES (Execute in Order)

### **STAGE 1: Data Loading & Initial Cleaning**

```python
import pandas as pd

df = pd.read_csv(INPUT_PATH)  # or pd.read_excel for xlsx

# Clean EAN columns - CRITICAL for accurate matching
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column (check which one exists)
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
elif 'Sales' in df.columns:
    df['sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# 🆕 Handle SellingPrice column properly
if 'SellingPrice_incVAT' in df.columns:
    df['selling_price'] = pd.to_numeric(df['SellingPrice_incVAT'], errors='coerce').fillna(0)
elif 'SellingPrice' in df.columns:
    df['selling_price'] = pd.to_numeric(df['SellingPrice'], errors='coerce').fillna(0)
else:
    df['selling_price'] = 0

# Add RowID for traceability
df['RowID'] = df.index + 1
```

### **STAGE 2: Known Brand Extraction (v4.1 NEW)**

```python
KNOWN_BRANDS = [
    "AMTECH", "MASON CASH", "ROLSON", "KILNER", "DRAPER", "PYREX", "CHEF AID",
    "BLUE CANYON", "ELLIOTT", "FALCON", "BAKER & SALT", "BAKER AND SALT",
    "SCHOTT ZWIESEL", "MARIGOLD", "FAIRY", "DETTOL", "EVERBUILD", "SOUDAL",
    "TIDYZ", "BACOFOIL", "HARRIS", "EXTRASTAR", "GIFTMAKER", "PRIMA", "APOLLO",
    "KILROCK", "PRODEC", "HOUSE MATE", "TALA", "LITTLE TREES", "ELBOW GREASE",
    "PRICE & KENSINGTON", "ULTRATAPE", "FIRE UP", "DOFF", "GEEPAS", "STATUS",
    "ROUNDUP", "SUPERIOR", "FIRST STEPS", "MINKY", "RUSSELL HOBBS", "QUEST",
    "YALE", "VINERS", "MASTERCLASS", "HEM", "AIRWICK", "AIR WICK", "SPONTEX",
    "PASABAHCE", "RCR", "SCHOTT", "DENBY", "HEAT HOLDERS", "KORKEN", "ZEAL",
    "OXO", "JOSEPH JOSEPH", "BRABANTIA", "KENWOOD", "SWAN", "TOWER", "MORPHY RICHARDS",
    "TEFAL", "WILTON", "SABICHI", "DUNLOP", "JML", "BELDRAY", "PROGRESS", "SALTER",
    "PRESTIGE", "STELLAR", "HORWOOD", "RAVENHEAD", "DURALEX", "LUMINARC", "ARC",
    "ARCOROC", "PYREX ESSENTIALS", "MASTER CLASS", "MASTERCLASS", "JUDGE"
]

INVALID_FIRST_WORDS = [
    "MONEY", "HAPPY", "SALT", "LED", "BBQ", "DOOR", "PET", "CAT", "DOG",
    "CANDLE", "MIRROR", "BOTTLE", "BASKET", "GLOVES", "WATCH", "LARGE",
    "SMALL", "PREMIUM", "DELUXE", "CLASSIC", "MODERN", "WOODEN", "METAL",
    "PLASTIC", "STEEL", "GLASS", "CHRISTMAS", "BIRTHDAY", "GARDEN", "KITCHEN",
    "BATHROOM", "BEDROOM", "OUTDOOR", "INDOOR", "BLACK", "WHITE", "BLUE", "RED"
]

def extract_known_brand(title):
    """Extract brand from KNOWN_BRANDS list, return empty string if not found."""
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            return brand
    return ""

def starts_with_invalid_word(title):
    """Check if title starts with an invalid brand word."""
    if pd.isna(title):
        return False
    first_word = str(title).split()[0].upper() if str(title).split() else ""
    return first_word in INVALID_FIRST_WORDS

df['supplier_brand'] = df['SupplierTitle'].apply(extract_known_brand)
df['amazon_brand'] = df['AmazonTitle'].apply(extract_known_brand)
df['brand_match'] = (df['supplier_brand'] != "") & (df['supplier_brand'] == df['amazon_brand'])
df['starts_invalid'] = df['SupplierTitle'].apply(starts_with_invalid_word)
```

### **STAGE 3: Variant Mismatch Detection (v4.1 NEW)**

```python
VARIANT_SCENTS = ["EUCALYPTUS", "LEMON", "LIME", "LAVENDER", "VANILLA", "ORANGE", "FRESH", "CITRUS", "MINT", "ROSE"]
VARIANT_COLORS = ["BLACK", "WHITE", "GREY", "GRAY", "NAVY", "CREAM", "RED", "BLUE", "GREEN", "PINK", "BROWN", "SILVER", "GOLD"]
VARIANT_SIZES = ["SMALL", "MEDIUM", "LARGE", "XL", "XXL", "MINI", "GIANT"]

def detect_variant_mismatch(sup_title, amz_title):
    """Detect if same product family but different variant (scent/color/size)."""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return False, ""
    
    sup_upper = str(sup_title).upper()
    amz_upper = str(amz_title).upper()
    
    # Check scent mismatch
    sup_scents = [s for s in VARIANT_SCENTS if s in sup_upper]
    amz_scents = [s for s in VARIANT_SCENTS if s in amz_upper]
    if sup_scents and amz_scents and set(sup_scents) != set(amz_scents):
        return True, f"Scent mismatch: {sup_scents} vs {amz_scents}"
    
    # Check color mismatch
    sup_colors = [c for c in VARIANT_COLORS if c in sup_upper]
    amz_colors = [c for c in VARIANT_COLORS if c in amz_upper]
    if sup_colors and amz_colors and set(sup_colors) != set(amz_colors):
        return True, f"Color mismatch: {sup_colors} vs {amz_colors}"
    
    # Check size mismatch
    sup_sizes = [s for s in VARIANT_SIZES if s in sup_upper]
    amz_sizes = [s for s in VARIANT_SIZES if s in amz_upper]
    if sup_sizes and amz_sizes and set(sup_sizes) != set(amz_sizes):
        return True, f"Size mismatch: {sup_sizes} vs {amz_sizes}"
    
    return False, ""

# Apply variant mismatch detection
variant_results = df.apply(lambda r: detect_variant_mismatch(r['SupplierTitle'], r['AmazonTitle']), axis=1)
df['variant_mismatch'] = [r[0] for r in variant_results]
df['variant_reason'] = [r[1] for r in variant_results]
```

### **STAGE 4: Pack Size Extraction & Profit Recalculation**

```python
import re

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    # Dimension patterns to IGNORE (not pack counts)
    dimension_pattern = r'\d+\s*x\s*\d+\s*(cm|mm|inch|in|m)\b'
    if re.search(dimension_pattern, title):
        # Check if there's ALSO a pack pattern
        pass  # Continue to check for explicit pack patterns
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'^(\d+)\s*x\s+[a-z]',  # "3 x Product" at start
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'(\d+)\s*bags?\b',
        r'(\d+)\s*containers?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']

def recalculate_profit(row):
    """
    Adjust profit based on quantity ratio.
    If Amazon sells a 6-pack and Supplier sells singles,
    we need to buy 6 units, so: Adjusted_Profit = Original - (Cost * (Ratio - 1))
    """
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)
```

### **STAGE 5: Title Similarity & Categorization**

```python
from difflib import SequenceMatcher

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['confidence'] = (df['title_match'] * 100).astype(int)
```

### **STAGE 6: v4.1 Category Assignment Decision Tree**

```python
def assign_category_v41(row):
    """
    v4.1 Category Assignment with:
    - Pack check before VERIFIED
    - Known brands for HIGHLY LIKELY
    - Variant mismatch detection
    """
    is_exact_ean = row.get('is_exact_ean_strict', False)
    net_profit = float(row['NetProfit']) if pd.notna(row['NetProfit']) else 0
    adjusted_profit = float(row['Adjusted_Profit']) if pd.notna(row['Adjusted_Profit']) else 0
    sales = float(row.get('sales', 0))
    brand_match = row.get('brand_match', False)
    variant_mismatch = row.get('variant_mismatch', False)
    variant_reason = row.get('variant_reason', "")
    title_sim = row.get('title_match', 0)
    starts_invalid = row.get('starts_invalid', False)
    qty_ratio = row.get('Qty_Ratio', 1)
    
    # Check for variant mismatch FIRST
    if variant_mismatch and (brand_match or is_exact_ean):
        return 'FILTERED_OUT', f"Confirmed match; {variant_reason}"
    
    # VERIFIED: Exact EAN + positive adjusted profit + no pack issues
    if is_exact_ean:
        if adjusted_profit <= 0:
            return 'FILTERED_OUT', f"Exact EAN; pack ratio {qty_ratio:.1f}x makes profit negative"
        if net_profit > 0:
            return 'VERIFIED', "Exact EAN match"
        else:
            return 'FILTERED_OUT', "Exact EAN but profit negative"
    
    # HIGHLY LIKELY: Known brand + product match + passes all checks
    if brand_match and not starts_invalid and not variant_mismatch:
        if adjusted_profit <= 0:
            return 'FILTERED_OUT', f"Brand match; adjusted profit negative due to pack"
        if title_sim >= 0.55 and net_profit > 0.10:
            if sales > 0:
                return 'HIGHLY_LIKELY', f"Brand match: {row.get('supplier_brand', '')}"
            else:
                return 'NEEDS_VERIFICATION', f"Brand match but Sales=0; verify demand"
    
    # NEEDS VERIFICATION: Brand visible OR high similarity + positive profit
    if (brand_match or title_sim >= 0.55) and adjusted_profit > 0.50:
        if net_profit > 0:
            return 'NEEDS_VERIFICATION', "Partial match - verify details"
    
    # Check for weak matches that still have brand in Amazon title
    amazon_brand = row.get('amazon_brand', '')
    if amazon_brand and title_sim >= 0.40 and adjusted_profit > 0:
        return 'NEEDS_VERIFICATION', "Brand visible in Amazon; verify product match"
    
    # FILTERED OUT: Negative profit with any match evidence
    if adjusted_profit <= 0 and (brand_match or title_sim >= 0.50):
        return 'FILTERED_OUT', f"Match evidence but profit negative"
    
    # LOW_PRIORITY or OTHER
    if title_sim >= 0.30 and net_profit > 0:
        return 'LOW_PRIORITY', "Weak match evidence"
    
    return 'OTHER', "Insufficient match evidence"
```

---

## 📊 OUTPUT REQUIREMENTS

### **Output File: PHASEA_MANUAL_REPORT_YYYYMMDD.md**

The report must contain:
1. **Summary counts** at the top
2. **VERIFIED** section (sorted by NetProfit descending)
3. **HIGHLY LIKELY** section (sorted by Confidence descending)
4. **NEEDS VERIFICATION** section (sorted by Confidence descending)
5. **FILTERED OUT** section (sorted by NetProfit descending)

---

## 🆕 TABLE SCHEMA (v4.1 - USE THIS EXACT SCHEMA)

| Verdict | Confidence | SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | SupplierPrice | SellingPrice | NetProfit | ROI | Sales | Pack Verdict | Adjusted Profit | Key Match Evidence | Filter Reason |

**Table Formatting Requirements:**
- All tables must be emitted as fixed-width, space-padded tables
- Wrap every table in a fenced code block using triple backticks (```text and ```)
- No tabs. Spaces only.
- 🆕 **SellingPrice must show actual value from source data** (not 0 unless source is 0)
- 🆕 **Sales must show actual value from source data** (not 0 unless source is 0)

**Sorting Requirements (v4.1 NEW):**
- **VERIFIED**: Sort by NetProfit descending (highest profit first)
- **HIGHLY LIKELY**: Sort by Confidence descending (highest match confidence first)
- **NEEDS VERIFICATION**: Sort by Confidence descending (highest match confidence first)
- **FILTERED OUT**: Sort by NetProfit descending

---

## 📊 EXPECTED REPORT DISTRIBUTION (v4.1 GUIDANCE)

| Category | Expected Range | Contents |
|----------|----------------|----------|
| VERIFIED | 15-50 | All exact EAN matches that pass pack check with positive profit |
| HIGHLY LIKELY | 25-50 | Known brand + product matches only (strict) |
| NEEDS VERIFICATION | 80-150 | Only items upgradeable via 1-2 confirmable details |
| FILTERED OUT | 10-50 | **CONFIRMED matches** that are unprofitable due to pack/variant issues |

---

## 📋 REPORT STRUCTURE

```markdown
# PHASEA MANUAL REPORT

**Generated:** YYYY-MM-DD
**Input File:** [path to file]
**Supplier:** [supplier name if known]
**Prompt Version:** v4.1

## Summary Counts
- VERIFIED: X
- HIGHLY LIKELY: Y
- NEEDS VERIFICATION: Z
- FILTERED OUT: W
- TOTAL ANALYZED: N

## VERIFIED (count=X)
*Sorted by NetProfit descending*

[Fixed-width table]

## HIGHLY LIKELY (count=Y)
*Sorted by Confidence descending (highest match confidence first)*

[Fixed-width table]

## NEEDS VERIFICATION (count=Z)
*Sorted by Confidence descending (highest match confidence first)*

[Fixed-width table]

## FILTERED OUT (count=W)
*Sorted by NetProfit descending*

[Fixed-width table]

## Reconciliation
- Total rows in input: N
- Rows categorized: X + Y + Z + W
```

---

*Prompt Version 4.1 - 