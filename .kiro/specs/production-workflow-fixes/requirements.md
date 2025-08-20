# Requirements Document - Production Workflow Fixes

## Introduction

This specification addresses critical production failures in the Amazon FBA Agent System where cached product processing bypasses manifest population, causing universal Amazon processing failures and broken resume functionality. The system currently has working components that are isolated from production execution paths, creating a "testing theater" scenario where 154 tests pass but production consistently fails.

## Requirements

### Requirement 1: Cached Product Manifest Population

**User Story:** As a system operator, I want cached products to populate category manifests correctly, so that Amazon processing runs instead of being universally skipped.

#### Acceptance Criteria

1. WHEN cached products are loaded from configurable_supplier_scraper.py THEN category_manifests SHALL be populated with product URLs
2. WHEN manifest population occurs via cached path THEN the same data structure SHALL be created as fresh extraction path
3. WHEN manifests are populated THEN log entries SHALL show "MANIFEST: [1-9]+ URLs" instead of "MANIFEST: 0 URLs"
4. WHEN Amazon processing phase begins THEN it SHALL NOT be skipped due to empty manifests

### Requirement 2: Resume Functionality Restoration

**User Story:** As a system operator, I want the system to resume from actual progress instead of always restarting from category 0, so that processing continues efficiently from where it left off.

#### Acceptance Criteria

1. WHEN system restarts with existing progress THEN resumption_index SHALL reflect actual completed categories
2. WHEN reverse gap is detected (linking_map > cache) THEN system SHALL NOT automatically reset to index 0
3. WHEN resume point is calculated THEN it SHALL use category completion data instead of flawed reverse gap logic
4. WHEN system logs resume decision THEN it SHALL show "START_AT_INDEX=[1-9]+" for systems with progress

### Requirement 3: Amazon Processing Logic Correction

**User Story:** As a system operator, I want Amazon processing to run for products that are already in the linking map, so that Amazon data can be refreshed and analysis completed.

#### Acceptance Criteria

1. WHEN URL filter classifies all URLs as "skip_entirely" THEN Amazon processing SHALL still occur for linking map items
2. WHEN category_analysis_products is empty due to filter results THEN system SHALL check for linking map products to process
3. WHEN linking map products exist for a category THEN they SHALL be processed through Amazon analysis workflow
4. WHEN Amazon processing completes THEN log SHALL show "Processing X linking map products" instead of "Amazon skipped"

### Requirement 4: Enhanced Components Integration

**User Story:** As a system developer, I want the enhanced state components to be used in production workflow, so that atomic operations and invariant validation provide the intended reliability improvements.

#### Acceptance Criteria

1. WHEN production workflow initializes THEN it SHALL import and instantiate enhanced state components
2. WHEN state updates occur THEN they SHALL use AtomicStateUpdater for critical operations
3. WHEN state is saved THEN InvariantValidator SHALL validate consistency before persistence
4. WHEN invariant violations are detected THEN auto-repair mechanisms SHALL attempt correction

### Requirement 5: Dual Path Architecture Unification

**User Story:** As a system architect, I want both fresh extraction and cached product loading to use the same manifest population logic, so that behavior is consistent regardless of data source.

#### Acceptance Criteria

1. WHEN fresh products are extracted THEN manifest population SHALL occur via existing P0 fix
2. WHEN cached products are loaded THEN manifest population SHALL occur via callback mechanism
3. WHEN either path completes THEN the resulting category_manifests structure SHALL be identical
4. WHEN workflow processes manifests THEN it SHALL handle both data sources transparently

### Requirement 6: Filter Logic Enhancement

**User Story:** As a system operator, I want the URL filter to properly classify linking map items for Amazon processing, so that already-processed products can still receive Amazon analysis updates.

#### Acceptance Criteria

1. WHEN URLs are classified by filter THEN linking map items SHALL be tracked separately from skip_entirely
2. WHEN filter results are processed THEN workflow SHALL have access to linking_map_items category
3. WHEN invariant validation runs THEN it SHALL account for all classification categories
4. WHEN filter diagnostics are needed THEN detailed breakdown SHALL be available for troubleshooting

### Requirement 7: Production Monitoring and Verification

**User Story:** As a system operator, I want comprehensive logging and monitoring to verify that fixes are working correctly in production, so that failures can be quickly identified and resolved.

#### Acceptance Criteria

1. WHEN manifest population occurs THEN logs SHALL clearly indicate source (fresh vs cached) and URL count
2. WHEN resume logic executes THEN logs SHALL show decision reasoning and calculated resume point
3. WHEN Amazon processing runs THEN logs SHALL indicate product source (fresh, cached, linking map)
4. WHEN enhanced components are used THEN logs SHALL confirm atomic operations and invariant validation