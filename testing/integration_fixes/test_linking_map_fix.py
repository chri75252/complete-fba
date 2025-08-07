#!/usr/bin/env python3
"""
Test script for the WSL-compatible linking map save fix
"""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import required modules
from utils.path_manager import get_linking_map_path
from wsl_compatible_save import wsl_compatible_save

def test_linking_map_save():
    """Test the WSL-compatible linking map save functionality"""
    
    print("🔧 Testing WSL-compatible linking map save fix...")
    
    # Create test linking map data similar to actual system
    test_linking_map = [
        {
            "supplier_product_identifier": "EAN_1234567890123",
            "supplier_title_snippet": "Test Product 1",
            "chosen_amazon_asin": "B08XYZ123", 
            "amazon_title_snippet": "Amazon Test Product 1",
            "amazon_ean_on_page": "1234567890123",
            "match_method": "EAN",
            "confidence": "high",
            "supplier_url": "https://www.poundwholesale.co.uk/test-product-1",
            "supplier_price": 1.50,
            "amazon_price": 9.99,
            "created_at": "2025-07-27T10:00:00Z"
        },
        {
            "supplier_product_identifier": "EAN_9876543210987",
            "supplier_title_snippet": "Test Product 2", 
            "chosen_amazon_asin": "B09ABC456",
            "amazon_title_snippet": "Amazon Test Product 2",
            "amazon_ean_on_page": "9876543210987",
            "match_method": "title",
            "confidence": "medium",
            "supplier_url": "https://www.poundwholesale.co.uk/test-product-2",
            "supplier_price": 2.00,
            "amazon_price": 12.99,
            "created_at": "2025-07-27T10:01:00Z"
        },
        {
            "supplier_product_identifier": "EAN_5555666677778",
            "supplier_title_snippet": "Unmatchable Product",
            "chosen_amazon_asin": None,
            "amazon_title_snippet": None,
            "amazon_ean_on_page": None,
            "match_method": "none",
            "confidence": "none",
            "supplier_url": "https://www.poundwholesale.co.uk/unmatchable-product",
            "supplier_price": 0.75,
            "amazon_price": None,
            "created_at": "2025-07-27T10:02:00Z",
            "no_match_reason": "No EAN match found, title similarity below threshold"
        }
    ]
    
    # Test with actual system paths
    supplier_name = "poundwholesale.co.uk"
    
    try:
        # Get the actual linking map path using the system's path manager
        linking_map_path = get_linking_map_path(supplier_name)
        print(f"📁 Target path: {linking_map_path}")
        
        # Test the WSL-compatible save function
        print(f"💾 Attempting to save {len(test_linking_map)} test entries...")
        success = wsl_compatible_save(test_linking_map, linking_map_path)
        
        if success:
            print(f"✅ SUCCESS: Linking map saved successfully!")
            
            # Verify the save worked
            if linking_map_path.exists():
                file_size = linking_map_path.stat().st_size
                print(f"✅ VERIFICATION: File exists with size {file_size} bytes")
                
                # Read back and verify content
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                print(f"✅ CONTENT VERIFICATION: Loaded {len(loaded_data)} entries")
                
                # Check if we have the expected entry types
                ean_matches = [e for e in loaded_data if e.get('match_method') == 'EAN']
                title_matches = [e for e in loaded_data if e.get('match_method') == 'title']
                no_matches = [e for e in loaded_data if e.get('match_method') == 'none']
                
                print(f"📊 Match types: {len(ean_matches)} EAN, {len(title_matches)} title, {len(no_matches)} none")
                
                # Show a sample entry
                if loaded_data:
                    sample = loaded_data[0]
                    print(f"📋 Sample entry: {sample.get('supplier_product_identifier')} -> {sample.get('chosen_amazon_asin', 'No match')}")
                
                print("🎉 WSL-compatible linking map save fix is working correctly!")
                return True
                
            else:
                print(f"❌ FAILURE: File was not created at {linking_map_path}")
                return False
                
        else:
            print(f"❌ FAILURE: WSL-compatible save returned False")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_linking_map_save()
    
    if success:
        print("\n🎯 RESULT: WSL-compatible linking map save fix is ready for integration!")
        print("🔧 The fix has been applied to passive_extraction_workflow_latest.py")
        print("📈 This should resolve the WinError 5 permission failures")
    else:
        print("\n❌ RESULT: Fix needs additional work")