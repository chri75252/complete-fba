# E2E Interaction Guide: Context Memory & Natural Language

This report demonstrates the capability of the FBA Agent System Chat UI following the implementation of the **Context Memory Fix**. 

By correctly maintaining conversational state across Streamlit reruns, the LLM can now sustain long, complex, and highly natural conversational threads. You no longer need to copy-paste Run IDs or exact file paths.

---

## Scenario 1: Category Run & Resumption (Conversational Memory)

This scenario proves the LLM can infer the target of actions like "cancel" and "continue" based entirely on conversational history.

**User:**
> "Start a category analysis for clearance-king.co.uk on: https://www.clearance-king.co.uk/smoking-products/lighters-accessories.html. Max products: 10."

**LLM Action:**
*   *Tool:* `enqueue_run`
*   *Result:* "I have enqueued the category analysis job for clearance-king.co.uk." (User clicks Approve).

**User:**
> "Actually, cancel the run."

**LLM Action:**
*   *Inference:* "the run" refers to the `last_run_id` injected into the prompt's `planner_hints`.
*   *Tool:* `cancel_run`
*   *Result:* "I have successfully cancelled the run. The cancellation marker has been placed." (User clicks Approve).

**User:**
> "Okay, continue it."

**LLM Action:**
*   *Inference:* "it" refers to the `sandbox_suffix` of the previously cancelled run.
*   *Tool:* `enqueue_run` with parameter `"sandbox_suffix": "sandbox_aebdad60"`
*   *Result:* "I have resumed the clearance-king run. The system will automatically pick up from where it left off."

---

## Scenario 2: Product List Generation & Refresh

This scenario demonstrates how the LLM remembers file paths it generated in earlier steps.

**User:**
> "Create a product list JSON containing these EANs: ['5010993836714', '5055579165464']. Save it as test_products_alpha.json."

**LLM Action:**
*   *Tool:* `write_output_file(rel_path="OUTPUTS/PRODUCTS_LISTS/test_products_alpha.json")`
*   *Result:* "I've generated the JSON product list and saved it to the products directory."

**User:**
> "Now start a product list refresh analysis for clearance-king.co.uk using that exact file."

**LLM Action:**
*   *Inference:* "that exact file" refers to the path generated in the previous step.
*   *Tool:* `enqueue_product_list_refresh(products_path="OUTPUTS/PRODUCTS_LISTS/test_products_alpha.json")`
*   *Result:* "I have enqueued a Product List Run (PLR) using the test file we just created."

---

## Scenario 3: Validation & Financial Review

This scenario shows how the LLM executes the complex Post-Run Audit without needing constant handholding.

**User:**
> *(Clicks the "🔍 Validate Last Run" UI Button)*

**LLM Action:**
*   *Inference:* Reads the `last_run_id` from the hidden UI prompt injection.
*   *Tool:* `validate_run_integrity`
*   *Result:* "Validation complete. 
    1. Cached Products: 10
    2. Linking Map Entries: 10
    3. Schema Valid: Yes.
    4. Financial Report: Generated successfully."

**User:**
> "Read that financial report for clearance-king and write a markdown summary detailing any products with an ROI > 10%."

**LLM Action:**
*   *Inference:* Knows the active supplier is `clearance_king`. 
*   *Tool 1:* `query_financial`
*   *Tool 2:* `write_output_file(rel_path="OUTPUTS/CONTROL_PLANE/reports/clearance_roi.md")`
*   *Result:* "I have analyzed the CSV data and generated the final markdown financial report for the Clearance King run."