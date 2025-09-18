"""
Sentinel Integration Patch for Amazon FBA Agent System

This script patches the PassiveExtractionWorkflow to add comprehensive sentinel monitoring.
Run this to integrate sentinel monitoring into the main workflow.

INTEGRATION POINTS:
1. Initialize sentinel monitor in __init__
2. Monitor linking map saves for shrinkage detection  
3. Track session vs global totals divergence
4. Monitor path variants and save retry patterns
5. Add sentinel finalization to cleanup

Usage: python sentinel_integration_patch.py
"""

import os
import shutil
from pathlib import Path
import re

def create_backup(file_path: str) -> str:
    """Create backup of original file before patching"""
    backup_path = f"{file_path}.sentinel_backup"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return backup_path

def patch_workflow_file():
    """Apply sentinel monitoring patches to PassiveExtractionWorkflow"""
    
    workflow_path = "tools/passive_extraction_workflow_latest.py"
    
    if not os.path.exists(workflow_path):
        print(f"❌ ERROR: {workflow_path} not found")
        return False
    
    # Create backup
    backup_path = create_backup(workflow_path)
    
    # Read the file
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patch 1: Add sentinel import
    import_patch = """
# Import WSL-compatible save function for linking maps
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wsl_compatible_save import wsl_compatible_save
from dataclasses import dataclass, field
from pathlib import Path # ADDED IMPORT
import aiohttp  # Added for async HTTP requests

# 🚨 SENTINEL MONITORING: Import sentinel monitoring system
from utils.sentinel_monitor import get_sentinel_monitor, SentinelMonitor"""
    
    # Find the import section and add sentinel import
    import_pattern = r"(from wsl_compatible_save import wsl_compatible_save.*?\nimport aiohttp.*?\n)"
    if re.search(import_pattern, content, re.DOTALL):
        content = re.sub(import_pattern, import_patch, content, flags=re.DOTALL)
    else:
        # Fallback: add after the existing imports
        content = content.replace(
            "import aiohttp  # Added for async HTTP requests",
            "import aiohttp  # Added for async HTTP requests\n\n# 🚨 SENTINEL MONITORING: Import sentinel monitoring system\nfrom utils.sentinel_monitor import get_sentinel_monitor, SentinelMonitor"
        )
    
    # Patch 2: Initialize sentinel monitor in __init__
    init_patch = """        # 🚨 SENTINEL MONITORING: Initialize proactive monitoring system
        self.sentinel_monitor = get_sentinel_monitor(self.supplier_name)
        self.log.info("🚨 SENTINEL MONITORING: Proactive monitoring system initialized")
        
        # self.performance_tracker = PerformanceTracker()  # Removed - not defined"""
    
    content = content.replace(
        "        # self.performance_tracker = PerformanceTracker()  # Removed - not defined",
        init_patch
    )
    
    # Patch 3: Add sentinel monitoring to _save_linking_map method
    save_patch = """    def _save_linking_map(self, supplier_name: str):
        \"\"\"Save linking map to supplier-specific JSON file using WSL-compatible save function\"\"\"
        self.log.info(f"🔍 DEBUG: _save_linking_map called with {len(self.linking_map)} entries for supplier {supplier_name}")
        
        # 🚨 SENTINEL MONITORING: Track linking map size before save
        previous_size = 0
        linking_map_path = get_linking_map_path(supplier_name)
        if linking_map_path.exists():
            try:
                with open(linking_map_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    previous_size = len(existing_data) if isinstance(existing_data, list) else 0
            except Exception as e:
                self.log.warning(f"⚠️ Could not read existing linking map for size comparison: {e}")
        
        sample_entry = self.linking_map[0] if self.linking_map else {}
        truncated_sample = {k: str(v)[:50] + '...' if len(str(v)) > 50 else v for k, v in sample_entry.items()}
        self.log.info(f"🔍 DEBUG: linking_map type: {type(self.linking_map)}, entries: {len(self.linking_map)}, sample: {truncated_sample}")
        
        if not self.linking_map:
            self.log.warning("⚠️ CRITICAL: Empty linking map - nothing to save. This suggests linking map entries are not being created!")
            # 🚨 SENTINEL MONITORING: Alert on empty linking map
            self.sentinel_monitor.check_linking_map_shrinkage(0, previous_size)
            return
            
        # Use consistent path naming with get_linking_map_path
        try:
            self.log.info(f"🔍 DEBUG: Target file path: {linking_map_path}")
            
        except Exception as path_error:
            self.log.error(f"❌ CRITICAL: Failed to create linking map path: {path_error}")
            return
        
        # 🔧 WSL-COMPATIBLE SAVE: Use multi-strategy save function
        self.log.info(f"🔧 WSL-COMPATIBLE SAVE: Attempting to save {len(self.linking_map)} entries using multiple strategies...")
        
        try:
            # 🚨 SENTINEL MONITORING: Track save attempt
            current_size = len(self.linking_map)
            save_success = False
            retry_count = 1
            
            # Use WSL-compatible save function with multiple fallback strategies
            success = wsl_compatible_save(self.linking_map, linking_map_path, log=self.log)
            
            if success:
                save_success = True
                self.log.info(f"✅ Successfully saved linking map with {len(self.linking_map)} entries to {linking_map_path}")
                
                # Verify the file was actually created and has content
                if linking_map_path.exists():
                    file_size = linking_map_path.stat().st_size
                    self.log.info(f"✅ VERIFICATION: File exists at {linking_map_path} with size {file_size} bytes")
                    
                    # 🚀 HASH OPTIMIZATION: Rebuild hash indexes after saving linking map
                    self.hash_optimizer.build_indexes(self.linking_map)
                    self.log.info(f"🚀 HASH INDEXES REBUILT: Updated indexes for {len(self.linking_map)} entries")
                    
                    # 🚨 SENTINEL MONITORING: Check for linking map shrinkage
                    self.sentinel_monitor.check_linking_map_shrinkage(current_size, previous_size)
                    self.sentinel_monitor.track_save_retry("wsl_compatible_save", True, retry_count)
                else:
                    self.log.error(f"❌ CRITICAL: File was not created at {linking_map_path}")
                    self.sentinel_monitor.track_save_retry("wsl_compatible_save", False, retry_count)
            else:
                self.log.error(f"❌ CRITICAL: WSL-compatible save failed for {linking_map_path}")
                self.sentinel_monitor.track_save_retry("wsl_compatible_save", False, retry_count)
                
        except Exception as e:
            self.log.error(f"❌ CRITICAL: Error in WSL-compatible save: {e}", exc_info=True)
            self.sentinel_monitor.track_save_retry("wsl_compatible_save", False, retry_count)"""
    
    # Find and replace the _save_linking_map method
    save_pattern = r"def _save_linking_map\(self, supplier_name: str\):.*?def _classify_url\(self, url: str\) -> str:"
    if re.search(save_pattern, content, re.DOTALL):
        # Extract the _classify_url method start to preserve it
        classify_match = re.search(r"def _classify_url\(self, url: str\) -> str:", content)
        if classify_match:
            save_replacement = save_patch + "\n\n    " + classify_match.group(0)
            content = re.sub(save_pattern, save_replacement, content, flags=re.DOTALL)
    
    # Patch 4: Add sentinel monitoring to progress tracking methods
    progress_patch = """    def get_current_progress_from_files(self) -> Dict[str, int]:
        \"\"\"Get comprehensive progress status by reading directly from files (zero-risk method)\"\"\"
        try:
            progress = {
                'supplier_products': self.get_supplier_product_count_from_file(),
                'processed_products': self.get_processed_products_count_from_state(),
                'linking_entries': self.get_linking_map_count_from_file(),
                'auth_fallback_count': self.get_authentication_fallback_count_from_state()
            }
            
            # 🚨 SENTINEL MONITORING: Check for session vs global totals divergence  
            session_products = len(getattr(self, 'products_in_memory', []))
            session_linking = len(getattr(self, 'linking_map', []))
            
            self.sentinel_monitor.check_totals_divergence(
                session_products, progress['supplier_products'], 'supplier_products'
            )
            self.sentinel_monitor.check_totals_divergence(
                session_linking, progress['linking_entries'], 'linking_entries'  
            )
            
            return progress
            
        except Exception as e:
            self.log.error(f"❌ Error getting progress from files: {e}")
            return {'supplier_products': 0, 'processed_products': 0, 'linking_entries': 0, 'auth_fallback_count': 0}"""
    
    # Find and replace the progress method
    progress_pattern = r"def get_current_progress_from_files\(self\) -> Dict\[str, int\]:.*?except Exception as e:.*?return.*?\}"
    if re.search(progress_pattern, content, re.DOTALL):
        content = re.sub(progress_pattern, progress_patch.strip(), content, flags=re.DOTALL)
    
    # Patch 5: Add sentinel monitoring to file access operations
    file_access_patch = """        # 🚨 SENTINEL MONITORING: Check for path variants
        self.sentinel_monitor.check_path_variants(str(linking_map_path), "linking_map_access")"""
    
    # Add path variant monitoring near file access operations
    content = content.replace(
        "linking_map_path = get_linking_map_path(supplier_name)",
        "linking_map_path = get_linking_map_path(supplier_name)\n        " + file_access_patch.strip()
    )
    
    # Patch 6: Add finalization call to the run method
    finalize_patch = """            # 🚨 SENTINEL MONITORING: Finalize monitoring and generate summary
            self.sentinel_monitor.finalize_monitoring()
            
            self.log.info(f"\\n\\n🎉 **WORKFLOW COMPLETED SUCCESSFULLY** 🎉")"""
    
    content = content.replace(
        '            self.log.info(f"\\n\\n🎉 **WORKFLOW COMPLETED SUCCESSFULLY** 🎉")',
        finalize_patch
    )
    
    # Write the patched content
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully patched {workflow_path}")
    print(f"📁 Backup created at: {backup_path}")
    return True

