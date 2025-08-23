# Requirements Document

## Introduction

This feature addresses critical issues in the Amazon FBA Agent System's processing workflow, specifically focusing on hybrid processing mode optimization, metrics synchronization, and system progression tracking. The system currently has fundamental flaws in how it handles product processing, state management, and progress tracking across different processing modes.

## Requirements

### Requirement 1: Hybrid Processing Mode Workflow Optimization

**User Story:** As a system administrator, I want the hybrid processing mode to correctly handle product filtering and progression tracking, so that the system can efficiently process products without redundant operations and maintain accurate state.

#### Acceptance Criteria

1. WHEN the system runs in hybrid processing mode THEN it SHALL apply filtering logic before product extraction, not after
2. WHEN products are found in the product cache THEN the system SHALL proceed to Amazon analysis instead of skipping them entirely
3. WHEN the system processes products in chunks THEN it SHALL maintain accurate progression metrics for resumption after interruption
4. IF a product exists in the linking map THEN the system SHALL skip it entirely as it is fully processed
5. WHEN the system switches between supplier extraction and Amazon analysis phases THEN it SHALL update the current_phase indicator correctly

### Requirement 2: System Progression Metrics Synchronization

**User Story:** As a system operator, I want accurate and consistent progression metrics, so that I can track system progress and the system can resume correctly after interruptions.

#### Acceptance Criteria

1. WHEN the system updates progression metrics THEN it SHALL differentiate between system-internal metrics (for resumption) and user-display metrics (for monitoring)
2. WHEN the system processes products THEN it SHALL update supplier_extraction_resumption_index and amazon_analysis_resumption_index separately
3. WHEN category totals are discovered during URL extraction THEN the system SHALL update total_products_in_current_category if it differs from initial estimates
4. WHEN the system saves state THEN it SHALL use atomic writes with frequency of 1-3 products maximum
5. IF the system is interrupted THEN it SHALL be able to resume from the exact product and phase where it stopped

### Requirement 3: FBA Financial Report Batch Configuration Fix

**User Story:** As a financial analyst, I want FBA reports to contain only the configured batch size of products, so that reports are manageable and processing is efficient.

#### Acceptance Criteria

1. WHEN generating FBA financial reports THEN the system SHALL read batch size from system.financial_report_batch_size in system config
2. WHEN the batch size is configured as N THEN the FBA report SHALL contain exactly N products, not 5000+
3. WHEN processing financial reports THEN the system SHALL respect the configured batch toggle setting
4. IF no batch size is configured THEN the system SHALL use a default value of 50 products

### Requirement 4: Linking Map Duplicate Prevention

**User Story:** As a data integrity manager, I want the linking map to contain unique entries only, so that system performance is optimal and data is consistent.

#### Acceptance Criteria

1. WHEN adding entries to the linking map THEN the system SHALL check for existing entries using supplier_url as the unique key
2. WHEN a duplicate entry is detected THEN the system SHALL update the existing entry instead of creating a new one
3. WHEN the system loads the linking map THEN it SHALL maintain hash indexes for O(1) lookup performance
4. WHEN duplicate prevention is active THEN the system SHALL reduce duplicate entries from current 9.5% to less than 1%

### Requirement 5: Cache vs Linking Map Logic Correction

**User Story:** As a system architect, I want clear distinction between cache hits and linking map hits, so that products are processed through the complete workflow correctly.

#### Acceptance Criteria

1. WHEN a product is found in the product cache THEN it SHALL be marked as "supplier data available" and proceed to Amazon analysis
2. WHEN a product is found in the linking map THEN it SHALL be marked as "fully processed" and skipped entirely
3. WHEN filtering products THEN the system SHALL prioritize linking map checks over product cache checks
4. WHEN reporting metrics THEN the system SHALL clearly distinguish between cache hits (partial) and linking map hits (complete)
5. WHEN products have supplier data but no Amazon data THEN they SHALL be processed through Amazon analysis workflow

### Requirement 6: Processing State File Consistency

**User Story:** As a system monitor, I want the processing state file to show consistent and accurate values, so that I can understand system progress and troubleshoot issues effectively.

#### Acceptance Criteria

1. WHEN updating state metrics THEN supplier_extraction_resumption_index SHALL match the actual number of products processed for supplier extraction
2. WHEN updating state metrics THEN amazon_analysis_resumption_index SHALL match the actual number of products processed for Amazon analysis
3. WHEN categories are processed THEN total_categories SHALL remain consistent throughout the run
4. WHEN the system processes multiple categories THEN category progression metrics SHALL accurately reflect the current category being processed
5. WHEN state is saved THEN all related metrics SHALL be synchronized and consistent with each other

### Requirement 7: Redundant Operations Elimination

**User Story:** As a performance optimizer, I want to eliminate redundant filtering and processing operations, so that system efficiency is maximized and processing time is reduced.

#### Acceptance Criteria

1. WHEN processing products THEN filtering SHALL occur only once before extraction, not after
2. WHEN products are already filtered THEN the system SHALL not re-filter them in subsequent steps
3. WHEN the system identifies processed products THEN it SHALL skip them without performing unnecessary operations
4. WHEN efficiency metrics are calculated THEN they SHALL reflect actual time and resource savings
5. WHEN the system reports processing statistics THEN they SHALL accurately represent work performed vs work skipped

### Requirement 8: Category-by-Category Processing Logic

**User Story:** As a system operator, I want the system to process categories individually and sequentially, so that category progression is accurate and the system moves to the next category after completing the current one.

#### Acceptance Criteria

1. WHEN processing a category THEN the system SHALL process only products from that specific category, not mixed products from multiple categories
2. WHEN a category is completed THEN the system SHALL move to the next category URL instead of processing accumulated products from previous categories
3. WHEN extracting URLs from a category THEN the system SHALL update the category total denominator to the actual discovered count (e.g., 76 products instead of 1)
4. WHEN checking product status THEN the system SHALL prioritize linking map checks over product cache checks for each category
5. WHEN category processing is complete THEN the system SHALL update category progression metrics before moving to the next category

### Requirement 9: Linking Map Priority Enforcement

**User Story:** As a data integrity manager, I want the system to check the linking map first before any other processing, so that fully processed products are skipped immediately without unnecessary operations.

#### Acceptance Criteria

1. WHEN processing any product URL THEN the system SHALL check the linking map FIRST before checking product cache
2. WHEN a product exists in the linking map THEN the system SHALL skip it entirely and log it as "fully processed" 
3. WHEN a product is NOT in the linking map but IS in product cache THEN the system SHALL proceed to Amazon analysis only
4. WHEN a product is in neither linking map nor product cache THEN the system SHALL perform full supplier extraction and Amazon analysis
5. WHEN logging product status THEN the system SHALL clearly distinguish between "fully processed" (linking map) and "supplier data available" (product cache)

### Requirement 10: Mixed Product Processing Prevention

**User Story:** As a system administrator, I want to prevent the system from processing mixed products from multiple categories simultaneously, so that category-specific workflow and progression tracking work correctly.

#### Acceptance Criteria

1. WHEN the system loads cached products THEN it SHALL filter them to only include products from the current category being processed
2. WHEN the system accumulates products THEN it SHALL NOT mix products from different categories in the same processing batch
3. WHEN hybrid processing mode is active THEN the system SHALL process categories individually, not accumulate products across categories
4. WHEN 190+ mixed products are detected THEN the system SHALL reject this batch and process only the current category's products
5. WHEN category switching occurs THEN the system SHALL clear any accumulated products from previous categories