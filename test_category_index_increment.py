#!/usr/bin/env python3
"""
Test script to verify category index increment functionality
"""

import sys
import json
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_category_index_increment():
    """Test that category index increments correctly"""
    
    # Initialize state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    print("🧪 TESTING CATEGORY INDEX INCREMENT")
    print("=" * 50)
    
    # Load existing state
    state_loaded = state_manager.load_state()
    print(f"State loaded: {state_loaded}")
    
    # Get initial state
    sp = state_manager.state_data.get("system_progression", {})
    initial_persistent = sp.get("persistent_category_index", 0)
    initial_current = sp.get("current_category_index", 0)
    
    print(f"Initial persistent_category_index: {initial_persistent}")
    print(f"Initial current_category_index: {initial_current}")
    
    # Test 1: Call mark_category_completed
    print("\n📋 TEST 1: Calling mark_category_completed()")
    test_url = "https://www.poundwholesale.co.uk/test-category"
    state_manager.mark_category_completed(test_url)
    
    # Check results
    sp_after = state_manager.state_data.get("system_progression", {})
    after_persistent = sp_after.get("persistent_category_index", 0)
    after_current = sp_after.get("current_category_index", 0)
    
    print(f"After Test 1 persistent_category_index: {after_persistent}")
    print(f"After Test 1 current_category_index: {after_current}")
    
    # Verify increment worked
    if after_persistent == initial_persistent + 1 and after_current == initial_current + 1:
        print("✅ TEST 1 PASSED: Category index incremented correctly")
    else:
        print("❌ TEST 1 FAILED: Category index did not increment correctly")
        return False
    
    # Test 2: Call mark_category_completed again
    print("\n📋 TEST 2: Calling mark_category_completed() again")
    test_url2 = "https://www.poundwholesale.co.uk/test-category-2"
    state_manager.mark_category_completed(test_url2)
    
    # Check results
    sp_after2 = state_manager.state_data.get("system_progression", {})
    after2_persistent = sp_after2.get("persistent_category_index", 0)
    after2_current = sp_after2.get("current_category_index", 0)
    
    print(f"After Test 2 persistent_category_index: {after2_persistent}")
    print(f"After Test 2 current_category_index: {after2_current}")
    
    # Verify second increment worked
    if after2_persistent == after_persistent + 1 and after2_current == after_current + 1:
        print("✅ TEST 2 PASSED: Category index incremented correctly on second call")
    else:
        print("❌ TEST 2 FAILED: Category index did not increment correctly on second call")
        return False
    
    # Test 3: Verify persistence by creating new state manager instance
    print("\n📋 TEST 3: Testing persistence across instances")
    state_manager2 = FixedEnhancedStateManager("poundwholesale.co.uk")
    state_manager2.load_state()
    
    sp_reload = state_manager2.state_data.get("system_progression", {})
    reload_persistent = sp_reload.get("persistent_category_index", 0)
    reload_current = sp_reload.get("current_category_index", 0)
    
    print(f"Reloaded persistent_category_index: {reload_persistent}")
    print(f"Reloaded current_category_index: {reload_current}")
    
    if reload_persistent == after2_persistent and reload_current == after2_current:
        print("✅ TEST 3 PASSED: Category index persisted correctly across instances")
    else:
        print("❌ TEST 3 FAILED: Category index did not persist correctly")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print(f"Final category index values: persistent={reload_persistent}, current={reload_current}")
    
    return True

def show_current_state():
    """Show the current state for debugging"""
    try:
        state_file = Path("processing_states/poundwholesale_co_uk_processing_state.json")
        if state_file.exists():
            with open(state_file, 'r') as f:
                state_data = json.load(f)
            
            sp = state_data.get("system_progression", {})
            print("\n📊 CURRENT STATE:")
            print(f"persistent_category_index: {sp.get('persistent_category_index', 'NOT FOUND')}")
            print(f"current_category_index: {sp.get('current_category_index', 'NOT FOUND')}")
            print(f"current_phase: {sp.get('current_phase', 'NOT FOUND')}")
            print(f"total_categories: {sp.get('total_categories', 'NOT FOUND')}")
        else:
            print("📊 No state file found")
    except Exception as e:
        print(f"📊 Error reading state file: {e}")

if __name__ == "__main__":
    print("🔍 CATEGORY INDEX INCREMENT TEST")
    print("=" * 60)
    
    # Show current state first
    show_current_state()
    
    # Run tests
    success = test_category_index_increment()
    
    # Show final state
    show_current_state()
    
    if success:
        print("\n🎯 CONCLUSION: Category index increment is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 CONCLUSION: Category index increment needs further investigation")
        sys.exit(1)