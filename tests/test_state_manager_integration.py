"""
Integration Tests for Enhanced State Manager
==========================================

This module tests the integration between FixedEnhancedStateManager
and the enhanced state components.
"""

import unittest
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
from utils.enhanced_state_components import ProductsExtractedCalculator, AtomicStateUpdater


class TestStateManagerIntegration(unittest.TestCase):
    """Test integration between state manager and enhanced components"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        
        # Set up test data
        self._setup_test_data()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_test_data(self):
        """Set up realistic test data"""
        # Set up processed products
        self.state_manager.state_data['processed_products'] = {
            'https://test.com/product1': {'status': 'processed', 'source_category': 'cat1'},
            'https://test.com/product2': {'status': 'processed', 'source_category': 'cat1'},
            'https://test.com/product3': {'status': 'processed', 'source_category': 'cat2'},
        }
        
        # Set up successful products
        self.state_manager.state_data['successful_products'] = 3
    
    def test_enhanced_components_initialization(self):
        """Test that enhanced components are properly initialized"""
        # Components should be available
        calculator = self.state_manager.get_calculator()
        atomic_updater = self.state_manager.get_atomic_updater()
        structured_logger = self.state_manager.get_structured_logger()
        
        if calculator:  # Only test if components are available
            self.assertIsInstance(calculator, ProductsExtractedCalculator)
            self.assertIsInstance(atomic_updater, AtomicStateUpdater)
            self.assertIsNotNone(structured_logger)
    
    def test_update_products_extracted_total_enhanced(self):
        """Test enhanced products extracted total update"""
        # Initial value should be 0
        initial_value = self.state_manager.state_data['supplier_extraction_progress'].get('products_extracted_total', 0)
        self.assertEqual(initial_value, 0)
        
        # Update using enhanced method
        result = self.state_manager.update_products_extracted_total_enhanced()
        self.assertTrue(result)
        
        # Value should be updated
        updated_value = self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total']
        self.assertEqual(updated_value, 3)  # Should match processed products count
    
    def test_update_category_atomic_enhanced(self):
        """Test enhanced atomic category update"""
        url = "https://test.com/category1"
        index = 5
        products_total = 100
        
        result = self.state_manager.update_category_atomic_enhanced(url, index, products_total)
        self.assertTrue(result)
        
        # Check that values were updated
        sep = self.state_manager.state_data['supplier_extraction_progress']
        self.assertEqual(sep['current_category_url'], url)
        self.assertEqual(sep['current_category_index'], index)
        self.assertEqual(sep['products_extracted_total'], products_total)
    
    def test_get_calculation_report(self):
        """Test calculation report generation"""
        report = self.state_manager.get_calculation_report()
        
        # Report should have required fields
        self.assertIn('canonical_count', report)
        self.assertIn('calculation_analysis', report)
        self.assertIn('validation_result', report)
        self.assertIn('generated_at', report)
        
        # Canonical count should match our test data
        if 'error' not in report:
            self.assertEqual(report['canonical_count'], 3)
    
    def test_fallback_behavior_without_enhanced_components(self):
        """Test that fallback methods work when enhanced components are not available"""
        # Simulate missing enhanced components
        original_calculator = self.state_manager._calculator
        self.state_manager._calculator = None
        
        try:
            # Should still work with fallback
            result = self.state_manager.update_products_extracted_total_enhanced()
            self.assertTrue(result)
            
            # Value should be updated using basic calculation
            updated_value = self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total']
            self.assertEqual(updated_value, 3)
            
        finally:
            # Restore original calculator
            self.state_manager._calculator = original_calculator
    
    def test_basic_category_update_fallback(self):
        """Test basic category update fallback"""
        # Simulate missing atomic updater
        original_updater = self.state_manager._atomic_updater
        self.state_manager._atomic_updater = None
        
        try:
            url = "https://test.com/category2"
            index = 3
            products_total = 50
            
            result = self.state_manager.update_category_atomic_enhanced(url, index, products_total)
            self.assertTrue(result)
            
            # Check that values were updated using basic method
            sep = self.state_manager.state_data['supplier_extraction_progress']
            self.assertEqual(sep['current_category_url'], url)
            self.assertEqual(sep['current_category_index'], index)
            self.assertEqual(sep['products_extracted_total'], products_total)
            
        finally:
            # Restore original updater
            self.state_manager._atomic_updater = original_updater
    
    def test_state_persistence_with_enhanced_data(self):
        """Test that enhanced data persists correctly"""
        # Update using enhanced methods
        self.state_manager.update_products_extracted_total_enhanced()
        self.state_manager.update_category_atomic_enhanced("https://test.com/cat1", 2, 75)
        
        # Save state
        self.state_manager.save_state()
        
        # Create new state manager and load
        new_state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        new_state_manager.load_state()
        
        # Check that enhanced data was persisted
        sep = new_state_manager.state_data['supplier_extraction_progress']
        self.assertEqual(sep['products_extracted_total'], 75)
        self.assertEqual(sep['current_category_url'], "https://test.com/cat1")
        self.assertEqual(sep['current_category_index'], 2)
    
    def test_calculation_metadata_storage(self):
        """Test that calculation metadata is stored correctly"""
        # Update using enhanced method
        result = self.state_manager.update_products_extracted_total_enhanced()
        self.assertTrue(result)
        
        # Check if metadata was stored (only if enhanced components are available)
        if self.state_manager._calculator:
            self.assertIn('calculation_metadata', self.state_manager.state_data)
            metadata = self.state_manager.state_data['calculation_metadata']['products_extracted_total']
            
            self.assertIn('last_update', metadata)
            self.assertIn('method_used', metadata)
            self.assertIn('confidence', metadata)
            self.assertIn('old_value', metadata)
            self.assertIn('new_value', metadata)
    
    def test_error_handling_in_enhanced_methods(self):
        """Test error handling in enhanced methods"""
        # Corrupt the state data to trigger errors
        original_data = self.state_manager.state_data['processed_products']
        self.state_manager.state_data['processed_products'] = "invalid_data"
        
        try:
            # Should handle error gracefully
            result = self.state_manager.update_products_extracted_total_enhanced()
            # Result might be True (fallback) or False (error), but shouldn't crash
            self.assertIsInstance(result, bool)
            
        finally:
            # Restore original data
            self.state_manager.state_data['processed_products'] = original_data


if __name__ == '__main__':
    unittest.main(verbosity=2)