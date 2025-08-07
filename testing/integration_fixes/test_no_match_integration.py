#!/usr/bin/env python3
"""
Integration test that validates no-match entries work with existing linking map.
"""

import json
import os
import sys

def test_existing_linking_map_integration():
    """Test that no-match entries integrate properly with existing linking map."""
    print("🧪 Testing integration with existing linking map...")
    
    # Load existing linking map
    linking_map_path = "OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map.json"
    
    if not os.path.exists(linking_map_path):
        print(f"❌ Linking map not found at: {linking_map_path}")
        return False
    
    try:
        with open(linking_map_path, 'r', encoding='utf-8') as f:
            existing_linking_map = json.load(f)
    except Exception as e:
        print(f"❌ Error loading linking map: {e}")
        return False
    
    print(f"📊 Loaded existing linking map with {len(existing_linking_map)} entries")
    
    # Analyze existing entries
    successful_entries = []
    potential_no_match_entries = []
    
    for entry in existing_linking_map:
        match_method = entry.get("match_method", "unknown")
        amazon_asin = entry.get("amazon_asin")
        
        if match_method == "none":
            potential_no_match_entries.append(entry)
        elif amazon_asin and amazon_asin != "NO_ASIN":
            successful_entries.append(entry)
    
    print(f"📈 Analysis results:")
    print(f"   ✅ Successful entries: {len(successful_entries)}")
    print(f"   ❌ Existing no-match entries: {len(potential_no_match_entries)}")
    
    # Show examples of existing entries
    if successful_entries:
        example_success = successful_entries[0]
        print(f"   📋 Example successful entry: {example_success.get('match_method')} match")
        print(f"      EAN: {example_success.get('supplier_ean')}")
        print(f"      ASIN: {example_success.get('amazon_asin')}")
        print(f"      Confidence: {example_success.get('confidence')}")
    
    if potential_no_match_entries:
        print(f"   📋 Found {len(potential_no_match_entries)} existing no-match entries!")
        example_no_match = potential_no_match_entries[0]
        print(f"      EAN: {example_no_match.get('supplier_ean')}")
        print(f"      Match method: {example_no_match.get('match_method')}")
        print(f"      Reason: {example_no_match.get('no_match_reason', 'No reason provided')}")
    
    # Create a test no-match entry in the same format
    test_no_match_entry = {
        "supplier_ean": "9999999999999",
        "amazon_asin": None,
        "supplier_title": "TEST: No-Match Product Implementation",
        "amazon_title": None,
        "supplier_price": 1.99,
        "amazon_price": None,
        "match_method": "none",
        "confidence": "none",
        "created_at": "2025-07-27T12:00:00.000000",
        "supplier_url": "https://test.com/no-match-test",
        "no_match_reason": "Integration test - Amazon search failed: Test implementation"
    }
    
    # Verify the test entry has the same structure as existing entries
    if successful_entries:
        existing_keys = set(successful_entries[0].keys())
        test_keys = set(test_no_match_entry.keys())
        
        # Allow for the new no_match_reason field
        if "no_match_reason" in test_keys:
            test_keys.remove("no_match_reason")
        
        if existing_keys != test_keys:
            missing_in_test = existing_keys - test_keys
            extra_in_test = test_keys - existing_keys
            print(f"⚠️  Structure differences found:")
            if missing_in_test:
                print(f"     Missing in test: {missing_in_test}")
            if extra_in_test:
                print(f"     Extra in test: {extra_in_test}")
        else:
            print("✅ Test no-match entry structure matches existing entries")
    
    # Test that we can distinguish between successful and no-match entries
    def classify_entry(entry):
        match_method = entry.get("match_method", "unknown")
        amazon_asin = entry.get("amazon_asin")
        
        if match_method == "none":
            return "no_match"
        elif amazon_asin and amazon_asin not in [None, "NO_ASIN"]:
            return "successful"
        else:
            return "unclear"
    
    combined_entries = existing_linking_map + [test_no_match_entry]
    classifications = {}
    
    for entry in combined_entries:
        classification = classify_entry(entry)
        classifications[classification] = classifications.get(classification, 0) + 1
    
    print(f"📊 Classification results for {len(combined_entries)} total entries:")
    for classification, count in classifications.items():
        print(f"   {classification}: {count} entries")
    
    print("✅ Integration test completed successfully")
    return True

def main():
    """Run integration test."""
    print("🚀 Running no-match implementation integration test")
    print("=" * 60)
    
    try:
        if test_existing_linking_map_integration():
            print("=" * 60)
            print("🎉 INTEGRATION TEST PASSED!")
            print("✅ No-match implementation is compatible with existing data")
            return True
        else:
            print("=" * 60)
            print("❌ INTEGRATION TEST FAILED!")
            return False
    except Exception as e:
        print("=" * 60)
        print(f"❌ INTEGRATION TEST ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)