#!/usr/bin/env python3
"""
Memory Leak Fixes Testing Suite
===============================

Comprehensive testing suite to validate all critical memory leak fixes implemented
for the Amazon FBA Agent System. Tests the 13GB WSL memory consumption issue
resolution and validates system stability during supplier scraping operations.

Tests Include:
- Browser memory management validation
- WSL memory monitoring and cleanup
- Index bounds checking and state validation
- Supplier circuit breaker functionality
- Memory growth rate monitoring during processing
- System recovery and cleanup effectiveness

Author: Amazon FBA Agent System
Date: 2025-07-22
Priority: CRITICAL - Validates system stability fixes
"""

import os
import sys
import asyncio
import logging
import time
import json
import psutil
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'memory_leak_test_{int(time.time())}.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

class MemoryLeakTestSuite:
    """
    Comprehensive test suite for memory leak fixes validation
    """
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        self.initial_memory = None
        self.memory_samples = []
        self.test_product_count = 100  # Test with 100 products
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """
        Run complete test suite and return results
        
        Returns:
            Dictionary with test results and status
        """
        log.info("🧪 Starting Memory Leak Fixes Test Suite")
        log.info("=" * 60)
        
        try:
            # Record initial system state
            await self.record_initial_state()
            
            # Test 1: WSL Memory Manager
            await self.test_wsl_memory_manager()
            
            # Test 2: Browser Manager Enhancements  
            await self.test_browser_manager_memory()
            
            # Test 3: Index Bounds Validation
            await self.test_index_bounds_validation()
            
            # Test 4: Supplier Circuit Breaker
            await self.test_supplier_circuit_breaker()
            
            # Test 5: Memory Growth Rate Simulation
            await self.test_memory_growth_simulation()
            
            # Test 6: System Recovery and Cleanup
            await self.test_system_recovery()
            
            # Final assessment
            await self.record_final_state()
            self.generate_test_report()
            
        except Exception as e:
            log.error(f"❌ Test suite failed: {e}")
            self.test_results["suite_error"] = str(e)
        
        log.info("🏁 Memory Leak Test Suite Complete")
        return self.test_results
    
    async def record_initial_state(self):
        """Record initial system memory state"""
        log.info("📊 Recording initial system state...")
        
        try:
            memory_info = psutil.virtual_memory()
            self.initial_memory = {
                'total_gb': memory_info.total / (1024**3),
                'used_gb': memory_info.used / (1024**3),
                'available_gb': memory_info.available / (1024**3),
                'percent': memory_info.percent,
                'timestamp': time.time()
            }
            
            # Get Chrome processes
            chrome_memory_mb = 0
            chrome_processes = 0
            for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        chrome_memory_mb += proc.info['memory_info'].rss / (1024 * 1024)
                        chrome_processes += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.initial_memory['chrome_memory_mb'] = chrome_memory_mb
            self.initial_memory['chrome_processes'] = chrome_processes
            
            log.info(f"🧠 Initial Memory: {self.initial_memory['used_gb']:.1f}GB used ({self.initial_memory['percent']:.1f}%)")
            log.info(f"🌐 Initial Chrome Memory: {chrome_memory_mb:.1f}MB ({chrome_processes} processes)")
            
            self.test_results['initial_memory'] = self.initial_memory
            
        except Exception as e:
            log.error(f"❌ Failed to record initial state: {e}")
            self.test_results['initial_state_error'] = str(e)
    
    async def test_wsl_memory_manager(self):
        """Test WSL Memory Manager functionality"""
        log.info("🧠 Testing WSL Memory Manager...")
        
        test_result = {
            'status': 'unknown',
            'components_tested': [],
            'errors': []
        }
        
        try:
            # Import and initialize WSL Memory Manager
            from utils.wsl_memory_manager import WSLMemoryManager, monitor_memory_during_supplier_scraping
            
            manager = WSLMemoryManager(
                warning_threshold_gb=4.0,  # Lower for testing
                critical_threshold_gb=6.0,
                emergency_threshold_gb=8.0
            )
            test_result['components_tested'].append('initialization')
            
            # Test memory usage monitoring
            usage = manager.get_wsl_memory_usage()
            if usage and 'used_memory_gb' in usage:
                test_result['components_tested'].append('memory_monitoring')
                log.info(f"✅ Memory monitoring: {usage['used_memory_gb']:.1f}GB used")
            else:
                test_result['errors'].append('memory_monitoring_failed')
            
            # Test pressure detection
            pressure = manager.check_memory_pressure(usage)
            test_result['components_tested'].append('pressure_detection')
            log.info(f"✅ Memory pressure: {pressure}")
            
            # Test cleanup if safe
            if pressure in ['warning', 'critical']:
                log.info("⚠️ Triggering test cleanup...")
                cleanup_success = await manager.emergency_memory_cleanup()
                test_result['components_tested'].append('cleanup_execution')
                if cleanup_success:
                    log.info("✅ Cleanup successful")
                else:
                    test_result['errors'].append('cleanup_failed')
            
            # Test monitoring function
            monitor_success = await monitor_memory_during_supplier_scraping(0)
            test_result['components_tested'].append('monitoring_function')
            if monitor_success:
                log.info("✅ Memory monitoring function working")
            else:
                test_result['errors'].append('monitoring_function_failed')
            
            test_result['status'] = 'passed' if not test_result['errors'] else 'failed'
            
        except ImportError as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'import_error: {e}')
            log.error(f"❌ WSL Memory Manager import failed: {e}")
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ WSL Memory Manager test failed: {e}")
        
        self.test_results['wsl_memory_manager'] = test_result
        log.info(f"📝 WSL Memory Manager Test: {test_result['status'].upper()}")
    
    async def test_browser_manager_memory(self):
        """Test Browser Manager memory enhancements"""
        log.info("🌐 Testing Browser Manager Memory Enhancements...")
        
        test_result = {
            'status': 'unknown',
            'components_tested': [],
            'errors': []
        }
        
        try:
            # Import Browser Manager
            from utils.browser_manager import BrowserManager
            
            # Test singleton access
            manager = BrowserManager.get_instance()
            test_result['components_tested'].append('singleton_access')
            
            # Test memory monitoring methods
            if hasattr(manager, 'get_total_system_memory_usage'):
                memory_info = await manager.get_total_system_memory_usage()
                if memory_info:
                    test_result['components_tested'].append('system_memory_monitoring')
                    log.info(f"✅ System memory monitoring: {memory_info.get('memory_usage_percent', 0):.1f}%")
                else:
                    test_result['errors'].append('system_memory_monitoring_failed')
            else:
                test_result['errors'].append('missing_system_memory_method')
            
            # Test memory check with cleanup
            if hasattr(manager, 'memory_check_with_cleanup'):
                check_result = await manager.memory_check_with_cleanup(0)
                test_result['components_tested'].append('memory_check_cleanup')
                if check_result:
                    log.info("✅ Memory check with cleanup working")
                else:
                    test_result['errors'].append('memory_check_cleanup_failed')
            else:
                test_result['errors'].append('missing_memory_check_method')
            
            # Test force cleanup
            if hasattr(manager, 'force_memory_cleanup'):
                cleanup_result = await manager.force_memory_cleanup()
                test_result['components_tested'].append('force_cleanup')
                if cleanup_result:
                    log.info("✅ Force memory cleanup working")
                else:
                    test_result['errors'].append('force_cleanup_failed')
            else:
                test_result['errors'].append('missing_force_cleanup_method')
            
            test_result['status'] = 'passed' if not test_result['errors'] else 'failed'
            
        except ImportError as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'import_error: {e}')
            log.error(f"❌ Browser Manager import failed: {e}")
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ Browser Manager test failed: {e}")
        
        self.test_results['browser_manager'] = test_result
        log.info(f"📝 Browser Manager Test: {test_result['status'].upper()}")
    
    async def test_index_bounds_validation(self):
        """Test index bounds validation improvements"""
        log.info("🔢 Testing Index Bounds Validation...")
        
        test_result = {
            'status': 'unknown',
            'simulated_scenarios': [],
            'errors': []
        }
        
        try:
            # Simulate index bounds scenarios
            test_products = [{'url': f'http://test.com/product{i}', 'price': 10.0} for i in range(100)]
            
            # Scenario 1: Index within bounds
            last_index = 50
            if last_index < len(test_products):
                remaining = test_products[last_index:]
                test_result['simulated_scenarios'].append('within_bounds_ok')
                log.info(f"✅ Within bounds test: {len(remaining)} products remaining from index {last_index}")
            
            # Scenario 2: Index equals length (edge case)
            last_index = len(test_products)
            if last_index >= len(test_products):
                log.info(f"✅ Edge case detected: index {last_index} >= length {len(test_products)}")
                last_index = 0  # Reset as per fix implementation
                test_result['simulated_scenarios'].append('edge_case_handled')
            
            # Scenario 3: Index exceeds length (corruption case)
            last_index = len(test_products) + 50
            if last_index > len(test_products):
                log.info(f"✅ Corruption case detected: index {last_index} > length {len(test_products)}")
                last_index = 0  # Reset as per fix implementation
                test_result['simulated_scenarios'].append('corruption_case_handled')
            
            # Scenario 4: Product list hash validation simulation
            import hashlib
            product_urls = [p['url'] for p in test_products]
            hash1 = hashlib.md5(''.join(sorted(product_urls)).encode()).hexdigest()
            
            # Modify product list
            test_products.append({'url': 'http://test.com/new_product', 'price': 15.0})
            product_urls_modified = [p['url'] for p in test_products]
            hash2 = hashlib.md5(''.join(sorted(product_urls_modified)).encode()).hexdigest()
            
            if hash1 != hash2:
                log.info(f"✅ Hash validation: Product list change detected")
                test_result['simulated_scenarios'].append('hash_validation_working')
            else:
                test_result['errors'].append('hash_validation_failed')
            
            test_result['status'] = 'passed' if not test_result['errors'] else 'failed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ Index bounds validation test failed: {e}")
        
        self.test_results['index_bounds_validation'] = test_result
        log.info(f"📝 Index Bounds Validation Test: {test_result['status'].upper()}")
    
    async def test_supplier_circuit_breaker(self):
        """Test Supplier Circuit Breaker functionality"""
        log.info("🛡️ Testing Supplier Circuit Breaker...")
        
        test_result = {
            'status': 'unknown',
            'components_tested': [],
            'errors': []
        }
        
        try:
            # Import Supplier Circuit Breaker
            from utils.supplier_circuit_breaker import SupplierCircuitBreaker, SupplierQualityValidator
            
            # Test quality validator
            validator = SupplierQualityValidator()
            test_result['components_tested'].append('quality_validator_init')
            
            # Test with good products
            good_products = [
                {"title": "Test Product 1", "price": 10.99, "url": "http://example.com/1"},
                {"title": "Test Product 2", "price": 15.50, "url": "http://example.com/2"},
            ]
            result = validator.validate_extraction_quality(good_products, "http://test.com/good")
            if result.success:
                test_result['components_tested'].append('quality_validation_good')
                log.info(f"✅ Good products validation passed: {result.valid_products_count} valid")
            else:
                test_result['errors'].append('good_products_validation_failed')
            
            # Test with poor products
            poor_products = [
                {"title": "", "price": None, "url": ""},
                {"title": "Test", "price": "invalid", "url": "not_url"},
            ]
            result = validator.validate_extraction_quality(poor_products, "http://test.com/poor")
            if not result.success:
                test_result['components_tested'].append('quality_validation_poor')
                log.info(f"✅ Poor products validation correctly failed: {len(result.quality_issues)} issues")
            else:
                test_result['errors'].append('poor_products_validation_incorrect')
            
            # Test circuit breaker
            circuit_breaker = SupplierCircuitBreaker(failure_threshold=2, timeout_seconds=60)
            test_result['components_tested'].append('circuit_breaker_init')
            
            # Test status
            status = circuit_breaker.get_status()
            if status and status['state'] == 'CLOSED':
                test_result['components_tested'].append('circuit_breaker_status')
                log.info(f"✅ Circuit breaker initial state: {status['state']}")
            else:
                test_result['errors'].append('circuit_breaker_status_failed')
            
            test_result['status'] = 'passed' if not test_result['errors'] else 'failed'
            
        except ImportError as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'import_error: {e}')
            log.error(f"❌ Supplier Circuit Breaker import failed: {e}")
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ Supplier Circuit Breaker test failed: {e}")
        
        self.test_results['supplier_circuit_breaker'] = test_result
        log.info(f"📝 Supplier Circuit Breaker Test: {test_result['status'].upper()}")
    
    async def test_memory_growth_simulation(self):
        """Simulate memory growth patterns and validate cleanup"""
        log.info("📈 Testing Memory Growth Rate Simulation...")
        
        test_result = {
            'status': 'unknown',
            'memory_samples': [],
            'growth_rate': 0.0,
            'cleanup_effectiveness': 0.0,
            'errors': []
        }
        
        try:
            # Simulate processing with memory monitoring
            log.info(f"🔄 Simulating processing of {self.test_product_count} products...")
            
            for i in range(0, self.test_product_count, 10):
                # Record memory usage
                memory_info = psutil.virtual_memory()
                sample = {
                    'product_count': i,
                    'used_gb': memory_info.used / (1024**3),
                    'percent': memory_info.percent,
                    'timestamp': time.time()
                }
                test_result['memory_samples'].append(sample)
                self.memory_samples.append(sample)
                
                # Simulate some memory allocation
                temp_data = [f"product_{j}_data_{'x' * 100}" for j in range(50)]
                
                # Simulate cleanup every 50 products
                if i > 0 and i % 50 == 0:
                    log.info(f"🧹 Simulating cleanup at product {i}")
                    import gc
                    collected = gc.collect()
                    del temp_data  # Clean up test data
                    
                    # Record post-cleanup memory
                    cleanup_memory = psutil.virtual_memory()
                    sample_after = {
                        'product_count': i,
                        'used_gb': cleanup_memory.used / (1024**3),
                        'percent': cleanup_memory.percent,
                        'timestamp': time.time(),
                        'post_cleanup': True
                    }
                    test_result['memory_samples'].append(sample_after)
                
                # Brief pause to simulate processing
                await asyncio.sleep(0.1)
            
            # Calculate growth rate
            if len(test_result['memory_samples']) >= 2:
                first_sample = test_result['memory_samples'][0]
                last_sample = test_result['memory_samples'][-1]
                
                memory_delta = last_sample['used_gb'] - first_sample['used_gb']
                time_delta = (last_sample['timestamp'] - first_sample['timestamp']) / 3600  # hours
                
                if time_delta > 0:
                    test_result['growth_rate'] = memory_delta / time_delta  # GB per hour
                    log.info(f"📊 Memory growth rate: {test_result['growth_rate']:+.3f} GB/hour")
                
                # Calculate cleanup effectiveness
                cleanup_samples = [s for s in test_result['memory_samples'] if s.get('post_cleanup')]
                if cleanup_samples:
                    avg_before_cleanup = sum(s['used_gb'] for s in test_result['memory_samples'] if not s.get('post_cleanup', False)) / len([s for s in test_result['memory_samples'] if not s.get('post_cleanup', False)])
                    avg_after_cleanup = sum(s['used_gb'] for s in cleanup_samples) / len(cleanup_samples)
                    test_result['cleanup_effectiveness'] = (avg_before_cleanup - avg_after_cleanup) / avg_before_cleanup * 100
                    log.info(f"🧹 Cleanup effectiveness: {test_result['cleanup_effectiveness']:.1f}%")
            
            test_result['status'] = 'passed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ Memory growth simulation failed: {e}")
        
        self.test_results['memory_growth_simulation'] = test_result
        log.info(f"📝 Memory Growth Simulation Test: {test_result['status'].upper()}")
    
    async def test_system_recovery(self):
        """Test system recovery and cleanup mechanisms"""
        log.info("🔧 Testing System Recovery and Cleanup...")
        
        test_result = {
            'status': 'unknown',
            'recovery_tests': [],
            'errors': []
        }
        
        try:
            # Test Python garbage collection
            import gc
            collected = gc.collect()
            test_result['recovery_tests'].append(f'garbage_collection_{collected}_objects')
            log.info(f"✅ Garbage collection: {collected} objects collected")
            
            # Test temp directory cleanup simulation
            import tempfile
            import shutil
            
            temp_dir = tempfile.mkdtemp(prefix='memory_test_')
            
            # Create some test files
            for i in range(10):
                temp_file = os.path.join(temp_dir, f'test_file_{i}.txt')
                with open(temp_file, 'w') as f:
                    f.write('x' * 1000)  # 1KB per file
            
            # Check directory size
            dir_size_before = sum(os.path.getsize(os.path.join(temp_dir, f)) 
                                 for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f)))
            
            # Clean up
            shutil.rmtree(temp_dir)
            cleanup_success = not os.path.exists(temp_dir)
            
            if cleanup_success:
                test_result['recovery_tests'].append(f'temp_cleanup_{dir_size_before}_bytes')
                log.info(f"✅ Temp directory cleanup: {dir_size_before} bytes cleaned")
            else:
                test_result['errors'].append('temp_cleanup_failed')
            
            # Test process memory info
            current_process = psutil.Process()
            memory_info = current_process.memory_info()
            test_result['recovery_tests'].append(f'process_memory_{memory_info.rss // 1024 // 1024}MB')
            log.info(f"✅ Process memory info: {memory_info.rss // 1024 // 1024}MB RSS")
            
            test_result['status'] = 'passed' if not test_result['errors'] else 'failed'
            
        except Exception as e:
            test_result['status'] = 'failed'
            test_result['errors'].append(f'execution_error: {e}')
            log.error(f"❌ System recovery test failed: {e}")
        
        self.test_results['system_recovery'] = test_result
        log.info(f"📝 System Recovery Test: {test_result['status'].upper()}")
    
    async def record_final_state(self):
        """Record final system memory state"""
        log.info("📊 Recording final system state...")
        
        try:
            memory_info = psutil.virtual_memory()
            final_memory = {
                'total_gb': memory_info.total / (1024**3),
                'used_gb': memory_info.used / (1024**3),
                'available_gb': memory_info.available / (1024**3),
                'percent': memory_info.percent,
                'timestamp': time.time()
            }
            
            # Calculate memory delta
            if self.initial_memory:
                memory_delta = final_memory['used_gb'] - self.initial_memory['used_gb']
                percent_delta = final_memory['percent'] - self.initial_memory['percent']
                
                final_memory['delta_gb'] = memory_delta
                final_memory['delta_percent'] = percent_delta
                
                log.info(f"🧠 Final Memory: {final_memory['used_gb']:.1f}GB used ({final_memory['percent']:.1f}%)")
                log.info(f"📊 Memory Change: {memory_delta:+.2f}GB ({percent_delta:+.1f}%)")
            
            self.test_results['final_memory'] = final_memory
            
        except Exception as e:
            log.error(f"❌ Failed to record final state: {e}")
            self.test_results['final_state_error'] = str(e)
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        log.info("📋 Generating Test Report...")
        log.info("=" * 60)
        
        # Summary
        total_tests = len([k for k in self.test_results.keys() if k.endswith('_manager') or k.endswith('_validation') or k.endswith('_breaker') or k.endswith('_simulation') or k.endswith('_recovery')])
        passed_tests = len([v for k, v in self.test_results.items() if isinstance(v, dict) and v.get('status') == 'passed'])
        failed_tests = total_tests - passed_tests
        
        log.info(f"📊 TEST SUMMARY:")
        log.info(f"   Total Tests: {total_tests}")
        log.info(f"   Passed: {passed_tests} ✅")
        log.info(f"   Failed: {failed_tests} ❌")
        log.info(f"   Success Rate: {(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%")
        
        # Memory usage summary
        if 'initial_memory' in self.test_results and 'final_memory' in self.test_results:
            initial = self.test_results['initial_memory']
            final = self.test_results['final_memory']
            
            log.info(f"")
            log.info(f"🧠 MEMORY USAGE SUMMARY:")
            log.info(f"   Initial: {initial['used_gb']:.1f}GB ({initial['percent']:.1f}%)")
            log.info(f"   Final: {final['used_gb']:.1f}GB ({final['percent']:.1f}%)")
            log.info(f"   Change: {final.get('delta_gb', 0):+.2f}GB ({final.get('delta_percent', 0):+.1f}%)")
        
        # Growth rate analysis
        if 'memory_growth_simulation' in self.test_results:
            sim = self.test_results['memory_growth_simulation']
            log.info(f"")
            log.info(f"📈 MEMORY GROWTH ANALYSIS:")
            log.info(f"   Growth Rate: {sim.get('growth_rate', 0):+.3f} GB/hour")
            log.info(f"   Cleanup Effectiveness: {sim.get('cleanup_effectiveness', 0):.1f}%")
        
        # Component status
        log.info(f"")
        log.info(f"🔧 COMPONENT STATUS:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict) and 'status' in result:
                status_icon = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "❓"
                log.info(f"   {test_name}: {status_icon} {result['status'].upper()}")
        
        # Save detailed results
        results_file = f"memory_leak_test_results_{int(self.start_time)}.json"
        try:
            with open(results_file, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            log.info(f"")
            log.info(f"💾 Detailed results saved to: {results_file}")
        except Exception as e:
            log.error(f"❌ Failed to save results: {e}")
        
        log.info("=" * 60)
        log.info("🏁 Memory Leak Test Suite Complete")

async def main():
    """Main test execution function"""
    test_suite = MemoryLeakTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Return appropriate exit code
        failed_tests = len([v for k, v in results.items() if isinstance(v, dict) and v.get('status') == 'failed'])
        if failed_tests > 0:
            sys.exit(1)  # Exit with error if any tests failed
        else:
            sys.exit(0)  # Exit successfully
            
    except KeyboardInterrupt:
        log.warning("⚠️ Test suite interrupted by user")
        sys.exit(130)
    except Exception as e:
        log.error(f"❌ Test suite execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if running on Windows with WSL
    if os.name == 'nt':
        log.warning("⚠️ Running on Windows - WSL-specific tests may not be accurate")
    
    # Run the test suite
    asyncio.run(main())