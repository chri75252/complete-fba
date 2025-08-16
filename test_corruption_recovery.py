#!/usr/bin/env python3
"""
Test corruption detection and recovery functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_corruption_detection():
    """Test corruption detection on real state"""
    print("🔧 Testing corruption detection...")
    
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    state_manager.load_state()
    
    # Run corruption detection
    corruption_report = state_manager.detect_state_corruption()
    
    print(f"📊 Corruption detected: {corruption_report.get('corrupted', False)}")
    print(f"📋 Issues found: {len(corruption_report.get('issues', []))}")
    
    for issue in corruption_report.get('issues', []):
        print(f"   • {issue}")
    
    sources = corruption_report.get('sources', {})
    for source_name, data in sources.items():
        print(f"📍 {source_name}: index={data.get('index')}, url={data.get('url', '')[:50]}...")
    
    if corruption_report.get('expected'):
        expected = corruption_report['expected']
        print(f"🎯 Expected correction:")
        print(f"   • index: {expected.get('current_category_index')}")
        print(f"   • url: {expected.get('current_category_url', '')[:50]}...")
    
    return corruption_report.get('corrupted', False)

def test_corruption_recovery():
    """Test corruption recovery"""
    print("🔧 Testing corruption recovery...")
    
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    state_manager.load_state()
    
    # Detect corruption
    corruption_report = state_manager.detect_state_corruption()
    
    if corruption_report.get('corrupted'):
        print("🚨 Corruption detected, attempting recovery...")
        
        # Attempt recovery
        recovery_success = state_manager.recover_from_corruption(corruption_report)
        
        if recovery_success:
            print("✅ Recovery successful")
            
            # Verify recovery
            sep = state_manager.state_data.get("supplier_extraction_progress", {})
            sp = state_manager.state_data.get("system_progression", {})
            
            print(f"📊 After recovery:")
            print(f"   • Operational: index={sep.get('current_category_index')}, url={sep.get('current_category_url', '')[:50]}...")
            print(f"   • Tracking: index={sp.get('current_category_index')}, url={sp.get('current_category_url', '')[:50]}...")
            
            # Save corrected state
            state_manager.save_state()
            print("💾 Corrected state saved")
            
            return True
        else:
            print("❌ Recovery failed")
            return False
    else:
        print("ℹ️ No corruption detected")
        return True

def test_corruption_prevention():
    """Test corruption prevention during updates"""
    print("🔧 Testing corruption prevention...")
    
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    state_manager.load_state()
    
    # Set up good operational data
    state_manager.state_data["supplier_extraction_progress"] = {
        "current_category_index": 1,
        "current_category_url": "https://www.poundwholesale.co.uk/seasonal/wholesale-winter-essentials"
    }
    
    # Try to update with corrupted data (should be prevented)
    print("🧪 Attempting to update with corrupted data...")
    state_manager.update_progression_unified(
        current_category_index=0,
        current_category_url="https://www.poundwholesale.co.uk/seasonal/wholesale-halloween"
    )
    
    # Check if corruption was prevented
    sep = state_manager.state_data.get("supplier_extraction_progress", {})
    final_index = sep.get("current_category_index")
    final_url = sep.get("current_category_url", "")
    
    print(f"📊 Final state after update attempt:")
    print(f"   • index: {final_index}")
    print(f"   • url: {final_url[:50]}...")
    
    # Should still have good data (index 1, winter URL)
    if final_index == 1 and "winter-essentials" in final_url:
        print("✅ CORRUPTION PREVENTED: Good data preserved")
        return True
    else:
        print("❌ CORRUPTION NOT PREVENTED: Bad data accepted")
        return False

def main():
    """Run all corruption tests"""
    print("🚨 CORRUPTION DETECTION & RECOVERY TESTS")
    print("=" * 50)
    
    tests = [
        ("Corruption Detection", test_corruption_detection),
        ("Corruption Recovery", test_corruption_recovery),
        ("Corruption Prevention", test_corruption_prevention)
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

if __name__ == "__main__":
    main()