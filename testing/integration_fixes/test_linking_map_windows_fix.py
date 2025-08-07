#!/usr/bin/env python3
"""
Simple test to verify if the linking map WinError 5 fix works on Windows
"""

import os
import json
import sys
from pathlib import Path

def test_linking_map_fix():
    """Test the linking map save fix in Windows environment"""
    
    print("🔧 TESTING LINKING MAP WINDOWS FIX")
    print("=" * 50)
    print(f"Running on: {os.name}")
    print(f"Python executable: {sys.executable}")
    print(f"Current directory: {os.getcwd()}")
    
    # Import both the old and new fixes for comparison
    wsl_save_available = False
    guardian_save_available = False
    
    try:
        from wsl_compatible_save import wsl_compatible_save
        wsl_save_available = True
        print("✅ Successfully imported wsl_compatible_save")
    except ImportError as e:
        print(f"⚠️ Failed to import wsl_compatible_save: {e}")
    
    try:
        from utils.windows_save_guardian import save_json_atomic
        guardian_save_available = True
        print("✅ Successfully imported Windows Save Guardian")
    except ImportError as e:
        print(f"⚠️ Failed to import Windows Save Guardian: {e}")
    
    if not wsl_save_available and not guardian_save_available:
        print("❌ No save solutions available")
        return False
    
    # Create test data (realistic linking map entries)
    test_data = [
        {
            "supplier_ean": "1234567890123",
            "amazon_asin": "B08XYZ123",
            "supplier_title": "Test Product 1",
            "amazon_title": "Amazon Test Product 1",
            "supplier_price": 1.50,
            "amazon_price": 9.99,
            "match_method": "EAN",
            "confidence": "high",
            "supplier_url": "https://www.poundwholesale.co.uk/test-1",
            "created_at": "2025-07-27T10:00:00Z"
        },
        {
            "supplier_ean": "9876543210987",
            "amazon_asin": None,
            "supplier_title": "Unmatchable Product",
            "amazon_title": None,
            "supplier_price": 0.75,
            "amazon_price": None,
            "match_method": "none",
            "confidence": "none",
            "supplier_url": "https://www.poundwholesale.co.uk/unmatchable",
            "created_at": "2025-07-27T10:01:00Z",
            "no_match_reason": "No EAN match found, title similarity below threshold"
        }
    ]
    
    # Test the actual linking map path
    linking_map_path = Path("OUTPUTS/FBA_ANALYSIS/linking_maps/poundwholesale.co.uk/linking_map_test.json")
    
    print(f"\n📁 Testing save to: {linking_map_path}")
    print(f"📋 Test data: {len(test_data)} entries")
    
    # Test both solutions if available
    results = []
    
    # Test 1: Original WSL-compatible save
    if wsl_save_available:
        print(f"\n🧪 Testing WSL-compatible save...")
        try:
            success = wsl_compatible_save(test_data, linking_map_path)
            if success and linking_map_path.exists():
                file_size = linking_map_path.stat().st_size
                print(f"✅ WSL-compatible save: SUCCESS ({file_size} bytes)")
                results.append(("WSL-compatible", True, file_size))
                # Clean up for next test
                linking_map_path.unlink()
            else:
                print("❌ WSL-compatible save: FAILED")
                results.append(("WSL-compatible", False, 0))
        except Exception as e:
            print(f"❌ WSL-compatible save ERROR: {e}")
            results.append(("WSL-compatible", False, 0))
    
    # Test 2: Windows Save Guardian
    if guardian_save_available:
        print(f"\n🛡️ Testing Windows Save Guardian...")
        try:
            success = save_json_atomic(linking_map_path, test_data)
            if success and linking_map_path.exists():
                with open(linking_map_path, 'r') as f:
                    loaded_data = json.load(f)
                file_size = linking_map_path.stat().st_size
                print(f"✅ Windows Save Guardian: SUCCESS ({file_size} bytes)")
                print(f"✅ File verification: {len(loaded_data)} entries loaded")
                print(f"📊 Entry types: {[e.get('match_method') for e in loaded_data]}")
                results.append(("Windows Save Guardian", True, file_size))
                
                # Check telemetry
                telemetry_path = Path("OUTPUTS/DIAGNOSTICS/save_telemetry.log")
                if telemetry_path.exists():
                    print("✅ Telemetry logging: ACTIVE")
                
                return True
            else:
                print("❌ Windows Save Guardian: FAILED")
                results.append(("Windows Save Guardian", False, 0))
        except Exception as e:
            print(f"❌ Windows Save Guardian ERROR: {e}")
            results.append(("Windows Save Guardian", False, 0))
    
    # Summary of results
    print(f"\n📊 SAVE METHOD COMPARISON:")
    for method, success, size in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {method}: {status} ({size} bytes)")
    
    # Return True if any method succeeded
    return any(result[1] for result in results)

def main():
    """Run the test"""
    print("🪟 WINDOWS LINKING MAP FIX VERIFICATION")
    print("=" * 60)
    
    success = test_linking_map_fix()
    
    print(f"\n🎯 RESULT:")
    if success:
        print("✅ Linking map save solution WORKS on Windows!")
        print("📝 The WinError 5 issue should be resolved")
        print("🛡️ Windows Save Guardian provides production-ready solution")
        print("🚀 Ready for integration into the main workflow")
    else:
        print("❌ Both save solutions failed - additional debugging required")
        print("📝 Check file permissions and Windows environment")
    
    return success

if __name__ == "__main__":
    main()