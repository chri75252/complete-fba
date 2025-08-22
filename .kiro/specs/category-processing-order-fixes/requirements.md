# Requirements Document - Category Processing Order Fixes

## Introduction

This specification addresses critical category processing order issues in the Amazon FBA Agent System where the system processes categories based on completion percentage rather than the natural JSON file order, causing fresh starts to jump to incorrect category indices (like index 93) and preventing proper sequential processing. The system currently uses category_completion_tracker.py which overrides the intended sequential processing behavior that worked correctly in older versions.

## Requirements

### Requirement 1: Sequential Category Processing Order

**User Story:** As a system operator, I want categories to be processed in the exact order they appear in the JSON configuration file, so that processing follows a predictable sequence regardless of completion status.

#### Acceptance Criteria

1. WHEN system loads categories from JSON file THEN processing order SHALL follow the natural array sequence
2. WHEN fresh start occurs THEN system SHALL begin with the first category (index 0) from the JSON file
3. WHEN system resumes THEN it SHALL continue from the next sequential category after the last completed one
4. WHEN category_completion_tracker.py logic is removed THEN no completion-percentage-based reordering SHALL occur

### Requirement 2: Fresh Start Category Selection

**User Story:** As a system operator, I want fresh starts to always begin with the first category in the JSON file, so that processing starts from a known, predictable state.

#### Acceptance Criteria

1. WHEN no processing state file exists THEN system SHALL select category at index 0
2. WHEN FORCE_FRESH_START environment variable is set THEN system SHALL ignore existing state and start at index 0
3. WHEN fresh start is detected THEN system SHALL NOT apply URL/index correction logic
4. WHEN fresh start begins THEN logs SHALL show "🆕 FRESH START: Starting from category 0" instead of correction messages

### Requirement 3: Resume Point Accuracy

**User Story:** As a system operator, I want the system to resume from the correct category index based on actual progress, so that no categories are skipped or repeated unnecessarily.

#### Acceptance Criteria

1. WHEN system resumes THEN current_category_index SHALL reflect the next unprocessed category
2. WHEN resume occurs THEN system SHALL use state_manager.get_current_category_index() for positioning
3. WHEN resume point is determined THEN it SHALL NOT be overridden by completion tracker logic
4. WHEN resume happens THEN logs SHALL show "🔄 RESUMING: Starting from category index X" with correct sequential index

### Requirement 4: Category Completion Tracker Removal

**User Story:** As a system developer, I want the category_completion_tracker.py dependency removed from the main workflow, so that category selection follows simple sequential logic instead of complex completion-based algorithms.

#### Acceptance Criteria

1. WHEN workflow initializes THEN it SHALL NOT import category_completion_tracker module
2. WHEN category selection occurs THEN it SHALL use direct JSON file indexing
3. WHEN completion metrics are needed THEN they SHALL be calculated from state data, not external tracker
4. WHEN system determines next category THEN it SHALL use simple index arithmetic: current_index + 1

### Requirement 5: Fresh Start Detection Enhancement

**User Story:** As a system operator, I want reliable fresh start detection that prevents inappropriate correction logic, so that fresh starts behave consistently and predictably.

#### Acceptance Criteria

1. WHEN state_manager.is_fresh_start() is called THEN it SHALL return true for genuinely fresh starts
2. WHEN fresh start is detected THEN URL/index correction logic SHALL be bypassed completely
3. WHEN FORCE_FRESH_START is enabled THEN system SHALL clear existing state and behave as fresh start
4. WHEN fresh start guard activates THEN logs SHALL show "🆕 FRESH START: Skipping URL/index correction"

### Requirement 6: Manifest Persistence Reliability

**User Story:** As a system operator, I want category manifests to be populated with actual product URLs instead of empty lists, so that downstream processing has the necessary data to operate.

#### Acceptance Criteria

1. WHEN category URLs are discovered THEN they SHALL be stored in category_manifests immediately
2. WHEN manifest is populated THEN logs SHALL show "💾 MANIFEST: N URLs stored for [category]" with N > 0
3. WHEN manifests are saved THEN they SHALL persist to disk for resume functionality
4. WHEN filtering occurs THEN it SHALL operate on populated manifests, not empty lists

### Requirement 7: Index Correction Logic Refinement

**User Story:** As a system operator, I want index correction to only apply during legitimate resume scenarios, so that fresh starts are not incorrectly "corrected" to wrong indices.

#### Acceptance Criteria

1. WHEN fresh start is detected THEN _validate_category_consistency SHALL return selected_category_url unchanged
2. WHEN resume occurs with state mismatch THEN correction logic MAY apply to align with saved state
3. WHEN correction is applied THEN it SHALL only happen for resume scenarios, never fresh starts
4. WHEN correction occurs THEN logs SHALL clearly indicate "Resume-only correction path"

### Requirement 8: Startup State Recomputation

**User Story:** As a system operator, I want accurate product totals calculated at startup from ground truth data, so that progress tracking reflects actual system state.

#### Acceptance Criteria

1. WHEN system starts THEN products_extracted_total SHALL be recalculated from actual cache data
2. WHEN startup recomputation occurs THEN logs SHALL show "📊 FIX F: Recalculating products_extracted_total from ground truth"
3. WHEN recomputation completes THEN updated totals SHALL be persisted to state
4. WHEN recomputation fails THEN system SHALL log warning but continue operation

### Requirement 9: Category Processing Integration

**User Story:** As a system developer, I want the category processing logic to integrate seamlessly with existing state management and resume functionality, so that all system components work together correctly.

#### Acceptance Criteria

1. WHEN category processing begins THEN it SHALL coordinate with state_manager for current position
2. WHEN category completes THEN state SHALL be updated with next sequential index
3. WHEN all categories are processed THEN system SHALL recognize completion and terminate gracefully
4. WHEN integration occurs THEN existing APIs SHALL remain stable and unchanged

### Requirement 10: Backward Compatibility Preservation

**User Story:** As a system maintainer, I want the fixes to preserve all existing functionality while correcting the category processing order, so that no regression occurs in other system components.

#### Acceptance Criteria

1. WHEN fixes are applied THEN all existing public APIs SHALL remain unchanged
2. WHEN category processing is fixed THEN other workflow components SHALL continue operating normally
3. WHEN changes are implemented THEN existing logging patterns SHALL be preserved where not explicitly changed
4. WHEN system operates THEN performance characteristics SHALL be maintained or improved