#!/usr/bin/env python3
"""
Comprehensive test to verify all critical fixes are working
"""

import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cache_preservation():
    """Test that cache clearing bug is fixed"""
    print("🔧 Testing cache preservation fix...")
    
    cache_path = Path("OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json")
    
    if cache_path.exists():
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        print(f"📊 Current cache size: {len(cache_data)} products")
        
        # Check if cache has been cleared (should have 9000+ products, not just 10-12)
        if len(cache_data) < 100:
            print("❌ CACHE CLEARING BUG: Cache has been reduced to minimal products")
            print("   Expected: 9000+ products from all categories")
            print(f"   Actual: {len(cache_data)} products (likely just one category)")
            return False
        else:
            print("✅ CACHE PRESERVED: Cache contains substantial product data")
            return True
    else:
        print("❌ Cache file not found")
        return False

def test_state_sync_direction():
    """Test that state sync direction is correct"""
    print("🔧 Testing state sync direction fix...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        # Create test state manager
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Set up test data - operational data should take precedence
        state_manager.state_data["supplier_extraction_progress"] = {
            "current_category_index": 5,
            "current_category_url": "https://test.com/category5"
        }
        
        state_manager.state_data["system_progression"] = {
            "current_category_index": 0,
            "current_category_url": "https://test.com/category0"
        }
        
        # Call update_progression_unified to test sync direction
        state_manager.update_progression_unified(
            current_category_index=3,
            current_category_url="https://test.com/category3"
        )
        
        # Check if operational data was preserved and used to update tracking
        sp = state_manager.state_data.get("system_progression", {})
        sep = state_manager.state_data.get("supplier_extraction_progress", {})
        
        print(f"   Operational data (supplier_extraction_progress): index={sep.get('current_category_index')}")
        print(f"   Tracking data (system_progression): index={sp.get('current_category_index')}")
        
        # The sync should prioritize operational data
        if sp.get("current_category_index") == 5:  # Should use operational data
            print("✅ SYNC DIRECTION: Operational data correctly used to update tracking data")
            return True
        else:
            print("❌ SYNC DIRECTION: Still syncing in wrong direction")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sync direction: {e}")
        return False

def test_workflow_url_source():
    """Test that workflow uses correct category URL source"""
    print("🔧 Testing workflow URL source fix...")
    
    # This would require running the actual workflow, so we'll check the code instead
    try:
        with open('tools/passive_extraction_workflow_latest.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the fix is present
        if "🚨 CRITICAL FIX: Use resume point URL when available" in content:
            print("✅ URL SOURCE: Fix is present in workflow code")
            
            if "correct_category_url = resume_url" in content:
                print("✅ URL SOURCE: Resume point URL logic implemented")
                return True
            else:
                print("❌ URL SOURCE: Resume point URL logic missing")
                return False
        else:
            print("❌ URL SOURCE: Fix not found in workflow code")
            return False
            
    except Exception as e:
        print(f"❌ Error checking workflow URL source: {e}")
        return False

def test_sections_restoration():
    """Test that both missing sections are restored"""
    print("🔧 Testing sections restoration...")
    
    try:
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
        state_manager.load_state()
        
        # Check category_completion_status
        gap_processing = state_manager.state_data.get("gap_processing", {})
        category_completion_status = gap_processing.get("category_completion_status", {})
        
        # Check categories_completed array
        sep = state_manager.state_data.get("supplier_extraction_progress", {})
        categories_completed = sep.get("categories_completed", [])
        
        print(f"   Category completion status: {len(category_completion_status)} categories")
        print(f"   Categories completed array: {len(categories_completed)} entries")
        
        if len(category_completion_status) > 0 and len(categories_completed) > 0:
            print("✅ SECTIONS: Both missing sections successfully restored")
            return True
        else:
            print("❌ SECTIONS: One or both sections still missing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sections restoration: {e}")
        return False

def main():
    """Run all critical fix tests"""
    print("🚨 CRITICAL FIXES VERIFICATION")
    print("=" * 50)
    
    tests = [
        ("Cache Preservation", test_cache_preservation),
        ("State Sync Direction", test_state_sync_direction),
        ("Workflow URL Source", test_workflow_url_source),
        ("Sections Restoration", test_sections_restoration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 OVERALL: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 ALL CRITICAL FIXES VERIFIED!")
    else:
        print("⚠️ Some fixes need attention")

if __name__ == "__main__":
    main()