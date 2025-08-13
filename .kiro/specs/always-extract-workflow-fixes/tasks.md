# Implementation Plan

## Task Overview

Convert the system remediation design into a series of coding tasks that implement reliable resume functionality, state consistency, and data integrity. Each task builds incrementally with mandatory sequencing requirements and invariant enforcement.

- [x] 1. Implement Data Integrity Guardian with mandatory startup reconciliation



  - Create `DataIntegrityGuardian` class with sequenced startup reconciliation
  - Implement `reconcile_on_startup_prereq()` method that MUST run before resume calculation
  - Add linking map hydration from supplier cache with atomic state persistence
  - Create reconciliation logging with detailed item tracking
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 1.1 Create startup reconciliation prerequisite logic

  - Write method to compare processed_products vs linking_map entries
  - Implement missing entry detection and classification logic
  - Add hydration attempts from supplier cache with fallback to Amazon analysis marking
  - Create atomic state persistence after reconciliation completion
  - _Requirements: 6.1, 6.2_

- [x] 1.2 Implement linking map hydration from cache

  - Write `hydrate_linking_map_entry()` method to create entries from cached supplier data
  - Add validation for required fields (title, price, EAN) before hydration
  - Implement fallback marking for items that cannot be hydrated
  - Create logging for hydration success/failure with detailed reasons
  - _Requirements: 4.3, 6.2_

- [x] 1.3 Add atomic reconciliation state persistence

  - Implement `persist_reconciled_state_atomic()` with backup rotation
  - Add validation that reconciliation completed successfully before proceeding
  - Create rollback mechanism if persistence fails during reconciliation
  - Add comprehensive logging of reconciliation results and state changes
  - _Requirements: 4.4, 6.5_

- [x] 2. Create Enhanced URL Filter with invariant enforcement


  - Modify `filter_urls()` to accept processed_urls_set parameter for state reconciliation
  - Implement mandatory invariant validation: skip + needs_amazon + needs_full == total_input
  - Add formal denominator calculation: discovered_urls - linking_map_hits
  - Create filter failure snapshots and repair mode entry on invariant failure
  - _Requirements: 2.1, 2.3, 5.1, 5.5_

- [x] 2.1 Add invariant validation with mandatory enforcement

  - Write `validate_filter_invariant()` method with detailed failure logging
  - Implement filter failure snapshot creation for debugging
  - Add invariant gate that prevents queue construction on failure
  - Create repair mode entry or halt mechanism on invariant failure
  - _Requirements: 5.1, 5.5_

- [x] 2.2 Implement formal denominator calculation

  - Write denominator formula: discovered_urls - linking_map_hits
  - Add denominator logging with category ID for traceability
  - Persist denominator atomically with state after filtering
  - Create denominator validation against expected work item counts
  - _Requirements: 5.2, 5.4_

- [x] 2.3 Add processed products reconciliation in filter

  - Implement logic to move processed-but-unlinked items from needs_full to needs_amazon
  - Add reconciliation item tracking and logging
  - Create validation that reconciled items maintain filter invariant
  - Add comprehensive reconciliation result reporting
  - _Requirements: 2.3, 2.4_

- [x] 3. Implement Unified State Manager with accumulator resets




  - Create `UnifiedStateManager` class that updates both system_progression and supplier_extraction_progress
  - Add deterministic per-category accumulator reset on entry and completion
  - Implement guarded breadcrumb logging that only logs when all required fields are populated
  - Create state regression protection with ALLOW_STATE_REGRESSION bypass
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 3.1 Create unified progression update method

  - Write `update_progression()` method that updates both state structures atomically
  - Add validation that both structures remain synchronized
  - Implement field validation before updates to prevent invalid state
  - Create comprehensive logging of state changes with before/after values
  - _Requirements: 1.1, 1.2_

- [x] 3.2 Add deterministic accumulator reset logic

  - Implement `reset_category_accumulators()` for both entry and completion
  - Clear manifest, filtered queues, per-category counters, and in-memory trackers
  - Add reset logging with category ID and timestamp for traceability
  - Create validation that reset completed successfully before proceeding
  - _Requirements: 1.3, 5.4_

- [x] 3.3 Implement guarded breadcrumb logging

  - Write `log_breadcrumb_guarded()` that validates all required fields before logging
  - Add missing field detection and diagnostic warning emission
  - Implement zero denominator detection and warning logging
  - Create breadcrumb delay mechanism when fields are not ready
  - _Requirements: 1.3, 7.1_

- [x] 3.4 Add state regression protection

  - Implement validation in `load_state()` that prevents backwards progress
  - Add ALLOW_STATE_REGRESSION environment variable bypass mechanism
  - Create detailed regression detection logging with specific field comparisons
  - Add SystemExit with clear error message on regression without bypass
  - _Requirements: 1.4, 1.5_

- [x] 4. Create Resume Controller with validation


  - Implement `ResumeController` class that calculates resume points AFTER reconciliation
  - Add resume point validation against current category totals
  - Create safe fallback mechanisms when resume validation fails
  - Add comprehensive resume decision logging with reasoning
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4.1 Implement resume point calculation with prerequisites

  - Write `calculate_resume_point()` that only runs after reconciliation completion
  - Add validation that reconciliation succeeded before resume calculation
  - Implement resume point extraction from reconciled system_progression data
  - Create resume point validation against current system state
  - _Requirements: 3.1, 3.2_

