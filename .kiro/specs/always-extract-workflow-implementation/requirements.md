# Requirements Document

## Introduction

This specification defines the implementation of a production-ready Amazon FBA Agent System that enforces per-category Always-Extract workflow, robust supplier login, precise resume pointers, clean logs, and per-category manifests. The system must eliminate cache short-circuiting, provide reliable authentication, maintain accurate state tracking, and deliver clean, actionable logging for operators.

## Requirements

### Requirement 1: Always-Extract Product URLs Per Category

**User Story:** As a system operator, I want the system to always extract product URLs at the start of every category processing, so that I have a complete and accurate view of all available products without cache short-circuiting.

#### Acceptance Criteria

1. WHEN processing any category THEN the system SHALL extract all product URLs from that category regardless of cache state
2. WHEN cache data exists for a category THEN the system SHALL NOT skip URL extraction based on cache hits
3. WHEN URLs are extracted THEN the system SHALL filter against linking-map first, then product cache, to build category-local processing queues
4. WHEN filtering is complete THEN the system SHALL process supplier data only for URLs not in cache
5. WHEN supplier processing is complete THEN the system SHALL run Amazon analysis for that category before advancing to the next category

### Requirement 2: Robust Supplier Authentication System

**User Story:** As a system operator, I want reliable supplier login functionality that correctly detects authentication state and performs login when needed, so that the system can access supplier data without manual intervention.

#### Acceptance Criteria

1. WHEN checking authentication status THEN the system SHALL use DOM-based indicators rather than broad text matches
2. WHEN detecting logged-in state THEN the system SHALL verify presence of logout links, account UI elements, or price access on product pages
3. WHEN login is required THEN the system SHALL use PoundWholesale/Magento-specific selectors for email and password fields
4. WHEN login is attempted THEN the system SHALL verify successful authentication by checking price element visibility with currency symbols
5. WHEN authentication fails THEN the system SHALL provide clear error messages and retry logic

### Requirement 3: Per-Category Manifest Generation

**User Story:** As a system operator, I want the system to generate a manifest file for each category containing all extracted product URLs, so that I have a ground truth record of what was processed.

#### Acceptance Criteria

1. WHEN a category's URLs are extracted THEN the system SHALL save a manifest file at OUTPUTS/manifests/<supplier>/<slug>.json
2. WHEN saving manifests THEN the system SHALL include category_url, scraped_at timestamp, product_urls array, and count fields
3. WHEN saving files THEN the system SHALL use atomic file operations via WindowsSaveGuardian where available
4. WHEN manifest is saved THEN the system SHALL log "📝 MANIFEST: {N} URLs → {path}"
5. WHEN processing multiple categories THEN each category SHALL have its own separate manifest file

### Requirement 4: Clean and Actionable Logging

**User Story:** As a system operator, I want clean, summarized logs that provide actionable information without spam, so that I can monitor system progress and identify issues efficiently.

#### Acceptance Criteria

1. WHEN processing categories THEN the system SHALL emit a single summary line per category: "FILTER[C{idx} {slug}]: in={N} skip={A} needs_amz={B} needs_full={C}"
2. WHEN cache hits occur THEN the system SHALL NOT log individual "Cache hit (EAN)... skipping extraction" messages
3. WHEN gap processing occurs THEN the system SHALL log "GAP PROCESSING:" summary only once at startup, not per category
4. WHEN filtering results are calculated THEN the system SHALL NOT repeat "Enhanced Filtering Results" blocks for every category
5. WHEN logging filtering results THEN the invariant skip + needs_amz + needs_full = in SHALL always hold

### Requirement 5: Precise Resume Pointer System

**User Story:** As a system operator, I want the system to maintain precise resume pointers with breadcrumbs on every save, so that I can track progress and resume processing from exact positions after interruptions.

#### Acceptance Criteria

