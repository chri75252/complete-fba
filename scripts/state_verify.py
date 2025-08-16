#!/usr/bin/env python3
"""
State Verification Tool - Validate State Consistency
Checks invariants and reports violations
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class StateVerifier:
    """Verifies state consistency and invariants"""
    
    def __init__(self):
        self.state_files = [
            "OUTPUTS/processing_state.json",
            "OUTPUTS/CACHE/processing_states/poundwholesale_co_uk_processing_state.json"
        ]
        
    def find_state_files(self) -> List[str]:
        """Find all state files in the system"""
        found_files = []
        for file_path in self.state_files:
            if os.path.exists(file_path):
                found_files.append(file_path)
        return found_files
    
    def load_state(self, file_path: str) -> Dict:
        """Load state file safely"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e), "file": file_path}
    
    def check_single_source_of_truth(self) -> Tuple[bool, str]:
        """Verify only one state file exists"""
        state_files = self.find_state_files()
        
        if len(state_files) == 0:
            return False, "❌ No state files found"
        elif len(state_files) == 1:
            return True, f"✅ Single state file: {state_files[0]}"
        else:
            return False, f"❌ Multiple state files found: {state_files}"
    
    def check_product_count_consistency(self, state: Dict) -> Tuple[bool, str]:
        """Check product count consistency"""
        processed_products = state.get("processed_products", {})
        successful_products = state.get("successful_products", 0)
        total_products = state.get("total_products", 0)
        
        processed_count = len(processed_products)
        
        issues = []
        
        if processed_count != successful_products:
            issues.append(f"processed_products count ({processed_count}) != successful_products ({successful_products})")
        
        if successful_products > total_products:
            issues.append(f"successful_products ({successful_products}) > total_products ({total_products})")
        
        if issues:
            return False, f"❌ Product count issues: {'; '.join(issues)}"
        else:
            return True, f"✅ Product counts consistent: {processed_count} processed, {successful_products} successful, {total_products} total"
    
    def check_index_consistency(self, state: Dict) -> Tuple[bool, str]:
        """Check index consistency"""
        last_processed = state.get("last_processed_index", 0)
        resumption = state.get("resumption_index", 0)
        progress = state.get("progress_index", 0)
        total_products = state.get("total_products", 0)
        
        issues = []
        
        # Check non-negative
        for name, value in [("last_processed_index", last_processed), 
                           ("resumption_index", resumption), 
                           ("progress_index", progress)]:
            if value < 0:
                issues.append(f"{name} is negative: {value}")
        
        # Check bounds
        if total_products > 0:
            for name, value in [("last_processed_index", last_processed), 
                               ("resumption_index", resumption), 
                               ("progress_index", progress)]:
                if value > total_products:
                    issues.append(f"{name} ({value}) > total_products ({total_products})")
        
        if issues:
            return False, f"❌ Index issues: {'; '.join(issues)}"
        else:
            return True, f"✅ Indices consistent: last={last_processed}, resume={resumption}, progress={progress}"
    
    def check_timestamp_format(self, state: Dict) -> Tuple[bool, str]:
        """Check timestamp format consistency"""
        timestamp = state.get("last_updated", "")
        
        if not timestamp:
            return False, "❌ No last_updated timestamp found"
        
        try:
            # Try to parse as ISO format
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True, f"✅ Timestamp format valid: {timestamp}"
        except ValueError as e:
            return False, f"❌ Invalid timestamp format: {timestamp} ({e})"
    
    def check_category_url_consistency(self, state: Dict) -> Tuple[bool, str]:
        """Check category URL consistency across state sections"""
        supplier_progress = state.get("supplier_extraction_progress", {})
        system_progression = state.get("system_progression", {})
        
        supplier_url = supplier_progress.get("current_category_url", "")
        system_url = system_progression.get("current_category_url", "")
        
        if supplier_url and system_url and supplier_url != system_url:
            return False, f"❌ Category URL mismatch: supplier='{supplier_url}' vs system='{system_url}'"
        elif supplier_url or system_url:
            return True, f"✅ Category URL consistent: '{supplier_url or system_url}'"
        else:
            return True, "✅ No category URLs set (consistent)"
    
    def check_category_index_consistency(self, state: Dict) -> Tuple[bool, str]:
        """Check category index consistency"""
        supplier_progress = state.get("supplier_extraction_progress", {})
        system_progression = state.get("system_progression", {})
        
        supplier_index = supplier_progress.get("current_category_index", 0)
        system_index = system_progression.get("current_category_index", 0)
        
        if supplier_index != system_index:
            return False, f"❌ Category index mismatch: supplier={supplier_index} vs system={system_index}"
        else:
            return True, f"✅ Category index consistent: {supplier_index}"
    
    def check_processing_status(self, state: Dict) -> Tuple[bool, str]:
        """Check processing status validity"""
        status = state.get("processing_status", "")
        valid_statuses = ["initialized", "active", "in_progress", "completed", "paused", "error", "reconciled"]
        
        if status not in valid_statuses:
            return False, f"❌ Invalid processing status: '{status}' (valid: {valid_statuses})"
        else:
            return True, f"✅ Processing status valid: '{status}'"
    
    def run_all_checks(self, state_file: str = None) -> Dict:
        """Run all verification checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "overall_status": "UNKNOWN",
            "issues_found": 0
        }
        
        # Check single source of truth
        sot_pass, sot_msg = self.check_single_source_of_truth()
        results["checks"]["single_source_of_truth"] = {"pass": sot_pass, "message": sot_msg}
        
        if not sot_pass:
            results["overall_status"] = "FAILED"
            results["issues_found"] += 1
            return results
        
        # Load the single state file
        state_files = self.find_state_files()
        if not state_files:
            results["overall_status"] = "FAILED"
            results["issues_found"] += 1
            return results
        
        state_file = state_files[0]
        state = self.load_state(state_file)
        
        if "error" in state:
            results["checks"]["state_loading"] = {"pass": False, "message": f"❌ Failed to load state: {state['error']}"}
            results["overall_status"] = "FAILED"
            results["issues_found"] += 1
            return results
        
        # Run all checks
        checks = [
            ("product_count_consistency", self.check_product_count_consistency),
            ("index_consistency", self.check_index_consistency),
            ("timestamp_format", self.check_timestamp_format),
            ("category_url_consistency", self.check_category_url_consistency),
            ("category_index_consistency", self.check_category_index_consistency),
            ("processing_status", self.check_processing_status)
        ]
        
        issues_found = 0
        for check_name, check_func in checks:
            try:
                passed, message = check_func(state)
                results["checks"][check_name] = {"pass": passed, "message": message}
                if not passed:
                    issues_found += 1
            except Exception as e:
                results["checks"][check_name] = {"pass": False, "message": f"❌ Check failed with error: {e}"}
                issues_found += 1
        
        results["issues_found"] = issues_found
        results["overall_status"] = "PASSED" if issues_found == 0 else "FAILED"
        
        return results
    
    def print_results(self, results: Dict):
        """Print verification results in a readable format"""
        print("🔍 State Verification Results")
        print("=" * 50)
        print(f"⏰ Timestamp: {results['timestamp']}")
        print(f"📊 Overall Status: {results['overall_status']}")
        print(f"🚨 Issues Found: {results['issues_found']}")
        print()
        
        for check_name, check_result in results["checks"].items():
            status_icon = "✅" if check_result["pass"] else "❌"
            print(f"{status_icon} {check_name.replace('_', ' ').title()}")
            print(f"   {check_result['message']}")
            print()
        
        if results["overall_status"] == "PASSED":
            print("🎉 All state verification checks passed!")
        else:
            print("💥 State verification failed. Run reconciliation to fix issues.")

def main():
    verifier = StateVerifier()
    results = verifier.run_all_checks()
    verifier.print_results(results)
    
    # Return appropriate exit code
    return 0 if results["overall_status"] == "PASSED" else 1

if __name__ == "__main__":
    exit(main())