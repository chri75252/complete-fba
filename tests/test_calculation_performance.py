"""
Performance Tests for ProductsExtractedCalculator
===============================================

This module tests the performance optimizations in ProductsExtractedCalculator
including caching, lazy calculation, and performance monitoring.
"""

import unittest
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.enhanced_state_components import ProductsExtractedCalculator
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager


class TestCalculationPerformance(unittest.TestCase):
    """Test performance optimizations in ProductsExtractedCalculator"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = FixedEnhancedStateManager("test_supplier", self.temp_dir)
        self.calculator = ProductsExtractedCalculator(self.state_manager)
        
        # Set up test data
        self._setup_test_data()
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _setup_test_data(self, size: int = 100):
        """Set up test data of specified size"""
        # Create processed products
        processed_products = {}
        for i in range(size):
            processed_products[f'https://test.com/product{i}'] = {
                'status': 'processed',
                'source_category': f'https://test.com/category{i % 10}',
                'processed_at': datetime.now(timezone.utc).isoformat()
            }
        
        self.state_manager.state_data['processed_products'] = processed_products
        self.state_manager.state_data['successful_products'] = size
        
        # Set up completed categories
        categories = [f'https://test.com/category{i}' for i in range(10)]
        self.state_manager.state_data['supplier_extraction_progress']['categories_completed'] = categories
    
    def test_cache_functionality(self):
        """Test that caching works correctly"""
        # First call should calculate
        start_time = time.time()
        count1, analysis1 = self.calculator.get_canonical_count()
        first_call_time = time.time() - start_time
        
        # Second call should use cache
        start_time = time.time()
        count2, analysis2 = self.calculator.get_canonical_count()
        second_call_time = time.time() - start_time
        
        # Results should be identical
        self.assertEqual(count1, count2)
        
        # Second call should be faster (cached)
        self.assertLess(second_call_time, first_call_time)
        
        # Check performance metrics
        metrics = self.calculator.get_performance_metrics()
        self.assertEqual(metrics['metrics']['cache_hits'], 1)
        self.assertEqual(metrics['metrics']['cache_misses'], 1)
        self.assertGreater(metrics['cache_hit_rate'], 0)
    
    def test_cache_expiration(self):
        """Test that cache expires correctly"""
        # Set short cache TTL for testing
        original_ttl = self.calculator._cache_ttl_seconds
        self.calculator._cache_ttl_seconds = 0.1  # 100ms
        
        try:
            # First call
            count1, _ = self.calculator.get_canonical_count()
            
            # Wait for cache to expire
            time.sleep(0.2)
            
            # Second call should recalculate
            count2, _ = self.calculator.get_canonical_count()
            
            # Results should be identical but cache should have been refreshed
            self.assertEqual(count1, count2)
            
            # Should have 2 cache misses (no hits due to expiration)
            metrics = self.calculator.get_performance_metrics()
            self.assertEqual(metrics['metrics']['cache_misses'], 2)
            self.assertEqual(metrics['metrics']['cache_hits'], 0)
            
        finally:
            # Restore original TTL
            self.calculator._cache_ttl_seconds = original_ttl
    
    def test_lazy_calculation_threshold(self):
        """Test lazy calculation for large datasets"""
        # Set up large dataset
        self._setup_test_data(2000)  # Above lazy threshold
        
        # Set low lazy threshold for testing
        original_threshold = self.calculator._lazy_calculation_threshold
        self.calculator._lazy_calculation_threshold = 1000
        
        try:
            count, analysis = self.calculator.get_canonical_count()
            
            # Should use lazy calculation
            self.assertEqual(analysis['calculation_method'], 'lazy')
            self.assertEqual(count, 2000)
            
        finally:
            # Restore original threshold
            self.calculator._lazy_calculation_threshold = original_threshold
    
    def test_full_calculation_for_small_datasets(self):
        """Test full calculation for small datasets"""
        # Set up small dataset
        self._setup_test_data(50)  # Below lazy threshold
        
        count, analysis = self.calculator.get_canonical_count()
        
        # Should use full calculation
        self.assertEqual(analysis['calculation_method'], 'full')
        self.assertEqual(count, 50)
        
        # Should have all calculation methods in metadata
        self.assertIn('category_completion', analysis['metadata'])
        self.assertIn('processed_products', analysis['metadata'])
        self.assertIn('successful_products', analysis['metadata'])
    
    def test_performance_metrics_tracking(self):
        """Test that performance metrics are tracked correctly"""
        # Make several calculations
        for _ in range(5):
            self.calculator.get_canonical_count()
            self.calculator.clear_cache("test")  # Force recalculation
        
        metrics = self.calculator.get_performance_metrics()
        
        # Check metrics
        self.assertEqual(metrics['metrics']['calculation_count'], 5)
        self.assertEqual(metrics['metrics']['cache_misses'], 5)
        self.assertEqual(metrics['metrics']['cache_hits'], 0)
        self.assertGreater(metrics['metrics']['total_calculation_time'], 0)
        self.assertGreater(metrics['metrics']['average_calculation_time'], 0)
    
    def test_performance_optimization(self):
        """Test automatic performance optimization"""
        # Make many calculations to trigger optimization
        for _ in range(60):  # Above optimization threshold
            self.calculator.get_canonical_count()
            self.calculator.clear_cache("test")
        
        # Get original settings
        original_ttl = self.calculator._cache_ttl_seconds
        
        # Optimize settings
        optimization_result = self.calculator.optimize_performance_settings(dataset_size=5000)
        
        # Should have optimized settings
        self.assertTrue(optimization_result['optimization_applied'])
        self.assertGreater(self.calculator._cache_ttl_seconds, original_ttl)
    
    def test_cache_warming(self):
        """Test cache warming functionality"""
        # Clear cache first
        self.calculator.clear_cache("test")
        
        # Warm cache
        result = self.calculator.warm_cache()
        self.assertTrue(result)
        
        # Cache should now be populated
        self.assertIsNotNone(self.calculator._cache_timestamp)
        self.assertIn('canonical_count', self.calculator._calculation_cache)
    
    def test_performance_recommendations(self):
        """Test performance recommendations"""
        # Create scenario with poor cache hit rate
        for _ in range(10):
            self.calculator.get_canonical_count()
            self.calculator.clear_cache("test")  # Force cache misses
        
        metrics = self.calculator.get_performance_metrics()
        recommendations = metrics['recommendations']
        
        # Should have recommendations due to poor cache performance
        self.assertIsInstance(recommendations, list)
        # Should recommend cache TTL increase due to low hit rate
        cache_recommendation = any('cache TTL' in rec for rec in recommendations)
        self.assertTrue(cache_recommendation)
    
    def test_calculation_report_with_performance_data(self):
        """Test that calculation report includes performance data"""
        # Make some calculations
        self.calculator.get_canonical_count()
        
        report = self.calculator.get_calculation_report()
        
        # Check that performance data is included
        self.assertIn('performance_metrics', report)
        self.assertIn('optimization_settings', report)
        self.assertIn('cache_info', report)
        
        # Check performance metrics structure
        perf_metrics = report['performance_metrics']
        self.assertIn('calculation_count', perf_metrics)
        self.assertIn('cache_hits', perf_metrics)
        self.assertIn('cache_misses', perf_metrics)
        self.assertIn('total_calculation_time', perf_metrics)
        self.assertIn('average_calculation_time', perf_metrics)
    
    def test_large_dataset_performance(self):
        """Test performance with large dataset"""
        # Set up large dataset
        large_size = 10000
        self._setup_test_data(large_size)
        
        # Measure calculation time
        start_time = time.time()
        count, analysis = self.calculator.get_canonical_count()
        calculation_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(calculation_time, 1.0)  # Should complete within 1 second
        self.assertEqual(count, large_size)
        
        # Should use lazy calculation for large dataset
        self.assertEqual(analysis['calculation_method'], 'lazy')


if __name__ == '__main__':
    unittest.main(verbosity=2)