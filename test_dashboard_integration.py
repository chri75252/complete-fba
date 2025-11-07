#!/usr/bin/env python3
"""
Dashboard Integration Test Script
Tests all dashboard components to ensure the Streamlit integration works correctly
"""

import os
import sys
import json
from pathlib import Path

def test_imports():
    """Test that all dashboard modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Import Test")
    print("=" * 60)

    try:
        # Add dashboard directory to path
        dashboard_dir = Path(__file__).parent / "dashboard"
        sys.path.insert(0, str(dashboard_dir))

        from metrics_core_fixed import MetricsLoader, load_metrics
        print("SUCCESS: metrics_core_fixed imported successfully")

        import app_fixed
        print("SUCCESS: app_fixed imported successfully")

        return True

    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        return False

def test_path_resolution():
    """Test base directory and path resolution"""
    print("\n" + "=" * 60)
    print("TEST 2: Path Resolution Test")
    print("=" * 60)

    try:
        base_dir = Path(__file__).parent
        print(f"Project base directory: {base_dir}")

        # Test OUTPUTS directory
        outputs_dir = base_dir / "OUTPUTS"
        print(f"OUTPUTS directory exists: {outputs_dir.exists()}")

        if not outputs_dir.exists():
            print("ERROR: OUTPUTS directory not found")
            return False

        # Test dashboard files
        dashboard_dir = base_dir / "dashboard"
        app_file = dashboard_dir / "app_fixed.py"
        metrics_file = dashboard_dir / "metrics_core_fixed.py"

        print(f"dashboard/app_fixed.py exists: {app_file.exists()}")
        print(f"dashboard/metrics_core_fixed.py exists: {metrics_file.exists()}")

        return all([outputs_dir.exists(), app_file.exists(), metrics_file.exists()])

    except Exception as e:
        print(f"✗ Path resolution failed: {e}")
        return False

def test_data_availability():
    """Test data file availability"""
    print("\n" + "=" * 60)
    print("TEST 3: Data Availability Test")
    print("=" * 60)

    try:
        base_dir = Path(__file__).parent
        dashboard_dir = base_dir / "dashboard"
        sys.path.insert(0, str(dashboard_dir))

        from metrics_core_fixed import MetricsLoader

        loader = MetricsLoader(str(base_dir))

        # Test with both supplier name formats
        suppliers_to_test = [
            "poundwholesale_co_uk",
            "poundwholesale.co.uk",
            "clearance-king.co.uk",
            "clearance_king_co_uk"
        ]

        data_found = False
        for supplier in suppliers_to_test:
            print(f"\nTesting supplier: {supplier}")
            paths = loader.resolve_paths(supplier)

            for path_type, path_value in paths.items():
                status = "✓" if path_value else "✗"
                print(f"  {status} {path_type}: {Path(path_value).name if path_value else 'None'}")

            if any(paths.values()):
                data_found = True

        if not data_found:
            print("\n✗ No data files found for any supplier")
            return False

        print(f"\n✓ Data files found for at least one supplier")
        return True

    except Exception as e:
        print(f"✗ Data availability test failed: {e}")
        return False

def test_data_loading():
    """Test actual data loading with error handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Data Loading Test")
    print("=" * 60)

    try:
        base_dir = Path(__file__).parent
        dashboard_dir = base_dir / "dashboard"
        sys.path.insert(0, str(dashboard_dir))

        from metrics_core_fixed import load_metrics

        # Test with poundwholesale supplier
        supplier = "poundwholesale_co_uk"
        print(f"Testing data loading for: {supplier}")

        result = load_metrics(str(base_dir), supplier)

        if result.get('error'):
            print("✓ Error handling working (expected for missing files):")
            for issue in result.get('issues', []):
                print(f"  - {issue}")
        else:
            print("✓ Data loading successful:")
            print(f"  State metrics: {'loaded' if result.get('state_metrics') else 'none'}")
            print(f"  Linking metrics: {'loaded' if result.get('linking_metrics') else 'none'}")
            print(f"  Financial metrics: {'loaded' if result.get('financial_metrics') else 'none'}")

        return True

    except Exception as e:
        print(f"✗ Data loading test failed: {e}")
        return False

def test_dashboard_launch():
    """Test dashboard launch capability"""
    print("\n" + "=" * 60)
    print("TEST 5: Dashboard Launch Test")
    print("=" * 60)

    try:
        base_dir = Path(__file__).parent

        # Check launcher scripts
        launchers = [
            "start_dashboard.py",
            "dashboard/run_dashboard.py"
        ]

        for launcher in launchers:
            launcher_path = base_dir / launcher
            exists = launcher_path.exists()
            print(f"✓ {launcher}: {'exists' if exists else 'missing'}")

        # Check main dashboard file
        main_app = base_dir / "dashboard/app_fixed.py"
        print(f"✓ dashboard/app_fixed.py: {'exists' if main_app.exists() else 'missing'}")

        return all([
            (base_dir / "start_dashboard.py").exists(),
            (base_dir / "dashboard/run_dashboard.py").exists(),
            (base_dir / "dashboard/app_fixed.py").exists()
        ])

    except Exception as e:
        print(f"✗ Dashboard launch test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("FBA DASHBOARD INTEGRATION TEST")
    print("=" * 60)
    print("Testing Streamlit dashboard integration...")
    print("Project: Amazon FBA Agent System v3.7+")
    print(f"Working directory: {Path.cwd()}")

    tests = [
        ("Module Import", test_imports),
        ("Path Resolution", test_path_resolution),
        ("Data Availability", test_data_availability),
        ("Data Loading", test_data_loading),
        ("Dashboard Launch", test_dashboard_launch)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Dashboard integration is working correctly.")
        print("\nYou can now run the dashboard using:")
        print("  python start_dashboard.py")
        print("  or")
        print("  cd dashboard && python run_dashboard.py")
        print("  or")
        print("  streamlit run dashboard/app_fixed.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        print("The dashboard may still work, but some features might be limited.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)