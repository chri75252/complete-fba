# Surgical Fixes Plan - v4.3.0 Report Accuracy Issues
**Generated:** 2026-01-09 01:02
**Updated:** 2026-01-09 01:07  
**Status:** ✅ ALL FIXES APPLIED

---

## Executive Summary

This document contains surgical fixes for **5 critical root causes** identified during the agent run analysis. Each fix is presented in diff format with:
- Root cause description
- Impact assessment
- Exact file and line locations
- Before/After code diffs
- Testing verification steps

---

## Issue #1: EAN Match Priority Override Bug

### Root Cause
In `analysis.py`, the `different_brands_validated` check (lines 159-166) sets `bucket = "FILTERED_OUT"` **before** the EAN match check runs. This causes **19 exact EAN matches to be incorrectly filtered out** due to brand mismatch detection.

### Impact
- 19 rows with valid exact EAN matches categorized as `FILTERED_OUT`
- AI Critique correctly flagged as `EAN_MATCH_WRONG_BUCKET`
- Report shows only 15 VERIFIED instead of expected 34

### File: `src/fba_agent/analysis.py`

### Diff Fix

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -156,17 +156,22 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
     # Keep original check for reporting (but don't use for exclusion)
     different_brands = bool(brand_s and brand_a and brand_s != brand_a)
 
-    # EXCLUSION RULE FIRST (only if BOTH are validated known brands)
-    if different_brands_validated:
+    # CRITICAL FIX: EAN MATCH OVERRIDES BRAND MISMATCH
+    # Exact EAN matches MUST go to VERIFIED regardless of brand detection
+    # Only apply brand exclusion if there is NO exact EAN match
+    if different_brands_validated and not exact_ean_match:
         include_in_tables = False
         bucket = "FILTERED_OUT"
         track = "UNKNOWN"
         filter_reason = f"Different known brands detected ({brand_s} vs {brand_a}); products not compatible"
-        #  Skip remaining analysis for this row by setting confirmed_match = False
         confirmed_match = False
     else:
         # MATCHING LOGIC (MUCH more inclusive now)
         confirmed_match = (
             exact_ean_match  # Use combined strict+soft EAN match
             or (brand_match and product_type_match)  # Original: both brand and product  
             or (partial_brand_match and strong_product_match)  # NEW: partial brand + moderate product
             or (strong_product_match and len(product_s & product_a) >= 3)  # NEW: strong product without brand if 3+ tokens
             or (similarity >= 0.30 and len(product_s & product_a) >= 2)  # NEW: 30% similarity + 2 tokens
         )
+    
+    # SECOND FIX: Ensure exact EAN matches always set confirmed_match = True
+    if exact_ean_match:
+        confirmed_match = True
```

### Verification
After fix, run:
```python
# Count rows where supplier_ean == amazon_ean and bucket != "VERIFIED"
ean_mismatches = ledger[(ledger['supplier_ean'] == ledger['amazon_ean']) & 
                        (ledger['bucket'] != 'VERIFIED') & 
                        (ledger['bucket'] != 'FILTERED_OUT')]
assert len(ean_mismatches) == 0, f"Found {len(ean_mismatches)} EAN match misplacements"
```

---

## Issue #2: Pack Detection Failure - "Pack of N" Pattern

### Root Cause
The `pack.py` module does not correctly parse Amazon title patterns like:
- `Pack of 12`
- `(Pack of 6)`
- `24pc`
- `24 Piece`

The preflight calibration correctly identified keywords like `PK`, `PACK`, but the regex patterns don't capture `Pack of \d+` constructs.

### Impact
- Most items show `Pack Verdict: UNKNOWN`
- AUDITED OUT section is empty (adjusted profit not calculated correctly)
- Items like "GORILLA WOOD GLUE 236ML" matched to "Pack of 12" show no pack detection

### File: `src/fba_agent/pack.py`

### Diff Fix

```diff
--- a/src/fba_agent/pack.py
+++ b/src/fba_agent/pack.py
@@ -15,6 +15,15 @@ class PackInfo:
     traps: list[str] = field(default_factory=list)
 
 
