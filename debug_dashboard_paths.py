import sys
import os
from pathlib import Path

# Add dashboard directory to path
sys.path.append(os.path.join(os.getcwd(), 'dashboard'))

try:
    from metrics_core import MetricsLoader
except ImportError:
    # If running from root, dashboard.metrics_core might be needed or just add dashboard to sys.path
    sys.path.append(os.getcwd())
    from dashboard.metrics_core import MetricsLoader

def test_paths():
    base_dir = os.getcwd()
    print(f"Base Directory: {base_dir}")
    
    loader = MetricsLoader(base_dir)
    
    suppliers_to_test = [
        "angelwholesale.co.uk",
        "angelwholesale_co_uk",
        "angelwholesale-co-uk" # Testing if user manually types this
    ]
    
    for supplier in suppliers_to_test:
        print(f"\n--- Testing Supplier: '{supplier}' ---")
        paths = loader.resolve_paths(supplier)
        financial_dir = paths.get("financial_dir")
        print(f"Resolved Financial Dir: {financial_dir}")
        
        if financial_dir:
            if os.path.exists(financial_dir):
                print("  [OK] Directory exists")
                # List latest file
                files = [f for f in os.listdir(financial_dir) if f.endswith('.csv')]
                if files:
                    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(financial_dir, f)))
                    print(f"  Latest File: {latest}")
                else:
                    print("  [WARN] No CSV files found")
            else:
                print("  [FAIL] Directory does not exist")
        else:
            print("  [FAIL] No financial dir resolved")

if __name__ == "__main__":
    test_paths()
