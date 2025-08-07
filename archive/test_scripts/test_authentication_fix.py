#!/usr/bin/env python3
"""
Test script to verify the authentication fix implementation
"""

import sys
import os
import asyncio
import inspect

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_authentication_implementation():
    """Test which authentication methods are available in the current workflow"""
    
    print("🔍 Testing authentication implementation...")
    
    try:
        # Import the workflow class
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        
        # Check if the problematic authentication trigger method exists
        has_trigger_method = hasattr(PassiveExtractionWorkflow, '_trigger_authentication_check')
        print(f"❓ Has _trigger_authentication_check method: {has_trigger_method}")
        
        if has_trigger_method:
            method = getattr(PassiveExtractionWorkflow, '_trigger_authentication_check')
            print(f"🔍 Method signature: {inspect.signature(method)}")
            print("❌ PROBLEM: The problematic authentication trigger method still exists!")
            return False
        else:
            print("✅ GOOD: The problematic authentication trigger method has been removed")
        
        # Check if the deprecated method exists
        has_deprecated_method = hasattr(PassiveExtractionWorkflow, '_check_authentication_before_category')
        print(f"❓ Has _check_authentication_before_category method: {has_deprecated_method}")
        
        if has_deprecated_method:
            print("ℹ️  INFO: Deprecated authentication method still exists (this is expected)")
        
        # Check if the authentication fallback method exists
        has_fallback_method = hasattr(PassiveExtractionWorkflow, '_perform_authentication_fallback')
        print(f"❓ Has _perform_authentication_fallback method: {has_fallback_method}")
        
        if has_fallback_method:
            print("✅ GOOD: Authentication fallback method exists")
        else:
            print("❌ PROBLEM: Authentication fallback method is missing!")
            return False
        
        # Check the source file location
        import tools.passive_extraction_workflow_latest
        source_file = inspect.getfile(tools.passive_extraction_workflow_latest)
        print(f"📁 Source file: {source_file}")
        
        # Check if there are any references to LOGIN SCRIPT TRIGGER in the source
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'LOGIN SCRIPT TRIGGER' in content:
            print("❌ PROBLEM: LOGIN SCRIPT TRIGGER code still exists in the source file!")
            return False
        else:
            print("✅ GOOD: LOGIN SCRIPT TRIGGER code has been removed from source")
        
        print("\n🎯 CONCLUSION:")
        print("The authentication trigger method has been properly removed from the current workflow file.")
        print("If you're still seeing LOGIN SCRIPT TRIGGER messages in logs, it means:")
        print("1. The system is using a cached/compiled version of the old code")
        print("2. There might be another process running with the old code")
        print("3. The Python import cache needs to be cleared")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_authentication_implementation())
    if result:
        print("\n✅ Test completed successfully")
    else:
        print("\n❌ Test failed - authentication implementation needs fixing")