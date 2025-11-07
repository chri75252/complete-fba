#!/usr/bin/env python3
"""
Test script to verify fix for erratic category index behavior.

This script tests the scenario where the workflow calls:
1. initialize_category_processing() - should not override existing incremented values
2. mark_category_completed() - should increment the index
3. Various validation functions - should not reset incremented values
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_erratic_behavior_fix():
    print("🔧 TESTING ERRATIC BEHAVIOR FIX")
    
    # Initialize state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # Get initial state
    sp_initial = state_manager.state_data.get("system_progression", {})
    initial_index = sp_initial.get("persistent_category_index", 0)
    print(f"📊 Initial category index: {initial_index}")
    
    # Test 1: Simulate first category completion
    print("\n🧪 TEST 1: Mark first category as completed")
    state_manager.mark_category_completed("https://example.com/category-1", 0)
    
    sp_after1 = state_manager.state_data.get("system_progression", {})
    after1_index = sp_after1.get("persistent_category_index", 0)
    print(f"📊 After first completion: {after1_index}")
    
    # Test 2: Simulate workflow calling initialize_category_processing (should NOT override)
    print("\n🧪 TEST 2: Call initialize_category_processing (should preserve incremented value)")
    state_manager.initialize_category_processing(
        category_index=0,  # This should NOT override the incremented value
        category_url="https://example.com/category-2",
        total_categories=10
    )
    
    sp_after2 = state_manager.state_data.get("system_progression", {})
    after2_index = sp_after2.get("persistent_category_index", 0)
    print(f"📊 After initialize_category_processing: {after2_index}")
    
    if after2_index == after1_index:
        print("✅ TEST 2 PASSED: initialize_category_processing preserved incremented value")
    else:
        print(f"❌ TEST 2 FAILED: Expected {after1_index}, got {after2_index}")
        return False
    
    # Test 3: Complete second category
    print("\n🧪 TEST 3: Mark second category as completed")
    state_manager.mark_category_completed("https://example.com/category-2", 1)
    
    sp_after3 = state_manager.state_data.get("system_progression", {})
    after3_index = sp_after3.get("persistent_category_index", 0)
    print(f"📊 After second completion: {after3_index}")
    
    if after3_index == after2_index + 1:
        print("✅ TEST 3 PASSED: Second category incremented correctly")
    else:
        print(f"❌ TEST 3 FAILED: Expected {after2_index + 1}, got {after3_index}")
        return False
    
    # Test 4: Simulate validation function (should NOT reset)
    print("\n🧪 TEST 4: Run state validation (should preserve incremented value)")
    state_manager.validate_loaded_state()
    
    sp_after4 = state_manager.state_data.get("system_progression", {})
    after4_index = sp_after4.get("persistent_category_index", 0)
    print(f"📊 After validation: {after4_index}")
    
    if after4_index == after3_index:
        print("✅ TEST 4 PASSED: Validation preserved incremented value")
    else:
        print(f"❌ TEST 4 FAILED: Expected {after3_index}, got {after4_index}")
        return False
    
    # Test 5: Simulate bounds validation (index > total_categories)
    print("\n🧪 TEST 5: Test bounds validation with index > total_categories")
    sp = state_manager.state_data.setdefault("system_progression", {})
    sp["total_categories"] = 1  # Set total to be less than current index
    
    is_valid, repairs = state_manager.validate_and_repair_state()
    
    sp_after5 = state_manager.state_data.get("system_progression", {})
    after5_index = sp_after5.get("persistent_category_index", 0)
    print(f"📊 After bounds validation: {after5_index}")
    
    if after5_index == after4_index:
        print("✅ TEST 5 PASSED: Bounds validation preserved incremented value")
    else:
        print(f"❌ TEST 5 FAILED: Expected {after4_index}, got {after5_index}")
        return False
    
    print(f"\n🎉 ALL TESTS PASSED!")
    print(f"📈 Category index successfully maintained incremental behavior: {initial_index} → {after5_index}")
    
    return True

if __name__ == "__main__":
    success = test_erratic_behavior_fix()
    if success:
        print("\n✅ ERRATIC BEHAVIOR FIX VERIFIED SUCCESSFULLY")
    else:
        print("\n❌ ERRATIC BEHAVIOR FIX FAILED")
        sys.exit(1)