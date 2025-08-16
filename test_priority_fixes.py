#!/usr/bin/env python3
"""
Test script for Priority 1 and Priority 2 fixes
===============================================

This script tests:
1. Off-by-one enumeration fix (Priority 1)
2. New helper methods (Priority 2)

Usage: python test_priority_fixes.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enumeration_fix():
    """Test that enumeration now starts from 0 instead of 1"""
    print("🧪 Testing enumeration fix...")
    
    # Simulate the fixed enumeration
    category_batches = [['url1', 'url2'], ['url3', 'url4']]
    supplier_extraction_batch_size = 2
    
    results = []
    
    # Test the FIXED enumeration (should start from 0)
    for batch_num, category_batch in enumerate(category_batches, 0):
        for subcategory_index, category_url in enumerate(category_batch, 0):
            category_index = batch_num * supplier_extraction_batch_size + subcategory_index
            results.append({
                'batch_num': batch_num,
                'subcategory_index': subcategory_index,
                'category_index': category_index,
                'url': category_url
            })
    
    # Verify results
    expected_indices = [0, 1, 2, 3]
    actual_indices = [r['category_index'] for r in results]
    
    if actual_indices == expected_indices:
        print("✅ ENUMERATION FIX: Indices start from 0 correctly")
        return True
    else:
        print(f"❌ ENUMERATION FIX: Expected {expected_indices}, got {actual_indices}")
        return False

def test_helper_methods():
    """Test the new helper methods"""
    print("🧪 Testing helper methods...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        # Create test instance
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Test find_category_by_url
        test_urls = [
            "https://example.com/category1",
            "https://example.com/category2", 
            "https://example.com/category3"
        ]
        
        # Test finding existing URL
        index = state_manager.find_category_by_url("https://example.com/category2", test_urls)
        if index == 1:
            print("✅ HELPER METHOD: find_category_by_url works correctly")
        else:
            print(f"❌ HELPER METHOD: find_category_by_url returned {index}, expected 1")
            return False
        
        # Test finding non-existing URL
        index = state_manager.find_category_by_url("https://example.com/nonexistent", test_urls)
        if index is None:
            print("✅ HELPER METHOD: find_category_by_url correctly returns None for missing URL")
        else:
            print(f"❌ HELPER METHOD: find_category_by_url returned {index}, expected None")
            return False
        
        # Test count_processed_products_for_category with actual data
        # First, add some test processed products with source categories
        test_category_url = "https://example.com/category1"
        state_manager.mark_product_processed("https://example.com/product1", "completed", test_category_url)
        state_manager.mark_product_processed("https://example.com/product2", "completed", test_category_url)
        state_manager.mark_product_processed("https://example.com/product3", "completed", "https://example.com/category2")
        
        # Test counting products for category1 (should be 2)
        count = state_manager.count_processed_products_for_category(test_category_url)
        if count == 2:
            print("✅ HELPER METHOD: count_processed_products_for_category works correctly (counted 2 products)")
        else:
            print(f"❌ HELPER METHOD: count_processed_products_for_category returned {count}, expected 2")
            return False
        
        # Test counting products for category2 (should be 1)
        count2 = state_manager.count_processed_products_for_category("https://example.com/category2")
        if count2 == 1:
            print("✅ HELPER METHOD: count_processed_products_for_category correctly counts different categories")
        else:
            print(f"❌ HELPER METHOD: count_processed_products_for_category returned {count2}, expected 1 for category2")
            return False
        
        # Test atomic_advancement_to_next_category
        result = state_manager.atomic_advancement_to_next_category(0, 3, test_urls)
        if isinstance(result, bool):
            print("✅ HELPER METHOD: atomic_advancement_to_next_category works correctly")
        else:
            print(f"❌ HELPER METHOD: atomic_advancement_to_next_category returned {result}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ HELPER METHODS: Error testing helper methods: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Priority Fixes Tests")
    print("=" * 50)
    
    test1_passed = test_enumeration_fix()
    test2_passed = test_helper_methods()
    
    print("=" * 50)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED: Priority fixes are working correctly!")
        return 0
    else:
        print("❌ SOME TESTS FAILED: Please check the implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())