+# Explicit "Pack of N" pattern - highest priority
+PACK_OF_PATTERN = re.compile(
+    r'\b(?:pack\s+of|pack\s*-?\s*of|packs?\s+of)\s*(\d+)\b',
+    re.IGNORECASE
+)
+
+# Parenthetical pack pattern: (Pack of 12), (12 Pack), (12)
+PAREN_PACK_PATTERN = re.compile(r'\((?:pack\s+of\s+)?(\d+)(?:\s*(?:pack|pc|pcs|pieces?))?\)', re.IGNORECASE)
+
 # Core pack patterns - these are definitive pack indicators
 CORE_PACK_PATTERNS = [
     # "Pack of N" or "N Pack" - very explicit
@@ -85,6 +94,23 @@ def parse_pack_quantity(title: str, naming_config: NamingConventionConfig | None
     if not title or not title.strip():
         return PackInfo(quantity=1, ambiguous=True)
 
+    # PRIORITY 1: Check for explicit "Pack of N" pattern first
+    pack_of_match = PACK_OF_PATTERN.search(title)
+    if pack_of_match:
+        qty = int(pack_of_match.group(1))
+        if qty > 0 and qty <= 500:  # Sanity check
+            return PackInfo(quantity=qty, ambiguous=False, source="pack_of_pattern")
+    
+    # PRIORITY 2: Check parenthetical patterns like "(Pack of 12)" or "(12)"
+    paren_match = PAREN_PACK_PATTERN.search(title)
+    if paren_match:
+        qty = int(paren_match.group(1))
+        # Only accept if it looks like a pack count, not a dimension
+        if qty > 0 and qty <= 200:
+            # Check it's not followed by dimension units
+            after_match = title[paren_match.end():paren_match.end()+10].lower()
+            if not any(dim in after_match for dim in ['cm', 'mm', 'inch', 'ml', 'oz', 'kg', 'g', 'l']):
+                return PackInfo(quantity=qty, ambiguous=False, source="paren_pattern")
+
     upper_title = title.upper()
     naming = naming_config or NamingConventionConfig()
```

### Verification
```python
from fba_agent.pack import parse_pack_quantity
from fba_agent.types import NamingConventionConfig

cfg = NamingConventionConfig()
assert parse_pack_quantity("Gorilla Wood Glue 236ml (Pack of 12)", cfg).quantity == 12
assert parse_pack_quantity("Pack of 6 Bowls", cfg).quantity == 6
assert parse_pack_quantity("Dekton 24pc Masonary Brick Line", cfg).quantity == 24
assert parse_pack_quantity("100 x 33 mm Foil Container", cfg).quantity == 1  # Dimension, not pack
```

---

## Issue #3: Bucket Name Inconsistency

### Root Cause
The bucket names `NEEDS_VERIFICATION` and `NEEDS VERIFICATION` (with space) are used inconsistently, causing:
- Split counts in `bucket_counts`: 36 + 9 = 45 total
- Rendering issues in report sections

### Impact
- Report reconciliation math is incorrect
- AI critique receives inconsistent data

### File: `src/fba_agent/analysis.py`

### Diff Fix

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -250,9 +250,9 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
     ):
         # Check if profit is sufficient for NEEDS_VERIFICATION (> £0.50)
         if adjusted_profit is not None and adjusted_profit > 0.50:
-            track = "NEEDS_VERIFICATION"
-            bucket = "NEEDS_VERIFICATION"
+            track = "NEEDS_VERIFICATION"  # Use underscore consistently
+            bucket = "NEEDS_VERIFICATION"  # Use underscore consistently
             include_in_tables = True
             if partial_brand_match:
                 filter_reason = f"Partial brand match ({brand_s or brand_a}) - requires verification"
```

### Additional Check: Search for all bucket assignments

```bash
grep -n "NEEDS.VERIFICATION" src/fba_agent/*.py
```

Ensure ALL occurrences use `NEEDS_VERIFICATION` (with underscore).

### File: `src/fba_agent/render.py`

```diff
--- a/src/fba_agent/render.py
+++ b/src/fba_agent/render.py
@@ -112,7 +112,8 @@ def render_phasea_report(
     verified_fo = included[(included["track"] == "VERIFIED") & (included["bucket"] == "FILTERED_OUT")]
     hl_rec = included[(included["track"] == "HIGHLY_LIKELY") & (included["bucket"] == "HIGHLY_LIKELY")]
     hl_fo = included[(included["track"] == "HIGHLY_LIKELY") & (included["bucket"] == "FILTERED_OUT")]
-    needs_ver = included[included["bucket"] == "NEEDS_VERIFICATION"]
+    # Handle both underscore and space variants to be safe
+    needs_ver = included[included["bucket"].isin(["NEEDS_VERIFICATION", "NEEDS VERIFICATION"])]
```

---

## Issue #4: Missing AUDITED OUT Entries

### Root Cause
In `analysis.py` lines 218-226, when `exact_ean_match=True` and `adjusted_profit <= 0`, the code sets:
- `bucket = "FILTERED_OUT"` ✓
- `filter_reason = "Adjusted profit <= 0..."` ✓
- **BUT does NOT set `include_in_tables = True`** ✗

This causes these rows to be excluded from the report's "VERIFIED - AUDITED OUT" section.

### Impact
- Reference report shows 7 AUDITED OUT entries
- Generated report shows 0 AUDITED OUT entries

### File: `src/fba_agent/analysis.py`

### Diff Fix

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -210,12 +210,14 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
     # Use combined EAN match (strict OR soft) for VERIFIED categorization
     if exact_ean_match:
         track = "VERIFIED"
-        # CRITICAL FIX: ALL exact EAN matches should be included in tables!
+        # CRITICAL: ALL exact EAN matches MUST be included in tables for visibility
         include_in_tables = True
         if cap_gate in {"fo_25_50", "fo_gt_50"}:
             bucket = "FILTERED_OUT"
             filter_reason = f"Capacity mismatch ({cap_gate})"
+            # Keep include_in_tables = True for AUDITED OUT section
         elif adjusted_profit is not None and adjusted_profit <= 0:
             bucket = "FILTERED_OUT"
             filter_reason = "Adjusted profit <= 0 after pack adjustment"
+            # CRITICAL FIX: Keep in tables for AUDITED OUT section
+            include_in_tables = True  # Explicit re-assertion
         elif ratio is not None and ratio < 1:
             bucket = "NEEDS_VERIFICATION"
             filter_reason = "Split candidate (supplier pack > Amazon pack)"
```

### Also fix the HIGHLY_LIKELY path (lines 236-240):

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -233,10 +233,11 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
         elif cap_gate in {"fo_25_50", "fo_gt_50"}:
             bucket = "FILTERED_OUT"
             filter_reason = f"Capacity mismatch ({cap_gate})"
+            include_in_tables = True  # Keep visible in AUDITED OUT
         elif adjusted_profit is not None and adjusted_profit <= 0:
             bucket = "FILTERED_OUT"
             filter_reason = "Adjusted profit <= 0 after pack adjustment"
-            # CRITICAL: Keep in tables for AUDITED OUT section
-            include_in_tables = True
+            # CRITICAL: Keep in tables for HIGHLY LIKELY - AUDITED OUT section
+            include_in_tables = True  # Explicit to ensure visibility
         # REMOVED pack_ambiguous check - strong matches should stay HIGHLY_LIKELY
         else:
             bucket = "HIGHLY_LIKELY"
```

---

## Issue #5: High-Profit Rows in FILTERED_OUT (903 "Different Brands")

### Root Cause
The filter reason shows **903 rows** filtered with "Different brands detected; products not compatible". However, many of these are because the first token of the title is incorrectly treated as a "brand".

Example: `ESSENTIAL PLASTIC 6 ICE CREAM BOWL` - "ESSENTIAL" is extracted as brand, but the Amazon product `Motorola razr 60 ultra...` has "Motorola" as brand → Different brands → FILTERED_OUT.

This is actually **correct behavior** for truly unrelated products, but the issue is that:
1. Some products that ARE related are getting filtered due to false brand detection
2. High-profit outliers (£500+) in FILTERED_OUT need manual review

### Impact
- 903 rows (85% of all rows) are in FILTERED_OUT due to brand mismatch
- Some may be legitimate matches with incorrect brand detection

### File: `src/fba_agent/analysis.py`

### Diff Fix (Tighten brand validation requirements)

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -146,11 +146,18 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
         len(product_s & product_a) >= 2  # At least 2 shared tokens
     )
     
-    # DIFFERENT_BRANDS: Only fire exclusion if BOTH are validated known brands
-    # Per ULTIMATE_FIX_PLAN: Random first words (like "151", "LG") should NOT trigger exclusion
+    # DIFFERENT_BRANDS: STRICT VALIDATION REQUIRED
+    # Only fire exclusion if:
+    # 1. BOTH brands are validated (found in known brands list)
+    # 2. AND there are NO shared product tokens (truly unrelated)
+    # 3. AND there is no partial overlap in title semantics
     different_brands_validated = bool(
         brand_s_validated and brand_a_validated  # BOTH must be known brands
         and brand_s and brand_a 
         and brand_s != brand_a
+        # NEW: Require ZERO product overlap to confirm truly different products
+        and len(product_s & product_a) == 0
     )
```

### Alternative: Add minimum product overlap requirement

```diff
--- a/src/fba_agent/analysis.py
+++ b/src/fba_agent/analysis.py
@@ -156,8 +156,15 @@ def analyze_row(row: pd.Series, config: MergedConfig, brand_aliases: dict[str, s
     # Keep original check for reporting (but don't use for exclusion)
     different_brands = bool(brand_s and brand_a and brand_s != brand_a)
 
-    # EXCLUSION RULE FIRST (only if BOTH are validated known brands)
-    if different_brands_validated and not exact_ean_match:
+    # EXCLUSION RULE: Multiple conditions must be met
+    # 1. Different validated brands
+    # 2. No exact EAN match
+    # 3. No strong product overlap (< 2 shared tokens)
+    should_exclude_for_brands = (
+        different_brands_validated 
+        and not exact_ean_match
+        and len(product_s & product_a) < 2  # Must have minimal product overlap
+    )
+    if should_exclude_for_brands:
         include_in_tables = False
         bucket = "FILTERED_OUT"
         track = "UNKNOWN"
```

---

## Summary Checklist

| # | Issue | File | Lines | Severity | Status |
|---|-------|------|-------|----------|--------|
| 1 | EAN match priority override | `analysis.py` | 159-166 | CRITICAL | ✅ APPLIED |
| 2 | Pack "Pack of N" detection | `pack.py` | 85-110 | HIGH | ✅ APPLIED |
| 3 | Bucket name inconsistency | `analysis.py`, `render.py` | Multiple | MEDIUM | ✅ APPLIED |
| 4 | AUDITED OUT include_in_tables | `analysis.py` | 218-240 | HIGH | ✅ APPLIED |
| 5 | False brand exclusion | `analysis.py` | 146-166 | MEDIUM | ✅ APPLIED |

---

## Recommended Application Order

1. **Issue #1** (EAN Priority) - Fixes 19 rows immediately
2. **Issue #4** (AUDITED OUT) - Enables visibility of filtered VERIFIED items
3. **Issue #2** (Pack Detection) - Fixes profit calculations
4. **Issue #3** (Bucket Names) - Fixes consistency
5. **Issue #5** (Brand Exclusion) - Reduces false positives

---

## Post-Fix Verification

After applying all fixes, run:
```bash
python -m fba_agent analyze --input "report\part1.xlsx" --supplier "test_v43_fixed" --enable-ai true
```

**Expected Changes:**
- VERIFIED count: 15 → ~34+
- VERIFIED - AUDITED OUT: 0 → ~7+
- FILTERED_OUT: 948 → ~880 (fewer false exclusions)
- Pack Verdict: Most "UNKNOWN" → actual pack ratios

---

**AWAITING USER APPROVAL BEFORE APPLYING FIXES**
