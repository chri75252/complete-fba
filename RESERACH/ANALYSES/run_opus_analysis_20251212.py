"""
FBA Product Analysis Pipeline V2 - Opus 20251212 Final Report
Executes all 5 analysis stages with STRICT EAN verification
"""

import pandas as pd
import re
from difflib import SequenceMatcher
from datetime import datetime

# Configuration
INPUT_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\angelwholesale-co-uk\fba_financial_report_20251211_203547.csv"
OUTPUT_DIR = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH"

print("=" * 80)
print("🔍 FBA PRODUCT ANALYSIS PIPELINE V2 - OPUS 20251212")
print("=" * 80)

# ============================================================================
# STAGE 1: Data Loading & Initial Cleaning
# ============================================================================
print("\n📂 STAGE 1: Loading and Cleaning Data...")

df = pd.read_csv(INPUT_PATH)
print(f"   Loaded {len(df)} total products")

# Clean EAN columns - CRITICAL for accurate matching
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Handle sales column
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    # Extract numeric from text like "100" or "1K+" 
    def parse_sales(val):
        if pd.isna(val):
            return 0
        val_str = str(val).strip()
        if val_str == '' or val_str.lower() == 'nan':
            return 0
        # Replace K with 000
        val_str = val_str.upper().replace('K+', '000').replace('K', '000')
        val_str = re.sub(r'[^\d.]', '', val_str)
        try:
            return float(val_str)
        except:
            return 0
    df['sales'] = df['bought_in_past_month'].apply(parse_sales)
else:
    df['sales'] = 0

# Ensure numeric columns
df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
df['ROI'] = pd.to_numeric(df['ROI'], errors='coerce').fillna(0)
df['SupplierPrice_incVAT'] = pd.to_numeric(df['SupplierPrice_incVAT'], errors='coerce').fillna(0)
df['SellingPrice_incVAT'] = pd.to_numeric(df['SellingPrice_incVAT'], errors='coerce').fillna(0)

print(f"   Products with sales > 0: {len(df[df['sales'] > 0])}")
print(f"   Products with NetProfit > 0: {len(df[df['NetProfit'] > 0])}")

# ============================================================================
# STAGE 2: Title Similarity Calculation
# ============================================================================
print("\n📝 STAGE 2: Calculating Title Similarity...")

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_match'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)
print(f"   Average title match: {df['title_match'].mean():.2%}")

# ============================================================================
# STAGE 3: STRICT EAN Matching (CRITICAL)
# ============================================================================
print("\n🔐 STAGE 3: STRICT EAN Matching...")

def is_valid_ean(ean):
    """Check if EAN is a valid barcode (not empty, nan, None, etc.)"""
    if pd.isna(ean):
        return False
    ean_str = str(ean).strip()
    return ean_str not in ['nan', '', 'None', 'NaN', '0', '-', 'N/A', 'n/a']

def is_exact_ean_match(row):
    """Returns True ONLY if BOTH EANs are valid AND they match exactly"""
    ean_sup = str(row['EAN']).strip()
    ean_amz = str(row['EAN_OnPage']).strip()
    
    # Both must be valid
    if not is_valid_ean(ean_sup) or not is_valid_ean(ean_amz):
        return False
    
    # Must match exactly
    return ean_sup == ean_amz

df['is_exact_ean'] = df.apply(is_exact_ean_match, axis=1)
exact_ean_count = df['is_exact_ean'].sum()
print(f"   ✅ Exact EAN matches (BOTH present AND matching): {exact_ean_count}")

# ============================================================================
# STAGE 4: Pack Size Extraction & Profit Recalculation
# ============================================================================
print("\n📦 STAGE 4: Pack Size Analysis & Profit Recalculation...")

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
    ]
    
    for pat in patterns:
        match = re.search(pat, title)
        if match:
            qty = float(match.group(1))
            if qty > 1 and qty < 500:  # Sanity check
                return qty
    return 1.0

df['Sup_Qty'] = df['SupplierTitle'].apply(extract_quantity)
df['Amz_Qty'] = df['AmazonTitle'].apply(extract_quantity)
df['Qty_Ratio'] = df['Amz_Qty'] / df['Sup_Qty'].replace(0, 1)

def recalculate_profit(row):
    """
    Adjust profit based on quantity ratio.
    If Amazon sells a 6-pack and Supplier sells singles,
    we need to buy 6 units, so: Adjusted_Profit = Original - (Cost * (Ratio - 1))
    """
    try:
        original_profit = float(row['NetProfit'])
        supplier_cost = float(row['SupplierPrice_incVAT'])
        ratio = row['Qty_Ratio']
        adjustment = supplier_cost * (ratio - 1)
        return original_profit - adjustment
    except:
        return 0.0

df['Adjusted_Profit'] = df.apply(recalculate_profit, axis=1)

