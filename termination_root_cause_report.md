# Critical Investigation Report: Premature System Termination (Category 2/328)

**Date:** November 25, 2025
**Status:** Root Cause Identified
**Severity:** Critical (Logic Flow Error)

## 1. Executive Summary
The system did **not crash**; it terminated gracefully ("Workflow completed successfully") after processing Category 2.
The root cause is a specific implementation in the `run()` method's resumption logic. When resuming from the `amazon_analysis` phase, the code executes the Amazon phase for the *current* category and then explicitly **returns** (exits) the entire workflow, instead of proceeding to the next category in the list.

This behavior effectively turns the system into a "single-category processor" when resuming from the Amazon phase.

---

## 2. Triangular Protocol Verification (3 Sources of Truth)

### Truth Source 1: The Logs (Behavioral Evidence)
**Evidence:** `run_custom_poundwholesale_20251125_083638.log` (and snippet provided in prompt)
*   **Observation:** The logs show the successful completion of Category 2.
*   **Key Log Line:** `2025-11-25 09:58:21,905 - __main__ - INFO - ✅ Workflow completed successfully`
*   **Context:** This line appears immediately after `CATEGORY_INDEX_TRACKER: Category completed ... -> next pci=3`.
*   **Conclusion:** The system state correctly advanced to Category 3, but the application process exited voluntarily with exit code 0.

### Truth Source 2: The Codebase (Implementation Evidence)
**Evidence:** `tools/passive_extraction_workflow_latest.py` (Method: `run`)
*   **Observation:** Lines ~2120-2130 (variable based on edits) contain the resumption routing logic.
*   **The Culprit Code:**
    ```python
    if resume_phase == "amazon_analysis":
        self.log.info("🔄 PHASE-AWARE GATING: Routing to Amazon analysis phase")
        # ... setup resume_ptr ...
        return await self._run_amazon_phase_from_resume(resume_ptr)  # <--- CRITICAL ERROR
    ```
*   **Analysis:** The keyword `return` forces the `run()` method to stop execution immediately after `_run_amazon_phase_from_resume` finishes. The `for` loop that iterates through the remaining 326 categories (which is located *below* this block) is never reached.

### Truth Source 3: State Persistence (Data Evidence)
**Evidence:** State logs and atomic save confirmation
*   **Observation:** `2025-11-25 09:58:21,885 - utils.fixed_enhanced_state_manager - INFO - ✅ CATEGORY_INDEX_TRACKER: Category completed ... -> next pci=3`
*   **Analysis:** The persistent state manager **did** its job. It recorded that Category 2 was done and the system should work on Category 3 next. The fact that the file saved successfully proves the logic flow reached the end of the category processing block but then "fell off a cliff" due to the `return` statement in the parent caller.

---

## 3. Root Cause Analysis
The logic for "Resume from Amazon Phase" was implemented as a **diversion** rather than a **re-entry**.

*   **Intended Behavior:** Resume Amazon phase for Cat 2 -> Finish Cat 2 -> Continue to Cat 3 (Supplier Phase) -> ... -> Cat 328.
*   **Actual Behavior:** Resume Amazon phase for Cat 2 -> Finish Cat 2 -> **EXIT PROGRAM**.

This is a regression introduced when "Phase-Aware Gating" was added. The developer assumed `_run_amazon_phase_from_resume` would handle the rest of the workflow, or simply forgot that `return` would bypass the primary category iteration loop.

---

## 4. Remediation Plan

**Constraint:** Do not "blindly integrate implementations."
**Approach:** We will modify the control flow to **remove the early return**. Instead of returning, we will let the code fall through to the main loop, but we must ensure the main loop knows to *skip* the parts of Category 2 that were already handled by the resume function, OR (better) refactor the resume logic to set up the state so the main loop can handle it naturally.

**Corrective Action:**
1.  Modify `tools/passive_extraction_workflow_latest.py`.
2.  Remove `return` from the `_run_amazon_phase_from_resume` call.
3.  Ensure that after `_run_amazon_phase_from_resume` completes (finishing Cat 2), the `category_urls` list is sliced or the loop is entered at the correct index (Cat 3) to continue processing.

**Note:** Since `_run_amazon_phase_from_resume` specifically handles the Amazon part of the *current* category, once it returns, that category is *done*. The workflow needs to proceed to the *next* category in the list.

**Detailed Fix Instruction for Developer:**
The `run()` method needs to be restructured. If `resume_phase == "amazon_analysis"`, we await the completion of that phase, and *then* we must proceed to the main loop. The main loop logic typically iterates over `category_urls`. We need to ensure that if we just finished Cat 2 via the resume handler, the main loop picks up at Cat 3.

*Current Code (Abstract):*
```python
if resume_phase == "amazon_analysis":
    return await self._run_amazon_phase_from_resume(...) # EXITS HERE
# ...
for category in category_urls:
    # process categories
```

*Fixed Code (Abstract):*
```python
if resume_phase == "amazon_analysis":
    await self._run_amazon_phase_from_resume(...)
    # RE-CALCULATE start_category_index based on the *new* state after that function finished
    # OR simply assume that function updated the state and we can fall through, 
    # provided we manage the loop iterator correctly.
```

However, a cleaner fix (less invasive) might be to ensure `_run_amazon_phase_from_resume` returns `True` (success), and then we modify the logic to:
```python
if resume_phase == "amazon_analysis":
    await self._run_amazon_phase_from_resume(...)
    # Start main loop from next category
    start_category_index += 1 
```

I will wait for your confirmation to apply this fix.
