#!/usr/bin/env python3
"""
Investigate Superior brand products and missing profit data
"""
import pandas as pd
import numpy as np

# Load data
df = pd.read_excel(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx")
df.columns = [c.strip() for c in df.columns]

print("=" * 60)
print("SUPERIOR BRAND PRODUCTS INVESTIGATION")
print("=" * 60)

# Filter for Superior brand products
superior = df[df['SupplierTitle'].str.contains('SUPERIOR', case=False, na=False)]
print(f"\nFound {len(superior)} Superior products in the dataset\n")

for idx, row in superior.iterrows():
    print(f"--- Row {idx+2} ---")
    print(f"Title: {str(row['SupplierTitle'])[:60]}")
    print(f"ASIN: {row['ASIN']}")
    print(f"Adjusted Profit: {row['Adjusted Profit']}")
    print(f"ROI: {row['ROI']}")
    print(f"SupplierPrice: {row['SupplierPrice']}")
    print(f"Verdict: {row['Verdict']}")
    
    # Check if profit is missing
    if pd.isna(row['Adjusted Profit']):
        print(">>> ISSUE: Adjusted Profit is NaN/Missing!")
    print()

print("\n" + "=" * 60)
print("ALL ROWS WITH MISSING ADJUSTED PROFIT")
print("=" * 60)

missing_profit = df[df['Adjusted Profit'].isna()]
print(f"\nTotal rows with missing Adjusted Profit: {len(missing_profit)}\n")

for idx, row in missing_profit.iterrows():
    print(f"Row {idx+2}: {str(row['SupplierTitle'])[:50]}")
    print(f"  ASIN: {row['ASIN']}, ROI: {row['ROI']}, Verdict: {row['Verdict']}")
    print()
