# Implementation Plan

- [x] 1. Fix Pagination Logging Format


  - Update passive_extraction_workflow_latest.py to use correct pagination format "PAGINATION[C{idx} {slug}]: pages={P} urls_page={u1,u2,...} total={N}"
  - Replace hardcoded "C1" with actual category index from processing loop
  - Implement _generate_category_slug() method to create readable slugs from category URLs
  - Ensure pagination logging occurs after URL extraction with accurate totals
  - Validate that sum(urls_page) equals total in all pagination logs
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_



- [ ] 2. Fix Breadcrumb Logging Format and Timing
  - Update fixed_enhanced_state_manager.py to only log breadcrumbs when denominators are non-zero
  - Implement proper timing so breadcrumbs are logged after totals are set
  - Fix breadcrumb format to use "RESUME PTR: phase=<supplier|amazon> cat_idx=<n>/<N> url=<category_url> prod_idx=<i>/<M>"
  - Ensure total_categories (N) reflects actual category count from configuration
  - Ensure total_products_in_current_category (M) reflects actual product count from manifest

  - Add phase field validation to show "supplier" or "amazon" accurately
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 3. Implement Per-Category Manifest Generation System
  - Create _save_category_manifest() method in passive_extraction_workflow_latest.py
  - Implement atomic manifest saving using WindowsSaveGuardian
  - Create OUTPUTS/manifests/<supplier>/<slug>.json directory structure
  - Add manifest logging with "📝 MANIFEST: {N} URLs → {path}" format
  - Implement overwrite detection and logging with "MANIFEST UPDATE[C{idx} {slug}]: overwritten=true prev={M} curr={N}"

  - Include required fields: category_url, scraped_at, product_urls, count, supplier_name, slug
  - Integrate manifest generation into category processing workflow after URL extraction
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 4. Implement Clean Filter Summary Logging
  - Create _log_filter_summary() method in passive_extraction_workflow_latest.py
  - Replace verbose filtering logs with single-line "FILTER[C{idx} {slug}]: in={N} skip={A} needs_amz={B} needs_full={C}" format
  - Implement filter invariant validation: skip + needs_amz + needs_full = in

  - Remove individual "Cache hit (EAN)... skipping extraction" spam messages
  - Ensure each category has exactly one filter summary line
  - Add warning logs when filter invariant is violated
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5. Implement Module Path Logging for Import Hygiene
  - Add "MODULE PATH: {__file__}" logging at workflow startup in __init__ method

  - Implement _check_import_hygiene() method to detect potential workflow file conflicts
  - Add warnings when multiple workflow files exist outside archive/backup directories
  - Provide clear guidance on using canonical tools/ directory version
  - Add validation to prevent execution when wrong module is detected
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 6. Implement URL/EAN Normalization System
  - Create utils/url_filter.py with normalize_url() and normalize_ean() functions

  - Implement URL normalization: lowercase host, strip tracking params, stable query ordering, normalize trailing slashes
  - Implement EAN normalization: string type, preserve leading zeros, trim whitespace
  - Update filter_urls() function to use normalized keys for linking-map and cache comparisons
  - Apply normalization consistently across all URL/EAN matching operations
  - Add error handling and fallback to original values when normalization fails
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. Implement State Validation and Repair System


  - Add validate_and_repair_state() method to fixed_enhanced_state_manager.py
  - Implement startup state validation with automatic repair of common issues
  - Add repair logging with "State repaired: {repairs}" format showing details
  - Validate resumption indices for bounds and monotonicity
  - Ensure required system_progression fields exist with proper defaults
  - Call validation on system startup before processing begins

  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 8. Fix Reverse Gap Policy to Preserve Resume Index
  - Modify reverse gap detection logic to preserve existing resume index unless explicit cache rebuild
  - Add clear logging when reverse gap is detected but resume index is preserved
  - Ensure resumption_index is not automatically reset to 0 on every startup
  - Add configuration flag or explicit trigger for cache rebuild scenarios


  - Maintain monotonic progression across system restarts
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 9. Remove Cache Hit Spam and Clean Up Logging
  - Remove or gate individual "Cache hit (EAN): ... skipping extraction" messages behind disabled debug flag
  - Ensure "GAP PROCESSING:" summary appears only once at startup, not per category
  - Remove repeated "Enhanced Filtering Results" blocks for each category


  - Focus logs on actionable information and progress tracking
  - Maintain clean, operator-friendly log output
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 10. Implement Category-Local Processing Queues
  - Build category-local to_amazon queue from needs_amazon_only + newly extracted URLs
  - Process needs_full_extraction URLs for current category only in supplier phase
  - Immediately process Amazon analysis for category's to_amazon queue after supplier phase
  - Complete both phases for current category before advancing to next category
  - Add logging when Amazon phase is skipped due to empty to_amazon queue
  - Eliminate global cross-category processing queues
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 11. Create Comprehensive Test Suite for All Fixes
  - Implement TST-PAGINATION-FIX-001: Test correct pagination format with category indices and slugs
  - Implement TST-BREADCRUMB-FIX-001: Test accurate breadcrumb denominators and timing
  - Implement TST-MANIFEST-001: Test manifest generation, atomic saving, and logging
  - Implement TST-FILTER-001: Test clean filter summary format and invariant validation
  - Implement TST-MODULE-001: Test module path logging and import hygiene detection
  - Implement TST-NORMALIZATION-001: Test URL/EAN normalization consistency
  - Implement TST-STATE-001: Test state validation and repair functionality
  - Implement TST-REVERSE-GAP-001: Test reverse gap policy preserving resume index
  - Implement TST-SPAM-001: Test removal of cache hit spam logging
  - Implement TST-CATEGORY-LOCAL-001: Test category-local processing queue implementation
  - _Requirements: All acceptance tests from requirements document_

