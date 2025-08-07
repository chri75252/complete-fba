#!/usr/bin/env python3
"""
Quick Hash Optimization Validation Script
================================================================================

This script provides a quick validation test of the hash optimization system
to ensure it's working correctly before running the full system.

Author: Hash Optimization Validator
Date: July 26, 2025
"""

import os
import sys
import json
import time
import logging

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Quick validation of hash optimization system"""
    print("🚀 HASH OPTIMIZATION QUICK VALIDATION")
    print("=" * 60)
    
    try:
        # Test imports
        print("🧪 Testing imports...")
        from utils.hash_lookup_optimizer import HashLookupOptimizer, LegacyPerformanceComparator
        print("✅ Hash optimization modules imported successfully")
        
        # Initialize optimizer
        print("🧪 Initializing hash optimizer...")
        hash_optimizer = HashLookupOptimizer(logger=logger)
        performance_comparator = LegacyPerformanceComparator(logger=logger)
        print("✅ Hash optimizer initialized successfully")
        
        # Create test data
        print("🧪 Creating test data...")
        test_linking_map = []
        for i in range(100):
            entry = {
                "supplier_ean": f"123456789{i:03d}",
                "supplier_url": f"https://test.com/product/{i}",
                "amazon_asin": f"T{i:09d}",
                "chosen_amazon_asin": f"T{i:09d}",
                "supplier_title": f"Test Product {i}",
                "match_method": "EAN"
            }
            test_linking_map.append(entry)
        print(f"✅ Created {len(test_linking_map)} test entries")
        
        # Build indexes
        print("🧪 Building hash indexes...")
        start_time = time.time()
        hash_optimizer.build_indexes(test_linking_map)
        build_time = time.time() - start_time
        print(f"✅ Hash indexes built in {build_time*1000:.3f}ms")
        
        # Test lookups
        print("🧪 Testing hash lookups...")
        test_ean = test_linking_map[50]['supplier_ean']
        test_url = test_linking_map[50]['supplier_url']
        
        # EAN lookup
        start_time = time.time()
        found_entry = hash_optimizer.get_entry_by_ean(test_ean)
        ean_time = time.time() - start_time
        
        if found_entry and found_entry['supplier_ean'] == test_ean:
            print(f"✅ EAN lookup successful in {ean_time*1000:.3f}ms")
        else:
            print("❌ EAN lookup failed")
            return False
        
        # URL lookup
        start_time = time.time()
        found_entry = hash_optimizer.get_entry_by_url(test_url)
        url_time = time.time() - start_time
        
        if found_entry and found_entry['supplier_url'] == test_url:
            print(f"✅ URL lookup successful in {url_time*1000:.3f}ms")
        else:
            print("❌ URL lookup failed")
            return False
        
        # Test performance comparison
        print("🧪 Testing performance comparison...")
        test_eans = [entry['supplier_ean'] for entry in test_linking_map[0:20:2]]
        test_urls = [entry['supplier_url'] for entry in test_linking_map[1:21:2]]
        
        benchmark_results = performance_comparator.benchmark_performance(
            linking_map=test_linking_map,
            test_eans=test_eans,
            test_urls=test_urls,
            hash_optimizer=hash_optimizer
        )
        
        if benchmark_results.get('performance_improvement', 0) > 1.0:
            print(f"✅ Performance improvement: {benchmark_results['performance_improvement']:.1f}x faster")
        else:
            print("❌ Performance comparison failed")
            return False
        
        # Test statistics
        print("🧪 Testing statistics...")
        stats = hash_optimizer.get_index_stats()
        if stats['ean_entries'] == len(test_linking_map):
            print(f"✅ Statistics correct: {stats['ean_entries']} EAN entries")
        else:
            print("❌ Statistics validation failed")
            return False
        
        print("\n🎉 HASH OPTIMIZATION VALIDATION SUCCESSFUL!")
        print("=" * 60)
        print("✅ All tests passed - hash optimization system is ready!")
        print(f"📊 Performance improvement: {benchmark_results['performance_improvement']:.1f}x")
        print(f"⚡ Average hash lookup time: {benchmark_results.get('avg_hash_time_ms', 0):.3f}ms")
        print(f"🐌 Average linear lookup time: {benchmark_results.get('avg_linear_time_ms', 0):.3f}ms")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure hash_lookup_optimizer.py is in the utils/ directory")
        return False
    except Exception as e:
        print(f"❌ Validation Error: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)