# Count pack adjustments
bundle_count = len(df[df['Qty_Ratio'] > 1])
split_count = len(df[df['Qty_Ratio'] < 1])
print(f"   Products requiring bundling (Qty Ratio > 1): {bundle_count}")
print(f"   Products with split opportunity (Qty Ratio < 1): {split_count}")

# ============================================================================
# STAGE 5: Product Categorization
# ============================================================================
print("\n🏷️ STAGE 5: Categorizing Products...")

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
for cat in ['EXACT_EAN_MATCH', 'HIGH_LIKELIHOOD', 'MODERATE_CONFIDENCE', 'UNCERTAIN']:
    count = len(df[df['category'] == cat])
    print(f"   {cat}: {count}")

# ============================================================================
# FILTER FOR REPORT
# ============================================================================
print("\n📊 Preparing Report Data...")

# Filter profitable products
profitable = df[df['NetProfit'] > 0].copy()
print(f"   Profitable products: {len(profitable)}")

# GROUP 1: EXACT EAN MATCHES - HIGHEST CONFIDENCE
# STRICT: Both EANs present AND matching, NetProfit > 0
group1 = profitable[(profitable['is_exact_ean'] == True)].copy()
group1 = group1.sort_values('sales', ascending=False)
print(f"   🟢 GROUP 1 (Exact EAN Match): {len(group1)}")

# GROUP 2: HIGH LIKELIHOOD - Sales > 0, Title match >= 50%, NOT exact EAN
group2 = profitable[
    (profitable['is_exact_ean'] == False) &
    (profitable['title_match'] >= 0.50) &
    (profitable['sales'] > 0)
].copy()
group2 = group2.sort_values('sales', ascending=False)
print(f"   🟡 GROUP 2 (High Likelihood): {len(group2)}")

# GROUP 3: MODERATE CONFIDENCE - Sales > 0, Title match 30-50%
group3 = profitable[
    (profitable['is_exact_ean'] == False) &
    (profitable['title_match'] >= 0.30) &
    (profitable['title_match'] < 0.50) &
    (profitable['sales'] > 0)
].copy()
group3 = group3.sort_values('sales', ascending=False)
print(f"   🟠 GROUP 3 (Moderate Confidence): {len(group3)}")

# GROUP 4: SPLIT OPPORTUNITIES - Supplier multipack -> Amazon single, Profitable
group4 = profitable[
    (profitable['Qty_Ratio'] < 1) &
    (profitable['Adjusted_Profit'] > 0) &
    (profitable['sales'] > 0)
].copy()
group4 = group4.sort_values('sales', ascending=False)
print(f"   🔵 GROUP 4 (Split Opportunities): {len(group4)}")

# FALSE MATCHES - Products that became losses after pack adjustment
false_matches = df[
    (df['NetProfit'] > 0) &  # Originally profitable
    (df['Adjusted_Profit'] <= 0)  # Loss after adjustment
].copy()
print(f"   🔴 FALSE MATCHES (Loss after adjustment): {len(false_matches)}")

# ============================================================================
# GENERATE CSV OUTPUT
# ============================================================================
print("\n💾 Saving CSV Output...")

output_cols = [
    'category', 'is_exact_ean', 'Pack_Verdict',
    'Adjusted_Profit', 'NetProfit', 'ROI',
    'Qty_Ratio', 'Sup_Qty', 'Amz_Qty',
    'title_match', 'sales',
    'SupplierTitle', 'AmazonTitle',
    'EAN', 'EAN_OnPage',
    'ASIN', 'SupplierPrice_incVAT', 'SellingPrice_incVAT',
    'SupplierURL', 'AmazonURL'
]

csv_path = f"{OUTPUT_DIR}\\deep_analysis_opus_20251212.csv"
df[output_cols].to_csv(csv_path, index=False)
print(f"   Saved: {csv_path}")

# ============================================================================
# GENERATE MARKDOWN REPORT
# ============================================================================
print("\n📝 Generating Markdown Report...")

report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
report_lines = []

