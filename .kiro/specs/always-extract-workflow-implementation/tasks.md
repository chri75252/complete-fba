# Implementation Plan

- [x] 1. Enhance Authentication System with DOM-Based Detection




  - Update standalone_playwright_login.py to accept credentials in constructor and use PoundWholesale/Magento-specific selectors
  - Implement verify_price_access() method to check price element visibility with currency symbols
  - Update supplier_authentication_service.py to use DOM-based authentication detection instead of text matching
  - Add logout link detection, account UI detection, and price access verification

  - Implement clean authentication logging with specified log formats
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 2. Implement Always-Extract Workflow with Pagination Tracking


  - Remove cache short-circuit logic from passive_extraction_workflow_latest.py that skips URL extraction
  - Eliminate "CHUNK CACHE HIT" and "CHUNK CACHE REFERENCE" branches that prevent category re-crawl
  - Implement next/last navigation with explicit stop criteria for complete page coverage
  - Add pagination tracking with complete page enumeration and urls_per_page list building
  - Implement PAGINATION log emission: "PAGINATION[C{idx} {slug}]: pages={P} urls_page={u1,u2,...} total={N}"
  - Assert sum(urls_page) == manifest.count for pagination completeness validation
  - Ensure supplier scraper is called for every category regardless of cache state
  - _Requirements: 1.1, 1.2, 1.3, 9.1, 9.2, 9.3_



- [x] 3. Create Per-Category Manifest Generation System


  - Implement atomic manifest saving using WindowsSaveGuardian for each category
  - Create OUTPUTS/manifests/<supplier>/<slug>.json structure with required fields
  - Add manifest logging with "📝 MANIFEST: {N} URLs → {path}" format
  - Implement manifest overwrite detection and logging for re-runs

  - Ensure manifest count equals total scraped URLs across all pages
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 11.1, 11.3_

- [x] 4. Implement URL/EAN Normalization System




  - Create normalization utilities for consistent URL and EAN processing across all system components
  - Implement URL normalization with lowercase host, stripped tracking params, normalized trailing slashes, and stable query ordering
  - Implement EAN normalization as string type with preserved leading zeros and trimmed whitespace
  - Apply normalization consistently in filtering, resume checks, manifest write, and all cache operations
  - Apply normalization in linking-map and product cache matching to ensure consistent key comparison
  - Add normalization error handling and logging with fallback to original values
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 5. Build Category-Local Processing Queues and Clean Logging


  - Implement category-local to_amazon queue building from filtered URLs
  - Create single-line filter summary logging with "FILTER[C{idx} {slug}]: in={N} skip={A} needs_amz={B} needs_full={C}" format
  - Remove per-item "Cache hit (EAN)... skipping extraction" spam logging
  - Eliminate repeated "Enhanced Filtering Results" blocks per category
  - Ensure filter summary invariant: skip + needs_amz + needs_full = in
  - _Requirements: 4.1, 4.2, 4.4, 4.5, 6.1, 6.2, 6.3_

- [x] 6. Implement Sequential Category Processing


  - Process supplier phase for needs_full_extraction URLs within each category
  - Process Amazon phase for category-local to_amazon queue immediately after supplier phase
  - Complete both phases for current category before advancing to next category
  - Eliminate global cross-category processing queues
  - Add category completion tracking and logging
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 7. Add State Management with Validation and Resume Breadcrumbs


  - Implement validate_and_repair_state() method in FixedEnhancedStateManager
  - Add state validation for required keys, monotonic resumption indices, and correct bounds
  - Implement automatic state repair for common issues with logging
  - Add resume breadcrumb logging on every state save with "RESUME PTR: phase=<supplier|amazon> cat_idx=<n>/<N> url=<category_url> prod_idx=<i>/<M>" format
  - Ensure state consistency checks align with actual file contents
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Implement Configuration Normalization and Access Patterns
  - Add get_full_config() method to SystemConfigLoader for complete configuration structure
  - Ensure get_system_config() returns only system subsection
  - Create single accessor for financial_report_batch_size with consistent defaults
  - Add financial trigger logging with "🚨 FINANCIAL REPORT TRIGGER: Reached {k} linking map entries (trigger every {N})" format
  - Eliminate duplicated configuration code with different default values
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [-] 9. Add Import Path Hygiene and Module Validation

  - Add module path logging at workflow startup to confirm correct module is running
  - Ensure main orchestrator imports PassiveExtractionWorkflow from authoritative tools/ path
  - Remove or rename stale copies of workflow files to prevent import confusion
  - Add import validation to detect when wrong module version is loaded
  - Print warning if multiple workflow candidates exist in different directories
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 10. Implement Reverse Gap Policy Fixes
  - Modify reverse gap detection to preserve existing resume index unless explicit cache rebuild
  - Add logging when reverse gap is detected but resume index is preserved
  - Ensure resumption_index is not reset to 0 on every startup
  - Add clear decision logging for gap processing policy
  - Validate that resume indices remain monotonic across restarts
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. Remove Cache Hit Spam and Clean Up Logging
  - Remove per-item "Cache hit (EAN): ... skipping extraction" debug messages
  - Keep only startup "GAP PROCESSING:" summary if retained
  - Ensure no repeated per-category gap processing messages
  - Gate cache hit logging behind disabled debug flag
  - Maintain clean, actionable log output for operators
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 12. Create Comprehensive Acceptance Test Suite
  - Implement TST-LOGIN-001/002 tests for authentication logging verification
  - Create TST-MANIFEST-001 test for category manifest generation validation
  - Implement TST-FILTER-001 test for filter summary invariant verification
  - Create TST-PAGINATION-001 test for complete page coverage validation
  - Implement TST-RESUME-001/002 tests for breadcrumb logging verification
  - Create TST-STATE-001 test for state validation and repair functionality
  - Implement TST-FIN-001 test for financial trigger timing verification
  - Create TST-IMPORT-001 test for module import hygiene validation
  - _Requirements: All acceptance tests from requirements document_

- [ ] 13. Validate System Invariants and Production Readiness
  - Verify INV-001: skip + needs_amz + needs_full == manifest.count for all categories
  - Validate INV-002: Resume indices are monotonic and phase-correct; breadcrumbs emitted on every save
  - Check INV-003: Manifests are written atomically and reflect latest scrape results
  - Confirm INV-004: Total URLs across all pages equals manifest count (pagination completeness)
  - Verify INV-005: All URL/EAN matching uses normalized keys consistently across components
  - Test rollout flags: EXTRACT_POLICY=ALWAYS, MANIFEST_WRITE=ON, LOG_BREADCRUMBS=ON
  - Execute T+1 canary with 2-3 categories: verify pagination, manifests, filter invariant, breadcrumbs
  - Execute T+7 rollout sampling ≥10% categories: verify invariants and financial trigger cadence
  - Validate risk mitigations: DOM/price checks, pagination logs, normalization utility, state validator
  - _Requirements: All invariants from requirements document_