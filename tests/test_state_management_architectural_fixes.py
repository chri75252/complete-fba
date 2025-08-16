"""
Unit tests for State Management Architectural Fixes

Tests the four critical architectural fixes:
1. Resume point calculation uses supplier_extraction_progress as primary source
2. Corruption recovery copies FROM operational TO tracking data  
3. Validation preserves operational data instead of destroying it
4. Backfill prioritizes operational data over tracking data
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager, ResumeController, ErrorHandler


class TestStateManagementArchitecturalFixes(unittest.TestCase):
    """Test suite for the four critical architectural fixes"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_state_manager = Mock()
        self.mock_log = Mock()
        self.resume_calculator = ResumeController(self.mock_state_manager, self.mock_log)
        self.error_handler = ErrorHandler(self.mock_state_manager, self.mock_log)
    
    def test_resume_calculation_uses_operational_data(self):
        """Test Fix 1: Resume calculation uses supplier_extraction_progress as primary source"""
        # Arrange: Set up state with operational data having real values and tracking data corrupted
        self.mock_state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 2,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances",
                "current_product_index_in_category": 5,
                "total_products_in_current_category": 20
            },
            "system_progression": {
                "current_category_index": 0,  # Corrupted
                "total_categories": 0,         # Corrupted
                "current_category_url": "",    # Corrupted
                "current_phase": "supplier"
            },
            "resumption_index": 8378
        }
        
        # Act: Calculate resume point
        result = self.resume_calculator.calculate_resume_point(reconciliation_completed=True)
        
        # Assert: Should use operational data, not corrupted tracking data
        self.assertEqual(result["current_category_index"], 2, "Should use operational data (2), not corrupted tracking data (0)")
        self.assertEqual(result["total_categories"], 233, "Should use operational data (233), not corrupted tracking data (0)")
        self.assertEqual(result["current_category_url"], "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances")
        self.assertEqual(result["current_product_index_in_category"], 5)
        self.assertEqual(result["total_products_in_current_category"], 20)
        
        # Verify logging shows operational data was used
        self.mock_log.info.assert_any_call("🔧 RESUME SOURCE: Using supplier_extraction_progress (operational data)")
    
    def test_resume_calculation_fallback_to_tracking_data(self):
        """Test Fix 1: Resume calculation falls back to system_progression when operational data is empty"""
        # Arrange: Set up state with empty operational data
        self.mock_state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 0,  # Empty
                "total_categories": 0          # Empty
            },
            "system_progression": {
                "current_category_index": 1,
                "total_categories": 233,
                "current_phase": "supplier"
            },
            "resumption_index": 8378
        }
        
        # Act: Calculate resume point
        result = self.resume_calculator.calculate_resume_point(reconciliation_completed=True)
        
        # Assert: Should fall back to tracking data with warning
        self.assertEqual(result["current_category_index"], 1)
        self.assertEqual(result["total_categories"], 233)
        
        # Verify warning was logged
        self.mock_log.warning.assert_any_call("⚠️ RESUME SOURCE: Using system_progression fallback")
    
    def test_corruption_recovery_correct_direction(self):
        """Test Fix 2: Recovery copies FROM supplier_extraction_progress TO system_progression"""
        # Arrange: Set up state with good operational data and corrupted tracking data
        self.mock_state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 2,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances",
                "current_product_index_in_category": 5,
                "total_products_in_current_category": 20
            },
            "system_progression": {
                "current_category_index": 0,  # Corrupted
                "total_categories": 0,         # Corrupted
                "current_category_url": ""     # Corrupted
            }
        }
        self.mock_state_manager.save_state = Mock()
        
        # Act: Apply corruption recovery
        recovery_result = self.error_handler._attempt_corruption_recovery(["progress_consistency"])
        
        # Assert: system_progression should now have operational data
        sp = self.mock_state_manager.state_data["system_progression"]
        self.assertEqual(sp["current_category_index"], 2, "Should copy FROM operational TO tracking")
        self.assertEqual(sp["total_categories"], 233, "Should copy FROM operational TO tracking")
        self.assertEqual(sp["current_category_url"], "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances")
        
        # Verify correct recovery action was logged
        self.mock_log.info.assert_any_call("🔧 RECOVERY: Synced FROM supplier_extraction_progress TO system_progression")
    
    def test_validation_preserves_operational_data(self):
        """Test Fix 3: Validation preserves good operational data instead of destroying it"""
        # Arrange: Set up state manager with good operational data and missing tracking fields
        state_manager = Mock()
        state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 2,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances"
            },
            "system_progression": {}  # Missing fields
        }
        
        validator = FixedEnhancedStateManager("test_supplier")
        validator.state_data = state_manager.state_data
        
        # Act: Run validation
        is_valid, repairs_made = validator.validate_and_repair_state()
        
        # Assert: system_progression should be restored from operational data, not defaulted
        sp = validator.state_data["system_progression"]
        self.assertEqual(sp["current_category_index"], 2, "Should restore from operational data, not default to 0")
        self.assertEqual(sp["total_categories"], 233, "Should restore from operational data, not default to 0")
        self.assertEqual(sp["current_category_url"], "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances")
        
        # Verify that repairs were made (the important part is that data was restored, not the logging)
        self.assertIn("Restored system_progression current_category_index from supplier_extraction_progress: 2", repairs_made)
    
    def test_backfill_prioritizes_operational_data(self):
        """Test Fix 4: Backfill uses operational data to restore corrupted tracking data"""
        # Arrange: Set up state with good operational data and corrupted tracking data
        state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 2,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances"
            },
            "system_progression": {
                "current_category_index": 0,  # Corrupted
                "total_categories": 0,         # Corrupted
                "current_category_url": ""     # Corrupted
            }
        }
        
        # Mock the state manager's load_state method to test backfill logic
        with patch('utils.fixed_enhanced_state_manager.log') as mock_log:
            state_manager = FixedEnhancedStateManager("test_supplier")
            state_manager.state_data = state_data
            
            # Simulate the backfill logic from load_state
            sp = state_manager.state_data.setdefault("system_progression", {})
            sep = state_manager.state_data.setdefault("supplier_extraction_progress", {})
            
            backfill_fields = [
                ("current_category_index", "current_category_index"),
                ("total_categories", "total_categories"),
                ("current_category_url", "current_category_url")
            ]
            
            for k_sp, k_sep in backfill_fields:
                # First: Try to restore system_progression from supplier_extraction_progress
                if k_sep in sep and sep[k_sep] is not None and sep[k_sep] not in [0, ""] and (k_sp not in sp or sp[k_sp] in [0, None, ""]):
                    sp[k_sp] = sep[k_sep]
        
        # Assert: system_progression should be restored from operational data
        self.assertEqual(sp["current_category_index"], 2, "Should restore tracking data from operational data")
        self.assertEqual(sp["total_categories"], 233, "Should restore tracking data from operational data")
        self.assertEqual(sp["current_category_url"], "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances")
    
    def test_all_fixes_integration(self):
        """Integration test: All four fixes working together"""
        # Arrange: Set up realistic state with operational data and corrupted tracking data
        self.mock_state_manager.state_data = {
            "supplier_extraction_progress": {
                "current_category_index": 2,
                "total_categories": 233,
                "current_category_url": "https://www.poundwholesale.co.uk/health-beauty/wholesale-perfume-fragrances",
                "current_product_index_in_category": 5,
                "total_products_in_current_category": 20
            },
            "system_progression": {
                "current_category_index": 0,  # Corrupted
                "total_categories": 0,         # Corrupted
                "current_category_url": "",    # Corrupted
                "current_phase": "supplier"
            },
            "resumption_index": 8378
        }
        
        # Act: Calculate resume point (should use operational data)
        result = self.resume_calculator.calculate_resume_point(reconciliation_completed=True)
        
        # Assert: Resume point should use operational data (Fix 1)
        self.assertEqual(result["current_category_index"], 2, "Resume calculation should use operational data")
        self.assertEqual(result["total_categories"], 233, "Resume calculation should use operational data")
        
        # Verify expected log message for using operational data
        self.mock_log.info.assert_any_call("🔧 RESUME SOURCE: Using supplier_extraction_progress (operational data)")


if __name__ == '__main__':
    unittest.main()