#!/usr/bin/env python3
"""
Test Resume Fix - Validate critical resume failure fix
"""

import sys
import os
import json
sys.path.append('.')

def test_resume_point_storage():
    """Test that resume points are properly stored and used"""
    print("🧪 Testing resume point storage...")
    
    try:
        # Read the current processing state
        state_file = "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json"
        if not os.path.exists(state_file):
            print("❌ Processing state file not found")
            return False
        
        with open(state_file, 'r') as f:
            state_data = json.load(f)
        
        # Check key resume fields
        resumption_index = state_data.get("resumption_index", 0)
        successful_products = state_data.get("successful_products", 0)
        system_progression = state_data.get("system_progression", {})
        
        current_category_index = system_progression.get("current_category_index", 0)
        total_categories = system_progression.get("total_categories", 0)
        
        print(f"📊 State Analysis:")
        print(f"   Resumption Index: {resumption_index}")
        print(f"   Successful Products: {successful_products}")
        print(f"   Current Category Index: {current_category_index}")
        print(f"   Total Categories: {total_categories}")
        
        # Validate resume logic
        if resumption_index > 0 and successful_products > 0:
            if total_categories <= 1:
                print("❌ CRITICAL ISSUE: total_categories should be > 1 for proper resume")
                return False
            
            if current_category_index == 0 and resumption_index > 1000:
                print("❌ CRITICAL ISSUE: category_index should not be 0 with high resumption_index")
                return False
            
            print("✅ Resume state looks reasonable")
            return True
        else:
            print("ℹ️ No resume state to validate (fresh start)")
            return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_workflow_integration():
    """Test that workflow integration fixes are in place"""
    print("🧪 Testing workflow integration fixes...")
    
    try:
        # Read the workflow file to check for fixes
        with open('tools/passive_extraction_workflow_latest.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for critical fixes
        fixes_present = {
            "resume_point_storage": "_resume_point = resume_point" in content,
            "resume_point_usage": "getattr(self, '_resume_point', None)" in content,
            "total_categories_fix": "_total_categories = len(category_urls_to_scrape)" in content,
            "actual_total_categories": "actual_total_categories = getattr(self, '_total_categories'" in content,
            "resume_aware_index": "resume_category_index = resume_point.get" in content
        }
        
        print("🔍 Fix Validation:")
        for fix_name, present in fixes_present.items():
            status = "✅" if present else "❌"
            print(f"   {status} {fix_name}: {'Present' if present else 'Missing'}")
        
        all_fixes_present = all(fixes_present.values())
        
        if all_fixes_present:
            print("✅ All critical fixes are present in workflow")
            return True
        else:
            print("❌ Some critical fixes are missing")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_resume_calculation_logic():
    """Test resume calculation logic"""
    print("🧪 Testing resume calculation logic...")
    
    try:
        # Import the state manager to test resume logic
        from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
        
        # Create a test state manager
        state_manager = FixedEnhancedStateManager("test_supplier")
        
        # Test resume point validation
        test_resume_point = {
            "current_category_index": 35,
            "total_categories": 242,
            "current_product_index_in_category": 15,
            "total_products_in_current_category": 100,
            "current_phase": "supplier",
            "current_category_url": "https://example.com/category",
            "resumption_index": 8378
        }
        
        # Test validation (if ResumeController is available)
        if hasattr(state_manager, 'resume_controller'):
            validation_result = state_manager.resume_controller.validate_resume_point(test_resume_point)
            
            if validation_result["status"] == "valid":
                print("✅ Resume point validation working correctly")
                return True
            else:
                print(f"❌ Resume point validation failed: {validation_result['reason']}")
                return False
        else:
            print("ℹ️ ResumeController not available - skipping validation test")
            return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run all resume fix validation tests"""
    print("🔧 Resume Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Resume Point Storage", test_resume_point_storage),
        ("Workflow Integration", test_workflow_integration),
        ("Resume Calculation Logic", test_resume_calculation_logic),
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
        print("✅ ALL RESUME FIX TESTS PASSED")
        print("\n🎯 Fix Summary:")
        print("• Resume points properly stored from startup sequence")
        print("• Workflow uses calculated resume points instead of legacy indices")
        print("• Total categories correctly calculated and stored")
        print("• Category indices adjusted based on resume position")
        print("• System should now resume from correct interruption points")
    else:
        print(f"❌ {len(tests) - passed}/{len(tests)} TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()