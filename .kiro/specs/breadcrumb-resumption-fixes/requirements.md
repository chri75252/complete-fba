# Requirements Document

## Introduction

This specification addresses the critical breadcrumb tracking and resumption system issues in the FBA Data Extraction System. The system currently suffers from missing resumption field population, inconsistent state synchronization, and persistent breadcrumb warnings that prevent accurate progress tracking and precise resumption functionality.

## Requirements

### Requirement 1: Breadcrumb Field Population

**User Story:** As a system operator, I want all resumption tracking fields to be accurately populated during processing, so that I can monitor exact progress and resume from precise interruption points.

#### Acceptance Criteria

1. WHEN the system processes a category THEN it SHALL populate `current_category_index` and `total_categories` fields
2. WHEN the system processes a product THEN it SHALL populate `current_product_index_in_category` and `total_products_in_current_category` fields  
3. WHEN the system transitions phases THEN it SHALL update the `current_phase` field accurately
4. WHEN the system saves state THEN all breadcrumb fields SHALL be present and valid
5. IF any breadcrumb field is missing THEN the system SHALL populate it before logging breadcrumbs

### Requirement 2: State Structure Synchronization

**User Story:** As a system operator, I want both state structures to remain synchronized, so that resumption works consistently regardless of which structure is accessed.

#### Acceptance Criteria

1. WHEN `system_progression` is updated THEN `supplier_extraction_progress` SHALL be updated with corresponding values
2. WHEN category processing begins THEN both structures SHALL reflect the same category index and URL
3. WHEN product processing progresses THEN both structures SHALL show the same product index
4. WHEN state is saved THEN both structures SHALL contain consistent values
5. IF state inconsistency is detected THEN the system SHALL automatically synchronize the structures

### Requirement 3: Workflow Integration

**User Story:** As a system operator, I want the workflow to properly integrate with resumption tracking, so that progress is accurately tracked without breaking existing functionality.

#### Acceptance Criteria

1. WHEN a category begins processing THEN the workflow SHALL call category initialization methods
2. WHEN a product is processed THEN the workflow SHALL call product progress update methods
3. WHEN a category completes THEN the workflow SHALL call category completion methods
4. WHEN processing phases change THEN the workflow SHALL update phase tracking
5. IF workflow integration is missing THEN the system SHALL provide fallback population mechanisms

### Requirement 4: Index-Based Resumption

**User Story:** As a system operator, I want the system to support index-based resumption, so that processing can skip entire completed categories and resume at exact product positions.

#### Acceptance Criteria

1. WHEN the system resumes THEN it SHALL skip completed categories based on category index
2. WHEN resuming within a category THEN it SHALL skip completed products based on product index
3. WHEN resumption indices are invalid THEN it SHALL fall back to URL-based resumption
4. WHEN resumption is successful THEN it SHALL log the exact resumption point
5. IF index-based resumption fails THEN the system SHALL use URL-based resumption as backup

### Requirement 5: Category Processing Optimization

**User Story:** As a system operator, I want the system to efficiently skip completed categories, so that resumption is fast and doesn't waste time re-scanning completed work.

#### Acceptance Criteria

1. WHEN a category is fully processed THEN it SHALL be marked as completed in state
2. WHEN resuming THEN the system SHALL skip entirely completed categories without scanning
3. WHEN a category is partially processed THEN it SHALL resume at the correct product index
4. WHEN category totals change THEN the system SHALL update the tracking accordingly
5. IF category completion status is unclear THEN the system SHALL verify by checking processed products

### Requirement 6: Progress Tracking Accuracy

**User Story:** As a system operator, I want accurate progress tracking and completion estimates, so that I can monitor system performance and predict completion times.

#### Acceptance Criteria

1. WHEN processing begins THEN the system SHALL calculate total work items accurately
2. WHEN progress updates THEN completion percentages SHALL be calculated correctly
3. WHEN categories are discovered THEN total category counts SHALL be updated in real-time
4. WHEN products are discovered THEN category product counts SHALL be updated dynamically
5. IF progress calculations are inaccurate THEN the system SHALL recalculate based on current state

### Requirement 7: Breadcrumb Logging Enhancement

**User Story:** As a system operator, I want clear and actionable breadcrumb messages, so that I can understand system status and troubleshoot issues effectively.

#### Acceptance Criteria

1. WHEN all fields are populated THEN breadcrumbs SHALL show complete resumption information
2. WHEN fields are missing THEN the system SHALL populate them before logging
3. WHEN resumption points are logged THEN they SHALL include category URL and phase information
4. WHEN errors occur THEN breadcrumb messages SHALL provide actionable guidance
5. IF breadcrumb logging fails THEN the system SHALL continue processing without interruption

### Requirement 8: Error Recovery and Validation

**User Story:** As a system operator, I want robust error recovery for resumption tracking, so that temporary issues don't break the entire processing workflow.

#### Acceptance Criteria

1. WHEN resumption fields are missing THEN the system SHALL attempt to reconstruct them from available data
2. WHEN state corruption is detected THEN the system SHALL repair inconsistencies automatically
3. WHEN resumption indices are out of bounds THEN the system SHALL reset to safe values
4. WHEN category/product counts change THEN the system SHALL adjust indices accordingly
5. IF automatic recovery fails THEN the system SHALL provide manual recovery procedures

### Requirement 9: Backward Compatibility

**User Story:** As a system operator, I want the enhanced resumption system to maintain compatibility with existing functionality, so that current workflows continue to work without modification.

#### Acceptance Criteria

1. WHEN URL-based resumption is used THEN it SHALL continue to work as before
2. WHEN legacy state structures are accessed THEN they SHALL contain valid data
3. WHEN existing workflow methods are called THEN they SHALL work without modification
4. WHEN resumption fails THEN the system SHALL fall back to existing URL-based logic
5. IF new features cause issues THEN they SHALL be disabled automatically with graceful degradation

### Requirement 10: Performance Optimization

**User Story:** As a system operator, I want resumption enhancements to improve rather than degrade system performance, so that processing becomes more efficient over time.

#### Acceptance Criteria

1. WHEN categories are completed THEN they SHALL be skipped without URL scanning
2. WHEN resuming within categories THEN only remaining products SHALL be processed
3. WHEN progress is tracked THEN overhead SHALL be minimal and non-blocking
4. WHEN state is updated THEN operations SHALL be atomic and efficient
5. IF performance degrades THEN optimizations SHALL be applied to maintain speed