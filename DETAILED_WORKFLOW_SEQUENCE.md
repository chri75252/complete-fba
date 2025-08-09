# Detailed Workflow Sequence

This document describes the updated hybrid processing workflow used by the Amazon FBA Agent System.
All state metrics are derived from files on disk and the workflow resumes using
recorded indices only – user-facing counts never influence recovery.

## Startup
1. **Load configuration** from `config/system_config.json` and supplier category
   list from `config/poundwholesale_categories.json`.
2. **Initialize `FixedEnhancedStateManager`**, which in turn reads the product
   cache and linking map to calculate `user_display_metrics.total_products` and
   `successful_products`. These values come from actual file counts via
   `_calculate_file_grounded_totals`.
3. **Restore system progression** (`current_phase`, category index and product
   indices) from the processing state file for exact resume capability.

## Category Loop
1. **Iterate categories sequentially.** State manager records the category index
   and URL with `initialize_category_processing`.
2. **Extract product URLs** from the supplier category.
3. **Update category denominator:** call
   `update_discovered_products_in_category` so the processing state reflects the
   real product count if the initial estimate was wrong.
4. **Pre-filter URLs** using `utils.url_filter`:
   - Check the linking map first via `HashLookupOptimizer` indexes; any URL
     found here is treated as fully processed and added to `skip_entirely`.
   - Remaining URLs are checked against the product cache to populate
     `needs_amazon_only` (supplier data already cached).
   - URLs in neither file become `needs_full_extraction`.
5. **Update user-facing counts** (discovered totals) based on the size of these
   lists. These counts are for monitoring only and do not affect resumption.

## Supplier Extraction Phase
1. Process `needs_full_extraction` URLs.
2. For each extracted product:
   - Save supplier data to the cache.
   - Call `update_supplier_extraction_progress_new` to increment:
     - `system_progression.supplier_extraction_resumption_index`
     - `system_progression.current_product_index_in_category`
     - `user_display_metrics.progress_count`
   - Append to the linking map using `HashLookupOptimizer.add_entry()`. Duplicate
     supplier URLs or EANs update the existing record instead of adding a new
     entry, preventing growth of duplicates.
   - After each insertion the current linking map count is evaluated. When the
     count reaches a multiple of `financial_report_batch_size` from
     `system_config.json`, the system runs `FBA_Financial_calculator.run_calculations`
     to generate a CSV profitability report.
3. State is saved atomically after each product via `save_state_atomic`.
   `system_progression` indices and `user_display_metrics.progress_count` are
   updated every product.

## Amazon Analysis Phase
1. Combine `needs_amazon_only` URLs with newly extracted products that require
   Amazon analysis.
2. For each product:
   - `_get_amazon_data` performs an EAN-first search, falling back to title
     search if needed.
   - `update_amazon_analysis_progress_new` increments
     `amazon_analysis_resumption_index` and
     `session_products_processed`.
   - The resulting data is cached and merged into the linking map via
     `HashLookupOptimizer`, again updating existing entries if duplicates are
     detected.
   - The financial-report trigger described above also applies as new linking
     map entries accumulate during this phase.
3. Atomic state saves occur after each product to enable exact resumption.

## Progress Metrics
- **System Resumption (`system_progression`)**
  - `current_phase`
  - `current_category_index`
  - `current_product_index_in_category`
  - `supplier_extraction_resumption_index`
  - `amazon_analysis_resumption_index`
- **User Display (`user_display_metrics`)**
  - `progress_count` (incremented per supplier product extracted)
  - `session_products_processed` (incremented per Amazon analysis)
  - `total_products` and `successful_products` (recalculated from product cache
    and linking map counts during startup or full saves)

`user_display_metrics` values are never used for interruption recovery. The
system relies solely on `system_progression` indices, which are persisted after
every product. On restart, the workflow resumes from the recorded phase and
resumption index of the last processed product.

