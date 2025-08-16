#!/usr/bin/env python3
"""
State Reconciliation Script - Atomic State Repair
Detects and repairs state inconsistencies with atomic operations
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import sys
import argparse

class StateReconciler:
    def __init__(self, state_file="OUTPUTS/processing_state.json"):
        self.state_file = state_file
        self.backup_dir = None
        self.reconciliation_report = {
            "timestamp": datetime.now().isoformat(),
            "operation": "reconcile_state",
            "issues_found": [],
            "repairs_applied": [],
            "final_state": {}
        }
    
    def create_backup(self):
        """Create timestamped backup before any modifications"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"artifacts/backups/state_reconcile_{timestamp}"
        os.makedirs(self.backup_dir, exi
            if self.cache_state_path.exists():
                shutil.copy2(self.cache_state_path, self.backup_dir / "cache_processing_state.json")
                print(f"✅ Backed up cache state to {self.backup_dir}")
                
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def load_states(self) -> Tuple[Optional[Dict], Optional[Dict]]:
        """Load both state files safely"""
        main_state = None
        cache_state = None
        
        if self.main_state_path.exists():
            try:
                with open(self.main_state_path, 'r', encoding='utf-8') as f:
                    main_state = json.load(f)
                print(f"✅ Loaded main state: {len(main_state)} keys")
            except Exception as e:
                print(f"❌ Failed to load main state: {e}")
        
        if self.cache_state_path.exists():
            try:
                with open(self.cache_state_path, 'r', encoding='utf-8') as f:
                    cache_state = json.load(f)
                print(f"✅ Loaded cache state: {len(cache_state)} keys")
            except Exception as e:
                print(f"❌ Failed to load cache state: {e}")
        
        return main_state, cache_state
    
    def choose_source_of_truth(self, main_state: Dict, cache_state: Dict, source: str = "auto") -> Dict:
        """Choose which state to use as source of truth"""
        
        if source == "main":
            print("🎯 Using main state as source of truth")
            return main_state
        elif source == "cache":
            print("🎯 Using cache state as source of truth")
            return cache_state
        
        # Auto-selection logic
        main_timestamp = main_state.get("last_updated", "")
        cache_timestamp = cache_state.get("last_updated", "")
        
        main_products = main_state.get("successful_products", 0)
        cache_products = cache_state.get("successful_products", 0)
        
        # Prefer cache state if it has more recent timestamp and more products
        if cache_timestamp > main_timestamp and cache_products > main_products:
            print(f"🎯 Auto-selected cache state (newer: {cache_timestamp}, more products: {cache_products})")
            return cache_state
        else:
            print(f"🎯 Auto-selected main state (timestamp: {main_timestamp}, products: {main_products})")
            return main_state
    
    def merge_states(self, main_state: Dict, cache_state: Dict) -> Dict:
        """Intelligently merge two states, resolving conflicts"""
        print("🔄 Merging states with conflict resolution...")
        
        # Start with the state that has more processed products
        main_products = main_state.get("successful_products", 0)
        cache_products = cache_state.get("successful_products", 0)
        
        if cache_products > main_products:
            base_state = cache_state.copy()
            overlay_state = main_state
            print(f"📊 Using cache as base ({cache_products} products)")
        else:
            base_state = main_state.copy()
            overlay_state = cache_state
            print(f"📊 Using main as base ({main_products} products)")
        
        # Merge processed_products (union of both)
        if "processed_products" in overlay_state:
            base_products = base_state.get("processed_products", {})
            overlay_products = overlay_state.get("processed_products", {})
            
            merged_products = base_products.copy()
            merged_products.update(overlay_products)
            base_state["processed_products"] = merged_products
            
            print(f"🔗 Merged processed products: {len(merged_products)} total")
        
        # Use the most recent timestamp
        base_timestamp = base_state.get("last_updated", "")
        overlay_timestamp = overlay_state.get("last_updated", "")
        
        if overlay_timestamp > base_timestamp:
            base_state["last_updated"] = overlay_timestamp
        
        # Recalculate totals based on merged data
        if "processed_products" in base_state:
            base_state["successful_products"] = len(base_state["processed_products"])
            base_state["total_products"] = max(
                base_state.get("total_products", 0),
                len(base_state["processed_products"])
            )
        
        return base_state
    
    def create_fresh_state(self, preserve_products: bool = True) -> Dict:
        """Create fresh state structure, optionally preserving product data"""
        print("🆕 Creating fresh state structure...")
        
        # Load existing states to preserve product data if requested
        main_state, cache_state = self.load_states()
        processed_products = {}
        
        if preserve_products:
            if cache_state and "processed_products" in cache_state:
                processed_products.update(cache_state["processed_products"])
            if main_state and "processed_products" in main_state:
                processed_products.update(main_state["processed_products"])
            print(f"💾 Preserved {len(processed_products)} processed products")
        
        # Create clean state structure
        fresh_state = {
            "schema_version": "1.2_RECONCILED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "supplier_name": "poundwholesale.co.uk",
            
            # Reset indices for clean start
            "last_processed_index": 0,
            "resumption_index": 0,
            "progress_index": 0,
            "session_products_processed": 0,
            
            "total_products": len(processed_products) if preserve_products else 0,
            "processing_status": "reconciled",
            "successful_products": len(processed_products) if preserve_products else 0,
            "profitable_products": 0,
            "total_profit_found": 0.0,
            
            "processed_products": processed_products,
            
            "supplier_extraction_progress": {
                "current_category_index": 0,
                "total_categories": 0,
                "current_subcategory_index": 0,
                "pages_scraped_in_session": 0,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "current_category_url": "",
                "current_batch_number": 0,
                "total_batches": 0,
                "extraction_phase": "not_started",
                "last_completed_category": "",
                "categories_completed": [],
                "products_extracted_total": len(processed_products) if preserve_products else 0
            },
            
            "gap_processing": {
                "phase": "not_started",
                "gap_products_total": 0,
                "gap_products_processed": 0,
                "gap_start_time": None,
                "gap_end_time": None,
                "reverse_gap_detected": False,
                "startup_analysis_completed": True
            },
            
            "system_progression": {
                "current_phase": "supplier",
                "current_category_index": 0,
                "current_category_url": "",
                "total_categories": 0,
                "current_product_index_in_category": 0,
                "total_products_in_current_category": 0,
                "supplier_extraction_resumption_index": 0,
                "amazon_analysis_resumption_index": 0
            },
            
            "metadata": {
                "version": "3.8_RECONCILED",
                "reconciliation_timestamp": datetime.now(timezone.utc).isoformat(),
                "reconciliation_method": "fresh_start_with_preservation" if preserve_products else "fresh_start"
            }
        }
        
        return fresh_state
    
    def validate_state(self, state: Dict) -> Tuple[bool, list]:
        """Validate state consistency and return issues"""
        issues = []
        
        # Check required fields
        required_fields = [
            "last_processed_index", "total_products", "successful_products",
            "processed_products", "supplier_extraction_progress"
        ]
        
        for field in required_fields:
            if field not in state:
                issues.append(f"Missing required field: {field}")
        
        # Check product count consistency and auto-fix
        processed_count = len(state.get("processed_products", {}))
        successful_count = state.get("successful_products", 0)
        
        if processed_count != successful_count:
            # Auto-fix: use processed_products count as source of truth
            state["successful_products"] = processed_count
            print(f"🔧 Auto-fixed product count: {successful_count} -> {processed_count}")
            successful_count = processed_count
        
        # Check timestamp format
        timestamp = state.get("last_updated", "")
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            issues.append(f"Invalid timestamp format: {timestamp}")
        
        # Check indices are non-negative
        for index_field in ["last_processed_index", "resumption_index", "progress_index"]:
            if state.get(index_field, 0) < 0:
                issues.append(f"Negative index: {index_field}={state.get(index_field)}")
        
        return len(issues) == 0, issues
    
    def save_reconciled_state(self, state: Dict, dry_run: bool = False) -> bool:
        """Save reconciled state atomically"""
        if dry_run:
            print("🔍 DRY RUN: Would save reconciled state")
            print(f"   - Products: {state.get('successful_products', 0)}")
            print(f"   - Total: {state.get('total_products', 0)}")
            print(f"   - Status: {state.get('processing_status', 'unknown')}")
            return True
        
        try:
            # Remove old state files
            if self.main_state_path.exists():
                os.remove(self.main_state_path)
                print(f"🗑️ Removed old main state file")
            
            if self.cache_state_path.exists():
                os.remove(self.cache_state_path)
                print(f"🗑️ Removed old cache state file")
            
            # Save new unified state to main location
            self.main_state_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Use atomic write
            temp_path = self.main_state_path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(self.main_state_path)
            
            print(f"✅ Saved reconciled state to {self.main_state_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save reconciled state: {e}")
            return False
    
    def reconcile(self, method: str = "auto", dry_run: bool = False) -> bool:
        """Main reconciliation method"""
        print(f"🔧 Starting state reconciliation (method: {method}, dry_run: {dry_run})")
        
        # Create backup
        if not dry_run and not self.create_backup():
            return False
        
        # Load states
        main_state, cache_state = self.load_states()
        
        if not main_state and not cache_state:
            print("❌ No state files found to reconcile")
            return False
        
        # Choose reconciliation method
        if method == "cache" and cache_state:
            reconciled_state = cache_state
        elif method == "main" and main_state:
            reconciled_state = main_state
        elif method == "merge" and main_state and cache_state:
            reconciled_state = self.merge_states(main_state, cache_state)
        elif method == "fresh-start":
            reconciled_state = self.create_fresh_state(preserve_products=True)
        elif method == "fresh-clean":
            reconciled_state = self.create_fresh_state(preserve_products=False)
        else:
            # Auto method
            if main_state and cache_state:
                reconciled_state = self.choose_source_of_truth(main_state, cache_state)
            elif cache_state:
                reconciled_state = cache_state
            elif main_state:
                reconciled_state = main_state
            else:
                print("❌ No valid state found")
                return False
        
        # Validate reconciled state
        is_valid, issues = self.validate_state(reconciled_state)
        if not is_valid:
            print(f"❌ Reconciled state validation failed:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        
        print("✅ Reconciled state validation passed")
        
        # Save reconciled state
        return self.save_reconciled_state(reconciled_state, dry_run)

def main():
    parser = argparse.ArgumentParser(description="Reconcile conflicting state files")
    parser.add_argument("--method", choices=["auto", "main", "cache", "merge", "fresh-start", "fresh-clean"], 
                       default="auto", help="Reconciliation method")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    reconciler = StateReconciler()
    success = reconciler.reconcile(method=args.method, dry_run=args.dry_run)
    
    if success:
        print("🎉 State reconciliation completed successfully")
        return 0
    else:
        print("💥 State reconciliation failed")
        return 1

if __name__ == "__main__":
    exit(main())