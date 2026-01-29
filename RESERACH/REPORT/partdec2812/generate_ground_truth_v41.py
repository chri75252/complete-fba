"""
GROUND TRUTH GENERATOR v4.1 - With proper data columns and sorted output
Generates the ground truth report with:
- Correct SellingPrice and Sales values from source
- Output sorted by confidence (highest to lowest)
- Proper table schema
"""

import pandas as pd
import re
from difflib import SequenceMatcher

# Load dataset
df = pd.read_excel('PARTDEC28_1.xlsx')
print(f"Loaded {len(df)} rows")

# Check what columns exist for SellingPrice and Sales
print("\nChecking source columns for SellingPrice:")
selling_cols = [c for c in df.columns if 'sell' in c.lower() or 'price' in c.lower()]
print(f"  Found: {selling_cols}")

print("\nChecking source columns for Sales:")
sales_cols = [c for c in df.columns if 'sale' in c.lower() or 'bought' in c.lower()]
print(f"  Found: {sales_cols}")

# Map SellingPrice correctly
if 'SellingPrice_incVAT' in df.columns:
    df['selling_price'] = pd.to_numeric(df['SellingPrice_incVAT'], errors='coerce').fillna(0)
elif 'SellingPrice' in df.columns:
    df['selling_price'] = pd.to_numeric(df['SellingPrice'], errors='coerce').fillna(0)
else:
    df['selling_price'] = 0
    print("WARNING: No SellingPrice column found!")

# Map Sales correctly
if 'sales_numeric' in df.columns:
    df['sales'] = pd.to_numeric(df['sales_numeric'], errors='coerce').fillna(0)
elif 'bought_in_past_month' in df.columns:
    df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
elif 'Sales' in df.columns:
    df['sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
else:
    df['sales'] = 0
    print("WARNING: No Sales column found!")

print(f"\nSelling Price sample (first 5): {df['selling_price'].head().tolist()}")
print(f"Sales sample (first 5): {df['sales'].head().tolist()}")

# === NORMALIZE EAN ===
def normalize_ean(ean):
    if pd.isna(ean):
        return None
    ean_str = str(ean).strip()
    ean_str = re.sub(r'[^0-9]', '', ean_str)
    return ean_str if ean_str else None

df['EAN_norm'] = df['EAN'].apply(normalize_ean)
df['EAN_OnPage_norm'] = df['EAN_OnPage'].apply(normalize_ean)

exact_ean_mask = (df['EAN_norm'].notna()) & (df['EAN_OnPage_norm'].notna()) & (df['EAN_norm'] == df['EAN_OnPage_norm'])
print(f"\nExact EAN matches: {exact_ean_mask.sum()}")

# === PACK SIZE EXTRACTION ===
def extract_pack_count(title):
    if pd.isna(title):
        return 1
    title_upper = str(title).upper()
    
    # Skip dimension patterns
    if re.search(r'\d+\s*X\s*\d+\s*(CM|MM|INCH|IN|M)\b', title_upper):
        pass  # May still have pack patterns
    
    patterns = [
        (r'PACK\s*OF\s*(\d+)', 1),
        (r'PK\s*(\d+)', 1),
        (r'(\d+)\s*PACK\b', 1),
        (r'\((\d+)\s*X\s*\d+\)', 1),
        (r'^(\d+)\s*X\s+\w', 1),
        (r'SET\s*OF\s*(\d+)', 1),
        (r'(\d+)\s*PCE', 1),
        (r'(\d+)\s*PCS', 1),
        (r'(\d+)\s*PIECE', 1),
        (r'(\d+)\s*BAGS\b', 1),
        (r'(\d+)\s*CONTAINERS\b', 1),
    ]
    
    if 'TWINPACK' in title_upper or 'TWIN PACK' in title_upper:
        return 2
    if 'TRIPLE PACK' in title_upper:
        return 3
    
    for pattern, group in patterns:
        match = re.search(pattern, title_upper)
        if match:
            val = int(match.group(group))
            if val > 1 and val < 500:
                return val
    return 1

df['supplier_pack'] = df['SupplierTitle'].apply(extract_pack_count)
df['amazon_pack'] = df['AmazonTitle'].apply(extract_pack_count)

# === TITLE SIMILARITY ===
def title_similarity(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).upper(), str(s2).upper()).ratio()

df['title_similarity'] = df.apply(lambda r: title_similarity(r['SupplierTitle'], r['AmazonTitle']), axis=1)

