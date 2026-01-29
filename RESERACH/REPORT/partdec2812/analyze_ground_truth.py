"""
GROUND TRUTH GENERATOR v2 - Applies v2 Manual Analysis Methodology to PARTDEC28_1.xlsx

Fixed version with better brand matching and classification logic.
"""

import pandas as pd
import re
from difflib import SequenceMatcher

# Load dataset
df = pd.read_excel('PARTDEC28_1.xlsx')
print(f"Loaded {len(df)} rows")

# === STEP 1: EXACT EAN MATCHES ===
def normalize_ean(ean):
    """Normalize EAN for comparison"""
    if pd.isna(ean):
        return None
    ean_str = str(ean).strip()
    ean_str = re.sub(r'[^0-9]', '', ean_str)
    if not ean_str:
        return None
    return ean_str

df['EAN_norm'] = df['EAN'].apply(normalize_ean)
df['EAN_OnPage_norm'] = df['EAN_OnPage'].apply(normalize_ean)

exact_ean_mask = (df['EAN_norm'].notna()) & (df['EAN_OnPage_norm'].notna()) & (df['EAN_norm'] == df['EAN_OnPage_norm'])
print(f"Exact EAN matches: {exact_ean_mask.sum()}")

# === STEP 2: PACK SIZE EXTRACTION ===
def extract_pack_count(title):
    """Extract pack count from title, avoiding dimensions"""
    if pd.isna(title):
        return 1
    
    title_upper = str(title).upper()
    
    # Pattern: "Pack of X", "PK X", "X PACK", "X x Product"
    patterns = [
        (r'PACK\s*OF\s*(\d+)', 1),
        (r'PK\s*(\d+)', 1),
        (r'(\d+)\s*PACK\b', 1),
        (r'\((\d+)\s*X\s*\d+\)', 1),  # "(4 x 50)"
        (r'^(\d+)\s*X\s+\w', 1),  # "3 x Product" at start
        (r'SET\s*OF\s*(\d+)', 1),
        (r'(\d+)\s*PCE', 1),
        (r'(\d+)\s*PCS', 1),
        (r'(\d+)\s*BAGS\b', 1),
        (r'(\d+)\s*PIECE', 1),
    ]
    
    # Check for twin/triple pack
    if 'TWINPACK' in title_upper or 'TWIN PACK' in title_upper:
        return 2
    if 'TRIPLE PACK' in title_upper:
        return 3
    
    for pattern, group in patterns:
        match = re.search(pattern, title_upper)
        if match:
            return int(match.group(group))
    
    return 1

df['supplier_pack'] = df['SupplierTitle'].apply(extract_pack_count)
df['amazon_pack'] = df['AmazonTitle'].apply(extract_pack_count)

# === STEP 3: TITLE SIMILARITY ===
def title_similarity(s1, s2):
    """Calculate title similarity score"""
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).upper(), str(s2).upper()).ratio()

df['title_similarity'] = df.apply(lambda r: title_similarity(r['SupplierTitle'], r['AmazonTitle']), axis=1)

# === STEP 4: BRAND EXTRACTION AND MATCHING ===
KNOWN_BRANDS = [
    'AMTECH', 'MASON CASH', 'ROLSON', 'KILNER', 'DRAPER', 'PYREX', 'CHEF AID', 
    'BLUE CANYON', 'ELLIOTT', 'FALCON', 'BAKER & SALT', 'BAKER AND SALT',
    'SCHOTT ZWIESEL', 'MARIGOLD', 'FAIRY', 'DETTOL', 'EVERBUILD', 'SOUDAL',
    'TIDYZ', 'BACOFOIL', 'HARRIS', 'EXTRASTAR', 'GIFTMAKER', 'PRIMA', 'APOLLO',
    'KILROCK', 'PRODEC', 'HOUSE MATE', 'TALA', 'LITTLE TREES', 'ELBOW GREASE',
    'PRICE & KENSINGTON', 'ULTRATAPE', 'FIRE UP', 'DOFF', 'GEEPAS', 'STATUS'
]

def extract_brand(title):
    """Extract brand from title"""
    if pd.isna(title):
        return ""
    title_upper = str(title).upper()
    
    # Check known brands first
    for brand in KNOWN_BRANDS:
        if brand in title_upper:
            return brand
    
    # Fallback: first 2 words
    words = title_upper.split()
    if len(words) >= 2:
        return " ".join(words[:2])
    return words[0] if words else ""

df['supplier_brand'] = df['SupplierTitle'].apply(extract_brand)
df['amazon_brand'] = df['AmazonTitle'].apply(extract_brand)

