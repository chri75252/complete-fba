# Requirements Document - State Consistency Fixes

## Introduction

This specification addresses critical state management inconsistencies identified in incident state-consistency-20250816. The system currently suffers from missing calculation logic, non-atomic updates, and lack of invariant validation, leading to unreliable resume functionality and incorrect progress tracking.

## Requirements

### Requirement 1: Critical Data Flow Integrity (P0 - URGENT)

**User Story:** As a system operator, I want extracted products to flow correctly through the manifest generation pipeline, so that Amazon processing is not skipped due to empty URL lists.

#### Acceptance Criteria

1. WHEN products are successfully extracted from a category THEN the system SHALL populate category_manifests dictionary with extracted product URLs
2. WHEN manifest generation occurs THEN the system SHALL receive the actual extracted URLs instead of empty lists
3. WHEN URL filtering runs THEN it SHALL receive proper input (in>0) from populated manifests
4. WHEN Amazon processing phase begins THEN it SHALL have URLs to process instead of being skipped

### Requirement 2: Atomic State Management

**User Story:** As a system operator, I want all related state fields to be updated atomically, so that partial writes cannot create inconsistent state.

#### Acceptance Criteria

1. WHEN updating category information THEN the system SHALL update current_category_url, current_category_index, and products_extracted_total in a single atomic operation
2. WHEN a state update fails THEN the system SHALL rollback all related changes to maintain consistency
3. WHEN multiple state sections need synchronization THEN the system SHALL use transactional updates to prevent divergence
4. WHEN concurrent access occurs THEN the system SHALL use proper locking mechanisms to prevent race conditions

### Requirement 3: Missing Calculation Logic Implementation

**User Story:** As a system operator, I want products_extracted_total to be calculated from actual data sources, so that it accurately reflects the current extraction progress.

#### Acceptance Criteria

1. WHEN the system initializes THEN products_extracted_total SHALL be calculated from category completion data
2. WHEN products are extracted THEN products_extracted_total SHALL be updated using summation logic
3. WHEN state is loaded THEN products_extracted_total SHALL be recalculated to ensure accuracy
4. WHEN category processing completes THEN products_extracted_total SHALL reflect the cumulative total across all categories

### Requirement 4: State Invariant Validation

**User Story:** As a system operator, I want the system to automatically detect and repair state inconsistencies, so that data integrity is maintained without manual intervention.

#### Acceptance Criteria

1. WHEN saving state THEN the system SHALL validate that products_extracted_total equals successful_products
2. WHEN invariant violations are detected THEN the system SHALL automatically repair the inconsistency
3. WHEN cross-section synchronization is required THEN the system SHALL ensure supplier_extraction_progress and system_progression have consistent values
4. WHEN validation fails THEN the system SHALL log the violation and apply deterministic repair rules

### Requirement 5: Enhanced State Monitoring

**User Story:** As a system administrator, I want comprehensive monitoring of state operations, so that I can detect and respond to consistency issues proactively.

#### Acceptance Criteria

1. WHEN state updates occur THEN the system SHALL emit structured logs with operation details
2. WHEN invariant violations are detected THEN the system SHALL increment violation metrics
3. WHEN reconciliation operations run THEN the system SHALL track success/failure rates
4. WHEN partial writes are prevented THEN the system SHALL log the prevention action

### Requirement 6: Robust Resume Functionality

**User Story:** As a system operator, I want reliable resume functionality that works consistently across system restarts, so that processing can continue without data loss or duplication.

#### Acceptance Criteria

1. WHEN the system resumes THEN it SHALL validate state consistency before continuing
2. WHEN inconsistencies are found during resume THEN the system SHALL automatically reconcile the state
3. WHEN resume point calculation occurs THEN it SHALL use a single source of truth
4. WHEN resume validation fails THEN the system SHALL provide clear error messages and recovery options

### Requirement 7: Backward Compatibility

**User Story:** As a system operator, I want the enhanced state management to work with existing state files, so that current processing can continue without disruption.

#### Acceptance Criteria

1. WHEN loading existing state files THEN the system SHALL handle missing calculation fields gracefully
2. WHEN migrating from old state format THEN the system SHALL preserve all existing data
3. WHEN new validation logic is applied THEN it SHALL not break existing workflows
4. WHEN reconciliation is needed THEN it SHALL create backups before making changes

### Requirement 8: Performance Optimization

**User Story:** As a system operator, I want state management improvements to maintain or improve system performance, so that processing efficiency is not degraded.

#### Acceptance Criteria

1. WHEN atomic updates are implemented THEN they SHALL not significantly impact processing speed
2. WHEN invariant validation runs THEN it SHALL complete within acceptable time limits
3. WHEN monitoring is added THEN it SHALL have minimal performance overhead
4. WHEN calculation logic is implemented THEN it SHALL be optimized for frequent execution

### Requirement 9: Error Recovery and Resilience

**User Story:** As a system operator, I want the system to gracefully handle state corruption and provide recovery mechanisms, so that processing can continue even after unexpected failures.

#### Acceptance Criteria

1. WHEN state corruption is detected THEN the system SHALL attempt automatic recovery
2. WHEN automatic recovery fails THEN the system SHALL provide manual recovery procedures
3. WHEN backup restoration is needed THEN it SHALL preserve processing progress where possible
4. WHEN critical errors occur THEN the system SHALL fail safely without data loss