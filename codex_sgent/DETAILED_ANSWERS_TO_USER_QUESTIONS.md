# DETAILED ANSWERS TO USER QUESTIONS WITH EXAMPLES

**Generated:** 2026-01-06 04:53 UTC+4  
**Purpose:** Address all user questions about root causes, provide examples, and clarify fixes before implementation

---

## QUESTION 1: WHY DID AI PUT PK/PACK/PC IN SHIELD WORDS?

### ROOT CAUSE INVESTIGATION:

I examined the actual AI response from `llm_trace.jsonl` (entry 1 - Preflight call):

**AI WAS ASKED:**
```
"Analyze these rows and output a JSON object with keys:
explicit_units (list of strings), 
dimension_shield_keywords (list of strings), 
..."
```

**AI RESPONDED:**
```json
{
  "explicit_units": ["ML", "CM", "M", "L", "INCH", "MM", "G", "KG", "W", "MIN", "KPA", "CC", "PC", "PCS", "PIECES", "PK", "PACK", "GB"],
  "dimension_shield_keywords": ["ASSORTED", "EACH", "PIECES", "PC", "PCS", "PACK", "PK", "SET", "SETS", "ASSORT."]
}
```

### THE PROBLEM:

**AI PUT THE SAME KEYWORDS IN BOTH LISTS!**

- `explicit_units` includes: **PC, PCS, PIECES, PK, PACK** ✓ (Correct!)
- `dimension_shield_keywords` ALSO includes: **PC, PCS, PIECES, PK, PACK** ✗ (WRONG!)

### WHY THIS HAPPENED:

**The Preflight Prompt is TOO VAGUE** (lines 52-60 in `preflight.py`):

```python
user = (
    "Analyze these rows and output a JSON object with keys:\\n"
    "explicit_units (list of strings),  ← NO EXPLANATION WHAT THIS MEANS
    "dimension_shield_keywords (list of strings),  ← NO EXPLANATION WHAT THIS MEANS
    ...
)
```

**The AI was NOT told:**
1. What "explicit_units" are used for (detecting pack quantities)
2. What "dimension_shield_keywords" are used for (PREVENTING pack detection for dimensions)
3. That these lists should be MUTUALLY EXCLUSIVE
4. Examples of what belongs in each

**The AI saw sample titles like:**
- "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
- "PRIMA HEART SHAPED BAKE PAN 23CM"
- "PACK OF 12 ROLSON TOOLS"

And thought: 
- "PC, PCS, PK, PACK appear in titles → add to explicit_units" ✓
- "PC, PCS, PK, PACK could also be dimensions → add to shield too!" ✗

### WHY DIDN'T AI NOTICE THE DUPLICATION?

The AI completed its task exactly as instructed - it analyzed the data and populated both lists. **There was NO instruction to check for conflicts or duplicates between the lists.**

### FIX FOR THIS:

**Update the Preflight Prompt** in `src/fba_agent/preflight.py` (lines 52-60):

**CURRENT (VAGUE):**
```python
user = (
    "Analyze these rows and output a JSON object with keys:\\n"
    "explicit_units (list of strings), "
    "dimension_shield_keywords (list of strings), "
    ...
)
```

**FIXED (SPECIFIC WITH EXAMPLES):**
```python
user = (
    "Analyze these supplier product titles and output a JSON configuration.\\n\\n"
    
    "**explicit_units**: Keywords that indicate PACK QUANTITIES/MULTIPACKS.\\n"
    "Examples: 'pk', 'pack', 'pc', 'pcs', 'pieces' (as in '6 PK' or 'PACK OF 12')\\n"
    "These words ENABLE pack detection.\\n\\n"
    
    "**dimension_shield_keywords**: Keywords that indicate MEASUREMENTS/DIMENSIONS.\\n"
    "Examples: 'cm', 'mm', 'inch', 'ml', 'kg', 'g' (as in '30CM x 40CM' or '500ML')\\n"
    "These words PREVENT pack detection (they describe size, not quantity).\\n\\n"
    
    "⚠️ CRITICAL: These lists must be MUTUALLY EXCLUSIVE!\\n"
    "If a word appears in explicit_units (like 'PK'), do NOT add it to dimension_shield_keywords.\\n\\n"
    
    "**spec_x_shield_keywords**: Non-pack multipliers in specifications.\\n"
    "Examples: 'zoom', 'magnification', 'times' (as in '10X zoom' or '2000x magnification')\\n"
    "Avoid generic words like 'x', 'X', 'BY' which appear in valid pack patterns ('3 X 500ML').\\n\\n"
    
    f"Sample Rows:\\n{preview}\\n\\n"
    "Return ONLY valid JSON with these keys: explicit_units, dimension_shield_keywords, "
    "spec_x_shield_keywords, brand_position, sales_column, allow_trailing_number_as_qty, "
    "leading_multiplier_check, capacity_pattern_as_rsu, table_pipe_sanitization."
)
```

