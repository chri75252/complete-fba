#!/usr/bin/env python3
"""
Category Index Fix Verification Script
=====================================

This script verifies that the category index increment fix is working correctly
by simulating calls to mark_category_completed() and checking the results.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_category_increment_fix():
    """Test that the category index increment fix works correctly."""
    
    print("🔧 CATEGORY INDEX FIX VERIFICATION")
    print("=" * 50)
    
    # Initialize state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # Get initial state
    initial_state = state_manager.state_data.get("system_progression", {})
    initial_index = initial_state.get("persistent_category_index", 0)
    print(f"📊 Initial category index: {initial_index}")
    
    # Test 1: Mark first category as completed
    print("\n🧪 TEST 1: Mark first category as completed")
    state_manager.mark_category_completed("https://example.com/category-1", 0)
    
    # Check result
    updated_state = state_manager.state_data.get("system_progression", {})
    new_index = updated_state.get("persistent_category_index", 0)
    legacy_index = updated_state.get("current_category_index", 0)
    
    print(f"📊 After first completion:")
    print(f"   persistent_category_index: {new_index}")
    print(f"   current_category_index: {legacy_index}")
    
    # Verify increment
    if new_index == initial_index + 1:
        print("✅ TEST 1 PASSED: Category index incremented correctly")
    else:
        print(f"❌ TEST 1 FAILED: Expected {initial_index + 1}, got {new_index}")
        return False
    
    # Test 2: Mark second category as completed
    print("\n🧪 TEST 2: Mark second category as completed")
    state_manager.mark_category_completed("https://example.com/category-2", 1)
    
    # Check result
    updated_state = state_manager.state_data.get("system_progression", {})
    final_index = updated_state.get("persistent_category_index", 0)
    final_legacy_index = updated_state.get("current_category_index", 0)
    
    print(f"📊 After second completion:")
    print(f"   persistent_category_index: {final_index}")
    print(f"   current_category_index: {final_legacy_index}")
    
    # Verify increment
    if final_index == new_index + 1:
        print("✅ TEST 2 PASSED: Category index incremented correctly")
    else:
        print(f"❌ TEST 2 FAILED: Expected {new_index + 1}, got {final_index}")
        return False
    
    # Verify field synchronization
    if final_index == final_legacy_index:
        print("✅ SYNC TEST PASSED: Both fields are synchronized")
    else:
        print(f"❌ SYNC TEST FAILED: Fields not synchronized ({final_index} vs {final_legacy_index})")
        return False
    
    print("\n🎉 ALL TESTS PASSED!")
    print(f"📈 Category index successfully incremented from {initial_index} to {final_index}")
    
    return True

def check_processing_state_file():
    """Check the actual processing state file to see current values."""
    
    print("\n🔍 PROCESSING STATE FILE CHECK")
    print("=" * 40)
    
    state_file_path = Path("OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
    
    if state_file_path.exists():
        try:
            with open(state_file_path, 'r') as f:
                state_data = json.load(f)
            
            system_progression = state_data.get("system_progression", {})
            persistent_idx = system_progression.get("persistent_category_index", "NOT_FOUND")
            current_idx = system_progression.get("current_category_index", "NOT_FOUND")
            
            print(f"📄 State file: {state_file_path}")
            print(f"📊 persistent_category_index: {persistent_idx}")
            print(f"📊 current_category_index: {current_idx}")
            
            if persistent_idx != "NOT_FOUND" and current_idx != "NOT_FOUND":
                if persistent_idx == current_idx:
                    print("✅ Fields are synchronized in state file")
                else:
                    print("⚠️ Fields are NOT synchronized in state file")
            
        except Exception as e:
            print(f"❌ Error reading state file: {e}")
    else:
        print(f"⚠️ State file not found: {state_file_path}")

if __name__ == "__main__":
    print("🔧 VERIFYING CATEGORY INDEX INCREMENT FIX")
    print("=" * 60)
    
    # Run the fix verification test
    success = test_category_increment_fix()
    
    # Check actual state file
    check_processing_state_file()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 VERIFICATION COMPLETE: Category index increment fix is working!")
        print("✅ The next run should show incremented category indexes in the logs")
    else:
        print("❌ VERIFICATION FAILED: Fix needs additional work")
    
    print("=" * 60)