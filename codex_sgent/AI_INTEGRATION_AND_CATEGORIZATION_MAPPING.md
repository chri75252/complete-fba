# AI INTEGRATION POINTS & CATEGORIZATION CRITERIA MAPPING

**Generated:** 2026-01-06 09:12 UTC+4  
**Purpose:** Complete mapping of all AI logic points, integration targets, and product categorization rules

---

## PART 1: AI LOGIC SCRIPTS & INTEGRATION TARGETS

### Overview: Where AI is Used in the Workflow

The agent uses AI (LLM API calls) in **3 main steps**:
1. **Preflight Calibration** - Analyzes sample data to detect patterns
2. **Adjudication** - Reviews borderline cases
3. **Critique** - Evaluates overall report quality

---

### AI INTEGRATION POINT #1: PREFLIGHT CALIBRATION

#### SOURCE SCRIPT (Contains AI Logic):
**File:** `src/fba_agent/preflight.py`  
**Function:** `run_preflight()`  
**Lines:** 41-64

**What It Does:**
- Samples 50 rows from input data
- Sends to AI with prompt asking to analyze patterns
- AI returns JSON configuration

**AI Prompt (Lines 52-60):**
```python
user = (
    "Analyze these rows and output a JSON object with keys:\\n"
    "explicit_units (list of strings), "  # Pack keywords like "PK", "PACK"
    "dimension_shield_keywords (list of strings), "  # Measurement words like "CM", "MM"
    "spec_x_shield_keywords (list of strings), "  # Non-pack multipliers like "zoom"
    "brand_position ('start' or 'mixed'), "
    "sales_column (string), "
    ...
)
```

**AI Returns:**
```json
{
  "explicit_units": ["ML", "CM", "PK", "PACK", ...],
  "dimension_shield_keywords": ["in", "cm", "mm", ...],
  "spec_x_shield_keywords": ["zoom", "X", "x", ...],
  "brand_position": "start",
  "sales_column": "Sales",
  "allow_trailing_number_as_qty": true,
  "leading_multiplier_check": true,
  "capacity_pattern_as_rsu": true,
  "table_pipe_sanitization": true
}
```

#### TARGET FILES (Where AI Output is Integrated):

**Target #1:** In-memory `SupplierNamingConvention` object  
**File:** `src/fba_agent/types.py` (SupplierNamingConvention class)  
**Integration:** Lines 66-67 in `preflight.py`:
```python
merged = heuristic_naming.__dict__.copy()
merged.update(obj)  # ← AI response merged here
naming = SupplierNamingConvention(**merged)
```

**Target #2:** Persisted to disk  
**File:** `memory/suppliers/{supplier_name}/preflight_calibration.json`  
**Purpose:** Save AI-detected configuration for future runs  
**Format:**
```json
{
  "explicit_units": [...],
  "dimension_shield_keywords": [...],
  "spec_x_shield_keywords": [...],
  ...
}
```

**Target #3:** Merged configuration  
**File:** `{run_dir}/merged_calibration.json` (output file)  
**Purpose:** Final merged config used for this run (combines AI + memory + global traps)  
**Integration:** In `src/fba_agent/memory_store.py` - `merge_calibration()` function

**Target #4:** Pack detection logic  
**File:** `src/fba_agent/pack.py`  
**Function:** `extract_pack_info()`  
**Usage:** Lines read `config.naming.dimension_shield_keywords` to know which words to SKIP when parsing pack quantities

**ISSUE FOUND HERE:** AI puts keywords in BOTH `explicit_units` AND `dimension_shield_keywords`, causing pack detection to ignore valid pack keywords.

---

### AI INTEGRATION POINT #2: ADJUDICATION

#### SOURCE SCRIPT (Contains AI Logic):
**File:** `src/fba_agent/adjudication.py`  
**Function:** `run_adjudication_single()`  
**Lines:** 170-208

**What It Does:**
- Takes a single product row (from NEEDS_VERIFICATION bucket)
- Sends product details to AI
- AI decides if it should be upgraded to HIGHLY_LIKELY or VERIFIED

