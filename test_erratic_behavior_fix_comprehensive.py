#!/usr/bin/env python3
"""
Comprehensive Test Suite for Erratic Category Index Behavior Fix

This test suite validates that the surgical fix prevents the 0→1→2→0→1→2 
erratic behavior in chunked processing mode.

Test Scenarios:
1. Simulate chunked processing workflow calls to initialize_category_processing()
2. Verify that existing incremented values are preserved
3. Test multiple category completion cycles
4. Verify state persistence across different scenarios
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the state manager
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_chunked_processing_fix():
    """
    Test the fix for erratic category index behavior in chunked processing mode.
    
    This simulates the exact workflow pattern that was causing 0→1→2→0→1→2 behavior:
    1. mark_category_completed() increments index: 0→1
    2. initialize_category_processing() called with batch-calculated index (should NOT override)
    3. mark_category_completed() increments index: 1→2  
    4. initialize_category_processing() called again (should NOT override)
    5. Continue pattern...
    """
    print("🚀 COMPREHENSIVE TEST: Chunked Processing Erratic Behavior Fix")
    print("=" * 70)
    
    # Create temporary state file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_state_file = temp_file.name
    
    try:
        # Initialize state manager with temporary file
        state_manager = FixedEnhancedStateManager(
            supplier_name="test_supplier"
        )
        
        # Override the state file path to use our temporary file
        state_manager.state_file_path = Path(temp_state_file)
        
        print("📊 INITIAL STATE:")
        sp_initial = state_manager.state_data.get("system_progression", {})
        initial_index = sp_initial.get("persistent_category_index")
        print(f"   persistent_category_index: {initial_index}")
        
        # === SIMULATE CHUNKED PROCESSING WORKFLOW PATTERN ===
        
        print("\n🧪 TEST SEQUENCE: Simulating Chunked Processing Workflow")
        print("-" * 50)
        
        # Step 1: First category completion (should increment 0→1 or None→1)
        print("\n🎯 STEP 1: Mark first category as completed")
        state_manager.mark_category_completed("https://example.com/category-1", 0)
        
        sp_after1 = state_manager.state_data.get("system_progression", {})
        after1_index = sp_after1.get("persistent_category_index", 0)
        print(f"📊 After first completion: {after1_index}")
        
        # Step 2: Workflow calls initialize_category_processing (SHOULD NOT OVERRIDE)
        print("\n🎯 STEP 2: Chunked workflow calls initialize_category_processing with batch-calculated index")
        print("   (This was causing the erratic behavior - should now preserve incremented value)")
        state_manager.initialize_category_processing(
            category_index=0,  # ← This batch-calculated index should NOT override incremented value
            category_url="https://example.com/category-2", 
            total_categories=10
        )
        
        sp_after2 = state_manager.state_data.get("system_progression", {})
        after2_index = sp_after2.get("persistent_category_index", 0)
        print(f"📊 After initialize_category_processing: {after2_index}")
        
        if after2_index == after1_index:
            print("✅ STEP 2 PASSED: initialize_category_processing preserved incremented value")
        else:
            print(f"❌ STEP 2 FAILED: Expected {after1_index}, got {after2_index}")
            return False
        
        # Step 3: Second category completion (should increment preserved value)
        print("\n🎯 STEP 3: Mark second category as completed")
        state_manager.mark_category_completed("https://example.com/category-2", 1)
        
        sp_after3 = state_manager.state_data.get("system_progression", {})
        after3_index = sp_after3.get("persistent_category_index", 0)
        print(f"📊 After second completion: {after3_index}")
        expected_after3 = after2_index + 1
        
        if after3_index == expected_after3:
            print(f"✅ STEP 3 PASSED: Second completion incremented correctly: {after2_index}→{after3_index}")
        else:
            print(f"❌ STEP 3 FAILED: Expected {expected_after3}, got {after3_index}")
            return False
        
        # Step 4: Another workflow call (SHOULD NOT OVERRIDE)
        print("\n🎯 STEP 4: Another chunked workflow call with different batch-calculated index")
        state_manager.initialize_category_processing(
            category_index=1,  # ← Different batch-calculated index should NOT override
            category_url="https://example.com/category-3",
            total_categories=10
        )
        
        sp_after4 = state_manager.state_data.get("system_progression", {})
        after4_index = sp_after4.get("persistent_category_index", 0)
        print(f"📊 After second initialize_category_processing: {after4_index}")
        
        if after4_index == after3_index:
            print("✅ STEP 4 PASSED: Second initialize_category_processing preserved incremented value")
        else:
            print(f"❌ STEP 4 FAILED: Expected {after3_index}, got {after4_index}")
            return False
        
        # Step 5: Third category completion
        print("\n🎯 STEP 5: Mark third category as completed")
        state_manager.mark_category_completed("https://example.com/category-3", 2)
        
        sp_after5 = state_manager.state_data.get("system_progression", {})
        after5_index = sp_after5.get("persistent_category_index", 0)
        print(f"📊 After third completion: {after5_index}")
        expected_after5 = after4_index + 1
        
        if after5_index == expected_after5:
            print(f"✅ STEP 5 PASSED: Third completion incremented correctly: {after4_index}→{after5_index}")
        else:
            print(f"❌ STEP 5 FAILED: Expected {expected_after5}, got {after5_index}")
            return False
        
        # Step 6: Verify progression pattern is correct (should be: None/0→1→2→3)
        print("\n🎯 STEP 6: Verify overall progression pattern")
        expected_final = 3  # After 3 completions: None/0→1→2→3
        if after5_index == expected_final:
            print(f"✅ STEP 6 PASSED: Overall progression correct - final index: {after5_index}")
        else:
            print(f"❌ STEP 6 FAILED: Expected final index {expected_final}, got {after5_index}")
            return False
        
        # Step 7: Test state persistence
        print("\n🎯 STEP 7: Test state persistence")
        state_manager.save_state_atomic("test-persistence")
        
        # Create new state manager instance to test persistence
        state_manager_2 = FixedEnhancedStateManager(
            supplier_name="test_supplier"
        )
        
        # Override the state file path to use the same temporary file
        state_manager_2.state_file_path = Path(temp_state_file)
        state_manager_2.load_state()  # Load the saved state
        
        sp_persisted = state_manager_2.state_data.get("system_progression", {})
        persisted_index = sp_persisted.get("persistent_category_index", -1)
        
        if persisted_index == after5_index:
            print(f"✅ STEP 7 PASSED: State persisted correctly - index: {persisted_index}")
        else:
            print(f"❌ STEP 7 FAILED: Expected persisted index {after5_index}, got {persisted_index}")
            return False
        
        # === FINAL VALIDATION ===
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED! The surgical fix successfully prevents erratic behavior.")
        print("=" * 70)
        print("\n📋 SUMMARY:")
        print("✅ Chunked processing workflow calls do NOT override incremented values")
        print("✅ Category index increments correctly: 0→1→2→3")
        print("✅ State persistence works correctly")
        print("✅ No erratic 0→1→2→0→1→2 behavior observed")
        
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_state_file)
        except:
            pass

def test_edge_cases():
    """Test edge cases that might cause issues."""
    print("\n🧪 EDGE CASE TESTING")
    print("-" * 30)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
        temp_state_file = temp_file.name
    
    try:
        # Test 1: Multiple rapid initialize_category_processing calls
        print("\n🎯 EDGE CASE 1: Multiple rapid initialize_category_processing calls")
        state_manager = FixedEnhancedStateManager(
            supplier_name="test_supplier"
        )
        
        # Set initial value
        state_manager.mark_category_completed("https://example.com/category-1", 0)
        initial = state_manager.state_data.get("system_progression", {}).get("persistent_category_index", 0)
        
        # Multiple rapid calls with different indexes
        for i in range(5):
            state_manager.initialize_category_processing(
                category_index=i * 10,  # Various batch-calculated indexes
                category_url=f"https://example.com/category-{i+2}",
                total_categories=10
            )
        
        final = state_manager.state_data.get("system_progression", {}).get("persistent_category_index", 0)
        
        if final == initial:
            print("✅ EDGE CASE 1 PASSED: Multiple rapid calls preserved value")
        else:
            print(f"❌ EDGE CASE 1 FAILED: Expected {initial}, got {final}")
            return False
            
        print("✅ All edge cases passed!")
        return True
        
    except Exception as e:
        print(f"❌ EDGE CASE FAILED: {e}")
        return False
    
    finally:
        try:
            os.unlink(temp_state_file)
        except:
            pass

if __name__ == "__main__":
    print("🔧 COMPREHENSIVE TEST SUITE: Erratic Category Index Behavior Fix")
    print("=" * 80)
    print("This test suite validates the surgical fix that prevents 0→1→2→0→1→2 behavior")
    print("caused by chunked processing workflow calls to initialize_category_processing()")
    print("=" * 80)
    
    # Run comprehensive test
    main_test_passed = test_chunked_processing_fix()
    
    # Run edge case tests
    edge_test_passed = test_edge_cases()
    
    print("\n" + "=" * 80)
    if main_test_passed and edge_test_passed:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
        print("✅ The erratic 0→1→2→0→1→2 behavior has been eliminated.")
        print("✅ Category index will now increment properly: 0→1→2→3→4...")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! The fix needs additional work.")
        sys.exit(1)