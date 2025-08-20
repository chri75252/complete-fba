"""
Comprehensive Tests for InvariantValidator and AutoRepairEngine
============================================================

This module tests the critical invariant validation and auto-repair functionality
that prevents state corruption in production operations.
"""

import unittest
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.enhanced_state_components import InvariantValidator, AutoRepairEngine, ValidationResult, RepairResult
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestInvariantValidator(unittest.TestCase):
    """Test InvariantValidator functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.validator = InvariantValidator(self.state_manager)
        
        # Set up test data
        self._setup_consistent_state()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_consistent_state(self):
        """Set up consistent state for testing"""
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 100
        
        # Set up consistent cross-section data
        self.state_manager.state_data['supplier_extraction_progress']['current_category_url'] = "https://test.com/cat1"
        self.state_manager.state_data['supplier_extraction_progress']['current_category_index'] = 5
        
        self.state_manager.state_data['system_progression'] = {
            'current_category_url': "https://test.com/cat1",
            'current_category_index': 5
        }
    
    def test_validate_product_count_consistency_valid(self):
        """Test product count validation with consistent data"""
        result = self.validator.validate_product_count_consistency()
        
        self.assertIsInstance(result, ValidationResult)
        self.assertEqual(result.invariant_name, "product_count_consistency")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.severity, "low")
        self.assertTrue(result.auto_repairable)
        self.assertIsNone(result.repair_action)
    
    def test_validate_product_count_consistency_invalid(self):
        """Test product count validation with inconsistent data"""
        # Create inconsistency
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 150
        
        result = self.validator.validate_product_count_consistency()
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.severity, "critical")  # 50 difference is critical severity (>10)
        self.assertTrue(result.auto_repairable)
        self.assertEqual(result.repair_action, "synchronize_product_counts")
        self.assertIn("100", result.details)
        self.assertIn("150", result.details)
    
    def test_validate_product_count_consistency_critical(self):
        """Test product count validation with critical inconsistency"""
        # Create large inconsistency
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 200  # >10 difference = critical
        
        result = self.validator.validate_product_count_consistency()
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.severity, "critical")
        self.assertTrue(result.auto_repairable)
        self.assertEqual(result.repair_action, "synchronize_product_counts")
    
    def test_validate_cross_section_consistency_valid(self):
        """Test cross-section validation with consistent data"""
        result = self.validator.validate_cross_section_consistency()
        
        self.assertTrue(result.is_valid)
        self.assertEqual(result.severity, "low")
        self.assertTrue(result.auto_repairable)
        self.assertIsNone(result.repair_action)
        self.assertEqual(result.current_values["inconsistencies"], [])
    
    def test_validate_cross_section_consistency_invalid(self):
        """Test cross-section validation with inconsistent data"""
        # Create inconsistency
        self.state_manager.state_data['system_progression']['current_category_url'] = "https://test.com/different"
        self.state_manager.state_data['system_progression']['current_category_index'] = 10
        
        result = self.validator.validate_cross_section_consistency()
        
        self.assertFalse(result.is_valid)
        self.assertEqual(result.severity, "medium")
        self.assertTrue(result.auto_repairable)
        self.assertEqual(result.repair_action, "synchronize_sections")
        
        inconsistencies = result.current_values["inconsistencies"]
        self.assertEqual(len(inconsistencies), 2)  # URL and index inconsistencies
    
    def test_validate_all_invariants(self):
        """Test validation of all invariants"""
        results = self.validator.validate_all_invariants()
        
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 2)  # At least product count and cross-section
        
        # All should be valid with consistent state
        for result in results:
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.is_valid)
    
    def test_validate_all_invariants_with_violations(self):
        """Test validation with multiple violations"""
        # Create multiple inconsistencies
        self.state_manager.state_data['successful_products'] = 200  # Product count inconsistency
        self.state_manager.state_data['system_progression']['current_category_index'] = 10  # Cross-section inconsistency
        
        results = self.validator.validate_all_invariants()
        
        violations = [r for r in results if not r.is_valid]
        self.assertEqual(len(violations), 2)  # Both invariants should be violated


class TestAutoRepairEngine(unittest.TestCase):
    """Test AutoRepairEngine functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.repair_engine = AutoRepairEngine(self.state_manager)
        self.validator = InvariantValidator(self.state_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_repair_product_count_inconsistency(self):
        """Test repair of product count inconsistency"""
        # Set up inconsistent state
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 150
        
        # Create violation
        violation = self.validator.validate_product_count_consistency()
        self.assertFalse(violation.is_valid)
        
        # Apply repair
        repair_result = self.repair_engine.repair_product_count_inconsistency(violation)
        
        self.assertTrue(repair_result.success)
        self.assertEqual(len(repair_result.repairs_applied), 2)
        self.assertEqual(len(repair_result.errors), 0)
        
        # Check that both values are now synchronized to the higher value
        self.assertEqual(self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'], 150)
        self.assertEqual(self.state_manager.state_data['successful_products'], 150)
        
        # Verify repair worked
        post_repair_validation = self.validator.validate_product_count_consistency()
        self.assertTrue(post_repair_validation.is_valid)
    
    def test_repair_cross_section_inconsistency(self):
        """Test repair of cross-section inconsistency"""
        # Set up inconsistent state
        self.state_manager.state_data['supplier_extraction_progress']['current_category_url'] = "https://test.com/source"
        self.state_manager.state_data['supplier_extraction_progress']['current_category_index'] = 5
        self.state_manager.state_data['supplier_extraction_progress']['total_categories'] = 10
        
        self.state_manager.state_data['system_progression'] = {
            'current_category_url': "https://test.com/different",
            'current_category_index': 3,
            'total_categories': 8
        }
        
        # Create violation
        violation = self.validator.validate_cross_section_consistency()
        self.assertFalse(violation.is_valid)
        
        # Apply repair
        repair_result = self.repair_engine.repair_cross_section_inconsistency(violation)
        
        self.assertTrue(repair_result.success)
        self.assertGreater(len(repair_result.repairs_applied), 0)
        
        # Check that system_progression was synchronized from supplier_extraction_progress
        sp = self.state_manager.state_data['system_progression']
        self.assertEqual(sp['current_category_url'], "https://test.com/source")
        self.assertEqual(sp['current_category_index'], 5)
        self.assertEqual(sp['total_categories'], 10)
        self.assertIn('last_sync', sp)
        
        # Verify repair worked
        post_repair_validation = self.validator.validate_cross_section_consistency()
        self.assertTrue(post_repair_validation.is_valid)
    
    def test_auto_repair_violations(self):
        """Test comprehensive auto-repair of multiple violations"""
        # Set up multiple inconsistencies
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 150
        
        self.state_manager.state_data['supplier_extraction_progress']['current_category_url'] = "https://test.com/source"
        self.state_manager.state_data['system_progression'] = {
            'current_category_url': "https://test.com/different"
        }
        
        # Get violations
        violations = self.validator.validate_all_invariants()
        invalid_violations = [v for v in violations if not v.is_valid]
        self.assertGreater(len(invalid_violations), 0)
        
        # Apply auto-repair
        repair_result = self.validator.auto_repair_violations(invalid_violations)
        
        self.assertTrue(repair_result.success)
        self.assertGreater(len(repair_result.repairs_applied), 0)
        self.assertEqual(len(repair_result.errors), 0)
        self.assertIsNotNone(repair_result.backup_created)
        
        # Verify backup was created
        self.assertTrue(Path(repair_result.backup_created).exists())
        
        # Verify all violations are now resolved
        post_repair_violations = self.validator.validate_all_invariants()
        remaining_violations = [v for v in post_repair_violations if not v.is_valid]
        self.assertEqual(len(remaining_violations), 0)


class TestStateManagerIntegration(unittest.TestCase):
    """Test integration of invariant validation with state manager"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_invariant_validator_initialization(self):
        """Test that invariant validator is properly initialized"""
        validator = self.state_manager.get_invariant_validator()
        
        if validator:  # Only test if enhanced components are available
            self.assertIsInstance(validator, InvariantValidator)
            self.assertIsNotNone(validator.repair_engine)
    
    def test_save_state_atomic_with_validation(self):
        """Test that save_state_atomic includes invariant validation"""
        # Set up inconsistent state
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 200  # Critical inconsistency
        
        # Save state - should trigger validation and repair
        self.state_manager.save_state_atomic()
        
        # Check if repair was applied (if validator is available)
        validator = self.state_manager.get_invariant_validator()
        if validator:
            # Verify that the inconsistency was repaired
            extracted = self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total']
            successful = self.state_manager.state_data['successful_products']
            self.assertEqual(extracted, successful)  # Should be synchronized
    
    def test_atomic_progress_update_integration(self):
        """Test that atomic progress updates work correctly"""
        # Test the fixed update_processing_progress method
        initial_progress = self.state_manager.state_data.get('progress_index', 0)
        initial_session = self.state_manager.state_data.get('session_products_processed', 0)
        initial_resumption = self.state_manager.state_data.get('resumption_index', 0)
        
        # Update progress
        result = self.state_manager.update_processing_progress(increment=5)
        
        # Should succeed (either with atomic operations or fallback)
        self.assertTrue(result)
        
        # Check that progress was updated
        new_progress = self.state_manager.state_data.get('progress_index', 0)
        new_session = self.state_manager.state_data.get('session_products_processed', 0)
        new_resumption = self.state_manager.state_data.get('resumption_index', 0)
        
        self.assertEqual(new_progress, initial_progress + 5)
        self.assertEqual(new_session, initial_session + 5)
        self.assertEqual(new_resumption, initial_resumption + 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)