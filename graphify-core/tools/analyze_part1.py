
import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher
import sys

# INPUT/OUTPUT PATHS
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part1.xlsx"
OUTPUT_CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_part1.csv"

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

def is_valid_ean(ean):
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-']

def is_exact_ean_match(row):
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    return ean_sup == ean_amz

def extract_quantity(title):
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    patterns = [
        r'pack of (\d+)', r'set of (\d+)', r'\b(\d+)\s*pack\b', r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b', r'(\d+)\s*pieces?\b', r'(\d+)\s*pairs?\b', r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)', r'\(pack of (\d+)\)', r'\b(\d+)\s*rolls?\b', r'\b(\d+)\s*piece\b',
    ]
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:
                return qty
    return 1.0

def recalculate_profit(row):
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        if ratio > 1.0:
             # Need to buy 'ratio' supplier units to fulfill one Amazon unit
             # Cost increases by supplier_cost * (ratio - 1)
             # Profit decreases by that amount
             adjustment = supplier_cost * (ratio - 1)
             return original_profit - adjustment
        elif ratio < 1.0 and ratio > 0:
             # Supplier sells multipack (e.g. 10), Amazon sells single (1)
             # We buy 1 supplier unit, sell 10 Amazon units? 
             # Or is it "Supplier larger pack"?
             # If Sup=10, Amz=1. Ratio = 0.1.
             # This means we have 10 units to sell.
             # But the 'NetProfit' in the report is usually calculated per Amazon Sale.
             # If the report assumed Cost = SupplierPrice, then Profit = Sale - Fees - SupplierPrice.
             # But actually Cost per unit = SupplierPrice * Ratio.
             # So RealCost = SupplierPrice * 0.1.
             # Adjustment: We save money per unit.
             # OldCost = SupplierPrice. NewCost = SupplierPrice * Ratio.
             # Saving = SupplierPrice - (SupplierPrice * Ratio) = SupplierPrice * (1 - Ratio).
             # Profit increases by Saving.
             saving = supplier_cost * (1 - ratio)
             return original_profit + saving
        else:
             return original_profit
    except:
        return 0.0

def categorize(row):
    if row['is_exact_ean']:
        return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.50:
        return 'HIGH_LIKELIHOOD'
    elif row['title_match'] >= 0.30:
        return 'MODERATE_CONFIDENCE'
    else:
        return 'UNCERTAIN'

def pack_verdict(row):
    if row['Qty_Ratio'] == 1.0:
        return "1:1 Match"
    elif row['Qty_Ratio'] > 1.0:
        if row['Adjusted_Profit'] > 0:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - OK"
        else:
            return f"BUNDLE ({int(row['Qty_Ratio'])}x) - LOSS"
    else:
        if row['Adjusted_Profit'] > 0:
            return f"SPLIT (1/{int(1/row['Qty_Ratio'])}) - OK"
        else:
            return "SPLIT - LOSS"

print("Loading data...")
try:
    df = pd.read_excel(INPUT_PATH)
except Exception as e:
    print(f"Error reading Excel, trying CSV logic just in case: {e}")
    # Fallback if user named it xlsx but it's csv
    df = pd.read_csv(INPUT_PATH)

print(f"Loaded {len(df)} rows.")

# STAGE 1: CLEANING
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
else:
    df['sales'] = 0

# STAGE 2: TITLE MATCH
df['title_match'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# STAGE 3: STRICT EAN
df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)

# STAGE 4: PACK SIZE
df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']
df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# STAGE 5: CATEGORIZE
df['category'] = df.apply(categorize, axis=1)
df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# SAVE FULL OUTPUT
df.to_csv(OUTPUT_CSV_PATH, index=False)
print(f"Saved processed data to {OUTPUT_CSV_PATH}")

# PRINT ANALYSIS FOR MANUAL REVIEW
# Recommendation Filter: Sales > 0 AND NetProfit > 0 AND Adjusted_Profit > 0

print("\n\n=== STAGE 6: CANDIDATES FOR MANUAL VERIFICATION ===\n")

# Filter for candidates
candidates = df[
    (df['sales'] > 0) & 
    (df['NetProfit'] > 0) & 
    (df['Adjusted_Profit'] > 0)
].copy()

# Sort by Sales
candidates = candidates.sort_values(by='sales', ascending=False)

# GROUP 1: EXACT EAN MATCHES
exact = candidates[candidates['category'] == 'EXACT_EAN_MATCH']
print(f"--- EXACT EAN MATCHES ({len(exact)}) ---")
for idx, row in exact.head(20).iterrows():
    print(f"INDEX: {idx}")
    print(f"  Sales: {row['sales']}")
    print(f"  Titles: {row['SupplierTitle']}  VS  {row['AmazonTitle']}")
    print(f"  EANs: {row['EAN']} (Sup) vs {row['EAN_OnPage']} (Amz)")
    print(f"  Price: Buy £{row['SupplierPrice_incVAT']} -> Sell £{row['SellingPrice_incVAT']}")
    print(f"  Profit: Original £{row['NetProfit']:.2f} -> Adj £{row['Adjusted_Profit']:.2f}")
    print(f"  Pack: {row['Pack_Verdict']} (Ratio {row['Qty_Ratio']})")
    print("-" * 50)

# GROUP 2: HIGH LIKELIHOOD (Non-Exact EAN)
high = candidates[candidates['category'] == 'HIGH_LIKELIHOOD']
print(f"\n--- HIGH LIKELIHOOD CANDIDATES ({len(high)}) ---")
for idx, row in high.head(30).iterrows():
    print(f"INDEX: {idx}")
    print(f"  Sales: {row['sales']}")
    print(f"  Titles: {row['SupplierTitle']}  VS  {row['AmazonTitle']}")
    print(f"  EANs: {row['EAN']} (Sup) vs {row['EAN_OnPage']} (Amz)")
    print(f"  Price: Buy £{row['SupplierPrice_incVAT']} -> Sell £{row['SellingPrice_incVAT']}")
    print(f"  Profit: Original £{row['NetProfit']:.2f} -> Adj £{row['Adjusted_Profit']:.2f}")
    print(f"  Pack: {row['Pack_Verdict']} (Ratio {row['Qty_Ratio']})")
    print("-" * 50)

# GROUP 3: EXACT EAN BUT FILTERED OUT (For Audit)
# Sales > 0, NetProfit > 0 but Pack adjusted profit <= 0 OR some other issue?
# Actually, let me check strict EAN matches that failed the profit filter
exact_filtered = df[
    (df['is_exact_ean'] == True) &
    (df['sales'] > 0) &
    ((df['NetProfit'] <= 0) | (df['Adjusted_Profit'] <= 0))
].sort_values(by='sales', ascending=False)

print(f"\n--- EXACT EAN MATCHES (FILTERED OUT / UNPROFITABLE) ({len(exact_filtered)}) ---")
for idx, row in exact_filtered.head(10).iterrows():
    print(f"INDEX: {idx}")
    print(f"  Reason: Profit £{row['NetProfit']} / Adj £{row['Adjusted_Profit']}")
    print(f"  Titles: {row['SupplierTitle']}  VS  {row['AmazonTitle']}")
    print("-" * 50)

