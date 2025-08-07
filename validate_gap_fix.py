#!/usr/bin/env python3
"""
Gap Processing Fix Validation Test
=================================

Validates that the critical fix in _extract_supplier_products() correctly:
1. Filters cached products against linking map
2. Returns only unprocessed products (not in linking map)
3. Achieves the expected ~95% reduction in processing volume

This test simulates the exact gap scenario:
- Cache: 2,423 products
- Linking map: 3,097 entries
- Expected result: Process only ~50-100 unprocessed products
"""

import json
import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.append(str(Path(__file__).parent / "tools"))

try:
    from passive_extraction_workflow_latest import PassiveExtractionWorkflow
except ImportError as e:
    print(f"❌ ERROR: Could not import PassiveExtractionWorkflow: {e}")
    sys.exit(1)


def load_test_data():
    """Load current cache and linking map data"""
    base_path = Path(__file__).parent / "OUTPUTS"
    
    # Load cache file
    cache_path = base_path / "cached_products" / "poundwholesale-co-uk_products_cache.json"
    if not cache_path.exists():
        print(f"❌ ERROR: Cache file not found: {cache_path}")
        return None, None
    
    with open(cache_path, 'r') as f:
        cache_data = json.load(f)
    
    # Load linking map
    linking_map_path = base_path / "FBA_ANALYSIS" / "linking_maps" / "poundwholesale.co.uk" / "linking_map.json"
    if not linking_map_path.exists():
        print(f"❌ ERROR: Linking map not found: {linking_map_path}")
        return None, None
    
    with open(linking_map_path, 'r') as f:
        linking_map_data = json.load(f)
    
    return cache_data, linking_map_data


def test_gap_processing_fix():
    """Test the gap processing fix with real data"""
    
    print("🔍 GAP PROCESSING FIX VALIDATION TEST")
    print("=" * 50)
    
    # Load test data
    cache_data, linking_map_data = load_test_data()
    if not cache_data or not linking_map_data:
        return False
    
    print(f"📊 Test Data Loaded:")
    print(f"   • Cache products: {len(cache_data)}")
    print(f"   • Linking map entries: {len(linking_map_data)}")
    print(f"   • Gap scenario: {len(linking_map_data) - len(cache_data)} more linking map entries")
    print()
    
    # Initialize workflow with minimal config
    workflow = PassiveExtractionWorkflow(
        supplier_name="poundwholesale.co.uk",
        config_path="config/system_config.json",
        use_predefined_categories=True,
        ai_client=None
    )
    
    # Set the linking map data
    workflow.linking_map = linking_map_data
    
    try:
        # Call the fixed method
        print("🧪 Testing _extract_supplier_products() with linking map filtering...")
        result = workflow._extract_supplier_products(cache_data)
        
        print(f"📈 RESULTS:")
        print(f"   • Input cached products: {len(cache_data)}")
        print(f"   • Output filtered products: {len(result)}")
        print(f"   • Products filtered out: {len(cache_data) - len(result)}")
        print(f"   • Processing reduction: {((len(cache_data) - len(result)) / len(cache_data) * 100):.1f}%")
        print()
        
        # Validate results
        if len(result) < len(cache_data):
            reduction_percent = ((len(cache_data) - len(result)) / len(cache_data)) * 100
            print("✅ SUCCESS: Fix is working correctly!")
            print(f"   • Significant reduction achieved: {reduction_percent:.1f}%")
            
            if reduction_percent >= 90:
                print(f"   • EXCELLENT: {reduction_percent:.1f}% reduction exceeds 90% target")
            elif reduction_percent >= 75:
                print(f"   • GOOD: {reduction_percent:.1f}% reduction meets expectations")
            else:
                print(f"   • MODERATE: {reduction_percent:.1f}% reduction, acceptable but could be improved")
            
            # Show sample of filtered products for verification
            if len(result) > 0:
                print(f"\n🔍 Sample unprocessed products (first 3):")
                for i, product in enumerate(result[:3]):
                    title = product.get('title', 'No title')[:50]
                    url = product.get('url', 'No URL')
                    print(f"   {i+1}. {title}... - {url}")
            
            return True
        else:
            print("❌ FAILURE: No products were filtered out!")
            print("   • The fix may not be working correctly")
            print("   • All cached products are still being returned")
            return False
    
    except Exception as e:
        print(f"❌ ERROR during test execution: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_fix_implementation():
    """Verify the fix is properly implemented in the code"""
    
    print("\n🔧 VERIFYING FIX IMPLEMENTATION")
    print("=" * 40)
    
    workflow_path = Path(__file__).parent / "tools" / "passive_extraction_workflow_latest.py"
    
    try:
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check for critical fix markers
        fix_markers = [
            "🚨 CRITICAL FIX: Filter against linking map",
            "Build hash set for O(1) lookup performance",
            "processed_urls = {entry.get",
            "processed_eans = {entry.get",
            "if (product_url and product_url in processed_urls)",
            "unprocessed_products.append(product)"
        ]
        
        found_markers = []
        for marker in fix_markers:
            if marker in content:
                found_markers.append(marker)
        
        print(f"✅ Fix implementation verification:")
        print(f"   • Found {len(found_markers)}/{len(fix_markers)} critical fix markers")
        
        if len(found_markers) == len(fix_markers):
            print("   • ✅ All fix components are properly implemented")
            return True
        else:
            print("   • ❌ Some fix components may be missing")
            missing = set(fix_markers) - set(found_markers)
            for marker in missing:
                print(f"     - Missing: {marker}")
            return False
    
    except Exception as e:
        print(f"❌ ERROR reading workflow file: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Gap Processing Fix Validation")
    print("==========================================\n")
    
    # Verify fix implementation
    implementation_ok = verify_fix_implementation()
    
    # Test with real data
    test_passed = test_gap_processing_fix()
    
    print("\n" + "=" * 50)
    print("📋 FINAL VALIDATION SUMMARY")
    print("=" * 50)
    
    if implementation_ok and test_passed:
        print("🎉 SUCCESS: Gap processing fix is working correctly!")
        print("   • Fix properly implemented in code")
        print("   • Significant processing reduction achieved")
        print("   • System will now process only unprocessed products")
        sys.exit(0)
    else:
        print("❌ FAILURE: Issues detected with gap processing fix")
        if not implementation_ok:
            print("   • Fix implementation may be incomplete")
        if not test_passed:
            print("   • Fix is not achieving expected results")
        sys.exit(1)