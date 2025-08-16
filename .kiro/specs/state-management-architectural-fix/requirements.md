# State Management Architectural Fix - Requirements

## Introduction

The Amazon FBA Agent System has a critical architectural failure in its state management caused by fundamental data authority inversions AND workflow execution bugs. The system consistently calculates wrong resume points (cat=0 instead of cat=2), shows STATE CORRUPTION warnings on every run, and has recovery mechanisms that copy FROM corrupted TO good data. Additionally, even when the state management calculates correct resume points, the workflow execution ignores them and always starts from category 0. This specification addresses both the architectural fixes needed to correct the inverted data flow AND the workflow execution fixes needed to respect the calculated resume points.

## Requirements

### Requirement 1: Fix Resume Point Calculation Source

**User Story:** As a system operator, I want the resume point calculation to use the correct data source (supplier_extraction_progress), so that the system resumes from the actual operational position instead of corrupted tracking data.

#### Acceptance Criteria

1. WHEN calculate_resume_point() executes THEN it SHALL use supplier_extraction_progress as the primary data source
2. WHEN supplier_extraction_progress has valid data THEN it SHALL take precedence over system_progression
3. WHEN both data sources exist THEN the system SHALL choose the most complete source (supplier_extraction_progress)
4. WHEN resume point is calculated THEN it SHALL log which data source was used for transparency
5. IF supplier_extraction_progress is empty THEN system_progression MAY be used as fallback with explicit warning

### Requirement 2: Fix State Corruption Recovery Direction

**User Story:** As a system administrator, I want state corruption recovery to copy FROM good data TO corrupted data (not vice versa), so that corruption is eliminated instead of amplified.

#### Acceptance Criteria

1. WHEN progress_consistency corruption is detected THEN recovery SHALL copy FROM supplier_extraction_progress TO system_progression
2. WHEN sync_progress_systems executes THEN it SHALL use supplier_extraction_progress as the source of truth
3. WHEN recovery actions are applied THEN they SHALL preserve operational data and fix tracking data
4. WHEN recovery completes THEN it SHALL log the direction of data flow for audit purposes
5. IF supplier_extraction_progress is corrupted THEN recovery SHALL use the most complete available data source

### Requirement 3: Fix State Validation Data Destruction

**User Story:** As a system developer, I want state validation to preserve good operational data instead of resetting it to defaults, so that valid processing state is not destroyed by repair logic.

#### Acceptance Criteria

1. WHEN validate_and_repair_state() runs THEN it SHALL check supplier_extraction_progress before defaulting fields
2. WHEN system_progression fields are missing THEN they SHALL be restored from supplier_extraction_progress if available
3. WHEN defaults are applied THEN it SHALL only occur if no operational data exists in any structure
4. WHEN repairs are made THEN they SHALL log what data was preserved vs defaulted
5. IF operational data exists THEN validation SHALL NOT overwrite it with default values

### Requirement 4: Fix Backfill Logic Direction

**User Story:** As a system developer, I want backfill logic to prioritize operational data over tracking data, so that good operational state is used to restore corrupted tracking state.

#### Acceptance Criteria

1. WHEN backfill logic runs THEN it SHALL first try to restore system_progression from supplier_extraction_progress
2. WHEN supplier_extraction_progress has valid data THEN it SHALL be used to populate missing system_progression fields
3. WHEN both structures have data THEN supplier_extraction_progress SHALL take precedence for operational fields
4. WHEN backfill completes THEN it SHALL log which direction data flowed for each field
5. IF supplier_extraction_progress is empty THEN original backfill direction MAY be used as fallback

### Requirement 5: Fix Workflow Execution Resume Point Integration

**User Story:** As a system operator, I want the workflow execution to respect the calculated resume points from state management, so that the system actually resumes from the correct category instead of always starting from category 0.

#### Acceptance Criteria

1. WHEN hybrid processing mode starts THEN it SHALL get the resume category index from state management
2. WHEN processing categories in chunks THEN the loop SHALL start from the resume category index, not from 0
3. WHEN a resume point exists THEN the workflow SHALL process the correct category URL from the resume point
4. WHEN workflow execution begins THEN it SHALL log which category it's resuming from for transparency
5. IF no resume point exists THEN the workflow MAY start from category 0 as default behavior

### Requirement 6: Fix Category URL Consistency in Workflow

**User Story:** As a system developer, I want the workflow to maintain consistency between the category index and category URL, so that the system processes the intended category and updates state correctly.

#### Acceptance Criteria

1. WHEN a category is selected for processing THEN the category URL SHALL match the resume point from state management
2. WHEN category URL mismatch is detected THEN the system SHALL attempt to find the correct category in the list
3. WHEN state is updated during processing THEN both category_index and category_url SHALL be consistent
4. WHEN workflow logs category information THEN it SHALL show both index and URL for verification
5. IF category URL cannot be found THEN the system SHALL log an error and use best-effort recovery

### Requirement 7: Comprehensive Testing and Validation

**User Story:** As a test engineer, I want comprehensive tests that validate both the architectural fixes and workflow execution fixes work correctly under various scenarios, so that the system is proven to resume correctly and handle state corruption properly.

#### Acceptance Criteria

1. WHEN testing resume functionality THEN tests SHALL verify correct data source usage (supplier_extraction_progress)
2. WHEN testing corruption recovery THEN tests SHALL verify recovery copies FROM good TO corrupted data
3. WHEN testing validation logic THEN tests SHALL verify operational data is preserved, not destroyed
4. WHEN testing backfill logic THEN tests SHALL verify correct directional flow prioritizing operational data
5. WHEN testing workflow execution THEN tests SHALL verify resume points are respected and correct categories are processed
6. WHEN testing category consistency THEN tests SHALL verify category index and URL remain synchronized
7. IF any test fails THEN the system SHALL provide detailed diagnostics showing which architectural or workflow fix failed

