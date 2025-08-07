# Testing Directory Organization

This directory contains all testing scripts and demonstration files for the Amazon FBA Agent System.

## Directory Structure

### `/processing_state_fixes/`
Tests and implementations related to processing state management fixes:
- `test_processing_state_fixes.py` - Comprehensive test suite for processing state fixes
- `implement_processing_state_fixes.py` - Implementation script for processing state fixes
- `test_file_grounded_state.py` - Tests for file-grounded state calculations

### `/demonstrations/`
Example and demonstration scripts:
- `demonstration_file_grounded_usage.py` - Demonstrates file-grounded state manager usage
- `example_fixed_state_usage.py` - Example usage of FixedEnhancedStateManager

### `/integration_fixes/`
Tests for various system integration fixes:
- `test_gap_fix_simple.py` - Gap processing fixes
- `test_linking_map_fix.py` - Linking map fixes  
- `test_linking_map_windows_fix.py` - Windows-specific linking map fixes
- `test_no_match_*.py` - No-match scenario handling tests
- `test_cache_fixes.py` - Cache management fixes
- `test_hash_optimization_system.py` - Hash optimization tests
- `test_sentinel_effectiveness.py` - Sentinel monitoring tests
- `test_windows_file_operations.py` - Windows file operation tests
- `final_verification_test.py` - Final system verification

### `/multi_toggle_analysis/`
Comprehensive multi-agent testing framework for configuration toggles and system analysis.

## Running Tests

From the project root directory:

```bash
# Run all tests
python -m pytest testing/ -v

# Run specific test category
python -m pytest testing/processing_state_fixes/ -v
python -m pytest testing/integration_fixes/ -v

# Run individual test files
python testing/processing_state_fixes/test_processing_state_fixes.py
```

## Test Organization Principles

1. **Separation by Purpose**: Tests are organized by the type of functionality they test
2. **Clear Naming**: All test files follow the `test_*.py` convention
3. **Demonstrations**: Example scripts are kept separate from actual tests
4. **Integration Focus**: Most tests verify integration between components rather than unit tests
5. **System Verification**: Final verification tests ensure end-to-end functionality

## Recent Moves (2025-07-31)

All testing scripts were moved from the root directory to this organized structure to maintain a clean project root while preserving comprehensive testing capabilities.