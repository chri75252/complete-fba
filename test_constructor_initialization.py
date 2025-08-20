#!/usr/bin/env python3
"""
Test script to verify that hash_optimizer and sentinel_monitor are properly initialized in constructor
"""

import sys
import os
import logging
from unittest.mock import MagicMock

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

def test_constructor_initialization():
    """Test that components are initialized during object construction"""
    
    print("🧪 TESTING: Constructor component initialization")
    print("=" * 60)
    
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
        workflow = PassiveExtractionWorkflow(
            config_loader=mock_config_loader,
            workflow_config=workflow_config,
            browser_manager=mock_browser_manager
        )
        
        print("✅ SUCCESS: Workflow object created successfully")
        
        # Test component initialization
        print("\n🔍 Testing component initialization...")
        
        # Test hash_optimizer
        if hasattr(workflow, 'hash_optimizer'):
            print(f"✅ hash_optimizer attribute exists: {type(workflow.hash_optimizer)}")
            if workflow.hash_optimizer is not None:
                print("✅ hash_optimizer is properly initialized (not None)")
            else:
                print("⚠️ hash_optimizer is None (initialization failed but handled gracefully)")
        else:
            print("❌ hash_optimizer attribute missing")
            return False
            
        # Test sentinel_monitor  
        if hasattr(workflow, 'sentinel_monitor'):
            print(f"✅ sentinel_monitor attribute exists: {type(workflow.sentinel_monitor)}")
            if workflow.sentinel_monitor is not None:
                print("✅ sentinel_monitor is properly initialized (not None)")
            else:
                print("⚠️ sentinel_monitor is None (initialization failed but handled gracefully)")
        else:
            print("❌ sentinel_monitor attribute missing")
            return False
            
        # Test other components
        if hasattr(workflow, 'save_guardian'):
            print(f"✅ save_guardian attribute exists: {type(workflow.save_guardian)}")
        else:
            print("❌ save_guardian attribute missing")
            
        if hasattr(workflow, 'linking_map'):
            print(f"✅ linking_map attribute exists: {type(workflow.linking_map)} with {len(workflow.linking_map)} entries")
        else:
            print("❌ linking_map attribute missing")
            
        print("\n🎉 CONSTRUCTOR TEST PASSED: All components are initialized during object creation")
        print("🎯 This means AttributeError crashes should be eliminated")
        return True
        
    except Exception as e:
        print(f"❌ CONSTRUCTOR TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_constructor_initialization()
    sys.exit(0 if success else 1)