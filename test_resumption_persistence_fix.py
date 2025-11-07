"""
Test script to verify that per-category progress indices persist between runs.
This test simulates the exact scenario where the system is interrupted and resumed.
"""

import json
import os
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from fixed_enhanced_state_manager import FixedEnhancedStateManager


def test_resumption_persistence():
    """
    Test the core resumption persistence issue that the user reported.
    
    According to user specification:
    - persistent_category_index should NEVER reset (across all runs)
    - supplier_products_completed should persist between runs within same category
    - amazon_products_completed should persist between runs within same category
    """
    
    print("🧪 TESTING RESUMPTION PERSISTENCE FIX")
    print("=" * 60)
    
    # Setup test state file
    test_state_file = Path(__file__).parent / "test_resumption_state.json"
    if test_state_file.exists():
        test_state_file.unlink()
    
    # === SIMULATION 1: First run - make progress ===
    print("\n1️⃣ SIMULATION: First run - make progress")
    
    state_manager = FixedEnhancedStateManager("test_supplier", str(test_state_file.parent))
    
    # Initialize category processing (first time)
    category_url = "https://example.com/category/electronics"
    state_manager.initialize_category_processing(
        category_index=14,
        category_url=category_url,
        total_categories=100
    )
    
    # Set some denominators
    sp = state_manager.state_data["system_progression"]
    sp["supplier_products_needing_extraction"] = 85
    sp["amazon_products_needing_analysis"] = 120
    
    # Make some progress in supplier phase
    sp["supplier_products_completed"] = 50
    state_manager.save_state_atomic()
    
    # Switch to Amazon phase and make progress
    state_manager.commit_phase_switch(new_phase="amazon_analysis", reset_index=False)
    sp = state_manager.state_data["system_progression"]
    sp["amazon_products_completed"] = 30
    state_manager.save_state_atomic()
    
    print(f"   📊 After first run:")
    print(f"      persistent_category_index: {sp['persistent_category_index']}")
    print(f"      supplier_products_completed: {sp['supplier_products_completed']}")
    print(f"      amazon_products_completed: {sp['amazon_products_completed']}")
    
    # Store values for comparison
    expected_category_index = sp["persistent_category_index"]
    expected_supplier_completed = sp["supplier_products_completed"]
    expected_amazon_completed = sp["amazon_products_completed"]
    
    # Save final state to disk before creating new manager
    print(f"   💾 Saving final state to disk...")
    state_manager.save_state_atomic()
    
    # Debug: Check what's actually in the file
    state_file_actual = state_manager.state_file_path
    print(f"   🗂️ State file: {state_file_actual}")
    with open(state_file_actual, 'r') as f:
        saved_data = json.load(f)
        saved_sp = saved_data.get('system_progression', {})
        print(f"   📁 File contents after first run:")
        print(f"      persistent_category_index: {saved_sp.get('persistent_category_index')}")
        print(f"      supplier_products_completed: {saved_sp.get('supplier_products_completed')}")
        print(f"      amazon_products_completed: {saved_sp.get('amazon_products_completed')}")
    
    # === SIMULATION 2: System restart (interruption/resumption) ===
    print("\n2️⃣ SIMULATION: System restart (interruption/resumption)")
    
    # Create new state manager instance (simulates system restart)
    del state_manager
    state_manager = FixedEnhancedStateManager("test_supplier", str(test_state_file.parent))
    
    # Perform startup analysis (what happens during system startup)
    state_manager.perform_startup_analysis()
    
    # The key test: initialize_category_processing for SAME category
    # This should PRESERVE existing progress, not reset it
    print(f"   🔍 Before initialize_category_processing:")
    sp_before = state_manager.state_data["system_progression"]
    print(f"      current_category_url: '{sp_before.get('current_category_url', 'NONE')}'")
    print(f"      supplier_products_completed: {sp_before.get('supplier_products_completed', 0)}")
    print(f"      amazon_products_completed: {sp_before.get('amazon_products_completed', 0)}")
    
    state_manager.initialize_category_processing(
        category_index=14,  # Same category
        category_url=category_url,  # Same URL
        total_categories=100
    )
    
    sp = state_manager.state_data["system_progression"]
    
    print(f"   📊 After resumption:")
    print(f"      persistent_category_index: {sp['persistent_category_index']}")
    print(f"      supplier_products_completed: {sp['supplier_products_completed']}")
    print(f"      amazon_products_completed: {sp['amazon_products_completed']}")
    
    # === VERIFICATION ===
    print("\n✅ VERIFICATION:")
    
    success = True
    
    # Test 1: persistent_category_index should remain the same
    if sp["persistent_category_index"] != expected_category_index:
        print(f"   ❌ FAILED: persistent_category_index changed from {expected_category_index} to {sp['persistent_category_index']}")
        success = False
    else:
        print(f"   ✅ PASS: persistent_category_index preserved ({sp['persistent_category_index']})")
    
    # Test 2: supplier_products_completed should persist
    if sp["supplier_products_completed"] != expected_supplier_completed:
        print(f"   ❌ FAILED: supplier_products_completed reset from {expected_supplier_completed} to {sp['supplier_products_completed']}")
        success = False
    else:
        print(f"   ✅ PASS: supplier_products_completed preserved ({sp['supplier_products_completed']})")
    
    # Test 3: amazon_products_completed should persist
    if sp["amazon_products_completed"] != expected_amazon_completed:
        print(f"   ❌ FAILED: amazon_products_completed reset from {expected_amazon_completed} to {sp['amazon_products_completed']}")
        success = False
    else:
        print(f"   ✅ PASS: amazon_products_completed preserved ({sp['amazon_products_completed']})")
    
    # === SIMULATION 3: New category (should reset per-category counters) ===
    print("\n3️⃣ SIMULATION: New category (should reset per-category counters)")
    
    new_category_url = "https://example.com/category/books"
    state_manager.initialize_category_processing(
        category_index=15,  # New category
        category_url=new_category_url,  # Different URL
        total_categories=100
    )
    
    sp = state_manager.state_data["system_progression"]
    
    print(f"   📊 After new category:")
    print(f"      persistent_category_index: {sp['persistent_category_index']}")
    print(f"      supplier_products_completed: {sp['supplier_products_completed']}")
    print(f"      amazon_products_completed: {sp['amazon_products_completed']}")
    
    # Test 4: persistent_category_index should advance
    if sp["persistent_category_index"] != 15:
        print(f"   ❌ FAILED: persistent_category_index should advance to 15, got {sp['persistent_category_index']}")
        success = False
    else:
        print(f"   ✅ PASS: persistent_category_index advanced to new category ({sp['persistent_category_index']})")
    
    # Test 5: per-category counters should reset for new category
    if sp["supplier_products_completed"] != 0:
        print(f"   ❌ FAILED: supplier_products_completed should reset to 0 for new category, got {sp['supplier_products_completed']}")
        success = False
    else:
        print(f"   ✅ PASS: supplier_products_completed reset for new category ({sp['supplier_products_completed']})")
    
    if sp["amazon_products_completed"] != 0:
        print(f"   ❌ FAILED: amazon_products_completed should reset to 0 for new category, got {sp['amazon_products_completed']}")
        success = False
    else:
        print(f"   ✅ PASS: amazon_products_completed reset for new category ({sp['amazon_products_completed']})")
    
    # Cleanup
    try:
        # Use the actual state file path from the manager
        actual_state_file = Path(state_manager.state_file_path)
        if actual_state_file.exists():
            actual_state_file.unlink()
    except Exception as e:
        print(f"   ⚠️ Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Resumption persistence is working correctly.")
    else:
        print("💥 TESTS FAILED! Resumption persistence is still broken.")
    
    return success


if __name__ == "__main__":
    test_resumption_persistence()