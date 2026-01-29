import pandas as pd
import numpy as np

# Load the Excel file
df = pd.read_excel('PART3.xlsx')

print("="*70)
print("PART3.xlsx BASELINE ANALYSIS")
print("="*70)

# Basic counts
print(f"Total rows: {len(df)}")
print()

# Key field presence and counts
print("NON-NULL COUNTS:")
print(f"  EAN (Supplier): {df['EAN'].notna().sum()}")
print(f"  EAN_OnPage (Amazon): {df['EAN_OnPage'].notna().sum()}")
print(f"  ASIN: {df['ASIN'].notna().sum()}")
print(f"  SupplierTitle: {df['SupplierTitle'].notna().sum()}")
print(f"  AmazonTitle: {df['AmazonTitle'].notna().sum()}")
print(f"  bought_in_past_month: {df['bought_in_past_month'].notna().sum()}")
print()

# Clean EAN columns for comparison
df['_sup_ean'] = df['EAN'].astype(str).str.strip()
df['_amz_ean'] = df['EAN_OnPage'].astype(str).str.strip()

# Exact EAN matches
ean_match_mask = (
    (df['_sup_ean'] != '') & 
    (df['_sup_ean'] != 'nan') & 
    (df['_sup_ean'] != '-') &
    (df['_sup_ean'] != 'None') &
    (df['_amz_ean'] != '') & 
    (df['_amz_ean'] != 'nan') & 
    (df['_amz_ean'] != '-') &
    (df['_amz_ean'] != 'None') &
    (df['_sup_ean'] == df['_amz_ean'])
)
exact_ean_count = ean_match_mask.sum()
print(f"EXACT EAN MATCHES (Supplier EAN == Amazon EAN): {exact_ean_count}")

# List the ASINs with exact EAN matches
exact_ean_asins = df.loc[ean_match_mask, 'ASIN'].tolist()
print(f"  ASINs with exact EAN match: {exact_ean_asins}")
print()

# Rows with Supplier EAN only
has_sup_ean = (df['_sup_ean'] != '') & (df['_sup_ean'] != 'nan') & (df['_sup_ean'] != '-') & (df['_sup_ean'] != 'None')
has_amz_ean = (df['_amz_ean'] != '') & (df['_amz_ean'] != 'nan') & (df['_amz_ean'] != '-') & (df['_amz_ean'] != 'None')
print(f"Rows with Supplier EAN present: {has_sup_ean.sum()}")
print(f"Rows with Amazon EAN present: {has_amz_ean.sum()}")
print()

# Unique ASINs
unique_asins = df['ASIN'].nunique()
print(f"Unique ASINs: {unique_asins}")
print()

# NetProfit analysis
print("NETPROFIT ANALYSIS:")
print(f"  Rows with NetProfit > 0: {(df['NetProfit'] > 0).sum()}")
print(f"  Rows with NetProfit > 1: {(df['NetProfit'] > 1).sum()}")
print(f"  Rows with NetProfit > 5: {(df['NetProfit'] > 5).sum()}")
print()

# Sales (bought_in_past_month) analysis
sales_col = 'bought_in_past_month'
print("SALES ANALYSIS:")
print(f"  Rows with Sales > 0: {(df[sales_col] > 0).sum()}")
print(f"  Rows with Sales >= 50: {(df[sales_col] >= 50).sum()}")
print(f"  Rows with Sales >= 100: {(df[sales_col] >= 100).sum()}")
print()

# Profitable rows
profitable_mask = (df['NetProfit'] > 0) & (df[sales_col] > 0)
print(f"PROFITABLE ROWS (NetProfit > 0 AND Sales > 0): {profitable_mask.sum()}")
print()

# Exact EAN + Profitable
exact_ean_profitable = ean_match_mask & profitable_mask
print(f"EXACT EAN + PROFITABLE: {exact_ean_profitable.sum()}")
exact_ean_profitable_asins = df.loc[exact_ean_profitable, 'ASIN'].tolist()
print(f"  ASINs: {exact_ean_profitable_asins}")
print()

print("="*70)
print("EXACT EAN MATCH DETAILS")
print("="*70)
exact_ean_df = df[ean_match_mask][['ASIN', 'EAN', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'bought_in_past_month']]
pd.set_option('display.max_colwidth', 60)
pd.set_option('display.width', 200)
print(exact_ean_df.to_string())
