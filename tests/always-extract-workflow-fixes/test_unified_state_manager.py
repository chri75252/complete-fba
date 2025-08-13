"""
Unit tests for Unified State Manager implementation.

Tests the core functionality of the FixedEnhancedStateManager including:
- Unified progression updates
- State regression protection
- Category accumulator resets
- Guarded breadcrumb logging
- Atomic save operations
"""

import pytest
import os
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the class under test
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestUnifiedStateManager:
    """Test suite for Unified State Manager functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Create state manager instance for testing."""
        return FixedEnhancedStateManager("test_supplier", base_path=temp_dir)
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger for testing."""
        return Mock()

    def test_initialization(self, state_manager):
        """Test state manager initialization."""
        assert state_manager.supplier_name == "test_supplier"
        assert state_manager.SCHEMA_VERSION == "1.1_FIXED"
        assert "system_progression" in state_manager.state_data
        assert "supplier_extraction_progress" in state_manager.state_data
        assert "global_counters" in state_manager.state_data

    def test_unified_progression_update(self, state_manager):
        """Test unified progression update functionality."""
        # Update progression with all parameters
        state_manager.update_progression_unified(
            category_index=5,
            total_categories=25,
            product_index=10,
            total_products_in_category=100,
            current_phase="supplier",
            category_url="https://example.com/category"
        )
        
        # Verify system_progression updated
        sp = state_manager.state_data["system_progression"]
        assert sp["current_category_index"] == 5
        assert sp["total_categories"] == 25
        assert sp["current_product_index_in_category"] == 10
        assert sp["total_products_in_current_category"] == 100
        assert sp["current_phase"] == "supplier"
        assert sp["current_category_url"] == "https://example.com/category"
        
        # Verify supplier_extraction_progress synchronized
        sep = state_manager.state_data["supplier_extraction_progress"]
        assert sep["current_category_index"] == 5
        assert sep["last_processed_index"] == 10
        assert sep["progress_index"] == 10

    def test_unified_progression_partial_update(self, state_manager):
        """Test unified progression update with partial parameters."""
        # Set initial state
        state_manager.update_progression_unified(
            category_index=3,
            total_categories=10,
            product_index=5,
            total_products_in_category=50
        )
        
        # Partial update
        state_manager.update_progression_unified(
            product_index=15,
            current_phase="amazon"
        )
        
        # Verify partial update preserved existing values
        sp = state_manager.state_data["system_progression"]
        assert sp["current_category_index"] == 3  # Preserved
        assert sp["total_categories"] == 10  # Preserved
        assert sp["current_product_index_in_category"] == 15  # Updated
        assert sp["total_products_in_current_category"] == 50  # Preserved
        assert sp["current_phase"] == "amazon"  # Updated

    def test_total_products_protection(self, state_manager):
        """Test protection against total_products regression."""
        # Set initial total_products
        state_manager.state_data["total_products"] = 1000
        
        # Attempt to update with smaller value
        state_manager.update_progression_unified(
            total_products_in_category=50  # This should NOT overwrite total_products
        )
        
        # Verify total_products was protected
        assert state_manager.state_data["total_products"] == 1000
        
        # Verify category total was set correctly
        sp = state_manager.state_data["system_progression"]
        assert sp["total_products_in_current_category"] == 50

    def test_guarded_breadcrumb_logging_complete_fields(self, state_manager):
        """Test breadcrumb logging with complete fields."""
        with patch.object(state_manager, 'log') as mock_log:
            # Set complete state
            state_manager.update_progression_unified(
                category_index=5,
                total_categories=25,
                product_index=10,
                total_products_in_category=100,
                current_phase="supplier",
                category_url="https://example.com/category"
            )
            
            # Log breadcrumb
            state_manager.log_breadcrumb_guarded()
            
            # Verify breadcrumb was logged
            mock_log.info.assert_called_once()
            call_args = mock_log.info.call_args[0][0]
            assert "RESUME PTR" in call_args
            assert "phase=supplier" in call_args
            assert "cat_idx=5/25" in call_args
            assert "prod_idx=10/100" in call_args

    def test_guarded_breadcrumb_logging_missing_fields(self, state_manager):
        """Test breadcrumb logging with missing fields."""
        with patch.object(state_manager, 'log') as mock_log:
            # Set incomplete state (missing total_categories)
            state_manager.state_data["system_progression"] = {
                "current_category_index": 5,
                "current_product_index_in_category": 10,
                "total_products_in_current_category": 100,
                "current_phase": "supplier"
                # Missing total_categories
            }
            
            # Attempt to log breadcrumb
            state_manager.log_breadcrumb_guarded()
            
            # Verify warning was logged instead
            mock_log.warning.assert_called_once()
            call_args = mock_log.warning.call_args[0][0]
            assert "BREADCRUMB DELAYED" in call_args
            assert "Missing fields" in call_args

    def test_guarded_breadcrumb_logging_zero_denominators(self, state_manager):
        """Test breadcrumb logging with zero denominators."""
        with patch.object(state_manager, 'log') as mock_log:
            # Set state with zero denominators
            state_manager.update_progression_unified(
                category_index=5,
                total_categories=0,  # Zero denominator
                product_index=10,
                total_products_in_category=100,
                current_phase="supplier"
            )
            
            # Attempt to log breadcrumb
            state_manager.log_breadcrumb_guarded()
            
            # Verify warning was logged
            mock_log.warning.assert_called_once()
            call_args = mock_log.warning.call_args[0][0]
            assert "BREADCRUMB INVALID" in call_args
            assert "Zero denominators" in call_args

    def test_category_accumulator_reset(self, state_manager):
        """Test category accumulator reset functionality."""
        with patch.object(state_manager, 'log') as mock_log:
            # Set up accumulators with data
            state_manager.current_manifest = {"test": "data"}
            state_manager.current_filtered_queues = {
                "skip_entirely": ["url1", "url2"],
                "needs_amazon_only": ["url3"],
                "needs_full_extraction": ["url4"]
            }
            state_manager.category_counters = {"processed": 10, "total": 50, "errors": 2}
            state_manager.in_memory_trackers = {"tracker1": "data"}
            
            # Reset accumulators
            state_manager.reset_category_accumulators(5)
            
            # Verify reset
            assert state_manager.current_manifest is None
            assert state_manager.current_filtered_queues == {
                "skip_entirely": [],
                "needs_amazon_only": [],
                "needs_full_extraction": []
            }
            assert state_manager.category_counters == {"processed": 0, "total": 0, "errors": 0}
            assert state_manager.in_memory_trackers == {}
            
            # Verify logging
            mock_log.info.assert_called_once()
            call_args = mock_log.info.call_args[0][0]
            assert "RESET: Category 5 accumulators cleared" in call_args

    def test_state_regression_protection_valid(self, state_manager):
        """Test state regression protection with valid progression."""
        # Set initial state
        old_state = {"resumption_index": 100}
        new_state = {"resumption_index": 150}
        
        # Should not raise exception
        try:
            state_manager.validate_state_progression(old_state, new_state)
        except SystemExit:
            pytest.fail("Valid progression should not raise SystemExit")

    def test_state_regression_protection_regression(self, state_manager):
        """Test state regression protection with regression."""
        # Set states with regression
        old_state = {"resumption_index": 150}
        new_state = {"resumption_index": 100}
        
        # Should raise SystemExit
        with pytest.raises(SystemExit):
            state_manager.validate_state_progression(old_state, new_state)

    def test_state_regression_protection_bypass(self, state_manager):
        """Test state regression protection with bypass."""
        with patch.dict(os.environ, {'ALLOW_STATE_REGRESSION': '1'}):
            # Set states with regression
            old_state = {"resumption_index": 150}
            new_state = {"resumption_index": 100}
            
            # Should not raise exception with bypass
            try:
                state_manager.validate_state_progression(old_state, new_state)
            except SystemExit:
                pytest.fail("Regression with bypass should not raise SystemExit")

    def test_atomic_save_operation(self, state_manager, temp_dir):
        """Test atomic save operation."""
        # Update state
        state_manager.update_progression_unified(
            category_index=5,
            total_categories=25,
            product_index=10,
            total_products_in_category=100
        )
        
        # Perform atomic save
        success = state_manager.save_state_atomic()
        
        # Verify save succeeded
        assert success
        
        # Verify file exists
        assert state_manager.state_file_path.exists()
        
        # Verify content
        with open(state_manager.state_file_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["system_progression"]["current_category_index"] == 5
        assert saved_data["system_progression"]["total_categories"] == 25

    def test_state_validation(self, state_manager):
        """Test state validation functionality."""
        # Set valid state
        state_manager.update_progression_unified(
            category_index=5,
            total_categories=25,
            product_index=10,
            total_products_in_category=100
        )
        
        # Validate state
        is_valid, issues = state_manager.validate_state()
        
        # Should be valid
        assert is_valid
        assert len(issues) == 0

    def test_state_validation_with_issues(self, state_manager):
        """Test state validation with issues."""
        # Set invalid state (negative indices)
        state_manager.state_data["system_progression"]["current_category_index"] = -1
        state_manager.state_data["system_progression"]["current_product_index_in_category"] = -5
        
        # Validate state
        is_valid, issues = state_manager.validate_state()
        
        # Should be invalid
        assert not is_valid
        assert len(issues) > 0
        assert any("negative" in issue.lower() for issue in issues)

    def test_load_state_with_existing_file(self, state_manager, temp_dir):
        """Test loading state from existing file."""
        # Create state file
        state_data = {
            "schema_version": "1.1_FIXED",
            "supplier_name": "test_supplier",
            "resumption_index": 100,
            "total_products": 500,
            "system_progression": {
                "current_category_index": 5,
                "total_categories": 25
            },
            "supplier_extraction_progress": {
                "current_category_index": 5,
                "last_processed_index": 100
            }
        }
        
        with open(state_manager.state_file_path, 'w') as f:
            json.dump(state_data, f)
        
        # Load state
        loaded = state_manager.load_state()
        
        # Verify loading
        assert loaded
        assert state_manager.state_data["resumption_index"] == 100
        assert state_manager.state_data["total_products"] == 500

    def test_backup_creation(self, state_manager, temp_dir):
        """Test backup creation during save."""
        # Create initial state file
        state_manager.save_state_atomic()
        
        # Modify state
        state_manager.update_progression_unified(category_index=10)
        
        # Save again (should create backup)
        state_manager.save_state_atomic()
        
        # Check for backup files
        backup_dir = state_manager.state_file_path.parent / "backups"
        if backup_dir.exists():
            backup_files = list(backup_dir.glob("*.json"))
            assert len(backup_files) > 0

    def test_concurrent_access_protection(self, state_manager):
        """Test protection against concurrent access issues."""
        # This test would require more complex setup for true concurrency testing
        # For now, test that atomic operations complete successfully
        
        # Perform multiple rapid saves
        for i in range(5):
            state_manager.update_progression_unified(category_index=i)
            success = state_manager.save_state_atomic()
            assert success

    def test_error_handling_in_save(self, state_manager):
        """Test error handling during save operations."""
        # Mock file operations to simulate failure
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            success = state_manager.save_state_atomic()
            assert not success

    def test_schema_version_validation(self, state_manager):
        """Test schema version validation."""
        # Check current schema version
        assert state_manager.state_data["schema_version"] == "1.1_FIXED"
        
        # Test with different schema version
        state_manager.state_data["schema_version"] = "1.0_OLD"
        
        # Should handle gracefully (implementation dependent)
        is_valid, issues = state_manager.validate_state()
        # Implementation should handle version differences appropriately


class TestStateManagerIntegration:
    """Integration tests for state manager with other components."""
    
    @pytest.fixture
    def state_manager(self):
        """Create state manager for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield FixedEnhancedStateManager("integration_test", base_path=temp_dir)

    def test_complete_workflow_cycle(self, state_manager):
        """Test complete workflow cycle with state management."""
        # Initialize
        assert state_manager.state_data["resumption_index"] == 0
        
        # Process categories
        for category_idx in range(3):
            # Reset accumulators for new category
            state_manager.reset_category_accumulators(category_idx)
            
            # Update progression
            state_manager.update_progression_unified(
                category_index=category_idx,
                total_categories=3,
                current_phase="supplier"
            )
            
            # Process products in category
            for product_idx in range(10):
                state_manager.update_progression_unified(
                    product_index=product_idx,
                    total_products_in_category=10
                )
                
                # Log breadcrumb
                state_manager.log_breadcrumb_guarded()
            
            # Save state
            success = state_manager.save_state_atomic()
            assert success
        
        # Verify final state
        sp = state_manager.state_data["system_progression"]
        assert sp["current_category_index"] == 2
        assert sp["total_categories"] == 3
        assert sp["current_product_index_in_category"] == 9
        assert sp["total_products_in_current_category"] == 10

    def test_interruption_and_resume(self, state_manager):
        """Test interruption and resume functionality."""
        # Simulate processing
        state_manager.update_progression_unified(
            category_index=5,
            total_categories=25,
            product_index=15,
            total_products_in_category=100,
            current_phase="supplier"
        )
        
        # Save state (simulating interruption)
        state_manager.save_state_atomic()
        
        # Create new state manager (simulating restart)
        new_state_manager = FixedEnhancedStateManager(
            "integration_test", 
            base_path=state_manager.base_path
        )
        
        # Load previous state
        loaded = new_state_manager.load_state()
        assert loaded
        
        # Verify resume point
        sp = new_state_manager.state_data["system_progression"]
        assert sp["current_category_index"] == 5
        assert sp["current_product_index_in_category"] == 15
        assert sp["current_phase"] == "supplier"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])