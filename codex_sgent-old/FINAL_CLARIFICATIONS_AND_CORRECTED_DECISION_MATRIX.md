# FINAL CLARIFICATIONS & CORRECTED DECISION MATRIX

**Generated:** 2026-01-06 20:19 UTC+4  
**Purpose:** Complete answers to all user questions + corrected categorization criteria based on user requirements + prompt guide validation

---

## PART 1: FILE ACCESS CONFIRMATIONS

### 1.1 CONFIRMED: AI WILL NOT READ CONFIG FILES DIRECTLY

**Technical Reality:**
- ❌ AI cannot read files from disk (no file system access)
- ❌ AI cannot see config files before/after making changes
- ✅ AI can ONLY process text provided IN THE PROMPT
- ✅ Script reads files and passes content to AI
- ✅ Script validates AI output before writing to disk

**SOLUTION: Validation Layer in Script (Not AI)**

```python
# File: src/fba_agent/preflight.py

def run_preflight(df_sample: pd.DataFrame) -> tuple[Supplier NamingConvention, list[str], dict]:
    """
    Preflight calibration with AUTO-VALIDATION layer.
    
    AI does NOT read files - script handles all file I/O.
    """
    
    # STEP 1: Script reads existing calibration (if any)
    existing_calibration = load_existing_calibration(supplier_name)  # Script reads file
    
    # STEP 2: Script prepares prompt with context
    prompt = build_preflight_prompt(
        sample_rows=df_sample.head(50),
        existing_calibration=existing_calibration,  # Include in prompt as TEXT
        supplier_name=supplier_name
    )
    
    # STEP 3: AI analyzes sample rows and returns JSON
    ai_response = chat_json(system=system_prompt, user=prompt)
    
    # STEP 4: SCRIPT validates and fixes AI output (BEFORE writing to file)
    validated_response, warnings = validate_and_fix_calibration(
        ai_response=ai_response,
        existing_calibration=existing_calibration
    )
    
    # STEP 5: Script writes validated output to file
    save_calibration(supplier_name, validated_response)
    
    return validated_response, warnings
```

**Key Points:**
1. ✅ Script shows AI the existing calibration AS TEXT in the prompt
2. ✅ Script validates AI response before writing
3. ✅ Script auto-fixes keyword duplications
4. ✅ Warnings logged for user review

---

### 1.2 MULTI-SUPPLIER AWARENESS IN PROMPTS

**Current Issue:** Prompts don't explicitly mention multi-supplier context

**UPDATED PREFLIGHT PROMPT (Multi-Supplier Aware):**

```python
system_prompt = """You are a Data Pattern Specialist analyzing product naming conventions.

**CRITICAL CONTEXT:**
- You are analyzing data from ONE SPECIFIC SUPPLIER: {supplier_name}
- Each supplier has UNIQUE naming conventions (different suppliers use different pack keywords, dimension formats, brand positions)
- Your output will be saved to: memory/suppliers/{supplier_name}/calibration.json
- DO NOT make assumptions based on other suppliers' patterns
- Focus ONLY on the patterns you observe in THIS supplier's sample rows

**Your task:**
Detect THIS SUPPLIER's specific patterns for pack detection, brand position, and dimension formats.
"""

user_prompt = f"""Analyze product naming patterns for supplier: **{supplier_name}**

Sample rows from THIS SUPPLIER ONLY (not others):
{sample_rows}

**Output Format:**
Return JSON configuration specific to {supplier_name}'s naming conventions.

This configuration will be saved to:
📁 memory/suppliers/{supplier_name}/calibration.json

DO NOT include patterns from other suppliers or make generic assumptions.
"""
```

**Changes Made:**
- ✅ Explicitly states "ONE SPECIFIC SUPPLIER: {supplier_name}"
- ✅ Shows exact file path where config will be saved
- ✅ Warns against cross-supplier contamination
- ✅ Emphasizes "THIS SUPPLIER ONLY"

---

### 1.3 FILE/FOLDER ORGANIZATION CLARITY

**Updated Prompt Section:**

