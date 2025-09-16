#!/usr/bin/env python3
"""
Legacy Writer Detection Script - Python version
Comprehensive validation of Group 1 implementation
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class LegacyWriterDetector:
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root)
        self.errors_found = False
        
        # Define legacy patterns to detect
        self.legacy_patterns = [
            {
                "pattern": r"(?<!\.def )\bself\.\w*update_processing_index\s*\(",
                "description": "Legacy update_processing_index calls (not definitions)",
                "severity": "CRITICAL"
            },
            {
                "pattern": r"(?<!\.def )\bself\.\w*save_state\s*\(\)",
                "description": "Direct save_state calls (should use atomic commits)",
                "severity": "HIGH"
            },
            {
                "pattern": r"len\s*\(\s*completed_categories\s*\)\s*>\s*0",
                "description": "completed_categories in control flow",
                "severity": "CRITICAL"
            }
        ]
        
        # Active files to check (exclude backups and older versions)
        self.active_files = [
            "tools/passive_extraction_workflow_latest.py",
            "utils/fixed_enhanced_state_manager.py", 
            "tools/configurable_supplier_scraper.py"
        ]
    
    def check_file_for_patterns(self, file_path: Path) -> List[Dict]:
        """Check a single file for legacy patterns."""
        findings = []
        
        if not file_path.exists():
            findings.append({
                "type": "FILE_MISSING",
                "description": f"File not found: {file_path}",
                "severity": "WARNING"
            })
            return findings
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for pattern_info in self.legacy_patterns:
                pattern = pattern_info["pattern"]
                matches = list(re.finditer(pattern, content, re.MULTILINE))
                
                for match in matches:
                    # Find line number
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_num = content.count('\n', 0, line_start) + 1
                    line_content = lines[line_num - 1].strip()
                    
                    # Skip method definitions, comments, and documentation
                    if (line_content.startswith('def ') or 
                        line_content.strip().startswith('#') or
                        line_content.strip().startswith('"""') or
                        '# Fallback' in line_content or
                        'deprecated' in line_content.lower() or
                        '.append(' in line_content or
                        'recommendations' in line_content.lower()):
                        continue
                    
                    findings.append({
                        "type": "LEGACY_PATTERN",
                        "pattern": pattern_info["description"],
                        "severity": pattern_info["severity"],
                        "line": line_num,
                        "content": line_content,
                        "file": str(file_path)
                    })
                    
        except Exception as e:
            findings.append({
                "type": "READ_ERROR",
                "description": f"Error reading {file_path}: {e}",
                "severity": "ERROR"
            })
            
        return findings
    
    def check_atomic_commit_methods(self) -> List[Dict]:
        """Check that atomic commit methods are properly implemented."""
        findings = []
        state_manager_path = self.workspace_root / "utils/fixed_enhanced_state_manager.py"
        
        required_methods = [
            "commit_supplier_progress",
            "commit_amazon_progress", 
            "_validate_cross_run_monotonicity",
            "log_resume_proof_after_commit"
        ]
        
        if state_manager_path.exists():
            try:
                with open(state_manager_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for method in required_methods:
                    if f"def {method}" not in content:
                        findings.append({
                            "type": "MISSING_METHOD",
                            "description": f"Required method missing: {method}",
                            "severity": "CRITICAL",
                            "file": str(state_manager_path)
                        })
                        
            except Exception as e:
                findings.append({
                    "type": "READ_ERROR", 
                    "description": f"Error checking methods: {e}",
                    "severity": "ERROR"
                })
        
        return findings
    
    def check_hard_disable_implementation(self) -> List[Dict]:
        """Check that update_processing_index is hard-disabled."""
        findings = []
        state_manager_path = self.workspace_root / "utils/fixed_enhanced_state_manager.py"
        
        if state_manager_path.exists():
            try:
                with open(state_manager_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for NotImplementedError in update_processing_index
                pattern = r"def update_processing_index.*?NotImplementedError"
                if not re.search(pattern, content, re.DOTALL):
                    findings.append({
                        "type": "MISSING_HARD_DISABLE",
                        "description": "update_processing_index not hard-disabled with NotImplementedError",
                        "severity": "CRITICAL",
                        "file": str(state_manager_path)
                    })
                    
            except Exception as e:
                findings.append({
                    "type": "READ_ERROR",
                    "description": f"Error checking hard disable: {e}",
                    "severity": "ERROR"
                })
                
        return findings
    
    def run_validation(self) -> bool:
        """Run complete validation suite."""
        print("🔍 LEGACY WRITER DETECTION STARTING...")
        
        all_findings = []
        
        # Check each active file
        for file_path in self.active_files:
            full_path = self.workspace_root / file_path
            print(f"📁 Checking: {file_path}")
            
            findings = self.check_file_for_patterns(full_path)
            all_findings.extend(findings)
            
        # Check atomic commit methods
        print("🔧 Checking atomic commit methods...")
        findings = self.check_atomic_commit_methods()
        all_findings.extend(findings)
        
        # Check hard disable
        print("🚨 Checking hard disable implementation...")
        findings = self.check_hard_disable_implementation()
        all_findings.extend(findings)
        
        # Report findings
        critical_count = sum(1 for f in all_findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in all_findings if f.get("severity") == "HIGH")
        
        if all_findings:
            print(f"\n❌ ISSUES FOUND: {len(all_findings)} total ({critical_count} critical, {high_count} high)")
            
            for finding in all_findings:
                severity_icon = {"CRITICAL": "🚨", "HIGH": "⚠️", "WARNING": "💡"}.get(finding.get("severity", "INFO"), "ℹ️")
                print(f"{severity_icon} {finding.get('description', 'Unknown issue')}")
                
                if "line" in finding:
                    print(f"   📍 {finding['file']}:{finding['line']}")
                    print(f"   📝 {finding['content']}")
                    
            self.errors_found = True
            return False
        else:
            print("\n🎯 LEGACY WRITER DETECTION: PASSED")
            print("   ✅ No legacy writers detected in active codebase")
            print("   ✅ All atomic commit methods present")
            print("   ✅ Hard disable properly implemented")
            return True

def main():
    detector = LegacyWriterDetector()
    success = detector.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()