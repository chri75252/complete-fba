````markdown
# 🔬 COMPREHENSIVE FBA REPORT ANALYSIS & VALIDATION PROMPT

**Purpose:** This prompt instructs you to conduct an exhaustive, manual analysis of multiple AI-generated FBA (Fulfillment by Amazon) product reports, validate each product categorization against the original source data, reclassify products based on your own independent analysis, and generate a comprehensive validation report with accuracy statistics for each AI model.

**Version:** 1.0  
**Created:** 2025-12-30 (Asia/Dubai)

---

## 📋 YOUR TASK OVERVIEW

You are a **Senior E-Commerce Analyst** tasked with evaluating the accuracy of multiple AI-generated FBA product analysis reports. Your job is to:

1. **Load and understand** the original source dataset
2. **Extract products** from each AI-generated report (organized by folder/model)
3. **Manually analyze** each product row using title comparison, EAN matching, brand detection, and pack size verification
4. **Independently reclassify** each product into the correct category based on YOUR analysis (not the AI's categorization)
5. **Compare** your classifications against what each AI report claimed
6. **Generate** a comprehensive validation report with detailed findings
7. **Calculate and present** accuracy statistics for each AI model/folder

---

## 📂 INPUT FILES

### Source Dataset (Ground Truth Data)
```
```

This Excel file contains the raw product data with columns including:
- `EAN` - Supplier's product EAN/barcode
- `EAN_OnPage` - Amazon's listed EAN (if available)
- `ASIN` - Amazon Standard Identification Number
- `SupplierTitle` - Product title from supplier catalog
- `AmazonTitle` - Product title from Amazon listing
- `SupplierPrice_incVAT` - Supplier's price including VAT
- `SellingPrice_incVAT` - Amazon selling price
- `NetProfit` - Calculated net profit
- `ROI` - Return on investment percentage
- `Sales` or `sales_numeric` or `bought_in_past_month` - Sales volume indicator


---

## 🎯 ANALYSIS METHODOLOGY

### STEP 1: Load Source Data

First, load the source Excel file (`part_N_XXX.xlsx`) and understand its structure:

```python
import pandas as pd

# Load source data
source_df = pd.read_excel('part_N_XXX.xlsx')

# Display column names and sample rows
print(f"Total rows: {len(source_df)}")
print(f"Columns: {list(source_df.columns)}")

# Identify key columns
# - EAN, EAN_OnPage for barcode matching
# - SupplierTitle, AmazonTitle for title comparison
# - NetProfit, ROI, Sales for financial viability
```

### STEP 2: Extract Products from Each AI Report

For each of the  AI-generated reports:

1. **Locate the report file** (usually `PHASEA_MANUAL_REPORT_*.md` in each folder)
2. **Parse the markdown tables** to extract:
   - Row ID (if present, usually in format `[RowID]` or `RowID=X`)
   - Verdict/Category (VERIFIED, HIGHLY LIKELY, NEEDS VERIFICATION, AUDITED OUT)
   - SupplierTitle, AmazonTitle
   - Supplier EAN, Amazon EAN
   - ASIN
   - NetProfit, ROI, Sales
   - Key Match Evidence
   - Filter Reason

3. **Create a structured list** of products per category per report

### STEP 3: Manual Product Analysis Protocol

**For EACH product row extracted from the AI reports, conduct the following INDEPENDENT analysis:**

#### 3.1 EAN Matching Analysis
```
1. Clean both EANs (remove non-digits, handle .0 suffixes)
2. Check if both EANs are present and valid:
   - Valid = digits only, length 8/12/13/14, passes checksum (if applicable)
3. Compare cleaned EANs:
   - EXACT MATCH = Both present, valid, and identical
   - MISMATCH = Both present but different
   - INCOMPLETE = One or both missing/invalid
```

#### 3.2 Brand Matching Analysis
```
EXAMPLE OF KNOWN_BRANDS = [
    "AMTECH", "MASON CASH", "ROLSON", "KILNER", "DRAPER", "PYREX", "CHEF AID",
    "BLUE CANYON", "ELLIOTT", "FALCON", "BAKER & SALT", "SCHOTT ZWIESEL",
    "MARIGOLD", "FAIRY", "DETTOL", "EVERBUILD", "SOUDAL", "TIDYZ", "BACOFOIL",
    "HARRIS", "EXTRASTAR", "GIFTMAKER", "PRIMA", "APOLLO", "KILROCK", "PRODEC",
    "HOUSE MATE", "TALA", "LITTLE TREES", "ELBOW GREASE", "ULTRATAPE", "FIRE UP",
    "DOFF", "GEEPAS", "STATUS", "ROUNDUP", "SUPERIOR", "FIRST STEPS", "MINKY",
    "RUSSELL HOBBS", "QUEST", "YALE", "VINERS", "MASTERCLASS", "HEM", "AIRWICK",
    "AIR WICK", "SPONTEX", "PASABAHCE", "DENBY", "HEAT HOLDERS", "KENWOOD",
    "SWAN", "TOWER", "MORPHY RICHARDS", "TEFAL", "SABICHI", "DUNLOP", "JML",
    "BELDRAY", "PROGRESS", "SALTER", "PRESTIGE", "STELLAR", "JUDGE"
]

1. Scan SupplierTitle for known brand
2. Scan AmazonTitle for same brand
3. Brand Match = Same known brand appears in BOTH titles (case-insensitive)

INVALID FIRST WORDS (Cannot be treated as brands):
"MONEY", "HAPPY", "SALT", "LED", "BBQ", "DOOR", "PET", "CAT", "DOG",
"CANDLE", "MIRROR", "BOTTLE", "BASKET", "GLOVES", "WATCH", "LARGE",
"SMALL", "WOODEN", "METAL", "PLASTIC", "CHRISTMAS", "BIRTHDAY", "GARDEN"
```

#### 3.3 Title Similarity Analysis
```
1. Calculate sequence similarity between SupplierTitle and AmazonTitle
2. Identify matching product type words (e.g., "torch", "bowl", "trowel")
3. Look for shared distinctive keywords

Similarity thresholds:
- >= 55%: Strong similarity
- 40-55%: Moderate similarity
- < 40%: Weak similarity
```

#### 3.4 Pack Size Analysis
```
PACK PATTERNS TO DETECT:
- "Pack of X", "X-pack", "X pack"
- "X pcs", "X pieces"
- "Set of X"
- "X x" at start of title (e.g., "3 x Product")
- Explicit quantity words: "bags", "containers", "rolls"

DIMENSION PATTERNS (NOT PACK COUNTS):
- "X x Y cm/mm/inch/m"
- "XxYxZ" measurements
- Capacity: "Xml", "XL", "Xg", "Xkg"

1. Extract pack count from SupplierTitle
2. Extract pack count from AmazonTitle
3. Calculate pack ratio = Amazon pack / Supplier pack
4. Calculate Adjusted Profit = NetProfit - (PackRatio - 1) × SupplierPrice
```

#### 3.5 Variant Mismatch Detection
```
VARIANT INDICATORS:
- Scents: EUCALYPTUS, LEMON, LIME, LAVENDER, VANILLA, ORANGE, FRESH, CITRUS
- Colors: BLACK, WHITE, GREY, NAVY, CREAM, RED, BLUE, GREEN, PINK, BROWN
- Sizes: SMALL, MEDIUM, LARGE, XL, MINI
- Capacities: Compare L, ML, CC values

If same brand/product but different variant detected:
→ This is a VARIANT MISMATCH (should be AUDITED OUT)
```

### STEP 4: Independent Reclassification

Based on YOUR manual analysis, assign each product to ONE of these categories:

#### **VERIFIED (Your Classification)**
Requirements - ALL must be TRUE:
- ✓ Exact EAN match (both present, valid, identical)
- ✓ Pack ratio = 1 OR Adjusted Profit > 0 after pack calculation
- ✓ No variant mismatch
- ✓ NetProfit > 0

#### **HIGHLY LIKELY (Your Classification)**
Requirements - ALL must be TRUE:
- ✓ Brand from KNOWN_BRANDS appears in BOTH titles
- ✓ Product type matches (same category of item)
- ✓ No pack mismatch OR Adjusted Profit > 0
- ✓ No variant mismatch
- ✓ NetProfit > 0
- ✓ Title similarity >= 55%

#### **NEEDS VERIFICATION (Your Classification)**
Requirements - ALL must be TRUE:
- ✓ Partial match evidence (brand in one title, OR similarity >= 55%, OR same product type)
- ✓ Only 1-2 specific details need confirmation
- ✓ Adjusted Profit > £0.50
- ✓ ROI > 15%

#### **AUDITED OUT (Your Classification)**
Assign here if ANY of these are TRUE:
- Pack mismatch makes Adjusted Profit ≤ 0
- Variant mismatch detected (same product family, different variant)
- NetProfit ≤ 0
- Clear product mismatch (different product types)

#### **OTHER / LOW PRIORITY (Your Classification)**
- Weak match evidence
- No shared brand, low title similarity
- Different product categories

### STEP 5: Comparison Against AI Reports

For each product:
1. Record the AI Report's categorization (what the report claimed)
2. Record YOUR independent categorization (what you determined)
3. Mark as:
   - ✅ **CORRECT** if AI category matches your category
   - ⚠️ **ACCEPTABLE** if AI category is adjacent (e.g., HIGHLY LIKELY vs NEEDS VERIFICATION)
   - ❌ **INCORRECT** if AI category is clearly wrong

---

## 📊 OUTPUT REQUIREMENTS

### OUTPUT 1: Comprehensive Validation Report

Generate a detailed markdown report with the following structure:

```markdown
# FBA REPORT VALIDATION ANALYSIS

**Generated:** [DATE]
**Source Dataset:** part_N_XXX.xlsx ([X] rows)
**Reports Analyzed:** 8 (cli, Codex HIGH, Codex samecha, Codex very high, Gemini, Opus, opus2, webapp gpt)

## Executive Summary

[Brief 3-5 sentence summary of overall findings]

## Methodology

[Explain the analysis approach used]

## Detailed Product Analysis

### VERIFIED Products (All Reports Combined)

For each product claimed as VERIFIED by any report:

| Row ID | SupplierTitle | AmazonTitle | AI Report | AI Category | Your Category | Correct? | Evidence |
|--------|---------------|-------------|-----------|-------------|---------------|----------|----------|
| [ID]   | [title]       | [title]     | [folder]  | VERIFIED    | [your cat]    | ✅/❌     | [why]    |

### HIGHLY LIKELY Products (All Reports Combined)

[Same format as above]

### NEEDS VERIFICATION Products (All Reports Combined)

[Same format as above]

### AUDITED OUT Products (All Reports Combined)

[Same format as above]

## Problem Patterns Identified

### Pattern 1: [Name of Pattern]
- **Frequency:** X occurrences across Y reports
- **Description:** [What the issue is]
- **Example:** [Specific example]
- **Root Cause:** [Why this happens]

[Repeat for each pattern identified]

## Your Ground Truth Classification

### VERIFIED (Your Analysis)
[Table of products YOU classified as VERIFIED with evidence]

### HIGHLY LIKELY (Your Analysis)
[Table of products YOU classified as HIGHLY LIKELY with evidence]

### NEEDS VERIFICATION (Your Analysis)
[Table of products YOU classified as NEEDS VERIFICATION with evidence]

### AUDITED OUT (Your Analysis)
[Table of products YOU classified as AUDITED OUT with evidence]
```

### OUTPUT 2: Model Accuracy Statistics Report (CRITICAL)

**After completing the full analysis**, generate this summary section:

```markdown
## 📈 MODEL ACCURACY STATISTICS ( below is an example, depending on the number of reports) 

### Overall Accuracy by Model/Folder

| Model/Folder | Total Products | Correct | Acceptable | Incorrect | Accuracy % |
|--------------|----------------|---------|------------|-----------|------------|
| cli          | [X]            | [X]     | [X]        | [X]       | [X]%       |
| Codex HIGH   | [X]            | [X]     | [X]        | [X]       | [X]%       |
| Codex samecha| [X]            | [X]     | [X]        | [X]       | [X]%       |
| Codex very high| [X]          | [X]     | [X]        | [X]       | [X]%       |
| Gemini       | [X]            | [X]     | [X]        | [X]       | [X]%       |
| Opus         | [X]            | [X]     | [X]        | [X]       | [X]%       |
| opus2        | [X]            | [X]     | [X]        | [X]       | [X]%       |
| webapp gpt   | [X]            | [X]     | [X]        | [X]       | [X]%       |

### Category-Level Accuracy by Model

#### VERIFIED Category Accuracy

| Model/Folder | Claimed VERIFIED | Actually VERIFIED | Actually HL | Actually NV | Actually FO | Accuracy |
|--------------|------------------|-------------------|-------------|-------------|-------------|----------|
| cli             | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| Codex HIGH      | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| Codex samecha   | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| Codex very high | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| Gemini          | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| Opus            | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| opus2           | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |
| webapp gpt      | [X]              | [X]               | [X]         | [X]         | [X]         | [X]%     |

#### HIGHLY LIKELY Category Accuracy

| Model/Folder | Claimed HL | Actually VERIFIED | Actually HL | Actually NV | Actually FO | Actually OTHER | Accuracy |
|--------------|------------|-------------------|-------------|-------------|-------------|----------------|----------|
| cli             | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex HIGH      | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex samecha   | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex very high | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Gemini          | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Opus            | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| opus2           | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| webapp gpt      | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |

#### NEEDS VERIFICATION Category Accuracy

| Model/Folder | Claimed NV | Actually VERIFIED | Actually HL | Actually NV | Actually FO | Actually OTHER | Accuracy |
|--------------|------------|-------------------|-------------|-------------|-------------|----------------|----------|
| cli             | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex HIGH      | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex samecha   | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Codex very high | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Gemini          | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| Opus            | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| opus2           | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |
| webapp gpt      | [X]        | [X]               | [X]         | [X]         | [X]         | [X]            | [X]%     |

#### AUDITED OUT Category Accuracy

| Model/Folder | Claimed FO | Actually FO | Should be Other Category | Accuracy |
|--------------|------------|-------------|--------------------------|----------|
| cli             | [X]        | [X]         | [X]                      | [X]%     |
| Codex HIGH      | [X]        | [X]         | [X]                      | [X]%     |
| Codex samecha   | [X]        | [X]         | [X]                      | [X]%     |
| Codex very high | [X]        | [X]         | [X]                      | [X]%     |
| Gemini          | [X]        | [X]         | [X]                      | [X]%     |
| Opus            | [X]        | [X]         | [X]                      | [X]%     |
| opus2           | [X]        | [X]         | [X]                      | [X]%     |
| webapp gpt      | [X]        | [X]         | [X]                      | [X]%     |

### Key Findings by Model

#### cli
- **Strengths:** [What this model does well]
- **Weaknesses:** [Where this model fails]
- **Common Errors:** [Specific error patterns]

#### Codex HIGH
- **Strengths:** [...]
- **Weaknesses:** [...]
- **Common Errors:** [...]

[Continue for each model/folder]

### Ranking of Models by Accuracy

| Rank | Model/Folder | Overall Accuracy | VERIFIED Acc | HIGHLY LIKELY Acc | NEEDS VERIF Acc |
|------|--------------|------------------|--------------|-------------------|-----------------|
| 1    | [Best]       | [X]%             | [X]%         | [X]%              | [X]%            |
| 2    | [...]        | [...]            | [...]        | [...]             | [...]           |
| ...  | [...]        | [...]            | [...]        | [...]             | [...]           |
| 8    | [Worst]      | [X]%             | [X]%         | [X]%              | [X]%            |

### Recommendations

Based on the analysis, the following recommendations are made:

1. **Best Performing Model:** [folder name] with [X]% accuracy
2. **Most Reliable for VERIFIED:** [folder name]
3. **Most Reliable for HIGHLY LIKELY:** [folder name]
4. **Areas Needing Improvement:** [specific issues across models]
```

---

## ⚠️ CRITICAL INSTRUCTIONS

### DO's:
1. ✅ **Analyze EVERY product** from every report - do not sample or skip
2. ✅ **Use YOUR OWN judgment** based on the analysis methodology - do not trust the AI reports' categorizations
3. ✅ **Be thorough with title analysis** - read titles character by character, identify brands, product types, dimensions
4. ✅ **Calculate financial impact** - pack mismatches can make profitable products unprofitable
5. ✅ **Document your reasoning** - for each reclassification, explain WHY
6. ✅ **Use folder names** when referencing reports (e.g., "Opus", "Codex HIGH", not generic names)
7. ✅ **Cross-reference with source data** - verify values against the original `part_30_dec.xlsx`

### DON'Ts:
1. ❌ **Do NOT trust the AI reports' categorizations** - that's what you're validating
2. ❌ **Do NOT skip the manual title analysis** - automation errors are what you're catching
3. ❌ **Do NOT confuse dimensions with pack counts** - "30x20cm" is a size, not 600 units
4. ❌ **Do NOT accept generic first words as brands** - "MONEY", "HAPPY", "SALT" are not brands
5. ❌ **Do NOT mark variant mismatches as valid matches** - Eucalyptus ≠ Lemon, even if same brand

---

## 📝 EXAMPLE MANUAL ANALYSIS

**Product Row from AI Report:**
```
| HIGHLY LIKELY | 85 | ELBOW GREASE EUCALYPTUS 750ML | Elbow Grease Lemon Fresh All Purpose 750ml | B0CCJS5GKB | Brand match |
```

**Your Manual Analysis:**

1. **EAN Check:** [Examine if EANs match]

2. **Brand Check:** 
   - Supplier brand: "ELBOW GREASE" ✓ (known brand)
   - Amazon brand: "Elbow Grease" ✓ (matches)
   - Brand match: YES ✓

3. **Product Type Check:**
   - Both are: "All Purpose Cleaner" ✓
   - Product match: YES ✓

4. **Variant Check:**
   - Supplier variant: "EUCALYPTUS"
   - Amazon variant: "LEMON FRESH"
   - **VARIANT MISMATCH DETECTED** ❌

5. **Your Classification:** **AUDITED OUT** (not HIGHLY LIKELY)
   - Reason: Same brand, same product type, but DIFFERENT SCENT VARIANT

6. **AI Report Accuracy:** ❌ INCORRECT
   - AI claimed: HIGHLY LIKELY
   - Correct answer: AUDITED OUT

---

## 🚀 EXECUTION CHECKLIST

Before submitting your analysis, verify:

- [ ] Loaded and reviewed source dataset (`part_30_dec.xlsx`)
- [ ] Extracted products from all 8 AI report folders
- [ ] Manually analyzed each product using the methodology
- [ ] Independently reclassified each product
- [ ] Compared AI classifications vs your classifications
- [ ] Generated comprehensive validation report with all sections
- [ ] Calculated accuracy statistics for each model/folder
- [ ] Used folder names (cli, Codex HIGH, etc.) when referencing reports
- [ ] Included ranking of models by accuracy
- [ ] Provided specific recommendations

---

## 📤 FINAL DELIVERABLES

1. **`COMPREHENSIVE_VALIDATION_REPORT_[DATE].md`**
   - Complete analysis of all products from all reports
   - Your independent classifications with evidence
   - Problem patterns identified

2. **Model Accuracy Statistics Section** (within the same report)
   - Overall accuracy by model/folder
   - Category-level accuracy breakdown
   - Ranking of models
   - Recommendations

---

*End of Prompt*
*Version 1.0 - Comprehensive FBA Report Validation*
````
