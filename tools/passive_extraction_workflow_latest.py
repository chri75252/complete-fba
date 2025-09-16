"""
passive_extraction_workflow.py - Architectural Summary & Script Index
================================================================================

**High-Level Summary:**
This script is the central engine for a multi-stage workflow that identifies profitable products for Amazon FBA. When executed by a targeted runner like `run_custom_poundwholesale.py`, it operates in a deterministic mode, using a predefined list of category URLs to ensure reliable and repeatable scraping runs. The system is architected for resilience and statefulness, allowing it to resume interrupted sessions and handle supplier authentication, making it ideal for the thorough analysis of complex e-commerce websites.

**Key Features & Concepts:**
- **Centralized Configuration:** The workflow is now exclusively controlled by `system_config.json`. The launcher script (`run_custom_poundwholesale.py`) is a simple trigger, and the `PassiveExtractionWorkflow` class itself is responsible for loading and respecting all operational toggles, ensuring a single source of truth.
- **Batched Supplier Scraping:** The system processes supplier categories in configurable chunks (defined by `supplier_extraction_batch_size`). This provides critical memory management and stability, preventing the system from being overwhelmed when scraping suppliers with many categories.
- **Stateful Resume Capability:** The workflow's progress is meticulously tracked using an `EnhancedStateManager`. This component saves the index of the last processed product, allowing the script to be stopped and resumed without losing work—a critical feature for long-running, interruptible scraping tasks.
- **Integrated Authentication & Retry:** The workflow is designed to handle supplier logins. It can detect authentication failures during a run, trigger a re-login attempt via the `SupplierAuthenticationService`, and retry the workflow, making it resilient to session timeouts.
- **Robust Dual-Pronged Product Matching:** The system employs a powerful two-step process to find products on Amazon. It first attempts a high-confidence match using the product's EAN. If that fails, it falls back to a title-based search that uses an advanced similarity scoring algorithm to ensure the match is rational.
- **Comprehensive Financial Analysis:** After a match is validated, the script invokes the `FBA_Financial_calculator` to determine ROI, net profit, and other key financial metrics, ensuring only genuinely profitable products are flagged.
- **Atomic & Batched Data Persistence:** To ensure data integrity against crashes, critical state files (like the linking map and processing state) are saved using an atomic write pattern (write to a temp file, then rename). These saves occur periodically in configurable batches during the main processing loop.

**--(Latent AI Capabilities - Bypassed in this Workflow)--**
*   **(Inactive) AI-Powered Category Selection:** The codebase contains sophisticated logic (`_get_ai_suggested_categories_enhanced`) to use an OpenAI client to intelligently select categories. This is bypassed when using a predefined category list.
*   **(Inactive) Hierarchical Category Processing:** The script has the capability (`_hierarchical_category_selection`) to explore a supplier's site by prioritizing FBA-friendly categories first, then moving to other phases. This is not used in the custom Pound Wholesale run.

**Core Workflow Logic (as executed by `run_custom_poundwholesale.py`):**
1.  **Initialization and Configuration Loading:** The workflow starts, initializing the `EnhancedStateManager`. Its first action is to load `system_config.json` to set all operational parameters (`max_products`, `max_products_per_category`, batch sizes, etc.).
2.  **Predefined Category Loading:** The `use_predefined_categories=True` flag is detected. The workflow bypasses all AI logic and instead calls `_get_predefined_categories` to load a hard-coded list of URLs from a specific config file.
3.  **Batched Supplier Product Scraping & Caching:** Using the predefined category list, `_extract_supplier_products` is called. This method now processes the category URLs in batches (controlled by `supplier_extraction_batch_size`), scraping the products from each batch sequentially before moving to the next.
4.  **Product Filtering and Resume Point Identification:** After all scraping is complete, the collected products are filtered by the configured price range. The script then slices the product list to start processing from the `last_processed
