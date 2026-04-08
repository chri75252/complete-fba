# REVERT TRACKING — product_list_log_aesthetic_fixes_20260408

**Date:** 2026-04-08
**Files changed:**
- `control_plane/run_product_list_refresh.py`
- `control_plane/tools/tool_param_validation.py`

To fully revert all changes below:
```
cp backup/product_list_log_aesthetic_fixes_20260408/control_plane/run_product_list_refresh.py \
   control_plane/run_product_list_refresh.py

cp backup/product_list_log_aesthetic_fixes_20260408/control_plane/tools/tool_param_validation.py \
   control_plane/tools/tool_param_validation.py
```

---

## Summary of Changes (4 fixes)

### Fix A — current_phase state field accuracy
**File:** `control_plane/run_product_list_refresh.py`
**Location:** Inside the category loop, between the existing `state_manager.save_state_atomic()` call and `for _idx, product in enumerate(source_products, start=1):` (Phase 2 Amazon loop).

**Added:**
```python
# Fix A (20260408): Reflect actual phase before entering Amazon analysis loop.
sp["current_phase"] = "amazon_analysis"
```

**Why:** `current_phase` remained `"supplier"` in the state file throughout Phase 2 execution. Purely cosmetic — resumption logic does not read this field. No impact on processing.

**To revert Fix A only:** Remove the `sp["current_phase"] = "amazon_analysis"` line and its comment.

---

### Fix B1 — Log format aesthetics (remove FIX 3 prefix, add evidence block)
**File:** `control_plane/run_product_list_refresh.py`
**Location 1:** Inside the category loop, the per-category STEP 1/STEP 2/Invariant/RESUME STATE block.
**Location 2:** Startup cached_keys log line (~line 517).

**Changes:**
- `FIX 3 STEP 1 - LINKING MAP CHECK:` → `STEP 1 - LINKING MAP CHECK:`
- `FIX 3 STEP 2 - PRODUCT CACHE CHECK:` → `STEP 2 - PRODUCT CACHE CHECK:`
- `FIX 3 Filter Invariant:` → `Filter Invariant:` (kept as simple line) + `FILTER INVARIANT VALIDATED:` multi-line block after fast-forward
- Added `FILE-BASED RESUME CALCULATION:` multi-line evidence block after invariant
- `FIX 3 RESUME STATE:` → `RESUME STATE:`
- `FIX 3 STEP 2 startup:` → `STEP 2 startup:`
- Invariant failure now logs at ERROR level instead of INFO

**Why:** Matches the main workflow (PassiveExtractionWorkflow) log format for consistency in diagnostic output.

**To revert Fix B1 only:** Restore the `FIX 3 ...` prefixed log lines and remove the FILTER INVARIANT VALIDATED / FILE-BASED RESUME CALCULATION blocks. See backup file for exact original content.

---

### Fix B2 — Suppress rapid-fire state save burst in skip path
**File:** `control_plane/run_product_list_refresh.py`
**Location:** Inside the Phase 2 Amazon loop skip check (~line 857).

**Changed:**
```python
# Before:
if _idx % 10 == 0 or _idx == len(source_products):
    state_manager.save_state_atomic()

# After:
if _idx == len(source_products):
    state_manager.save_state_atomic()
```

**Why:** When all products in a category are already processed (full=0), the skip condition fired 46+ times within 200ms producing 46 identical `(27 entries) saved successfully` log lines. State is still saved once at end of skip pass and again by `_finalize_refresh_run`.

**To revert Fix B2 only:** Restore `if _idx % 10 == 0 or _idx == len(source_products):`.

---

### Fix C — tool_param_validation.py timeout default
**File:** `control_plane/tools/tool_param_validation.py`
**Location:** Line 406 inside `_validate_product_list_refresh` (or equivalent validation function).

**Changed:**
```python
# Before:
timeout_seconds = 4200

# After:
timeout_seconds = 216000  # 60 hours — matches worker.py default for product_list_refresh
```

**Why:** Residual 70-minute default posed risk for jobs submitted via this validation path. Aligned with `worker.py` default of 216000 seconds (60 hours).

**To revert Fix C only:** Change `216000` back to `4200`.

---

## Prior Fixes Unchanged

All fixes applied in previous sessions (Fix 1, Fix 2, Fix 3, Fix A, Fix B, Fix C, Fix D, Fix 5) remain intact.
