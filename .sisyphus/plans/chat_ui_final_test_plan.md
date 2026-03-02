# Comprehensive Chat UI End-to-End Test Plan
**Date:** 2026-02-26
**Target:** MiniMax M2.5 via Streamlit Chat UI (`http://localhost:8501`)
**Goal:** Verify the Supplier Onboarding Skill integration, test Category Run resumption (with timeout logic), and re-verify the critical legacy Chat UI functionalities to ensure zero regressions.

---

## 🚀 Pre-requisites: How to Launch the Environment

Before starting the tests, you must have the system fully operational according to `docs/CONCISE_LAUNCH_GUIDE.md`. The user has already started the Chrome CDP session.

**Terminal 1: Start the Dashboard**
Ensure you are using the OpenCode provider configuration (already set in `.env` or system environment).
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python dashboard\run_dashboard.py
```
*Wait for the dashboard to initialize and open `http://localhost:8501` in your browser.*

**Terminal 2: Start the Worker**
This executes the queued jobs (like the onboarding wizard or FBA runs).
```bat
cd /d "C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
python -m control_plane worker
```

---

## 🟢 Test 1: Supplier Onboarding Skill Execution
**Aspect Tested:** The LLM's ability to read external skill markdown files, read user text files, generate JSON payloads, output them to the staging directory, and invoke the backend `supplier_onboarding_wizard.py` securely.

**Execution Steps:**
1.  **Prompt:** *"I want to onboard a new supplier using the onboarding skill. The domain is stationerywholesale.co.uk. The raw categories are saved in `setup/stationerywholesale/stationerywholesale_categories.txt`. The selectors are saved in `config/supplier_configs/stationerywholesale.co.uk.json`. No login required."*
2.  **Wait for LLM:** The LLM should automatically execute a multi-tool chain:
    *   `read_repo_file` on the SKILL.md.
    *   `read_repo_file` on the setup `.txt` and `.json` files.
    *   `write_output_file` to drop the combined payload into `OUTPUTS/CONTROL_PLANE/jobs/onboarding_staging/wizard_input_stationerywholesale.json`.
    *   `enqueue_onboarding` with the correct `supplier_domain`.
3.  **Action:** The worker in Terminal 2 should pick up the job and execute the wizard.
4.  **Verification:** Check the project root. Ensure `run_custom_stationerywholesale-co-uk.py` was successfully generated, and the system config was atomically updated.

---

## 🟢 Test 2: Category Run Interruption & Resumption (With Delay)
**Aspect Tested:** The `sandbox_suffix` schema fix, Chat memory injection (`last_run_id`), and robust state resumption logic ensuring product counters carry over.

**Execution Steps:**
1.  **Prompt:** *"Start a category analysis for clearance-king.co.uk on: https://www.clearance-king.co.uk/smoking-products/lighters-accessories.html. Max products: 10."*
2.  **Action:** Let the worker run. **WAIT EXACTLY 45 SECONDS.** (This delay guarantees the system has enough time to initialize Chrome, log in, process the first few products, and save a non-zero progress state).
3.  **Prompt:** *"Cancel the run immediately."*
4.  **Verification:** Check `OUTPUTS/CACHE/processing_states/`. Ensure a state file exists for the cancelled run and `supplier_products_completed` is > 0.
5.  **Prompt:** *"Resume the cancelled run so we can finish analyzing the remaining products."*
6.  **Verification:** The LLM should fire `enqueue_run` and explicitly pass the matching `"sandbox_suffix"`. The worker log should state: `RESUMPTION POINT CONFIRMED: Starting from category index X at product Y`.

---

## 🟢 Test 3: Product List Generation & Refresh
**Aspect Tested:** Regression check for JSON file writing and `enqueue_product_list_refresh` execution using chat memory context.

**Execution Steps:**
1.  **Prompt:** *"Create a product list JSON containing these EANs: ['5010993836714', '5055579165464']. Save it as `test_products_alpha.json` in the appropriate directory for product list analysis."*
2.  **Verification:** The LLM uses `write_output_file`. The file appears in `OUTPUTS/PRODUCTS_LISTS/`.
3.  **Prompt:** *"Great. Now start a product list refresh analysis for clearance-king.co.uk using that exact file."*
4.  **Verification:** The LLM uses `enqueue_product_list_refresh`. Verify the generated job in `pending/` maps `products_path` correctly without needing absolute path reiteration.

---

## 🟢 Test 4: Financial Query Routing & Reporting
**Aspect Tested:** Validation of explicit system instructions preventing the LLM from attempting to use `read_repo_file` on massive financial CSVs, forcing it to use the optimized pandas tool.

**Execution Steps:**
1.  **Prompt:** *"Look at the financial reports for efghousewares.co.uk (the main workflow, not a sandbox). Find me how many products have a positive ROI."*
2.  **Verification:** The LLM MUST use the `query_financial` tool. If it attempts `read_repo_file`, the test fails.
3.  **Prompt:** *"Write a detailed Markdown report summarizing those financial findings. Save it to the control plane reports folder."*
4.  **Verification:** The LLM writes to `OUTPUTS/CONTROL_PLANE/reports/efghousewares_financial_summary.md`.

---

## 🟢 Test 5: Dynamic Expected Outputs & Large File Reading
**Aspect Tested:** Fix validation for the `too_large` error hallucination, and verifying the LLM predicts output files by reading the codebase rather than relying on a static template.

**Execution Steps:**
1.  **Prompt:** *"Use read_repo_file to read the entire `run_custom_clearance_king.py` script. Tell me what the logger base name is."*
2.  **Verification:** The LLM uses `read_repo_file` with a `max_bytes` limit large enough to ingest the file (the schema allows up to 1MB now). It accurately returns the logger base name without failing.
3.  **Prompt:** *"If I run that script, what files will it produce when it finishes?"*
4.  **Verification:** The LLM dynamically outlines the processing state, linking map, and cache files based on the workflow logic, avoiding generic templates.

---

## 🟢 Test 6: System Output Discovery
**Aspect Tested:** The new `get_run_outputs` tool utility.

**Execution Steps:**
1.  **Prompt:** *"Scan the system and tell me exactly what output files were produced by the run we did in Test 2."*
2.  **Verification:** The LLM leverages chat memory to retrieve the run ID, executes `get_run_outputs`, and retrieves all JSONs, logs, and CSVs linked to that run's sandbox ID.