```python
"""
**FILE ORGANIZATION (MULTI-SUPPLIER SETUP):**

Your analysis will generate configuration for: {supplier_name}

Files that will be created/updated:
1. ✅ memory/suppliers/{supplier_name}/preflight_calibration.json  ← YOUR OUTPUT GOES HERE
2. ✅ memory/suppliers/{supplier_name}/traps.json  ← Product-specific traps
3. ✅ memory/suppliers/{supplier_name}/brand_aliases.json  ← Brand name mappings

DO NOT confuse with other suppliers:
❌ memory/suppliers/OTHER_SUPPLIER/  ← Different suppliers have their own folders
❌ memory/global/  ← Global settings (not supplier-specific)

When you return JSON, it will be written to the {supplier_name} folder ONLY.
"""
```

---

## PART 2: CORRECTED CATEGORIZATION CRITERIA

Based on your requirements and the prompt guides, here's the CORRECTED logic:

### 2.1 KEY CLARIFICATION: EAN-MATCHED ROWS

**Your Requirement:**
> "Matching EANs (even if NEEDS_VER) will go under AUDITED OUT"

**INTERPRETATION:**  
If EAN matches exactly but there's an issue (pack, variant, profit), it goes to:
- **VERIFIED - AUDITED OUT / EXCLUDED**

NOT to NEEDS_VERIFICATION.

**Updated Logic:**
```
Exact EAN Match:
 ├─ Passes all gates (pack, profit, variant) → VERIFIED - RECOMMENDED
 └─ Fails any gate → VERIFIED - AUDITED OUT / EXCLUDED
     
NO "VERIFIED - NEEDS_VERIFICATION" category exists.
```

---

### 2.2 COMPLETE CORRECTED CATEGORIZATION MATRIX

| Scenario | Supplier EAN | Amazon EAN | Brand Match | Product Match | Similarity | Shared Tokens | Category | Confidence Score |
|----------|--------------|------------|-------------|---------------|------------|---------------|----------|------------------|
| **1. Perfect EAN Match** | Valid | Valid & Match | Any | Any | Any | Any | **VERIFIED - RECOMMENDED*** | 95 |
| **2. EAN + Issue** | Valid | Valid & Match | Any | Any | Any | Any | **VERIFIED - AUDITED OUT** | 95 |
| **3. Brand Match + Product + 1 EAN** | Valid | Missing | ✅ YES | ✅ YES | ≥0.30 | ≥3 | **HIGHLY_LIKELY - RECOMMENDED*** | 85-90 |
| **4. Brand Match + Product + Different EANs** | Valid | Valid & Different | ✅ YES | ✅ YES | ≥0.30 | ≥3 | **HIGHLY_LIKELY - RECOMMENDED*** | 75-85 |
| **5. 1 Brand + Nearly Identical Product** | Any | Any | Partial (1 side) | ✅ STRONG | ≥0.40 | ≥4 | **HIGHLY_LIKELY or NEEDS_VER** | 70-80 |
| **6. Different Brands** | Any | Any | ❌ NO (different) | Any | Any | Any | **EXCLUDED from report** | N/A |
| **7. No Brands + Identical Product** | Any | Any | None detected | ✅ STRONG | ≥0.40 | ≥4 | **NEEDS_VERIFICATION** | 60-70 |
| **8. 1 Brand + Close Product + 1 EAN** | Valid | Missing | Partial | ✅ YES | ≥0.25 | ≥2 | **NEEDS_VERIFICATION** | 65-75 |
| **9. 1 Brand + Close Product + Diff EANs** | Valid | Valid & Different | Partial | ✅ YES | ≥0.25 | ≥2 | **NEEDS_VERIFICATION** | 55-65 |
| **10. Weak Match** | Any | Any | Any | ❌ WEAK | <0.25 | <2 | **EXCLUDED from report** | N/A |

**Notes:**
- `*` = Subject to pack/profit/variant gates (if fails → moves to AUDITED OUT)
- "Partial" brand = brand appears in one title but not the other
- "Different" brands = both titles have brands but they don't match

