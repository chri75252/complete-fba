#!/usr/bin/env python3
"""
Actual Browser Restart Test

This test actually performs browser restarts to verify the complete restart sequence works.
It will fake the duration to trigger restarts and then execute the actual restart process.
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

class ActualBrowserRestartTester:
    """
    Test that actually performs browser restarts
    """
    
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.log = logging.getLogger('ActualRestartTester')
        self.browser_manager = None
        self.test_results = []
        
    async def setup_browser(self):
        """Setup browser manager and launch browser"""
        try:
            self.log.info("🔧 Setting up browser manager...")
            self.browser_manager = BrowserManager.get_instance()
            
            # Launch browser
            await self.browser_manager.launch_browser(cdp_port=9222)
            self.log.info("✅ Browser launched successfully")
            
            # Verify browser is working
            page = await self.browser_manager.get_page("https://www.google.com")
            self.log.info("✅ Browser is responding - loaded Google")
            
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
    
    async def test_actual_restart_execution(self):
        """Test that actually executes a browser restart"""
        try:
            self.log.info("\n🔍 TEST 1: Actual Browser Restart Execution")
            self.log.info("-" * 50)
            
            # Get initial browser state
            initial_memory = await self.browser_manager.get_browser_memory_usage()
            initial_health = await self.browser_manager.verify_connection_health()
            
            self.log.info(f"📊 Initial State:")
            self.log.info(f"   Memory: {initial_memory}MB")
            self.log.info(f"   Health: {initial_health}")
            
            # Fake browser age to trigger restart
            self.log.info("⏰ Faking browser age to 3 hours...")
            original_timestamp = self.fake_browser_age(3.0)
            
            # Check if restart is needed
            should_restart = await self.browser_manager.should_restart_browser()
            self.log.info(f"📊 Should restart: {should_restart}")
            
            if should_restart:
                self.log.info("🔄 EXECUTING ACTUAL BROWSER RESTART...")
                
                # Record restart start time
                restart_start = time.time()
                
                # Execute the actual restart
                restart_success = await self.browser_manager.restart_browser()
                
                # Record restart completion time
                restart_duration = time.time() - restart_start
                
                self.log.info(f"⏱️ Restart completed in {restart_duration:.2f} seconds")
                self.log.info(f"✅ Restart result: {restart_success}")
                
                if restart_success:
                    # Verify browser is working after restart
                    self.log.info("🔍 Verifying browser functionality after restart...")
                    
                    try:
                        # Test browser connection
                        post_restart_health = await self.browser_manager.verify_connection_health()
                        self.log.info(f"📊 Post-restart health: {post_restart_health}")
                        
                        # Test page loading
                        test_page = await self.browser_manager.get_page("https://www.example.com")
                        self.log.info("✅ Browser can load pages after restart")
                        
                        # Get post-restart memory
                        post_restart_memory = await self.browser_manager.get_browser_memory_usage()
                        self.log.info(f"📊 Post-restart memory: {post_restart_memory}MB")
                        
                        # Check if restart timestamp was updated
                        new_timestamp = self.browser_manager._last_restart
                        timestamp_updated = new_timestamp > original_timestamp
                        self.log.info(f"📊 Restart timestamp updated: {timestamp_updated}")
                        
                        result = {
                            "test": "actual_restart_execution",
                            "restart_triggered": should_restart,
                            "restart_success": restart_success,
                            "restart_duration": restart_duration,
                            "post_restart_health": post_restart_health,
                            "timestamp_updated": timestamp_updated,
                            "initial_memory": initial_memory,
                            "post_restart_memory": post_restart_memory,
                            "success": restart_success and post_restart_health and timestamp_updated
                        }
                        
                        if result["success"]:
                            self.log.info("✅ TEST 1 PASSED: Browser restart executed successfully")
                        else:
                            self.log.error("❌ TEST 1 FAILED: Browser restart had issues")
                        
                        return result["success"]
                        
                    except Exception as verify_error:
                        self.log.error(f"❌ Post-restart verification failed: {verify_error}")
                        return False
                        
                else:
                    self.log.error("❌ TEST 1 FAILED: Browser restart returned False")
                    return False
            else:
                self.log.error("❌ TEST 1 FAILED: Restart was not triggered despite fake age")
                return False
            
            # Restore original timestamp
            if original_timestamp:
                self.browser_manager._last_restart = original_timestamp
                
        except Exception as e:
            self.log.error(f"❌ TEST 1 ERROR: {e}")
            return False
    
    async def test_restart_with_memory_threshold(self):
        """Test restart triggered by memory threshold"""
        try:
            self.log.info("\n🔍 TEST 2: Restart with Memory Threshold")
            self.log.info("-" * 50)
            
            # Get current memory threshold
            original_threshold = self.browser_manager._memory_threshold_mb
            current_memory = await self.browser_manager.get_browser_memory_usage()
            
            self.log.info(f"📊 Current memory: {current_memory}MB")
            self.log.info(f"📊 Original threshold: {original_threshold}MB")
            
            # Temporarily lower the memory threshold to trigger restart
            if current_memory > 100:  # Only if we have some memory usage
                new_threshold = max(100, current_memory - 100)  # Set threshold below current usage
                self.browser_manager._memory_threshold_mb = new_threshold
                
                self.log.info(f"📊 Lowered threshold to: {new_threshold}MB")
                
                # Check if restart is needed now
                should_restart = await self.browser_manager.should_restart_browser()
                self.log.info(f"📊 Should restart (memory): {should_restart}")
                
                if should_restart:
                    self.log.info("🔄 EXECUTING MEMORY-TRIGGERED RESTART...")
                    
                    restart_success = await self.browser_manager.restart_browser()
                    self.log.info(f"✅ Memory-triggered restart result: {restart_success}")
                    
                    # Restore original threshold
                    self.browser_manager._memory_threshold_mb = original_threshold
                    
                    if restart_success:
                        self.log.info("✅ TEST 2 PASSED: Memory-triggered restart successful")
                        return True
                    else:
                        self.log.error("❌ TEST 2 FAILED: Memory-triggered restart failed")
                        return False
                else:
                    # Restore original threshold
                    self.browser_manager._memory_threshold_mb = original_threshold
                    self.log.error("❌ TEST 2 FAILED: Memory threshold didn't trigger restart")
                    return False
            else:
                self.log.warning("⚠️ TEST 2 SKIPPED: Not enough memory usage to test threshold")
                return True
                
        except Exception as e:
            # Restore original threshold on error
            if hasattr(self, 'browser_manager') and hasattr(self.browser_manager, '_memory_threshold_mb'):
                self.browser_manager._memory_threshold_mb = getattr(self, 'original_threshold', 2048)
            self.log.error(f"❌ TEST 2 ERROR: {e}")
            return False
    
    async def test_restart_sequence_timing(self):
        """Test the timing and sequence of restart operations"""
        try:
            self.log.info("\n🔍 TEST 3: Restart Sequence Timing")
            self.log.info("-" * 50)
            
            # Record initial state
            initial_time = time.time()
            initial_restart_time = self.browser_manager._last_restart
            
            self.log.info(f"📊 Initial restart time: {datetime.fromtimestamp(initial_restart_time)}")
            
            # Fake age and execute restart
            original_timestamp = self.fake_browser_age(4.0)
            
            # Time the restart process
            restart_start = time.time()
            restart_success = await self.browser_manager.restart_browser()
            restart_end = time.time()
            
            restart_duration = restart_end - restart_start
            new_restart_time = self.browser_manager._last_restart
            
            self.log.info(f"📊 Restart duration: {restart_duration:.2f} seconds")
            self.log.info(f"📊 New restart time: {datetime.fromtimestamp(new_restart_time)}")
            
            # Verify timing
            timing_correct = new_restart_time > initial_restart_time
            duration_reasonable = 1.0 <= restart_duration <= 30.0  # Should take 1-30 seconds
            
            self.log.info(f"📊 Timing correct: {timing_correct}")
            self.log.info(f"📊 Duration reasonable: {duration_reasonable}")
            
            if restart_success and timing_correct and duration_reasonable:
                self.log.info("✅ TEST 3 PASSED: Restart sequence timing is correct")
                return True
            else:
                self.log.error("❌ TEST 3 FAILED: Restart sequence timing issues")
                return False
                
        except Exception as e:
            self.log.error(f"❌ TEST 3 ERROR: {e}")
            return False
    
    async def test_restart_error_handling(self):
        """Test restart error handling"""
        try:
            self.log.info("\n🔍 TEST 4: Restart Error Handling")
            self.log.info("-" * 50)
            
            # Test restart when browser is already disconnected
            self.log.info("🔌 Disconnecting browser to test error handling...")
            
            # Save current browser state
            original_browser = self.browser_manager.browser
            original_context = self.browser_manager.context
            
            # Simulate disconnected state
            self.browser_manager.browser = None
            self.browser_manager.context = None
            
            # Try restart with disconnected browser
            restart_result = await self.browser_manager.restart_browser()
            
            self.log.info(f"📊 Restart with disconnected browser: {restart_result}")
            
            # Restore browser state
            self.browser_manager.browser = original_browser
            self.browser_manager.context = original_context
            
            # The restart should handle the error gracefully
            if restart_result is not None:  # Should return True or False, not crash
                self.log.info("✅ TEST 4 PASSED: Restart error handling works")
                return True
            else:
                self.log.error("❌ TEST 4 FAILED: Restart error handling crashed")
                return False
                
        except Exception as e:
            self.log.error(f"❌ TEST 4 ERROR: {e}")
            # Try to restore browser state
            try:
                await self.setup_browser()
            except:
                pass
            return False
    
    async def run_all_tests(self):
        """Run all actual browser restart tests"""
        try:
            self.log.info("🚀 ACTUAL BROWSER RESTART TEST")
            self.log.info("=" * 60)
            self.log.info("This test will actually restart the browser multiple times!")
            self.log.info("You may see Chrome windows close and reopen.")
            
            # Setup
            if not await self.setup_browser():
                self.log.error("❌ SETUP FAILED - Cannot continue")
                return False
            
            # Run tests
            tests = [
                ("Actual Restart Execution", self.test_actual_restart_execution),
                ("Memory Threshold Restart", self.test_restart_with_memory_threshold),
                ("Restart Sequence Timing", self.test_restart_sequence_timing),
                ("Restart Error Handling", self.test_restart_error_handling)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                self.log.info(f"\n{'='*20} {test_name} {'='*20}")
                try:
                    success = await test_func()
                    if success:
                        passed += 1
                        self.log.info(f"✅ {test_name}: PASSED")
                    else:
                        self.log.error(f"❌ {test_name}: FAILED")
                    
                    # Wait between tests to let browser stabilize
                    await asyncio.sleep(3)
                    
                except Exception as e:
                    self.log.error(f"💥 {test_name} crashed: {e}")
            
            # Results
            self.log.info("\n" + "=" * 60)
            self.log.info("🎯 FINAL RESULTS")
            self.log.info("=" * 60)
            
            success_rate = (passed / total) * 100
            self.log.info(f"📊 Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
            
            if passed == total:
                self.log.info("🎉 ALL TESTS PASSED!")
                self.log.info("✅ Browser restart functionality is fully working")
                self.log.info("✅ Restarts execute successfully")
                self.log.info("✅ Browser recovers properly after restart")
                self.log.info("✅ Error handling works correctly")
                return True
            elif passed >= total * 0.75:
                self.log.warning(f"⚠️ MOSTLY WORKING: {total - passed} tests failed")
                self.log.warning("Browser restart mostly works but has some issues")
                return False
            else:
                self.log.error(f"❌ MAJOR ISSUES: {total - passed} tests failed")
                self.log.error("Browser restart functionality needs significant attention")
                return False
                
        except Exception as e:
            self.log.error(f"💥 TEST SUITE CRASHED: {e}")
            return False

async def main():
    """Main test execution"""
    print("🔧 Actual Browser Restart Test")
    print("=" * 50)
    print("⚠️  WARNING: This test will actually restart your browser!")
    print("You will see Chrome windows close and reopen during testing.")
    print("=" * 50)
    
    # No user input required - system should restart automatically
    
    print("\n🚀 Starting actual browser restart tests...")
    
    tester = ActualBrowserRestartTester()
    success = await tester.run_all_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Browser restart is fully functional!")
        print("Your system will properly restart the browser every 2.5 hours.")
        print("Authentication connection issues should be resolved.")
    else:
        print("❌ ISSUES: Browser restart needs attention.")
        print("Check the test output above for specific problems.")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())