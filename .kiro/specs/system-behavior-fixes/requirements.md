# Requirements Document

## Introduction

This specification addresses critical system behavior issues in the Amazon FBA Agent System that are causing confusion, incorrect processing, and resumption failures. The system currently has several architectural problems that prevent proper category processing, accurate product counting, and reliable state management.

## Requirements

### Requirement 1: Fix SystemConfigLoader Missing Method

**User Story:** As a system administrator, I want the SystemConfigLoader to properly load configuration without throwing attribute errors, so that the system can initialize correctly without warnings.

#### Acceptance Criteria

1. WHEN the system initializes THEN the SystemConfigLoader SHALL have a working `load_config()` method
2. WHEN the PassiveExtractionWorkflow attempts to initialize state manager with totals THEN it SHALL NOT throw "'SystemConfigLoader' object has no attribute 'load_config'" error
3. WHEN the system starts THEN it SHALL load configuration without any attribute-related warnings

### Requirement 2: Transparent Category URL Extraction Logging

**User Story:** As a system operator, I want to see exactly which product URLs are being extracted from each category before they are checked against cache files, so that I can verify the system is processing all products correctly.

#### Acceptance Criteria

1. WHEN the system processes a category THEN it SHALL first extract and log all product URLs from that category
2. WHEN product URLs are extracted THEN the system SHALL display the count of URLs found (e.g., "Extracted 498 product URLs from category X")
3. WHEN the system checks against linking map and product cache THEN it SHALL clearly show which specific URLs are being checked
4. WHEN a product is found in cache/linking map THEN the system SHALL log the specific URL that was matched
5. WHEN the system reports "need extraction" counts THEN it SHALL be based on the actual extracted URLs minus the cached ones

### Requirement 3: Accurate Product Count Reconciliation

**User Story:** As a system operator, I want the system to accurately count and report the number of products that need processing in each category, so that I can trust the progress metrics and understand what work remains.

#### Acceptance Criteria

1. WHEN the system processes a category THEN it SHALL extract all product URLs first before any cache checking
2. WHEN comparing against linking map THEN it SHALL use the actual extracted URLs as the baseline, not cached estimates
3. WHEN reporting "X products need extraction" THEN X SHALL equal (extracted URLs - URLs found in linking map - URLs found in product cache)
4. WHEN the system shows different counts (e.g., 444 expected vs 7 actual) THEN it SHALL explain the discrepancy in the logs
5. WHEN products appear in multiple categories THEN the system SHALL handle deduplication correctly and report it clearly

### Requirement 4: Reliable Processing State Resumption

**User Story:** As a system operator, I want the system to resume processing from where it left off when interrupted, so that I don't lose progress and can continue processing efficiently.

#### Acceptance Criteria

1. WHEN the system is interrupted THEN it SHALL save the exact category and product position being processed
2. WHEN the system restarts THEN it SHALL resume from the last saved position, not from the beginning
3. WHEN resuming THEN the system SHALL display "Resuming from category X, product Y of Z" 
4. WHEN the processing state shows specific indexes THEN those indexes SHALL accurately reflect the actual resumption point
5. WHEN the system completes a category THEN it SHALL mark that category as complete and not reprocess it on restart

### Requirement 5: Clear Cache Hit Workflow Explanation

**User Story:** As a system operator, I want to understand why the system is showing cache hits and what processing phase it's in, so that I can monitor progress effectively and identify any issues.

#### Acceptance Criteria

1. WHEN the system shows cache hits THEN it SHALL explain what phase of processing is occurring (e.g., "Gap processing phase: checking for unprocessed products")
2. WHEN all products in a category are cached THEN the system SHALL clearly state "All products in category X already processed, moving to next category"
3. WHEN the system performs "enhanced filtering" THEN it SHALL explain why this step is necessary and what it accomplishes
4. WHEN the system reports "100% efficiency gain" THEN it SHALL clarify whether this means the category is complete or if gap processing is needed
5. WHEN the system moves between categories THEN it SHALL clearly log the transition and reason

### Requirement 6: Comprehensive System State Validation

**User Story:** As a system operator, I want the system to validate its internal state against actual file contents to ensure accuracy, so that processing decisions are based on correct information.

#### Acceptance Criteria

1. WHEN the system starts THEN it SHALL validate total product counts against actual cache file contents
2. WHEN the system calculates processed products THEN it SHALL count actual entries in the linking map file
3. WHEN there are discrepancies between state and files THEN the system SHALL log the differences and explain corrective actions
4. WHEN the system updates progress THEN it SHALL ensure state files accurately reflect the current processing position
5. WHEN resuming processing THEN the system SHALL verify that the resumption point is valid based on actual file contents

### Requirement 7: Enhanced Error Reporting and Diagnostics

**User Story:** As a system operator, I want detailed diagnostic information when the system encounters issues or unexpected behavior, so that I can quickly identify and resolve problems.

#### Acceptance Criteria

1. WHEN the system encounters unexpected product counts THEN it SHALL provide detailed breakdown of where the numbers come from
2. WHEN cache hits occur THEN the system SHALL log which cache type (EAN, URL, linking map) was hit and the specific product
3. WHEN the system skips products THEN it SHALL clearly explain why each product was skipped
4. WHEN processing state is inconsistent THEN the system SHALL provide diagnostic information about the inconsistency
5. WHEN the system makes processing decisions THEN it SHALL log the reasoning behind those decisions