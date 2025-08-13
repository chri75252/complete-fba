# Unified State Management Guide

## Overview

The Unified State Management system provides a comprehensive solution for maintaining consistent state across the FBA extraction workflow. It addresses critical issues with state drift, resume failures, and inconsistent progress tracking through atomic operations and unified progression updates.

## Key Features

- **Atomic State Operations**: All state changes use atomic file operations
- **Unified Progress Tracking**: Single source of truth for all progress data
- **Resume Reliability**: 100% reliable resume functionality with validation
- **Data Integrity**: Comprehensive validation and corruption detection
- **Error Recovery**: Automatic repair of common state inconsistencies

## Architecture

```
Unified State Management Architecture
├── FixedEnhancedStateManager
│   ├── Unified progression updates
│   ├── Atomic save operations
│   ├── State regression protection
│   └── Category accumulator resets
├── Data Integrity Guardian
│   ├── Startup reconciliation
│   ├── Linking map hydration
│   └── Corruption detection
├── Resume Controller
│   ├── Resume point validation
│   ├── Safe fallback mechanisms
│   └── Prerequisite checking
└── Error Handler
    ├── Invariant failure handling
    ├── State corruption repair
    └── Diagnostic capabilities
```

## Core Components

### FixedEnhancedStateManager

The main state management class that provides unified tracking and atomic operations.

```python
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

# Initialize state manager
state_manager = FixedEnhancedStateManager("supplier_name")

# Update progression atomically
state_manager.update_progression_unified(
    category_index=5,
    total_categories=25,
    product_index=10,
    total_products_in_category=100,
    current_phase="supplier"
)

# Save state atomically
success = state_manager.save_state_atomic()
```

### Data Integrity Guardian

Ensures data consistency through startup reconciliation and corruption detection.

```python
from utils.fixed_enhanced_state_manager import DataIntegrityGuardian

# Initialize guardian
guardian = DataIntegrityGuardian(state_manager, logger)

# Perform startup reconciliation
success, reconciled_items = guardian.reconcile_on_startup_prereq(
    linking_map, cached_products
)

# Detect corruption
corruption_issues = guardian.detect_state_corruption()
```

### Resume Controller

Provides intelligent resume point calculation with validation and safe fallbacks.

```python
from utils.fixed_enhanced_state_manager import ResumeController

# Initialize controller
resume_controller = ResumeController(state_manager, logger)

# Calculate resume point
resume_point = resume_controller.calculate_resume_point(
    reconciliation_completed=True
)

# Validate resume point
is_valid = resume_controller.validate_resume_point(resume_point)
```

## State Structure

### Enhanced State Schema

```json
{
  "schema_version": "2.0_UNIFIED",
  "created_at": "2025-08-13T10:00:00Z",
  "last_updated": "2025-08-13T10:30:00Z",
  
  "system_progression": {
    "current_category_index": 5,
    "total_categories": 25,
    "current_product_index_in_category": 10,
    "total_products_in_current_category": 100,
    "current_phase": "supplier",
    "current_category_url": "https://example.com/category",
    "phase_start_time": "2025-08-13T10:25:00Z"
  },
  
  "supplier_extraction_progress": {
    "current_category_index": 5,
    "last_processed_index": 10,
    "progress_index": 10
  },
  
  "global_counters": {
    "total_products_discovered": 2500,
    "total_products_processed": 1250,
    "total_categories_completed": 4
  },
  
  "integrity_status": {
    "last_reconciliation": "2025-08-13T10:00:00Z",
    "items_reconciled": 15,
    "consistency_score": 1.0
  }
}
```

## Usage Patterns

### Basic State Management

```python
# Initialize and load existing state
state_manager = FixedEnhancedStateManager("poundwholesale")
state_loaded = state_manager.load_state()

# Update progression during processing
state_manager.update_progression_unified(
    category_index=current_category,
    total_categories=len(categories),
    product_index=current_product,
    total_products_in_category=category_total,
    current_phase="supplier",
    category_url=category_url
)

# Reset accumulators between categories
state_manager.reset_category_accumulators(current_category)

# Save state atomically
state_manager.save_state_atomic()
```

### Startup Sequence

