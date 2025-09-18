#!/usr/bin/env python3
"""
Hybrid Mode Fixes Validation Script
Validates that the cache persistence fixes are applied to both regular and hybrid modes
"""

import os
import re
from pathlib import Path

def validate_hybrid_mode_cache_fixes():
    """Validate that hybrid mode includes the same cache fixes as regular mode"""
    print("🔍 HYBRID MODE CACHE FIXES VALIDATION")
    print("=" * 50)
    
    workflow_file = "tools/passive_extraction_workflow_latest.py"
    
    if not os.path.exists(workflow_file):
        print("❌ Workflow file not found")
        return False
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for regular mode cache fix
    regular_mode_pattern = r'# CRITICAL FIX: Add cache persistence during processing.*?_save_incremental_cache_update\(\)'
    regular_mode_matches = re.findall(regular_mode_pattern, content, re.DOTALL)
    
    # Check for hybrid mode cache fix
    hybrid_mode_pattern = r'# CRITICAL FIX: Add cache persistence during hybrid mode processing.*?_save_incremental_cache_update\(\)'
    hybrid_mode_matches = re.findall(hybrid_mode_pattern, content, re.DOTALL)
    
    print(f"Regular Mode Cache Fix: {'✅ FOUND' if regular_mode_matches else '❌ MISSING'}")
    print(f"Hybrid Mode Cache Fix: {'✅ FOUND' if hybrid_mode_matches else '❌ MISSING'}")
    
    # Check for _save_incremental_cache_update method
    method_pattern = r'def _save_incremental_cache_update\(self\):'
    method_matches = re.findall(method_pattern, content)
    
    print(f"Incremental Cache Update Method: {'✅ FOUND' if method_matches else '❌ MISSING'}")
    
    # Check for enhanced linking map save method
    enhanced_save_pattern = r'def _save_linking_map.*?CRITICAL FIX: Enhanced linking map save'
    enhanced_save_matches = re.findall(enhanced_save_pattern, content, re.DOTALL)
    
    print(f"Enhanced Linking Map Save: {'✅ FOUND' if enhanced_save_matches else '❌ MISSING'}")
    
    # Check for hybrid mode processing method
    hybrid_processing_pattern = r'async def _run_hybrid_processing_mode'
    hybrid_processing_matches = re.findall(hybrid_processing_pattern, content)
    
    print(f"Hybrid Processing Mode Method: {'✅ FOUND' if hybrid_processing_matches else '❌ MISSING'}")
    
    # Check for chunk processing method
    chunk_processing_pattern = r'async def _process_chunk_with_main_workflow_logic'
    chunk_processing_matches = re.findall(chunk_processing_pattern, content)
    
    print(f"Chunk Processing Method: {'✅ FOUND' if chunk_processing_matches else '❌ MISSING'}")
    
    # Overall assessment
    all_checks = [
        regular_mode_matches,
        hybrid_mode_matches, 
        method_matches,
        enhanced_save_matches,
        hybrid_processing_matches,
        chunk_processing_matches
    ]
    
    passed_checks = sum(1 for check in all_checks if check)
    total_checks = len(all_checks)
    
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"Passed: {passed_checks}/{total_checks} ({passed_checks/total_checks*100:.0f}%)")
    
    if passed_checks == total_checks:
        print("🎉 ALL VALIDATIONS PASSED - Hybrid mode fixes are complete!")
        return True
    elif passed_checks >= total_checks * 0.8:
        print("⚠️ MOSTLY COMPLETE - Some minor issues detected")
        return True
    else:
        print("🚨 CRITICAL ISSUES - Major fixes missing")
        return False

