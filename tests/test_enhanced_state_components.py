"""
Test Suite for Enhanced State Management Components
=================================================

This module provides comprehensive tests for the enhanced state management components
including atomic operations, calculation logic, and structured logging.
"""

import unittest
import tempfile
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.enhanced_state_components import (
    AtomicStateUpdater,
    ProductsExtractedCalculator,
    StructuredLogger,
    ValidationResult,
    RepairResult,
    create_enhanced_state_components
)
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestAtomicStateUpdater(unittest.TestCase):
    """Test atomic state update operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.atomic_updater = AtomicStateUpdater(self.state_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_update_category_atomic_success(self):
        """Test successful atomic category update"""
        url = "https://test.com/category1"
        index = 5
        products_total = 100
        
        result = self.atomic_updater.update_category_atomic(url, index, products_total)
        
        self.assertTrue(result)
        self.assertEqual(
            self.state_manager.state_data['supplier_extraction_progress']['current_category_url'], 
            url
        )
        self.assertEqual(
            self.state_manager.state_data['supplier_extraction_progress']['current_category_index'], 
            index
        )
        self.assertEqual(
            self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'], 
            products_total
        )
    
    def test_update_progress_atomic_success(self):
        """Test successful atomic progress update"""
        updates = {
            'successful_products': 50,
            'profitable_products': 10,
            'total_profit_found': 125.50
        }
        
        result = self.atomic_updater.update_progress_atomic(**updates)
        
        self.assertTrue(result)
        for key, value in updates.items():
            self.assertEqual(self.state_manager.state_data[key], value)
    
    def test_synchronize_sections_atomic(self):
        """Test atomic section synchronization"""
        # Set up initial data
        self.state_manager.state_data['supplier_extraction_progress']['current_category_url'] = "https://test.com/cat1"
        self.state_manager.state_data['supplier_extraction_progress']['current_category_index'] = 3
        
        result = self.atomic_updater.synchronize_sections_atomic()
        
        self.assertTrue(result)
        self.assertIn('system_progression', self.state_manager.state_data)
        self.assertEqual(
            self.state_manager.state_data['system_progression']['current_category_url'],
            "https://test.com/cat1"
        )
        self.assertEqual(
            self.state_manager.state_data['system_progression']['current_category_index'],
            3
        )


class TestProductsExtractedCalculator(unittest.TestCase):
    """Test products extracted calculation logic"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.calculator = ProductsExtractedCalculator(self.state_manager)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_calculate_from_processed_products(self):
        """Test calculation from processed_products dictionary"""
        # Set up test data
        self.state_manager.state_data['processed_products'] = {
            'url1': {'status': 'processed'},
            'url2': {'status': 'processed'},
            'url3': {'status': 'processed'}
        }
        
        result = self.calculator.calculate_from_processed_products()
        self.assertEqual(result, 3)
    
    def test_calculate_from_category_completion(self):
        """Test calculation from category completion data"""
        # Set up test data
        self.state_manager.state_data['supplier_extraction_progress']['categories_completed'] = [
            'https://test.com/cat1',
            'https://test.com/cat2'
        ]
        self.state_manager.state_data['processed_products'] = {
            'url1': {'status': 'processed', 'source_category': 'https://test.com/cat1'},
            'url2': {'status': 'processed', 'source_category': 'https://test.com/cat1'},
            'url3': {'status': 'processed', 'source_category': 'https://test.com/cat2'}
        }
        
        result = self.calculator.calculate_from_category_completion()
        self.assertEqual(result, 3)
    
    def test_get_canonical_count(self):
        """Test canonical count calculation"""
        # Set up test data
        self.state_manager.state_data['processed_products'] = {
            'url1': {'status': 'processed'},
            'url2': {'status': 'processed'},
            'url3': {'status': 'processed'},
            'url4': {'status': 'processed'},
            'url5': {'status': 'processed'}
        }
        
        result = self.calculator.get_canonical_count()
        self.assertEqual(result, 5)
    
    def test_update_products_extracted_total(self):
        """Test updating products_extracted_total field"""
        # Set up test data
        self.state_manager.state_data['processed_products'] = {
            'url1': {'status': 'processed'},
            'url2': {'status': 'processed'}
        }
        
        result = self.calculator.update_products_extracted_total()
        
        self.assertTrue(result)
        self.assertEqual(
            self.state_manager.state_data['supplier_extraction_progress']['products_extracted_total'],
            2
        )


class TestStructuredLogger(unittest.TestCase):
    """Test structured logging functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.logger = StructuredLogger("TestLogger")
    
    def test_log_state_update(self):
        """Test state update logging"""
        fields = {'field1': 'value1', 'field2': 'value2'}
        
        # Should not raise any exceptions
        self.logger.log_state_update("test_operation", fields, True, 15.5)
        
        # Check metrics
        metrics = self.logger.get_metrics()
        self.assertEqual(metrics['state_updates'], 1)
    
    def test_log_invariant_check(self):
        """Test invariant check logging"""
        details = {'current': 10, 'expected': 10}
        
        # Should not raise any exceptions
        self.logger.log_invariant_check("test_invariant", "valid", details)
        
        # Check metrics
        metrics = self.logger.get_metrics()
        self.assertEqual(metrics['invariant_checks'], 1)
    
    def test_log_reconciliation(self):
        """Test reconciliation logging"""
        changes = ['change1', 'change2']
        
        # Should not raise any exceptions
        self.logger.log_reconciliation("test_reconciliation", changes, True)
        
        # Check metrics
        metrics = self.logger.get_metrics()
        self.assertEqual(metrics['reconciliations'], 1)


class TestComponentFactory(unittest.TestCase):
    """Test component factory function"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_enhanced_state_components(self):
        """Test factory function creates all components"""
        components = create_enhanced_state_components(self.state_manager)
        
        self.assertIn('atomic_updater', components)
        self.assertIn('calculator', components)
        self.assertIn('logger', components)
        
        self.assertIsInstance(components['atomic_updater'], AtomicStateUpdater)
        self.assertIsInstance(components['calculator'], ProductsExtractedCalculator)
        self.assertIsInstance(components['logger'], StructuredLogger)


if __name__ == '__main__':
    # Create tests directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)