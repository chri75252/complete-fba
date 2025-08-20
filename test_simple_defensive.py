#!/usr/bin/env python3
"""
Simple verification that defensive checks are in place in the actual code
"""

import sys
import os

# Add the tools directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

def test_defensive_code_exists():
    """Test that the defensive code patterns exist in the source file"""
    
    print("🧪 TESTING: Verification of defensive code patterns")
    print("=" * 60)
    
    workflow_file = "tools/passive_extraction_workflow_latest.py"
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test patterns that should exist after our fixes
    tests = [
        {
            "name": "Line 1182 defensive check",
            "pattern": "self.hash_optimizer.add_entry(entry) if self.hash_optimizer else False",
            "description": "Defensive check for add_entry method"
        },
        {
            "name": "Line 2371 defensive check", 
            "pattern": "self.hash_optimizer.get_processed_urls_set() if self.hash_optimizer else set()",
            "description": "Defensive check for get_processed_urls_set method"
        },
        {
            "name": "Line 2533 defensive check",
            "pattern": "if self.hash_optimizer:\n                        self.hash_optimizer.build_indexes(self.linking_map)",
            "description": "Defensive check for build_indexes method"
        },
        {
            "name": "Enhanced hash optimizer logging",
            "pattern": "❌ CRITICAL: HashLookupOptimizer initialization failed:",
            "description": "Enhanced error logging for hash optimizer"
        },
        {
            "name": "Enhanced sentinel monitor logging",
            "pattern": "❌ CRITICAL: SentinelMonitor initialization failed:",
            "description": "Enhanced error logging for sentinel monitor"
        }
    ]
    
    all_passed = True
    
    for test in tests:
        if test["pattern"] in content:
            print(f"✅ FOUND: {test['name']} - {test['description']}")
        else:
            print(f"❌ MISSING: {test['name']} - {test['description']}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL DEFENSIVE PATTERNS VERIFIED: Code contains all expected defensive checks")
        print("\n📋 SUMMARY OF FIXES:")
        print("1. Line 1182: hash_optimizer.add_entry() now returns False if hash_optimizer is None")
        print("2. Line 2371: hash_optimizer.get_processed_urls_set() now returns empty set if None")  
        print("3. Line 2533: hash_optimizer.build_indexes() now skipped if hash_optimizer is None")
        print("4. Enhanced logging with stack traces for initialization failures")
        print("\n✅ RESULT: AttributeError crashes should be eliminated")
        return True
    else:
        print("❌ VERIFICATION FAILED: Some defensive patterns are missing")
        return False

if __name__ == "__main__":
    success = test_defensive_code_exists()
    sys.exit(0 if success else 1)