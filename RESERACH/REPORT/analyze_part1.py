"""
FBA Product Analysis Script - Part 1
Following the Master Prompt V2 protocol for deep analysis.
Generated: 2025-12-23 (Asia/Dubai)
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from pathlib import Path
import json
from datetime import datetime

# Configuration
INPUT_PATH = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part1.xlsx")
OUTPUT_DIR = INPUT_PATH.parent
DATE_STAMP = datetime.now().strftime("%Y%m%d")

print(f"=" * 80)
print(f"FBA PRODUCT ANALYSIS - STAGE 1: DATA LOADING")
print(f"=" * 80)
print(f"Input file: {INPUT_PATH}")
print(f"File exists: {INPUT_PATH.exists()}")

# STAGE 1: Data Loading & Initial Cleaning
df = pd.read_excel(INPUT_PATH)

print(f"\n📊 INITIAL DATA SHAPE: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"\n📋 COLUMNS AVAILABLE:")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. {col}")

# Show first few rows to understand structure
print(f"\n📝 SAMPLE DATA (first 3 rows):")
print(df.head(3).to_string())

# Clean EAN columns - CRITICAL for accurate matching
print(f"\n" + "=" * 80)
print(f"STAGE 1: EAN CLEANING")
print(f"=" * 80)

# Check which EAN columns exist
ean_cols = [col for col in df.columns if 'ean' in col.lower()]
print(f"EAN-related columns found: {ean_cols}")

if 'EAN' in df.columns:
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
if 'EAN_OnPage' in df.columns:
    df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column (check which one exists)
print(f"\n📈 SALES COLUMN DETECTION:")
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
    print(f"  Using 'sales_numeric' column")
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
    print(f"  Using 'bought_in_past_month' column")
else:
    df['sales'] = 0
    print(f"  ⚠️ No sales column found - defaulting to 0")

# STAGE 2: Title Similarity Calculation
print(f"\n" + "=" * 80)
print(f"STAGE 2: TITLE SIMILARITY CALCULATION")
print(f"=" * 80)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

# Check for title columns
title_cols = [col for col in df.columns if 'title' in col.lower()]
print(f"Title-related columns found: {title_cols}")

if 'SupplierTitle' in df.columns and 'AmazonTitle' in df.columns:
    df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
    print(f"  Title similarity calculated for {len(df)} rows")
else:
    # Try alternative column names
    sup_title_col = next((c for c in df.columns if 'supplier' in c.lower() and 'title' in c.lower()), None)
    amz_title_col = next((c for c in df.columns if 'amazon' in c.lower() and 'title' in c.lower()), None)
    
    if sup_title_col and amz_title_col:
        df['title_match'] = df.apply(lambda x: title_similarity(x[sup_title_col], x[amz_title_col]), axis=1)
        print(f"  Using columns: {sup_title_col}, {amz_title_col}")
    else:
        df['title_match'] = 0.0
        print(f"  ⚠️ Could not find title columns")

# STAGE 3: STRICT EAN Matching (CRITICAL)
print(f"\n" + "=" * 80)
print(f"STAGE 3: STRICT EAN MATCHING")
print(f"=" * 80)

def is_valid_ean(ean):
    """Check if EAN is a valid barcode (not empty, nan, None, etc.)"""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-', 'N/A', 'n/a']

def is_exact_ean_match(row):
    """Returns True ONLY if BOTH EANs are valid AND they match exactly"""
    ean_sup = str(row.get('EAN', '')).strip()
    ean_amz = str(row.get('EAN_OnPage', '')).strip()
    
    # Both must be valid
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    
    # Must match exactly
    return ean_sup == ean_amz

if 'EAN' in df.columns and 'EAN_OnPage' in df.columns:
    df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)
    exact_ean_count = df['is_exact_ean'].sum()
    print(f"  ✅ Exact EAN matches found: {exact_ean_count}")
else:
    df['is_exact_ean'] = False
    print(f"  ⚠️ EAN columns not found - no exact matches possible")

# STAGE 4: Pack Size Extraction & Profit Recalculation
print(f"\n" + "=" * 80)
print(f"STAGE 4: PACK SIZE EXTRACTION")
print(f"=" * 80)

def extract_quantity(title):
    """Extract pack size from product title. Defaults to 1."""
    if pd.isna(title):
        return 1.0
    title = str(title).lower()
    
    patterns = [
        r'pack of (\d+)',
        r'set of (\d+)',
        r'\b(\d+)\s*pack\b',
        r'\b(\d+)\s*pk\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces?\b',
        r'(\d+)\s*pairs?\b',
        r'\bx\s*(\d+)\b',
        r'\((\d+)\s*pack\)',
        r'\(pack of (\d+)\)',
        r'\b(\d+)\s*rolls?\b',
        r'\b(\d+)\s*piece\b',
        r'\b(\d+)\s*bags?\b',
        r'\b(\d+)\s*liners?\b',
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:  # Sanity check
                return qty
    return 1.0

# Find title columns
sup_title_col = 'SupplierTitle' if 'SupplierTitle' in df.columns else next((c for c in df.columns if 'supplier' in c.lower() and 'title' in c.lower()), None)
amz_title_col = 'AmazonTitle' if 'AmazonTitle' in df.columns else next((c for c in df.columns if 'amazon' in c.lower() and 'title' in c.lower()), None)

if sup_title_col and amz_title_col:
    df['Sup_Qty'] = df[sup_title_col].apply(extract_quantity)
    df['Amz_Qty'] = df[amz_title_col].apply(extract_quantity)
    df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty']
    print(f"  Pack sizes extracted from: {sup_title_col}, {amz_title_col}")
else:
    df['Sup_Qty'] = 1.0
    df['Amz_Qty'] = 1.0
    df['Qty_Ratio'] = 1.0
    print(f"  ⚠️ Could not find title columns for pack extraction")

# Find price/profit columns
price_col = next((c for c in df.columns if 'supplierprice' in c.lower().replace('_', '')), None)
profit_col = next((c for c in df.columns if 'netprofit' in c.lower().replace('_', '')), None)

print(f"  Price column: {price_col}")
print(f"  Profit column: {profit_col}")

def recalculate_profit(row):
    """
    Adjust profit based on quantity ratio.
    If Amazon sells a 6-pack and Supplier sells singles,
    we need to buy 6 units, so: Adjusted_Profit = Original - (Cost * (Ratio - 1))
    """
    try:
        original_profit = float(row.get(profit_col, 0) if profit_col else row.get('NetProfit', 0))
        supplier_cost = float(row.get(price_col, 0) if price_col else row.get('SupplierPrice_incVAT', 0))
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# STAGE 5: Product Categorization
print(f"\n" + "=" * 80)
print(f"STAGE 5: PRODUCT CATEGORIZATION")
print(f"=" * 80)

def categorize(row):
    if row['is_exact_ean']:  # STRICT: Both EANs valid AND matching
        return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.50:
        return 'HIGH_LIKELIHOOD'
    elif row['title_match'] >= 0.30:
        return 'MODERATE_CONFIDENCE'
    else:
        return 'UNCERTAIN'

df['category'] = df.apply(categorize, axis=1)

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

df['Pack_Verdict'] = df.apply(pack_verdict, axis=1)

# Category counts
print(f"\n📊 CATEGORY DISTRIBUTION:")
for cat in ['EXACT_EAN_MATCH', 'HIGH_LIKELIHOOD', 'MODERATE_CONFIDENCE', 'UNCERTAIN']:
    count = (df['category'] == cat).sum()
    print(f"  {cat}: {count}")

# SUMMARY STATISTICS
print(f"\n" + "=" * 80)
print(f"📊 SUMMARY STATISTICS")
print(f"=" * 80)

# Get profit column name
if profit_col:
    df['NetProfit_numeric'] = pd.to_numeric(df[profit_col], errors='coerce').fillna(0)
elif 'NetProfit' in df.columns:
    df['NetProfit_numeric'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
else:
    df['NetProfit_numeric'] = 0

total_rows = len(df)
rows_with_sales = (df['sales'] > 0).sum()
rows_profitable = (df['NetProfit_numeric'] > 0).sum()
rows_pack_profitable = (df['Adjusted_Profit'] > 0).sum()
rows_sellable_profitable = ((df['sales'] > 0) & (df['NetProfit_numeric'] > 0) & (df['Adjusted_Profit'] > 0)).sum()

print(f"Total rows: {total_rows}")
print(f"Rows with Sales > 0: {rows_with_sales}")
print(f"Rows with NetProfit > 0: {rows_profitable}")
print(f"Rows with Adjusted_Profit > 0: {rows_pack_profitable}")
print(f"Rows meeting ALL criteria (sellable + profitable + pack-profitable): {rows_sellable_profitable}")

# Filter for recommendation candidates
df_recommend = df[(df['sales'] > 0) & (df['NetProfit_numeric'] > 0) & (df['Adjusted_Profit'] > 0)].copy()
print(f"\n✅ RECOMMENDATION CANDIDATES: {len(df_recommend)}")

# Save full analysis CSV
output_csv = OUTPUT_DIR / f"deep_analysis_{DATE_STAMP}.csv"
df.to_csv(output_csv, index=False)
print(f"\n💾 Full analysis saved to: {output_csv}")

# Print detailed breakdown for manual review
print(f"\n" + "=" * 80)
print(f"🔍 DETAILED BREAKDOWN FOR MANUAL REVIEW")
print(f"=" * 80)

# EXACT EAN MATCHES (for VERIFIED section)
exact_ean_df = df_recommend[df_recommend['is_exact_ean'] == True].sort_values('sales', ascending=False)
print(f"\n📌 VERIFIED (Exact EAN) - Recommended: {len(exact_ean_df)}")
if len(exact_ean_df) > 0:
    print(exact_ean_df.head(20).to_string())

# HIGH LIKELIHOOD
high_likelihood_df = df_recommend[df_recommend['category'] == 'HIGH_LIKELIHOOD'].sort_values('sales', ascending=False)
print(f"\n📌 HIGH LIKELIHOOD - Recommended: {len(high_likelihood_df)}")
if len(high_likelihood_df) > 0:
    print(high_likelihood_df.head(20).to_string())

# MODERATE CONFIDENCE  
moderate_df = df_recommend[df_recommend['category'] == 'MODERATE_CONFIDENCE'].sort_values('sales', ascending=False)
print(f"\n📌 MODERATE CONFIDENCE - Recommended: {len(moderate_df)}")

# FILTERED OUT - Exact EAN but excluded
exact_ean_filtered = df[(df['is_exact_ean'] == True) & ~((df['sales'] > 0) & (df['NetProfit_numeric'] > 0) & (df['Adjusted_Profit'] > 0))]
print(f"\n❌ VERIFIED (Exact EAN) - FILTERED OUT: {len(exact_ean_filtered)}")

# FILTERED OUT - High Likelihood but excluded
high_likelihood_filtered = df[(df['category'] == 'HIGH_LIKELIHOOD') & ~((df['sales'] > 0) & (df['NetProfit_numeric'] > 0) & (df['Adjusted_Profit'] > 0))]
print(f"❌ HIGH LIKELIHOOD - FILTERED OUT: {len(high_likelihood_filtered)}")

print(f"\n" + "=" * 80)
print(f"ANALYSIS COMPLETE")
print(f"=" * 80)
