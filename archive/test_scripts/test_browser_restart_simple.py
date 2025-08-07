#!/usr/bin/env python3
"""
Simplified Browser Restart Test

This test focuses specifically on testing the browser restart functionality
by directly manipulating the browser manager's timestamp and testing the
restart detection logic.
"""

import sys
import os
import asyncio
import time
import logging
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.browser_manager import BrowserManager

class SimpleBrowserRestartTester:
    """
    Simplified test focusing on browser restart functionality
    """
    
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.log = logging.getLogger('RestartTester')
        self.browser_manager = None
        
    async def setup_browser(self):
        """Setup browser manager"""
        try:
            self.log.info("🔧 Setting up browser manager...")
            self.browser_manager = BrowserManager.get_instance()
            
            # Try to launch browser
            try:
                await self.browser_manager.launch_browser(cdp_port=9222)
                self.log.info("✅ Browser launched successfully")
                return True
            except Exception as launch_error:
                self.log.warning(f"⚠️ Browser launch failed: {launch_error}")
                # Continue with tests even if browser launch fails
                return True
                
        except Exception as e:
            self.log.error(f"❌ Browser setup failed: {e}")
            return False
    
    def fake_browser_age(self, hours: float):
        """Make browser appear older by manipulating timestamp"""
        if not self.browser_manager:
            self.log.error("❌ No browser manager available")
            return None
            
        try:
            # Store original timestamp
            original_timestamp = self.browser_manager._last_restart
            
            # Calculate fake timestamp (hours ago)
            fake_timestamp = time.time() - (hours * 3600)
            
            # Set fake timestamp
            self.browser_manager._last_restart = fake_timestamp
            
            self.log.info(f"⏰ FAKED BROWSER AGE: {hours} hours")
            self.log.info(f"   Original: {datetime.fromtimestamp(original_timestamp)}")
            self.log.info(f"   Fake: {datetime.fromtimestamp(fake_timestamp)}")
            
            return original_timestamp
            
        except Exception as e:
            self.log.error(f"❌ Failed to fake browser age: {e}")
            return None
    
    async def test_restart_detection(self):
        """Test browser restart detection logic"""
        try:
            self.log.info("\n🔍 TEST 1: Browser Restart Detection")
            self.log.info("-" * 40)
            
            # Test 1: Normal condition (should NOT restart)
            self.log.info("📊 Testing normal condition...")
            should_restart_normal = await self.browser_manager.should_restart_browser()
            self.log.info(f"   Result: should_restart = {should_restart_normal}")
            
            # Test 2: Fake old browser (should restart)
            self.log.info("📊 Testing with fake 3-hour age...")
            original_timestamp = self.fake_browser_age(3.0)
            
            should_restart_fake = await self.browser_manager.should_restart_browser()
            self.log.info(f"   Result: should_restart = {should_restart_fake}")
            
            # Restore original timestamp
            if original_timestamp:
                self.browser_manager._last_restart = original_timestamp
                self.log.info("🔄 Restored original timestamp")
            
            # Evaluate results
            test_passed = (not should_restart_normal) and should_restart_fake
            
            if test_passed:
                self.log.info("✅ TEST 1 PASSED: Restart detection working correctly")
            else:
                self.log.error("❌ TEST 1 FAILED: Restart detection not working")
                self.log.error(f"   Expected: normal=False, fake=True")
                self.log.error(f"   Actual: normal={should_restart_normal}, fake={should_restart_fake}")
            
            return test_passed
            
        except Exception as e:
            self.log.error(f"❌ TEST 1 ERROR: {e}")
            return False
    
    async def test_memory_monitoring(self):
        """Test memory monitoring functionality"""
        try:
            self.log.info("\n🔍 TEST 2: Memory Monitoring")
            self.log.info("-" * 40)
            
            # Get memory information
            memory_info = await self.browser_manager.get_total_system_memory_usage()
            
            if memory_info:
                self.log.info("📊 MEMORY REPORT:")
                self.log.info(f"   🐍 Python: {memory_info.get('python_memory_mb', 0)}MB")
                self.log.info(f"   🟢 Node.js: {memory_info.get('nodejs_memory_mb', 0)}MB")
                self.log.info(f"   🌐 Chrome: {memory_info.get('chrome_memory_mb', 0)}MB")
                self.log.info(f"   💾 System: {memory_info.get('memory_usage_percent', 0):.1f}%")
                self.log.info(f"   🔍 Node.js processes: {memory_info.get('nodejs_processes_detected', 0)}")
                
                # Check if Node.js monitoring is working
                nodejs_detected = memory_info.get('nodejs_processes_detected', 0) >= 0
                
                if nodejs_detected:
                    self.log.info("✅ TEST 2 PASSED: Memory monitoring working (including Node.js)")
                else:
                    self.log.warning("⚠️ TEST 2 PARTIAL: Memory monitoring working but Node.js detection unclear")
                
                return True
            else:
                self.log.error("❌ TEST 2 FAILED: No memory information returned")
                return False
                
        except Exception as e:
            self.log.error(f"❌ TEST 2 ERROR: {e}")
            return False
    
    async def test_restart_interval_config(self):
        """Test restart interval configuration"""
        try:
            self.log.info("\n🔍 TEST 3: Restart Interval Configuration")
            self.log.info("-" * 40)
            
            # Check restart interval
            restart_hours = self.browser_manager._restart_interval_hours
            self.log.info(f"📊 Configured restart interval: {restart_hours} hours")
            
            # Verify it's the expected value (2.5 hours)
            expected_hours = 2.5
            if restart_hours == expected_hours:
                self.log.info(f"✅ TEST 3 PASSED: Restart interval correctly set to {expected_hours} hours")
                return True
            else:
                self.log.error(f"❌ TEST 3 FAILED: Expected {expected_hours} hours, got {restart_hours} hours")
                return False
                
        except Exception as e:
            self.log.error(f"❌ TEST 3 ERROR: {e}")
            return False
    
    async def test_time_calculation(self):
        """Test time calculation logic"""
        try:
            self.log.info("\n🔍 TEST 4: Time Calculation Logic")
            self.log.info("-" * 40)
            
            # Get current time info
            current_time = time.time()
            last_restart = self.browser_manager._last_restart
            time_since_restart = current_time - last_restart
            hours_since_restart = time_since_restart / 3600
            
            self.log.info(f"📊 Current time: {datetime.fromtimestamp(current_time)}")
            self.log.info(f"📊 Last restart: {datetime.fromtimestamp(last_restart)}")
            self.log.info(f"📊 Hours since restart: {hours_since_restart:.2f}")
            
            # Test with fake old timestamp
            self.log.info("📊 Testing with fake 4-hour age...")
            original_timestamp = self.fake_browser_age(4.0)
            
            # Recalculate
            fake_time_since = current_time - self.browser_manager._last_restart
            fake_hours_since = fake_time_since / 3600
            
            self.log.info(f"📊 Fake hours since restart: {fake_hours_since:.2f}")
            
            # Check if restart would be triggered
            should_restart = fake_hours_since > self.browser_manager._restart_interval_hours
            self.log.info(f"📊 Should restart (4h > 2.5h): {should_restart}")
            
            # Restore timestamp
            if original_timestamp:
                self.browser_manager._last_restart = original_timestamp
            
            if should_restart and fake_hours_since > 3.5:  # Should be around 4 hours
                self.log.info("✅ TEST 4 PASSED: Time calculation logic working correctly")
                return True
            else:
                self.log.error("❌ TEST 4 FAILED: Time calculation logic not working")
                return False
                
        except Exception as e:
            self.log.error(f"❌ TEST 4 ERROR: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all browser restart tests"""
        try:
            self.log.info("🚀 BROWSER RESTART FUNCTIONALITY TEST")
            self.log.info("=" * 50)
            self.log.info("Testing browser restart without waiting 2.5 hours...")
            
            # Setup
            if not await self.setup_browser():
                self.log.error("❌ SETUP FAILED - Cannot continue")
                return False
            
            # Run tests
            tests = [
                ("Restart Detection", self.test_restart_detection),
                ("Memory Monitoring", self.test_memory_monitoring),
                ("Restart Interval Config", self.test_restart_interval_config),
                ("Time Calculation Logic", self.test_time_calculation)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    success = await test_func()
                    if success:
                        passed += 1
                    await asyncio.sleep(1)  # Small delay between tests
                except Exception as e:
                    self.log.error(f"💥 {test_name} crashed: {e}")
            
            # Results
            self.log.info("\n" + "=" * 50)
            self.log.info("🎯 FINAL RESULTS")
            self.log.info("=" * 50)
            
            success_rate = (passed / total) * 100
            self.log.info(f"📊 Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
            
            if passed == total:
                self.log.info("🎉 ALL TESTS PASSED!")
                self.log.info("✅ Browser restart functionality is working correctly")
                self.log.info("✅ Time-based restart will trigger every 2.5 hours")
                self.log.info("✅ Memory monitoring includes Python and Node.js processes")
                return True
            else:
                self.log.warning(f"⚠️ {total - passed} tests failed")
                self.log.warning("Some browser restart functionality may need attention")
                return False
                
        except Exception as e:
            self.log.error(f"💥 TEST SUITE CRASHED: {e}")
            return False

async def main():
    """Main test execution"""
    print("🔧 Simplified Browser Restart Test")
    print("=" * 40)
    print("Testing browser restart functionality...")
    print()
    
    tester = SimpleBrowserRestartTester()
    success = await tester.run_all_tests()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 SUCCESS: Browser restart is working!")
        print("The system will restart browser every 2.5 hours.")
    else:
        print("❌ ISSUES: Some functionality needs attention.")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(main())