---

## QUESTION 2: WHAT DOES "AI SUGGESTIONS BEING IGNORED" MEAN?

### EXPLANATION WITH EXAMPLE:

**"AI suggestions being ignored" refers to ADJUDICATION RESULTS not being applied to the data.**

### WHAT IS ADJUDICATION? 

**Adjudication** is when the AI reviews borderline cases and makes recommendations.

**Example Flow:**

1. **Deterministic Analysis** (script) categorizes Row 269:
   ```
   Supplier: "WORLD OF PETS CAT LITTER SCENTED 3LT"
   Amazon: "World's Best Cat Litter 28lb (12.7kg) Lavender Scented"
   
   Brand match: NO (WORLD OF PETS ≠ World's Best)
   Product match: YES (CAT, LITTER, SCENTED)
   Similarity: 0.38
   
   → Script decision: NEEDS_VERIFICATION (borderline case)
   ```

2. **Adjudication** (AI) is called to review Row 269:
   ```
   AI analyzes:
   - Shared tokens: CAT, LITTER, SCENTED (3 strong product tokens)
   - Context: Both are cat litter products
   - Similarity: 0.38 (reasonable)
   - Profit: £16.14 (good)
   
   → AI recommendation: "Upgrade to HIGHLY_LIKELY"
   ```

3. **What SHOULD happen:**
   - Update Row 269 in ledger: bucket = "HIGHLY_LIKELY"
   - Update Row 269 confidence: 85
   - Row 269 appears in HIGHLY_LIKELY section of report

4. **What ACTUALLY happens:**
   - AI recommendation stored in `adjudication_results` array
   - Ledger is NEVER updated
   - Row 269 stays in NEEDS_VERIFICATION
   - Report shows Row 269 under NEEDS_VERIFICATION ✗

### WHO IS AI SUGGESTING TO?

**The AI is NOT suggesting to anyone**. It's part of an automated workflow:

```
Adjudication AI → Returns recommendations → Should update ledger automatically
                                         ↓
                                    ✗ BROKEN STEP ✗
                                    (recommendations ignored)
```

The issue is that **the code to apply AI recommendations is missing/not called**.

### WHERE IS THE BUG?

**File:** `src/fba_agent/iteration.py` (line 244)

```python
adjudication_results = run_adjudication(candidates, provider)
# ← NOTHING HAPPENS HERE WITH THE RESULTS!
# Results are stored but never applied to ledger
```

Later (line 269), the code DOES apply changes, but only for CRITIQUE:

```python
if critique and critique.proposed_changes:
    current_config, current_brand_aliases, logs = apply_adjustments(...)
    # ↑ This applies CRITIQUE changes
    # But ADJUDICATION results are still sitting unused!
```

---

## QUESTION 3: MATCHING CONDITIONS FOR EACH REPORT SECTION

### CLARIFICATION OF YOUR REQUIREMENTS:

Based on your feedback, here's the correct logic:

### FOR NON-MATCHING EAN PRODUCTS:

