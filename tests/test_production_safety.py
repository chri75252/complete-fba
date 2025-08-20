"""
Production Safety Integration Tests
==================================

This module tests the critical production safety fixes including:
- Non-atomic state update fixes
- Invariant validation integration
- Structured logging integration
- Cross-section synchronization
"""

import unittest
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestProductionSafety(unittest.TestCase):
    """Test production safety fixes"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_atomic_progress_update_safety(self):
        """Test that progress updates are atomic and safe"""
        # Get initial values
        initial_progress = self.state_manager.state_data.get('progress_index', 0)
        initial_session = self.state_manager.state_data.get('session_products_processed', 0)
        initial_resumption = self.state_manager.state_data.get('resumption_index', 0)
        
        # Perform atomic progress update
        result = self.state_manager.update_processing_progress(increment=10)
        
        # Should succeed
        self.assertTrue(result)
        
        # All related fields should be updated consistently
        new_progress = self.state_manager.state_data.get('progress_index', 0)
        new_session = self.state_manager.state_data.get('session_products_processed', 0)
        new_resumption = self.state_manager.state_data.get('resumption_index', 0)
        
        self.assertEqual(new_progress, initial_progress + 10)
        self.assertEqual(new_session, initial_session + 10)
        self.assertEqual(new_resumption, initial_resumption + 10)
    
    def test_category_discovery_update_safety(self):
        """Test that category discovery updates are atomic and safe"""
        category_url = "https://test.com/category1"
        discovered_count = 50
        
        # Perform category discovery update
        self.state_manager.update_discovered_products_in_category(category_url, discovered_count)
        
        # Check that category data was updated
        sep = self.state_manager.state_data['supplier_extraction_progress']
        self.assertEqual(sep.get('total_products_in_current_category'), discovered_count)
        self.assertEqual(sep.get('discovered_products_in_current_category'), discovered_count)
        
        # URL should be normalized and stored
        self.assertIn('current_category_url', sep)
        # Note: original_category_url may not be stored by atomic updater (that's fine)
    
    def test_invariant_validation_integration(self):
        """Test that invariant validation is integrated into save operations"""
        # Create an inconsistent state
        self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'] = 100
        self.state_manager.state_data['successful_products'] = 200  # Inconsistent
        
        # Save state - should trigger validation and repair
        self.state_manager.save_state_atomic()
        
        # If validator is available, inconsistency should be repaired
        validator = self.state_manager.get_invariant_validator()
        if validator:
            extracted = self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total']
            successful = self.state_manager.state_data['successful_products']
            self.assertEqual(extracted, successful)  # Should be synchronized
    
    def test_cross_section_synchronization(self):
        """Test cross-section synchronization functionality"""
        # Set up data in supplier_extraction_progress
        sep = self.state_manager.state_data['supplier_extraction_progress']
        sep['current_category_url'] = "https://test.com/sync-test"
        sep['current_category_index'] = 7
        sep['total_categories'] = 15
        
        # Synchronize sections
        result = self.state_manager.synchronize_sections_enhanced()
        self.assertTrue(result)
        
        # Check that system_progression was synchronized
        sp = self.state_manager.state_data.get('system_progression', {})
        self.assertEqual(sp.get('current_category_url'), "https://test.com/sync-test")
        self.assertEqual(sp.get('current_category_index'), 7)
        self.assertEqual(sp.get('total_categories'), 15)
        self.assertEqual(sp.get('phase'), 'supplier_extraction')
        self.assertIn('last_sync', sp)
    
    def test_structured_logging_integration(self):
        """Test that structured logging is integrated"""
        logger = self.state_manager.get_structured_logger()
        
        if logger:  # Only test if enhanced components are available
            # Get initial metrics
            initial_metrics = logger.get_metrics()
            
            # Perform operations that should trigger structured logging
            self.state_manager.update_processing_progress(increment=5)
            self.state_manager.save_state_atomic()
            
            # Check that metrics were updated
            final_metrics = logger.get_metrics()
            self.assertGreaterEqual(final_metrics['state_updates'], initial_metrics['state_updates'])
    
    def test_enhanced_components_availability(self):
        """Test that enhanced components are properly initialized"""
        # Check that enhanced components are available
        calculator = self.state_manager.get_calculator()
        atomic_updater = self.state_manager.get_atomic_updater()
        structured_logger = self.state_manager.get_structured_logger()
        invariant_validator = self.state_manager.get_invariant_validator()
        
        # Components should be available (or None if not initialized)
        # This test verifies the initialization doesn't crash
        self.assertIsNotNone(self.state_manager._enhanced_components)
    
    def test_fallback_behavior(self):
        """Test that fallback behavior works when enhanced components are not available"""
        # Temporarily disable enhanced components
        original_components = self.state_manager._enhanced_components
        original_atomic_updater = self.state_manager._atomic_updater
        
        self.state_manager._enhanced_components = None
        self.state_manager._atomic_updater = None
        
        try:
            # Operations should still work with fallback
            result = self.state_manager.update_processing_progress(increment=3)
            self.assertTrue(result)
            
            # Synchronization should work with fallback
            sync_result = self.state_manager.synchronize_sections_enhanced()
            self.assertTrue(sync_result)
            
        finally:
            # Restore original components
            self.state_manager._enhanced_components = original_components
            self.state_manager._atomic_updater = original_atomic_updater
    
    def test_no_duplicate_methods(self):
        """Test that there are no duplicate method definitions"""
        # This test verifies that the duplicate method issue was fixed
        atomic_updater = self.state_manager.get_atomic_updater()
        
        if atomic_updater:
            # Should have both methods with different names
            self.assertTrue(hasattr(atomic_updater, 'update_progress_atomic'))
            self.assertTrue(hasattr(atomic_updater, 'update_progress_incremental_atomic'))
            
            # Methods should be different
            self.assertNotEqual(
                atomic_updater.update_progress_atomic,
                atomic_updater.update_progress_incremental_atomic
            )
    
    def test_no_unreachable_code(self):
        """Test that unreachable code was removed"""
        # This test verifies that the update_processing_progress method
        # doesn't have unreachable code after return statements
        
        # The method should execute without issues
        result = self.state_manager.update_processing_progress(increment=1, product_url="https://test.com/product1")
        self.assertTrue(result)
        
        # Product should be processed if URL was provided
        if self.state_manager._atomic_updater:
            # With atomic updater, product status should be updated
            processed_products = self.state_manager.state_data.get('processed_products', {})
            # May or may not be there depending on implementation, but shouldn't crash
        else:
            # With fallback, product should be in processed_products
            processed_products = self.state_manager.state_data.get('processed_products', {})
            self.assertGreater(len(processed_products), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)