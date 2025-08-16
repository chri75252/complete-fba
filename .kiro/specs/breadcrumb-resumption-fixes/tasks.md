# Implementation Tasks

## Task 1: Category Start Integration (CRITICAL)
- [ ] Locate category processing loop in `tools/passive_extraction_workflow_latest.py`
- [ ] Add write-ahead point 1 before any filtering or side-effects
- [ ] Populate: `current_category_index`, `total_categories`, `current_category_url`, `current_phase="supplier"`
- [ ] Add `hasattr()` safety check and `save_state_atomic()` + `log_breadcrumb_guarded()` calls

## Task 2: Post-Filter Denominator Persistence
- [ ] Locate `filter_urls()` call in workflow
- [ ] Verify filter returns `denominator` and `invariant_check` fields
- [ ] Add write-ahead point 2 immediately after filtering
- [ ] Set `total_products_in_current_category=filter_result["denominator"]`

## Task 3: Product Loop Staggered Updates
- [ ] Locate product processing loops (supplier and Amazon phases)
- [ ] Add write-ahead point 3 with index updates before each product
- [ ] Implement throttled saves every 10 items with 100ms timing gaps
- [ ] Add final sync at loop completion

## Task 4: Phase Transition Updates
- [ ] Locate supplier→Amazon phase transition point
- [ ] Add write-ahead point 4 with `current_phase="amazon"` update
- [ ] Reset product index and update totals for Amazon phase
- [ ] Ensure atomic update with save and log

## Task 5: URL Filter Verification
- [ ] Inspect `utils/url_filter.py` filter_urls function
- [ ] Confirm return format includes required fields
- [ ] Add missing fields if not present: `invariant_check`, `denominator`, `linking_map_hits`

## Task 6: Integration Testing & Validation
- [ ] Run 2-minute smoke test with log monitoring
- [ ] Verify elimination of "BREADCRUMB DELAYED" warnings
- [ ] Confirm staggered write timing and file conflict prevention
- [ ] Validate index-based progression and resume functionality