#### SCENARIO A: NO BRAND IN EITHER TITLE
```
Example:
Supplier: "CAT LITTER SCENTED 3L"
Amazon: "Premium Cat Litter Lavender Scent 28lb"

Brand in Supplier Title: ❌ NO
Brand in Amazon Title: ❌ NO
Product Match: ✅ YES (CAT, LITTER, SCENTED)

→ Decision: NEEDS_VERIFICATION
→ Reason: "No brand detected in titles; verify packaging manually"
```

#### SCENARIO B: DIFFERENT BRANDS IN BOTH TITLES
```
Example:
Supplier: "TESCO CAT LITTER SCENTED 3L"
Amazon: "PURINA Cat Litter Lavender Scent 28lb"

Brand in Supplier Title: ✅ YES (TESCO)
Brand in Amazon Title: ✅ YES (PURINA)
Brands Match: ❌ NO (different brands)

→ Decision: EXCLUDED FROM REPORT (UNRELATED)
→ Reason: "Different brands → different products"
```

#### SCENARIO C: BRAND IN ONE TITLE, MISSING IN OTHER
```
Example:
Supplier: "TIDYZ WHEELY BIN LINERS 5 BAGS 300L"
Amazon: "Premium Wheelie Bin Liners 30 Pack Extra Large"

Brand in Supplier Title: ✅ YES (TIDYZ)
Brand in Amazon Title: ❌ NO (generic description)
Product Match: ✅ STRONG (BIN, LINERS, WHEELIE)

→ Decision: NEEDS_VERIFICATION
→ Reason: "Brand present in supplier title but not Amazon; verify if TIDYZ rebranded or OEM"
```

#### SCENARIO D: MATCHING BRANDS + FEW MATCHING WORDS
```
Example:
Supplier: "PYREX SQUARE GLASS DISH 20X17CM"
Amazon: "PYREX Square Glass Dish 20 x 17 cm – 1 L"

Brand Match: ✅ YES (PYREX)
Product Match: ✅ YES (SQUARE, GLASS, DISH)
Dimensions Match: ✅ YES (20X17CM)
Pack: ✅ 1:1

→ Decision: HIGHLY_LIKELY
→ Reason: "Brand match + product match + size match"
```

### UPDATED FIX #2A LOGIC:

```python
# Determine if brands are present in both titles
brand_s_exists = brand_s is not None and brand_s != ""
brand_a_exists = brand_a is not None and brand_a != ""

# Brand scenarios
both_brands_present = brand_s_exists and brand_a_exists
no_brands_detected = not brand_s_exists and not brand_a_exists
one_brand_missing = (brand_s_exists and not brand_a_exists) or (not brand_s_exists and brand_a_exists)

# Matching logic
if strict_exact_ean:
    confirmed_match = True
    require_needs_ver = False
    
elif both_brands_present:
    if brand_match:
        # Same brand + product match → HIGHLY_LIKELY
        confirmed_match = product_type_match
        require_needs_ver = False
    else:
        # Different brands → EXCLUDE from report
        confirmed_match = False
        require_needs_ver = False
        filter_reason = "Different brands detected"
        
elif no_brands_detected:
    # No brands → needs manual verification if product matches
    if product_type_match and len(product_s & product_a) >= 3:
        confirmed_match = False
        require_needs_ver = True
        filter_reason = "No brands detected; verify product manually"
    else:
        confirmed_match = False
        require_needs_ver = False
        filter_reason = "Weak product match; no brand anchor"
        
elif one_brand_missing:
    # Brand in one title only → needs verification if strong product match
    if product_type_match and similarity >= 0.30 and len(product_s & product_a) >= 3:
        confirmed_match = False
        require_needs_ver = True
        filter_reason = "Brand missing in one title; verify OEM/rebrand possibility"
    else:
        confirmed_match = False
        require_needs_ver = False
        filter_reason = "Weak product match; brand mismatch"
```

---

## QUESTION 4: CLARIFY FIX #2B WITH EXAMPLES

### WHAT IS THE ISSUE IN FIX #2B?

**The issue is the FORMAT of the "Key Match Evidence" column in the report.**

### CURRENT BEHAVIOR:

When a product match is detected WITHOUT brand match, the evidence shows:

```
Key Match Evidence: "Shared anchors: CAT, LITTER, SCENTED"
```

