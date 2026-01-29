# New Supplier Analysis Workflow & Guide

This master guide details the end-to-end process for analyzing a new supplier website using the **Amazon FBA Agent System**. It covers strict onboarding protocols, system configuration, automated execution, and final financial analysis.

---

## 🏗️ Phase 1: Supplier Onboarding (The Skill)

**Core Tool:** `.claude/skills/supplier-onboarding`  
**Reference:** `SKILL.md` inside the skill directory.

### 1.1. Data Preprocessing (Manual)
Before generating any code, you must manually gather and validate the supplier's structure:
1.  **Categories List:** Collect all category URLs you intend to scrape (`http://...`). Save as `setup/{supplier}_categories.txt` (optional but recommended).
2.  **Selectors:** Identify CSS selectors using **Chrome DevTools** or the **Chrome DevTools MCP**.
    *   **Product Container** (`.product-item`): The specific element wrapping a single product card.
    *   **Title** (`h2.title`): The product name.
    *   **Price** (`span.price`): The **wholesale** price (excluding VAT if possible, or note it).
    *   **Image** (`img.product-image`): The main product image URL.
    *   **EAN/Barcode**: Often hidden or on the detail page. If absent, the system relies on title matching.
    *   **Next Page / Pagination** (`a.next`): Crucial for traversing categories.

> **💡 Tips for Selectors:**
> *   **Verification:** Open Chrome Console (F12) and type `document.querySelectorAll('.your-selector')`. Ensure it highlights the correct elements.
> *   **Standard CSS Only:** The system uses `BeautifulSoup`, so avoid Playwright pseudo-selectors like `:text("Next")` or xpath. Use `a.next_page` or similar class-based selectors.

### 1.2. The Wizard Script
The system includes a wizard to automate boilerplate creation.
*   **Script:** `utils/supplier_onboarding_wizard.py`
*   **Command:**
    ```bash
    python utils/supplier_onboarding_wizard.py --domain "example.com" --mode generate --authentication-required false
    ```
    *(Add `--authentication-required true` if login is needed)*

### 1.3. Mandatory File Verification & Customization
The wizard generates templates. **You must manually review and finalize them.**

| File | Purpose | Customization Action |
| :--- | :--- | :--- |
| `run_custom_{supplier}.py` | **Launcher Script**. Entry point for the run. | **Verify Imports:** Check that `tools.{supplier}.supplier_authentication_service` is imported if auth is used. **Verify Config:** Ensure `workflow_config` loads the correct key. |
| `config/supplier_configs/{domain}.json` | **Selector Config**. Defines how to scrape. | **Refine Selectors:** Ensure `price_selector` and `next_page_selector` are robust. |
| `tools/{supplier}/supplier_authentication_service.py` | **Auth Helper**. Handles login logic. | **CRITICAL (If Auth=True):** You **MUST** implement the `login()` and `is_authenticated()` methods manually. The wizard only creates the file structure. |
| `config/{supplier}_workflow_categories.json` | **Category List**. | **Verify URLs:** Ensure no "test" or "example" URLs remain. |

---

## 🛠️ Phase 2: Script Refinement & Logic

### 2.1. Expected Scripts & Logic
*   **`run_custom_{supplier}.py`**:
    *   Initializes `BrowserManager` (Connects to Chrome on port 9222).
    *   Loads `PassiveExtractionWorkflow`.
    *   **Why Edit?** Sometimes you need to add specific `user_agent` strings or headers to `BrowserManager` if the site blocks default requests.
*   **`tools/configurable_supplier_scraper.py`**:
    *   The core scraping engine.
    *   **Standard Pagination:** It assumes `?page=N`.
    *   **Why Edit?** If the supplier uses `/page/N/` or "Load More" buttons, you may need to override `_iterate_pages` or `_get_next_page_url` in a custom subclass (e.g., `tools/{supplier}/custom_scraper.py`).

### 2.2. Pre-Launch Checks
1.  **Chrome Debug Mode:**
    ```bash
    chrome --remote-debugging-port=9222 --user-data-dir=C:\temp\chrome-debug
    ```
2.  **Auth Test:** Run the auth helper in isolation to confirm login works.
3.  **Config Validation:** Ensure `total_categories` in your JSON config matches the actual number of URLs.

---

## ⚙️ Phase 3: System Configuration & Workflow