- [x] 4.2 Add resume point validation logic

  - Write `validate_resume_point()` that checks indices against current totals
  - Add logical consistency validation (category exists, phase is valid, etc.)
  - Implement validation failure logging with specific reasons
  - Create safe fallback point calculation when validation fails
  - _Requirements: 3.3, 3.4_

- [x] 4.3 Create safe fallback mechanisms

  - Implement `get_safe_fallback_point()` for invalid resume points
  - Add fallback decision logging with clear reasoning
  - Create fallback point validation to ensure it's actually safe
  - Add user notification of fallback usage with recovery suggestions
  - _Requirements: 3.4, 7.2_

- [x] 5. Implement Queue Processor with separate phases


  - Create `QueueProcessor` class with formal denominator calculation
  - Implement separate supplier and Amazon processing phases with accurate counting
  - Add phase progress tracking with correct denominators
  - Create phase boundary state saves with validation
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 5.1 Add separate phase processing logic

  - Write `process_supplier_phase()` and `process_amazon_phase()` methods
  - Implement accurate work item counting for each phase
  - Add phase-specific progress tracking with correct denominators
  - Create phase completion validation and logging
  - _Requirements: 5.3, 5.4_

- [x] 5.2 Implement accurate queue counting

  - Write logic to calculate total work items as sum of needs_amazon + needs_full
  - Add queue count validation against filter results
  - Implement queue count logging with category ID and breakdown
  - Create queue count mismatch detection and error reporting
  - _Requirements: 5.1, 5.2, 5.5_

- [x] 5.3 Add phase progress tracking

  - Implement `update_phase_progress()` with phase-specific denominators
  - Add progress validation that indices don't exceed totals
  - Create progress logging with phase, category, and product context
  - Add progress state saves at appropriate intervals
  - _Requirements: 5.4, 1.3_

- [x] 6. Create startup sequence orchestration


  - Implement main startup sequence: Reconcile → Resume → Filter → Process
  - Add sequence validation that each phase completes before the next begins
  - Create atomic state transitions between sequence phases
  - Add comprehensive sequence logging with timing and success indicators
  - _Requirements: 6.1, 6.5, 3.1_

- [x] 6.1 Implement mandatory sequence ordering

  - Write startup orchestrator that enforces Reconcile → Resume → Filter order
  - Add validation that reconciliation completes successfully before resume calculation
  - Implement sequence phase completion checks before proceeding
  - Create sequence failure handling with clear error messages
  - _Requirements: 6.1, 6.5_

- [x] 6.2 Add atomic state transitions

  - Implement atomic state saves between each sequence phase
  - Add state transition validation to ensure consistency
  - Create rollback mechanisms if transitions fail
  - Add state transition logging with before/after snapshots
  - _Requirements: 4.4, 6.5_

- [x] 7. Add comprehensive error handling and recovery


  - Implement invariant failure handling with repair mode
  - Add state corruption detection with automatic recovery attempts
  - Create diagnostic snapshots for debugging filter and queue failures
  - Add recovery procedure documentation in error messages
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 7.1 Implement invariant failure handling

  - Write invariant failure detection with detailed logging
  - Add filter failure snapshot creation for debugging
  - Implement repair mode entry or safe halt on invariant failure
  - Create invariant failure recovery procedures with user guidance
  - _Requirements: 5.5, 7.1, 7.2_

- [x] 7.2 Add state corruption detection

  - Implement state consistency validation across all data structures
  - Add corruption detection logging with specific inconsistency details
  - Create automatic repair attempts for common corruption patterns
  - Add manual recovery procedure documentation for complex cases
  - _Requirements: 4.1, 4.2, 7.3, 7.4_

- [x] 7.3 Create diagnostic capabilities

  - Implement comprehensive diagnostic logging for all failure modes
  - Add state snapshot creation for debugging complex issues
  - Create diagnostic data export for support and analysis
  - Add diagnostic validation to ensure snapshots are complete and useful
  - _Requirements: 7.1, 7.3, 7.5_

- [x] 8. Add comprehensive testing suite


  - Create unit tests for all new components with edge case coverage
  - Implement integration tests for startup sequence and resume functionality
  - Add performance tests for large state files and reconciliation operations
  - Create end-to-end tests that validate complete interrupt-resume cycles
  - _Requirements: All requirements validation_

- [x] 8.1 Create unit tests for core components

  - Write tests for UnifiedStateManager with state regression scenarios
  - Add tests for Enhanced URL Filter with invariant validation
  - Implement tests for DataIntegrityGuardian with reconciliation scenarios
  - Create tests for ResumeController with validation failure cases
  - _Requirements: 1.1-1.5, 2.1-2.4, 6.1-6.5, 3.1-3.4_

- [x] 8.2 Implement integration tests

  - Write end-to-end resume tests with actual interruption and restart
  - Add startup sequence tests with reconciliation → resume → filter ordering
  - Implement data consistency tests with intentional inconsistencies
  - Create queue processing tests with mixed category scenarios
  - _Requirements: All requirements integration validation_

- [x] 8.3 Add performance and stress tests

  - Write tests for large state files (10k+ processed products)
  - Add reconciliation performance tests with 1k+ inconsistent items
  - Implement memory usage tests for large linking maps
  - Create concurrent access tests for atomic operations
  - _Requirements: Performance validation for all components_