### REFERENCE REPORT FORMAT:

The reference report shows it differently:

```
Key Match Evidence: "WORLD, CAT, LITTER, SCENTED"
```

(No "Shared anchors:" prefix - just the tokens)

### WHY THIS MATTERS:

**Current format:**
```
| Row 269 | NEEDS_VER | ... | Shared anchors: CAT, LITTER, SCENTED | ... |
```

**Reference format:**
```
| Row 269 | HIGHLY_LIKELY | ... | WORLD, CAT, LITTER, SCENTED | ... |
```

The reference format is cleaner and includes the brand token from supplier title (WORLD) even though it doesn't match Amazon's brand.

### THE FIX:

**File:** `src/fba_agent/analysis.py` (lines 119-127)

**BEFORE:**
```python
if strict_exact_ean:
    key_match_evidence = "Exact EAN match; checksums validate"
else:
    shared = sorted(list(product_s & product_a))[:6]
    if brand_match:
        key_match_evidence = f"Brand match: {brand_s}; anchors: {', '.join(shared) or '-'}"
    elif shared:
        key_match_evidence = f"Shared anchors: {', '.join(shared)}"  ← CHANGES THIS
```

**AFTER:**
```python
if strict_exact_ean:
    key_match_evidence = "Exact EAN match; checksums validate"
else:
    shared = sorted(list(product_s & product_a))[:6]
    if brand_match:
        key_match_evidence = f"Brand match: {brand_s}; anchors: {', '.join(shared) or '-'}"
    elif shared:
        # Include supplier brand token + shared product tokens (matches reference format)
        all_tokens = ([brand_s] if brand_s else []) + shared
        key_match_evidence = ', '.join(all_tokens)  # "WORLD, CAT, LITTER, SCENTED"
    else:
        key_match_evidence = "-"
```

### EXAMPLE OUTPUT:

**Row 269:**
- Supplier brand: "WORLD"
- Shared product tokens: ["CAT", "LITTER", "SCENTED"]
- Output: "WORLD, CAT, LITTER, SCENTED"

This matches the reference report exactly.

---

## QUESTION 5: ROOT CAUSE #3 (ADJUDICATION) - DETAILED EXPLANATION

### WHAT IS ADJUDICATION?

**Adjudication is the AI-powered review step that evaluates borderline cases.**

Think of it like this:
1. **Deterministic Script** = Fast, rule-based sorting (like a machine)
2. **Adjudication AI** = Intelligent review of uncertain cases (like a human expert)

### PURPOSE OF ADJUDICATION:

**To rescue valid products that the deterministic rules couldn't confidently categorize.**

### EXAMPLE WORKFLOW:

#### Step 1: Deterministic Analysis

The script analyzes 2696 products and categorizes them:

```
VERIFIED: 8 items (exact EAN match)
HIGHLY_LIKELY: 9 items (brand + product match)
NEEDS_VERIFICATION: 103 items ← BORDERLINE CASES
FILTERED_OUT: 2576 items
```

#### Step 2: Select Adjudication Candidates

The system selects items from NEEDS_VER for AI review:

```python
# Select top candidates
candidates = select_candidates(ledger, evidence, config)
# Returns: [Row 269, Row 731, Row 1248, ... ] (50-300 items)
```

**Selection criteria:**
- High profit potential
- Reasonable similarity score
- Not obviously wrong

#### Step 3: AI Reviews Each Candidate

For EACH candidate, the AI is asked:

```
INPUT TO AI:
{
  "row_id": 269,
  "supplier_title": "WORLD OF PETS CAT LITTER SCENTED 3LT",
  "amazon_title": "World's Best Cat Litter 28lb (12.7kg) Lavender Scented",
  "supplier_ean": "5052516216876",
  "amazon_ean": "-",
  "similarity": 0.38,
  "profit": 16.14,
  "sales": 800,
  "current_bucket": "NEEDS_VERIFICATION",
  "shared_tokens": ["CAT", "LITTER", "SCENTED"]
}

QUESTION TO AI:
"Is this a valid product match? Should it be upgraded to HIGHLY_LIKELY or VERIFIED?"

AI ANALYZES:
- Strong product match (CAT LITTER is specific product type)
- High sales volume (800 units/month) suggests it's correct
- Good profit (£16.14)
- Brands different but product clearly matches
- Amazon EAN missing (doesn't disqualify)

AI RESPONSE:
{
  "row_id": 269,
  "recommended_bucket": "HIGHLY_LIKELY",
  "confidence": 85,
  "reasoning": "Strong product type match (cat litter) with multiple shared descriptive tokens. Different brand names don't disqualify as products are clearly the same type."
}
```