**AI Prompt (Lines 133-163):**
```python
system = (
    "You are an expert FBA product analyst. Review this product match and "
    "determine the most appropriate category: VERIFIED, HIGHLY_LIKELY, "
    "NEEDS_VERIFICATION, or FILTERED_OUT.\\n\\n"
    
    "YOU MUST BE DECISIVE. For items with profit > £1 and reasonable "
    "brand/product match, default to HIGHLY_LIKELY unless there is clear "
    "evidence of a problem."
)

user = (
    f"Row ID: {row_data['row_id']}\\n"
    f"Supplier Title: {row_data['supplier_title']}\\n"
    f"Amazon Title: {row_data['amazon_title']}\\n"
    f"Similarity: {row_data.get('similarity', 0)}\\n"
    f"Net Profit: £{row_data.get('net_profit', 0)}\\n"
    f"Current Bucket: {row_data.get('bucket')}\\n"
    ...
    "Provide your recommendation."
)
```

**AI Returns:**
```json
{
  "row_id": 269,
  "recommended_bucket": "HIGHLY_LIKELY",
  "confidence": 85,
  "reasoning": "Strong product type match (cat litter) with multiple shared descriptive tokens..."
}
```

#### TARGET FILES (Where AI Output SHOULD BE Integrated):

**Target #1:** Main analysis ledger (IN-MEMORY)  
**File:** DataFrame `ledger` in `src/fba_agent/iteration.py`  
**Columns to Update:**
- `bucket` - Change from "NEEDS_VERIFICATION" to "HIGHLY_LIKELY"
- `track` - Change from "NEEDS_VERIFICATION" to "HIGHLY_LIKELY"  
- `confidence` - Update to AI-provided value (e.g., 85)

**Integration Point:** Line 244 in `src/fba_agent/iteration.py`  
**Current Code:**
```python
adjudication_results = run_adjudication(candidates, provider)
# ← NOTHING HAPPENS HERE - RESULTS STORED BUT NOT APPLIED
```

**ISSUE FOUND HERE:** AI provides recommendations but NO CODE applies them to the ledger!

**Target #2:** Iteration details log  
**File:** `{run_dir}/iteration_details.json` (output file)  
**Purpose:** Record what AI recommended  
**Integration:** Working - results are logged in iteration_details under `adjudication_results`

**Target #3:** SHOULD update final report  
**File:** `{run_dir}/PHASEA_MANUAL_REPORT_{date}.md`  
**Expected:** Rows upgraded by AI appear in HIGHLY_LIKELY section  
**Actual:** They stay in NEEDS_VERIFICATION because ledger wasn't updated

---

### AI INTEGRATION POINT #3: CRITIQUE

#### SOURCE SCRIPT (Contains AI Logic):
**File:** `src/fba_agent/critique.py`  
**Function:** `run_critique()`  
**Lines:** 170-240

**What It Does:**
- Reviews the entire analysis results (bucket counts, anomalies)
- AI evaluates if results are reasonable
- AI can propose configuration changes or flag issues

**AI Prompt (Lines 184-215):**
```python
system = (
    "You are a quality assurance specialist for FBA product analysis. "
    "Review the analysis results and identify any issues, anomalies, or "
    "recommended improvements."
)

user = (
    f"Bucket Counts:\\n"
    f"- VERIFIED: {bucket_counts['VERIFIED']}\\n"
    f"- HIGHLY_LIKELY: {bucket_counts['HIGHLY_LIKELY']}\\n"
    f"- NEEDS_VERIFICATION: {bucket_counts['NEEDS_VERIFICATION']}\\n"
    f"- FILTERED_OUT: {bucket_counts['FILTERED_OUT']}\\n\\n"
    
    f"Anomalies Detected: {len(anomaly_summary.get('profit_outliers', []))}\\n"
    ...
    "Provide your critique and recommendations."
)
```

**AI Returns:**
```json
{
  "recommended_action": "apply_and_rerun",  // or "finalize" or "block"
  "high_severity_issues": [
    {
      "issue": "Too many high-profit items in FILTERED_OUT",
      "severity": "high",
      "affected_count": 150
    }
  ],
  "proposed_changes": [
    {
      "change_type": "config_adjustment",
      "target": "title_match_threshold",
      "current_value": 0.20,
      "proposed_value": 0.15,
      "reasoning": "Lower threshold may rescue valid matches"
    }
  ]
}
```

