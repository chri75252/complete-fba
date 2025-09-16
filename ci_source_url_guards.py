#!/usr/bin/env python3
"""
CI Guard script to prevent regression of source_url fixes.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_scraper_method_signature():
    """Check that _extract_product_data_from_soup accepts category_url parameter."""
    scraper_file = project_root / "tools" / "configurable_supplier_scraper.py"
    
    if not scraper_file.exists():
        print(f"❌ Scraper file not found: {scraper_file}")
        return False
    
    with open(scraper_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that the method signature includes category_url
    if "async def _extract_product_data_from_soup(" in content and "category_url: Optional[str] = None" in content:
        print("✅ Scraper method signature includes category_url parameter")
        return True
    else:
        print("❌ Scraper method signature missing category_url parameter")
        return False

def check_scraper_includes_source_url():
    """Check that the scraper method includes source_url in returned product dict."""
    scraper_file = project_root / "tools" / "configurable_supplier_scraper.py"
    
    if not scraper_file.exists():
        print(f"❌ Scraper file not found: {scraper_file}")
        return False
    
    with open(scraper_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that the return dict includes source_url
    if '"source_url": category_url' in content:
        print("✅ Scraper method includes source_url in returned product dict")
        return True
    else:
        print("❌ Scraper method missing source_url in returned product dict")
        return False

def check_workflow_backstop():
    """Check that the workflow has the backstop for missing source_url."""
    workflow_file = project_root / "tools" / "passive_extraction_workflow_latest.py"
    
    if not workflow_file.exists():
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    with open(workflow_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that the backstop code exists
    if 'missing_src = 0' in content and 'if "source_url" not in _p or not _p.get("source_url"):' in content:
        print("✅ Workflow backstop for missing source_url exists")
        return True
    else:
        print("❌ Workflow backstop for missing source_url missing")
        return False

def check_state_manager_tolerance():
    """Check that the state manager handles missing source_url gracefully."""
    state_manager_file = project_root / "utils" / "fixed_enhanced_state_manager.py"
    
    if not state_manager_file.exists():
        print(f"❌ State manager file not found: {state_manager_file}")
        return False
    
    with open(state_manager_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check that the method handles missing source_url gracefully
    if "missing = 0" in content and "if not src:" in content and "ignored in category analysis" in content:
        print("✅ State manager handles missing source_url gracefully")
        return True
    else:
        print("❌ State manager does not handle missing source_url gracefully")
        return False

def main():
    """Run all CI guards."""
    print("🛡️ Running CI guards for source_url fixes...")
    print("=" * 50)
    
    # Run checks
    checks = [
        check_scraper_method_signature(),
        check_scraper_includes_source_url(),
        check_workflow_backstop(),
        check_state_manager_tolerance(),
    ]
    
    print("=" * 50)
    
    if all(checks):
        print("🎉 All CI guards PASSED! The source_url fixes are protected from regression.")
        return 0
    else:
        print("❌ Some CI guards FAILED! The source_url fixes may be at risk of regression.")
        return 1

if __name__ == "__main__":
    sys.exit(main())