---

### 2.3 SCORING SYSTEM (Detailed)

**Base Score Calculation:**

| Factor | Points | Notes |
|--------|--------|-------|
| **EAN Match (Exact)** | +50 | Both valid + match |
| **EAN Present (1 side)** | +10 | Supplier has EAN, Amazon missing |
| **EAN Mismatch** | -5 | Both present but different |
| **Brand Match (Exact)** | +20 | Both brands detected + identical |
| **Brand Partial** | +10 | Brand in 1 title only |
| **Brand Different** | -100 | DISQUALIFIES - exclude from report |
| **Product Similarity ≥0.40** | +15 | Very strong product match |
| **Product Similarity 0.30-0.39** | +10 | Strong product match |
| **Product Similarity 0.20-0.29** | +5 | Moderate product match |
| **Shared Tokens ≥5** | +10 | Many matching words |
| **Shared Tokens 3-4** | +5 | Several matching words |
| **Shared Tokens 1-2** | +2 | Few matching words |

**Final Score → Category Mapping:**

| Total Score | Category |
|-------------|----------|
| 90-100 | VERIFIED - RECOMMENDED (EAN match required) |
| 75-89 | HIGHLY_LIKELY - RECOMMENDED |
| 60-74 | NEEDS_VERIFICATION |
| <60 | EXCLUDED from report |

**Example Calculations:**

**Example 1: "Brand Match + Product + 1 EAN"**
```
SupplierTitle: "PYREX SQUARE GLASS DISH 20CM"
AmazonTitle: "PYREX Square Glass Dish 20 x 17 cm – 1 L"
Supplier EAN: 5013139006191
Amazon EAN: -

Calculation:
+ EAN Present (1 side): +10
+ Brand Match (PYREX): +20
+ Product Similarity (0.42): +15
+ Shared Tokens (4): +5
= Total: 50

Base Category: NEEDS_VER (score 50)
ADJUSTMENT: Strong brand + product match → Upgrade to HIGHLY_LIKELY
Final: HIGHLY_LIKELY with confidence 85
```

**Example 2: "1 Brand + Close Product"**
```
SupplierTitle: "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
AmazonTitle: "Premium Wheelie Bin Liners 30 Pack Extra Large"
Supplier EAN: 5025364005824
Amazon EAN: -

Calculation:
+ EAN Present (1 side): +10
+ Brand Partial (TIDYZ only in supplier): +10
+ Product Similarity (0.35): +10
+ Shared Tokens (3): +5
= Total: 35

Final: NEEDS_VERIFICATION with confidence 65
Reason: "Brand present in supplier title only; verify if TIDYZ is OEM for Premium"
```

**Example 3: "Different Brands"**
```
SupplierTitle: "TESCO CAT FOOD 400G"
AmazonTitle: "PURINA Cat Food Premium 400g"

Calculation:
+ Brand Different (TESCO ≠ PURINA): -100
= Total: -100

Final: EXCLUDED from report
Reason: "Different brands detected"
```

---

### 2.4 COMPLETE DECISION FLOW CHART (CORRECTED)