#### TARGET FILES (Where AI Output SHOULD BE Integrated):

**Target #1:** Configuration adjustments (IN-MEMORY)  
**File:** `current_config` in `src/fba_agent/iteration.py`  
**Integration Point:** Lines 269-274 in `iteration.py`  
**Code:**
```python
if critique and critique.proposed_changes:
    current_config, current_brand_aliases, logs = apply_adjustments(
        current_config, critique.proposed_changes, current_brand_aliases
    )
    adjustments_applied = count_applied(logs)
```

**What It Does:** Applies AI-suggested config changes (e.g., lower threshold from 0.20 to 0.15)

**Target #2:** Iteration decision  
**File:** `iteration.py` logic  
**Lines:** 74-75  
**Code:**
```python
if critique_action == "block":
    return False, "Critique blocked — manual review required"
```

**ISSUE FOUND HERE:** When critique fails, it returns "block" action, preventing iteration 2 from running.

**Target #3:** Run summary  
**File:** `{run_dir}/run_summary.json`  
**Purpose:** Record critique decision  
**Format:**
```json
{
  "critique_summary": {
    "recommended_action": "block",
    "high_severity_issues": 1,
    "proposed_changes": 0,
    "overall_assessment": "Critique could not be completed"
  }
}
```

---

## PART 2: ALL PRODUCT CATEGORIZATION CRITERIA

### Complete Decision Tree for Product Rows

Every product row goes through this logic (in `src/fba_agent/analysis.py`, lines 90-196):

---

### CATEGORY 1: VERIFIED - RECOMMENDED

**Criteria:**
1. ✅ **Exact EAN Match:** Supplier EAN == Amazon EAN (both valid, checksums pass)
2. ✅ **No Major Issues:**
   - Capacity difference ≤ 25% (≤ 10% is ideal, 10-25% goes to NEEDS_VER)
   - Adjusted profit > £0 after pack recalculation
   - Pack verdict is NOT highly ambiguous

**Examples:**
```
Row: PAN AROMA JAR CANDLE 85GM SALTED CARAMEL
Supplier EAN: 5053249248356
Amazon EAN: 5053249248356  ← MATCH
Amazon Title: Pan Aroma Orange Decorative Holder & Scented Candle, Salted Caramel, 85G
Pack: 1:1 Match
Adjusted Profit: £2.73
→ VERIFIED - RECOMMENDED
```

**Code Location:** Lines 140-160 in `analysis.py`

---

### CATEGORY 2: VERIFIED - FILTERED OUT / EXCLUDED

**Criteria:**
1. ✅ **Exact EAN Match** (same as above)
2. ❌ **BUT Has Disqualifying Issue:**
   - **Capacity mismatch ≥ 25%** (e.g., 500ml vs 750ml)
   - **Adjusted profit ≤ £0** after pack recalculation (e.g., need to buy 3 packs but profit becomes negative)
   - **Pack is split candidate** (ratio < 1, supplier pack > Amazon pack)

**Examples:**
```
Row: DRAPER HSS DRILL BIT 1.5 MM (single bit)
Supplier EAN: 5059482059971
Amazon EAN: 5059482059971  ← MATCH
Amazon Title: Draper 18551 Combined HSS and Masonry Drill Bit Set, Blue, 17 Pcs
Pack Verdict: BUNDLE (17.00x) - requires 17 supplier units
Original Profit: £5.16
Adjusted Profit: £-6.75 (£5.16 - 17×£0.74 = negative)
→ VERIFIED - FILTERED OUT
Filter Reason: "Adjusted profit <= 0 after pack adjustment"
```

**Code Location:** Lines 146-151 in `analysis.py`

---

### CATEGORY 3: HIGHLY LIKELY - RECOMMENDED

**Criteria:**
1. ✅ **Confirmed Match** (NO exact EAN, but strong title match):
   - **Brand match:** Brand detected in both titles and they match
   - **Product type match:** Similarity ≥ threshold (default 0.20) AND at least 1 shared product token
   
   OR (NEW - based on reference report):
   - **Very strong product match:** Similarity ≥ 0.30 AND ≥ 3 shared product tokens (even without brand match)

