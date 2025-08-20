#!/usr/bin/env python3
"""
State Reconciliation Script - Atomic State Repair
"""

import json
import os
import shutil
from datetime import datetime
import sys
import argparse

class StateReconciler:
    def __init__(self, state_file="OUTPUTS/processing_state.json"):
        self.state_file = state_file
        self.backup_dir = None
    
    def create_backup(self):
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"artifacts/backups/state_reconcile_{timestamp}"
        os.makedirs(self.backup_dir, exist_ok=True)
        
        if os.path.exists(self.state_file):
            backup_file = os.path.join(self.backup_dir, "processing_state_backup.json")
            shutil.copy2(self.state_file, backup_file)
            print(f"✅ Backup created: {backup_file}")
            return backup_file
        return None
    
    def load_state(self):
        """Load current state"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading state: {e}")
            return None
    
    def detect_inconsistencies(self, state_data):
        """Detect state inconsistencies"""
        issues = []
        
        # Check products_extracted_total vs successful_products
        products_extracted = state_data.get("supplier_extraction_progress", {}).get("products_extracted_total", 0)
        successful_products = state_data.get("successful_products", 0)
        
        if products_extracted != successful_products:
            issues.append({
                "type": "product_count_mismatch",
                "description": f"products_extracted_total ({products_extracted}) != successful_products ({successful_products})",
                "severity": "high"
            })
        
        return issues
    
    def reconcile(self, dry_run=False):
        """Main reconciliation process"""
        print(f"🔧 State Reconciliation {'(DRY RUN)' if dry_run else '(LIVE)'}")
        
        # Create backup
        if not dry_run:
            self.create_backup()
        
        # Load state
        state_data = self.load_state()
        if not state_data:
            return False
        
        # Detect issues
        issues = self.detect_inconsistencies(state_data)
        print(f"🔍 Issues detected: {len(issues)}")
        
        if not issues:
            print("✅ No inconsistencies found")
            return True
        
        # Fix product count mismatch
        successful_products = state_data.get("successful_products", 0)
        if not dry_run:
            state_data.setdefault("supplier_extraction_progress", {})["products_extracted_total"] = successful_products
            
            # Save atomically
            temp_file = f"{self.state_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            os.replace(temp_file, self.state_file)
            
            print(f"✅ Fixed products_extracted_total: {successful_products}")
        
        return True

def main():
    parser = argparse.ArgumentParser(description="State Reconciliation Tool")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()
    
    reconciler = StateReconciler()
    success = reconciler.reconcile(dry_run=args.dry_run)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())