def check_brand_match(row):
    """Check if brands match between supplier and Amazon"""
    sup_brand = row['supplier_brand']
    amz_title = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    
    if not sup_brand:
        return False
    
    # Check if supplier brand appears in Amazon title
    return sup_brand in amz_title

df['brand_match'] = df.apply(check_brand_match, axis=1)

# === STEP 5: CALCULATE ADJUSTED PROFIT ===
df['pack_ratio'] = df['amazon_pack'] / df['supplier_pack'].replace(0, 1)
df['adjusted_profit'] = df['NetProfit'] - (df['pack_ratio'] - 1) * df['SupplierPrice_incVAT'].fillna(0)

# === STEP 6: CLASSIFICATION ===
def classify_row(row):
    """Apply v2 methodology to classify each row"""
    
    # Check for exact EAN match
    is_exact_ean = (pd.notna(row['EAN_norm']) and 
                    pd.notna(row['EAN_OnPage_norm']) and 
                    row['EAN_norm'] == row['EAN_OnPage_norm'])
    
    # Get values
    net_profit = float(row['NetProfit']) if pd.notna(row['NetProfit']) else 0
    adjusted_profit = float(row['adjusted_profit']) if pd.notna(row['adjusted_profit']) else 0
    
    # Handle sales column - try both possible names
    sales = 0
    if 'sales_numeric' in row.index and pd.notna(row.get('sales_numeric')):
        sales = float(row['sales_numeric'])
    elif 'Sales' in row.index and pd.notna(row.get('Sales')):
        sales = float(row['Sales'])
    
    title_sim = float(row['title_similarity']) if pd.notna(row['title_similarity']) else 0
    pack_ratio = float(row['pack_ratio']) if pd.notna(row['pack_ratio']) else 1
    brand_match = row['brand_match']
    
    # --- CLASSIFICATION LOGIC ---
    
    # 1. VERIFIED: Exact EAN + No pack contradiction + Positive profit
    if is_exact_ean:
        if pack_ratio > 1 and adjusted_profit <= 0:
            return 'FILTERED_OUT', 90, 'Exact EAN but pack mismatch makes profit negative'
        elif net_profit > 0:
            if pack_ratio > 1:
                return 'VERIFIED', 90, f'Exact EAN match, pack {pack_ratio}x - verify pack'
            return 'VERIFIED', 95, 'Exact EAN match, positive profit'
        else:
            return 'FILTERED_OUT', 90, 'Exact EAN but profit too low'
    
    # 2. HIGHLY LIKELY: Brand matches + Strong title similarity + Positive profit
    if brand_match and title_sim >= 0.55 and net_profit > 0.05:
        if pack_ratio > 1 and adjusted_profit <= 0:
            return 'FILTERED_OUT', 85, 'Brand match but pack mismatch makes profit negative'
        return 'HIGHLY_LIKELY', int(title_sim * 100), 'Strong brand and title match'
    
    # 3. NEEDS VERIFICATION: Moderate match that needs checking
    if title_sim >= 0.40 and net_profit > 0:
        if brand_match:
            return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Brand match, verify pack/variant'
        elif title_sim >= 0.55:
            return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Good title similarity, verify brand'
        return 'NEEDS_VERIFICATION', int(title_sim * 100), 'Partial match - verify details'
    
    # 4. LOW PRIORITY: Weak evidence
    if title_sim >= 0.30 and net_profit > 0:
        return 'LOW_PRIORITY', int(title_sim * 100), 'Weak match - low confidence'
    
    # 5. FILTERED OUT / OTHER
    if net_profit <= 0:
        return 'FILTERED_OUT', 50, 'Not profitable'
    
    return 'OTHER', 30, 'Insufficient match evidence'

# Apply classification
results = df.apply(classify_row, axis=1)
df['verdict'] = [r[0] for r in results]
df['confidence'] = [r[1] for r in results]
df['reason'] = [r[2] for r in results]

# === PRINT SUMMARY ===
print("\n" + "="*60)
print("GROUND TRUTH CLASSIFICATION SUMMARY")
print("="*60)
counts = df['verdict'].value_counts()
print(counts)

# === SAVE DETAILED RESULTS ===
output = []
output.append("# GROUND TRUTH REFERENCE REPORT")
output.append("")
output.append("**Generated:** 2025-12-29")
output.append("**Dataset:** PARTDEC28_1.xlsx (1758 rows)")
output.append("**Methodology:** v2 Manual Analysis (Brand + Title + EAN)")
output.append("")
output.append("## Summary Counts")
output.append("")
output.append("| Category | Count |")
output.append("|----------|-------|")
for cat, count in counts.items():
    output.append(f"| {cat} | {count} |")
output.append("")

