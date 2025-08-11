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

## Gap Processing
Before moving to new categories, the workflow compares the counts of cached
supplier products with existing linking-map entries. Any surplus cached products
are treated as a "gap" and are passed directly to Amazon analysis. During this
phase the system logs an **ENHANCED FILTERING RESULTS** block detailing cache and
linking-map hits. Once the gap is cleared, normal category processing resumes.

## Category Loop
1. **Iterate categories sequentially starting from the resumption index.** The
   state manager reads `system_progression.current_category_index` on startup so
   interrupted runs continue with the first unprocessed category. Each category's
   index and URL are recorded via `initialize_category_processing`.
2. **Extract product URLs** from the supplier category (always fresh).
3. **Persist a category manifest** listing all URLs and their count
   (`OUTPUTS/manifests/<supplier>/<slug>.json`).
4. **Update category denominator:** call
   `correct_category_totals_realtime` so the processing state reflects the
   real product count if the initial estimate was wrong.
5. **Filter URLs against the linking map first.** Matches are fully processed
   and removed.
6. **Filter remaining URLs against the product cache.** These URLs already have
   supplier data and are queued for Amazon analysis.
7. **Whatever remains requires full supplier extraction.** These URLs are
   processed immediately and then queued for Amazon analysis.
8. **Update user-facing counts** (discovered totals) based on the size of each
   queue. These counts are for monitoring only and do not affect resumption.

## Supplier Extraction Phase
1. Process `needs_full_extraction` URLs.
2. For each extracted product:
   - Save supplier data to the cache.
   - Call `update_supplier_extraction_progress_new` to increment:
     - `system_progression.supplier_extraction_resumption_index`
     - `system_progression.current_category_index`
     - `system_progression.current_subcategory_index`
     - `system_progression.pages_scraped_in_session`
     - `system_progression.current_product_index_in_category`
     - `user_display_metrics.progress_count`
   - Queue the product for Amazon analysis.
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
     `HashLookupOptimizer`. Duplicate supplier URLs or EANs update the existing
     record instead of creating a new entry.
   - After each successful merge the current linking map count is evaluated.
     When the count reaches a multiple of `financial_report_batch_size` from
     `system_config.json`, the system runs
     `FBA_Financial_calculator.run_calculations` to generate a CSV profitability
     report.
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
exact product index in either the supplier or Amazon phase. Hybrid mode ensures
each category’s supplier extraction and Amazon analysis are completed before the
workflow advances to the next category.

