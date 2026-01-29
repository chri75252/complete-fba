"""
Extract all potential matches from the CSV and categorize them:
1. EXACT EAN MATCHES - where supplier EAN = Amazon EAN
2. HIGH CONFIDENCE - high title match score OR verified by page visit
3. UNCERTAIN - need manual verification
"""

import pandas as pd
import re

# Load original data
df = pd.read_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251207_064703.csv")

# Clean EAN columns
df['EAN'] = df['EAN'].astype(str).str.strip().replace('nan', '')
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.strip().replace('nan', '')

# Filter profitable products only
profitable = df[df['NetProfit'] > 0].copy()

# Parse sales
def parse_sales(val):
    if pd.isna(val) or val == '' or val == 'nan':
        return 0
    val = str(val).replace('+', '').replace('K', '000').replace(',', '')
    try:
        return float(val)
    except:
        return 0

profitable['sales_numeric'] = profitable['bought_in_past_month'].apply(parse_sales)

# Identify EXACT EAN matches
profitable['is_exact_ean'] = profitable['EAN'] == profitable['EAN_OnPage']
profitable['is_exact_ean'] = profitable['is_exact_ean'] & (profitable['EAN'] != '') & (profitable['EAN'] != 'nan')

# Calculate title similarity
from difflib import SequenceMatcher

def title_similarity(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio()

profitable['title_match'] = profitable.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# Categorize
def categorize(row):
    if row['is_exact_ean']:
        return 'EXACT_EAN_MATCH'
    elif row['title_match'] >= 0.5:
        return 'HIGH_CONFIDENCE'
    elif row['title_match'] >= 0.3:
        return 'MODERATE_CONFIDENCE'
    else:
        return 'UNCERTAIN'

profitable['category'] = profitable.apply(categorize, axis=1)

# Sort by profitability and sales
profitable = profitable.sort_values(['sales_numeric', 'NetProfit'], ascending=[False, False])

# Filter for recommended products (must have sales OR high profit)
recommended = profitable[(profitable['sales_numeric'] > 0) | (profitable['NetProfit'] > 5)]

# Save to CSV
output_cols = ['category', 'EAN', 'EAN_OnPage', 'ASIN', 'SupplierTitle', 'AmazonTitle', 
               'title_match', 'sales_numeric', 'NetProfit', 'ROI', 
               'SupplierPrice_incVAT', 'SellingPrice_incVAT']
recommended[output_cols].to_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\categorized_products_20251207.csv", index=False)

# Print summary
print("="*80)
print("PRODUCT CATEGORIZATION SUMMARY")
print("="*80)
print(f"\nTotal profitable products: {len(profitable)}")
print(f"Products with sales data: {len(profitable[profitable['sales_numeric'] > 0])}")
print(f"\nRecommended products (sales > 0 OR profit > £5): {len(recommended)}")
print(f"\nBy category:")
print(recommended['category'].value_counts())

print("\n" + "="*80)
print("EXACT EAN MATCHES (100% confidence) - TOP 20")
print("="*80)
exact = recommended[recommended['category'] == 'EXACT_EAN_MATCH'].head(20)
for _, row in exact.iterrows():
    print(f"\nEAN: {row['EAN']} | ASIN: {row['ASIN']}")
    print(f"  Supplier: {str(row['SupplierTitle'])[:60]}")
    print(f"  Amazon:   {str(row['AmazonTitle'])[:60]}")
    print(f"  Sales: {row['sales_numeric']:.0f} | Profit: {row['NetProfit']:.2f} | ROI: {row['ROI']:.1f}%")

print("\n" + "="*80)
print("HIGH CONFIDENCE MATCHES (>50% title match) - TOP 20")
print("="*80)
high = recommended[recommended['category'] == 'HIGH_CONFIDENCE'].head(20)
for _, row in high.iterrows():
    print(f"\nTitle Match: {row['title_match']:.1%} | ASIN: {row['ASIN']}")
    print(f"  Supplier: {str(row['SupplierTitle'])[:60]}")
    print(f"  Amazon:   {str(row['AmazonTitle'])[:60]}")
    print(f"  Supplier EAN: {row['EAN']} | Amazon EAN: {row['EAN_OnPage']}")
    print(f"  Sales: {row['sales_numeric']:.0f} | Profit: {row['NetProfit']:.2f} | ROI: {row['ROI']:.1f}%")

print("\n\nFull data saved to: RESERACH\\categorized_products.csv")
