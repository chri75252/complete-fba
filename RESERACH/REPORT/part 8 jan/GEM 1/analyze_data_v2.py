import pandas as pd
import re

file_path = "temp_part8.xlsx"
try:
    df = pd.read_excel(file_path, nrows=50)
    
    print("=== ANALYSIS V2 ===")
    
    # 1. Check for trailing numbers in Supplier Title
    print("\n--- TRAILING NUMBER CHECK (Supplier) ---")
    for i, row in df.head(20).iterrows():
        st = str(row['SupplierTitle']).strip()
        if re.search(r'\s\d+$', st):
            print(f"ROW {i}: TRAILING NUM DETECTED: '{st}'")
            
    # 2. Check for explicit units
    print("\n--- EXPLICIT UNITS CHECK (Supplier) ---")
    for i, row in df.head(20).iterrows():
        st = str(row['SupplierTitle']).strip().lower()
        if any(x in st for x in ['pcs', 'pk', 'pack', 'set', 'pce']):
            print(f"ROW {i}: UNIT DETECTED: '{row['SupplierTitle']}'")

    # 3. Check for leading multipliers
    print("\n--- LEADING MULTIPLIER CHECK (Supplier) ---")
    for i, row in df.head(20).iterrows():
        st = str(row['SupplierTitle']).strip()
        if re.match(r'^\d+\s*x', st, re.IGNORECASE):
            print(f"ROW {i}: LEADING MULTIPLIER: '{st}'")

    # 4. Amazon Capacity Multipacks
    print("\n--- AMAZON CAPACITY PATTERNS ---")
    for i, row in df.head(20).iterrows():
        at = str(row['AmazonTitle'])
        # Look for N x Mml or similar
        if re.search(r'\d+\s*x\s*\d+\s*(ml|g|l|kg)', at, re.IGNORECASE):
             print(f"ROW {i}: CAPACITY MULTIPACK: '{at[:80]}...'")

    # 5. Raw titles for manual brand check
    print("\n--- RAW TITLES (First 10) ---")
    for i, row in df.head(10).iterrows():
        print(f"R{i} SUP: {row['SupplierTitle']}")
        print(f"R{i} AMZ: {row['AmazonTitle'][:60]}...")
        print("-" * 10)

except Exception as e:
    print(e)
