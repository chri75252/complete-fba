# Requirements Document

## Introduction

This specification defines the critical fixes needed to complete the Always-Extract Workflow implementation. Based on analysis of the current system behavior (from log file `run_custom_poundwholesale_20250811_184557.log`) compared to the intended behavior defined in the existing spec, several key features are missing or incorrectly implemented.

The current system shows evidence of:
- Incorrect pagination logging format: `PAGINATION[C1 https-www-poundwholesale-co-uk]: pages=5 urls_page=20,20,20,16,0 total=76`
- Incorrect breadcrumb format: `RESUME PTR: phase=supplier_extraction cat_idx=0/1 url=... prod_idx=1/0`
- Missing manifest generation and logging
- Missing filter summary logging
- Missing module path logging for import hygiene
- Missing URL/EAN normalization
- Missing state validation and repair functionality
- Reverse gap detection still resets resumption_index to 0 every run

## Requirements

### Requirement 1: Fix Pagination Logging Format

**User Story:** As a system operator, I want pagination logs to use the correct format with category index and slug, so that I can easily identify which category is being processed.

#### Acceptance Criteria

1. WHEN pagination is logged THEN the system SHALL use format "PAGINATION[C{idx} {slug}]: pages={P} urls_page={u1,u2,...} total={N}"
2. WHEN category index is available THEN the system SHALL use the actual category index (0-based) instead of hardcoded "C1"
3. WHEN category URL is processed THEN the system SHALL generate a readable slug from the URL path
4. WHEN pagination completes THEN the logged total SHALL match the sum of urls_page values
5. WHEN multiple categories are processed THEN each category SHALL have its own unique index in the log

### Requirement 2: Fix Breadcrumb Logging Format

**User Story:** As a system operator, I want breadcrumb logs to show accurate denominators and phase information, so that I can track exact progress and resume points.

#### Acceptance Criteria

1. WHEN breadcrumbs are logged THEN the system SHALL use format "RESUME PTR: phase=<supplier|amazon> cat_idx=<n>/<N> url=<category_url> prod_idx=<i>/<M>"
2. WHEN total categories are known THEN the denominator N SHALL reflect the actual total category count
3. WHEN products are processed THEN the denominator M SHALL reflect the actual product count for the current category
4. WHEN phase changes THEN the phase field SHALL accurately reflect "supplier" or "amazon" processing
5. WHEN denominators are zero THEN the system SHALL NOT log breadcrumbs until accurate totals are available

### Requirement 3: Implement Per-Category Manifest Generation

**User Story:** As a system operator, I want the system to generate atomic manifest files for each category with proper logging, so that I have a ground truth record of what was extracted.

#### Acceptance Criteria

1. WHEN category URLs are extracted THEN the system SHALL save a manifest at OUTPUTS/manifests/<supplier>/<slug>.json
2. WHEN manifest is saved THEN the system SHALL log "📝 MANIFEST: {N} URLs → {path}"
3. WHEN manifest is overwritten THEN the system SHALL log "MANIFEST UPDATE[C{idx} {slug}]: overwritten=true prev={M} curr={N}"
4. WHEN saving manifests THEN the system SHALL use WindowsSaveGuardian for atomic writes
5. WHEN manifest contains data THEN it SHALL include category_url, scraped_at, product_urls, and count fields

### Requirement 4: Implement Clean Filter Summary Logging

**User Story:** As a system operator, I want single-line filter summaries that replace the current verbose logging, so that I can quickly understand filtering results without log spam.

#### Acceptance Criteria

1. WHEN URLs are filtered THEN the system SHALL log "FILTER[C{idx} {slug}]: in={N} skip={A} needs_amz={B} needs_full={C}"
2. WHEN filter summary is calculated THEN the invariant skip + needs_amz + needs_full = in SHALL always hold
3. WHEN filtering completes THEN the system SHALL NOT log individual "Cache hit (EAN)... skipping extraction" messages
4. WHEN multiple categories are processed THEN each category SHALL have exactly one filter summary line
5. WHEN filter results are empty THEN the system SHALL still log the summary with zero counts

### Requirement 5: Implement Module Path Logging for Import Hygiene

**User Story:** As a system operator, I want the system to log which workflow module is actually running, so that I can verify the correct version is being executed.

#### Acceptance Criteria