- [ ] 12. Validate System Invariants and Log Format Compliance
  - Verify INV-001: Pagination format consistency with sum(urls_page) == total
  - Validate INV-002: Breadcrumb accuracy with non-zero denominators when totals are known
  - Check INV-003: Filter summary mathematics with skip + needs_amz + needs_full == in
  - Confirm INV-004: Manifest atomicity with accurate counts matching extracted URLs
  - Verify INV-005: Normalization consistency across all URL/EAN matching operations
  - Test all log format patterns match expected specifications exactly
  - Validate that no old log patterns remain in output
  - _Requirements: All invariants from requirements document_

- [ ] 13. Performance Testing and Optimization
  - Test pagination logging performance (target: < 100ms per category)
  - Test manifest generation performance (target: < 2 seconds per category)
  - Test state validation performance (target: < 5 seconds on startup)
  - Test filter summary performance (target: < 1 second per category)
  - Test normalization performance (target: < 10ms per URL/EAN)
  - Optimize any performance bottlenecks identified
  - Add performance monitoring and alerting thresholds
  - _Requirements: Performance targets from design document_

- [ ] 14. Integration Testing with Real Data
  - Test complete workflow with sample categories from poundwholesale.co.uk
  - Verify all log formats appear correctly in real execution
  - Test manifest generation with various category sizes and structures
  - Validate state validation and repair with corrupted state files
  - Test normalization with real URLs containing tracking parameters and edge cases
  - Verify filter invariants hold with real cache and linking-map data
  - Test resume functionality after interruption at various points
  - _Requirements: End-to-end validation of all implemented fixes_

- [ ] 15. Documentation and Deployment Preparation
  - Update system documentation with new log formats and behavior
  - Create operator guide for interpreting new log patterns
  - Document troubleshooting steps for common issues
  - Prepare deployment checklist with feature flags and rollout plan
  - Create monitoring dashboard for new metrics and invariants
  - Document rollback procedures if issues are discovered
  - _Requirements: Production readiness and operational support_