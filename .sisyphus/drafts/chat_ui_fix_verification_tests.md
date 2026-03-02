# Chat UI Fix Verification & Resilience Tests
**Date**: 2026-02-25
**Target**: MiniMax M2.5 via Chat UI
**Objective**: Validate the fixes applied to the `read_repo_file` limit hallucination and the `sandbox_suffix` schema omission. Ensure category resumption legitimately processes products by introducing deliberate execution delays.

---

## 🟢 Test 1: Category Run Resumption (With Delays & Products)
**Purpose**: Verify that resuming a cancelled category run accurately retains the previous state *and* successfully extracts products (unlike the previous test on an empty category).

**Step 1: Enqueue Populated Category Run**
*   **Prompt**: *"Start a new category analysis for clearance-king.co.uk on this category: https://www.clearance-king.co.uk/smoking-products/lighters-accessories.html. Set the max products to 10."*
*   **Expected UI Output**: Job queued successfully.
*   **Action**: Start the worker. **WAIT EXACTLY 45 SECONDS.** (This ensures the worker actually navigates, logs in, and processes the first chunk of products).

**Step 2: Interrupt the Run**
*   **Prompt**: *"Cancel the run immediately."*
*   **Expected UI Output**: Run cancelled successfully.
*   **Action**: Wait for the worker to shut down. Verify that a `processing_state` JSON was generated and `supplier_products_completed` is > 0.

**Step 3: Resume the Run**
*   **Prompt**: *"Resume the cancelled run so we can finish analyzing the remaining products."*
*   **Expected UI Output**: The LLM executes `enqueue_run`. Critically, the `params` JSON **MUST** contain the `sandbox_suffix` key matching the previous run.
*   **Action**: Start the worker. Monitor the logs to verify it prints `RESUMPTION POINT CONFIRMED: Starting from category index X at product Y`.

---

## 🟢 Test 2: Large File Read Fix (`too_large` error)
**Purpose**: Verify the LLM no longer hallucinates a 200,000-byte limit (or smaller) when using `read_repo_file`, and successfully reads mid-sized scripts.

**Step 1: Read Mid-Sized Script**
*   **Prompt**: *"Use read_repo_file to read the entire `run_custom_clearance_king.py` script. Tell me what the logger base name is."*
*   **Expected UI Output**: The LLM successfully executes the tool without restricting its own `max_bytes` to tiny amounts (since the schema now says 1,000,000). It should return the exact logger name without a `too_large` error.

---

## 🟢 Test 3: Financial Routing Validation (Regression Check)
**Purpose**: Re-verify that financial routing wasn't broken by schema updates.

**Step 1: Query Financial Data**
*   **Prompt**: *"Query the financial reports for clearance-king.co.uk (sandbox). How many products have >1% ROI?"*
*   **Expected UI Output**: The LLM executes `query_financial` (NOT `read_repo_file`) and returns the row count.

---

## 🟢 Test 4: Write Output File Gating (Regression Check)
**Purpose**: Ensure the LLM can write outputs, but only to allowed directories.

**Step 1: Attempt Illegal Write**
*   **Prompt**: *"Write a markdown file to the `config/` directory summarizing the financial results."*
*   **Expected UI Output**: The tool execution fails with `write_path_not_allowed`, and the LLM informs the user it can only write to `OUTPUTS/CONTROL_PLANE/reports` or `PRODUCTS_LISTS`.

**Step 2: Attempt Legal Write**
*   **Prompt**: *"Okay, write it to the reports folder instead."*
*   **Expected UI Output**: Tool executes successfully. The file appears in `OUTPUTS/CONTROL_PLANE/reports/`.