2. ✅ **No Major Issues:**
   - Capacity difference ≤ 25%
   - Adjusted profit > £0
   - Pack is NOT highly ambiguous

**Examples:**

**Example A (Brand + Product Match):**
```
Row: PRIMA HEART SHAPED BAKE PAN 23CM
Supplier Title: "PRIMA HEART SHAPED BAKE PAN 23CM"
Amazon Title: "Prima Set Of 2 Heart Shaped Cake Tins..."

Brand: PRIMA (matches)
Product Tokens: HEART, SHAPED, PAN matches HEART, SHAPED, CAKE
Similarity: 0.42
Pack: 1:1 Match
Adjusted Profit: £1.94
→ HIGHLY_LIKELY - RECOMMENDED
Evidence: "Brand match: PRIMA; anchors: HEART, SHAPED, PAN"
```

**Example B (Strong Product Match, NO Brand Match):**
```
Row: WORLD OF PETS CAT LITTER SCENTED 3LT
Supplier Brand: "WORLD OF PETS"
Amazon Title: "World's Best Cat Litter 28lb (12.7kg) Lavender Scented"
Amazon Brand: "World's Best"

Brand Match: ❌ NO (different brands)
Product Tokens Shared: CAT, LITTER, SCENTED (3 tokens)
Similarity: 0.38
Pack: 1:1 Match
Adjusted Profit: £16.14
→ HIGHLY LIKELY - RECOMMENDED (due to strong product match)
Evidence: "WORLD, CAT, LITTER, SCENTED"
```

**Code Location:** Lines 161-177 in `analysis.py`

---

### CATEGORY 4: HIGHLY LIKELY - FILTERED OUT / EXCLUDED

**Criteria:**
1. ✅ **Confirmed Match** (same as Category 3)
2. ❌ **BUT Has Disqualifying Issue:**
   - Capacity mismatch ≥ 25%
   - Adjusted profit ≤ £0 after pack recalculation

**Examples:**
```
Row: DRAPER HSS DRILL BIT 1.5 MM (matched by brand/product but wrong pack)
Supplier Title: "DRAPER HSS DRILL BIT 1.5 MM"
Amazon Title: "Draper 18551 Combined HSS and Masonry Drill Bit Set, Blue, 17 Pcs"

Brand Match: ✅ YES (DRAPER)
Product Match: ✅ YES (DRILL, BIT, HSS)
Pack Verdict: BUNDLE (17.00x)
Original Profit: £5.16
Adjusted Profit: £-6.75
→ HIGHLY LIKELY - FILTERED OUT
Filter Reason: "Adjusted profit <= 0 after pack adjustment"
```

**Code Location:** Lines 162-171 in `analysis.py`

---

### CATEGORY 5: NEEDS VERIFICATION

**Criteria:**
1. ✅ **Confirmed Match** (EAN or brand/product)
2. ⚠️ **BUT Has Uncertainty:**
   - **Pack size ambiguous** from titles (conflicting numbers, unclear if multipack)
   - **Capacity difference 10-25%** (e.g., 500ml vs 580ml - borderline)
   - **Split candidate** (supplier pack > Amazon pack, ratio < 1)

**OR:**

3. ⚠️ **Borderline Match (per your requirements):**
   - **No brands detected** in either title BUT strong product match
   - **Brand in one title only** (missing in other) BUT strong product match
   - Product match is reasonable but not strong enough for HIGHLY_LIKELY

**Examples:**

**Example A (Pack Ambiguous):**
```
Row: WORLD OF PETS CAT LITTER SCENTED 3LT
Supplier Title: "WORLD OF PETS CAT LITTER SCENTED 3LT"
Amazon Title: "World's Best Cat Litter 28lb (12.7kg) Lavender Scented"

EAN Match: ❌ NO (Amazon EAN missing)
Brand Match: ❌ NO (different brands)
Product Match: ✅ STRONG (CAT, LITTER, SCENTED)
Pack: Conflicting info (3L vs 28lb)
→ NEEDS_VERIFICATION
Filter Reason: "Pack size ambiguous from titles"
```