1. WHEN saving state after supplier processing THEN the system SHALL log "RESUME PTR: phase=supplier cat_idx=<n>/<N> url=<category_url> prod_idx=<i>/<M>"
2. WHEN saving state after Amazon processing THEN the system SHALL log "RESUME PTR: phase=amazon cat_idx=<n>/<N> url=<category_url> prod_idx=<i>/<M>"
3. WHEN state is loaded THEN the system SHALL validate and repair state inconsistencies automatically
4. WHEN resumption indices are checked THEN the system SHALL ensure monotonic progression and correct bounds
5. WHEN state validation fails THEN the system SHALL log "State repaired: ..." with details of corrections made

### Requirement 6: Category-Local Processing Queues

**User Story:** As a system operator, I want the system to build category-local processing queues and complete both supplier and Amazon phases for each category before moving to the next, so that processing is organized and trackable.

#### Acceptance Criteria

1. WHEN URLs are filtered THEN the system SHALL create category-local to_amazon queue containing needs_amazon_only + newly extracted URLs
2. WHEN supplier processing is needed THEN the system SHALL process needs_full_extraction URLs for the current category
3. WHEN supplier processing is complete THEN the system SHALL immediately process Amazon analysis for the category's to_amazon queue
4. WHEN both phases are complete THEN the system SHALL advance to the next category
5. WHEN processing categories THEN the system SHALL NOT maintain global cross-category queues

### Requirement 7: Configuration Normalization

**User Story:** As a system operator, I want consistent configuration access patterns throughout the system, so that settings are read from a single source of truth without duplication.

#### Acceptance Criteria

1. WHEN reading financial_report_batch_size THEN the system SHALL use a single accessor method with consistent defaults
2. WHEN accessing system configuration THEN the system SHALL provide get_system_config() for system subsection only
3. WHEN accessing full configuration THEN the system SHALL provide get_full_config() for complete configuration structure
4. WHEN financial triggers fire THEN the system SHALL log "🚨 FINANCIAL REPORT TRIGGER: Reached {k} linking map entries (trigger every {N})"
5. WHEN configuration is loaded THEN the system SHALL eliminate duplicated code with different default values

### Requirement 8: Import Path Hygiene

**User Story:** As a system operator, I want the system to import the correct workflow modules without ambiguity, so that the latest code is always executed without stale copies.

#### Acceptance Criteria

1. WHEN the main orchestrator starts THEN it SHALL import PassiveExtractionWorkflow from the authoritative module path
2. WHEN imports are resolved THEN the system SHALL NOT rely on stale copies of workflow files
3. WHEN ImportError occurs THEN the system SHALL provide clear error messages indicating the expected module path
4. WHEN multiple copies of files exist THEN the system SHALL use the canonical version in tools/ directory
5. WHEN runtime imports occur THEN the system SHALL validate that the correct module version is loaded

### Requirement 9: Pagination Completeness

**User Story:** As a system operator, I want the system to crawl all pages for each category with clear pagination tracking, so that I have complete product coverage without missing items.

#### Acceptance Criteria

1. WHEN processing a category THEN the system SHALL crawl all pages using next/last navigation or explicit stop conditions
2. WHEN pagination is complete THEN the system SHALL log "PAGINATION[C{idx} {slug}]: pages={P} urls_page={u1,u2,...} total={N}"
3. WHEN manifest is generated THEN the manifest count SHALL equal total scraped URLs across all pages
4. WHEN pagination fails THEN the system SHALL log the failure and continue with collected URLs
5. WHEN stop condition is reached THEN the system SHALL verify no additional pages exist

### Requirement 10: URL/EAN Normalization Policy

**User Story:** As a system operator, I want consistent URL and EAN normalization throughout the system, so that matching against caches and linking maps is reliable and accurate.

#### Acceptance Criteria

1. WHEN URLs are processed THEN the system SHALL normalize with lowercase host, stripped tracking params, normalized trailing slashes, and stable query ordering
2. WHEN EANs are processed THEN the system SHALL normalize as string type, preserve leading zeros, and trim whitespace
3. WHEN matching against linking-map THEN the system SHALL use normalized keys for comparison
4. WHEN matching against product cache THEN the system SHALL use normalized keys for comparison
5. WHEN normalization fails THEN the system SHALL log the failure and use original values

### Requirement 11: Resume Idempotency on Re-extract

