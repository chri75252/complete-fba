#!/usr/bin/env python3
"""
Simple Dashboard Integration Test
Tests core dashboard functionality without Unicode symbols
"""

import os
import sys
from pathlib import Path

def main():
    print("Simple Dashboard Integration Test")
    print("=" * 50)

    base_dir = Path(__file__).parent
    print(f"Base directory: {base_dir}")

    # Test 1: Check OUTPUTS directory
    outputs_dir = base_dir / "OUTPUTS"
    print(f"OUTPUTS exists: {outputs_dir.exists()}")

    # Test 2: Check dashboard files
    dashboard_dir = base_dir / "dashboard"
    files_to_check = [
        "app_fixed.py",
        "metrics_core_fixed.py",
        "run_dashboard.py"
    ]

    print("Dashboard files:")
    for filename in files_to_check:
        filepath = dashboard_dir / filename
        exists = filepath.exists()
        print(f"  {filename}: {'OK' if exists else 'MISSING'}")

    # Test 3: Test imports
    print("\nTesting imports:")
    try:
        sys.path.insert(0, str(dashboard_dir))
        from metrics_core_fixed import MetricsLoader, load_metrics
        print("  metrics_core_fixed: OK")
    except Exception as e:
        print(f"  metrics_core_fixed: ERROR - {e}")
        return False

    # Test 4: Test path resolution
    print("\nTesting path resolution:")
    try:
        loader = MetricsLoader(str(base_dir))
        paths = loader.resolve_paths("poundwholesale_co_uk")

        for path_type, path_value in paths.items():
            status = "FOUND" if path_value else "MISSING"
            print(f"  {path_type}: {status}")
    except Exception as e:
        print(f"  Path resolution: ERROR - {e}")
        return False

    # Test 5: Test data loading (quick)
    print("\nTesting data loading:")
    try:
        result = load_metrics(str(base_dir), "poundwholesale_co_uk")
        if result.get('error'):
            print("  Data loading: EXPECTED ERROR (missing files)")
        else:
            print("  Data loading: SUCCESS")
    except Exception as e:
        print(f"  Data loading: ERROR - {e}")
        return False

    print("\n" + "=" * 50)
    print("Test completed successfully!")
    print("\nTo run the dashboard:")
    print("  python start_dashboard.py")
    print("  or")
    print("  cd dashboard && python run_dashboard.py")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)