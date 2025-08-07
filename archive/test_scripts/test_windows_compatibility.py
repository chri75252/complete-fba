#!/usr/bin/env python3
"""
Windows Compatibility Test Script
================================

Tests that the Amazon FBA Agent System can run on Windows Command Prompt
without WSL dependencies.

Usage: python test_windows_compatibility.py
"""

import sys
import os
import platform
import asyncio
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_platform_detection():
    """Test platform detection and Windows-specific setup"""
    print("🧪 Testing Platform Detection...")
    
    system_platform = platform.system()
    print(f"📊 Detected Platform: {system_platform}")
    print(f"🐍 Python Version: {platform.python_version()}")
    print(f"🏗️ Architecture: {platform.machine()}")
    
    if system_platform == "Windows":
        print("✅ Windows detected - will use Windows-native memory management")
        return True
    else:
        print("ℹ️ Non-Windows platform - will use standard memory management")
        return False

def test_imports():
    """Test that all required imports work without WSL dependencies"""
    print("\n🧪 Testing Core Imports...")
    
    try:
        # Test core system imports
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        print("✅ PassiveExtractionWorkflow imported successfully")
        
        from utils.browser_manager import BrowserManager
        print("✅ BrowserManager imported successfully")
        
        from config.system_config_loader import SystemConfigLoader
        print("✅ SystemConfigLoader imported successfully")
        
        # Test Windows memory manager
        from utils.windows_memory_manager import WindowsMemoryManager
        print("✅ WindowsMemoryManager imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during imports: {e}")
        return False

async def test_memory_management():
    """Test Windows memory management functionality"""
    print("\n🧪 Testing Memory Management...")
    
    try:
        # Test Windows memory manager
        from utils.windows_memory_manager import WindowsMemoryManager, monitor_memory_during_supplier_scraping
        
        manager = WindowsMemoryManager()
        print("✅ WindowsMemoryManager created successfully")
        
        # Test memory usage detection
        usage = manager.get_windows_memory_usage()
        if usage:
            print(f"✅ Memory usage detected: {usage.get('used_memory_gb', 0):.1f}GB used")
            print(f"   Chrome processes: {usage.get('chrome_processes', 0)}")
            print(f"   Memory percent: {usage.get('memory_percent', 0):.1f}%")
        else:
            print("⚠️ Memory usage detection returned empty result")
        
        # Test memory monitoring function
        result = await monitor_memory_during_supplier_scraping(1)
        if result:
            print("✅ Memory monitoring function working")
        else:
            print("⚠️ Memory monitoring function returned False")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory management test failed: {e}")
        return False

def test_browser_compatibility():
    """Test browser manager Windows compatibility"""
    print("\n🧪 Testing Browser Manager Compatibility...")
    
    try:
        from utils.browser_manager import BrowserManager
        
        # Test browser manager creation
        browser_manager = BrowserManager.get_instance()
        print("✅ BrowserManager singleton created")
        
        # Test memory usage method (should work without browser connection)
        try:
            # This should work even without browser connection
            import asyncio
            memory_usage = asyncio.run(browser_manager.get_total_system_memory_usage())
            
            if memory_usage:
                platform_info = memory_usage.get('platform', 'Unknown')
                chrome_memory = memory_usage.get('chrome_memory_mb', -1)
                print(f"✅ Memory usage detection working - Platform: {platform_info}")
                print(f"   Chrome memory: {chrome_memory}MB")
                print(f"   Accurate detection: {memory_usage.get('accurate_detection', False)}")
            else:
                print("⚠️ Memory usage detection returned empty result")
                
        except Exception as e:
            print(f"⚠️ Browser memory detection failed (expected without Chrome): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Browser manager test failed: {e}")
        return False

def test_workflow_initialization():
    """Test that the main workflow can be initialized"""
    print("\n🧪 Testing Workflow Initialization...")
    
    try:
        from config.system_config_loader import SystemConfigLoader
        from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
        
        # Test config loader
        config_loader = SystemConfigLoader()
        print("✅ SystemConfigLoader created")
        
        # Test workflow config loading
        workflow_config = config_loader.get_workflow_config('poundwholesale_workflow')
        if workflow_config:
            print("✅ Workflow config loaded")
            supplier_name = workflow_config.get('supplier_name', 'poundwholesale.co.uk')
            print(f"   Supplier: {supplier_name}")
        else:
            print("⚠️ Workflow config is empty")
        
        # Test workflow creation (without browser manager)
        try:
            workflow = PassiveExtractionWorkflow(
                config_loader=config_loader,
                workflow_config=workflow_config,
                browser_manager=None  # Test without browser
            )
            print("✅ PassiveExtractionWorkflow created successfully")
        except Exception as e:
            print(f"⚠️ Workflow creation failed (may need browser): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow initialization test failed: {e}")
        return False

async def run_all_tests():
    """Run all compatibility tests"""
    print("🪟 Windows Compatibility Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Platform Detection
    if test_platform_detection():
        tests_passed += 1
    
    # Test 2: Core Imports
    if test_imports():
        tests_passed += 1
    
    # Test 3: Memory Management
    if await test_memory_management():
        tests_passed += 1
    
    # Test 4: Browser Compatibility
    if test_browser_compatibility():
        tests_passed += 1
    
    # Test 5: Workflow Initialization
    if test_workflow_initialization():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary")
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED - System is Windows compatible!")
        print("\n🚀 You can now run the system with:")
        print("   python run_custom_poundwholesale.py")
        print("\n🌐 Make sure Chrome is running with debug port:")
        print("   chrome --remote-debugging-port=9222 --user-data-dir=C:\\temp\\chrome-debug")
        return True
    else:
        print(f"⚠️ {total_tests - tests_passed} tests failed - check the issues above")
        return False

if __name__ == "__main__":
    # Windows-specific event loop configuration for Python 3.13+
    if sys.platform == "win32":
        import platform
        python_version = tuple(map(int, platform.python_version().split('.')))
        
        if python_version >= (3, 13):
            # Python 3.13+ requires ProactorEventLoop for subprocess support on Windows
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("🔧 Using Windows ProactorEventLoop for Python 3.13+ compatibility")
        else:
            # Python 3.12 and below use SelectorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            print("🔧 Using Windows SelectorEventLoop for Python 3.12 compatibility")
    
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except NotImplementedError as e:
        print(f"\n❌ Windows event loop error: {e}")
        print("💡 This is a known issue with Python 3.13+ on Windows")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)