# Requirements Document

## Introduction

This specification addresses the critical breadcrumb tracking and resumption system issues in the FBA Data Extraction System using a **write-ahead, minimal change approach**. The system currently suffers from timing issues where breadcrumb logging occurs before field population, causing persistent "BREADCRUMB DELAYED" warnings and preventing reliable resumption.

## Implementation Approach: Write-Ahead Unified Progression

**Core Strategy**: Enforce write-ahead unified progression updates at four precise workflow points, keeping guarded breadcrumbs, persisting totals immediately after filtering, and adding minimal disk-first load-time backfill.

**Scope**: Edit only 3 files (`tools/passive_extraction_workflow_latest.py`, `utils/fixed_enhanced_state_manager.py`, `utils/url_filter.py`) with no new components or schema fields.

## Non-Goals (Explicitly Out of Scope)

- No new classes (UnifiedProgressTracker, StateSynchronizationManager, BreadcrumbEnhancementSystem, WorkflowIntegrationLayer)
- No schema additions (estimated_completion, breadcrumb_metadata, confidence scores, category_completion maps)
- No complex field reconstruction in breadcrumb logging
- No extensive monitoring/alerting additions in this change set

## Key Implementation Constraints

1. **Write-Ahead Updates**: Enforce progression updates at 4 workflow points BEFORE any side-effects
2. **Single Update Surface**: Use `update_progression_unified()` to update both structures atomically
3. **Staggered Writes**: Throttle saves/logs (every 10 items) with small gaps to prevent file conflicts
4. **Feature Flags**: Support `STATE_STRICT_MODE` and `ALLOW_STATE_REGRESSION` for rollout safety
5. **Fallback Safety**: Maintain existing URL-based resumption and ErrorHandler paths
6. **Minimal Integration**: Enhance existing methods without breaking changes

## Requirements

### Requirement 1: Write-Ahead Field Population

**User Story:** As a system operator, I want breadcrumb fields populated BEFORE any side-effects occur, so that "BREADCRUMB DELAYED" warnings are eliminated through timing fixes.

#### Acceptance Criteria

1. WHEN category processing begins THEN all category fields SHALL be populated before filtering
2. WHEN filtering completes THEN product totals SHALL be persisted using filter denominator
3. WHEN products are processed THEN index updates SHALL occur before each product's side-effects
4. WHEN phases transition THEN current_phase field SHALL be updated atomically
5. IF any write-ahead point fails THEN system SHALL log error but continue processing

### Requirement 2: Staggered Write Protection

**User Story:** As a system operator, I want state saves throttled to prevent file conflicts, so that rapid processing doesn't corrupt state files.

#### Acceptance Criteria

1. WHEN processing products THEN saves SHALL occur every 10 items maximum
2. WHEN concurrent saves occur THEN timing gaps SHALL prevent file access conflicts
3. WHEN processing completes THEN final save SHALL occur regardless of throttle count
4. IF write conflicts occur THEN atomic save mechanism SHALL prevent corruption

### Requirement 3: Index-Based Progression

**User Story:** As a system operator, I want progression tracked by indexes only, so that resumption is deterministic and independent of cache state.

#### Acceptance Criteria

1. WHEN products are processed THEN index advancement SHALL use stored values only
2. WHEN cache is cleared THEN progression SHALL continue using disk-based indexes
3. WHEN linking map entries exist THEN they SHALL NOT affect index progression
4. IF index validation fails THEN system SHALL fall back to URL-based resumption

### Requirement 4: Graceful Integration

**User Story:** As a system operator, I want workflow integration without breaking existing functionality, so that rollback is safe and immediate.

#### Acceptance Criteria

1. WHEN new methods are unavailable THEN system SHALL use hasattr() checks for graceful fallback
2. WHEN integration is disabled THEN existing URL-based resumption SHALL continue working
3. WHEN feature flags are set THEN behavior SHALL be controllable via environment variables
4. IF integration causes issues THEN system SHALL degrade gracefully to previous behavior