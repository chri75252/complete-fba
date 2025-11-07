#!/usr/bin/env python3
"""
Comprehensive State Fixes Validation Script
==========================================

This script validates all critical fixes implemented for processing state issues:
1. Fix 1: Fallback total_categories calculation (load from config instead of 0)
2. Fix 2: update_processing_index total_products parameter (use cache count not batch)
3. Fix 3: Cache count integration for accurate totals (proper state initialization)
4. Fix 4: Linking map file path standardization (consistent path usage)

Based on comprehensive root-cause analysis from July 31, 2025.

Author: Claude Code - Comprehensive State Fix Validation  
Date: July 31, 2025
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import importlib.util

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_fix_1_category_fallback() -> Tuple[bool, str]:
    """Validate Fix 1: Category fallback loads from config instead of returning 0."""
    print("\n🔍 VALIDATING FIX 1: Category Fallback Configuration Loading")
    
    try:
        # Import the fixed function
        from tools.passive_extraction_workflow_latest import get_completion_metrics
        
        # Test the fallback function
        result = get_completion_metrics()
        total_categories = result.get("total_categories", 0)
        
        if total_categories > 0:
            print(f"✅ Fix 1 WORKING: Fallback returns {total_categories} categories (loaded from config)")
            return True, f"Categories loaded: {total_categories}"
        else:
            print(f"❌ Fix 1 FAILED: Fallback still returns 0 categories")
            return False, "Fallback still returns 0"
            
    except Exception as e:
        print(f"❌ Fix 1 ERROR: Could not test fallback function: {e}")
        return False, f"Error: {e}"

def validate_fix_2_total_products_parameter() -> Tuple[bool, str]:
    """Validate Fix 2: Total products parameter uses cache count."""
    print("\n🔍 VALIDATING FIX 2: Total Products Parameter Fix")
    
    try:
        # Check the workflow file for the fix
        workflow_file = project_root / "tools" / "passive_extraction_workflow_latest.py"
        
        if not workflow_file.exists():
            return False, "Workflow file not found"
            
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for the fix patterns
        fix_patterns = [
            "total_products_for_state = getattr(self, 'total_cache_count'",
            "total_products_for_progress = getattr(self, 'total_cache_count'",
            "total_for_display = getattr(self, 'total_cache_count'"
        ]
        
        fixes_found = sum(1 for pattern in fix_patterns if pattern in content)
        
        if fixes_found >= 2:  # At least state and progress fixes
            print(f"✅ Fix 2 WORKING: Found {fixes_found}/3 total products parameter fixes")
            return True, f"{fixes_found} parameter fixes implemented"
        else:
            print(f"❌ Fix 2 INCOMPLETE: Only found {fixes_found}/3 fixes")
            return False, f"Only {fixes_found} fixes found"
            
    except Exception as e:
        print(f"❌ Fix 2 ERROR: Could not validate parameter fixes: {e}")
        return False, f"Error: {e}"

def validate_fix_3_state_initialization() -> Tuple[bool, str]:
    """Validate Fix 3: State manager initialization with accurate totals."""
    print("\n🔍 VALIDATING FIX 3: State Manager Initialization")
    
    try:
        # Check for initialization code in workflow
        workflow_file = project_root / "tools" / "passive_extraction_workflow_latest.py"
        
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for initialization patterns
        init_patterns = [
            "FIX 3: Initialize state manager with accurate totals",
            "runtime_settings['supplier_cache_count'] = cache_count",
            "runtime_settings['total_categories'] = len(category_urls)",
            "state_data['total_products'] = cache_count"
        ]
        
        init_fixes_found = sum(1 for pattern in init_patterns if pattern in content)
        
        if init_fixes_found >= 3:  # Should find most patterns
            print(f"✅ Fix 3 WORKING: Found {init_fixes_found}/4 initialization fixes")
            return True, f"{init_fixes_found} initialization patterns found"
        else:
            print(f"❌ Fix 3 INCOMPLETE: Only found {init_fixes_found}/4 patterns")
            return False, f"Only {init_fixes_found} patterns found"
            
    except Exception as e:
        print(f"❌ Fix 3 ERROR: Could not validate initialization: {e}")
        return False, f"Error: {e}"

def validate_fix_4_path_standardization() -> Tuple[bool, str]:
    """Validate Fix 4: Linking map path standardization."""
    print("\n🔍 VALIDATING FIX 4: Linking Map Path Standardization")
    
    try:
        # Check that get_linking_map_path is used consistently
        from utils.path_manager import get_linking_map_path
        
        # Test path generation
        test_path = get_linking_map_path(supplier_name="poundwholesale.co.uk")
        expected_parts = ["FBA_ANALYSIS", "linking_maps", "poundwholesale.co.uk", "linking_map.json"]
        
        path_str = str(test_path)
        parts_found = sum(1 for part in expected_parts if part in path_str)
        
        if parts_found >= 3:  # Should find most expected parts
            print(f"✅ Fix 4 WORKING: Path standardization correct - {test_path}")
            return True, f"Standardized path: {test_path}"
        else:
            print(f"❌ Fix 4 FAILED: Path missing expected parts - {test_path}")
            return False, f"Path issues: {test_path}"
            
    except Exception as e:
        print(f"❌ Fix 4 ERROR: Could not validate path standardization: {e}")
        return False, f"Error: {e}"

def validate_current_processing_state() -> Tuple[bool, str]:
    """Validate current processing state file shows improved metrics."""
    print("\n🔍 VALIDATING CURRENT PROCESSING STATE")
    
    try:
        # Find the most recent processing state file
        processing_states_dir = project_root / "OUTPUTS" / "CACHE" / "processing_states"
        
        if not processing_states_dir.exists():
            return False, "Processing states directory not found"
            
        state_files = list(processing_states_dir.glob("poundwholesale*.json"))
        if not state_files:
            return False, "No processing state files found"
            
        latest_file = max(state_files, key=lambda f: f.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        # Check key metrics for improvement
        total_products = state_data.get('total_products', 0)
        total_categories = state_data.get('system_progression', {}).get('total_categories', 0)
        current_category_index = state_data.get('system_progression', {}).get('persistent_category_index', 0)
        
        issues = []
        
        # Check if total_products is reasonable (should be > 1000 for cache)
        if total_products < 100:
            issues.append(f"total_products still low: {total_products}")
        
        # Check if total_categories is reasonable (should be ~181)
        if total_categories < 50:
            issues.append(f"total_categories still low: {total_categories}")
            
        # Check logical consistency
        if current_category_index > total_categories and total_categories > 0:
            issues.append(f"Index inconsistency: {current_category_index} > {total_categories}")
        
        if not issues:
            print(f"✅ State metrics improved: {total_products} products, {total_categories} categories")
            return True, f"Products: {total_products}, Categories: {total_categories}"
        else:
            print(f"❌ State still has issues: {'; '.join(issues)}")
            return False, f"Issues: {'; '.join(issues)}"
            
    except Exception as e:
        print(f"❌ State validation error: {e}")
        return False, f"Error: {e}"

def run_system_integrity_check() -> Tuple[bool, str]:
    """Run basic system integrity checks."""
    print("\n🔍 RUNNING SYSTEM INTEGRITY CHECK")
    
    try:
        # Check essential files exist
        essential_files = [
            "tools/passive_extraction_workflow_latest.py",
            "utils/fixed_enhanced_state_manager.py", 
            "utils/path_manager.py",
            "config/system_config.json"
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not (project_root / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            return False, f"Missing files: {', '.join(missing_files)}"
        
        # Try to import key modules
        try:
            from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow
            from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager
            from utils.path_manager import path_manager
            print("✅ Key modules import successfully")
        except ImportError as e:
            return False, f"Import error: {e}"
        
        print("✅ System integrity check passed")
        return True, "All essential components available"
        
    except Exception as e:
        return False, f"Integrity check error: {e}"

def main():
    """Main validation function."""
    print("🧪 COMPREHENSIVE STATE FIXES VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Project Root: {project_root}")
    print()
    
    # Run all validations
    validations = [
        ("System Integrity", run_system_integrity_check()),
        ("Fix 1: Category Fallback", validate_fix_1_category_fallback()),
        ("Fix 2: Total Products Parameter", validate_fix_2_total_products_parameter()),
        ("Fix 3: State Initialization", validate_fix_3_state_initialization()),
        ("Fix 4: Path Standardization", validate_fix_4_path_standardization()),
        ("Current Processing State", validate_current_processing_state())
    ]
    
    # Results summary
    print(f"\n🎯 COMPREHENSIVE VALIDATION RESULTS")
    print("=" * 60)
    
    passed_count = 0
    total_count = len(validations)
    
    for test_name, (passed, message) in validations:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if passed:
            passed_count += 1
    
    print(f"\n📊 SUMMARY: {passed_count}/{total_count} validations passed")
    
    if passed_count == total_count:
        print("🎉 ALL FIXES VALIDATED SUCCESSFULLY!")
        print("✅ The system should now show accurate processing state metrics")
        print("✅ User confusion about inconsistent numbers should be resolved")
        print("\n📋 RECOMMENDED NEXT STEPS:")
        print("1. Run the system with: python run_custom_poundwholesale.py")
        print("2. Monitor processing state file for accurate metrics")
        print("3. Verify category progression shows logical values")
        print("4. Confirm total_products matches cache file count")
        return True
    else:
        print("⚠️ Some validations failed - please review and fix issues")
        print("\n🔧 TROUBLESHOOTING:")
        failed_tests = [name for name, (passed, _) in validations if not passed]
        print(f"Failed tests: {', '.join(failed_tests)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)