1. WHEN workflow starts THEN the system SHALL log "MODULE PATH: {__file__}" at startup
2. WHEN multiple workflow files exist THEN the system SHALL warn about potential import conflicts
3. WHEN wrong module is detected THEN the system SHALL provide clear guidance on resolution
4. WHEN import path is resolved THEN the system SHALL use the canonical tools/ directory version
5. WHEN module validation fails THEN the system SHALL prevent execution with clear error messages

### Requirement 6: Implement URL/EAN Normalization System

**User Story:** As a system operator, I want consistent URL and EAN normalization across all system components, so that matching and filtering work reliably without duplicates.

#### Acceptance Criteria

1. WHEN URLs are processed THEN the system SHALL normalize with lowercase host, stripped tracking params, and stable query ordering
2. WHEN EANs are processed THEN the system SHALL normalize as string type with preserved leading zeros and trimmed whitespace
3. WHEN filtering against linking-map THEN the system SHALL use normalized keys for comparison
4. WHEN filtering against cache THEN the system SHALL use normalized keys for comparison
5. WHEN normalization fails THEN the system SHALL log the failure and use original values as fallback

### Requirement 7: Implement State Validation and Repair System

**User Story:** As a system operator, I want automatic state validation and repair on startup, so that the system can recover from corruption and maintain consistent resume behavior.

#### Acceptance Criteria

1. WHEN system starts THEN the system SHALL call validate_and_repair_state() before processing
2. WHEN state validation finds issues THEN the system SHALL automatically repair common problems
3. WHEN repairs are made THEN the system SHALL log "State repaired: {repairs}" with details
4. WHEN resumption indices are invalid THEN the system SHALL correct bounds and monotonicity
5. WHEN state is corrupted THEN the system SHALL provide fallback defaults and continue processing

### Requirement 8: Fix Reverse Gap Policy to Preserve Resume Index

**User Story:** As a system operator, I want the system to preserve existing resume indices unless explicitly rebuilding cache, so that processing doesn't restart from category 0 every run.

#### Acceptance Criteria

1. WHEN reverse gap is detected THEN the system SHALL NOT automatically reset resumption_index to 0
2. WHEN valid resume index exists THEN the system SHALL preserve it unless cache rebuild is explicitly requested
3. WHEN gap processing decision is made THEN the system SHALL log the reasoning clearly
4. WHEN resumption continues THEN the system SHALL maintain monotonic progression
5. WHEN explicit cache rebuild is triggered THEN the system SHALL reset to 0 with clear logging

### Requirement 9: Remove Cache Hit Spam and Clean Up Logging

**User Story:** As a system operator, I want clean logs without per-item cache hit spam, so that I can focus on important information and system progress.

#### Acceptance Criteria

1. WHEN cache hits occur THEN the system SHALL NOT log individual "Cache hit (EAN): ... skipping extraction" messages
2. WHEN gap processing occurs THEN the system SHALL log "GAP PROCESSING:" summary only once at startup
3. WHEN repeated filtering occurs THEN the system SHALL NOT emit multiple "Enhanced Filtering Results" blocks per category
4. WHEN debug logging is needed THEN cache hit messages SHALL be gated behind a disabled debug flag
5. WHEN logs are generated THEN they SHALL focus on actionable information and progress tracking

### Requirement 10: Implement Category-Local Processing Queues

**User Story:** As a system operator, I want the system to build category-local processing queues and complete both supplier and Amazon phases per category, so that processing is organized and trackable.

#### Acceptance Criteria

1. WHEN URLs are filtered THEN the system SHALL create category-local to_amazon queue from needs_amazon_only + newly extracted URLs
2. WHEN supplier processing is needed THEN the system SHALL process needs_full_extraction URLs for current category only
3. WHEN supplier processing completes THEN the system SHALL immediately process Amazon analysis for the category's to_amazon queue
4. WHEN both phases complete THEN the system SHALL advance to the next category
5. WHEN Amazon queue is empty THEN the system SHALL log "Amazon skipped: nothing to analyze for category"

## Acceptance Tests

### TST-PAGINATION-FIX-001: Correct Pagination Format
**Preconditions:** Category with multiple pages being processed
**Action:** Extract URLs from category
**Expected Logs:**
- "PAGINATION[C5 wholesale-hand-tools]: pages=3 urls_page=166,166,166 total=498"
**Artifacts:** Category index matches actual position, slug is readable, total equals sum

### TST-BREADCRUMB-FIX-001: Accurate Breadcrumb Denominators
**Preconditions:** Processing category with known product count
**Action:** Save state during processing
**Expected Logs:**
- "RESUME PTR: phase=supplier cat_idx=5/119 url=https://...wholesale-hand-tools prod_idx=3/498"
**Artifacts:** Denominators are non-zero and accurate

