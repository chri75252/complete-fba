# PHASE 2 TROUBLESHOOTING & ROOT CAUSE ANALYSIS REPORT
**Date:** 2026-01-09
**Run ID:** 20260109_002917

## 1. Execution & File Integrity
**Status:** ✅ **PASSED**
- All required files were generated in the correct order.
- `run_summary.json` confirms "status": "OK" and correct config usage.
- `coverage_ledger.csv` contains 3063 rows, matching the input file size.

## 2. Identified Logic Conflicts
**Finding:** `VERIFIED` rows containing Brand Mismatch Warnings.
**Location:** `src/analysis.py`
**Observation:** Rows like `ELBOW GREASE (Brand S) vs 3 (Brand A)` are marked as **VERIFIED**.
**Cause:**
- The `different_brands_validated` block sets `bucket="FILTERED_OUT"`.
- BUT, the subsequent `if exact_ean_match:` block **unconditionally** sets `bucket="VERIFIED"` and `include_in_tables=True`.
- **Impact:** This is technically "safe" (EAN matches *should* probably override soft brand mismatches), but the warning "Different known brands detected" indicates an underlying issue with brand detection.

## 3. PRIMARY ROOT CAUSE OF MISSED ITEMS
**The "False Negative" Explosion (Loss of ~238 valid items)**

The analysis identifies a critical failure chain:

### A. Garbage Brand Detection (The Source)
The `_extract_brand` logic (or Brand Detector) is blindly extracting the first token(s) or common words as "Brands" when a real brand is missing or misplaced.
- **Evidence from Report:**
  - `Different known brands detected (ELBOW vs 3)` -> Amazon Title started with "3 x ...". System thought "3" was the Brand.
  - `Different known brands detected (151 vs 3)` -> Amazon Title started with "3 Spray...". System thought "3" was the Brand.
  - `Different known brands detected (MEMORIAL vs WATERPROOF)` -> Amazon Title started with "Waterproof...". System thought "Waterproof" was the Brand.
  - `Different known brands detected (GLASS vs ALPINA)` -> Supplier Title started with "GLASS...". System thought "GLASS" was the Brand.

### B. Fail-Closed Logic Amplification (The Mechanism)
The Phase 2 "Fail-Closed" logic was implemented to strictly reject mismatches:
- **Rule:** `if brand_s_known and brand_s != brand_a: Reject`
- **Scenario:**
  - Supplier Brand: "ELBOW GREASE" (Known/Valid)
  - Amazon Brand: "3" (Garbage/False Positive)
  - **Result:** "ELBOW GREASE" != "3" -> **REJECTED (FILTERED OUT)**
- **Impact:** Hundreds of valid matches were rejected because the system trusted the "Garbage Brand" as a definitive signal to kill the match.

**Previous Behavior (Phase 1):** The "Fail-Open" logic ignored these mismatches, allowing the text similarity (which was high) to pass the item as `HIGHLY LIKELY`.
**Current Behavior (Phase 2):** The "Fail-Closed" logic correctly identified a mismatch *according to the data it had*, but the data (Brand A = "3") was wrong.

## 4. SECONDARY ROOT CAUSE: "Double Penalty" on Needs Verification
**Observation:** `NEEDS VERIFICATION` bucket dropped from 98 to 2 items.
**Cause:**
1.  **Token Cleaning:** We removed brand tokens (e.g. "CHEF", "AID") from product tokens. This *lowered* the Jaccard similarity scores because fewer matching tokens remained.
2.  **Threshold Raising:** Simultaneously, we *raised* the required threshold from 0.25 to 0.40.
**Impact:** Valid matches that previously scraped by with 0.30 similarity (due to matching brand tokens) now dropped to ~0.15 (no brand tokens) AND faced a higher hurdle (0.40). They were all wiped out.

## 5. Summary of Findings
The Phase 2 Agent logic works *correctly* according to its rules, but it exposed the **poor quality of the underlying Brand Detection**.

1.  **Strict EAN Logic:** Working (Correctly moved soft matches to HL).
2.  **Fail-Closed Gate:** Working *too well* (Rejecting valid items because of garbage brand inputs like "3", "Set", "Pack").
3.  **Token Cleaning:** Working, but reduced similarity scores necessitates a *lower* threshold, not higher.

## 6. Required Action Plan (For Next Iteration)
To fix the "Missed Items" (Recall) without re-introducing "Noise" (Precision):

1.  **Fix Brand Extraction**: The `_extract_brand` function MUST ignore numbers ("3"), common adjectives ("Waterproof", "Large"), and generic containers ("Pack", "Set") as potential brands.
2.  **Trust Hierarchy**: If `exact_ean_match` is True, it MUST override Brand Mismatch (currently happening by accident, but should be explicit).
3.  **Threshold Correction**: Lower `NEEDS_VERIFICATION` threshold back to **0.20 or 0.25** to account for the cleaner (but smaller) token sets.
