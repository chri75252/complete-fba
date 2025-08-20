#!/usr/bin/env python3
"""
Test script to verify that category_manifests AttributeError is fixed after removing duplicate method
"""

import sys
import os
import logging
from unittest.mock import MagicMock

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_category_manifests_fix():
    """Test that category_manifests is properly accessible after duplicate method fix"""
    
    print("🧪 TESTING: Category manifests fix after duplicate method removal")
    print("=" * 70)
    
    try:
        # Import required classes
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        from config.system_config_loader import SystemConfigLoader
        from utils.browser_manager import BrowserManager
        
        # Create mock dependencies
        print("🔧 Setting up mock dependencies...")
        mock_config_loader = MagicMock()
        mock_config_loader.get_full_config.return_value = {"system": {}}
        
        workflow_config = {"supplier_name": "test_supplier"}
        mock_browser_manager = MagicMock()
        
        # Initialize workflow - this should trigger constructor
        print("🚀 Creating PassiveExtractionWorkflow object...")
        try:
            workflow = PassiveExtractionWorkflow(
                config_loader=mock_config_loader,
                workflow_config=workflow_config,
                browser_manager=mock_browser_manager
            )
            print("✅ SUCCESS: Workflow object created successfully")
        except Exception as e:
            print(f"❌ ERROR during workflow creation: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Debug: Check all attributes
        print("\n🔍 DEBUG: Checking all workflow attributes...")
        all_attrs = [attr for attr in dir(workflow) if not attr.startswith('_')]
        print(f"Total public attributes: {len(all_attrs)}")
        
        # Check specifically for attributes we expect
        expected_attrs = ['category_manifests', 'hash_optimizer', 'sentinel_monitor', 'linking_map']
        for attr in expected_attrs:
            if hasattr(workflow, attr):
                value = getattr(workflow, attr)
                print(f"✅ {attr}: {type(value)} = {value}")
            else:
                print(f"❌ {attr}: MISSING")
        
        # Test category_manifests initialization
        print("\n🔍 Testing category_manifests attribute...")
        
        if hasattr(workflow, 'category_manifests'):
            print(f"✅ category_manifests attribute exists: {type(workflow.category_manifests)}")
            if isinstance(workflow.category_manifests, dict):
                print("✅ category_manifests is properly initialized as dictionary")
            else:
                print(f"⚠️ category_manifests is not a dictionary: {type(workflow.category_manifests)}")
                return False
        else:
            print("❌ category_manifests attribute missing")
            return False
            
        # Test accessing category_manifests (simulate the crash line)
        print("\n🧪 Testing category_manifests.get() method (line 4560 simulation)...")
        try:
            test_url = "https://example.com/test-category"
            urls = workflow.category_manifests.get(test_url, [])
            print(f"✅ category_manifests.get() works: returned {type(urls)} with {len(urls)} items")
        except AttributeError as e:
            print(f"❌ AttributeError still occurs: {e}")
            return False
        except Exception as e:
            print(f"⚠️ Other error occurred: {e}")
            return False
            
        # Test setting values in category_manifests (simulate the callback function)
        print("\n🧪 Testing category_manifests assignment (line 1058 simulation)...")
        try:
            test_urls = ["https://example.com/product1", "https://example.com/product2"]
            workflow.category_manifests[test_url] = test_urls
            print(f"✅ category_manifests assignment works: set {len(test_urls)} URLs")
            
            # Verify retrieval
            retrieved_urls = workflow.category_manifests.get(test_url, [])
            print(f"✅ Retrieved {len(retrieved_urls)} URLs from category_manifests")
        except Exception as e:
            print(f"❌ Error during assignment: {e}")
            return False
            
        print("\n🎉 ALL TESTS PASSED: category_manifests AttributeError has been fixed!")
        print("🎯 The duplicate method removal successfully resolved the issue")
        print("🛡️ System should now be able to access category_manifests consistently")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_category_manifests_fix()
    sys.exit(0 if success else 1)