#### Step 4: What SHOULD Happen (Apply Recommendations)

For EACH AI recommendation, the system should:

```python
# Find Row 269 in ledger
row_269 = ledger[ledger["row_id"] == 269]

# Update bucket
row_269["bucket"] = "HIGHLY_LIKELY"  # Was: NEEDS_VERIFICATION

# Update confidence
row_269["confidence"] = 85  # Was: 60

# Update track for reporting
row_269["track"] = "HIGHLY_LIKELY"
```

After applying all recommendations:
```
VERIFIED: 8 items (no change)
HIGHLY_LIKELY: 35 items (was 9, +26 from adjudication)
NEEDS_VERIFICATION: 77 items (was 103, -26 to HIGHLY_LIKELY)
FILTERED_OUT: 2576 items (no change)
```

#### Step 5: What ACTUALLY Happens (BUG)

```python
# Line 244 in iteration.py
adjudication_results = run_adjudication(candidates, provider)

# Results contain:
# [{row_id: 269, recommended_bucket: "HIGHLY_LIKELY", confidence: 85}, ...]

# ← BUT NOTHING IS DONE WITH THESE RESULTS!
# Ledger is never updated
# Results just sit in memory unused
```

**Final counts stay the same:**
```
HIGHLY_LIKELY: 9 items (no change!)
NEEDS_VERIFICATION: 103 items (no change!)
```

### ROOT CAUSE:

**The function to apply adjudication results to the ledger DOES NOT EXIST.**

The workflow assumes it exists:
```
run_adjudication() → [results] → apply_results_to_ledger() → updated ledger
                                         ↑
                                    MISSING FUNCTION!
```

### THE FIX:

**Part A:** Add the missing function to `src/fba_agent/adjustments.py`:

```python
def apply_adjudication_to_ledger(
    ledger: pd.DataFrame,
    adjudication_results: list[dict],
) -> tuple[pd.DataFrame, int]:
    """
    Apply adjudication AI recommendations to the ledger.
    
    For each result, if the AI recommends upgrading a row
    from NEEDS_VERIFICATION to HIGHLY_LIKELY, update the ledger.
    
    Only safe transitions are allowed:
    - NEEDS_VERIFICATION → HIGHLY_LIKELY
    - NEEDS_VERIFICATION → VERIFIED
    - FILTERED_OUT → NEEDS_VERIFICATION
    
    Args:
        ledger: DataFrame with all product rows
        adjudication_results: List of AI decisions
        
    Returns:
        (updated_ledger, count_of_applied_changes)
    """
    applied_count = 0
    
    for result in adjudication_results:
        row_id = result.get("row_id")
        recommended_bucket = result.get("recommended_bucket")
        
        # Find row in ledger
        mask = ledger["row_id"] == row_id
        if not mask.any():
            continue  # Row not found
        
        current_bucket = ledger.loc[mask, "bucket"].iloc[0]
        
        # Only allow safe upgrades
        if (current_bucket == "NEEDS_VERIFICATION" and 
            recommended_bucket == "HIGHLY_LIKELY"):
            # Apply upgrade
            ledger.loc[mask, "bucket"] = "HIGHLY_LIKELY"
            ledger.loc[mask, "track"] = "HIGHLY_LIKELY"
            if "confidence" in result:
                ledger.loc[mask, "confidence"] = result["confidence"]
            applied_count += 1
            
    return ledger, applied_count
```

**Part B:** Call this function in `src/fba_agent/iteration.py` (after line 244):