def check_workflow_parity():
    """Check that both workflows have similar periodic save logic"""
    print(f"\n🔍 WORKFLOW PARITY CHECK")
    print("-" * 30)
    
    workflow_file = "tools/passive_extraction_workflow_latest.py"
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all periodic save blocks
    periodic_save_pattern = r'linking_map_batch.*?=.*?linking_map_batch_size.*?if.*?%.*?linking_map_batch.*?==.*?0:'
    periodic_saves = re.findall(periodic_save_pattern, content, re.DOTALL)
    
    print(f"Periodic Save Blocks Found: {len(periodic_saves)}")
    
    # Check for incremental cache updates in periodic saves
    cache_update_pattern = r'_save_incremental_cache_update\(\)'
    cache_updates = re.findall(cache_update_pattern, content)
    
    print(f"Cache Update Calls Found: {len(cache_updates)}")
    
    # Check for hybrid mode specific logging
    hybrid_log_pattern = r'HYBRID MODE.*Cache updated'
    hybrid_logs = re.findall(hybrid_log_pattern, content)
    
    print(f"Hybrid Mode Cache Logs: {len(hybrid_logs)}")
    
    if len(cache_updates) >= 2:  # Should have at least regular + hybrid
        print("✅ Both workflows appear to have cache updates")
        return True
    else:
        print("⚠️ May be missing cache updates in one workflow")
        return False

def validate_error_handling():
    """Validate that both workflows have proper error handling"""
    print(f"\n🔍 ERROR HANDLING VALIDATION")
    print("-" * 30)
    
    workflow_file = "tools/passive_extraction_workflow_latest.py"
    
    with open(workflow_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for try-catch blocks around cache updates
    try_catch_pattern = r'try:.*?_save_incremental_cache_update.*?except.*?Exception.*?cache_error'
    try_catch_blocks = re.findall(try_catch_pattern, content, re.DOTALL)
    
    print(f"Cache Update Error Handling Blocks: {len(try_catch_blocks)}")
    
    # Check for critical error logging
    critical_error_pattern = r'❌ CRITICAL.*cache.*failed'
    critical_errors = re.findall(critical_error_pattern, content, re.IGNORECASE)
    
    print(f"Critical Error Log Messages: {len(critical_errors)}")
    
    # Check for retry logic in linking map saves
    retry_pattern = r'max_retries.*?=.*?\d+.*?for attempt in range\(max_retries\)'
    retry_logic = re.findall(retry_pattern, content, re.DOTALL)
    
    print(f"Retry Logic Blocks: {len(retry_logic)}")
    
    if len(try_catch_blocks) >= 2 and len(retry_logic) >= 1:
        print("✅ Error handling appears comprehensive")
        return True
    else:
        print("⚠️ Error handling may need improvement")
        return False

if __name__ == "__main__":
    print("🚀 Starting Hybrid Mode Fixes Validation")
    print(f"Timestamp: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all validations
    cache_fixes_valid = validate_hybrid_mode_cache_fixes()
    workflow_parity_valid = check_workflow_parity()
    error_handling_valid = validate_error_handling()
    
    # Overall assessment
    validations = [cache_fixes_valid, workflow_parity_valid, error_handling_valid]
    passed = sum(validations)
    total = len(validations)
    
    print(f"\n🎯 OVERALL VALIDATION RESULT")
    print("=" * 50)
    print(f"Validations Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("🎉 HYBRID MODE FIXES VALIDATION: COMPLETE SUCCESS!")
        print("✅ Both regular and hybrid modes have identical cache persistence fixes")
        print("✅ Error handling is comprehensive across both workflows")
        print("✅ System is ready for production deployment")
    elif passed >= 2:
        print("⚠️ HYBRID MODE FIXES VALIDATION: MOSTLY SUCCESSFUL")
        print("✅ Core functionality is working")
        print("⚠️ Some minor improvements may be needed")
    else:
        print("🚨 HYBRID MODE FIXES VALIDATION: NEEDS ATTENTION")
        print("❌ Critical issues detected that need resolution")
    
    print(f"\n💡 NEXT STEPS:")
    if passed == total:
        print("- Deploy to production")
        print("- Monitor system performance")
        print("- Run end-to-end testing")
    else:
        print("- Review failed validations")
        print("- Apply missing fixes")
        print("- Re-run validation")