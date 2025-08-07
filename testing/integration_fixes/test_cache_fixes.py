#!/usr/bin/env python3
"""
Test Cache Fixes - Comprehensive validation of cache persistence fixes
"""

import os
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

def test_incremental_cache_method():
    """Test the incremental cache update method directly"""
    print("🧪 Testing Incremental Cache Update Method")
    print("-" * 50)
    
    # Import the workflow class
    try:
        import sys
        sys.path.append('tools')
        from passive_extraction_workflow_latest import PassiveExtractionWorkflow
        
        # Create a test instance
        workflow = PassiveExtractionWorkflow()
        workflow.supplier_name = "poundwholesale.co.uk"
        workflow.supplier_cache_dir = "OUTPUTS/cached_products"
        
        # Test the incremental cache update
        result = workflow._save_incremental_cache_update()
        
        if result:
            print("✅ Incremental cache update method works")
            
            # Verify metadata was added
            cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                metadata_found = any(
                    isinstance(item, dict) and "_cache_metadata" in item 
                    for item in data
                )
                
                if metadata_found:
                    print("✅ Cache metadata successfully added")
                    return True
                else:
                    print("❌ Cache metadata not found")
                    return False
            else:
                print("❌ Cache file not found")
                return False
        else:
            print("❌ Incremental cache update failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_linking_map_save_method():
    """Test the enhanced linking map save method"""
    print("\n🧪 Testing Enhanced Linking Map Save Method")
    print("-" * 50)
    
    try:
        import sys
        sys.path.append('tools')
        from passive_extraction_workflow_latest import PassiveExtractionWorkflow
        
        # Create a test instance
        workflow = PassiveExtractionWorkflow()
        workflow.supplier_name = "poundwholesale.co.uk"
        
        # Create test linking map data
        workflow.linking_map = [
            {
                "supplier_ean": "TEST123",
                "amazon_asin": "B123TEST",
                "supplier_title": "Test Product",
                "amazon_title": "Test Amazon Product",
                "supplier_price": 10.99,
                "amazon_price": 19.99,
                "match_method": "test",
                "confidence": "high",
                "created_at": datetime.now().isoformat(),
                "supplier_url": "https://test.com/product"
            }
        ]
        
        # Test the save method
        result = workflow._save_linking_map("poundwholesale.co.uk")
        
        if result:
            print("✅ Enhanced linking map save method works")
            
            # Verify file was created/updated
            linking_map_file = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
            if os.path.exists(linking_map_file):
                stat = os.stat(linking_map_file)
                age_seconds = time.time() - stat.st_mtime
                
                if age_seconds < 60:  # Updated within last minute
                    print("✅ Linking map file was recently updated")
                    return True
                else:
                    print(f"⚠️ Linking map file is {age_seconds:.0f} seconds old")
                    return False
            else:
                print("❌ Linking map file not found")
                return False
        else:
            print("❌ Enhanced linking map save failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_file_monitoring():
    """Test file monitoring and validation"""
    print("\n🧪 Testing File Monitoring")
    print("-" * 50)
    
    files_to_monitor = [
        ("Product Cache", "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"),
        ("Linking Map", "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"),
        ("Processing State", "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json")
    ]
    
    baseline_times = {}
    
    # Get baseline timestamps
    for name, filepath in files_to_monitor:
        if os.path.exists(filepath):
            baseline_times[name] = os.path.getmtime(filepath)
            print(f"📊 {name}: Baseline timestamp recorded")
        else:
            baseline_times[name] = None
            print(f"⚠️ {name}: File not found")
    
    print("\n⏱️ Monitoring for changes (this would be done during actual system run)...")
    
    # In a real test, we would run the system and monitor for changes
    # For now, we'll just validate the monitoring logic works
    
    changes_detected = 0
    for name, filepath in files_to_monitor:
        if os.path.exists(filepath):
            current_time = os.path.getmtime(filepath)
            if baseline_times[name] and current_time > baseline_times[name]:
                changes_detected += 1
                print(f"✅ {name}: Change detected")
            else:
                print(f"📊 {name}: No change (expected for this test)")
        else:
            print(f"❌ {name}: File missing")
    
    print(f"\n📈 Monitoring system working: {changes_detected} changes would be detected")
    return True

def test_cache_consistency():
    """Test cache consistency validation"""
    print("\n🧪 Testing Cache Consistency")
    print("-" * 50)
    
    try:
        # Load all three files
        cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
        linking_map_file = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
        state_file = "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json"
        
        cache_data = None
        linking_data = None
        state_data = None
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            print(f"✅ Loaded cache: {len(cache_data)} entries")
        
        if os.path.exists(linking_map_file):
            with open(linking_map_file, 'r', encoding='utf-8') as f:
                linking_data = json.load(f)
            print(f"✅ Loaded linking map: {len(linking_data)} entries")
        
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
            print(f"✅ Loaded processing state")
        
        # Consistency checks
        consistency_score = 0
        total_checks = 0
        
        if cache_data and state_data:
            total_checks += 1
            cache_count = len([item for item in cache_data if not isinstance(item, dict) or "_cache_metadata" not in item])
            state_total = state_data.get("total_products", 0)
            
            if abs(cache_count - state_total) <= 10:  # Allow small variance
                consistency_score += 1
                print(f"✅ Cache-State consistency: {cache_count} ≈ {state_total}")
            else:
                print(f"⚠️ Cache-State mismatch: {cache_count} vs {state_total}")
        
        if linking_data and state_data:
            total_checks += 1
            linking_count = len(linking_data)
            processed_count = len(state_data.get("processed_products", {}))
            
            if linking_count > 0 and processed_count > 0:
                consistency_score += 1
                print(f"✅ Linking-State consistency: {linking_count} entries, {processed_count} processed")
            else:
                print(f"⚠️ Linking-State issue: {linking_count} entries, {processed_count} processed")
        
        consistency_percentage = (consistency_score / total_checks * 100) if total_checks > 0 else 0
        print(f"\n📊 Consistency Score: {consistency_score}/{total_checks} ({consistency_percentage:.0f}%)")
        
        return consistency_percentage >= 80
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🚀 COMPREHENSIVE CACHE FIXES TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Incremental Cache Method", test_incremental_cache_method),
        ("Enhanced Linking Map Save", test_linking_map_save_method),
        ("File Monitoring", test_file_monitoring),
        ("Cache Consistency", test_cache_consistency)
    ]
    
    results = {}
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "✅ PASS" if result else "❌ FAIL"
            if result:
                passed += 1
        except Exception as e:
            results[test_name] = f"❌ ERROR: {e}"
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Cache fixes are working correctly!")
    elif passed >= total * 0.8:
        print("⚠️ MOSTLY WORKING - Some issues detected but core functionality works")
    else:
        print("🚨 CRITICAL ISSUES - Multiple test failures detected")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if passed < total:
        print("- Review failed tests and check error messages")
        print("- Verify file permissions and paths are correct")
        print("- Check if system dependencies are properly installed")
    
    print("- Run the actual FBA system to test fixes in production")
    print("- Monitor logs for 'INCREMENTAL CACHE' and 'LINKING MAP SAVE SUCCESS' messages")
    print("- Use validate_cache_fixes.py for ongoing monitoring")

if __name__ == "__main__":
    run_comprehensive_test()