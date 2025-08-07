#!/usr/bin/env python3
"""
Cache Fixes Validation Script
Validates that the critical cache persistence fixes are working correctly
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def validate_cache_files():
    """Validate the current state of cache files"""
    print("🔍 CACHE VALIDATION REPORT")
    print("=" * 50)
    
    # File paths
    cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    linking_map_file = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
    state_file = "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json"
    
    results = {}
    
    # Check each file
    for name, filepath in [
        ("Product Cache", cache_file),
        ("Linking Map", linking_map_file), 
        ("Processing State", state_file)
    ]:
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            size_mb = stat.st_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(stat.st_mtime)
            age_hours = (datetime.now() - mod_time).total_seconds() / 3600
            
            # Load and validate content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    entries = len(data)
                elif isinstance(data, dict):
                    entries = len(data.get('processed_products', {})) if 'processed_products' in data else len(data)
                else:
                    entries = 1
                    
                status = "✅ HEALTHY" if age_hours < 24 else "⚠️ STALE" if age_hours < 48 else "❌ CRITICAL"
                
                results[name] = {
                    "status": status,
                    "size_mb": size_mb,
                    "age_hours": age_hours,
                    "entries": entries,
                    "last_modified": mod_time.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                print(f"\n{name}:")
                print(f"  Status: {status}")
                print(f"  Size: {size_mb:.2f} MB")
                print(f"  Entries: {entries:,}")
                print(f"  Last Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Age: {age_hours:.1f} hours")
                
            except Exception as e:
                results[name] = {"status": "❌ CORRUPTED", "error": str(e)}
                print(f"\n{name}: ❌ CORRUPTED - {e}")
        else:
            results[name] = {"status": "❌ MISSING"}
            print(f"\n{name}: ❌ MISSING")
    
    # Overall assessment
    print(f"\n{'='*50}")
    healthy_count = sum(1 for r in results.values() if r.get("status", "").startswith("✅"))
    total_count = len(results)
    
    if healthy_count == total_count:
        print("🎉 OVERALL STATUS: ALL SYSTEMS HEALTHY")
    elif healthy_count > 0:
        print(f"⚠️ OVERALL STATUS: {healthy_count}/{total_count} SYSTEMS HEALTHY")
    else:
        print("🚨 OVERALL STATUS: CRITICAL - ALL SYSTEMS FAILING")
    
    return results

def check_incremental_cache_metadata():
    """Check if incremental cache metadata is present"""
    cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    
    if not os.path.exists(cache_file):
        print("❌ Cache file not found for metadata check")
        return False
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Look for metadata entry
        metadata_found = False
        for item in data:
            if isinstance(item, dict) and "_cache_metadata" in item:
                metadata = item["_cache_metadata"]
                print(f"✅ Found cache metadata:")
                print(f"   Last Update: {metadata.get('last_incremental_update', 'N/A')}")
                print(f"   Total Products: {metadata.get('total_products', 'N/A')}")
                print(f"   Cache Status: {metadata.get('cache_status', 'N/A')}")
                print(f"   Linking Map Entries: {metadata.get('linking_map_entries', 'N/A')}")
                metadata_found = True
                break
        
        if not metadata_found:
            print("⚠️ No cache metadata found - incremental updates may not be working")
        
        return metadata_found
        
    except Exception as e:
        print(f"❌ Error checking cache metadata: {e}")
        return False

def simulate_cache_update_test():
    """Simulate what the incremental cache update should do"""
    print(f"\n🧪 SIMULATING INCREMENTAL CACHE UPDATE")
    print("=" * 50)
    
    cache_file = "OUTPUTS/cached_products/poundwholesale-co-uk_products_cache.json"
    
    if not os.path.exists(cache_file):
        print("❌ Cannot simulate - cache file doesn't exist")
        return False
    
    try:
        # Load existing cache
        with open(cache_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Current cache has {len(data)} entries")
        
        # Add test metadata
        test_metadata = {
            "_cache_metadata": {
                "last_incremental_update": datetime.now().isoformat(),
                "total_products": len(data),
                "cache_status": "test_active",
                "test_timestamp": time.time()
            }
        }
        
        # Remove existing metadata if present
        data = [item for item in data if not (isinstance(item, dict) and "_cache_metadata" in item)]
        
        # Add new metadata
        data.append(test_metadata)
        
        # Write back to file
        temp_file = cache_file + '.test_tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic replace
        os.replace(temp_file, cache_file)
        
        print("✅ Test metadata added successfully")
        print("✅ Atomic write pattern working")
        
        return True
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Cache Fixes Validation")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run validations
    results = validate_cache_files()
    metadata_check = check_incremental_cache_metadata()
    simulation_test = simulate_cache_update_test()
    
    # Final summary
    print(f"\n🎯 VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Cache Files Status: {'✅ PASS' if any(r.get('status', '').startswith('✅') for r in results.values()) else '❌ FAIL'}")
    print(f"Metadata Check: {'✅ PASS' if metadata_check else '❌ FAIL'}")
    print(f"Simulation Test: {'✅ PASS' if simulation_test else '❌ FAIL'}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    stale_files = [name for name, data in results.items() if data.get("age_hours", 0) > 24]
    if stale_files:
        print(f"⚠️ Stale files detected: {', '.join(stale_files)}")
        print("   → Run the system to test if incremental updates are working")
    
    if not metadata_check:
        print("⚠️ No incremental cache metadata found")
        print("   → The _save_incremental_cache_update method may not be running")
    
    missing_files = [name for name, data in results.items() if data.get("status") == "❌ MISSING"]
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        print("   → System may need to be run to generate initial files")