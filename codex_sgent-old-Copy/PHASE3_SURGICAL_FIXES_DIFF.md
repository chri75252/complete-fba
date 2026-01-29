# PHASE 3 SURGICAL FIXES - DIFF FORMAT
**Date:** 2026-01-09
**Target:** `src - Copy old - Copy/fba_agent/analysis.py`

## Root Cause 1: Garbage Brand Extraction
**Problem:** `_extract_brand` blindly returns the first token, which may be a number ("3"), adjective ("Waterproof"), or generic word ("Glass").

**Fix Location:** Lines 16-23

### Current Code:
```python
def _extract_brand(title: str, brand_position: str) -> str | None:
    tokens = tokenize(title)
    if not tokens:
        return None
    if brand_position == "start":
        return tokens[0]
    # "mixed": still prefer first token as a deterministic anchor.
    return tokens[0]
```

### Fixed Code (DIFF):
```diff
def _extract_brand(title: str, brand_position: str) -> str | None:
+    # GARBAGE BRAND FILTER (Phase 3 Fix):
+    # These words should NEVER be treated as brands.
+    INVALID_BRAND_TOKENS = {
+        "3", "4", "5", "6", "10", "12", "20", "24", "40", "50", "100",  # Numbers
+        "SET", "PACK", "BOX", "BAG", "BOTTLE", "JAR", "TIN", "CAN",    # Containers
+        "LARGE", "SMALL", "MINI", "MEDIUM", "EXTRA", "BIG",            # Sizes
+        "WHITE", "BLACK", "RED", "BLUE", "GREEN", "GREY", "PINK",      # Colors
+        "WATERPROOF", "STAINLESS", "PLASTIC", "WOODEN", "METAL",       # Materials
+        "NEW", "PREMIUM", "BEST", "QUALITY", "PROFESSIONAL",           # Marketing
+        "CHRISTMAS", "BIRTHDAY", "HAPPY", "MEMORIAL",                  # Occasion
+        "GLASS", "RUBBER", "SILICONE", "FABRIC", "LEATHER",            # Materials
+    }
+
    tokens = tokenize(title)
    if not tokens:
        return None
-    if brand_position == "start":
-        return tokens[0]
-    # "mixed": still prefer first token as a deterministic anchor.
-    return tokens[0]
+    
+    # Try to find a valid brand token (skip garbage)
+    for token in tokens[:3]:  # Only check first 3 tokens
+        if token.upper() not in INVALID_BRAND_TOKENS:
+            return token
+    
+    # If all first 3 tokens are garbage, return None (no brand detected)
+    return None
```

---

## Root Cause 2: Brand Mismatch Blocking EAN Matches
**Problem:** The `different_brands_validated` block sets `bucket="FILTERED_OUT"` BEFORE the `if exact_ean_match:` block can override it. This causes EAN matches to still show brand mismatch warnings.

**Fix Location:** Lines 186-193 and Lines 237-259

### Current Code (Lines 186-193):
```python
    # EXCLUSION RULE FIRST (only if BOTH are validated known brands)
    if different_brands_validated:
        include_in_tables = False
        bucket = "FILTERED_OUT"
        track = "UNKNOWN"
        filter_reason = f"Different known brands detected ({brand_s} vs {brand_a}); products not compatible"
        #  Skip remaining analysis for this row by setting confirmed_match = False
        confirmed_match = False
```

### Fixed Code (DIFF):
```diff
    # EXCLUSION RULE FIRST (only if BOTH are validated known brands)
-    if different_brands_validated:
+    # PHASE 3 FIX: EAN Match OVERRIDES Brand Mismatch
+    if different_brands_validated and not exact_ean_match:
        include_in_tables = False
        bucket = "FILTERED_OUT"
        track = "UNKNOWN"
        filter_reason = f"Different known brands detected ({brand_s} vs {brand_a}); products not compatible"
        #  Skip remaining analysis for this row by setting confirmed_match = False
        confirmed_match = False
+    elif different_brands_validated and exact_ean_match:
+        # EAN Override: Brand mismatch warning, but still process as EAN match
+        confirmed_match = True  # Allow EAN logic to proceed
+        filter_reason = f"Brand mismatch ({brand_s} vs {brand_a}) - EAN override"
```

---

## Root Cause 3: Threshold Too High After Token Cleaning
**Problem:** The `NEEDS_VERIFICATION` threshold was raised to 0.40, but token cleaning reduced similarity scores. Items that were 0.30 now show as 0.15.

**Fix Location:** Line 281

### Current Code (Line 279-281):
```python
    elif not different_brands_validated and (
        partial_brand_match  # Brand in ONE title only
        or (similarity >= 0.40 and len(product_s & product_a) >= 2)  # LOWERED THRESHOLD (Phase 2 Fix)
    ):
```

### Fixed Code (DIFF):
```diff
    elif not different_brands_validated and (
        partial_brand_match  # Brand in ONE title only
-        or (similarity >= 0.40 and len(product_s & product_a) >= 2)  # LOWERED THRESHOLD (Phase 2 Fix)
+        or (similarity >= 0.20 and len(product_s & product_a) >= 2)  # PHASE 3: Return to 0.20 (safe with clean tokens)
    ):
```

---

## Root Cause 4: Brand Mismatch Logic Too Aggressive (Unknown vs Known)
**Problem:** If Supplier Brand is "Unknown" and Amazon Brand is "Known", we reject. But "Unknown" often means garbage was extracted (see Root Cause 1).

**Fix Location:** Lines 171-173

### Current Code:
```python
         # 2. Unknown vs Known (Generic vs Brand)
         elif not brand_s_known and brand_a_known:
             is_brand_mismatch = True
```

### Fixed Code (DIFF):
```diff
         # 2. Unknown vs Known (Generic vs Brand)
-         elif not brand_s_known and brand_a_known:
-             is_brand_mismatch = True
+         # PHASE 3: Removed. This rule creates too many false positives when
+         # brand extraction returns garbage. Let similarity/EAN decide instead.
+         # elif not brand_s_known and brand_a_known:
+         #     is_brand_mismatch = True
```

---

## Summary of All Fixes

| Root Cause | Location | Fix Description |
|------------|----------|-----------------|
| Garbage Brand Extraction | `_extract_brand` (L16-23) | Add `INVALID_BRAND_TOKENS` filter |
| EAN Override Missing | Brand Mismatch Block (L186-193) | Add `and not exact_ean_match` condition |
| Threshold Too High | NV Path (L281) | Lower from 0.40 to 0.20 |
| Unknown vs Known Too Strict | Brand Logic (L171-173) | Remove/Comment out rule |

---

## Expected Outcome After Fixes

| Metric | Phase 2 (Current) | Phase 3 (Projected) |
|--------|-------------------|---------------------|
| Accuracy | 67.4% | ~55-60% (slight drop expected) |
| Total Entries | 129 | ~250-300 (recovery of missed items) |
| Correct Matches | 127 | ~200+ (recovery target) |
| False Positives | 42 | ~80-100 (acceptable increase) |

The goal is to **recover the ~200 missed valid items** while maintaining **>50% accuracy**.
