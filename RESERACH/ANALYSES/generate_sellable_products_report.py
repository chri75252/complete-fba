"""
SELLABLE PRODUCTS REPORT GENERATOR
===================================
Generates a clean, actionable list of products that are:
- Profitable (NetProfit > 0)
- Sellable (Sales > 0)
- Segregated by EAN match confidence
"""

import pandas as pd
import re
from datetime import datetime
from difflib import SequenceMatcher

# Configuration
CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251211_203547.csv"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH"

print("=" * 80)
print("📦 SELLABLE PRODUCTS REPORT GENERATOR")
print("=" * 80)

# Load data
print("\n📂 Loading data...")
df = pd.read_csv(CSV_PATH)
print(f"   Total products: {len(df)}")

# Clean EAN columns
def clean_ean(val):
    if pd.isna(val):
        return ''
    s = str(val).strip()
    s = re.sub(r'\.0$', '', s)  # Remove trailing .0
    if s.lower() in ['nan', 'none', '', '-']:
        return ''
    return s

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# Get sales column
sales_col = None
for col in ['bought_in_past_month', 'sales', 'monthly_sales']:
    if col in df.columns:
        sales_col = col
        break

if sales_col:
    df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0).astype(int)
else:
    df['sales'] = 0

# Title similarity function
def title_similarity(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio()

df['TitleMatch'] = df.apply(lambda x: title_similarity(x.get('SupplierTitle', ''), x.get('AmazonTitle', '')), axis=1)

# Define match categories
def categorize_match(row):
    ean_supplier = row['EAN_clean']
    ean_amazon = row['EAN_OnPage_clean']
    title_match = row['TitleMatch']
    
    # Exact EAN Match - both present AND identical
    if ean_supplier and ean_amazon and ean_supplier == ean_amazon:
        return 'EXACT_EAN_MATCH'
    
    # High Likelihood - Title >= 50%
    if title_match >= 0.50:
        return 'HIGH_LIKELIHOOD'
    
    # Moderate Confidence - Title 30-50%
    if title_match >= 0.30:
        return 'MODERATE_CONFIDENCE'
    
    return 'LOW_CONFIDENCE'

df['MatchCategory'] = df.apply(categorize_match, axis=1)

# STRICT FILTERS: Sales > 0 AND NetProfit > 0
print("\n🔍 Applying strict filters: Sales > 0 AND NetProfit > 0...")
sellable = df[(df['sales'] > 0) & (df['NetProfit'] > 0)].copy()
print(f"   Sellable products found: {len(sellable)}")

# Categorize
exact_matches = sellable[sellable['MatchCategory'] == 'EXACT_EAN_MATCH'].sort_values('sales', ascending=False)
high_likelihood = sellable[sellable['MatchCategory'] == 'HIGH_LIKELIHOOD'].sort_values('sales', ascending=False)
moderate = sellable[sellable['MatchCategory'] == 'MODERATE_CONFIDENCE'].sort_values('sales', ascending=False)
low = sellable[sellable['MatchCategory'] == 'LOW_CONFIDENCE'].sort_values('sales', ascending=False)

print(f"\n📊 RESULTS:")
print(f"   🟢 EXACT EAN MATCHES: {len(exact_matches)}")
print(f"   🟡 HIGH LIKELIHOOD (Title ≥50%): {len(high_likelihood)}")
print(f"   🟠 MODERATE CONFIDENCE (Title 30-50%): {len(moderate)}")
print(f"   ⚪ LOW CONFIDENCE (Title <30%): {len(low)}")

# Generate Report
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
report = []
report.append("# 📦 SELLABLE PRODUCTS REPORT\n")
report.append(f"**Generated:** {timestamp}")
report.append(f"**Source:** `fba_financial_report_20251211_203547.csv`")
report.append(f"**Filters Applied:** Sales > 0 AND NetProfit > 0\n")
report.append("---\n")

# Summary
report.append("## 📊 SUMMARY\n")
report.append("| Category | Count | Criteria |")
report.append("|:---------|------:|:---------|")
report.append(f"| 🟢 **EXACT EAN MATCHES** | **{len(exact_matches)}** | Supplier EAN = Amazon EAN (both present) |")
report.append(f"| 🟡 HIGH LIKELIHOOD | {len(high_likelihood)} | Title similarity ≥ 50% |")
report.append(f"| 🟠 MODERATE CONFIDENCE | {len(moderate)} | Title similarity 30-50% |")
report.append(f"| ⚪ LOW CONFIDENCE | {len(low)} | Title similarity < 30% |")
report.append(f"| **TOTAL SELLABLE** | **{len(sellable)}** | All with Sales > 0, NetProfit > 0 |\n")
report.append("---\n")

# Function to generate product table
def generate_table(products, max_rows=None, show_ean=True):
    lines = []
    if show_ean:
        lines.append("| # | Supplier Title | Amazon Title | Supplier EAN | Amazon EAN | ASIN | Title% | Sales | Profit | ROI |")
        lines.append("|:-:|:---------------|:-------------|:-------------|:-----------|:-----|:------:|------:|-------:|----:|")
    else:
        lines.append("| # | Supplier Title | Amazon Title | ASIN | Title% | Sales | Profit | ROI |")
        lines.append("|:-:|:---------------|:-------------|:-----|:------:|------:|-------:|----:|")
    
    displayed = products if max_rows is None else products.head(max_rows)
    
    for i, (_, row) in enumerate(displayed.iterrows(), 1):
        sup_title = str(row.get('SupplierTitle', ''))[:50] + ('...' if len(str(row.get('SupplierTitle', ''))) > 50 else '')
        amz_title = str(row.get('AmazonTitle', ''))[:50] + ('...' if len(str(row.get('AmazonTitle', ''))) > 50 else '')
        title_pct = f"{row['TitleMatch']*100:.0f}%"
        profit = f"£{row['NetProfit']:.2f}"
        roi = f"{row.get('ROI', 0)*100:.0f}%" if pd.notna(row.get('ROI')) else '-'
        sales = int(row['sales'])
        asin = row.get('ASIN', '-')
        
        if show_ean:
            ean_s = row['EAN_clean'] if row['EAN_clean'] else '-'
            ean_a = row['EAN_OnPage_clean'] if row['EAN_OnPage_clean'] else '-'
            lines.append(f"| {i} | {sup_title} | {amz_title} | {ean_s} | {ean_a} | {asin} | {title_pct} | {sales} | {profit} | {roi} |")
        else:
            lines.append(f"| {i} | {sup_title} | {amz_title} | {asin} | {title_pct} | {sales} | {profit} | {roi} |")
    
    return lines

# SECTION 1: EXACT EAN MATCHES
report.append("## 🟢 TIER 1: EXACT EAN MATCHES (HIGHEST CONFIDENCE)\n")
report.append("**These are your SAFEST BUYS** - the barcode on the supplier product matches the Amazon listing exactly.\n")
if len(exact_matches) > 0:
    report.extend(generate_table(exact_matches, max_rows=50))
    if len(exact_matches) > 50:
        report.append(f"\n*...and {len(exact_matches) - 50} more exact matches*\n")
    
    # Summary stats
    total_profit = exact_matches['NetProfit'].sum()
    avg_profit = exact_matches['NetProfit'].mean()
    report.append(f"\n**💰 Total Potential Profit:** £{total_profit:.2f}")
    report.append(f"**📈 Average Profit/Product:** £{avg_profit:.2f}\n")
else:
    report.append("*No exact EAN matches found with sales > 0*\n")
report.append("---\n")

# SECTION 2: HIGH LIKELIHOOD
report.append("## 🟡 TIER 2: HIGH LIKELIHOOD MATCHES (Title ≥ 50%)\n")
report.append("**⚠️ Verify before ordering** - titles match well but EANs don't confirm 100%.\n")
if len(high_likelihood) > 0:
    report.extend(generate_table(high_likelihood, max_rows=30, show_ean=True))
    if len(high_likelihood) > 30:
        report.append(f"\n*...and {len(high_likelihood) - 30} more high likelihood matches*\n")
    
    total_profit = high_likelihood['NetProfit'].sum()
    report.append(f"\n**💰 Total Potential Profit (if verified):** £{total_profit:.2f}\n")
else:
    report.append("*No high likelihood matches found*\n")
report.append("---\n")

# SECTION 3: MODERATE CONFIDENCE  
report.append("## 🟠 TIER 3: MODERATE CONFIDENCE (Title 30-50%)\n")
report.append("**⚠️ Manual verification REQUIRED** - lower title match, higher risk of mismatch.\n")
if len(moderate) > 0:
    # Only show top 20 for moderate
    report.extend(generate_table(moderate, max_rows=20, show_ean=False))
    if len(moderate) > 20:
        report.append(f"\n*...and {len(moderate) - 20} more moderate confidence matches*\n")
else:
    report.append("*No moderate confidence matches found*\n")
report.append("---\n")

# TOP 10 BY SALES (regardless of category)
report.append("## 🏆 TOP 10 SELLABLE PRODUCTS BY SALES VOLUME\n")
top10 = sellable.nlargest(10, 'sales')
report.append("| Rank | Supplier Title | ASIN | Sales | Profit | Match Type |")
report.append("|:----:|:---------------|:-----|------:|-------:|:-----------|")
for i, (_, row) in enumerate(top10.iterrows(), 1):
    title = str(row.get('SupplierTitle', ''))[:45] + ('...' if len(str(row.get('SupplierTitle', ''))) > 45 else '')
    match_icon = {"EXACT_EAN_MATCH": "🟢 Exact EAN", "HIGH_LIKELIHOOD": "🟡 High", "MODERATE_CONFIDENCE": "🟠 Moderate", "LOW_CONFIDENCE": "⚪ Low"}
    report.append(f"| {i} | {title} | {row.get('ASIN', '-')} | {int(row['sales'])} | £{row['NetProfit']:.2f} | {match_icon.get(row['MatchCategory'], row['MatchCategory'])} |")

report.append("\n---\n")

# TOP 10 BY PROFIT
report.append("## 💰 TOP 10 SELLABLE PRODUCTS BY PROFIT\n")
top10_profit = sellable.nlargest(10, 'NetProfit')
report.append("| Rank | Supplier Title | ASIN | Sales | Profit | ROI | Match Type |")
report.append("|:----:|:---------------|:-----|------:|-------:|----:|:-----------|")
for i, (_, row) in enumerate(top10_profit.iterrows(), 1):
    title = str(row.get('SupplierTitle', ''))[:40] + ('...' if len(str(row.get('SupplierTitle', ''))) > 40 else '')
    roi = f"{row.get('ROI', 0)*100:.0f}%" if pd.notna(row.get('ROI')) else '-'
    match_icon = {"EXACT_EAN_MATCH": "🟢 Exact EAN", "HIGH_LIKELIHOOD": "🟡 High", "MODERATE_CONFIDENCE": "🟠 Moderate", "LOW_CONFIDENCE": "⚪ Low"}
    report.append(f"| {i} | {title} | {row.get('ASIN', '-')} | {int(row['sales'])} | £{row['NetProfit']:.2f} | {roi} | {match_icon.get(row['MatchCategory'], row['MatchCategory'])} |")

report.append("\n---\n")

# Action Plan
report.append("## 🚀 ACTION PLAN\n")
report.append("1. **IMMEDIATE ORDER** → 🟢 TIER 1 (Exact EAN Matches) - These are verified, order with confidence")
report.append("2. **TEST ORDER (5-10 units)** → 🟡 TIER 2 - Verify product matches before scaling")
report.append("3. **MANUAL CHECK FIRST** → 🟠 TIER 3 - Compare actual product images before ordering")
report.append("4. **AVOID** → ⚪ Low confidence unless manually verified\n")

report.append("---\n")
report.append(f"*Report generated: {timestamp}*\n")

# Write report
report_path = f"{OUTPUT_DIR}/SELLABLE_PRODUCTS_REPORT_20251212.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print(f"\n✅ Report saved to: {report_path}")

# Also save CSV of all sellable products
csv_path = f"{OUTPUT_DIR}/sellable_products_20251212.csv"
export_cols = ['SupplierTitle', 'AmazonTitle', 'EAN_clean', 'EAN_OnPage_clean', 'ASIN', 
               'SupplierPrice_incVAT', 'SellingPrice_incVAT', 'NetProfit', 'ROI', 
               'sales', 'TitleMatch', 'MatchCategory']
existing_cols = [c for c in export_cols if c in sellable.columns]
sellable[existing_cols].to_csv(csv_path, index=False)
print(f"✅ CSV saved to: {csv_path}")

print("\n" + "=" * 80)
print("📦 SELLABLE PRODUCTS SUMMARY")
print("=" * 80)
print(f"   🟢 EXACT EAN MATCHES: {len(exact_matches)} products (SAFEST)")
print(f"   🟡 HIGH LIKELIHOOD:   {len(high_likelihood)} products (verify first)")
print(f"   🟠 MODERATE:          {len(moderate)} products (manual check)")
print(f"   ⚪ LOW CONFIDENCE:    {len(low)} products (risky)")
print(f"   ─────────────────────────────────────")
print(f"   📦 TOTAL SELLABLE:    {len(sellable)} products")
print("=" * 80)
