# Requirements Document

## Introduction

This specification addresses critical systemic failures in the FBA Data Extraction System that prevent reliable resume functionality and cause data inconsistencies. The system currently suffers from state drift, filter-workflow desynchronization, and non-idempotent resume logic that makes it impossible to reliably continue processing after interruptions.

## Requirements

### Requirement 1: State Management Consistency

**User Story:** As a system operator, I want the system to maintain consistent state tracking across all components, so that resume functionality works reliably.

#### Acceptance Criteria

1. WHEN the system updates processing progress THEN it SHALL update both `system_progression` and `supplier_extraction_progress` structures consistently
2. WHEN the system logs resume breadcrumbs THEN it SHALL show accurate category and product indices that reflect actual processing state
3. WHEN the system saves state THEN it SHALL include complete progression information with non-zero denominators
4. WHEN the system loads state THEN it SHALL validate against regression and prevent backwards progress without explicit override
5. IF state regression is detected THEN the system SHALL raise an error unless `ALLOW_STATE_REGRESSION=1` environment variable is set

### Requirement 2: Filter-Workflow Synchronization

**User Story:** As a system operator, I want the URL filtering and processing workflow to use consistent data sources, so that products are not incorrectly skipped or re-processed.

#### Acceptance Criteria

1. WHEN the system filters URLs THEN it SHALL check linking map, supplier cache, AND processed products state consistently
2. WHEN a product is marked as `needs_full_extraction` by the filter THEN the workflow SHALL NOT skip it as "already processed"
3. WHEN a product exists in processed_products but not in linking_map THEN the system SHALL reclassify it as `needs_amazon_only`
4. WHEN the system processes a category THEN the filter results SHALL match the actual processing queue counts
5. IF a processed product lacks a linking map entry THEN the system SHALL create one from cached data

### Requirement 3: Resume Functionality

**User Story:** As a system operator, I want to be able to resume processing from any interruption point, so that long-running extractions can be completed reliably.

#### Acceptance Criteria

1. WHEN the system starts up THEN it SHALL load the previous state file if it exists
2. WHEN loading previous state THEN it SHALL reconcile any inconsistencies between processed_products and linking_map
3. WHEN resuming processing THEN it SHALL continue from the exact category and product index where it was interrupted
4. WHEN calculating resume point THEN it SHALL validate the indices against current category totals
5. IF resume indices are invalid THEN the system SHALL reset to a safe starting point and log the decision

### Requirement 4: Data Integrity Protection

**User Story:** As a system operator, I want the system to protect against data corruption and maintain referential integrity, so that all processed products are properly tracked.

#### Acceptance Criteria

1. WHEN the system updates global counters THEN it SHALL prevent accidental overwrites with per-category values
2. WHEN a product is processed THEN it SHALL have entries in both supplier cache and linking map
3. WHEN the system detects missing linking map entries THEN it SHALL attempt to hydrate them from supplier cache
4. WHEN saving state THEN it SHALL use atomic operations to prevent corruption
5. IF data inconsistencies are detected THEN the system SHALL log warnings and attempt automatic repair

### Requirement 5: Queue Processing Accuracy

**User Story:** As a system operator, I want accurate processing counts and progress tracking, so that I can monitor system performance and completion status.

#### Acceptance Criteria

1. WHEN the system filters a category THEN it SHALL report accurate counts for skip, needs_amazon, and needs_full
2. WHEN processing begins THEN the logged product count SHALL match the sum of needs_amazon and needs_full items
3. WHEN processing products THEN the system SHALL handle supplier and Amazon phases separately with accurate progress tracking
4. WHEN updating progress THEN it SHALL use the correct total count for the current processing phase
5. IF queue counts don't match filter results THEN the system SHALL log an error and investigate the discrepancy

### Requirement 6: Startup Reconciliation

**User Story:** As a system operator, I want the system to automatically detect and repair data inconsistencies on startup, so that processing can continue without manual intervention.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL compare processed_products against linking_map entries
2. WHEN processed products lack linking map entries THEN it SHALL attempt to create them from supplier cache
3. WHEN reconciliation is performed THEN it SHALL log the number of items found and repaired
4. WHEN reconciliation fails for specific items THEN it SHALL log warnings but continue processing
5. IF reconciliation creates new linking map entries THEN it SHALL save the updated linking map atomically

### Requirement 7: Error Recovery and Logging

**User Story:** As a system operator, I want comprehensive error logging and recovery mechanisms, so that I can diagnose and resolve issues quickly.

#### Acceptance Criteria

1. WHEN state inconsistencies are detected THEN the system SHALL log detailed diagnostic information
2. WHEN resume operations fail THEN the system SHALL provide clear error messages and recovery suggestions
3. WHEN data corruption is suspected THEN the system SHALL create backup copies before attempting repairs
4. WHEN critical errors occur THEN the system SHALL fail safely without corrupting existing data
5. IF automatic recovery is not possible THEN the system SHALL provide manual recovery procedures in the logs