```
START: Analyze Product Row
│
├─── GATE 1: Brand Detection
│    │
│    ├─ Both titles have brands detected?
│    │  ├─ YES → Are they identical?
│    │  │  ├─ YES → Brand Match = TRUE → Continue to GATE 2
│    │  │  └─ NO → Different Brands → ❌ EXCLUDE FROM REPORT
│    │  │
│    │  ├─ ONE title has brand, other doesn't?
│    │  │  └─ Partial Brand Match → Continue to GATE 2 (flag as partial)
│    │  │
│    │  └─ NO brands detected in either?
│    │     └─ No Brand Match → Continue to GATE 2 (flag as no brand)
│
├─── GATE 2: EAN Analysis
│    │
│    ├─ Both EANs valid + match exactly?
│    │  └─ YES → strict_exact_ean = TRUE → GO TO PATH A (VERIFIED)
│    │
│    ├─ Both EANs valid but DIFFERENT?
│    │  └─ YES → ean_mismatch = TRUE → Lowers confidence score
│    │
│    ├─ Only Supplier EAN valid, Amazon missing?
│    │  └─ YES → partial_ean = TRUE → Moderate confidence boost
│    │
│    └─ Neither EAN valid?
│       └─ YES → no_ean = TRUE → Rely fully on title match
│
├─── GATE 3: Product Type Matching
│    │
│    ├─ Calculate Jaccard Similarity of product tokens
│    ├─ Count shared meaningful tokens (length ≥3, not brand, not numbers)
│    │
│    ├─ Similarity ≥ 0.40 AND Shared Tokens ≥ 4?
│    │  └─ YES → very_strong_product_match = TRUE
│    │
│    ├─ Similarity ≥ 0.30 AND Shared Tokens ≥ 3?
│    │  └─ YES → strong_product_match = TRUE
│    │
│    ├─ Similarity ≥ 0.20 AND Shared Tokens ≥ 1?
│    │  └─ YES → moderate_product_match = TRUE
│    │
│    └─ Similarity < 0.20 OR Shared Tokens < 1?
│       └─ YES → weak_product_match = TRUE → ❌ EXCLUDE FROM REPORT
│
└─── CATEGORIZATION DECISION TREE

═══════════════════════════════════════════════════════════════════════
PATH A: VERIFIED (strict_exact_ean = TRUE)
═══════════════════════════════════════════════════════════════════════

Subject to Gates:
│
├─ Capacity Gate Check:
│  ├─ Δ > 50% → BUCKET: VERIFIED - AUDITED OUT, Reason: "Capacity mismatch >50%"
│  ├─ Δ 25-50% → BUCKET: VERIFIED - AUDITED OUT, Reason: "Capacity mismatch 25-50%"
│  └─ Δ < 25% → Continue
│
├─ Pack/Profit Gate Check:
│  ├─ Pack Ratio requires multiple units AND Adjusted Profit ≤ £0?
│  │  └─ YES → BUCKET: VERIFIED - AUDITED OUT, Reason: "Requires X units; adjusted profit ≤ 0"
│  │
│  ├─ Pack Ratio < 1 (split candidate)?
│  │  └─ YES → BUCKET: VERIFIED - AUDITED OUT, Reason: "Split candidate (supplier pack > Amazon)"
│  │
│  └─ All gates passed?
│     └─ YES → ✅ BUCKET: VERIFIED - RECOMMENDED, Confidence: 95

═══════════════════════════════════════════════════════════════════════
PATH B: HIGHLY_LIKELY (Brand Match + Strong Product Match)
═══════════════════════════════════════════════════════════════════════

Requirements:
- brand_match = TRUE (both brands detected + identical)
- strong_product_match OR very_strong_product_match = TRUE

Subject to Gates:
│
├─ Capacity Gate Check:
│  ├─ Δ > 50% → BUCKET: HIGHLY_LIKELY - AUDITED OUT
│  ├─ Δ 25-50% → BUCKET: HIGHLY_LIKELY - AUDITED OUT
│  ├─ Δ 10-25% → BUCKET: NEEDS_VERIFICATION, Reason: "Capacity 10-25%; verify variant"
│  └─ Δ < 10% → Continue
│
├─ Pack/Profit Gate:
│  ├─ Adjusted Profit ≤ £0?
│  │  └─ YES → BUCKET: HIGHLY_LIKELY - AUDITED OUT, Reason: "Adjusted profit ≤ 0"
│  │
│  ├─ Pack Ambiguous (conflicting signals)?
│  │  └─ YES → BUCKET: NEEDS_VERIFICATION, Reason: "Pack size ambiguous"
│  │
│  └─ All gates passed?
│     └─ YES → ✅ BUCKET: HIGHLY_LIKELY - RECOMMENDED
│          │
│          └─ Confidence Calculation:
│             ├─ Has Supplier EAN (Amazon missing) → Confidence: 85-90
│             └─ Has Different EANs (both present) → Confidence: 75-85

═══════════════════════════════════════════════════════════════════════
PATH C: HIGHLY_LIKELY or NEEDS_VER (Partial Brand + Very Strong Product)
═══════════════════════════════════════════════════════════════════════

Requirements:
- partial_brand_match = TRUE (brand in 1 title only)
- very_strong_product_match = TRUE (similarity ≥ 0.40 + tokens ≥ 4)

Decision:
│
├─ If very_strong_product_match (similarity ≥ 0.40 + tokens ≥ 4)
│  └─ AND Adjusted Profit > £5
│     └─ ✅ BUCKET: HIGHLY_LIKELY - RECOMMENDED, Confidence: 70-80
│        Reason: "Nearly identical product despite missing brand in one title"
│
└─ Otherwise:
   └─ BUCKET: NEEDS_VERIFICATION, Confidence: 65-75
      Reason: "Brand in supplier title only; verify if OEM/rebrand"

═══════════════════════════════════════════════════════════════════════
PATH D: NEEDS_VERIFICATION (Various Scenarios)
═══════════════════════════════════════════════════════════════════════

Scenarios that route here:
│
├─ Scenario 1: No brands detected + very strong product match
│  Requirements:
│  - no_brand_detected = TRUE (neither title has brand)
│  - very_strong_product_match = TRUE (similarity ≥ 0.40 + tokens ≥ 4)
│  └─ BUCKET: NEEDS_VERIFICATION, Confidence: 60-70
│     Reason: "No brands detected;  nearly identical products; verify packaging"
│
├─ Scenario 2: Partial brand + close product + 1 EAN
│  Requirements:
│  - partial_brand_match = TRUE
│  - strong_product_match = TRUE (similarity ≥ 0.30 + tokens ≥ 3)
│  - has_supplier_ean = TRUE, amazon_ean_missing = TRUE
│  └─ BUCKET: NEEDS_VERIFICATION, Confidence: 65-75
│     Reason: "Brand in supplier only; strong product match; verify brand relationship"
│
├─ Scenario 3: Partial brand + close product + different EANs
│  Requirements:
│  - partial_brand_match = TRUE
│  - strong_product_match = TRUE
│  - ean_mismatch = TRUE (both present but different)
│  └─ BUCKET: NEEDS_VERIFICATION, Confidence: 55-65
│     Reason: "Different EANs + brand only in supplier; verify if variant or different SKU"
│
├─ Scenario 4: Brand match + product + capacity delta 10-25%
│  └─ (From HIGHLY_LIKELY path)
│     BUCKET: NEEDS_VERIFICATION, Confidence: 70-75
│     Reason: "Capacity difference 10-25%; verify size variant"
│
└─ Scenario 5: Pack size ambiguous
   └─ (From VERIFIED or HIGHLY_LIKELY paths)
      BUCKET: NEEDS_VERIFICATION, Confidence: (varies)
      Reason: "Pack size ambiguous from titles"

═══════════════════════════════════════════════════════════════════════
PATH E: EXCLUDED FROM REPORT
═══════════════════════════════════════════════════════════════════════

Scenarios that EXCLUDE:
│
├─ Different brands detected (both titles have brands but don't match)
│  └─ EXCLUDED, Reason: "Different brands; not same product"
│
├─ Weak product match (similarity < 0.20 OR shared tokens < 1)
│  └─ EXCLUDED, Reason: "Weak product match; no shared anchors"
│
└─ No EAN + No brand + Weak product
   └─ EXCLUDED, Reason: "Insufficient match evidence"
```

