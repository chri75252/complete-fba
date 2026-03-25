"""
Solo Financial Calculator Runner
Regenerates financial reports for all 3 fully-analyzed suppliers using the
fixed FBA_Financial_calculator.py (C1+C2 EAN fix applied).

Suppliers: efghousewares.co.uk, poundwholesale.co.uk, angelwholesale.co.uk

NOTE for angelwholesale: The active linking_map.json has only 11 entries
(overwritten by sandbox runs). This script temporarily uses the correct
9,777-entry map ("angelwholesale actual linkingmap.json") and restores
the original afterward.

Run from the project root directory:
    python run_solo_financial_calc.py
"""

import os
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(ROOT))

from tools.FBA_Financial_calculator import run_calculations

SUPPLIERS = [
    "efghousewares.co.uk",
    "poundwholesale.co.uk",
    "angelwholesale.co.uk",
]

ANGEL_LINKING_DIR = ROOT / "OUTPUTS" / "FBA_ANALYSIS" / "linking_maps" / "angelwholesale.co.uk"
ANGEL_REAL_MAP = ANGEL_LINKING_DIR / "angelwholesale actual linkingmap.json"
ANGEL_CURRENT_MAP = ANGEL_LINKING_DIR / "linking_map.json"
ANGEL_BACKUP = ANGEL_LINKING_DIR / "linking_map.json.solo_runner_backup"


def run_supplier(supplier_name: str):
    print(f"\n{'='*60}")
    print(f"Processing: {supplier_name}")
    print(f"{'='*60}")
    try:
        results = run_calculations(supplier_name)
        stats = results.get("statistics", {})
        out_file = stats.get("output_file", "unknown")
        print(f"\nDone. Output: {out_file}")
        print(f"Records processed: {stats.get('processed', '?')}")
        print(f"Matches found: {stats.get('found_matches', '?')}")
        print(f"Report rows: {stats.get('generated_calculations', '?')}")
        return True
    except Exception as e:
        print(f"\nERROR for {supplier_name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    for supplier in SUPPLIERS:
        swapped = False
        try:
            # For angelwholesale: swap in the correct linking map
            if supplier == "angelwholesale.co.uk":
                if ANGEL_REAL_MAP.exists():
                    print(f"\n[ANGEL] Swapping linking map: using '{ANGEL_REAL_MAP.name}' ({ANGEL_REAL_MAP.stat().st_size:,} bytes)")
                    # Backup current (11-entry) map
                    if ANGEL_CURRENT_MAP.exists():
                        shutil.copy2(ANGEL_CURRENT_MAP, ANGEL_BACKUP)
                    # Replace with real map
                    shutil.copy2(ANGEL_REAL_MAP, ANGEL_CURRENT_MAP)
                    swapped = True
                    print(f"[ANGEL] Real map in place. Entries: ~9,777")
                else:
                    print(f"\n[ANGEL] WARNING: '{ANGEL_REAL_MAP.name}' not found. Using current map (only 11 entries — output will be incomplete).")

            success = run_supplier(supplier)

        finally:
            # Always restore angelwholesale linking_map
            if swapped and ANGEL_BACKUP.exists():
                shutil.copy2(ANGEL_BACKUP, ANGEL_CURRENT_MAP)
                ANGEL_BACKUP.unlink()
                print(f"\n[ANGEL] Original linking_map.json restored.")

    print(f"\n{'='*60}")
    print("All suppliers processed.")
    print("New CSVs with correct EANs are in:")
    for supplier in SUPPLIERS:
        norm = supplier.replace(".", "-")
        print(f"  OUTPUTS/FBA_ANALYSIS/financial_reports/{norm}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
