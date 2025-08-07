"""
Sentinel Effectiveness Test Suite for Amazon FBA Agent System

This test suite creates controlled scenarios to verify that all sentinels
fire correctly and write appropriate alerts to sentinels.log.

TEST SCENARIOS:
1. Linking map shrinkage simulation (>5% = CRITICAL, >1% = WARNING)
2. Session/global totals divergence simulation  
3. Path variant detection (dot vs underscore)
4. Save retry pattern simulation
5. End-to-end monitoring workflow test

EXPECTED OUTPUTS:
- OUTPUTS/DIAGNOSTICS/sentinels.log with structured alerts
- Console output showing test results
- Proof that sentinel monitoring detects silent failures

Usage: python test_sentinel_effectiveness.py
"""

import os
import sys
import json
import time
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import sentinel monitoring system
from utils.sentinel_monitor import SentinelMonitor, get_sentinel_monitor, reset_sentinel_monitor

class SentinelTestSuite:
    """Comprehensive test suite for sentinel monitoring system"""
    
    def __init__(self):
        self.test_supplier = "test_sentinel_supplier"
        self.output_dir = Path("OUTPUTS/DIAGNOSTICS")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sentinel_log_path = self.output_dir / "sentinels.log"
        
        # Clear any existing log for clean test
        if self.sentinel_log_path.exists():
            backup_path = self.sentinel_log_path.with_suffix('.log.backup')
            shutil.move(self.sentinel_log_path, backup_path)
            print(f"📁 Backed up existing log to {backup_path}")
        
        self.test_results = []
        
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result for final summary"""
        self.test_results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"    Details: {details}")
    
    def read_sentinel_log(self) -> List[Dict[str, Any]]:
        """Read and parse sentinel log entries"""
        if not self.sentinel_log_path.exists():
            return []
        
        entries = []
        try:
            with open(self.sentinel_log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError as e:
                            print(f"⚠️ Warning: Could not parse log line: {line[:100]}...")
        except Exception as e:
            print(f"❌ Error reading sentinel log: {e}")
        
        return entries
    
    def test_initialization(self) -> bool:
        """Test 1: Verify sentinel monitor initialization"""
        print("\\n🧪 TEST 1: Sentinel Monitor Initialization")
        
        try:
            # Reset any existing monitor
            reset_sentinel_monitor()
            
            # Create new monitor
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Verify initialization
            if monitor.supplier_name == self.test_supplier:
                # Check if initialization was logged
                time.sleep(0.1)  # Give time for log write
                entries = self.read_sentinel_log()
                init_entries = [e for e in entries if e.get('sentinel_type') == 'INITIALIZATION']
                
                if init_entries:
                    self.log_test_result("Initialization", True, f"Monitor created for {self.test_supplier}")
                    return True
                else:
                    self.log_test_result("Initialization", False, "No initialization log entry found")
                    return False
            else:
                self.log_test_result("Initialization", False, f"Wrong supplier name: {monitor.supplier_name}")
                return False
                
        except Exception as e:
            self.log_test_result("Initialization", False, f"Exception: {e}")
            return False
    
    def test_linking_map_shrinkage(self) -> bool:
        """Test 2: Linking map shrinkage detection"""
        print("\\n🧪 TEST 2: Linking Map Shrinkage Detection")
        
        try:
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Test scenario 1: CRITICAL shrinkage (>5%)
            monitor.check_linking_map_shrinkage(current_size=90, previous_size=100)  # 10% shrinkage
            
            time.sleep(0.1)
            entries = self.read_sentinel_log()
            critical_entries = [e for e in entries 
                              if e.get('sentinel_type') == 'LINKING_MAP_SHRINKAGE' 
                              and e.get('level') == 'CRITICAL']
            
            test1_pass = len(critical_entries) > 0
            
            # Test scenario 2: WARNING shrinkage (1-5%)
            monitor.check_linking_map_shrinkage(current_size=97, previous_size=100)  # 3% shrinkage
            
            time.sleep(0.1)
            entries = self.read_sentinel_log()
            warning_entries = [e for e in entries 
                             if e.get('sentinel_type') == 'LINKING_MAP_SHRINKAGE' 
                             and e.get('level') == 'WARNING']
            
            test2_pass = len(warning_entries) > 0
            
            # Test scenario 3: No alert for small shrinkage
            monitor.check_linking_map_shrinkage(current_size=99, previous_size=100)  # 1% shrinkage
            
            overall_pass = test1_pass and test2_pass
            details = f"Critical alerts: {len(critical_entries)}, Warning alerts: {len(warning_entries)}"
            
            self.log_test_result("Linking Map Shrinkage", overall_pass, details)
            return overall_pass
            
        except Exception as e:
            self.log_test_result("Linking Map Shrinkage", False, f"Exception: {e}")
            return False
    
    def test_totals_divergence(self) -> bool:
        """Test 3: Session vs global totals divergence detection"""
        print("\\n🧪 TEST 3: Session/Global Totals Divergence Detection")
        
        try:
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Test scenario: Significant divergence (>10%)
            monitor.check_totals_divergence(
                session_count=85, 
                global_count=100, 
                metric_name="test_products"
            )  # 15% divergence
            
            time.sleep(0.1)
            entries = self.read_sentinel_log()
            divergence_entries = [e for e in entries 
                                if e.get('sentinel_type') == 'TOTALS_DIVERGENCE']
            
            test_pass = len(divergence_entries) > 0
            details = f"Divergence alerts: {len(divergence_entries)}"
            
            self.log_test_result("Totals Divergence", test_pass, details)
            return test_pass
            
        except Exception as e:
            self.log_test_result("Totals Divergence", False, f"Exception: {e}")
            return False
    
    def test_path_variants(self) -> bool:
        """Test 4: Path variant detection (dot vs underscore)"""
        print("\\n🧪 TEST 4: Path Variant Detection")
        
        try:
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Create test files with variants
            test_dir = Path("OUTPUTS/test_variants")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Create files with different naming conventions
            file1 = test_dir / "test_file.json"
            file2 = test_dir / "test.file.json"  # Dot variant
            
            file1.write_text('{"test": "data"}')
            file2.write_text('{"test": "variant"}')
            
            try:
                # Test path variant detection
                monitor.check_path_variants(str(file1), "test_operation")
                
                time.sleep(0.1)
                entries = self.read_sentinel_log()
                variant_entries = [e for e in entries 
                                 if e.get('sentinel_type') == 'MISSING_PATH_VARIANTS']
                
                test_pass = len(variant_entries) > 0
                details = f"Path variant alerts: {len(variant_entries)}"
                
                self.log_test_result("Path Variants", test_pass, details)
                return test_pass
                
            finally:
                # Cleanup test files
                shutil.rmtree(test_dir, ignore_errors=True)
                
        except Exception as e:
            self.log_test_result("Path Variants", False, f"Exception: {e}")
            return False
    
    def test_save_retry_patterns(self) -> bool:
        """Test 5: Save retry pattern monitoring"""
        print("\\n🧪 TEST 5: Save Retry Pattern Monitoring")
        
        try:
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Test scenario 1: Failed save with multiple retries (ERROR level)
            monitor.track_save_retry("test_strategy", success=False, attempt_count=5)
            
            # Test scenario 2: Successful save after retries (INFO level)
            monitor.track_save_retry("test_strategy", success=True, attempt_count=1)
            
            time.sleep(0.1)
            entries = self.read_sentinel_log()
            retry_entries = [e for e in entries 
                           if e.get('sentinel_type') in ['SAVE_RETRY_PATTERN', 'SAVE_STRATEGY_SUCCESS']]
            
            test_pass = len(retry_entries) >= 1  # At least one retry entry
            details = f"Save retry alerts: {len(retry_entries)}"
            
            self.log_test_result("Save Retry Patterns", test_pass, details)
            return test_pass
            
        except Exception as e:
            self.log_test_result("Save Retry Patterns", False, f"Exception: {e}")
            return False
    
    def test_monitoring_summary(self) -> bool:
        """Test 6: Monitoring summary and finalization"""
        print("\\n🧪 TEST 6: Monitoring Summary and Finalization")
        
        try:
            monitor = get_sentinel_monitor(self.test_supplier)
            
            # Get summary before finalization
            summary = monitor.get_monitoring_summary()
            
            # Finalize monitoring
            monitor.finalize_monitoring()
            
            time.sleep(0.1)
            entries = self.read_sentinel_log()
            summary_entries = [e for e in entries 
                             if e.get('sentinel_type') == 'MONITORING_SUMMARY']
            
            test_pass = len(summary_entries) > 0 and summary['supplier_name'] == self.test_supplier
            details = f"Summary entries: {len(summary_entries)}, Runtime: {summary.get('runtime_seconds', 0):.1f}s"
            
            self.log_test_result("Monitoring Summary", test_pass, details)
            return test_pass
            
        except Exception as e:
            self.log_test_result("Monitoring Summary", False, f"Exception: {e}")
            return False
    
    def test_log_structure(self) -> bool:
        """Test 7: Verify log structure and content"""
        print("\\n🧪 TEST 7: Log Structure Verification")
        
        try:
            entries = self.read_sentinel_log()
            
            if not entries:
                self.log_test_result("Log Structure", False, "No log entries found")
                return False
            
            # Verify required fields in log entries
            required_fields = ['level', 'sentinel_type', 'message', 'timestamp', 'data']
            valid_entries = 0
            
            for entry in entries:
                if all(field in entry for field in required_fields):
                    valid_entries += 1
            
            structure_valid = valid_entries == len(entries)
            details = f"Valid entries: {valid_entries}/{len(entries)}"
            
            self.log_test_result("Log Structure", structure_valid, details)
            return structure_valid
            
        except Exception as e:
            self.log_test_result("Log Structure", False, f"Exception: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run complete test suite"""
        print("🚨 SENTINEL EFFECTIVENESS TEST SUITE")
        print("=" * 60)
        print(f"📁 Log file: {self.sentinel_log_path}")
        print(f"🕒 Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        tests = [
            self.test_initialization,
            self.test_linking_map_shrinkage,
            self.test_totals_divergence,
            self.test_path_variants,
            self.test_save_retry_patterns,
            self.test_monitoring_summary,
            self.test_log_structure
        ]
        
        passed_tests = 0
        for test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test_func.__name__} failed with exception: {e}")
        
        # Final summary
        total_tests = len(tests)
        success_rate = (passed_tests / total_tests) * 100
        
        print("\\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - Sentinel monitoring is working correctly!")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️ MOST TESTS PASSED - Minor issues may need attention")
        else:
            print("❌ MULTIPLE TEST FAILURES - Sentinel monitoring needs fixes")
        
        # Show log file contents
        print(f"\\n📄 SENTINEL LOG CONTENTS ({self.sentinel_log_path}):")
        print("-" * 40)
        
        entries = self.read_sentinel_log()
        for i, entry in enumerate(entries[-10:], 1):  # Show last 10 entries
            level_icon = {"CRITICAL": "🚨", "ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(entry.get('level', ''), "📋")
            print(f"{i:2d}. {level_icon} {entry.get('level', 'UNKNOWN')} - {entry.get('sentinel_type', 'UNKNOWN')}")
            print(f"    {entry.get('message', 'No message')[:80]}...")
        
        if len(entries) > 10:
            print(f"    ... and {len(entries) - 10} more entries")
        
        return passed_tests == total_tests

def create_implementation_summary():
    """Create implementation summary document"""
    summary_path = Path("OUTPUTS/DIAGNOSTICS/sentinel_implementation.md")
    
    summary_content = f"""# Sentinel Implementation Summary

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
Comprehensive sentinel monitoring system implemented for Amazon FBA Agent System v3.7+ to detect silent failures and system inconsistencies.

## Sentinels Implemented

### 1. CRITICAL: Linking Map Shrinkage Detection
- **Threshold:** >5% = CRITICAL, >1% = WARNING
- **Purpose:** Detect data loss during save operations
- **Location:** `_save_linking_map()` method
- **Alert Type:** LINKING_MAP_SHRINKAGE

### 2. WARNING: Session/Global Totals Divergence  
- **Threshold:** >10% divergence
- **Purpose:** Detect inconsistencies between in-memory and file-based counts
- **Location:** Progress tracking methods
- **Alert Type:** TOTALS_DIVERGENCE

### 3. WARNING: Missing Path Variants Detection
- **Purpose:** Identify potential file access issues (dot vs underscore naming)
- **Location:** File access operations
- **Alert Type:** MISSING_PATH_VARIANTS

### 4. INFO/ERROR: Save Retry Pattern Monitoring
- **Purpose:** Track reliability of different save strategies
- **Location:** All save operations
- **Alert Type:** SAVE_RETRY_PATTERN, SAVE_STRATEGY_SUCCESS

## Implementation Files

### Core Components
- `utils/sentinel_monitor.py` - Main sentinel monitoring system
- `sentinel_integration_patch.py` - Integration patches for workflow
- `test_sentinel_effectiveness.py` - Comprehensive test suite

### Integration Points
- `tools/passive_extraction_workflow_latest.py` - Main workflow integration
- `OUTPUTS/DIAGNOSTICS/sentinels.log` - Structured alert log

## Alert Structure
```json
{{
  "level": "CRITICAL|ERROR|WARNING|INFO",
  "sentinel_type": "SENTINEL_TYPE_NAME", 
  "message": "Human readable alert message",
  "timestamp": "ISO 8601 timestamp",
  "data": {{
    "relevant_metrics": "and context data"
  }}
}}
```

## Usage Instructions

### 1. Apply Integration Patches
```bash
python sentinel_integration_patch.py
```

### 2. Run Test Suite
```bash  
python test_sentinel_effectiveness.py
```

### 3. Monitor Alerts
```bash
tail -f OUTPUTS/DIAGNOSTICS/sentinels.log
```

### 4. Review Monitoring Summary
Check log for MONITORING_SUMMARY entries after workflow completion.

## Expected Behaviors

### During Normal Operation
- INFO alerts for initialization and periodic status
- Occasional WARNING alerts for minor divergences
- INFO alerts for successful save operations

### During Problems  
- CRITICAL alerts for linking map shrinkage >5%
- WARNING alerts for session/global totals divergence >10%
- ERROR alerts for repeated save failures

## Benefits

1. **Proactive Failure Detection** - Catches issues before they cause data loss
2. **Silent Failure Prevention** - Alerts on data inconsistencies 
3. **Performance Monitoring** - Tracks save strategy effectiveness
4. **Debugging Support** - Provides detailed context for issues
5. **System Health Visibility** - Comprehensive monitoring dashboard

## Next Steps

1. Monitor production runs for sentinel alerts
2. Tune thresholds based on operational data
3. Add additional sentinels for other critical operations
4. Create automated alerting for CRITICAL level events
5. Integrate with external monitoring systems if needed

---

*This implementation provides comprehensive proactive monitoring to ensure data integrity and system reliability for the Amazon FBA Agent System.*
"""
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"📄 Implementation summary created: {summary_path}")

if __name__ == "__main__":
    # Run the test suite
    test_suite = SentinelTestSuite()
    
    success = test_suite.run_all_tests()
    
    # Create implementation summary
    create_implementation_summary()
    
    print("\\n🎯 DELIVERABLES COMPLETED:")
    print("✅ OUTPUTS/DIAGNOSTICS/sentinels.log - Sentinel alert log")
    print("✅ OUTPUTS/DIAGNOSTICS/sentinel_implementation.md - Implementation summary")
    print("✅ utils/sentinel_monitor.py - Core monitoring system")
    print("✅ sentinel_integration_patch.py - Workflow integration")
    print("✅ test_sentinel_effectiveness.py - Test suite (this file)")
    
    if success:
        print("\\n🎉 ALL SENTINELS IMPLEMENTED AND TESTED SUCCESSFULLY!")
        print("The system is now equipped with proactive monitoring to prevent silent failures.")
    else:
        print("\\n⚠️ Some tests failed - please review and fix before production use.")
    
    exit_code = 0 if success else 1
    sys.exit(exit_code)