# === BRAND MATCHING ===
KNOWN_BRANDS = [
    'AMTECH', 'MASON CASH', 'ROLSON', 'KILNER', 'DRAPER', 'PYREX', 'CHEF AID', 
    'BLUE CANYON', 'ELLIOTT', 'FALCON', 'BAKER & SALT', 'BAKER AND SALT',
    'SCHOTT ZWIESEL', 'MARIGOLD', 'FAIRY', 'DETTOL', 'EVERBUILD', 'SOUDAL',
    'TIDYZ', 'BACOFOIL', 'HARRIS', 'EXTRASTAR', 'GIFTMAKER', 'PRIMA', 'APOLLO',
    'KILROCK', 'PRODEC', 'HOUSE MATE', 'TALA', 'LITTLE TREES', 'ELBOW GREASE',
    'PRICE & KENSINGTON', 'ULTRATAPE', 'FIRE UP', 'DOFF', 'GEEPAS', 'STATUS',
    'ROUNDUP', 'SUPERIOR', 'FIRST STEPS', 'MINKY', 'RUSSELL HOBBS', 'QUEST',
    'YALE', 'VINERS', 'MASTERCLASS', 'HEM', 'AIRWICK', 'AIR WICK', 'SPONTEX'
]

def extract_brand(title):
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            return brand
    return ""

df['supplier_brand'] = df['SupplierTitle'].apply(extract_brand)
df['amazon_brand'] = df['AmazonTitle'].apply(extract_brand)

def check_brand_match(row):
    sup_brand = row['supplier_brand']
    amz_title = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    if not sup_brand:
        return False
    return sup_brand in amz_title

df['brand_match'] = df.apply(check_brand_match, axis=1)

# === CALCULATE ADJUSTED PROFIT ===
df['pack_ratio'] = df['amazon_pack'] / df['supplier_pack'].replace(0, 1)
df['adjusted_profit'] = df['NetProfit'] - (df['pack_ratio'] - 1) * df['SupplierPrice_incVAT'].fillna(0)

def get_pack_verdict(row):
    if row['pack_ratio'] == 1:
        return "1:1 Match"
    elif row['pack_ratio'] > 1:
        return f"Pack {row['pack_ratio']:.0f}x"
    else:
        return "Pack < 1"

df['pack_verdict'] = df.apply(get_pack_verdict, axis=1)

# === CLASSIFICATION ===
def classify_row(row):
    is_exact_ean = (pd.notna(row['EAN_norm']) and 
                    pd.notna(row['EAN_OnPage_norm']) and 
                    row['EAN_norm'] == row['EAN_OnPage_norm'])
    
    net_profit = float(row['NetProfit']) if pd.notna(row['NetProfit']) else 0
    adjusted_profit = float(row['adjusted_profit']) if pd.notna(row['adjusted_profit']) else 0
    title_sim = float(row['title_similarity']) if pd.notna(row['title_similarity']) else 0
    pack_ratio = float(row['pack_ratio']) if pd.notna(row['pack_ratio']) else 1
    brand_match = row['brand_match']
    
    # VERIFIED: Exact EAN + positive profit
    if is_exact_ean:
        if pack_ratio > 1 and adjusted_profit <= 0:
            return 'FILTERED_OUT', 90, 'Exact EAN but pack mismatch makes profit negative'
        elif net_profit > 0:
            return 'VERIFIED', 95, 'Exact EAN match'
        else:
            return 'FILTERED_OUT', 90, 'Exact EAN but profit too low'
    
    # HIGHLY LIKELY: Known brand matches + strong title similarity
    if brand_match and title_sim >= 0.55 and net_profit > 0.05:
        if pack_ratio > 1 and adjusted_profit <= 0:
            return 'FILTERED_OUT', 85, 'Brand match but pack mismatch makes profit negative'
        return 'HIGHLY_LIKELY', int(title_sim * 100), f'Brand match: {row["supplier_brand"]}'
    
    # NEEDS VERIFICATION: Partial match
    if title_sim >= 0.40 and net_profit > 0:
        if brand_match:
            return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Brand match, verify pack/variant'
        elif title_sim >= 0.55:
            return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Good title similarity, verify brand'
        return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Partial match - verify details'
    
    # LOW PRIORITY: Weak evidence
    if title_sim >= 0.30 and net_profit > 0:
        return 'LOW_PRIORITY', int(title_sim * 100), 'Weak match - low confidence'
    
    # FILTERED OUT / OTHER
    if net_profit <= 0:
        return 'FILTERED_OUT', 50, 'Not profitable'
    
    return 'OTHER', 30, 'Insufficient match evidence'

results = df.apply(classify_row, axis=1)
df['verdict'] = [r[0] for r in results]
df['confidence'] = [r[1] for r in results]
df['reason'] = [r[2] for r in results]

# === GENERATE FORMATTED REPORT ===
def format_value(val, width):
    """Format a value to fit within specified width"""
    if pd.isna(val):
        s = "-"
    elif isinstance(val, float):
        if abs(val) < 0.001:
            s = "0.00"
        else:
            s = f"{val:.2f}"
    else:
        s = str(val)
    return s[:width].ljust(width)