report_lines.append("# 🔍 OPUS 20251212 LATEST FINAL REPORT - Angel Wholesale")
report_lines.append("")
report_lines.append(f"**Generated:** {report_date}")
report_lines.append(f"**Source:** `fba_financial_report_20251211_203547.csv`")
report_lines.append(f"**Total Products Analyzed:** {len(df)}")
report_lines.append(f"**Profitable Products (NetProfit > 0):** {len(profitable)}")
report_lines.append(f"**Products With Sales Data (>0):** {len(df[df['sales'] > 0])}")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("## 📊 SUMMARY")
report_lines.append("")
report_lines.append("| Group | Count | Description |")
report_lines.append("|:------|:-----:|:------------|")
report_lines.append(f"| 🟢 GROUP 1: EXACT EAN MATCH | {len(group1)} | Both Supplier AND Amazon EANs present AND matching |")
report_lines.append(f"| 🟡 GROUP 2: HIGH LIKELIHOOD | {len(group2)} | Title match >=50%, Sales >0, EANs don't match |")
report_lines.append(f"| 🟠 GROUP 3: MODERATE CONFIDENCE | {len(group3)} | Title match 30-50%, Sales >0 |")
report_lines.append(f"| 🔵 GROUP 4: SPLIT OPPORTUNITIES | {len(group4)} | Supplier multipack -> Amazon single, Profitable |")
report_lines.append(f"| 🔴 FALSE MATCHES | {len(false_matches)} | Loss makers after pack adjustment (dropped) |")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# Helper function to create markdown table
def create_table(data, max_rows=50):
    if len(data) == 0:
        return ["*No products in this category.*", ""]
    
    lines = []
    lines.append("| SupplierTitle | AmazonTitle | Supplier EAN | Amazon EAN | ASIN | Title Match | Sales | Net Profit | ROI |")
    lines.append("|:--------------|:------------|:-------------|:-----------|:-----|:-----------:|------:|-----------:|----:|")
    
    for idx, row in data.head(max_rows).iterrows():
        sup_title = str(row['SupplierTitle'])[:50] + "..." if len(str(row['SupplierTitle'])) > 50 else str(row['SupplierTitle'])
        amz_title = str(row['AmazonTitle'])[:50] + "..." if len(str(row['AmazonTitle'])) > 50 else str(row['AmazonTitle'])
        ean_sup = str(row['EAN']) if is_valid_ean(row['EAN']) else "-"
        ean_amz = str(row['EAN_OnPage']) if is_valid_ean(row['EAN_OnPage']) else "-"
        asin = str(row['ASIN'])
        title_pct = f"{row['title_match']:.0%}"
        sales = int(row['sales'])
        profit = f"£{row['NetProfit']:.2f}"
        roi = f"{row['ROI']:.0f}%"
        
        lines.append(f"| {sup_title} | {amz_title} | {ean_sup} | {ean_amz} | {asin} | {title_pct} | {sales} | {profit} | {roi} |")
    
    if len(data) > max_rows:
        lines.append("")
        lines.append(f"*...and {len(data) - max_rows} more products*")
    
    lines.append("")
    return lines

# GROUP 1
report_lines.append("## 🟢 GROUP 1: EXACT EAN MATCHES (Highest Confidence)")
report_lines.append("")
report_lines.append("**Criteria:** Supplier EAN = Amazon EAN (BOTH must be present and valid), NetProfit > 0")
report_lines.append("")
report_lines.extend(create_table(group1, max_rows=50))
report_lines.append("**✅ These are your SAFEST buys - VERIFIED EAN matches. Order with confidence.**")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# GROUP 2
report_lines.append("## 🟡 GROUP 2: HIGH LIKELIHOOD MATCHES (Title Match >= 50%)")
report_lines.append("")
report_lines.append("**Criteria:** Sales > 0, Title similarity >= 50%, EANs do NOT match or are missing, NetProfit > 0")
report_lines.append("")
report_lines.extend(create_table(group2, max_rows=30))
report_lines.append("**⚠️ EANs don't match - verify manually before large orders. Start with test quantities.**")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# GROUP 3
report_lines.append("## 🟠 GROUP 3: MODERATE CONFIDENCE (Title Match 30-50%)")
report_lines.append("")
report_lines.append("**Criteria:** Sales > 0, Title match 30-50%, NetProfit > 0")
report_lines.append("")
report_lines.extend(create_table(group3, max_rows=20))
report_lines.append("**⚠️ Lower confidence - manual verification required before ordering.**")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# GROUP 4
report_lines.append("## 🔵 GROUP 4: SPLIT OPPORTUNITIES")
report_lines.append("")
report_lines.append("**Criteria:** Supplier sells multipack, Amazon sells singles, Profitable if split, Sales > 0")
report_lines.append("")
report_lines.extend(create_table(group4, max_rows=20))
report_lines.append("**💡 These require splitting supplier packs - check inner packaging has barcodes.**")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# FALSE MATCHES
report_lines.append("## 🔴 FALSE MATCHES / LOSS MAKERS (Do Not Buy)")
report_lines.append("")
report_lines.append("**These products looked profitable but became LOSSES after pack size adjustment:**")
report_lines.append("")
if len(false_matches) > 0:
    report_lines.append("| SupplierTitle | AmazonTitle | Pack Issue | Original Profit | Adjusted Profit |")
    report_lines.append("|:--------------|:------------|:-----------|----------------:|----------------:|")
    for idx, row in false_matches.head(15).iterrows():
        sup_title = str(row['SupplierTitle'])[:40] + "..." if len(str(row['SupplierTitle'])) > 40 else str(row['SupplierTitle'])
        amz_title = str(row['AmazonTitle'])[:40] + "..." if len(str(row['AmazonTitle'])) > 40 else str(row['AmazonTitle'])
        pack_issue = f"Sup: {int(row['Sup_Qty'])} vs Amz: {int(row['Amz_Qty'])}"
        orig = f"£{row['NetProfit']:.2f}"
        adj = f"£{row['Adjusted_Profit']:.2f}"
        report_lines.append(f"| {sup_title} | {amz_title} | {pack_issue} | {orig} | {adj} |")
    if len(false_matches) > 15:
        report_lines.append("")
        report_lines.append(f"*...and {len(false_matches) - 15} more false matches*")