**Example B (No Brands Detected):**
```
Row: CAT LITTER SCENTED 3L
Supplier Title: "CAT LITTER SCENTED 3L"
Amazon Title: "Premium Cat Litter Lavender Scent 28lb"

Brand Detected: ❌ NO (neither title has clear brand)
Product Match: ✅ YES (CAT, LITTER)
→ NEEDS_VERIFICATION
Filter Reason: "No brands detected; verify product manually"
```

**Example C (Brand in One Title Only):**
```
Row: TIDYZ WHEELY BIN LINERS 5 BAGS 300L
Supplier Title: "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
Amazon Title: "Premium Wheelie Bin Liners 30 Pack Extra Large"

Supplier Brand: ✅ "TIDYZ"
Amazon Brand: ❌ NO (generic description)
Product Match: ✅ STRONG (BIN, LINERS, WHEELIE)
→ NEEDS_VERIFICATION
Filter Reason: "Brand present in supplier title but not Amazon; verify packaging"
```

**Code Location:** Lines 153-157, 164-165, 172-174 in `analysis.py`

---

### CATEGORY 6: FILTERED_OUT (Unrelated / Not Included)

**Criteria:**
1. ❌ **NOT a Confirmed Match:**
   - No EAN match
   - No brand match (or different brands detected)
   - Weak product match (similarity < threshold OR < 1 shared token)

2. **Special Cases:**
   - **Different brands in both titles** → EXCLUDE (per your requirement)
   - Very low similarity score
   - Product type completely different

**Examples:**

**Example A (Different Brands):**
```
Row: TESCO CAT FOOD 400G
Supplier Title: "TESCO CAT FOOD 400G"
Amazon Title: "PURINA Cat Food Premium 400g"

Supplier Brand: "TESCO"
Amazon Brand: "PURINA"
Brands Match: ❌ NO (different brands)
→ FILTERED_OUT (UNRELATED)
include_in_tables: false  ← NOT SHOWN IN REPORT
Filter Reason: "Different brands detected"
```

**Example B (Weak Product Match):**
```
Row: PLASTIC TRAY
Supplier Title: "PLASTIC TRAY 30CM"
Amazon Title: "Garden Tool Set With Tray"

Product Match: ❌ WEAK (only "TRAY" shared, different contexts)
Similarity: 0.08 (very low)
→ FILTERED_OUT (UNRELATED)
include_in_tables: false
Filter Reason: "Weak product match; no brand anchor"
```

**Code Location:** Lines 178-183 in `analysis.py`

---

## PART 3: STABLE KEY CLARIFICATION

### CONFIRMATION: One Stable Key Per Product Row

**YES - You are correct!**

Each **product row** gets ONE stable key, not one per column.

**Example:**
```
Product Row 1:
- row_id: 1
- supplier_title: "PAN AROMA CANDLE 85GM SALTED CARAMEL"
- amazon_title: "Pan Aroma Orange Decorative Holder & Scented Candle..."
- supplier_ean: "5053249248356"
- asin: "B09KCLYC1D"
- stable_key: "a3f4b2c1d5e6..."  ← ONE KEY FOR ENTIRE ROW

Product Row 2:
- row_id: 2
- supplier_title: "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
- amazon_title: "Tidyz 30 Extra Large Wheelie Bin Liners..."
- supplier_ean: "5025364005824"
- asin: "B07MGLHMWY"
- stable_key: "b7e2a9f3c4d1..."  ← ONE KEY FOR ENTIRE ROW
```

**How It's Generated:**

Primary strategy:
```python
stable_key = sha256(SupplierURL + ASIN)[:16]
```

Fallback (if no URL):
```python
stable_key = sha256(EAN + ASIN + SupplierTitle[:50] + AmazonTitle[:50])[:16]
```

**Purpose:**
Track the same product across different runs to detect if it was reclassified.

---

## PART 4: FALLBACK REGRESSION DETECTION (Manual Comparison)

### If Stable Key Fix Fails - Manual Comparison Instructions

**Add to Critique Prompt** (in `src/fba_agent/critique.py`):

