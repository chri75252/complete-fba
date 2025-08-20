"""
Comprehensive Tests for AtomicStateUpdater
=========================================

This module tests the enhanced AtomicStateUpdater with retry logic,
error handling, and comprehensive atomic operations.
"""

import unittest
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.enhanced_state_components import AtomicStateUpdater
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestAtomicStateUpdater(unittest.TestCase):
    """Test enhanced AtomicStateUpdater functionality"""
    
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
        
        # Check that all related fields were updated
        sep = self.state_manager.state_data['supplier_extraction_progress']
        self.assertEqual(sep['current_category_url'], url)
        self.assertEqual(sep['current_category_index'], index)
        self.assertEqual(sep['products_extracted_total'], products_total)
        
        # Check that system_progression was synchronized
        if 'system_progression' in self.state_manager.state_data:
            sp = self.state_manager.state_data['system_progression']
            self.assertEqual(sp['current_category_url'], url)
            self.assertEqual(sp['current_category_index'], index)
        
        # Check metrics
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['successful_operations'], 1)
        self.assertEqual(metrics['metrics']['failed_operations'], 0)
    
    def test_update_category_atomic_validation(self):
        """Test input validation for atomic category update"""
        # Reset metrics to start clean
        self.atomic_updater.reset_metrics()
        
        # Test invalid URL
        result = self.atomic_updater.update_category_atomic("", 5, 100)
        self.assertFalse(result)
        
        # Test invalid index
        result = self.atomic_updater.update_category_atomic("https://test.com/cat", -1, 100)
        self.assertFalse(result)
        
        # Test invalid products_total
        result = self.atomic_updater.update_category_atomic("https://test.com/cat", 5, -10)
        self.assertFalse(result)
        
        # Check that failed operations were recorded (3 operations, each with retries)
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['failed_operations'], 3)
        # Should have retry operations due to validation failures
        self.assertGreater(metrics['metrics']['retry_operations'], 0)
    
    def test_update_progress_atomic_success(self):
        """Test successful atomic progress update"""
        updates = {
            'successful_products': 50,
            'profitable_products': 10,
            'total_profit_found': 125.50
        }
        
        result = self.atomic_updater.update_progress_atomic(**updates)
        
        self.assertTrue(result)
        
        # Check that all fields were updated
        for key, value in updates.items():
            self.assertEqual(self.state_manager.state_data[key], value)
        
        # Check that last_updated was set
        self.assertIsNotNone(self.state_manager.state_data.get('last_updated'))
        
        # Check metrics
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['successful_operations'], 1)
    
    def test_update_progress_atomic_validation(self):
        """Test input validation for atomic progress update"""
        # Reset metrics to start clean
        self.atomic_updater.reset_metrics()
        
        # Test invalid field
        result = self.atomic_updater.update_progress_atomic(invalid_field=100)
        self.assertFalse(result)
        
        # Test invalid value for successful_products
        result = self.atomic_updater.update_progress_atomic(successful_products=-5)
        self.assertFalse(result)
        
        # Test invalid value for total_profit_found
        result = self.atomic_updater.update_progress_atomic(total_profit_found="invalid")
        self.assertFalse(result)
        
        # Check that failed operations were recorded (3 operations, each with retries)
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['failed_operations'], 3)
        # Should have retry operations due to validation failures
        self.assertGreater(metrics['metrics']['retry_operations'], 0)
    
    def test_synchronize_sections_atomic(self):
        """Test atomic section synchronization"""
        # Set up initial data in supplier_extraction_progress
        sep = self.state_manager.state_data['supplier_extraction_progress']
        sep['current_category_url'] = "https://test.com/cat1"
        sep['current_category_index'] = 3
        sep['total_categories'] = 10
        
        result = self.atomic_updater.synchronize_sections_atomic()
        
        self.assertTrue(result)
        
        # Check that system_progression was created and synchronized
        self.assertIn('system_progression', self.state_manager.state_data)
        sp = self.state_manager.state_data['system_progression']
        
        self.assertEqual(sp['current_category_url'], "https://test.com/cat1")
        self.assertEqual(sp['current_category_index'], 3)
        self.assertEqual(sp['total_categories'], 10)
        self.assertEqual(sp['phase'], 'supplier_extraction')
        self.assertIsNotNone(sp.get('last_sync'))
    
    def test_update_product_status_atomic(self):
        """Test atomic product status update"""
        product_url = "https://test.com/product1"
        status = "processed"
        source_category = "https://test.com/category1"
        metadata = {"processing_time": 1.5, "success": True}
        
        result = self.atomic_updater.update_product_status_atomic(
            product_url, status, source_category, metadata
        )
        
        self.assertTrue(result)
        
        # Check that product was added to processed_products
        processed_products = self.state_manager.state_data.get('processed_products', {})
        self.assertIn(product_url, processed_products)
        
        product_data = processed_products[product_url]
        self.assertEqual(product_data['status'], status)
        self.assertEqual(product_data['source_category'], source_category)
        self.assertEqual(product_data['metadata'], metadata)
        self.assertIsNotNone(product_data.get('updated_at'))
    
    def test_retry_mechanism(self):
        """Test retry mechanism for failed operations"""
        # Set very short retry delay for testing
        original_delay = self.atomic_updater._retry_delay_seconds
        self.atomic_updater._retry_delay_seconds = 0.01
        
        try:
            # This should fail due to invalid input and trigger retries
            result = self.atomic_updater.update_category_atomic("", -1, -100)
            self.assertFalse(result)
            
            # Check that retries were attempted
            metrics = self.atomic_updater.get_metrics()
            self.assertGreater(metrics['metrics']['retry_operations'], 0)
            
        finally:
            # Restore original delay
            self.atomic_updater._retry_delay_seconds = original_delay
    
    def test_transaction_rollback(self):
        """Test transaction rollback on failure"""
        # Set initial values
        sep = self.state_manager.state_data['supplier_extraction_progress']
        original_url = "https://test.com/original"
        original_index = 1
        original_total = 50
        
        sep['current_category_url'] = original_url
        sep['current_category_index'] = original_index
        sep['products_extracted_total'] = original_total
        
        # Attempt update with invalid data (should fail and rollback)
        result = self.atomic_updater.update_category_atomic("", -1, -100)
        self.assertFalse(result)
        
        # Check that original values were preserved (rollback worked)
        self.assertEqual(sep['current_category_url'], original_url)
        self.assertEqual(sep['current_category_index'], original_index)
        self.assertEqual(sep['products_extracted_total'], original_total)
        
        # Check that rollback was recorded in metrics
        metrics = self.atomic_updater.get_metrics()
        self.assertGreater(metrics['metrics']['rollback_operations'], 0)
    
    def test_concurrent_operations(self):
        """Test handling of concurrent operations"""
        import threading
        
        results = []
        
        def update_category(index):
            result = self.atomic_updater.update_category_atomic(
                f"https://test.com/category{index}", 
                index, 
                index * 10
            )
            results.append(result)
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_category, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should succeed (though only the last one will be visible)
        self.assertTrue(all(results))
        
        # Check that operations were recorded
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['successful_operations'], 5)
    
    def test_metrics_tracking(self):
        """Test comprehensive metrics tracking"""
        # Reset metrics to start clean
        self.atomic_updater.reset_metrics()
        
        # Perform various operations
        self.atomic_updater.update_category_atomic("https://test.com/cat1", 1, 10)
        self.atomic_updater.update_progress_atomic(successful_products=5)
        self.atomic_updater.synchronize_sections_atomic()
        
        # Perform some failed operations
        self.atomic_updater.update_category_atomic("", -1, -10)  # Should fail
        
        metrics = self.atomic_updater.get_metrics()
        
        # Check metrics structure
        self.assertIn('metrics', metrics)
        self.assertIn('success_rate', metrics)
        self.assertIn('settings', metrics)
        
        # Check specific metrics
        self.assertEqual(metrics['metrics']['successful_operations'], 3)
        self.assertEqual(metrics['metrics']['failed_operations'], 1)
        self.assertEqual(metrics['success_rate'], 0.75)  # 3/4 = 0.75
        
        # Should have retry operations due to the failed operation
        self.assertGreater(metrics['metrics']['retry_operations'], 0)
    
    def test_metrics_reset(self):
        """Test metrics reset functionality"""
        # Perform some operations
        self.atomic_updater.update_category_atomic("https://test.com/cat1", 1, 10)
        self.atomic_updater.update_progress_atomic(successful_products=5)
        
        # Check that metrics are recorded
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['successful_operations'], 2)
        
        # Reset metrics
        self.atomic_updater.reset_metrics()
        
        # Check that metrics are cleared
        metrics = self.atomic_updater.get_metrics()
        self.assertEqual(metrics['metrics']['successful_operations'], 0)
        self.assertEqual(metrics['metrics']['failed_operations'], 0)
    
    def test_operation_timeout_settings(self):
        """Test operation timeout and retry settings"""
        # Check default settings
        metrics = self.atomic_updater.get_metrics()
        settings = metrics['settings']
        
        self.assertIn('max_retry_attempts', settings)
        self.assertIn('retry_delay_seconds', settings)
        self.assertIn('operation_timeout_seconds', settings)
        
        # Check that settings are reasonable
        self.assertGreater(settings['max_retry_attempts'], 0)
        self.assertGreater(settings['retry_delay_seconds'], 0)
        self.assertGreater(settings['operation_timeout_seconds'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)