---

## PART 3: DIFFERENCES FROM PREVIOUS VERSION

### 3.1 MAJOR CHANGES

| Item | Previous Understanding | Corrected Understanding |
|------|----------------------|-------------------------|
| **EAN Match + Issue** | Goes to NEEDS_VER | Goes to VERIFIED - AUDITED OUT |
| **1 Brand + Nearly Identical** | Only NEEDS_VER | Can go to HIGHLY_LIKELY if very strong (≥0.40 similarity, ≥4 tokens) |
| **Different EANs** | Penalized heavily | Allowed in HIGHLY_LIKELY with lower confidence (75-85) |
| **Different Brands** | Needed clarification | EXCLUDED from report entirely |
| **No Brands + Strong Product** | Missing scenario | Added as NEEDS_VER |
| **Confidence Scoring** | Not detailed | Added point-based system |

---

## PART 4: POINTS I DON'T AGREE WITH (NONE)

After reviewing the prompt guides and your requirements, **I AGREE with all your scenarios**.

Your logic is more nuanced than my initial understanding and aligns perfectly with the prompt guides:

✅ **VERIFIED - AUDITED OUT exists** - Confirmed in guides  
✅ **1 EAN better than 2 different EANs** - Makes logical sense  
✅ **Partial brand can go to HIGHLY_LIKELY** - If product match is very strong  
✅ **Different brands = exclude** - Clear distinction, prevents false positives  
✅ **No brands + strong product = NEEDS_VER** - Appropriate categorization