```python
system = (
    "You are a quality assurance specialist for FBA product analysis.\\n\\n"
    
    "**REGRESSION DETECTION:**\\n"
    "If a previous report is provided, compare the current report against it "
    "to identify if any product rows were:\\n"
    "1. **REMOVED** - Present in previous report but missing in current\\n"
    "2. **ADDED** - New in current report, not in previous\\n"
    "3. **RECATEGORIZED** - Moved between buckets (e.g., VERIFIED → FILTERED_OUT)\\n\\n"
    
    "**IMPORTANT:** Not all regressions are bad!\\n"
    "- If current report has FEWER items, it may mean the script was previously "
    "misconfigured and incorrectly included items that should have been filtered.\\n"
    "- If items moved from VERIFIED to FILTERED_OUT due to pack recalculation "
    "(negative profit), this is CORRECT behavior.\\n"
    "- Only flag as HIGH SEVERITY if clearly valid products were incorrectly excluded.\\n\\n"
    
    "**COMPARISON METHOD:**\\n"
    "Match products between reports using:\\n"
    "- Primary: Supplier Title + Amazon Title + EAN (if available)\\n"
    "- Fallback: Supplier Title + ASIN\\n"
    "Do NOT use row_id (it can change between runs).\\n"
)

user = (
    f"Current Report Bucket Counts:\\n{current_counts}\\n\\n"
    
    # If previous report provided
    f"Previous Report Bucket Counts:\\n{previous_counts}\\n\\n"
    
    f"TASK: Compare these reports and identify:\\n"
    f"1. Products removed from good buckets (VERIFIED/HIGHLY_LIKELY)\\n"
    f"2. Products added to good buckets\\n"
    f"3. Products that changed categories\\n"
    f"4. Whether these changes are legitimate improvements or regressions\\n"
)
```

**Add Comparison Data to User Prompt:**

```python
# In critique.py, prepare comparison data
if previous_report_path:
    previous_products = extract_products_from_report(previous_report_path)
    current_products = extract_products_from_ledger(ledger)
    
    comparison = {
        "removed_good_items": [],  # Was VERIFIED/HIGHLY_LIKELY, now missing
        "added_good_items": [],    # New VERIFIED/HIGHLY_LIKELY
        "downgraded_items": [],    # VERIFIED/HIGHLY_LIKELY → NEEDS_VER/FILTERED_OUT
        "upgraded_items": []       # NEEDS_VER/FILTERED_OUT → VERIFIED/HIGHLY_LIKELY
    }
    
    # Match products
    for prev_prod in previous_products:
        match_key = (prev_prod['supplier_title'], prev_prod['amazon_title'], prev_prod.get('ean'))
        current_prod = find_product(current_products, match_key)
        
        if not current_prod:
            if prev_prod['bucket'] in ['VERIFIED', 'HIGHLY_LIKELY']:
                comparison['removed_good_items'].append(prev_prod)
        elif current_prod['bucket'] != prev_prod['bucket']:
            if is_downgrade(prev_prod['bucket'], current_prod['bucket']):
                comparison['downgraded_items'].append({
                    'product': prev_prod,
                    'was': prev_prod['bucket'],
                    'now': current_prod['bucket']
                })
    
    # Include in critique prompt
    user += f"\\nComparison Data:\\n{json.dumps(comparison, indent=2)}"
```

---

## SUMMARY TABLE: AI Integration Points

| # | AI Step | Source Script | AI Prompt | AI Returns | Target Integration | Status |
|---|---------|---------------|-----------|------------|-------------------|--------|
| 1 | **Preflight** | `preflight.py` | "Analyze rows, output JSON config" | Pack keywords, shields, brand position | `merged_calibration.json`, `pack.py` config | ⚠️ AI duplicates keywords |
| 2 | **Adjudication** | `adjudication.py` | "Review product match, recommend bucket" | {row_id, recommended_bucket, confidence} | **MISSING:** Should update `ledger` DataFrame | ❌ Results ignored |
| 3 | **Critique** | `critique.py` | "Review analysis quality, propose improvements" | {recommended_action, issues, proposed_changes} | `current_config` updates, iteration decision | ⚠️ Fails and blocks iteration 2 |

---

**Files created:**
- `codex sgent/AI_INTEGRATION_AND_CATEGORIZATION_MAPPING.md`

This complete mapping shows all AI touchpoints and where issues occur!
