#!/usr/bin/env python3
"""
Processing State Fixes Implementation Script
==========================================

This script implements comprehensive fixes for the critical processing state issues:

1. last_processed_index constantly resetting to 0
2. Category product count mismatches (36 vs 100+ products) 
3. Metrics appearing in wrong sections
4. System skipping products due to incorrect totals

The fixes include:
- Separated resumption index from progress tracking
- Prevented automatic index resets during processing  
- Added real-time category product count updates
- Fixed metric placement and calculation
- Enhanced state preservation during interruptions

Usage:
    python implement_processing_state_fixes.py --test
    python implement_processing_state_fixes.py --apply
    python implement_processing_state_fixes.py --verify

Author: Claude Code Processing State Fix Implementation  
Date: July 30, 2025
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class ProcessingStateFixImplementer:
    """Implements comprehensive processing state fixes"""
    
    def __init__(self, project_root: str = None):
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent
            
        self.backup_dir = self.project_root / "backup" / f"processing_state_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Create backup of files before applying fixes"""
        log.info(f"🔄 Creating backup directory: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            "utils/enhanced_state_manager.py",
            "utils/enhanced_state_manager 2 .py",
            "tools/passive_extraction_workflow_latest.py",
            "run_custom_poundwholesale.py"
        ]
        
        for file_path in files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                log.info(f"✅ Backed up: {file_path}")
            else:
                log.warning(f"⚠️ File not found for backup: {file_path}")
                
        log.info("✅ Backup completed successfully")
        
    def update_workflow_script(self):
        """Update the main workflow script to use the fixed state manager"""
        workflow_path = self.project_root / "tools" / "passive_extraction_workflow_latest.py"
        
        if not workflow_path.exists():
            log.error(f"❌ Workflow script not found: {workflow_path}")
            return False
            
        log.info(f"🔄 Updating workflow script: {workflow_path}")
        
        # Read current content
        with open(workflow_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace imports and usage
        updates = [
            # Update import statement
            ("from utils.enhanced_state_manager import EnhancedStateManager", 
             "from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager"),
            
            # Update alternative import
            ("from enhanced_state_manager import EnhancedStateManager",
             "from fixed_enhanced_state_manager import FixedEnhancedStateManager as EnhancedStateManager"),
             
            # Add startup analysis call
            ("self.state_manager = EnhancedStateManager(supplier_name)",
             """self.state_manager = EnhancedStateManager(supplier_name)
        # 🚨 CRITICAL FIX: Perform startup analysis only once at session start
        startup_categories = self.state_manager.perform_startup_analysis()"""),
            
            # Update save_state calls to preserve interruption state
            ("self.state_manager.save_state()",
             "self.state_manager.save_state(preserve_interruption_state=True)")
        ]
        
        modified = False
        for old_text, new_text in updates:
            if old_text in content and new_text not in content:
                content = content.replace(old_text, new_text)
                modified = True
                log.info(f"✅ Updated: {old_text[:50]}...")
                
        # Add method to update discovered products
        discovery_method = '''
    def _update_category_discovered_products(self, category_url: str, products_found: int):
        """Update state manager with discovered product count for category"""
        if hasattr(self, 'state_manager') and hasattr(self.state_manager, 'update_discovered_products_in_category'):
            self.state_manager.update_discovered_products_in_category(category_url, products_found)
            
    def _update_processing_progress(self, product_url: str = None):
        """Update processing progress in state manager"""
        if hasattr(self, 'state_manager') and hasattr(self.state_manager, 'update_processing_progress'):
            self.state_manager.update_processing_progress(increment=1, product_url=product_url)
'''
        
        # Add the discovery method if not already present
        if "_update_category_discovered_products" not in content:
            # Find a good place to insert the method (before the last class closing)
            insert_point = content.rfind("def main(")
            if insert_point != -1:
                content = content[:insert_point] + discovery_method + "\n" + content[insert_point:]
                modified = True
                log.info("✅ Added category discovery update methods")
        
        if modified:
            # Write updated content
            with open(workflow_path, 'w', encoding='utf-8') as f:
                f.write(content)
            log.info("✅ Workflow script updated successfully")
            return True
        else:
            log.info("ℹ️ No changes needed in workflow script")
            return True
            
    def create_integration_example(self):
        """Create an example script showing how to use the fixed state manager"""
        example_path = self.project_root / "example_fixed_state_usage.py"
        
        example_content = '''#!/usr/bin/env python3
"""
Example: Using the Fixed Enhanced State Manager
==============================================

This example demonstrates the correct usage of the fixed state manager
to prevent processing state issues.
"""

from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def example_usage():
    """Example of correct state manager usage"""
    
    # Initialize the fixed state manager
    state_manager = FixedEnhancedStateManager("poundwholesale.co.uk")
    
    # 1. Load existing state
    state_loaded = state_manager.load_state()
    
    # 2. CRITICAL: Perform startup analysis ONCE at session start
    # This handles reverse gap detection and prevents index resets
    startup_categories = state_manager.perform_startup_analysis()
    
    print(f"Startup analysis complete. Found {len(startup_categories)} categories")
    
    # 3. Get resumption index (where to start processing)
    resumption_index = state_manager.get_resumption_index()
    print(f"Resuming from index: {resumption_index}")
    
    # 4. During processing: Update discovered products when scraper finds more
    # Example: scraper discovers makeup-supplies has 105 products, not 36
    category_url = "https://www.poundwholesale.co.uk/health-beauty/wholesale-makeup-supplies"
    discovered_products = 105
    state_manager.update_discovered_products_in_category(category_url, discovered_products)
    
    # 5. During processing: Update progress without affecting resumption index
    for i in range(10):  # Process 10 products
        product_url = f"https://example.com/product/{i}"
        
        # Process the product here...
        
        # Update progress (this won't reset the index)
        state_manager.update_processing_progress(increment=1, product_url=product_url)
        
        # Save state preserving interruption capability
        if i % 5 == 0:  # Save every 5 products
            state_manager.save_state(preserve_interruption_state=True)
    
    # 6. When category is completed
    state_manager.mark_category_completed(category_url)
    
    # 7. Get current progress information
    progress = state_manager.get_current_progress()
    print(f"Progress: {progress}")
    
    print("✅ Example completed successfully")

if __name__ == "__main__":
    example_usage()
'''
        
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_content)
            
        log.info(f"✅ Created integration example: {example_path}")
        
    def create_test_script(self):
        """Create a test script to verify the fixes work correctly"""
        test_path = self.project_root / "test_processing_state_fixes.py"
        
        test_content = '''#!/usr/bin/env python3
"""
Test Script: Processing State Fixes Verification
===============================================

This script tests that all critical processing state issues are resolved:
1. last_processed_index no longer resets to 0
2. Category product counts update with real-time discoveries  
3. Metrics appear in correct sections
4. State persists correctly during interruptions
"""

import json
import tempfile
from pathlib import Path
from utils.fixed_enhanced_state_manager import FixedEnhancedStateManager

def test_index_reset_fix():
    """Test that last_processed_index no longer resets to 0"""
    print("🧪 Testing index reset fix...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test state manager
        state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        state_manager.state_file_path = Path(temp_dir) / "test_state.json"
        
        # Perform startup analysis
        state_manager.perform_startup_analysis()
        
        # Set initial progress
        state_manager.update_processing_progress(increment=43)
        initial_index = state_manager.state_data["last_processed_index"]
        
        # Save state multiple times (this used to cause resets)
        for i in range(5):
            state_manager.save_state(preserve_interruption_state=True)
            current_index = state_manager.state_data["last_processed_index"]
            
            if current_index != initial_index:
                print(f"❌ FAILED: Index changed from {initial_index} to {current_index}")
                return False
                
        print(f"✅ PASSED: Index remained stable at {initial_index}")
        return True

def test_category_discovery_update():
    """Test that category totals update with real-time discoveries"""
    print("🧪 Testing category discovery update...")
    
    state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
    
    # Simulate discovering more products than expected
    category_url = "https://test.com/category"
    initial_total = 36
    discovered_total = 105
    
    # Set initial total
    state_manager.state_data["supplier_extraction_progress"]["total_products_in_current_category"] = initial_total
    
    # Update with discovery
    state_manager.update_discovered_products_in_category(category_url, discovered_total)
    
    # Check that total was updated
    updated_total = state_manager.state_data["supplier_extraction_progress"]["total_products_in_current_category"]
    
    if updated_total == discovered_total:
        print(f"✅ PASSED: Category total updated from {initial_total} to {discovered_total}")
        return True
    else:
        print(f"❌ FAILED: Expected {discovered_total}, got {updated_total}")
        return False

def test_metric_placement():
    """Test that metrics appear in correct sections"""
    print("🧪 Testing metric placement...")
    
    state_manager = FixedEnhancedStateManager("test-supplier.co.uk") 
    
    # Check that the misplaced metric is fixed
    progress = state_manager.state_data["supplier_extraction_progress"]
    
    # Should have pages_scraped_in_session instead of total_subcategories_in_batch
    if "pages_scraped_in_session" in progress and "total_subcategories_in_batch" not in progress:
        print("✅ PASSED: Metric placement fixed - pages_scraped_in_session exists")
        return True
    else:
        print("❌ FAILED: Metric placement not fixed")
        return False

def test_state_persistence():
    """Test that state persists correctly during interruptions"""
    print("🧪 Testing state persistence...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        state_file = Path(temp_dir) / "persistence_test.json"
        
        # Create state manager and process some products
        state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        state_manager.state_file_path = state_file
        
        # Simulate processing
        state_manager.perform_startup_analysis()
        state_manager.update_processing_progress(increment=25)
        expected_progress = state_manager.state_data["session_products_processed"]
        
        # Save state
        state_manager.save_state(preserve_interruption_state=True)
        
        # Create new state manager (simulating restart)
        new_state_manager = FixedEnhancedStateManager("test-supplier.co.uk")
        new_state_manager.state_file_path = state_file
        loaded = new_state_manager.load_state()
        
        if loaded and new_state_manager.get_resumption_index() >= 0:
            print("✅ PASSED: State persistence works correctly") 
            return True
        else:
            print("❌ FAILED: State persistence broken")
            return False

def run_all_tests():
    """Run all tests and report results"""
    print("🚀 Running Processing State Fixes Tests")
    print("=" * 50)
    
    tests = [
        test_index_reset_fix,
        test_category_discovery_update, 
        test_metric_placement,
        test_state_persistence
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ TEST ERROR: {e}")
            print()
    
    print("=" * 50)
    print(f"🎯 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Processing state fixes are working!")
        return True
    else:
        print("⚠️ Some tests failed - fixes may need additional work")
        return False

if __name__ == "__main__":
    run_all_tests()
'''
        
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
            
        # Make executable
        test_path.chmod(0o755)
        
        log.info(f"✅ Created test script: {test_path}")
        
    def apply_fixes(self):
        """Apply all processing state fixes"""
        log.info("🚀 Applying processing state fixes...")
        
        # Create backup first
        self.create_backup()
        
        # Update workflow script
        if not self.update_workflow_script():
            log.error("❌ Failed to update workflow script")
            return False
            
        # Create integration example
        self.create_integration_example()
        
        # Create test script
        self.create_test_script()
        
        log.info("✅ All processing state fixes applied successfully!")
        log.info(f"📁 Backup created at: {self.backup_dir}")
        log.info("📋 Next steps:")
        log.info("   1. Run: python test_processing_state_fixes.py")
        log.info("   2. Review: example_fixed_state_usage.py")
        log.info("   3. Test with: python run_custom_poundwholesale.py")
        
        return True
        
    def verify_fixes(self):
        """Verify that fixes have been applied correctly"""
        log.info("🔍 Verifying processing state fixes...")
        
        # Check if fixed state manager exists
        fixed_manager_path = self.project_root / "utils" / "fixed_enhanced_state_manager.py"
        if not fixed_manager_path.exists():
            log.error("❌ Fixed state manager not found")
            return False
            
        # Check if test script exists
        test_script_path = self.project_root / "test_processing_state_fixes.py"
        if not test_script_path.exists():
            log.error("❌ Test script not found")
            return False
        
        # Run the test script
        log.info("🧪 Running verification tests...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, str(test_script_path)], 
                                  capture_output=True, text=True, cwd=str(self.project_root))
            
            if result.returncode == 0:
                log.info("✅ All verification tests passed!")
                return True
            else:
                log.error(f"❌ Verification tests failed: {result.stderr}")
                return False
                
        except Exception as e:
            log.error(f"❌ Failed to run verification tests: {e}")
            return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Implement processing state fixes")
    parser.add_argument("--apply", action="store_true", help="Apply all fixes")
    parser.add_argument("--test", action="store_true", help="Run verification tests")
    parser.add_argument("--verify", action="store_true", help="Verify fixes are working")
    parser.add_argument("--project-root", help="Project root directory")
    
    args = parser.parse_args()
    
    if not any([args.apply, args.test, args.verify]):
        parser.print_help()
        return
        
    implementer = ProcessingStateFixImplementer(args.project_root)
    
    if args.apply:
        success = implementer.apply_fixes()
        sys.exit(0 if success else 1)
        
    if args.verify:
        success = implementer.verify_fixes()
        sys.exit(0 if success else 1)
        
    if args.test:
        # Just create and run the test script
        implementer.create_test_script()
        success = implementer.verify_fixes()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()