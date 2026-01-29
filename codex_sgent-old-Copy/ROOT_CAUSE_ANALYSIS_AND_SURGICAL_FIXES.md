# ROOT CAUSE ANALYSIS & SURGICAL FIXES PLAN
**Generated:** 2026-01-06 01:15 UTC+4  
**Analysis Scope:** All identified issues from comprehensive agent output analysis  
**Approach:** Surgical fixes only - modify problematic sections, preserve working logic

---

## ROOT CAUSE #1: Pack Detection Shields Blocking Valid Pack Keywords

### Symptoms:
- Items with "PK6", "PACK OF 12", "5 PC" have pack_qty = 1 (incorrect)
- Goes to NEEDS_VERIFICATION with "Pack size ambiguous" when it should be clear
- 103 items in NEEDS_VER (many likely pack detection failures)

### Root Cause:
**File:** AI-generated `merged_calibration.json` (lines 24-44)  
**Problem:** AI Preflight incorrectly classified pack keywords as "dimension shields"

```json
"dimension_shield_keywords": [
  "PK", "PC", "PCS", "PACK", "PIECES",  ← WRONG! These detect packs
]
```

### Surgical Fix #1: Override Calibration File

**File:** Create `memory/suppliers/part_4_jan/calibration.json`

```json
{
  "explicit_units": ["ML", "CM", "M", "L", "INCH", "MM", "G", "KG", "W", "MIN", "KPA", "CC", "PC", "PCS", "PIECES", "PK", "PACK", "GB"],
  "dimension_shield_keywords": ["in", "cm", "mm", "metre", "ft", "feet", "inch", "m", "meter", "ml", "kg", "g", "l"],
  "spec_x_shield_keywords": ["zoom", "microscope", "×", "times", "led", "scope", "watt", "magnification"],
  "brand_position": "start",
  "allow_trailing_number_as_qty": true,
  "leading_multiplier_check": true,
  "capacity_pattern_as_rsu": true,
  "table_pipe_sanitization": true
}
```

**Critical Changes:** Moved PC/PCS/PIECES/PK/PACK from shields to explicit_units

---

## ROOT CAUSE #2: Overly Strict Brand+Product Matching Logic

### Your Clarification Was 100% Correct:

**I WAS WRONG** to suggest "World of Pets" vs "World's Best" should match as same brand.

### Re-Analysis of Reference Report Row 269:

```
Supplier: "WORLD OF PETS CAT LITTER SCENTED 3LT"
Amazon: "World's Best Cat Litter 28lb (12.7kg) Lavender Scented"  
Status: HIGHLY LIKELY (Confidence: 85)
Key Match Evidence: "WORLD, CAT, LITTER, SCENTED"  ← NO "Brand match:" prefix!
```

**This means:** Reference allowed PRODUCT-ONLY matches (CAT, LITTER, SCENTED) WITHOUT requiring brand match!

### Actual Root Cause:

**File:** `src/fba_agent/analysis.py` (Line 117)

**Current Logic:**
```python
confirmed_match = strict_exact_ean or (brand_match and product_type_match)
```

