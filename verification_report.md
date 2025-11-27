# Verification Report: Proposed Fixes for System Termination & Mismatch Handling

**Date:** November 25, 2025
**Status:** Verified & Approved
**Auditor:** AI Assistant

## 1. Executive Summary
I have reviewed the proposed remediation plan against the provided logs, system state, and codebase.
The findings are **confirmed** across all three sources of truth. The proposed fixes are logically sound, adhere to the "surgical fix" mandate (no new features, just correction of existing logic), and will correctly resolve both the premature termination and the potential for data loss due to cache/manifest mismatches.

## 2. Issue Verification (Triangular Protocol)

### Issue A: Amazon Resume Exits Prematurely
*   **Claim:** System processes one category in Amazon resume mode and then exits.
*   **Source 1 (Code):** `tools/passive_extraction_workflow_latest.py:2042` (approx) clearly shows `return await self._run_amazon_phase_from_resume(...)`. The `return` keyword terminates the `run()` method immediately after the resume task returns, preventing the script from reaching the main category loop.
*   **Source 2 (Logs):** `run_custom_poundwholesale_20251125_083638.log` ends with `Workflow completed successfully` immediately after Category 2 completion. There is no attempt to start Category 3.
*   **Source 3 (State):** `angelwholesale_co_uk_processing_state.json` shows `persistent_category_index: 3`. This confirms the system state *advanced* correctly, but the runtime process *stopped*.
*   **Verdict:** **CONFIRMED**.

### Issue B: Denominator Mismatch (401 vs 397)
*   **Claim:** Category 2 was marked complete despite having 4 missing products (401 discovered vs 397 cached).
*   **Source 1 (State):** `processing_state.json` explicitly records `"https://angelwholesale.co.uk/Category/All-Baby-and-child": 401` in `frozen_category_denominators`.
*   **Source 2 (Logs):** Logs show `CATEGORY QUEUE ... size=397`. This confirms the Amazon phase only loaded the 397 cached items.
*   **Source 3 (Code):** The finalizer in `_run_amazon_phase_from_resume` checks `if ... done >= total`. Here, `total` is derived from the *queue length* (397), not the *frozen denominator* (401). Since 397/397 processed is "100% of the queue", the logic incorrectly allowed completion.
*   **Verdict:** **CONFIRMED**.

## 3. Plan Validation

### Fix 1: Remove Early Return
**Proposed Change:**
```python
# Remove 'return'
await self._run_amazon_phase_from_resume(resume_ptr)
# Reload state pointers
...
# Log continuation
```
**Logic Check:**
1.  Removing `return` allows execution to fall through.
2.  The next major block in `run()` is the call to `_extract_supplier_products`.
3.  `_extract_supplier_products` iterates through *all* categories.
4.  Crucially, `_extract_supplier_products` checks `persistent_category_index` (PCI) at the start of its loop.
5.  Since `_run_amazon_phase_from_resume` updates the PCI to 3 (confirmed by State evidence), `_extract_supplier_products` will correctly skip Cat 1 and Cat 2, and begin processing Cat 3.
**Safety:** High. This restores the intended "resume and continue" behavior.

### Fix 2: Denominator Mismatch Guard
**Proposed Change:**
```python
frozen_denom = self.state_manager.get_frozen_denominator(category_url) or 0
if frozen_denom and total < frozen_denom:
    self.log.error(...)
    raise RuntimeError(...)
```
**Logic Check:**
1.  It uses `get_frozen_denominator` (existing method).
2.  It compares `total` (cache queue size) against `frozen_denom` (manifest size).
3.  If `cache < frozen`, it raises `RuntimeError`.
4.  **Outcome:** The system crashes/stops *safely* for that category instead of marking it complete with missing data. This forces the user to investigate or re-run the supplier phase to fill the cache gap (401 - 397 = 4 missing items).
**Safety:** High. It prevents silent data loss (the "Partial Mismatch" bug).

## 4. Conclusion
The analysis is accurate. The plan addresses the root causes directly without introducing complex new "auto-fix" features that could be unstable.

**Recommendation:** Proceed with the application of the diffs exactly as outlined in the prompt.
