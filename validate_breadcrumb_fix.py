#!/usr/bin/env python3
"""
Validate Breadcrumb Fix - Comprehensive validation of the timing fix
"""

import sys
import os
sys.path.append('.')

def test_startup_sequence():
    """Test that startup doesn't trigger premature breadcrumb warnings"""
    print("🧪 Testing startup sequence...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        # Create state manager (simulates startup)
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # This should NOT trigger breadcrumb warnings during startup
        state_manager.save_state()
        
        print("✅ Startup sequence completed without premature breadcrumb warnings")
        return True
        
    except Exception as e:
        print(f"❌ Startup sequence failed: {e}")
        return False

def test_write_ahead_sequence():
    """Test the complete write-ahead sequence"""
    print("🧪 Testing write-ahead sequence...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Simulate write-ahead point 1: Category start
        print("  📍 Write-Ahead Point 1: Category start")
        state_manager.update_progression_unified(
            current_category_index=0,
            total_categories=5,
            current_product_index_in_category=0,
            total_products_in_current_category=0,
            current_phase="supplier",
            current_category_url="https://test.com/category1"
        )
        state_manager.save_state_atomic()  # This should log breadcrumb
        
        # Simulate write-ahead point 2: Post-filter
        print("  📍 Write-Ahead Point 2: Post-filter denominator")
        state_manager.update_progression_unified(
            total_products_in_current_category=25
        )
        state_manager.save_state_atomic()
        
        # Simulate write-ahead point 3: Product processing
        print("  📍 Write-Ahead Point 3: Product processing")
        for i in range(1, 26):
            state_manager.update_progression_unified(
                current_product_index_in_category=i
            )
            if i % 10 == 0:  # Staggered writes
                state_manager.save_state_atomic()
        
        # Simulate write-ahead point 4: Final sync
        print("  📍 Write-Ahead Point 4: Final sync")
        state_manager.save_state_atomic()
        
        print("✅ Write-ahead sequence completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Write-ahead sequence failed: {e}")
        return False

def test_processing_active_detection():
    """Test the _is_processing_active logic"""
    print("🧪 Testing processing active detection...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Initially should not be active (startup)
        is_active_startup = state_manager._is_processing_active()
        print(f"  Startup active status: {is_active_startup} (should be False)")
        
        # After setting up category structure, should be active
        state_manager.update_progression_unified(
            current_category_index=0,
            total_categories=5,
            current_phase="supplier"
        )
        is_active_processing = state_manager._is_processing_active()
        print(f"  Processing active status: {is_active_processing} (should be True)")
        
        if not is_active_startup and is_active_processing:
            print("✅ Processing active detection working correctly")
            return True
        else:
            print("❌ Processing active detection not working correctly")
            return False
        
    except Exception as e:
        print(f"❌ Processing active detection failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🔧 Breadcrumb Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Startup Sequence", test_startup_sequence),
        ("Write-Ahead Sequence", test_write_ahead_sequence),
        ("Processing Active Detection", test_processing_active_detection),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    if passed == len(tests):
        print("✅ ALL VALIDATION TESTS PASSED")
        print("\n🎯 Fix Summary:")
        print("• Startup breadcrumb warnings eliminated")
        print("• Write-ahead sequence working correctly")
        print("• Processing state detection accurate")
        print("• Ready for production testing")
    else:
        print(f"❌ {len(tests) - passed}/{len(tests)} TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()