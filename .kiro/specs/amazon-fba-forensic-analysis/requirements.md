# Requirements Document

## Introduction

This specification defines the requirements for implementing a comprehensive remediation plan for the Amazon FBA Agent System's processing state, filtering, and resume fidelity issues in hybrid mode. The plan addresses critical P0 issues including filter/dedup gating, single writer enforcement, denominator freeze, resume fidelity, and per-product progress callbacks. The system must implement surgical fixes to existing broken functionality while maintaining backward compatibility and avoiding over-engineering. The scope is limited to hybrid processing mode with focus on state consistency, performance optimization, and system stability.

## Requirements

### Requirement 1: Filter & Dedup Gating (P0)

**User Story:** As a system operator, I want per-category 2/3-step filtering only after product URL discovery and before supplier extraction, so that downstream deduplication is gated and silent to eliminate log spam and improve performance.

#### Acceptance Criteria

1. WHEN processing categories THEN the system SHALL apply linking-map skip (already processed → skip) as the first filter step
2. WHEN checking supplier cache THEN the system SHALL apply supplier-cache skip (have supplier data → Amazon-only or skip) as the second filter step  
3. WHEN needed later in pipeline THEN the system SHALL compare against Amazon cache only when product info exists but no linking-map entry yet
4. WHEN deduplication fallbacks exist THEN the system SHALL remain silent with no per-item spam and short-circuit when no new items are being written
5. WHEN saving products to cache THEN the system SHALL bypass global scans unless new products exist and strip per-item spam logging
6. WHEN processing categories with only duplicates THEN the system SHALL produce exactly one summary line instead of 100→200→… dedup series

### Requirement 2: Single Writer Enforcement for Progress (P0)

**User Story:** As a state management engineer, I want only system_progression to mutate while legacy supplier_extraction_progress remains read-only for compatibility, so that dual writer drift is eliminated and state consistency is maintained.

#### Acceptance Criteria

1. WHEN implementing normalizing shim THEN the system SHALL keep legacy update_supplier_extraction_progress API but implement as shim writing only to system_progression
2. WHEN processing legacy calls THEN the system SHALL clamp values, normalize phase ("supplier" vs "amazon_analysis"), and freeze totals via denominator freeze
3. WHEN migrating hot callsites THEN the system SHALL replace legacy calls with update_progression_unified in hybrid loop and per-product callback
4. WHEN during supplier phase THEN the system SHALL ensure only system_progression indices change while legacy block stays static
5. WHEN normalizing phase THEN the system SHALL correctly set phase as "supplier" throughout supplier extraction
6. WHEN handling extraction_phase parameter THEN the system SHALL normalize "fresh_categories" to "supplier" and preserve other phase values as strings

### Requirement 3: Denominator Freeze (P0)

**User Story:** As a progress tracking engineer, I want system_progression.total_categories frozen once and never replaced by batch/chunk counts, so that it remains stable across phases and resumes, eliminating the 1 vs 119 anomaly.

#### Acceptance Criteria

1. WHEN implementing authoritative total categories THEN the system SHALL introduce _authoritative_total_categories() in orchestrator with precedence: runtime_settings.total_categories → system_progression.total_categories → computed len(category_urls) → config fallback
2. WHEN freezing totals THEN the system SHALL freeze once and reuse everywhere, caching the value to avoid recomputation
3. WHEN replacing batch counts THEN the system SHALL replace any total_categories=total_batches or local len(batch) with _authoritative_total_categories()
4. WHEN on first write and resume THEN the system SHALL ensure total_categories stays the same value across both phases (supplier & Amazon)
5. WHEN preferring frozen values THEN the system SHALL prioritize previously-frozen values for resume stability
6. WHEN computing fallback THEN the system SHALL use len(self._pre_resolved_category_urls) as the computed fallback when no frozen value exists

### Requirement 4: Resume Fidelity & Banners (P0)

**User Story:** As a system operator, I want the system to never resume at 0 unless it's truly a first run and show clear resume banners with correct phase and category progress, so that resume operations are transparent and accurate.

#### Acceptance Criteria

1. WHEN using state manager authority THEN the system SHALL use resume_index = self.state_manager.get_resumption_index() retaining all policy/fallbacks plus bounds guard against current product list length
2. WHEN avoiding raw field reads THEN the system SHALL not read raw fields directly but use state manager authority methods
3. WHEN adding resume banner THEN the system SHALL provide human-readable resume banner with phase and category progress from system_progression
4. WHEN resuming after interruption THEN the system SHALL log "▶ RESUME supplier: category X/Y (system_progression)" and continue from X, not 0
5. WHEN implementing bounds guard THEN the system SHALL ensure resume index does not exceed current product list length
6. WHEN providing forensics THEN the system MAY optionally include +04:00 timestamps for forensics but this is not critical to correctness

### Requirement 5: Per-Product Progress Callback (P0)

**User Story:** As a progress tracking engineer, I want one callback per extracted product in both URL and prefiltered code paths that only updates unified state and triggers periodic cache-save cadence, so that progress tracking is consistent and no legacy back-writes occur.

#### Acceptance Criteria