# === VERIFIED SECTION ===
verified = df[df['verdict'] == 'VERIFIED'].sort_values('NetProfit', ascending=False)
output.append(f"## VERIFIED ({len(verified)} items)")
output.append("")
output.append("Exact EAN match + positive profit")
output.append("")
output.append("| Row | SupplierTitle | AmazonTitle | EAN | NetProfit |")
output.append("|-----|---------------|-------------|-----|-----------|")
for idx, row in verified.iterrows():
    stitle = str(row['SupplierTitle'])[:40] if pd.notna(row['SupplierTitle']) else ""
    atitle = str(row['AmazonTitle'])[:40] if pd.notna(row['AmazonTitle']) else ""
    ean = str(row['EAN'])[:15] if pd.notna(row['EAN']) else ""
    profit = f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else ""
    output.append(f"| {idx} | {stitle} | {atitle} | {ean} | {profit} |")
output.append("")

# === HIGHLY LIKELY SECTION ===
hl = df[df['verdict'] == 'HIGHLY_LIKELY'].sort_values('NetProfit', ascending=False)
output.append(f"## HIGHLY LIKELY ({len(hl)} items)")
output.append("")
output.append("Brand match + strong title similarity (>55%)")
output.append("")
output.append("| Row | SupplierTitle | AmazonTitle | Similarity | NetProfit |")
output.append("|-----|---------------|-------------|------------|-----------|")
for idx, row in hl.head(100).iterrows():
    stitle = str(row['SupplierTitle'])[:40] if pd.notna(row['SupplierTitle']) else ""
    atitle = str(row['AmazonTitle'])[:40] if pd.notna(row['AmazonTitle']) else ""
    sim = row['title_similarity']
    profit = f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else ""
    output.append(f"| {idx} | {stitle} | {atitle} | {sim:.0%} | {profit} |")
output.append("")

# === NEEDS VERIFICATION SECTION ===
nv = df[df['verdict'] == 'NEEDS_VERIFICATION'].sort_values('NetProfit', ascending=False)
output.append(f"## NEEDS VERIFICATION ({len(nv)} items)")
output.append("")
output.append("Partial match requiring manual confirmation")
output.append("")
output.append("| Row | SupplierTitle | AmazonTitle | Similarity | NetProfit | Reason |")
output.append("|-----|---------------|-------------|------------|-----------|--------|")
for idx, row in nv.head(100).iterrows():
    stitle = str(row['SupplierTitle'])[:35] if pd.notna(row['SupplierTitle']) else ""
    atitle = str(row['AmazonTitle'])[:35] if pd.notna(row['AmazonTitle']) else ""
    sim = row['title_similarity']
    profit = f"£{row['NetProfit']:.2f}" if pd.notna(row['NetProfit']) else ""
    reason = str(row['reason'])[:30]
    output.append(f"| {idx} | {stitle} | {atitle} | {sim:.0%} | {profit} | {reason} |")

# === FILTERED OUT SECTION (Confirmed matches that are unprofitable) ===
fo = df[(df['verdict'] == 'FILTERED_OUT') & (exact_ean_mask | df['brand_match'])].sort_values('NetProfit', ascending=False)
output.append("")
output.append(f"## FILTERED OUT - Confirmed Matches ({len(fo)} items)")
output.append("")
output.append("Confirmed matches that are unprofitable due to pack mismatch")
output.append("")
output.append("| Row | SupplierTitle | AmazonTitle | Pack Ratio | Reason |")
output.append("|-----|---------------|-------------|------------|--------|")
for idx, row in fo.head(50).iterrows():
    stitle = str(row['SupplierTitle'])[:35] if pd.notna(row['SupplierTitle']) else ""
    atitle = str(row['AmazonTitle'])[:35] if pd.notna(row['AmazonTitle']) else ""
    pack_ratio = row['pack_ratio'] if pd.notna(row['pack_ratio']) else 1
    reason = str(row['reason'])[:40]
    output.append(f"| {idx} | {stitle} | {atitle} | {pack_ratio:.1f}x | {reason} |")

# Save to markdown file
with open('GROUND_TRUTH_REFERENCE_REPORT.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"\nSaved to GROUND_TRUTH_REFERENCE_REPORT.md")

# Also save full CSV
df[['EAN', 'EAN_OnPage', 'ASIN', 'SupplierTitle', 'AmazonTitle', 'NetProfit', 'ROI', 
    'supplier_pack', 'amazon_pack', 'pack_ratio', 'adjusted_profit', 'title_similarity',
    'brand_match', 'verdict', 'confidence', 'reason']].to_csv('ground_truth_analysis.csv', index=True)
print("Saved full analysis to ground_truth_analysis.csv")
