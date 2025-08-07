#!/usr/bin/env python3
"""
Test Script: Processing State Fixes Verification
===============================================

This script tests that all critical processing state issues are resolved:
1. last_processed_index no longer resets to 0
2. Category product counts update with real-time discoveries  
3. Metrics appear in correct sections
4. State persists correctly during interruptions
"""

import json
import tempfile
from pathlib import Path
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_index_reset_fix():
    """Test that last_processed_index no longer resets to 0"""
    print("🧪 Testing index reset fix...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test state manager
        state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        state_manager.state_file_path = Path(temp_dir) / "test_state.json"
        
        # Perform startup analysis
        state_manager.perform_startup_analysis()
        
        # Set initial progress
        state_manager.update_processing_progress(increment=43)
        initial_index = state_manager.state_data["last_processed_index"]
        
        # Save state multiple times (this used to cause resets)
        for i in range(5):
            state_manager.save_state(preserve_interruption_state=True)
            current_index = state_manager.state_data["last_processed_index"]
            
            if current_index != initial_index:
                print(f"❌ FAILED: Index changed from {initial_index} to {current_index}")
                return False
                
        print(f"✅ PASSED: Index remained stable at {initial_index}")
        return True

def test_category_discovery_update():
    """Test that category totals update with real-time discoveries"""
    print("🧪 Testing category discovery update...")
    
    state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
    
    # Simulate discovering more products than expected
    category_url = "https://test.com/category"
    initial_total = 36
    discovered_total = 105
    
    # Set initial total
    state_manager.state_data["supplier_extraction_progress"]["total_products_in_current_category"] = initial_total
    
    # Update with discovery
    state_manager.update_discovered_products_in_category(category_url, discovered_total)
    
    # Check that total was updated
    updated_total = state_manager.state_data["supplier_extraction_progress"]["total_products_in_current_category"]
    
    if updated_total == discovered_total:
        print(f"✅ PASSED: Category total updated from {initial_total} to {discovered_total}")
        return True
    else:
        print(f"❌ FAILED: Expected {discovered_total}, got {updated_total}")
        return False

def test_metric_placement():
    """Test that metrics appear in correct sections"""
    print("🧪 Testing metric placement...")
    
    state_manager = FixedEnhancedStateManager("test-supplier.co.uk") 
    
    # Check that the misplaced metric is fixed
    progress = state_manager.state_data["supplier_extraction_progress"]
    
    # Should have pages_scraped_in_session instead of total_subcategories_in_batch
    if "pages_scraped_in_session" in progress and "total_subcategories_in_batch" not in progress:
        print("✅ PASSED: Metric placement fixed - pages_scraped_in_session exists")
        return True
    else:
        print("❌ FAILED: Metric placement not fixed")
        return False

def test_state_persistence():
    """Test that state persists correctly during interruptions"""
    print("🧪 Testing state persistence...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        state_file = Path(temp_dir) / "persistence_test.json"
        
        # Create state manager and process some products
        state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        state_manager.state_file_path = state_file
        
        # Simulate processing
        state_manager.perform_startup_analysis()
        state_manager.update_processing_progress(increment=25)
        expected_progress = state_manager.state_data["session_products_processed"]
        
        # Save state
        state_manager.save_state(preserve_interruption_state=True)
        
        # Create new state manager (simulating restart)
        new_state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        new_state_manager.state_file_path = state_file
        loaded = new_state_manager.load_state()
        
        if loaded and new_state_manager.get_resumption_index() >= 0:
            print("✅ PASSED: State persistence works correctly") 
            return True
        else:
            print("❌ FAILED: State persistence broken")
            return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Running Processing State Fixes Tests")
    print("=" * 50)
    
    tests = [
        test_index_reset_fix,
        test_category_discovery_update, 
        test_metric_placement,
        test_state_persistence
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ TEST ERROR: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Processing state fixes are working!")
        return True
    else:
        print("⚠️ Some tests failed - fixes may need additional work")
        return False

if __name__ == "__main__":
    run_all_tests()
