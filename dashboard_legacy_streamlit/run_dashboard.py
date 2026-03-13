#!/usr/bin/env python3
"""
FBA Dashboard Launcher - FIXED VERSION
Fixed version with proper path resolution from dashboard directory
"""

import os
import sys
import subprocess
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["streamlit", "pandas"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")

        print("Installing missing packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("Packages installed successfully")

        except subprocess.CalledProcessError as e:
            print(f"Failed to install packages: {e}")

            return False
    else:
        print("All required packages are installed")

    return True


def check_data_availability():
    """Check if FBA system data is available"""
    # Get project root directory (parent of dashboard directory)
    current_dir = os.getcwd()
    if current_dir.endswith("dashboard"):
        base_dir = os.path.dirname(current_dir)
    else:
        base_dir = current_dir

    outputs_dir = os.path.join(base_dir, "OUTPUTS")

    if not os.path.exists(outputs_dir):
        print(f"OUTPUTS directory not found: {outputs_dir}")

        print("Please run the FBA system first to generate data")
        return False

    # Check for key data files
    cache_dir = os.path.join(outputs_dir, "CACHE")
    if not os.path.exists(cache_dir):
        print("No CACHE directory found")

    financial_dir = os.path.join(outputs_dir, "FBA_ANALYSIS", "financial_reports")
    if not os.path.exists(financial_dir):
        print("No financial reports found")

    linking_dir = os.path.join(outputs_dir, "FBA_ANALYSIS", "linking_maps")
    if not os.path.exists(linking_dir):
        print("No linking maps found")

    logs_dir = os.path.join(base_dir, "logs", "debug")
    if not os.path.exists(logs_dir):
        print("No debug logs found")

    print("Basic directory structure found")

    return True, base_dir


def setup_environment(base_dir):
    """Set up environment for dashboard"""
    # Set base directory environment variable
    os.environ["FBA_BASE_DIR"] = base_dir
    print(f"Base directory set to: {base_dir}")

    return base_dir


def run_dashboard():
    """Run the Streamlit dashboard"""
    print("Starting FBA Analytics Dashboard...")

    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed")

        return

    # Check data availability and get base directory
    data_check = check_data_availability()
    if not data_check:
        print("Data availability check failed")

    base_dir = (
        check_data_availability()[1] if isinstance(data_check, tuple) else data_check or os.getcwd()
    )

    # Setup environment
    base_dir = setup_environment(base_dir)

    # Determine which app to use
    dashboard_dir = os.path.join(base_dir, "dashboard")
    app_fixed = os.path.join(dashboard_dir, "app_fixed.py")
    app_original = os.path.join(dashboard_dir, "app.py")

    app_file = app_fixed if os.path.exists(app_fixed) else app_original

    if not os.path.exists(app_file):
        print(f"Dashboard app not found: {app_file}")

        print("Available files in dashboard directory:")
        try:
            files = os.listdir(dashboard_dir)
            for f in files:
                if f.endswith(".py"):
                    print(f"  - {f}")
        except:
            pass
        return

    print(f"Using dashboard app: {os.path.basename(app_file)}")

    print("=" * 50)

    try:
        # Run Streamlit with fixed configuration
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                app_file,
                "--server.port",
                "8501",
                "--server.headless",
                "false",
                "--browser.gatherUsageStats",
                "false",
                "--logger.level",
                "info",
            ]
        )
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")

    except Exception as e:
        print(f"Error running dashboard: {e}")


if __name__ == "__main__":
    run_dashboard()
