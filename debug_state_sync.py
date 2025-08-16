#!/usr/bin/env python3
"""
Debug State Synchronization - Check what's actually being stored
"""

import sys
import os
sys.path.append('.')

def debug_state_sync():
    """Debug the state synchronization issue"""
    print("🔍 Debugging State Synchronization")
    print("=" * 50)
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        state_manager = FixedEnhancedStateManager("debug_test")
        
        print("📊 Initial state:")
        sp = state_manager.state_data.get("system_progression", {})
        print(f"  system_progression: {sp}")
        
        print("\n📝 Calling update_progression_unified...")
        state_manager.update_progression_unified(
            current_category_index=0,
            total_categories=5,
            current_product_index_in_category=0,
            total_products_in_current_category=0,
            current_phase="supplier",
            current_category_url="https://test.com/category1"
        )
        
        print("📊 After update:")
        sp = state_manager.state_data.get("system_progression", {})
        sep = state_manager.state_data.get("supplier_extraction_progress", {})
        print(f"  system_progression: {sp}")
        print(f"  supplier_extraction_progress: {sep}")
        
        print("\n🔍 Checking required fields:")
        required_fields = [
            "current_category_index",
            "total_categories", 
            "current_product_index_in_category",
            "total_products_in_current_category",
            "current_phase"
        ]
        
        for field in required_fields:
            sp_value = sp.get(field)
            sep_value = sep.get(field)
            print(f"  {field}: SP={sp_value}, SEP={sep_value}")
        
        print("\n🧪 Testing breadcrumb logging:")
        state_manager.log_breadcrumb_guarded()
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_state_sync()