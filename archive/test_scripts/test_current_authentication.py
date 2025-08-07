#!/usr/bin/env python3
"""
Test script to verify current authentication behavior
"""
import sys
import os
import asyncio
import importlib

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_authentication_behavior():
    """Test the current authentication behavior"""
    print("🔍 Testing current authentication behavior...")
    
    try:
        # Force reload the module to avoid cache
        import tools.passive_extraction_workflow_latest
        importlib.reload(tools.passive_extraction_workflow_latest)
        
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        
        # Check if the problematic method exists
        has_trigger_method = hasattr(PassiveExtractionWorkflow, '_trigger_authentication_check')
        print(f"❓ Has _trigger_authentication_check method: {has_trigger_method}")
        
        if has_trigger_method:
            print("❌ ERROR: The problematic authentication trigger method still exists!")
            print("This means the system is still using cached code.")
            return False
        else:
            print("✅ GOOD: The problematic authentication trigger method has been removed")
        
        # Check the category batch processing method
        # We'll just check the class methods without instantiating
        print("✅ GOOD: Checking class methods without instantiation")
        
        # Check if the method that processes category batches exists
        has_extract_method = hasattr(PassiveExtractionWorkflow, '_extract_supplier_products_with_batching')
        print(f"❓ Has _extract_supplier_products_with_batching method: {has_extract_method}")
        
        if has_extract_method:
            print("✅ GOOD: Main extraction method exists")
            
            # Get the source code of the method to check for authentication triggers
            import inspect
            source = inspect.getsource(PassiveExtractionWorkflow._extract_supplier_products_with_batching)
            
            if "LOGIN SCRIPT TRIGGER" in source:
                print("❌ ERROR: LOGIN SCRIPT TRIGGER code still exists in the method!")
                return False
            elif "_trigger_authentication_check" in source:
                print("❌ ERROR: _trigger_authentication_check call still exists in the method!")
                return False
            else:
                print("✅ GOOD: No authentication trigger code found in extraction method")
        
        print("\n🎯 CONCLUSION:")
        print("The authentication trigger code has been properly removed.")
        print("If you're still seeing LOGIN SCRIPT TRIGGER messages, restart the system completely.")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during test: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_authentication_behavior())
    if result:
        print("\n✅ Test passed - authentication trigger has been removed")
    else:
        print("\n❌ Test failed - authentication trigger still exists")