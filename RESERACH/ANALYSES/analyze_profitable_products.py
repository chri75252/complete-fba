"""
Analyze FBA Financial Report for Profitable Products
Priority order:
1. Products with sales
2. Matching EAN
3. High chance of title match
4. Net Profit > 0
"""

import pandas as pd
import re
from difflib import SequenceMatcher

# Load the CSV
csv_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251205_183550.csv"
df = pd.read_csv(csv_path)

# Filter for Net Profit > 0
profitable = df[df['NetProfit'] > 0].copy()

# Parse bought_in_past_month - convert to numeric
def parse_sales(x):
    if pd.isna(x) or x == '':
        return 0
    if isinstance(x, (int, float)):
        return float(x)
    x = str(x).strip()
    match = re.search(r'(\d+)', x)
    if match:
        return float(match.group(1))
    return 0

profitable['sales_numeric'] = profitable['bought_in_past_month'].apply(parse_sales)

# Check EAN match
def check_ean_match(row):
    ean = str(row['EAN']).strip() if pd.notna(row['EAN']) else ''
    ean_on_page = str(row['EAN_OnPage']).strip() if pd.notna(row['EAN_OnPage']) else ''
    # Remove any floats that got converted to strings with .0
    ean = ean.replace('.0', '') if ean.endswith('.0') else ean
    ean_on_page = ean_on_page.replace('.0', '') if ean_on_page.endswith('.0') else ean_on_page
    
    if ean and ean_on_page and ean == ean_on_page:
        return 'EXACT_MATCH'
    if ean or ean_on_page:
        return 'PARTIAL'
    return 'NONE'

profitable['ean_match_status'] = profitable.apply(check_ean_match, axis=1)

# Title similarity score
def title_similarity(row):
    supplier_title = str(row['SupplierTitle']).lower() if pd.notna(row['SupplierTitle']) else ''
    amazon_title = str(row['AmazonTitle']).lower() if pd.notna(row['AmazonTitle']) else ''
    
    if not supplier_title or not amazon_title:
        return 0.0
    
    # Get similarity ratio
    return SequenceMatcher(None, supplier_title, amazon_title).ratio()

profitable['title_match_score'] = profitable.apply(title_similarity, axis=1)

# Summary stats
print("=" * 80)
print("PROFITABLE PRODUCTS ANALYSIS - Angel Wholesale")
print("=" * 80)
print(f"\nTotal profitable products (NetProfit > 0): {len(profitable)}")
print(f"Products with confirmed sales > 0: {len(profitable[profitable['sales_numeric'] > 0])}")
print(f"Products with EXACT EAN match: {len(profitable[profitable['ean_match_status'] == 'EXACT_MATCH'])}")
print(f"Products with high title match (>0.5): {len(profitable[profitable['title_match_score'] > 0.5])}")

# Create priority scoring
def priority_score(row):
    score = 0
    # Sales weight (most important)
    if row['sales_numeric'] >= 500:
        score += 1000
    elif row['sales_numeric'] >= 200:
        score += 800
    elif row['sales_numeric'] >= 100:
        score += 600
    elif row['sales_numeric'] >= 50:
        score += 400
    elif row['sales_numeric'] > 0:
        score += 200
    
    # EAN match weight
    if row['ean_match_status'] == 'EXACT_MATCH':
        score += 150
    elif row['ean_match_status'] == 'PARTIAL':
        score += 50
    
    # Title match weight
    score += row['title_match_score'] * 100
    
    # Profit weight
    score += min(row['NetProfit'], 100)  # Cap at 100 to not overly weight high profits
    
    return score

profitable['priority_score'] = profitable.apply(priority_score, axis=1)

# Sort by priority
sorted_profitable = profitable.sort_values('priority_score', ascending=False)

# Display top products
print("\n" + "=" * 80)
print("TOP PRIORITY PRODUCTS (Sorted by: Sales > EAN Match > Title Match > Profit)")
print("=" * 80)

# Tier 1: Products with sales
with_sales = sorted_profitable[sorted_profitable['sales_numeric'] > 0].head(100)

print(f"\n### TIER 1: Products WITH Confirmed Sales ({len(with_sales)} total shown top 50)")
print("-" * 80)

cols_display = ['SupplierTitle', 'sales_numeric', 'NetProfit', 'ROI', 'ean_match_status', 'title_match_score', 'SupplierPrice_incVAT', 'SellingPrice_incVAT']

for idx, row in with_sales.head(50).iterrows():
    print(f"\n[{with_sales.head(50).index.get_loc(idx) + 1}] {row['SupplierTitle'][:60]}...")
    print(f"    Amazon: {str(row['AmazonTitle'])[:60]}...")
    print(f"    Sales/Month: {row['sales_numeric']:.0f} | Net Profit: £{row['NetProfit']:.2f} | ROI: {row['ROI']:.1f}%")
    print(f"    EAN Match: {row['ean_match_status']} | Title Match: {row['title_match_score']:.2f}")
    print(f"    Buy: £{row['SupplierPrice_incVAT']:.2f} | Sell: £{row['SellingPrice_incVAT']:.2f}")

# Tier 2: Exact EAN match but no sales data
exact_ean_no_sales = sorted_profitable[
    (sorted_profitable['ean_match_status'] == 'EXACT_MATCH') & 
    (sorted_profitable['sales_numeric'] == 0)
].head(20)

print(f"\n\n### TIER 2: EXACT EAN Match (No Sales Data) - {len(exact_ean_no_sales)} shown")
print("-" * 80)
for idx, row in exact_ean_no_sales.iterrows():
    print(f"\n* {row['SupplierTitle'][:60]}...")
    print(f"  Amazon: {str(row['AmazonTitle'])[:60]}...")
    print(f"  Net Profit: £{row['NetProfit']:.2f} | ROI: {row['ROI']:.1f}% | Title Match: {row['title_match_score']:.2f}")

# Tier 3: High title match
high_title_match = sorted_profitable[
    (sorted_profitable['title_match_score'] > 0.4) & 
    (sorted_profitable['sales_numeric'] == 0) &
    (sorted_profitable['ean_match_status'] != 'EXACT_MATCH')
].sort_values('title_match_score', ascending=False).head(20)

print(f"\n\n### TIER 3: High Title Match (>40% similarity) - {len(high_title_match)} shown")
print("-" * 80)
for idx, row in high_title_match.iterrows():
    print(f"\n* {row['SupplierTitle'][:60]}...")
    print(f"  Amazon: {str(row['AmazonTitle'])[:60]}...")
    print(f"  Net Profit: £{row['NetProfit']:.2f} | Title Match: {row['title_match_score']:.2f}")

print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total Profitable Products: {len(profitable)}")
print(f"Products with Sales: {len(profitable[profitable['sales_numeric'] > 0])}")
print(f"Exact EAN Matches: {len(profitable[profitable['ean_match_status'] == 'EXACT_MATCH'])}")

# Also save to CSV for easy review
output_file = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\profitable_products_prioritized.csv"
sorted_profitable.to_csv(output_file, index=False)
print(f"\nFull data saved to: {output_file}")