**User Story:** As a system operator, I want the system to handle re-runs mid-category gracefully by overwriting manifests atomically, so that there is no double counting or state corruption.

#### Acceptance Criteria

1. WHEN re-running mid-category THEN the system SHALL re-write the manifest atomically
2. WHEN manifest is overwritten THEN the system SHALL reset the per-category denominator from the new manifest
3. WHEN overwriting manifest THEN the system SHALL log "MANIFEST UPDATE[C{idx} {slug}]: overwritten=true prev={M} curr={N}"
4. WHEN filter summary is calculated THEN it SHALL use the new manifest count as denominator
5. WHEN resuming after re-extract THEN the system SHALL NOT double-count previously processed products

## Acceptance Tests

### TST-LOGIN-001: Authentication Required
**Preconditions:** System not authenticated
**Action:** Start category processing
**Expected Logs:** 
- "🔧 Using standalone playwright authentication"
- "✅ Standalone authentication successful: selector_fallback"
**Artifacts:** Successful login to supplier site

### TST-LOGIN-002: Authentication Already Present
**Preconditions:** System already authenticated
**Action:** Check authentication status
**Expected Logs:**
- "✅ Already logged in! Price access verified: True"
**Artifacts:** No additional login attempt

### TST-MANIFEST-001: Category Manifest Generation
**Preconditions:** Category URLs extracted
**Action:** Complete category processing
**Expected Logs:**
- "📝 MANIFEST: 498 URLs → C:\...\OUTPUTS\manifests\poundwholesale.co.uk\wholesale-hand-tools.json"
**Artifacts:** JSON file with count=498 and len(product_urls)=498

### TST-FILTER-001: Filter Summary Invariant
**Preconditions:** URLs filtered against caches
**Action:** Process category filtering
**Expected Logs:**
- "FILTER[C5 wholesale-hand-tools]: in=498 skip=491 needs_amz=0 needs_full=7"
**Artifacts:** Invariant verified: skip + needs_amz + needs_full = in

### TST-PAGINATION-001: Complete Page Coverage
**Preconditions:** Multi-page category
**Action:** Extract all category URLs
**Expected Logs:**
- "PAGINATION[C5 wholesale-hand-tools]: pages=3 urls_page=166,166,166 total=498"
**Artifacts:** sum(urls_page) == total == manifest.count

### TST-RESUME-001: Supplier Phase Breadcrumb
**Preconditions:** Processing supplier phase
**Action:** Save state during supplier processing
**Expected Logs:**
- "RESUME PTR: phase=supplier cat_idx=5/119 url=https://...wholesale-hand-tools prod_idx=3/498"
**Artifacts:** State file updated with correct indices

### TST-RESUME-002: Amazon Phase Breadcrumb
**Preconditions:** Processing Amazon phase
**Action:** Save state during Amazon processing
**Expected Logs:**
- "RESUME PTR: phase=amazon cat_idx=5/119 url=https://...wholesale-hand-tools prod_idx=2/498"
**Artifacts:** State file updated with correct indices

### TST-STATE-001: State Validation
**Preconditions:** System startup with existing state
**Action:** Load and validate state
**Expected Logs:**
- "State repaired: resumption_index bounds corrected" (if repairs needed)
**Artifacts:** validate_and_repair_state() returns ok=True

### TST-FIN-001: Financial Trigger
**Preconditions:** Linking map entries reach threshold
**Action:** Process products to trigger financial report
**Expected Logs:**
- "🚨 FINANCIAL REPORT TRIGGER: Reached 1000 linking map entries (trigger every 500)"
**Artifacts:** Financial report generated at correct interval

### TST-IMPORT-001: Module Import Hygiene
**Preconditions:** System startup
**Action:** Import PassiveExtractionWorkflow
**Expected Logs:**
- No ImportError messages
**Artifacts:** Correct workflow module loaded from tools/ directory

### TST-PAGINATION-001: Complete Page Coverage
**Preconditions:** Category with P>1 pages
**Action:** Extract all category URLs with pagination
**Expected Logs:**
- "PAGINATION[C5 wholesale-hand-tools]: pages=3 urls_page=166,166,166 total=498"
**Artifacts:** sum(urls_page) == total == manifest.count

