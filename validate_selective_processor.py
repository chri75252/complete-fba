#!/usr/bin/env python3
"""
Validation Script for Selective ASIN Processor

This script validates the selective ASIN processor setup and creates a backup
before running any processing. It checks system requirements, file paths,
and creates safety backups.

Author: Amazon FBA Agent System
Created: 2025-01-26
"""

import json
import os
import shutil
import sys
from datetime import datetime

def create_backup_directory():
    """Create timestamped backup directory."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"backup/selective_asin_processor_test_{timestamp}"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_backup_path = os.path.join(base_dir, backup_dir)

    os.makedirs(full_backup_path, exist_ok=True)
    return full_backup_path

def backup_critical_files(backup_dir):
    """Backup critical files before processing."""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    critical_paths = [
        "OUTPUTS/FBA_ANALYSIS/linking_maps",
        "OUTPUTS/FBA_ANALYSIS/amazon_cache",
        "OUTPUTS/CACHE/processing_states"
    ]

    backed_up_files = []

    for rel_path in critical_paths:
        full_path = os.path.join(base_dir, rel_path)
        if os.path.exists(full_path):
            dest_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if os.path.isdir(full_path):
                shutil.copytree(full_path, dest_path, dirs_exist_ok=True)
                backed_up_files.append(f"Directory: {rel_path}")
            else:
                shutil.copy2(full_path, dest_path)
                backed_up_files.append(f"File: {rel_path}")

    return backed_up_files

def validate_input_file(file_path):
    """Validate the input JSON file."""
    print(f"Validating input file: {os.path.basename(file_path)}")

    if not os.path.exists(file_path):
        print(f"X File not found: {file_path}")
        return False, []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("X File format error: Expected a JSON array")
            return False, []

        print(f"OK File loaded successfully: {len(data)} entries")

        # Validate entry structure
        valid_entries = []
        invalid_entries = []

        required_fields = ['supplier_ean', 'amazon_asin', 'supplier_title']

        for i, entry in enumerate(data):
            if all(field in entry and entry[field] for field in required_fields):
                if entry['amazon_asin'] != 'null':
                    valid_entries.append(entry)
                else:
                    invalid_entries.append(f"Entry {i+1}: ASIN is null")
            else:
                missing = [field for field in required_fields if field not in entry or not entry[field]]
                invalid_entries.append(f"Entry {i+1}: Missing fields: {missing}")

        print(f"Validation Results:")
        print(f"   Valid entries: {len(valid_entries)}")
        print(f"   Invalid entries: {len(invalid_entries)}")

        if invalid_entries and len(invalid_entries) <= 5:
            print("! Invalid entries:")
            for inv in invalid_entries[:5]:
                print(f"   - {inv}")
        elif len(invalid_entries) > 5:
            print(f"! {len(invalid_entries)} invalid entries found (showing first 5):")
            for inv in invalid_entries[:5]:
                print(f"   - {inv}")

        return len(valid_entries) > 0, valid_entries

    except json.JSONDecodeError as e:
        print(f"X JSON parsing error: {e}")
        return False, []
    except Exception as e:
        print(f"X File validation error: {e}")
        return False, []

def check_system_requirements():
    """Check if system requirements are met."""
    print("Checking system requirements...")

    issues = []

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        issues.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
    else:
        print(f"OK Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Check required modules
    required_modules = [
        'playwright',
        'asyncio',
        'json',
        'pandas',
        'logging'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        issues.append(f"Missing modules: {', '.join(missing_modules)}")
    else:
        print(f"OK All required modules available")

    # Check critical directories exist
    base_dir = os.path.dirname(os.path.abspath(__file__))
    critical_dirs = [
        'config',
        'tools',
        'utils',
        'OUTPUTS/FBA_ANALYSIS'
    ]

    missing_dirs = []
    for dir_path in critical_dirs:
        full_path = os.path.join(base_dir, dir_path)
        if not os.path.exists(full_path):
            missing_dirs.append(dir_path)

    if missing_dirs:
        issues.append(f"Missing directories: {', '.join(missing_dirs)}")
    else:
        print(f"OK All critical directories found")

    return issues

def analyze_processing_scope(valid_entries):
    """Analyze the scope of processing."""
    print("\nProcessing Scope Analysis:")

    # Count unique ASINs and EANs
    unique_asins = set(entry['amazon_asin'] for entry in valid_entries)
    unique_eans = set(entry['supplier_ean'] for entry in valid_entries)

    print(f"   Total entries: {len(valid_entries)}")
    print(f"   Unique ASINs: {len(unique_asins)}")
    print(f"   Unique EANs: {len(unique_eans)}")

    # Estimate processing time (2-3 seconds per entry)
    estimated_time_min = len(valid_entries) * 2 / 60
    estimated_time_max = len(valid_entries) * 3 / 60

    print(f"   Estimated time: {estimated_time_min:.1f}-{estimated_time_max:.1f} minutes")

    # Show sample entries
    print("\nSample entries to be processed:")
    for i, entry in enumerate(valid_entries[:3]):
        print(f"   {i+1}. EAN: {entry['supplier_ean']} -> ASIN: {entry['amazon_asin']}")
        print(f"      Title: {entry['supplier_title'][:50]}...")

    if len(valid_entries) > 3:
        print(f"   ... and {len(valid_entries) - 3} more entries")

def main():
    """Main validation function."""
    print("SELECTIVE ASIN PROCESSOR - VALIDATION & BACKUP")
    print("="*70)

    # Define input file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(
        base_dir,
        "OUTPUTS", "FBA_ANALYSIS", "linking_maps", "poundwholesale.co.uk",
        "not_found_asins.json"
    )

    # Step 1: Check system requirements
    print("Step 1: System Requirements")
    print("-" * 30)
    system_issues = check_system_requirements()

    if system_issues:
        print("\nX System issues found:")
        for issue in system_issues:
            print(f"   - {issue}")
        print("\n! Please resolve these issues before running the processor")
        return False

    print("OK All system requirements met\n")

    # Step 2: Validate input file
    print("Step 2: Input File Validation")
    print("-" * 30)
    file_valid, valid_entries = validate_input_file(input_file)

    if not file_valid:
        print("\nX Input file validation failed")
        return False

    # Step 3: Analyze processing scope
    analyze_processing_scope(valid_entries)

    # Step 4: Create backup
    print("\nStep 3: Creating Safety Backup")
    print("-" * 30)
    try:
        backup_dir = create_backup_directory()
        backed_up = backup_critical_files(backup_dir)

        print(f"OK Backup created: {backup_dir}")
        print("Backed up files/directories:")
        for item in backed_up:
            print(f"   - {item}")

        # Create backup manifest
        manifest_path = os.path.join(backup_dir, "backup_manifest.json")
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'purpose': 'selective_asin_processor_test',
            'backed_up_items': backed_up,
            'input_file': input_file,
            'valid_entries_count': len(valid_entries),
            'estimated_processing_time_minutes': len(valid_entries) * 2.5 / 60
        }

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"OK Backup manifest saved: backup_manifest.json")

    except Exception as e:
        print(f"X Backup creation failed: {e}")
        return False

    # Step 5: Final confirmation
    print(f"\nVALIDATION COMPLETE")
    print("="*70)
    print("OK System ready for selective ASIN processing")
    print(f"Ready to process {len(valid_entries)} valid entries")
    print(f"Backup created at: {backup_dir}")
    print("\nYou can now run:")
    print("   python run_selective_asin_processor.py --interactive")
    print("   or")
    print("   python run_selective_asin_processor.py")

    return True

if __name__ == "__main__":
    """Entry point for validation script."""
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n! Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n! Validation error: {e}")
        sys.exit(1)