### 3.1. Critical `config/system_config.json` Variables
*   **`hybrid_processing.enabled`**: **MUST BE TRUE.** This enables the modern "Supplier -> Amazon -> Next Category" flow (Freeze-Mark-Resume architecture).
*   **`processing_limits`**:
    *   `min_price_gbp`: Filter out cheap items (e.g., < £0.50).
    *   `max_products_per_category`: Safety stop (e.g., 2000).
*   **`supplier_cache_control`**:
    *   `update_frequency_products`: Save extraction progress every N products (e.g., 5).
*   **`performance.timeouts`**: Increase `page_load_timeout_ms` (e.g., 40000) for slow supplier sites.

### 3.2. System Workflow Summary
1.  **Discovery:** Scrapes the Category Page -> Extracts Product URLs.
2.  **Manifesting:** Saves ALL discovered URLs to `OUTPUTS/CACHE/manifests/`. **Freezes** the total count.
3.  **Filtering:** Checks `linking_map` (already done?) and `product_cache` (needs update?).
4.  **Extraction:** Scrapes supplier details (Price, Title, Images) for new items.
5.  **Amazon Analysis:** Matches EAN/Title against Amazon API (via Keepa/SellerAmp extensions).
6.  **Financials:** Calculates Profit/ROI.
7.  **Transition:** Moves to the next category.

---

## 🚀 Phase 4: Execution & Outputs

### 4.1. Launching
```bash
python run_custom_{supplier}.py
```

### 4.2. Expected Output Files
| Path | File | Purpose | Save Freq |
| :--- | :--- | :--- | :--- |
| `OUTPUTS/CACHE/processing_states/` | `{supplier}_processing_state.json` | **Single Source of Truth** for resumption. Tracks Category Index & Product Index. | Every Item |
| `OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier}/` | `linking_map.json` | The "Database" of matches. Maps Provider URL -> ASIN. | Batch (1-5) |
| `OUTPUTS/cached_products/` | `{supplier}_products_cache.json` | Raw scraped HTML data. | Batch (1-10) |
| `OUTPUTS/FBA_ANALYSIS/financial_reports/` | `{timestamp}.csv` / `.xlsx` | Preliminary financial dump (optional). | Configured |

### 4.3. Dashboard Monitoring
```bash
streamlit run dashboard/app_fixed.py
```
*   **System Health:** Indicators for "State File", "Data Loading", and "Phases".
*   **Progress:** Watch "System Progression (Category X / Y)" and "Category Progress".

---

## 📊 Phase 5: Financial Analysis (The Prompt)

**Goal:** Convert raw data into a decision-quality Buying Report using the AI Agent.

### 5.1. The Prompt File
*   **Path:** `RESERACH\REPORT\FINANCIAL REPORT PROMPT ANALYSIS.MD`
*   **Alternative:** `finale\part 2\PROMPT_V3_RECALL_MAXIMIZED.md`
*   **Key Logic:** "Identify TRUE profitable opportunities while AGGRESSIVELY filtering false positives."

### 5.2. Execution Instructions
Provide the Agent (Codex/Claude) with the **Final Financial Report** (Excel/CSV) and the **Prompt File**.

**Instruction to Agent:**
> "I want you to analyze the financial report at `[generated_report_path]`.
> Execute the analysis logic defined in `RESERACH\REPORT\FINANCIAL REPORT PROMPT ANALYSIS.MD`.
>
> **Mandatory Outputs:**
> 1.  `COMPREHENSIVE_MANUAL_FBA_REPORT.md`: A structured markdown report.
> 2.  **Reconciliation Table:** Proof that (Verified + Likely + Excluded) = Total Rows.
> 3.  **Filtered-Out Sections:** Explicitly list items excluded due to Pack Size or EAN Mismatch.
>
> **Criteria:**
> *   **Recall-First:** If uncertain, route to 'NEEDS VERIFICATION'.
> *   **Strict EAN:** Validation must check checksums.
> *   **Pack Logic:** Watch for 'Dimension Traps' (e.g., '9x9 inch' is NOT a pack of 81).
> *   **Final List:** MUST have Sales > 0 and Net Profit > 0."

### 5.3. Final Check
Before launching the system:
- [ ] **State Clean:** If this is a *new* run, ensure `processing_state` is empty or deleted to start fresh.
- [ ] **Config Correct:** `total_categories` in config matches reality.
- [ ] **Dashboard Up:** Dashboard is running and showing the correct supplier context.
- [ ] **Analyze**: Run `FINANCIAL REPORT PROMPT ANALYSIS.MD` on the final output.
