# Implementation Plan

## Pre-Implementation Verification

- [x] 1. Verify Current System Behavior


  - Confirm the passive workflow is calling the prefiltered path in scenarios where "no cache saves" are observed
  - Verify `self._current_all_products` in the workflow is the same list passed as `product_accumulator`
  - Document current log patterns showing missing cache saves
  - _Requirements: R1.1, R3.1_

## Core Implementation

- [x] 2. Add Progress Callback Integration





  - Locate the insertion point in `scrape_products_from_prefiltered_urls` method after `product_accumulator.append(product)`
  - Add accumulator sanity check with warning log when `product_accumulator is None` (critical breadcrumb for "why didn't it save?" debugging)
  - Add future-proof metadata to `product["__cb_meta"]` with phase, category_url, attempt_index, total_in_batch, accumulator_len, and ts_epoch
  - Add progress callback invocation with explicit callable guard: `if getattr(self, "progress_callback", None) and callable(self.progress_callback):`
  - Send both `i+1` (attempt index) and `accumulator_len` (via metadata/logs) - they diverge on failed/filtered items for resume math
  - Add exception handling with debug-level logging for callback failures
  - _Requirements: R1.1, R1.2, R2.1, R4.1_

- [x] 3. Add URL Normalization (Optional Enhancement)

  - Create `_normalize_url_for_cache` helper function using stdlib urllib.parse
  - Add `normalized_url` field to product dictionary
  - Handle edge cases gracefully with fallback to original URL
  - _Requirements: R2.1, R4.3_

- [x] 4. Add Parseable Logging

  - Add INFO-level log line with format: "🔄 REAL-TIME: appended=%s idx=%s/%s acc_len=%s url=%s"
  - Include accurate accumulator length and index information
  - Use normalized URL when available, fallback to original URL
  - _Requirements: R3.1_

## Testing and Validation

- [ ] 5. Create Unit Tests
  - Test progress callback integration with mock callback
  - Test callback error handling with exception simulation
  - Test no accumulator edge case with warning verification
  - Test metadata enrichment in product dictionary
  - Test URL normalization with various formats
  - Test config guard: explicitly verify `update_frequency_products=1` and `=2` are read from system config
  - Test prefiltered path assertion: verify the prefiltered method is invoked (via spy/patch or log marker)
  - Test compatibility: load cached product with `__cb_meta` and verify downstream consumers ignore unknown fields
  - _Requirements: R1.3, R2.1, R3.3, R4.1_

- [x] 6. Run Integration Tests


  - Test N=1 scenario (update_frequency_products=1) expecting cache save after each product
  - Test N=2 scenario (update_frequency_products=2) expecting saves on products 2, 4, 6, etc.
  - Test odd-count run (5 items with N=2) and confirm workflow emits final save at category/process end
  - Test callback exception scenario with continued extraction
  - Test crash resilience: "kill after product K" test to prove previously saved cache entries survive
  - Verify exact log contract: assert presence of "CACHE CHECK" lines and "REAL-TIME" line once per processed product
  - Verify "CACHE CHECK" logs appear in workflow
  - Verify atomic save logs appear with updated counts
  - Verify new "REAL-TIME" logs appear with correct data
  - _Requirements: R1.2, R1.3, R3.1, R3.2_

## Pre-Merge Verification

- [x] 7. Final System Validation


  - Run end-to-end test with actual supplier extraction
  - Confirm cache file updates at configured frequency
  - Verify log patterns match expected format
  - Confirm no regression in existing functionality
  - Verify backward compatibility with existing configurations
  - _Requirements: R3.1, R3.2, R4.1, R4.2, R4.3_

## Documentation and Cleanup

- [ ] 8. Update Documentation
  - Document the new metadata fields in product dictionary
  - Document the new log format for monitoring
  - Update any relevant troubleshooting guides
  - _Requirements: R3.1_

## Acceptance Criteria Verification

- [ ] 9. Verify All Requirements Met



  - R1: Progress callback fires after each product extraction in prefiltered path
  - R2: Consistent progress tracking signature across all scraper paths
  - R3: Cache save verification logs appear and atomic saves occur
  - R4: No signature changes, backward compatibility maintained
  - Future-proofing: Metadata and normalized URLs enable next phase development
  - _Requirements: R1.1, R1.2, R1.3, R2.1, R2.2, R3.1, R3.2, R3.3, R4.1, R4.2, R4.3_