1. WHEN implementing callback THEN the system SHALL reuse existing callback in both paths without adding a second callback to avoid double saves/log noise
2. WHEN updating state THEN the system SHALL make callback write only unified progression via update_progression_unified method
3. WHEN handling callback failures THEN the system SHALL log callback failures at WARNING level (not DEBUG) so operators see issues
4. WHEN triggering periodic saves THEN the system SHALL ensure periodic atomic saves occur exactly on N cadence even in prefiltered runs with update_frequency_products=N
5. WHEN avoiding legacy writes THEN the system SHALL remove legacy back-writes inside callback and prevent dual-writer drift
6. WHEN updating progression THEN the system SHALL call update_progression_unified with current_phase="supplier", current_category_url, and current_product_index_in_category
### 
Requirement 6: State Validation on Load & Atomic Save (P1)

**User Story:** As a system reliability engineer, I want bounded/capped indices and atomic writes for every state save, so that state corruption is prevented and partial writes are eliminated.

#### Acceptance Criteria

1. WHEN validating on load THEN the system SHALL cap indices to totals and warn on drift and impossible combinations (e.g., current_category_index > total_categories)
2. WHEN implementing atomic persistence THEN the system SHALL ensure save_state() wraps WindowsSaveGuardian.save_json_atomic to avoid partial writes
3. WHEN detecting tampered state THEN the system SHALL cap the index and log a single WARN on tampered state file (cat index > total)
4. WHEN validating loaded state THEN the system SHALL implement validate_loaded_state() with capping and warnings
5. WHEN enforcing atomic saves THEN the system SHALL ensure all state writes use WindowsSaveGuardian.save_json_atomic helper

### Requirement 7: Resume Boundary Tests & State Contradiction Detection

**User Story:** As a quality assurance engineer, I want boundary tests for resume operations and regression tests for state contradictions, so that off-by-one errors and silent regressions are prevented.

#### Acceptance Criteria

1. WHEN implementing boundary tests THEN the system SHALL add boundary tests covering indices 0, 1, n-1, n, n+1 in tests/test_resume_boundary.py
2. WHEN testing resume logic THEN the system SHALL validate that resume(idx) <= n for all boundary conditions to avoid empty slices or crashes
3. WHEN implementing contradiction tests THEN the system SHALL verify the guard by simulating contradictory state values in tests/test_state_contradiction.py
4. WHEN detecting contradictions THEN the system SHALL test state like {"is_fresh_start": True, "successful_products": 10} and assert detect_contradiction(state) is True
5. WHEN ensuring regression protection THEN the system SHALL ensure the contradiction warning remains functional and alerts operators to inconsistent state

### Requirement 8: Minimal Verification Commands & Dependency Order

**User Story:** As a deployment engineer, I want specific verification steps after each surgical fix and clear dependency order, so that fixes are applied safely and can be validated immediately.

#### Acceptance Criteria

1. WHEN implementing verification commands THEN the system SHALL provide specific grep commands for each fix: grep "total_categories" for denominator fix, grep "system_progression" for single-writer fix
2. WHEN establishing dependency order THEN the system SHALL implement fixes in correct order: 1) Denominator freeze, 2) Single writer shim, 3) Filter gating, 4) Resume fidelity, 5) Callback fix
3. WHEN preventing wrong totals THEN the system SHALL implement denominator freeze first to prevent wrong totals from propagating
4. WHEN preventing dual writing THEN the system SHALL implement single writer shim second to prevent dual writing
5. WHEN providing impact assessment THEN the system SHALL specify exactly which files get touched by each surgical fix with minimal change scope

### Requirement 9: Cache Schema Hygiene & Backward Compatibility (P2)

**User Story:** As a data integrity engineer, I want private/transient keys stripped before cache persistence and backward compatibility validation, so that cache diffs remain clean and legacy compatibility is maintained.

#### Acceptance Criteria

1. WHEN stripping private keys THEN the system SHALL strip any private/transient keys (e.g., __cb_meta, or any key starting with __) before persisting to supplier cache
2. WHEN preventing cache interference THEN the system SHALL prevent "hidden" attributes from interfering with URL/EAN comparison and keep cache diffs clean
3. WHEN sanitizing products THEN the system SHALL implement sanitized = {k: v for k, v in p.items() if not str(k).startswith("__")} before new_products.append(sanitized)
4. WHEN implementing backward compatibility checks THEN the system SHALL add drift/contradiction warnings that are log-only
5. WHEN validating phase transitions THEN the system SHALL add validate_phase_transition() with WARN on invalid hops (e.g., amazon→amazon)

### Requirement 10: Surgical-Only Implementation Scope & Rollback Criteria

**User Story:** As a project manager, I want clear scope limitation to surgical fixes only with defined rollback criteria, so that over-engineering is avoided and system stability is maintained.

#### Acceptance Criteria

1. WHEN limiting scope THEN the system SHALL implement only surgical fixes to existing broken functionality: filter gating, single writer, denominator, resume fidelity, callback fix
2. WHEN deferring enhancements THEN the system SHALL defer all validation features, monitoring enhancements, schema hygiene, and new safeguards that are not surgical fixes
3. WHEN defining rollback triggers THEN the system SHALL establish rollback criteria: if denominator fix causes crashes → revert, if single writer breaks resume → revert to dual writer temporarily, if filter gating stops processing → revert to original logic
4. WHEN verifying after each fix THEN the system SHALL test basic workflow with python run_custom_poundwholesale.py --max-products 5, check log sizes <1MB for 5 products, check state shows correct totals
5. WHEN maintaining minimal changes THEN the system SHALL limit changes to: Plan B (single writer) only utils/fixed_enhanced_state_manager.py, Plan C (denominator) only tools/passive_extraction_workflow_latest.py (2 locations), Plan A (filter gating) only tools/passive_extraction_workflow_latest.py (dedup methods)