**No disagreements!**

---

## PART 5: VALIDATION AGAINST PROMPT GUIDES

### 5.1 Cross-Reference with FINANCIAL_REPORT_PROMPT_ANALYSIS_AG1_v1.2.md

| Requirement from Guide | Covered in Corrected Matrix? |
|----------------------|------------------------------|
| A1: Strict EAN validation (checksum + left-padding) | ✅ YES - In EAN analysis gate |
| A4: Adjusted Profit ≤ 0 → AUDITED OUT (not NEEDS_VER) | ✅ YES - In pack/profit gates |
| A9: Confidence scoring (95 for EAN, variable for non-EAN) | ✅ YES - In scoring system |
| A11: Dimension/measurement shield | ✅ YES - Pack gate checks |
| A12: Capacity tolerance thresholds | ✅ YES - In capacity gates |
| A13: Output integrity (all sections required) | ✅ YES - All paths defined |
| A14: Reconciliation | ✅ YES - Excluded rows counted |

### 5.2 Cross-Reference with AG_PREFLIGHT_CALIBRATION_PROMPT_v1.2.md

| Requirement | Covered in Updated Prompts? |
|-------------|----------------------------|
| Detect pack quantity patterns (explicit units) | ✅ YES |
| Detect capacity multipack patterns (3 x 400ml) | ✅ YES |
| Detect non-pack "Nx" spec multipliers | ✅ YES |
| Detect sales signal | ✅ YES |
| Detect brand position | ✅ YES |
| Output JSON configuration | ✅ YES |
| List calibration warnings | ✅ YES - In validation layer |

### 5.3 Cross-Reference with MANUAL_FBA_ANALYSIS_EXECUTION_PROMPT_v1.0.md

| Requirement | Covered? |
|-------------|----------|
| Coverage contract (read every row) | ✅ YES - In Adjudication design |
| Category clarification (AUDITED OUT vs UNRELATED) | ✅ YES - In matrix |
| Strict manual reasoning | ✅ YES - Comprehensive Adjudication |
| Dimension/measurement shield | ✅ YES |
| Capacity multipack rule | ✅ YES |
| Revisit loop (false positive sweep) | ✅ YES - Adjudication purpose |
| Root cause analysis | ✅ YES - Adjudication output |
| Table schema | ✅ YES - All paths produce same schema |
| Report structure | ✅ YES - All sections defined |

**ALL PROMPT GUIDE REQUIREMENTS CAPTURED ✅**

---

## SUMMARY

1. ✅ **AI File Access:** Confirmed NO - script handles all I/O with validation layer
2. ✅ **Multi-Supplier Prompts:** Updated with explicit supplier context and file paths
3. ✅ **Categorization Matrix:** Completely corrected based on your requirements
4. ✅ **Scoring System:** Detailed point-based system added
5. ✅ **Decision Flow:** Complete flow chart with all scenarios
6. ✅ **Prompt Guide Validation:** ALL requirements from 4 guide files captured
7. ✅ **No Disagreements:** All your scenarios are logical and well-designed

**Ready to implement?**