### TST-NORMALIZATION-001: URL/EAN Normalization Consistency
**Preconditions:** URLs with tracking params; EAN with leading zeros
**Action:** Process URLs and EANs through normalization and matching
**Expected Logs:**
- Normalized matches align with linking-map/cache
**Artifacts:** FILTER invariant holds with normalized keys

### TST-RESUME-REEXTRACT-001: Resume Idempotency on Re-extract
**Preconditions:** Re-run system mid-category
**Action:** Overwrite manifest and reset processing
**Expected Logs:**
- "MANIFEST UPDATE[C5 wholesale-hand-tools]: overwritten=true prev=450 curr=498"
**Artifacts:** Denominator reset to new manifest; FILTER uses new N

### TST-COVERAGE-DELTA-001: Coverage Comparison Logging
**Preconditions:** Prior manifest exists with different URL count
**Action:** Re-extract category with changed product set
**Expected Logs:**
- "COVERAGE[C5 wholesale-hand-tools]: prev=450 curr=498 added=48 removed=0"
**Artifacts:** Added/removed URL counts accurately reflect differences

## Invariants

### INV-001: Filter Summary Mathematics
For each category: skip + needs_amz + needs_full == manifest.count

### INV-002: Resume Index Monotonicity
Resume indices must be monotonic and phase-correct; resumption_index never decreases within a session

### INV-003: Atomic Manifest Integrity
Manifests are written atomically and always reflect the latest scrape results

### INV-004: Pagination Completeness
Total URLs across all pages equals manifest count for each category

### INV-005: Normalization Consistency
All URL/EAN matching uses normalized keys consistently across linking-map and cache comparisons

## Rollout Plan

### Feature Flags
- **EXTRACT_POLICY=ALWAYS** (default ON): Enforce always-extract workflow
- **MANIFEST_WRITE=ON** (default ON): Enable per-category manifest generation
- **LOG_BREADCRUMBS=ON** (default ON): Enable resume pointer logging

### T+1 Canary Deployment
- **Scope:** Process 2-3 categories with known product overlaps
- **Validation:**
  - Verify pagination logs show complete page coverage
  - Confirm manifest counts match extracted URL totals
  - Check filter invariant holds (skip + needs_amz + needs_full = in)
  - Validate resume breadcrumbs appear on every save
- **Success Criteria:** All acceptance tests pass, no cache hit spam in logs

### T+7 Full Rollout
- **Scope:** Complete supplier run with sampling of ≥10% categories
- **Validation:**
  - Monitor manifest vs filter invariants across all processed categories
  - Confirm resume breadcrumbs maintain density throughout run
  - Verify financial triggers fire at exact configured intervals
  - Check log cleanliness (no spam patterns)
- **Success Criteria:** System completes full run with consistent behavior

## Risk Register

### R-001: Login Detection Regression
**Risk:** False positives in authentication detection cause skipped login attempts
**Mitigation:** Use multiple DOM-based indicators (logout links, account UI, price verification)
**Contingency:** Manual authentication verification and selector updates

### R-002: Pagination Misses Products
**Risk:** Incomplete pagination leads to missing products and inaccurate manifests
**Mitigation:** Robust pagination loop with explicit termination conditions and page count logging
**Contingency:** Manual category re-processing with pagination debugging

### R-003: Normalization Mismatch
**Risk:** Inconsistent normalization causes cache misses and duplicate processing
**Mitigation:** Centralized normalization utilities applied consistently across all matching operations
**Contingency:** Cache rebuild with consistent normalization applied

### R-004: Resume Pointer Drift
**Risk:** Resume pointers become inconsistent with actual file contents
**Mitigation:** validate_and_repair_state() on startup with automatic correction
**Contingency:** Manual state file correction and resumption point verification

### R-005: Manifest Corruption
**Risk:** Non-atomic writes corrupt manifest files during system interruption
**Mitigation:** Use WindowsSaveGuardian for atomic file operations
**Contingency:** Manifest regeneration from category re-extraction