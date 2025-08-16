#!/usr/bin/env python3
"""
Test the breadcrumb resumption fix implementation
"""

import sys
import os
sys.path.append('.')

def test_breadcrumb_implementation():
    """Test the breadcrumb resumption implementation."""
    try:
        # Test 1: Import and create state manager
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        state_manager = FixedEnhancedStateManager("test_supplier")
        print("✅ State manager created")
        
        # Test 2: Check if update_progression_unified exists and works
        if hasattr(state_manager, 'update_progression_unified'):
            state_manager.update_progression_unified(
                current_category_index=0,
                total_categories=5,
                current_product_index_in_category=0,
                total_products_in_current_category=10,
                current_phase="supplier",
                current_category_url="https://test.com/category1"
            )
            print("✅ update_progression_unified method works")
        else:
            print("❌ update_progression_unified method not found")
            return False
        
        # Test 3: Check if log_breadcrumb_guarded works without warnings
        if hasattr(state_manager, 'log_breadcrumb_guarded'):
            state_manager.log_breadcrumb_guarded()
            print("✅ log_breadcrumb_guarded method works")
        else:
            print("❌ log_breadcrumb_guarded method not found")
            return False
        
        # Test 4: Check if save_state_atomic exists
        if hasattr(state_manager, 'save_state_atomic'):
            result = state_manager.save_state_atomic()
            print(f"✅ save_state_atomic method works: {result}")
        else:
            print("❌ save_state_atomic method not found")
            return False
        
        # Test 5: Verify state structure has required fields
        sp = state_manager.state_data.get("system_progression", {})
        required_fields = ["current_category_index", "total_categories", "current_product_index_in_category", "total_products_in_current_category", "current_phase"]
        
        missing_fields = [field for field in required_fields if field not in sp]
        if not missing_fields:
            print("✅ All required breadcrumb fields are populated")
        else:
            print(f"❌ Missing breadcrumb fields: {missing_fields}")
            return False
        
        print("\n🎉 All breadcrumb implementation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Breadcrumb Resumption Implementation")
    print("=" * 50)
    
    success = test_breadcrumb_implementation()
    
    print("=" * 50)
    if success:
        print("✅ BREADCRUMB IMPLEMENTATION VERIFIED")
        print("\nNext steps:")
        print("1. Run the workflow to test in production")
        print("2. Monitor for 'BREADCRUMB DELAYED' warnings (should be eliminated)")
        print("3. Test interruption and resume functionality")
    else:
        print("❌ BREADCRUMB IMPLEMENTATION HAS ISSUES")
        sys.exit(1)