```python
from utils.fixed_enhanced_state_manager import StartupOrchestrator

# Execute complete startup sequence
orchestrator = StartupOrchestrator(state_manager, logger)
startup_result = orchestrator.execute_startup_sequence(
    linking_map=linking_map,
    cached_products=cached_products,
    category_urls=category_urls
)

if startup_result['success']:
    resume_point = startup_result['resume_point']
    reconciled_count = startup_result['reconciled_items']
else:
    # Handle startup failure
    logger.error(f"Startup failed: {startup_result['error']}")
```

### Error Handling

```python
from utils.fixed_enhanced_state_manager import ErrorHandler

# Initialize error handler
error_handler = ErrorHandler(state_manager, logger)

# Handle filter invariant failures
try:
    filtered_result = filter_urls(urls, linking_map, cached_products)
    if not filtered_result.get('invariant_check', False):
        recovery_result = error_handler.handle_invariant_failure(
            filtered_result, category_id
        )
        if recovery_result['repaired']:
            filtered_result = recovery_result['repaired_filter']
except Exception as e:
    # Create diagnostic snapshot
    error_handler.create_diagnostic_snapshot('filter_error', {
        'error': str(e),
        'category_id': category_id,
        'urls_count': len(urls)
    })
```

## Configuration

### Environment Variables

```bash
# State management
ALLOW_STATE_REGRESSION=0      # Prevent backwards progress
STATE_STRICT_MODE=1           # Enable strict validation
STATE_BACKUP_COUNT=5          # Number of backups to keep

# Error handling
AUTO_REPAIR_ENABLED=1         # Enable automatic repair
DIAGNOSTIC_SNAPSHOTS=1        # Create diagnostic snapshots
GRACEFUL_DEGRADATION=1        # Enable graceful error handling

# Performance
RECONCILIATION_BATCH_SIZE=100 # Batch size for reconciliation
ATOMIC_SAVE_TIMEOUT=30        # Timeout for atomic saves
```

### System Configuration

```json
{
  "state_management": {
    "atomic_saves": true,
    "backup_rotation": 5,
    "reconciliation_on_startup": true,
    "invariant_enforcement": true,
    "regression_protection": true
  },
  "error_handling": {
    "auto_repair_enabled": true,
    "diagnostic_snapshots": true,
    "graceful_degradation": true,
    "max_repair_attempts": 3
  },
  "performance": {
    "reconciliation_batch_size": 100,
    "atomic_save_timeout": 30,
    "validation_level": "strict"
  }
}
```

## Monitoring and Diagnostics

### Key Metrics

Monitor these metrics to ensure state management health:

```bash
# State consistency score (should be 1.0)
jq '.integrity_status.consistency_score' OUTPUTS/CACHE/processing_states/*.json

# Reconciliation items (items repaired on startup)
jq '.integrity_status.items_reconciled' OUTPUTS/CACHE/processing_states/*.json

# Resume success rate (should be 100%)
grep "RESUME SUCCESS" logs/state_management/*.log | wc -l

# Filter invariant compliance (should be 100%)
grep "INVARIANT PASS" logs/debug/*.log | wc -l
```

### Log Monitoring

```bash
# Monitor state management operations
tail -f logs/state_management/unified_state_*.log

# Check startup reconciliation
grep "RECONCILED" logs/debug/*.log

# Monitor error recovery
grep "REPAIRED" logs/error_recovery/*.log

# Check atomic operations
grep "ATOMIC SAVE" logs/debug/*.log
```

### Diagnostic Outputs

The system creates diagnostic outputs in `OUTPUTS/DIAGNOSTICS/`:

```
OUTPUTS/DIAGNOSTICS/
├── state_corruption/           # State corruption diagnostics
├── filter_failures/           # Filter invariant failure snapshots
├── reconciliation_reports/    # Startup reconciliation details
└── error_recovery/           # Error recovery diagnostics
```

## Troubleshooting

### Common Issues

#### State Regression Detected

```bash
# Check regression details
grep "STATE REGRESSION" logs/debug/*.log

# Temporarily allow regression for recovery
export ALLOW_STATE_REGRESSION=1

# Validate current state
python -c "
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
mgr = FixedEnhancedStateManager('test')
is_valid, issues = mgr.validate_state()
print(f'Valid: {is_valid}, Issues: {issues}')
"
```