def verify_patch():
    """Verify that the patches were applied correctly"""
    workflow_path = "tools/passive_extraction_workflow_latest.py"
    
    with open(workflow_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("Sentinel import", "from utils.sentinel_monitor import get_sentinel_monitor"),
        ("Sentinel initialization", "self.sentinel_monitor = get_sentinel_monitor"),
        ("Linking map monitoring", "self.sentinel_monitor.check_linking_map_shrinkage"),
        ("Totals divergence monitoring", "self.sentinel_monitor.check_totals_divergence"),
        ("Path variant monitoring", "self.sentinel_monitor.check_path_variants"),
        ("Save retry monitoring", "self.sentinel_monitor.track_save_retry"),
        ("Finalization", "self.sentinel_monitor.finalize_monitoring")
    ]
    
    all_good = True
    for check_name, check_text in checks:
        if check_text in content:
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🚨 SENTINEL INTEGRATION PATCH")
    print("=" * 50)
    
    if patch_workflow_file():
        print("\n🔍 VERIFICATION:")
        if verify_patch():
            print("\n✅ ALL SENTINEL PATCHES APPLIED SUCCESSFULLY!")
            print("\n📋 NEXT STEPS:")
            print("1. Run test scenarios to verify sentinel effectiveness")
            print("2. Check OUTPUTS/DIAGNOSTICS/sentinels.log for monitoring alerts")
            print("3. Monitor system for proactive failure detection")
        else:
            print("\n⚠️ SOME PATCHES MAY NOT HAVE APPLIED CORRECTLY")
            print("Please review the output above and check manually if needed")
    else:
        print("\n❌ PATCH FAILED - Please check the error messages above")