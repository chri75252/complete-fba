#!/usr/bin/env python3
"""
FBA Dashboard Launcher - Updated for New Streamlit Dashboard
Launches the robust Streamlit FBA Analytics Dashboard with error handling.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Launch the FBA Analytics Dashboard"""
    print("Starting FBA Analytics Dashboard...")
    print("=" * 50)

    # Get project directory
    project_dir = Path(__file__).parent
    dashboard_file = project_dir / "dashboard" / "streamlit_fba_dashboard.py"

    print(f"Project Directory: {project_dir}")
    print(f"Dashboard File: {dashboard_file}")

    # Check if dashboard file exists
    if not dashboard_file.exists():
        print(f"Error: Dashboard file not found at {dashboard_file}")
        print("Expected location: dashboard/streamlit_fba_dashboard.py")
        return 1

    # Check if financial reports exist
    financial_reports_path = project_dir / "OUTPUTS" / "FBA_ANALYSIS" / "financial_reports" / "poundwholesale-co-uk"
    if not financial_reports_path.exists():
        print(f"Warning: Financial reports directory not found at {financial_reports_path}")
        print("Please run the FBA analysis system first to generate data.")
    else:
        csv_files = list(financial_reports_path.glob("fba_financial_report_*.csv"))
        if csv_files:
            latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
            print(f"Found financial report: {latest_file.name}")
            print(f"Report size: {latest_file.stat().st_size / 1024:.1f} KB")
        else:
            print("Warning: No financial report CSV files found.")
            print("The dashboard will start but show limited data.")

    # Change to project directory
    os.chdir(project_dir)

    try:
        print("\nLaunching Streamlit dashboard...")
        print("Dashboard will be available at: http://localhost:8501")
        print("Press Ctrl+C to stop the dashboard")
        print("=" * 50)

        # Run streamlit with proper configuration
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ]

        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error starting Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())