def generate_table_row(row):
    """Generate a formatted table row with ACTUAL values"""
    verdict = format_value(row['verdict'], 12)
    conf = format_value(row['confidence'], 4)
    stitle = format_value(row['SupplierTitle'], 35)
    atitle = format_value(row['AmazonTitle'], 40)
    sean = format_value(row['EAN'], 13)
    aean = format_value(row['EAN_OnPage'], 13)
    asin = format_value(row['ASIN'], 10)
    sprice = format_value(row.get('SupplierPrice_incVAT', 0), 8)
    # Use actual selling_price from source
    sellprice = format_value(row.get('selling_price', row.get('SellingPrice_incVAT', 0)), 8)
    profit = format_value(row['NetProfit'], 8)
    roi = format_value(row.get('ROI', 0), 6)
    # Use actual sales from source
    sales = format_value(row.get('sales', 0), 5)
    pack = format_value(row['pack_verdict'], 12)
    adj = format_value(row['adjusted_profit'], 8)
    evidence = format_value(row['reason'], 25)
    filter_reason = "-" if row['verdict'] in ['VERIFIED', 'HIGHLY_LIKELY'] else format_value(row['reason'], 20)
    
    return f"| {verdict} | {conf} | {stitle} | {atitle} | {sean} | {aean} | {asin} | {sprice} | {sellprice} | {profit} | {roi} | {sales} | {pack} | {adj} | {evidence} | {filter_reason} |"

# Generate report
output = []
output.append("# GROUND TRUTH REFERENCE REPORT v4.1")
output.append("")
output.append("**Generated:** 2025-12-29")
output.append("**Dataset:** PARTDEC28_1.xlsx (1758 rows)")
output.append("**Methodology:** v4.1 Manual Analysis (Known Brands + Title Similarity + EAN + Variant Detection)")
output.append("")
output.append("## Summary Counts")
output.append("")
counts = df['verdict'].value_counts()
output.append("| Category | Count |")
output.append("|----------|-------|")
for cat in ['VERIFIED', 'HIGHLY_LIKELY', 'NEEDS_VERIFICATION', 'FILTERED_OUT', 'LOW_PRIORITY', 'OTHER']:
    count = counts.get(cat, 0)
    output.append(f"| {cat} | {count} |")
output.append("")

# Define table header
header = "| Verdict      | Conf | SupplierTitle                       | AmazonTitle                              | Supplier EAN  | Amazon EAN    | ASIN       | SuppPrice | SellPrice | NetProfit | ROI    | Sales | Pack Verdict | Adj Profit | Key Match Evidence          | Filter Reason        |"
separator = "|--------------|------|-------------------------------------|------------------------------------------|---------------|---------------|------------|-----------|-----------|-----------|--------|-------|--------------|------------|-----------------------------|-----------------------|"

# === VERIFIED SECTION (Sorted by NetProfit descending) ===
verified = df[df['verdict'] == 'VERIFIED'].sort_values('NetProfit', ascending=False)
output.append(f"## VERIFIED ({len(verified)} items)")
output.append("")
output.append("Exact EAN match + positive profit. **Sorted by NetProfit descending.**")
output.append("")
output.append("```text")
output.append(header)
output.append(separator)
for idx, row in verified.iterrows():
    output.append(generate_table_row(row))
output.append("```")
output.append("")

# === HIGHLY LIKELY SECTION (Sorted by Confidence descending) ===
hl = df[df['verdict'] == 'HIGHLY_LIKELY'].sort_values('confidence', ascending=False)
output.append(f"## HIGHLY LIKELY ({len(hl)} items)")
output.append("")
output.append("Known brand match in BOTH titles + strong title similarity. **Sorted by Confidence descending.**")
output.append("")
output.append("```text")
output.append(header)
output.append(separator)
for idx, row in hl.head(60).iterrows():
    output.append(generate_table_row(row))
output.append("```")
output.append("")

# === NEEDS VERIFICATION SECTION (Sorted by Confidence descending) ===
nv = df[df['verdict'] == 'NEEDS_VERIFICATION'].sort_values('confidence', ascending=False)
output.append(f"## NEEDS VERIFICATION ({len(nv)} items)")
output.append("")
output.append("Partial match requiring manual confirmation. **Sorted by Confidence descending.**")
output.append("")
output.append("```text")
output.append(header)
output.append(separator)
for idx, row in nv.head(80).iterrows():
    output.append(generate_table_row(row))
output.append("```")
output.append("")

# === FILTERED OUT SECTION (Sorted by NetProfit descending) ===
fo = df[(df['verdict'] == 'FILTERED_OUT') & (exact_ean_mask | df['brand_match'])].sort_values('NetProfit', ascending=False)
output.append(f"## FILTERED OUT - Confirmed Matches ({len(fo)} items)")
output.append("")
output.append("Confirmed product matches that are unprofitable. **Sorted by NetProfit descending.**")
output.append("")
output.append("```text")
output.append(header)
output.append(separator)
for idx, row in fo.head(30).iterrows():
    output.append(generate_table_row(row))
output.append("```")
output.append("")

# Save
with open('GROUND_TRUTH_REFERENCE_REPORT_v4.1.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\nSaved to GROUND_TRUTH_REFERENCE_REPORT_v4.1.md")
print("\nCategory Counts:")
print(counts)

# Also save updated CSV
df.to_csv('ground_truth_analysis_v41.csv', index=True)
print("\nSaved CSV: ground_truth_analysis_v41.csv")