#### Resume Point Validation Failures

```bash
# Check resume validation logs
grep "RESUME VALIDATION" logs/debug/*.log

# Test resume point calculation
python -c "
from utils.fixed_enhanced_state_manager import ResumeController
rc = ResumeController()
resume_point = rc.calculate_resume_point()
is_valid = rc.validate_resume_point(resume_point)
print(f'Resume point valid: {is_valid}')
"
```

#### Filter Invariant Failures

```bash
# Check invariant compliance
grep "INVARIANT FAIL" logs/debug/*.log

# Review diagnostic snapshots
ls -la OUTPUTS/DIAGNOSTICS/filter_failures/

# Enable automatic repair
export AUTO_REPAIR_ENABLED=1
```

#### Startup Reconciliation Issues

```bash
# Check reconciliation logs
grep "RECONCILIATION" logs/debug/*.log

# Review reconciliation reports
cat OUTPUTS/DIAGNOSTICS/reconciliation_reports/latest.json

# Test reconciliation manually
python -c "
from utils.fixed_enhanced_state_manager import DataIntegrityGuardian
guardian = DataIntegrityGuardian()
success, items = guardian.reconcile_on_startup_prereq([], [])
print(f'Success: {success}, Items: {len(items)}')
"
```

## Best Practices

### State Management

1. **Always use atomic operations** for state changes
2. **Reset accumulators** between categories
3. **Validate state** before critical operations
4. **Monitor consistency scores** regularly
5. **Enable regression protection** in production

### Error Handling

1. **Enable automatic repair** for common issues
2. **Create diagnostic snapshots** for debugging
3. **Monitor error recovery** success rates
4. **Review error logs** regularly
5. **Test recovery procedures** periodically

### Performance

1. **Use appropriate batch sizes** for reconciliation
2. **Monitor atomic save performance**
3. **Optimize validation frequency**
4. **Clean up old diagnostic files**
5. **Monitor memory usage** during operations

## Migration Guide

### From Legacy State Manager

1. **Update imports**:
   ```python
   # Old
   from utils.enhanced_state_manager import EnhancedStateManager
   
   # New
   from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
   ```

2. **Update method calls**:
   ```python
   # Old
   state_manager.save_state()
   
   # New
   state_manager.update_progression_unified(**kwargs)
   state_manager.save_state_atomic()
   ```

3. **Add accumulator resets**:
   ```python
   # Add between categories
   state_manager.reset_category_accumulators(category_index)
   ```

4. **Update startup sequence**:
   ```python
   # Add startup orchestration
   orchestrator = StartupOrchestrator(state_manager, logger)
   startup_result = orchestrator.execute_startup_sequence(...)
   ```

### Backward Compatibility

The system maintains backward compatibility with:
- Legacy state file formats
- Existing field names
- Previous API methods (with deprecation warnings)
- Old configuration options

## Testing

### Unit Tests

```python
# Test unified state updates
python tests/unit/test_unified_state_manager.py

# Test data integrity
python tests/unit/test_data_integrity_guardian.py

# Test resume controller
python tests/unit/test_resume_controller.py

# Test error handling
python tests/unit/test_error_handler.py
```

### Integration Tests

```python
# Test complete workflow
python tests/integration/test_state_management_workflow.py

# Test resume functionality
python tests/integration/test_resume_functionality.py

# Test error recovery
python tests/integration/test_error_recovery.py
```

### Performance Tests

```python
# Test large state files
python tests/performance/test_large_state_performance.py

# Test reconciliation performance
python tests/performance/test_reconciliation_performance.py
```

## Conclusion

The Unified State Management system provides:

1. **Reliability**: 100% reliable resume functionality
2. **Consistency**: Eliminates state drift and inconsistencies
3. **Recovery**: Automatic error detection and repair
4. **Performance**: Optimized for large-scale operations
5. **Monitoring**: Comprehensive diagnostics and logging

This system forms the foundation for robust, production-ready FBA extraction operations with guaranteed data integrity and reliable resume capabilities.