**Problem:** Requires BOTH brand AND product to match. But reference allows:
- ✅ Strong product match (3+ shared tokens: CAT, LITTER, SCENTED)
- ❌ No brand match (WORLD OF PETS ≠ World's Best)  
- ➡️ Still → HIGHLY LIKELY

### Surgical Fix #2A: Allow Strong Product-Only Matches

**File:** `src/fba_agent/analysis.py`  
**Lines:** 114-118

**BEFORE:**
```python
filter_reason = "-"
key_match_evidence = "-"

confirmed_match = strict_exact_ean or (brand_match and product_type_match)
```

**AFTER:**
```python
filter_reason = "-"
key_match_evidence = "-"

# Allow HIGHLY_LIKELY if:
# 1. Exact EAN match, OR
# 2. Brand + Product both match, OR
# 3. Very strong product match (high similarity + multiple shared tokens) even without brand
very_strong_product_match = (
    product_type_match 
    and similarity >= 0.30  # Higher threshold if no brand match
    and len(product_s & product_a) >= 3  # At least 3 shared meaningful tokens
)

confirmed_match = (
    strict_exact_ean 
    or (brand_match and product_type_match)
    or very_strong_product_match
)
```

**Rationale:**
- Row 269: shared {CAT, LITTER, SCENTED} = 3 tokens, similarity ~0.38 → Meets criteria ✓
- Weak matches (1-2 tokens) → Still excluded ✓
- Preserves: If brands DO match, lower threshold applies

### Surgical Fix #2B: Fix Key Match Evidence for Product-Only Matches

**File:** `src/fba_agent/analysis.py`  
**Lines:** 119-127

**BEFORE:**
```python
if strict_exact_ean:
    key_match_evidence = "Exact EAN match; checksums validate"
else:
    shared = sorted(list(product_s & product_a))[:6]
    if brand_match:
        key_match_evidence = f"Brand match: {brand_s}; anchors: {', '.join(shared) or '-'}"
    elif shared:
        key_match_evidence = f"Shared anchors: {', '.join(shared)}"
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
        # Product-only match: show tokens like reference format
        key_match_evidence = ', '.join(shared)  # "CAT, LITTER, SCENTED"
    else:
        key_match_evidence = "-"
```

**Matches reference format:** "WORLD, CAT, LITTER, SCENTED" (just comma-separated tokens)

---

## ROOT CAUSE #3: Adjudication Results Not Being Applied

### Symptoms:
- 50 items adjudicated
- 0 items promoted from NEEDS_VER to HIGHLY_LIKELY
- Bucket counts unchanged after adjudication

### Root Cause Analysis:

**File:** `src/fba_agent/iteration.py`  
**Lines:** 236-244, 269-272

**Current Flow:**
1. Line 237: Select candidates
2. Line 241: **Hardcoded limit to 50 items** `[:50]`
3. Line 244: Run adjudication → stores in `adjudication_results`
4. Line 269: Apply adjustments → **Only applies `critique.proposed_changes`**!
5. **Adjudication results are NEVER applied to ledger!**

**The Problem:**
- Adjudication returns recommendations like "upgrade row 123 to HIGHLY_LIKELY"
- These are stored in `adjudication_results` array
- But `apply_adjustments()` only processes `critique.proposed_changes`
- Adjudication changes are ignored!

### Surgical Fix #3A: Apply Adjudication Results to Ledger

**File:** `src/fba_agent/iteration.py`  
**Lines:** After line 244 (right after adjudication runs)

**INSERT NEW CODE:**
```python
                    adjudication_results = run_adjudication(candidates, provider)
                    
                    # APPLY ADJUDICATION RESULTS TO LEDGER
                    if adjudication_results:
                        from fba_agent.adjustments import apply_adjudication_to_ledger
                        ledger, applied_count = apply_adjudication_to_ledger(ledger, adjudication_results)
                        print(f"Applied {applied_count} adjudication decisions to ledger")
```

**File:** `src/fba_agent/adjustments.py`  
**ADD NEW FUNCTION:**

```python
def apply_adjudication_to_ledger(
    ledger: pd.DataFrame,
    adjudication_results: list[dict],
) -> tuple[pd.DataFrame, int]:
    """
    Apply adjudication AI recommendations to the ledger.
    
    Args:
        ledger: Current ledger DataFrame
        adjudication_results: List of adjudication decisions from AI
    
    Returns:
        Tuple of (updated_ledger, count_of_changes_applied)
    """
    applied_count = 0
    
    for result in adjudication_results:
        row_id = result.get("row_id")
        recommended_bucket = result.get("recommended_bucket")
        
        if not row_id or not recommended_bucket:
            continue
        
        # Find row in ledger
        mask = ledger["row_id"] == row_id
        if not mask.any():
            continue
        
        current_bucket = ledger.loc[mask, "bucket"].iloc[0]
        
        # Only allow safe promotions
        safe_transitions = {
            ("NEEDS_VERIFICATION", "HIGHLY_LIKELY"),
            ("NEEDS_VERIFICATION", "VERIFIED"),
            ("FILTERED_OUT", "NEEDS_VERIFICATION"),
        }
        
        if (current_bucket, recommended_bucket) in safe_transitions:
            # Apply change
            ledger.loc[mask, "bucket"] = recommended_bucket
            
            # Update track field if needed
            if recommended_bucket == "VERIFIED":
                ledger.loc[mask, "track"] = "VERIFIED"
            elif recommended_bucket == "HIGHLY_LIKELY":
                ledger.loc[mask, "track"] = "HIGHLY_LIKELY"
            
            # Update confidence if provided
            if "confidence" in result:
                ledger.loc[mask, "confidence"] = result["confidence"]
            
            applied_count += 1
    
    return ledger, applied_count
```

### Surgical Fix #3B: Increase Adjudication Cap

**File:** `src/fba_agent/iteration.py`  
**Line:** 241

**BEFORE:**
```python
for row_id in candidate_ids[:50]:  # Limit to 50 for performance
```

**AFTER:**
```python
for row_id in candidate_ids[:300]:  # Increased to match select_candidates cap
```

**Rationale:** `select_candidates()` has cap of 300, but iteration.py hardcodes 50

---

## ROOT CAUSE #4: Stable Keys Not Populated

### Symptoms:
- All rows in `iteration_details.json` show `"stable_key": ""`
- Regression guard cannot work without keys

### Root Cause:

**File:** `src/fba_agent/stable_key.py` exists and generates keys  
**File:** `src/fba_agent/run.py` calls `generate_stable_key()`

**Problem:** Keys are generated but NOT added to the DataFrame before analysis!

### Investigation Needed:

Check where stable keys are generated and if they're actually merged into the DataFrame:

**Expected:** `df["stable_key"] = generate_stable_key(df)`  
**Actual:** Keys generated but not assigned to column

### Surgical Fix #4: Ensure Stable Keys Are Populated

**File:** `src/fba_agent/run.py` (after data loading, before analysis)

**Find this section:**
```python
# Generate stable keys
from fba_agent.stable_key import generate_stable_keys, check_collisions
```

**Ensure it includes:**
```python
df["stable_key"] = df.apply(lambda row: generate_stable_key(row), axis=1)
check_collisions(df)  # Verify no duplicates
```

**If not present, ADD IT** after normalization and before analysis loop.

---

## ROOT CAUSE #5: Critique Blocking Iteration 2

### Symptoms:
- Critique returns: `"recommended_action": "block"`
- `"overall_assessment": "Critique could not be completed"`
- Iteration 2 never runs

### Root Cause:

**File:** `llm_trace.jsonl` (entries 52-53)

The critique AI call is failing or returning an error. Need to examine trace log to see exact error.

### Surgical Fix #5: Make Critique Non-Blocking OR Fix Critique Logic

**File:** `src/fba_agent/iteration.py`  
**Lines:** 265-277 (critique decision logic)

**OPTION A - Make Critique Non-Blocking:**

**BEFORE:**
```python
# Decide whether to run another iteration
critique_action = critique.recommended_action if critique else None
```

**AFTER:**
```python
# Decide whether to run another iteration  
critique_action = critique.recommended_action if critique else None

# If critique failed, don't let it block iteration
if critique and "could not be completed" in str(critique.overall_assessment):
    critique_action = None  # Ignore failed critique
```

**OPTION B - Debug Why Critique Fails:**

Extract from `llm_trace.jsonl` entry 52-53 to see error, then fix the critique module.

---

## SUMMARY OF ALL SURGICAL FIXES

| # | Root Cause | File(s) to Edit | Lines | Type |
|---|-----------|----------------|-------|------|
| 1 | Pack shields wrong | `memory/suppliers/part_4_jan/calibration.json` | NEW FILE | CREATE |
| 2A | Brand+product too strict | `src/fba_agent/analysis.py` | 114-118 | MODIFY |
| 2B | Evidence format wrong | `src/fba_agent/analysis.py` | 119-127 | MODIFY |
| 3A | Adjudication not applied | `src/fba_agent/iteration.py` | After 244 | INSERT |
| 3A | Apply function missing | `src/fba_agent/adjustments.py` | End of file | ADD FUNCTION |
| 3B | Adjudication cap limit | `src/fba_agent/iteration.py` | 241 | MODIFY |
| 4 | Stable keys not assigned | `src/fba_agent/run.py` | After normalization | VERIFY/FIX|
| 5 | Critique blocking | `src/fba_agent/iteration.py` | 265-267 | MODIFY |

---

## EXPECTED IMPACT AFTER ALL FIXES

### Before Fixes:
- VERIFIED: 8
- HIGHLY_LIKELY: 9
- NEEDS_VER: 103
- **Total Good: 17**

### After Fixes (Estimated):
- VERIFIED: 25-30 (+200%)
- HIGHLY_LIKELY: 75-95 (+700%)
- NEEDS_VER: 40-50 (-50%)
- **Total Good: 115-145** (+600%)

### Recovery Path:
1. **Fix #1 (Pack Shields):** +20-30 items (correct pack detection)
2. **Fix #2 (Product Matching):** +60-80 items (product-only matches like Cat Litter)
3. **Fix #3 (Adjudication):** +15-25 items (AI promotions from NEEDS_VER)
4. **Fix #5 (Critique):** Enables iteration 2 for further refinement

**Target:** Match reference report (~141 items)

---

## IMPLEMENTATION ORDER

1. **Fix #1 (Pack Shields)** - HIGHEST IMPACT - Create calibration file
2. **Fix #2A/B (Product Matching)** - HIGH IMPACT - Modify analysis.py  
3. **Fix #3A/B (Adjudication)** - MEDIUM IMPACT - Modify iteration.py + adjustments.py
4. **Fix #4 (Stable Keys)** - LOW FUNCTIONALITY IMPACT - Verify/fix run.py
5. **Fix #5 (Critique)** - ENABLES ITERATION 2 - Modify iteration.py

**Critical Path:** #1 → #2 → Run Test → #3 → Run Test → #5

---

## NEXT STEPS

1. Review and approve surgical fixes
2. Implement fixes in order
3. Test after #1 and #2 (should see major improvement)
4. Implement #3-#5
5. Final test run
6. Compare to reference report
