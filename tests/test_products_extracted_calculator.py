"""
Comprehensive Test Suite for ProductsExtractedCalculator
======================================================

This module provides detailed tests for the enhanced ProductsExtractedCalculator
including calculation methods, validation logic, and cross-checking capabilities.
"""

import unittest
import tempfile
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.enhanced_state_components import (
    ProductsExtractedCalculator,
    ValidationResult,
    CalculationMetadata
)
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestProductsExtractedCalculator(unittest.TestCase):
    """Comprehensive tests for ProductsExtractedCalculator"""
    
    def setUp(self):
        """Set up test environment with realistic data"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.calculator = ProductsExtractedCalculator(self.state_manager)
        
        # Set up realistic test data
        self._setup_test_data()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_test_data(self):
        """Set up realistic test data"""
        # Set up categories completed
        self.state_manager.state_data['supplier_extraction_progress']['categories_completed'] = [
            'https://test.com/category1',
            'https://test.com/category2',
            'https://test.com/category3'
        ]
        
        # Set up processed products with source categories
        self.state_manager.state_data['processed_products'] = {
            'https://test.com/product1': {
                'status': 'processed',
                'source_category': 'https://test.com/category1',
                'processed_at': '2025-08-16T10:00:00Z'
            },
            'https://test.com/product2': {
                'status': 'processed',
                'source_category': 'https://test.com/category1',
                'processed_at': '2025-08-16T10:01:00Z'
            },
            'https://test.com/product3': {
                'status': 'processed',
                'source_category': 'https://test.com/category2',
                'processed_at': '2025-08-16T10:02:00Z'
            },
            'https://test.com/product4': {
                'status': 'processed',
                'source_category': 'https://test.com/category2',
                'processed_at': '2025-08-16T10:03:00Z'
            },
            'https://test.com/product5': {
                'status': 'processed',
                'source_category': 'https://test.com/category3',
                'processed_at': '2025-08-16T10:04:00Z'
            }
        }
        
        # Set up successful products count
        self.state_manager.state_data['successful_products'] = 5
    
    def test_calculate_from_category_completion(self):
        """Test calculation from category completion data"""
        count, metadata = self.calculator.calculate_from_category_completion()
        
        # Should count all products from completed categories
        self.assertEqual(count, 5)
        self.assertIsInstance(metadata, CalculationMetadata)
        self.assertEqual(metadata.calculation_method, "category_completion")
        self.assertEqual(metadata.calculation_source_count, 3)  # 3 completed categories
        self.assertIsNotNone(metadata.validation_checksum)
    
    def test_calculate_from_processed_products(self):
        """Test calculation from processed_products dictionary"""
        count, metadata = self.calculator.calculate_from_processed_products()
        
        # Should count all processed products
        self.assertEqual(count, 5)
        self.assertIsInstance(metadata, CalculationMetadata)
        self.assertEqual(metadata.calculation_method, "processed_products")
        self.assertEqual(metadata.calculation_source_count, 5)
        self.assertIsNotNone(metadata.validation_checksum)
    
    def test_calculate_from_successful_products(self):
        """Test calculation from successful_products field"""
        count, metadata = self.calculator.calculate_from_successful_products()
        
        # Should return successful_products value
        self.assertEqual(count, 5)
        self.assertIsInstance(metadata, CalculationMetadata)
        self.assertEqual(metadata.calculation_method, "successful_products")
        self.assertEqual(metadata.calculation_source_count, 1)
    
    def test_get_canonical_count_consistent_data(self):
        """Test canonical count calculation with consistent data"""
        canonical_count, analysis = self.calculator.get_canonical_count()
        
        # All methods should return 5, so canonical should be 5
        self.assertEqual(canonical_count, 5)
        self.assertIn('canonical_count', analysis)
        self.assertIn('best_method', analysis)
        self.assertIn('all_counts', analysis)
        self.assertIn('consistency_check', analysis)
        
        # Check consistency
        self.assertTrue(analysis['consistency_check']['all_equal'])
        self.assertEqual(analysis['consistency_check']['max_deviation'], 0)
        self.assertEqual(analysis['consistency_check']['confidence'], 'high')
    
    def test_get_canonical_count_inconsistent_data(self):
        """Test canonical count calculation with inconsistent data"""
        # Modify data to create inconsistency
        self.state_manager.state_data['successful_products'] = 8  # Different from processed count
        
        canonical_count, analysis = self.calculator.get_canonical_count()
        
        # Should use the highest count (8)
        self.assertEqual(canonical_count, 8)
        self.assertEqual(analysis['best_method'], 'successful_products')
        
        # Check inconsistency detection
        self.assertFalse(analysis['consistency_check']['all_equal'])
        self.assertEqual(analysis['consistency_check']['max_deviation'], 3)  # 8 - 5 = 3
        self.assertEqual(analysis['consistency_check']['confidence'], 'medium')
    
    def test_update_products_extracted_total(self):
        """Test updating products_extracted_total field"""
        # Initial value should be 0
        initial_value = self.state_manager.state_data['supplier_extraction_progress'].get('products_extracted_total', 0)
        self.assertEqual(initial_value, 0)
        
        # Update should succeed
        result = self.calculator.update_products_extracted_total()
        self.assertTrue(result)
        
        # Value should be updated to canonical count
        updated_value = self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total']
        self.assertEqual(updated_value, 5)
        
        # Metadata should be stored
        self.assertIn('calculation_metadata', self.state_manager.state_data)
        metadata = self.state_manager.state_data['calculation_metadata']['products_extracted_total']
        self.assertIn('last_update', metadata)
        self.assertIn('method_used', metadata)
        self.assertIn('confidence', metadata)
        self.assertEqual(metadata['old_value'], 0)
        self.assertEqual(metadata['new_value'], 5)
    
    def test_validate_calculation_consistency_valid(self):
        """Test validation with consistent calculations"""
        validation = self.calculator.validate_calculation_consistency()
        
        self.assertIsInstance(validation, ValidationResult)
        self.assertEqual(validation.invariant_name, "calculation_consistency")
        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.severity, "low")
        self.assertFalse(validation.auto_repairable)  # No repair needed
    
    def test_validate_calculation_consistency_small_deviation(self):
        """Test validation with small deviation"""
        # Create small deviation
        self.state_manager.state_data['successful_products'] = 7  # Small difference
        
        validation = self.calculator.validate_calculation_consistency()
        
        self.assertTrue(validation.is_valid)  # Still valid within threshold
        self.assertEqual(validation.severity, "medium")
        self.assertTrue(validation.auto_repairable)
        self.assertEqual(validation.repair_action, "use_canonical_count")
    
    def test_validate_calculation_consistency_large_deviation(self):
        """Test validation with large deviation"""
        # Create large deviation
        self.state_manager.state_data['successful_products'] = 15  # Large difference
        
        validation = self.calculator.validate_calculation_consistency()
        
        self.assertFalse(validation.is_valid)  # Invalid due to large deviation
        self.assertEqual(validation.severity, "high")
        self.assertTrue(validation.auto_repairable)
        self.assertEqual(validation.repair_action, "recalculate_and_reconcile")
    
    def test_get_calculation_report(self):
        """Test comprehensive calculation report"""
        report = self.calculator.get_calculation_report()
        
        # Check report structure
        self.assertIn('canonical_count', report)
        self.assertIn('calculation_analysis', report)
        self.assertIn('validation_result', report)
        self.assertIn('cache_info', report)
        self.assertIn('generated_at', report)
        
        # Check values
        self.assertEqual(report['canonical_count'], 5)
        self.assertTrue(report['validation_result']['is_valid'])
        self.assertEqual(report['validation_result']['severity'], 'low')
    
    def test_caching_behavior(self):
        """Test calculation caching behavior"""
        # First call should calculate
        count1, analysis1 = self.calculator.get_canonical_count()
        
        # Second call within cache window should use cache
        count2, analysis2 = self.calculator.get_canonical_count()
        
        self.assertEqual(count1, count2)
        # Cache timestamp should be set
        self.assertIsNotNone(self.calculator._cache_timestamp)
    
    def test_error_handling(self):
        """Test error handling in calculations"""
        # Corrupt the state data
        self.state_manager.state_data['processed_products'] = "invalid_data"
        
        # Should handle error gracefully
        count, metadata = self.calculator.calculate_from_processed_products()
        self.assertEqual(count, 0)
        self.assertEqual(metadata.calculation_method, "processed_products_error")
    
    def test_empty_data_handling(self):
        """Test handling of empty data"""
        # Clear all data
        self.state_manager.state_data['supplier_extraction_progress']['categories_completed'] = []
        self.state_manager.state_data['processed_products'] = {}
        self.state_manager.state_data['successful_products'] = 0
        
        canonical_count, analysis = self.calculator.get_canonical_count()
        
        # Should handle empty data gracefully
        self.assertEqual(canonical_count, 0)
        self.assertTrue(analysis['consistency_check']['all_equal'])
        self.assertEqual(analysis['consistency_check']['confidence'], 'high')


if __name__ == '__main__':
    unittest.main(verbosity=2)