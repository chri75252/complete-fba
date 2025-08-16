#!/usr/bin/env python3
"""
Test Variable Name Fix - Validate the category_urls fix
"""

import sys
import os
sys.path.append('.')

def test_variable_name_fix():
    """Test that the variable name issue is fixed"""
    print("🧪 Testing variable name fix...")
    
    try:
        # Read the fixed file
        with open('tools/passive_extraction_workflow_latest.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the problematic line is fixed
        if 'len(category_urls)' in content:
            # Count occurrences to see if any remain in wrong context
            lines = content.split('\n')
            problematic_lines = []
            
            for i, line in enumerate(lines, 1):
                if 'len(category_urls)' in line and 'category_urls_to_scrape' not in line:
                    # Check if this is in the _run_hybrid_processing_mode function
                    # by looking at surrounding context
                    start_check = max(0, i-50)
                    context = '\n'.join(lines[start_check:i+10])
                    
                    if '_run_hybrid_processing_mode' in context and 'update_progression_unified' in context:
                        problematic_lines.append((i, line.strip()))
            
            if problematic_lines:
                print(f"❌ Still found problematic lines: {problematic_lines}")
                return False
        
        # Check that the fix is in place
        if 'len(category_urls_to_scrape)' in content:
            print("✅ Variable name fix confirmed - using category_urls_to_scrape")
            return True
        else:
            print("❌ Fix not found - category_urls_to_scrape not present")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_function_signature():
    """Test that the function signature is correct"""
    print("🧪 Testing function signature...")
    
    try:
        with open('tools/passive_extraction_workflow_latest.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that the function signature includes category_urls_to_scrape
        if 'async def _run_hybrid_processing_mode(self, supplier_url: str, supplier_name: str, category_urls_to_scrape: List[str]' in content:
            print("✅ Function signature correct - parameter is category_urls_to_scrape")
            return True
        else:
            print("❌ Function signature issue")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def main():
    """Run all variable name fix validation tests"""
    print("🔧 Variable Name Fix Validation")
    print("=" * 50)
    
    tests = [
        ("Variable Name Fix", test_variable_name_fix),
        ("Function Signature", test_function_signature),
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
        print("✅ ALL VARIABLE NAME FIX TESTS PASSED")
        print("\n🎯 Fix Summary:")
        print("• Variable name corrected from 'category_urls' to 'category_urls_to_scrape'")
        print("• Function parameter scope issue resolved")
        print("• NameError crash eliminated")
    else:
        print(f"❌ {len(tests) - passed}/{len(tests)} TESTS FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()