```python
adjudication_results = run_adjudication(candidates, provider)

# APPLY ADJUDICATION RESULTS TO LEDGER
if adjudication_results:
    from fba_agent.adjustments import apply_adjudication_to_ledger
    ledger, applied_count = apply_adjudication_to_ledger(ledger, adjudication_results)
    print(f"✓ Applied {applied_count} adjudication upgrades to ledger")
```

---

## QUESTION 6: STABLE KEYS - WHAT DOES "NOT ASSIGNED TO COLUMN" MEAN?

### EXPLANATION:

In pandas (Python data library), data is stored in **DataFrames** which are like Excel spreadsheets:

```
DataFrame = Table with rows and columns

        | row_id | supplier_title        | stable_key      | bucket         |
Row 0   | 1      | "PAN AROMA CANDLE..." | "a3f4b2c1d5e6..." | VERIFIED       |
Row 1   | 2      | "TIDYZ BIN LINERS..." | "b7e2a9f3c4d1..." | NEEDS_VER      |
Row 2   | 3      | "PYREX DISH..."       | "c9d1e4f2a3b5..." | HIGHLY_LIKELY  |
        ↑        ↑                       ↑                ↑
      Column   Column                  Column           Column
```

Each **column** has a name: `row_id`, `supplier_title`, `stable_key`, `bucket`

### THE PROBLEM:

The code GENERATES stable keys:
```python
key = generate_stable_key(row)  # Returns: "a3f4b2c1d5e6..."
```

But doesn't ASSIGN them to the `stable_key` column in the DataFrame:
```python
# MISSING: df["stable_key"] = key
```

So the DataFrame looks like:
```
| row_id | supplier_title        | stable_key | bucket       |
| 1      | "PAN AROMA CANDLE..." | ""         | VERIFIED     |  ← EMPTY!
| 2      | "TIDYZ BIN LINERS..." | ""         | NEEDS_VER    |  ← EMPTY!
| 3      | "PYREX DISH..."       | ""         | HIGHLY_LIKELY|  ← EMPTY!
```

### WHY DO WE NEED STABLE KEYS?

**To compare reports across different runs and detect regressions.**

**Example Use Case:**

Run 1 (Monday):
```
Row with stable_key "a3f4b2c1..." → VERIFIED (good product)
```

Run 2 (Tuesday - after code change):
```
Row with stable_key "a3f4b2c1..." → FILTERED_OUT (regression!)
```

Without stable keys, we can't track that the same product was downgraded.

### DO WE REALLY NEED THIS?

**For your immediate use case: NO, not critical.**

Regression detection is useful for:
- Automated testing
- Continuous monitoring
- Detecting if code changes break existing matches

But for manual analysis and fixing the current deficiency, it's **low priority**.

We can implement it later once the core matching logic is fixed.

---

## QUESTION 7: COMPLETE INVESTIGATION - CRITIQUE BLOCKING

Let me now investigate the critique blocking issue by examining the trace log:

```
STATUS: Investigating...
```

(Continuing in next message due to length)

---

## SUMMARY OF REQUIRED FIXES (UPDATED BASED ON YOUR CLARIFICATIONS)

### Fix #1: Pack Shields (IMMEDIATE)
- Create calibration file with correct shields
- Update preflight prompt to be more explicit

### Fix #2: Brand/Product Matching Logic (IMMEDIATE)  
**Updated based on your requirements:**
- Different brands in both titles → EXCLUDE from report
- No brands detected → NEEDS_VERIFICATION if strong product match
- Brand in one title only → NEEDS_VERIFICATION if strong product match
- Matching brands → HIGHLY_LIKELY if product matches

### Fix #3: Adjudication Application (HIGH PRIORITY)
- Add `apply_adjudication_to_ledger()` function
- Call it after adjudication runs
- Updates bucket assignments based on AI recommendations

### Fix #4: Stable Keys (LOW PRIORITY)
- Can defer until after core fixes

### Fix #5: Critique Blocking (INVESTIGATING)
- Need to examine trace log to understand error
- Will provide findings next

---

Ready to proceed with implementing fixes after you confirm the logic is correct?