else:
    report_lines.append("*No products became losses after pack adjustment.*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# WARNINGS
report_lines.append("## ⚠️ CRITICAL WARNINGS")
report_lines.append("")
report_lines.append("1. **GROUP 1 is SAFEST:** Only products with BOTH EANs matching are included.")
report_lines.append("2. **GROUP 2 needs verification:** Title match is good but EANs differ - could be same product, different variant.")
report_lines.append("3. **IP RISK:** Watch for luxury brand \"smell-alikes\" (Jo Malone, Chanel, etc.) - HIGH IP RISK.")
report_lines.append("4. **Always verify pack sizes:** Check supplier AND Amazon listing images before ordering.")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# ACTION PLAN
report_lines.append("## 🚀 ACTION PLAN")
report_lines.append("")
report_lines.append("1. **Immediate Order:** GROUP 1 - VERIFIED EAN matches with proven sales.")
report_lines.append("2. **Test Orders:** GROUP 2 - Order small quantities (5-10 units), verify manually.")
report_lines.append("3. **Manual Check:** GROUP 3 - Carefully verify title/product matches.")
report_lines.append("4. **Split Prep:** GROUP 4 - Verify inner packaging before splitting.")
report_lines.append("5. **Avoid:** All items in FALSE MATCHES section.")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# TOP PICKS
report_lines.append("## 🏆 TOP 10 RECOMMENDATIONS BY SALES")
report_lines.append("")
top_picks = profitable[profitable['sales'] > 0].sort_values('sales', ascending=False).head(10)
if len(top_picks) > 0:
    report_lines.append("| Rank | SupplierTitle | ASIN | Sales | Net Profit | Category | EAN Match? |")
    report_lines.append("|:----:|:--------------|:-----|------:|-----------:|:---------|:-----------|")
    for i, (idx, row) in enumerate(top_picks.iterrows(), 1):
        sup_title = str(row['SupplierTitle'])[:50] + "..." if len(str(row['SupplierTitle'])) > 50 else str(row['SupplierTitle'])
        ean_status = "✅ YES" if row['is_exact_ean'] else "❌ NO"
        report_lines.append(f"| {i} | {sup_title} | {row['ASIN']} | {int(row['sales'])} | £{row['NetProfit']:.2f} | {row['category']} | {ean_status} |")
report_lines.append("")
report_lines.append("---")
report_lines.append("")

# TOTAL PROFIT POTENTIAL
total_group1_profit = group1['NetProfit'].sum()
total_group2_profit = group2['NetProfit'].sum()
report_lines.append("## 💰 PROFIT POTENTIAL SUMMARY")
report_lines.append("")
report_lines.append(f"- **GROUP 1 (Verified EAN Matches):** £{total_group1_profit:.2f} potential profit")
report_lines.append(f"- **GROUP 2 (High Likelihood):** £{total_group2_profit:.2f} potential profit *(requires verification)*")
report_lines.append("")
report_lines.append("---")
report_lines.append("")
report_lines.append("*Report generated using FBA Deep Analysis Pipeline v2.0 - Opus 20251212*")
report_lines.append(f"*Analysis Date: {report_date}*")

# Write report
report_path = f"{OUTPUT_DIR}\\opus_20251212_LATEST_FINAL_REPORT.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report_lines))
print(f"   Saved: {report_path}")

print("\n" + "=" * 80)
print("✅ ANALYSIS COMPLETE!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   - Total products analyzed: {len(df)}")
print(f"   - 🟢 GROUP 1 (Exact EAN Match): {len(group1)}")
print(f"   - 🟡 GROUP 2 (High Likelihood): {len(group2)}")
print(f"   - 🟠 GROUP 3 (Moderate Confidence): {len(group3)}")
print(f"   - 🔵 GROUP 4 (Split Opportunities): {len(group4)}")
print(f"   - 🔴 FALSE MATCHES: {len(false_matches)}")
print(f"\n📁 Output files:")
print(f"   - {csv_path}")
print(f"   - {report_path}")