### TST-MANIFEST-001: Manifest Generation and Logging
**Preconditions:** Category URLs extracted
**Action:** Complete category processing
**Expected Logs:**
- "📝 MANIFEST: 498 URLs → C:\...\OUTPUTS\manifests\poundwholesale.co.uk\wholesale-hand-tools.json"
**Artifacts:** JSON file exists with correct structure and count

### TST-FILTER-001: Clean Filter Summary
**Preconditions:** URLs filtered against caches
**Action:** Process category filtering
**Expected Logs:**
- "FILTER[C5 wholesale-hand-tools]: in=498 skip=491 needs_amz=0 needs_full=7"
**Artifacts:** Invariant verified: skip + needs_amz + needs_full = in

### TST-MODULE-001: Module Path Logging
**Preconditions:** System startup
**Action:** Initialize workflow
**Expected Logs:**
- "MODULE PATH: C:\...\tools\passive_extraction_workflow_latest.py"
**Artifacts:** Correct module path logged at startup

### TST-NORMALIZATION-001: URL/EAN Normalization
**Preconditions:** URLs with tracking params, EANs with leading zeros
**Action:** Process normalization and filtering
**Expected Logs:**
- Normalized matches align with linking-map/cache
**Artifacts:** FILTER invariant holds with normalized keys

### TST-STATE-001: State Validation and Repair
**Preconditions:** System startup with existing state
**Action:** Load and validate state
**Expected Logs:**
- "State repaired: resumption_index bounds corrected" (if repairs needed)
**Artifacts:** validate_and_repair_state() returns repair report

### TST-REVERSE-GAP-001: Preserve Resume Index
**Preconditions:** Reverse gap detected with valid resume index
**Action:** System startup analysis
**Expected Logs:**
- Warning about gap but resume index preserved
**Artifacts:** resumption_index not reset to 0

### TST-SPAM-001: No Cache Hit Spam
**Preconditions:** Processing with many cache hits
**Action:** Process category with cached products
**Expected Logs:**
- No individual "Cache hit (EAN): ... skipping extraction" messages
**Artifacts:** Clean log output focused on progress

### TST-CATEGORY-LOCAL-001: Category-Local Processing
**Preconditions:** Category with mixed URL states
**Action:** Process category through both phases
**Expected Logs:**
- Supplier phase completion followed by Amazon phase for same category
**Artifacts:** Both phases complete before advancing to next category

## Invariants

### INV-001: Pagination Format Consistency
All pagination logs must use the format "PAGINATION[C{idx} {slug}]: pages={P} urls_page={u1,u2,...} total={N}" where sum(urls_page) == total

### INV-002: Breadcrumb Accuracy
All breadcrumb logs must have non-zero denominators when totals are known: cat_idx=<n>/<N> where N > 0, prod_idx=<i>/<M> where M > 0

### INV-003: Filter Summary Mathematics
For each category: skip + needs_amz + needs_full == in (manifest count)

### INV-004: Manifest Atomicity
All manifest files must be written atomically and contain accurate counts matching extracted URLs

### INV-005: Normalization Consistency
All URL/EAN matching must use normalized keys consistently across linking-map and cache comparisons

## Risk Register

### R-001: Log Format Breaking Changes
**Risk:** Changing log formats may break existing monitoring or parsing tools
**Mitigation:** Implement changes incrementally with feature flags
**Contingency:** Provide backward compatibility mode if needed

### R-002: State Validation Performance Impact
**Risk:** State validation on startup may slow system initialization
**Mitigation:** Optimize validation logic and cache results
**Contingency:** Make validation optional via configuration flag

### R-003: Normalization Edge Cases
**Risk:** URL/EAN normalization may fail on unexpected formats
**Mitigation:** Comprehensive testing with real data samples and fallback handling
**Contingency:** Log failures and use original values as fallback

### R-004: Category-Local Processing Memory Usage
**Risk:** Building category-local queues may increase memory usage
**Mitigation:** Process categories sequentially and clear queues after completion
**Contingency:** Add memory monitoring and queue size limits

### R-005: Manifest File System Issues
**Risk:** Atomic manifest writes may fail due to permissions or disk space
**Mitigation:** Check permissions and disk space before writes, use proper error handling
**Contingency:** Fall back to non-atomic writes with warning logs