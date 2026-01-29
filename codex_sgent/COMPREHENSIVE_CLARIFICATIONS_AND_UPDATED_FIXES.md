# COMPREHENSIVE CLARIFICATIONS & UPDATED FIXES PLAN

**Generated:** 2026-01-06 19:51 UTC+4  
**Purpose:** Complete, thorough answers to all user questions with NO MISSING DETAILS

---

## TABLE OF CONTENTS

1. [Preflight Calibration - Complete Explanation](#1-preflight-calibration)
2. [Adjudication - CORRECTED Understanding](#2-adjudication-corrected)
3. [Critique - Relationship with Adjudication](#3-critique-relationship)
4. [COMPLETE Categorization Criteria Matrix](#4-complete-categorization-criteria)
5. [Updated Surgical Fixes Plan](#5-updated-fixes-plan)

---

## 1. PREFLIGHT CALIBRATION - COMPLETE EXPLANATION

### 1.1 HOW DOES AI ADD KEYWORDS? (Technical Deep Dive)

**Current Process (Step-by-Step):**

1. **Script samples 50 rows** from Excel file (`preflight.py` line 50)
2. **Script sends data to AI** via API call (`preflight.py` line 64)
3. **AI analyzes text and returns JSON** (pure LLM reasoning, no file access)
4. **Script receives JSON response** (lines 65-67)
5. **Script BLINDLY merges** AI response into config object
6. **Script writes to file** - `memory/suppliers/{name}/preflight_calibration.json`

**CRITICAL ISSUE: AI CANNOT READ FILES**

The AI:
- ❌ Cannot see the calibration.json file before editing
- ❌ Cannot see the file after editing
- ❌ Cannot validate its own output
- ❌ Does NOT have file system access
- ✅ Only receives 50 sample rows as TEXT in the prompt
- ✅ Must infer patterns from THOSE ROWS ONLY

**How Keywords Ended Up in Both Lists:**

```python
# Line 64: preflight.py sends this to AI
obj = chat_json(config=config, system=system, user=user)

# AI returns this JSON (from memory, no file access):
{
  "explicit_units": ["ML", "CM", "PK", "PACK", "PC", "PCS"],  # Saw these in titles
  "dimension_shield_keywords": ["PK", "PACK", "PC", "PCS", "cm", "mm"],  # ALSO saw these!
  ...
}

# Line 66: Script BLINDLY accepts this
merged.update(obj)  # ← NO VALIDATION!

# Script writes to disk - duplication persists
```

**The AI made a "mistake" because:**
1. Prompt didn't explain what these fields are FOR
2. Prompt didn't say they should be mutually exclusive
3. Prompt didn't give clear examples
4. **NO validation layer exists** to catch the duplication

### 1.2 MULTI-SUPPLIER SUPPORT

**Your concern:** "Different suppliers have different naming conventions"

**Current Approach:**
- Each supplier gets its OWN calibration file: `memory/suppliers/{supplier_name}/calibration.json`
- Preflight runs PER supplier
- Configuration is supplier-specific

**Example:**
```
memory/suppliers/
├── efghousewares/
│   └── preflight_calibration.json  (has "PK", "PACK" patterns)
├── wholesaledeals/
│   └── preflight_calibration.json  (might have "CTN", "BOX" patterns)
└── part_4_jan/
    └── (will be created with patterns from part 4 jan.xlsx)
```

**This IS already designed for multiple suppliers!**

### 1.3 AI SELF-VALIDATION (What's Missing)

**CURRENT:** AI → JSON → Script writes to file → DONE (no validation)

**NEEDED:** AI → JSON → Validation Layer → Fix if needed → Write to file

**Proposed Fix for Preflight:**

```python
# File: src/fba_agent/preflight.py (NEW VALIDATION LAYER)

def validate_and_fix_calibration(ai_response: dict) -> tuple[dict, list[str]]:
    """
    Validate AI calibration response and auto-fix common issues.
    
    Returns:
        (fixed_response, warnings)
    """
    warnings = []
    
    explicit_units = set(ai_response.get("explicit_units", []))
    dim_shields = set(ai_response.get("dimension_shield_keywords", []))
    spec_shields = set(ai_response.get("spec_x_shield_keywords", []))
    
    # FIX #1: Remove pack keywords from shield lists
    pack_keywords = {"PK", "PACK", "PC", "PCS", "PIECES", "PIECE", "pk", "pack", "pc", "pcs", "pieces"}
    
    duplicates_in_dim = explicit_units & dim_shields & pack_keywords
    if duplicates_in_dim:
        warnings.append(f"AI put pack keywords in dimension_shield: {duplicates_in_dim}. Auto-fixing.")
        dim_shields -= pack_keywords  # Remove from shields
    
    duplicates_in_spec = explicit_units & spec_shields & pack_keywords
    if duplicates_in_spec:
        warnings.append(f"AI put pack keywords in spec_x_shield: {duplicates_in_spec}. Auto-fixing.")
        spec_shields -= pack_keywords
    
    # FIX #2: Don't shield generic multipliers like "X", "x", "BY"
    overly_broad_shields = {"X", "x", "BY", "/", "-"}
    removed_broad = spec_shields & overly_broad_shields
    if removed_broad:
        warnings.append(f"Removed overly broad spec shields: {removed_broad}")
        spec_shields -= overly_broad_shields
    
    # FIX #3: Ensure measurement units are in shields, not explicit_units
    measurement_units = {"CM", "MM", "ML", "KG", "G", "L", "cm", "mm", "ml", "kg", "g", "l"}
    measurements_in_explicit = explicit_units & measurement_units
    if measurements_in_explicit:
        warnings.append(f"Measurements in explicit_units: {measurements_in_explicit}. Moving to shields.")
        explicit_units -= measurement_units
        dim_shields |= (measurements_in_explicit & measurement_units)
    
    # Update response with fixed values
    ai_response["explicit_units"] = sorted(list(explicit_units))
    ai_response["dimension_shield_keywords"] = sorted(list(dim_shields))
    ai_response["spec_x_shield_keywords"] = sorted(list(spec_shields))
    
    return ai_response, warnings


# MODIFY run_preflight() to use validation:
def run_preflight(df_sample: pd.DataFrame) -> tuple[SupplierNamingConvention, list[str], dict[str, Any]]:
    ...
    try:
        obj = chat_json(config=config, system=system, user=user)
        
        # ADD VALIDATION LAYER
        obj, validation_warnings = validate_and_fix_calibration(obj)
        warnings.extend(validation_warnings)
        
        merged = heuristic_naming.__dict__.copy()
        merged.update(obj)
        naming = SupplierNamingConvention(**merged)
        return naming, warnings, {"mode": "openai_validated", "model": config.model}
    except Exception as e:
        ...
```

**This adds:**
1. ✅ Automatic fixing of AI duplication errors
2. ✅ Warnings logged so you can see what was fixed
3. ✅ Ensures pack keywords never end up in shields
4. ✅ No file access needed - validates in-memory before writing

### 1.4 IMPROVED PREFLIGHT PROMPT (Multi-Supplier Aware)

**CURRENT PROMPT (Too Vague):**
```python
user = (
    "Analyze these rows and output a JSON object with keys:\\n"
    "explicit_units (list of strings), ..."
)
```

**UPDATED PROMPT (Detailed + Multi-Supplier Aware):**
```python
user = (
    "You are analyzing product title patterns from a specific supplier's catalog. "
    "Each supplier may use different naming conventions (e.g., 'PK6', 'PACK OF 12', '6-PACK', '6CT'). "
    "Your task is to detect THIS SUPPLIER's specific patterns.\\n\\n"
    
    "**CRITICAL: These lists must be MUTUALLY EXCLUSIVE!**\\n\\n"
    
    "**explicit_units** (Pack quantity keywords that ENABLE pack detection):\\n"
    "- Words that indicate MULTIPACKS or QUANTITIES\\n"
    "- Examples: 'pk', 'pack', 'pc', 'pcs', 'pieces', 'ct', 'count'\\n"
    "- As in: '6 PK', 'PACK OF 12', '24 PC SET'\\n"
    "- These trigger pack quantity detection\\n\\n"
    
    "**dimension_shield_keywords** (Measurement words that PREVENT pack detection):\\n"
    "- Words that indicate PHYSICAL MEASUREMENTS or SIZES\\n"
    "- Examples: 'cm', 'mm', 'inch', 'ml', 'kg', 'g', 'l', 'oz'\\n"
    "- As in: '30CM x 40CM', '500ML BOTTLE', '2KG WEIGHT'\\n"
    "- These are dimensions, NOT pack quantities\\n"
    "- **DO NOT include pack keywords here!**\\n\\n"
    
    "**spec_x_shield_keywords** (Non-pack multipliers in specifications):\\n"
    "- Words that appear with 'X' but DON'T mean packs\\n"
    "- Examples: 'zoom', 'magnification', 'times' → as in '10X ZOOM', '2000X MICROSCOPE'\\n"
    "- **AVOID generic words:** Don't include 'X', 'x', 'BY', '/', '-' (too broad, blocks valid patterns)\\n\\n"
    
    "**brand_position** ('start' or 'mixed'):\\n"
    "- 'start' if brand is consistently the first word (e.g., 'PYREX Square Dish', 'DRAPER Drill Bit')\\n"
    "- 'mixed' if brand appears in various positions\\n\\n"
    
    "**capacity_pattern_as_rsu** (true/false):\\n"
    "- true if patterns like '3 X 500ML' mean 3 bottles (RSU=3)\\n"
    "- false if '3 X 500ML' is just describing total capacity (RSU=1)\\n\\n"
    
    f"Sample rows from THIS SUPPLIER:\\n{preview}\\n\\n"
    
    "Return ONLY valid JSON with these keys:\\n"
    "explicit_units, dimension_shield_keywords, spec_x_shield_keywords, "
    "brand_position, sales_column, allow_trailing_number_as_qty, "
    "leading_multiplier_check, capacity_pattern_as_rsu, table_pipe_sanitization"
)
```

**This ensures:**
- ✅ AI understands each field's PURPOSE
- ✅ Clear examples for each category
- ✅ Explicit instructions about mutual exclusivity
- ✅ Supplier-specific context ("THIS SUPPLIER's patterns")
- ✅ Warning about overly broad shields

---

## 2. ADJUDICATION - CORRECTED UNDERSTANDING

### 2.1 MY PREVIOUS MISUNDERSTANDING (APOLOGY)

**I WAS COMPLETELY WRONG about Adjudication's purpose!**

**What I incorrectly said:**
> "Adjudication reviews NEEDS_VER items and recommends upgrading to HIGHLY_LIKELY"

**What it ACTUALLY does (based on your clarification):**

### 2.2 ACTUAL PURPOSE OF ADJUDICATION (CORRECTED)

**Adjudication is a COMPREHENSIVE QUALITY REVIEW of the ENTIRE MD REPORT.**

**The AI should:**
1. ✅ Read EVERY entry listed in the MD report (not just NEEDS_VER)
2. ✅ Analyze each row MANUALLY (read titles, metrics, make educated decisions)
3. ✅ Identify ERRORS/DISCREPANCIES across ALL sections:
   - VERIFIED section - any false positives?
   - HIGHLY_LIKELY section - any false positives or should-be-VERIFIED?
   - NEEDS_VER section - any that should be upgraded or downgraded?
   - FILTERED_OUT section - any valid matches inappropriately excluded?
4. ✅ Perform root cause analysis for each error found
5. ✅ Decide if recategorization is needed
6. ✅ Determine if Critique (iteration 2) should run

### 2.3 CURRENT IMPLEMENTATION vs EXPECTED (THE PROBLEM)

**CURRENT IMPLEMENTATION** (`adjudication.py` lines 56-114):

```python
def select_candidates(...):
    """Select row_ids for AI adjudication"""
    
    # Selects only SPECIFIC rows based on triggers:
    candidates = set()
    
    # 1. Ambiguous pack verdict
    # 2. Mid-range confidence (45-60)
    # 3. High profit with weak match
    # 4. NEEDS_VERIFICATION bucket (first 50 only!)  ← ONLY 50!
    # 5. High profit but FILTERED_OUT
    
    effective_cap = min(cap, int(total_rows * cap_percentage))  # MAX 300 rows
    
    return list(candidates)[:effective_cap]  # Returns ~50-300 row IDs
```

**Then** (`iteration.py` line 241):
```python
for row_id in candidate_ids[:50]:  # ONLY processes first 50!
    ...
```

**So currently:**
- ❌ AI sees ONLY 50-300 rows (NOT the full report)
- ❌ AI only sees rows from specific buckets (trigger-based)
- ❌ AI analyzes DataFrame rows, NOT the MD report
- ❌ AI makes decisions per-row in isolation
- ❌ NO comprehensive review of the entire report

**EXPECTED IMPLEMENTATION (Based on your requirements):**

```python
def run_comprehensive_adjudication(
    report_path: str,  # Path to MD report file
    ledger: pd.DataFrame,
    provider: BaseProvider,
) -> ComprehensiveAdjudicationResult:
    """
    AI performs thorough manual review of ENTIRE MD report.
    
    This is NOT a row-by-row automated check.
    This IS a comprehensive audit where AI reads the report like a human would.
    """
    
    # 1. Read the ENTIRE MD report
    with open(report_path, 'r', encoding='utf-8') as f:
        report_content = f.read()
    
    # 2. Send FULL report to AI
    system_prompt = '''You are an FBA product analysis expert conducting a thorough manual audit.

Your task is to:
1. Read EVERY product entry in this markdown report (ALL sections)
2. For EACH entry, analyze:
   - Supplier Title vs Amazon Title
   - EAN match evidence
   - Pack size detection
   - Adjusted profit calculation
   - Categorization decision (VERIFIED, HIGHLY_LIKELY, NEEDS_VER,  FILTERED_OUT)
   
3. Identify ALL errors and discrepancies:
   - False Positives: Products incorrectly included
   - False Negatives: Valid matches incorrectly excluded
   - Miscategorizations: Products in wrong category
   - Calculation errors: Wrong pack ratios, profit miscalculations
   
4. For EACH error, determine ROOT CAUSE:
   - Was brand not detected?
   - Was pack size misread (dimension as pack)?
   - Was shield keyword blocking valid detection?
   - Was similarity threshold too strict?
   
5. Provide comprehensive recommendations:
   - Which rows need recategorization (with new category)
   - Which rows need removal (false positives)
   - Which configuration changes would fix systematic issues
   - Whether Critique (iteration 2) should run

This is a MANUAL ANALYSIS - think like a human reviewing each entry carefully.
'''
    
    user_prompt = f'''Review this complete FBA analysis report:

{report_content}

Provide comprehensive adjudication results as JSON.
'''
    
    # 3. AI performs comprehensive analysis
    response = provider.chat_json(system_prompt, user_prompt, schema=COMPREHENSIVE_ADJUDICATION_SCHEMA)
    
    # 4. Return structured results
    return ComprehensiveAdjudicationResult(
        errors_found=response['errors_found'],
        recategorizations=response['recategorizations'],
        root_causes=response['root_causes'],
        config_recommendations=response['config_recommendations'],
        should_run_critique=response['should_run_critique'],
        overall_assessment=response['overall_assessment']
    )
```

### 2.4 WHAT CAN AI CURRENTLY ACCESS?

**Current access** (`adjudication.py` line 187):
```python
# AI receives THIS per row:
user = (
    f"Row ID: {row_data['row_id']}\\n"
    f"Supplier Title: {row_data['supplier_title']}\\n"
    f"Amazon Title: {row_data['amazon_title']}\\n"
    f"Supplier EAN: {row_data.get('supplier_ean', '-')}\\n"
    f"Amazon EAN: {row_data.get('amazon_ean', '-')}\\n"
    f"Similarity: {row_data.get('similarity', 0)}\\n"
    f"Net Profit: £{row_data.get('net_profit', 0)}\\n"
    f"Adjusted Profit: £{row_data.get('adjusted_profit', 0)}\\n"
    f"Current Bucket: {row_data.get('bucket')}\\n"
    f"Pack Verdict: {row_data.get('pack_verdict', '')}\\n"
    ...
)
```

**What AI CANNOT currently access:**
- ❌ The MD report file itself
- ❌ Other rows for comparison/context
- ❌ Configuration files to adjust
- ❌ Excel source file to re-filter
- ❌ Calibration JSON to fix

**What AI SHOULD access (for comprehensive adjudication):**
- ✅ Complete MD report text (all sections, all entries)
- ✅ Bucket count statistics
- ✅ Sample high-profit FILTERED_OUT entries
- ✅ Current configuration summary

**What AI SHOULD be able to RECOMMEND (not directly edit):**
- ✅ Row recategorizations: "Move Row 269 from NEEDS_VER to HIGHLY_LIKELY"
- ✅ Configuration changes: "Add 'TIDYZ' to known brands list"
- ✅ Shield adjustments: "Remove 'PK' from dimension_shield_keywords"
- ✅ Whether to run Critique/iteration 2

### 2.5 CLARIFICATION: "Top 50 Rows"

**MY CONFUSION EXPLAINED:**

When I said "top 50 rows", I meant:
- First 50 rows from `candidate_ids` list (selected from DataFrame ledger)
- NOT the first 50 rows of the Excel file
- NOT the first 50 rows of the MD report

**The current code:**
1. Analyzes ALL 2696 rows from Excel → creates DataFrame ledger
2. Selects ~300 "candidate" row IDs based on triggers
3. Takes first 50 of those candidates
4. Sends each of those 50 to AI individually
5. AI never sees the MD report at all!

**What SHOULD happen (based on your requirement):**
1. Script generates MD report from analyzed data
2. AI receives ENTIRE MD report as text
3. AI reads and analyzes EVERY entry in the report
4. AI identifies errors across ALL sections
5. AI provides comprehensive feedback

---

## 3. CRITIQUE - RELATIONSHIP WITH ADJUDICATION

### 3.1 CURRENT RELATIONSHIP (As Implemented)

**Adjudication (Step 8):**
- Runs BEFORE Critique
- Reviews ~50 rows from DataFrame
- Returns: List of row-level recommendations
- **Currently:** Results are stored but NOT applied!

**Critique (Step 9):**
- Runs AFTER Adjudication
- Reviews overall bucket counts and anomalies
- **Does NOT see** adjudication results!
- Returns: Config changes + recommended_action (finalize/rerun/block)

**Current code** (`critique.py` lines 77-108):
```python
def build_critique_inputs(...):
    inputs = {
        "bucket_counts": ...,
        "sample_rows": ...,  # 5 samples per bucket
        "anomalies": ...,
        "regression_diff": ...,
    }
    # ← Adjudication results are NOT included!
```

**So currently:**
- ❌ Critique does NOT know what Adjudication found
- ❌ Critique cannot factor in adjudication recommendations
- ❌ They are completely independent steps

### 3.2 WHY THIS CONFUSES YOU (I Understand Now!)

**Your expectation:** "Adjudication should BE the thorough review that determines if Critique is needed"

**Reality:** They're currently two separate, disconnected AI calls

**Your mental model** (which makes more sense):
```
1. Script generates initial report
2. Adjudication: AI thoroughly reviews ENTIRE report
3. Adjudication decides: "Found 25 errors, recommend these fixes, run Critique: YES"
4. Script applies adjudication fixes
5. Critique: Run iteration 2 with updated config
```

**Current workflow** (disconnected):
```
1. Script generates DataFrame analysis
2. Adjudication: AI reviews 50 individual rows (results ignored!)
3. Script generates MD report (doesn't use adjudication results)
4. Critique: AI reviews bucket counts (doesn't know about adjudication)
5. Critique blocks (errors in report but can't see them)
```

### 3.3 PROPOSED UNIFIED WORKFLOW

**Step 8: Comprehensive Adjudication (REDESIGNED)**
- Input: Complete MD report + DataFrame ledger
- AI: Thoroughly reviews ALL entries
- AI: Identifies errors, root causes, recommendations
- Output: 
  - `recategorizations`: List of rows to move between buckets
  - `config_fixes`: Specific config changes needed
  - `run_critique`: Boolean (should iteration 2 happen?)
  - `critique_input`: Summary of findings for Critique to use

**Step 9: Critique (ENHANCED)**
- Input: Adjudication findings + bucket counts + config
- AI: Reviews adjudication findings
- AI: Proposes bounded config adjustments  
- Output:
  - `recommended_action`: "apply_and_rerun" (if adjudication found fixable issues)
  - `proposed_changes`: Specific config changes

**Data flow:**
```
Adjudication Results
    ↓
    ├─→ Apply recategorizations to ledger
    ├─→ Pass findings to Critique
    └─→ Decide if Critique should run

Critique (if Adjudication says yes)
    ↓
    ├─→ Review adjudication findings
    ├─→ Propose config changes
    └─→ Trigger iteration 2 if needed
```

---

## 4. COMPLETE CATEGORIZATION CRITERIA MATRIX

### 4.1 I MISSED SEVERAL CRITERIA - APOLOGY

**You are correct - the list I provided was incomplete!**

Looking at the methodology guide and the actual code, here's the COMPLETE criteria matrix:

### 4.2 FULL DECISION MATRIX (All Criteria)

| # | Criterion Name | Type | Used In Decision | Details |
|---|---------------|------|-----------------|---------|
| 1 | **Strict Exact EAN Match** | Primary | VERIFIED gate | Both EANs valid + checksums pass + exact match |
| 2 | **Brand Match** | Primary | HIGHLY_LIKELY gate | Both brands detected + identical |
| 3 | **Product Type Match** | Primary | HIGHLY_LIKELY gate | Similarity ≥ threshold (0.20) + ≥1 shared token |
| 4 | **Capacity Delta** | Secondary | Gates | % difference between supplier and Amazon size/capacity |
| 5 | **Capacity Gate** | Filter | All buckets | Categorizes capacity difference (ok_0_10, nv_10_25, fo_25_50, fo_gt_50) |
| 6 | **Pack Ratio** | Secondary | Profit adjustment | Amazon pack ÷ Supplier pack (e.g., 12÷6 = 2.0) |
| 7 | **Pack Ambiguous** | Filter | NEEDS_VER gate | Conflicting or unclear pack qty signals in titles |
| 8 | **Adjusted Profit** | Filter | FILTERED_OUT gate | Profit after pack recalculation |
| 9 | **Split Candidate** | Filter | NEEDS_VER gate | Ratio < 1 (supplier pack > Amazon pack) |
| 10 | **Amazon EAN Missing** | Info only | Evidence | If Amazon EAN is blank/null |
| 11 | **Similarity Score** | Threshold | Product match | Jaccard similarity of product tokens |
| 12 | **Shared Tokens Count** | Threshold | Product match | Number of matching product words |
| 13 | **Trap Detections** | Info | Pack analysis | Shield keywords that blocked pack detection |
| 14 | **Variant Match** | Info | Capacity gate | Size/color/scent compatibility |
| 15 | **ROI** | Info only | Not used in logic | Return on investment % |
| 16 | **Sales Volume** | Info only | Not used in logic | Monthly sales estimate |
| 17 | **Confidence Score** | Calculated | Post-decision | Scoring formula result (not used for bucketing) |

### 4.3 COMPLETE CATEGORIZATION LOGIC (Flow Chart)

```
START: Analyze row
    ↓
┌───────────────────────────────────────────────────┐
│ PRIMARY GATE: Do we have a confirmed match?      │
│                                                   │
│ Option 1: strict_exact_ean = TRUE                │
│   → Both EANs valid + checksums pass + match     │
│   → GO TO: VERIFIED PATH                         │
│                                                   │
│ Option 2: brand_match AND product_type_match     │
│   → Both brands detected + identical             │
│   → Similarity ≥ 0.20 + ≥1 shared token         │
│   → GO TO: HIGHLY_LIKELY PATH                    │
│                                                   │
│ Option 3: NONE OF ABOVE                          │
│   → GO TO: FILTERED_OUT (UNRELATED)              │
└───────────────────────────────────────────────────┘
    ↓
    
═══════════════════════════════════════════════════
PATH A: VERIFIED (strict_exact_ean = TRUE)
═══════════════════════════════════════════════════
    ↓
Check Capacity Gate:
    ├─ fo_25_50 or fo_gt_50? → BUCKET: FILTERED_OUT, Reason: "Capacity mismatch"
    │
    ├─ NO → Check Adjusted Profit:
    │       ├─ adjusted_profit ≤ £0? → BUCKET: FILTERED_OUT, Reason: "Adjusted profit ≤ 0"
    │       │
    │       ├─ NO → Check Pack Ratio:
    │       │       ├─ ratio < 1? → BUCKET: NEEDS_VERIFICATION, Reason: "Split candidate"
    │       │       │
    │       │       ├─ NO → Check Pack Ambiguous:
    │       │       │       ├─ pack_ambiguous = TRUE? → BUCKET: NEEDS_VERIFICATION, Reason: "Pack ambiguous"
    │       │       │       │
    │       │       │       └─ NO → ✅ BUCKET: VERIFIED (RECOMMENDED)
    
═══════════════════════════════════════════════════
PATH B: HIGHLY_LIKELY (brand + product match)
═══════════════════════════════════════════════════
    ↓
Check Capacity Gate:
    ├─ nv_10_25? → BUCKET: NEEDS_VERIFICATION, Reason: "Capacity 10-25%"
    │
    ├─ fo_25_50 or fo_gt_50? → BUCKET: FILTERED_OUT, Reason: "Capacity mismatch"
    │
    ├─ NO → Check Adjusted Profit:
    │       ├─ adjusted_profit ≤ £0? → BUCKET: FILTERED_OUT, Reason: "Adjusted profit ≤ 0"
    │       │
    │       ├─ NO → Check Pack Ambiguous:
    │       │       ├─ pack_ambiguous = TRUE? → BUCKET: NEEDS_VERIFICATION, Reason: "Pack ambiguous"
    │       │       │
    │       │       └─ NO → ✅ BUCKET: HIGHLY_LIKELY (RECOMMENDED)

═══════════════════════════════════════════════════
PATH C: NO CONFIRMED MATCH
═══════════════════════════════════════════════════
    ↓
    BUCKET: FILTERED_OUT
    include_in_tables: FALSE  ← Not shown in report
    Reason: "Unrelated / not included"
```

### 4.4 ADDITIONAL CRITERIA FROM METHODOLOGY GUIDE

**From** `FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md` **(lines 58-71):**

The guide defines a 5th category I didn't include:

| Category | Current Code Equivalent | Notes |
|----------|------------------------|-------|
| **AUDITED OUT** | FILTERED_OUT (with `include_in_tables=true`) | Confirmed match but excluded for reason |
| **UNRELATED / NOT INCLUDED** | FILTERED_OUT (with `include_in_tables=false`) | Not a confirmed match |

**So the COMPLETE category set is:**
1. VERIFIED - RECOMMENDED
2. VERIFIED - FILTERED_OUT/EXCLUDED (= AUDITED OUT)
3. HIGHLY_LIKELY - RECOMMENDED
4. HIGHLY_LIKELY - FILTERED_OUT/EXCLUDED (= AUDITED OUT)
5. NEEDS_VERIFICATION
6. FILTERED_OUT (UNRELATED - not shown in report tables)

### 4.5 CRITERIA I INITIALLY MISSED:

1. **Capacity variants** (size/color/scent) - I mentioned delta but not variant parsing
2. **Split candidate** (ratio < 1) - I mentioned but didn't explain fully
3. **Trap detections** - I didn't explain how shields affect decisions
4. **Ambiguous pack vs uncertain pack** - Different levels of pack confidence
5. **AUDITED OUT vs UNRELATED** distinction - Critical for report structure
6. **include_in_tables flag** - Controls whether row appears in report
7. **Confidence score calculation** - Happens AFTER bucketing (lines 226-228)

---

## 5. UPDATED SURGICAL FIXES PLAN

Based on all clarifications, here's the REVISED plan:

### FIX #1: Preflight Calibration (ENHANCED)

**Changes:**
1. ✅ Add validation layer to auto-fix keyword duplications
2. ✅ Improve prompt with detailed explanations + examples
3. ✅ Add multi-supplier context to prompt
4. ✅ Log warnings when auto-fixes are applied

**Files to modify:**
- `src/fba_agent/preflight.py` - Add `validate_and_fix_calibration()` function
- `src/fba_agent/preflight.py` - Update prompt (lines 52-60)

### FIX #2: Brand/Product Matching (UNCHANGED)

**Per your requirements:**
- Different brands in both → EXCLUDE
- No brands / one brand → NEEDS_VER if strong product match
- Same brand → HIGHLY_LIKELY if product matches

### FIX #3: Adjudication (COMPLETELY REDESIGNED)

**NEW PURPOSE:** Comprehensive report review

**Changes:**
1. ❌ REMOVE per-row adjudication
2. ✅ ADD comprehensive report review
3. ✅ AI receives full MD report text
4. ✅ AI identifies errors across ALL sections
5. ✅ AI performs root cause analysis
6. ✅ AI recommends recategorizations + config fixes

**New function:**
```python
def run_comprehensive_adjudication(
    report_path: str,
    ledger: pd.DataFrame,
    config: MergedConfig,
    provider: BaseProvider,
) -> ComprehensiveAdjudicationResult:
    # (See section 2.3 above for full implementation)
```

### FIX #4: Connect Adjudication → Critique

**Changes:**
1. ✅ Pass adjudication results to Critique
2. ✅ Critique reviews adjudication findings
3. ✅ Critique incorporates error analysis into decision

**Modified flow:**
```
iteration.py:
1. Generate MD report
2. Run comprehensive adjudication (reads full report)
3. Apply adjudication recategorizations to ledger
4. If adjudication.should_run_critique:
   - Run critique with adjudication findings
   - Apply critique config changes
   - Re-run iteration 2
```

### FIX #5: Stable Keys (Low Priority)

**Confirmed:** One key per product row (not per column)

**Simple fix:** Ensure assignment happens in run.py

### FIX #6: Complete Categorization Logic

**Add missing category:** AUDITED OUT (separate from UNRELATED)

**Changes:**
- Rename `FILTERED_OUT` with `include_in_tables=true` → "AUDITED_OUT"  
- Keep `FILTERED_OUT` with `include_in_tables=false` → "UNRELATED"
- Report shows both sections clearly labeled

---

## SUMMARY OF ALL CHANGES

| Fix # | Component | Type | Priority | Impact |
|-------|-----------|------|----------|--------|
| 1 | Preflight Validation | ADD | HIGH | Prevents keyword duplication |
| 2 | Preflight Prompt | ENHANCE | HIGH | Better cross-supplier support |
| 3 | Brand Matching Logic | MODIFY | HIGH | Matches your requirements |
| 4 | Adjudication | REDESIGN | CRITICAL | Enables full report review |
| 5 | Adjudication→Critique | ADD | CRITICAL | Connects workflow steps |
| 6 | Apply Recategorizations | ADD | CRITICAL | Makes adjudication useful |
| 7 | Category Names | CLARIFY | MEDIUM | AUDITED_OUT vs UNRELATED |
| 8 | Stable Keys | FIX | LOW | Regression detection |

**Next Step:** Shall I proceed with implementing these fixes?
