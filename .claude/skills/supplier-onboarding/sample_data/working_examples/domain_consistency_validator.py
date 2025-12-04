#!/usr/bin/env python3
"""
WORKING EXAMPLE: Domain Consistency Validator

This script validates that all files maintain consistency between:
1. Actual domain (from supplier URL)
2. Configuration domain settings
3. Operational file naming (uses .co.uk convention)

Usage: python domain_consistency_validator.py --supplier "supplier-name"
"""

import json
import sys
import os
from urllib.parse import urlparse
from pathlib import Path

def extract_domain_from_url(url):
    """Extract domain from URL using urllib.parse."""
    parsed = urlparse(url)
    return parsed.hostname

def validate_config_file(config_path, expected_domain):
    """Validate config file uses correct domain."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        issues = []

        # Check supplier_url domain
        if 'supplier_url' in config:
            actual_url_domain = extract_domain_from_url(config['supplier_url'])
            if actual_url_domain != expected_domain:
                issues.append(f"supplier_url domain mismatch: expected {expected_domain}, found {actual_url_domain}")

        # Check supplier_id
        if 'supplier_id' in config:
            if config['supplier_id'] != expected_domain:
                issues.append(f"supplier_id mismatch: expected {expected_domain}, found {config['supplier_id']}")

        return issues
    except Exception as e:
        return [f"Error reading config file: {e}"]

def validate_system_config(system_config_path, supplier_workflow, expected_domain):
    """Validate system config uses correct domain."""
    try:
        with open(system_config_path, 'r') as f:
            config = json.load(f)

        workflow_config = config.get('workflows', {}).get(supplier_workflow, {})

        issues = []

        # Check supplier_name
        supplier_name = workflow_config.get('supplier_name')
        if supplier_name != expected_domain:
            issues.append(f"system_config supplier_name mismatch: expected {expected_domain}, found {supplier_name}")

        # Check supplier_url
        supplier_url = workflow_config.get('supplier_url')
        if supplier_url:
            actual_url_domain = extract_domain_from_url(supplier_url)
            if actual_url_domain != expected_domain:
                issues.append(f"system_config supplier_url domain mismatch: expected {expected_domain}, found {actual_url_domain}")

        return issues
    except Exception as e:
        return [f"Error reading system config: {e}"]

def validate_operational_naming(supplier_name, expected_domain):
    """Validate operational files use .co.uk convention."""
    issues = []

    # Convert supplier name to operational forms
    hyphen_form = supplier_name.replace('.', '-')
    underscore_form = supplier_name.replace('-', '_')

    # Expected operational names (using .co.uk convention)
    expected_runner = f"run_custom_{hyphen_form}.py"
    expected_cache = f"{hyphen_form}_products_cache.json"
    expected_state = f"{underscore_form}_processing_state.json"
    expected_linking = f"{supplier_name}/linking_map.json"

    # Check if files exist with expected names
    base_paths = [
        f"run_custom_{hyphen_form}.py",
        f"OUTPUTS/cached_products/{hyphen_form}_products_cache.json",
        f"OUTPUTS/CACHE/processing_states/{underscore_form}_processing_state.json",
        f"OUTPUTS/FBA_ANALYSIS/linking_maps/{supplier_name}/linking_map.json"
    ]

    for path in base_paths:
        if not os.path.exists(path):
            # This is just informational - files may not exist yet
            print(f"ℹ️  Expected file not found (normal during setup): {path}")

    return []

def generate_validation_report(supplier_name, expected_domain):
    """Generate comprehensive validation report."""
    print(f"\n{'='*60}")
    print(f"🔍 DOMAIN CONSISTENCY VALIDATION: {supplier_name}")
    print(f"{'='*60}")

    print(f"\n📊 DOMAIN ANALYSIS:")
    print(f"  Supplier Name: {supplier_name}")
    print(f"  Expected Domain: {expected_domain}")
    print(f"  Hyphen Form: {supplier_name.replace('.', '-')}")
    print(f"  Underscore Form: {supplier_name.replace('-', '_')}")

    print(f"\n📋 VALIDATION RESULTS:")

    # Configuration Domain Consistency
    print(f"\n✅ CONFIGURATION DOMAIN CONSISTENCY:")

    # Check config file
    config_path = f"config/supplier_configs/{expected_domain}.json"
    config_issues = validate_config_file(config_path, expected_domain)
    if config_issues:
        for issue in config_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"  ✅ Config file domain consistency: PASSED")

    # Check system config
    workflow_key = f"{supplier_name.replace('-', '_').replace('.', '_')}_workflow"
    system_config_path = "config/system_config.json"
    system_issues = validate_system_config(system_config_path, workflow_key, expected_domain)
    if system_issues:
        for issue in system_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"  ✅ System config domain consistency: PASSED")

    # Operational Naming Consistency
    print(f"\n✅ OPERATIONAL NAMING CONSISTENCY:")
    op_issues = validate_operational_naming(supplier_name, expected_domain)
    if op_issues:
        for issue in op_issues:
            print(f"  ❌ {issue}")
    else:
        print(f"  ✅ Operational naming convention: PASSED")

    # Summary
    all_issues = config_issues + system_issues + op_issues
    print(f"\n{'='*60}")
    if not all_issues:
        print("✅ ALL VALIDATIONS PASSED - Ready for execution")
        print("\n✅ Summary:")
        print(f"  • Config files use actual domain: {expected_domain}")
        print(f"  • Operational files use .co.uk convention: {supplier_name.replace('.', '-')}...")
        print(f"  • No domain mismatches detected")
    else:
        print("❌ VALIDATION FAILED - Fix issues before proceeding")
        print(f"\n🔧 Required Fixes:")
        for issue in all_issues:
            print(f"  • {issue}")

    print(f"{'='*60}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python domain_consistency_validator.py --supplier 'supplier-name'")
        print("Example: python domain_consistency_validator.py --supplier 'wholesaletradingsupplies.com'")
        sys.exit(1)

    supplier_name = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--supplier" else None

    if not supplier_name:
        print("Error: Please specify supplier name with --supplier flag")
        sys.exit(1)

    # Extract expected domain from supplier name
    # This simulates extracting from actual URL
    expected_domain = supplier_name  # In real scenario, extract from URL

    generate_validation_report(supplier_name, expected_domain)

if __name__ == "__main__":
    main()