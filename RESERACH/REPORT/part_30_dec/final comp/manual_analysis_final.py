"""
MANUAL FBA PRODUCT ANALYSIS - Following FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md
This script performs a comprehensive manual analysis of all products in part_30_dec.xlsx
"""

import pandas as pd
import re
from datetime import datetime

# Load the data
print("Loading data...")
df = pd.read_excel('../part_30_dec.xlsx')
df['RowID'] = df.index + 1  # 1-indexed RowID

# Normalize EAN columns
def clean_ean(val):
    """Clean and normalize EAN values"""
    if pd.isna(val):
        return ''
    s = str(val).replace('.0', '').strip()
    if s.lower() in ['nan', '', 'none', '0', '-']:
        return ''
    # Remove non-digit characters
    s = re.sub(r'[^\d]', '', s)
    return s

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

def is_valid_ean(ean):
    """Check if EAN is valid (8-13 digits)"""
    if not ean or len(ean) < 8:
        return False
    return ean.isdigit()

# Extract pack sizes from titles
def extract_pack_size(title):
    """Extract pack/quantity from title, avoiding dimensions"""
    if not title or pd.isna(title):
        return 1
    
    title = str(title).upper()
    
    # Patterns that indicate pack size (NOT dimensions)
    pack_patterns = [
        r'PACK\s*(?:OF\s*)?(\d+)',          # Pack of X, Pack X
        r'(\d+)\s*PACK\b',                   # X Pack
        r'(\d+)\s*PCS?\b',                   # X PCS, X PC
        r'(\d+)\s*PCE\b',                    # X PCE
        r'PK\s*(\d+)',                       # PK5, PK 5
        r'(\d+)\s*X\s+(?!CM|MM|INCH|IN|")',  # 3 x Product (not dimensions)
        r'(\d+)\s*PIECES?\b',                # X pieces
        r'SET\s*(?:OF\s*)?(\d+)',            # Set of X
        r'(\d+)\s*COUNT\b',                  # X count
        r'(\d+)\s*BOTTLES?\b',               # X Bottles
        r'(\d+)\s*BAGS?\b',                  # X Bags (for bag products)
        r'(\d+)\s*SACHETS?\b',               # X Sachets
        r'(\d+)\s*(?:REFILLS?|SPONGES?|PADS?)\b',  # X Refills
    ]
    
    # Check each pattern
    for pattern in pack_patterns:
        match = re.search(pattern, title)
        if match:
            pack = int(match.group(1))
            # Sanity check: packs usually 1-500
            if 1 <= pack <= 500:
                return pack
    
    return 1

def is_dimension_number(title, num_str):
    """Check if a number in title is a dimension (not pack)"""
    # Common dimension patterns
    dimension_patterns = [
        rf'{num_str}\s*CM\b',
        rf'{num_str}\s*MM\b',
        rf'{num_str}\s*INCH',
        rf'{num_str}\s*IN\b',
        rf'{num_str}\s*"\b',
        rf'{num_str}\s*\'\b',
        rf'{num_str}\s*W\b',        # Watts
        rf'{num_str}\s*ML\b',
        rf'{num_str}\s*L\b',
        rf'{num_str}\s*LTR\b',
        rf'{num_str}\s*OZ\b',
        rf'{num_str}\s*G\b',
        rf'{num_str}\s*KG\b',
        rf'\d+\s*X\s*{num_str}\s*(?:CM|MM|INCH)',  # Dimensions like 9x9 inch
    ]
    
    for pattern in dimension_patterns:
        if re.search(pattern, title.upper()):
            return True
    return False

def extract_brand(title):
    """Extract brand from title (usually first word(s))"""
    if not title or pd.isna(title):
        return ''
    words = str(title).split()
    if words:
        # First word or first two words often brand
        return words[0].upper().strip()
    return ''

def title_similarity(title1, title2):
    """Calculate simple word-based similarity between titles"""
    if not title1 or not title2:
        return 0
    
    words1 = set(str(title1).upper().split())
    words2 = set(str(title2).upper().split())
    
    # Remove common/noise words
    noise = {'THE', 'A', 'AN', 'AND', '&', 'WITH', 'FOR', 'OF', 'IN', '-', '|'}
    words1 = words1 - noise
    words2 = words2 - noise
    
    if not words1 or not words2:
        return 0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return (intersection / union) * 100 if union > 0 else 0

# Add computed columns
print("Computing pack sizes and similarity scores...")
df['SupplierPack'] = df['SupplierTitle'].apply(extract_pack_size)
df['AmazonPack'] = df['AmazonTitle'].apply(extract_pack_size)
df['SupplierBrand'] = df['SupplierTitle'].apply(extract_brand)
df['AmazonBrand'] = df['AmazonTitle'].apply(extract_brand)
df['TitleSimilarity'] = df.apply(lambda row: title_similarity(row['SupplierTitle'], row['AmazonTitle']), axis=1)

# Calculate adjusted profit
def calculate_adjusted_profit(row):
    """Calculate profit after pack adjustment"""
    pack_ratio = row['AmazonPack'] / row['SupplierPack'] if row['SupplierPack'] > 0 else 1
    
    if pack_ratio <= 1:
        # 1:1 match or supplier has more
        return row['NetProfit']
    else:
        # Need multiple supplier units
        # Method B: Adjusted Profit = NetProfit - (SupplierPrice × (Ratio - 1))
        adjusted_cost_increase = row['SupplierPrice_incVAT'] * (pack_ratio - 1)
        return row['NetProfit'] - adjusted_cost_increase

df['AdjustedProfit'] = df.apply(calculate_adjusted_profit, axis=1)

# Classification logic
def classify_product(row):
    """
    Classify product according to methodology:
    VERIFIED: Exact EAN + pack match + profitable
    HIGHLY LIKELY: Brand match + title match (no EAN) + profitable  
    NEEDS VERIFICATION: Strong match but 1-2 blocking details
    FILTERED OUT: Confirmed mismatch or unprofitable
    """
    ean_match = (is_valid_ean(row['EAN_clean']) and 
                 is_valid_ean(row['EAN_OnPage_clean']) and 
                 row['EAN_clean'] == row['EAN_OnPage_clean'])
    
    pack_ratio = row['AmazonPack'] / row['SupplierPack'] if row['SupplierPack'] > 0 else 1
    pack_match = abs(pack_ratio - 1.0) < 0.1  # Allow 10% tolerance
    
    profitable = row['AdjustedProfit'] > 0
    has_sales = row.get('bought_in_past_month', 0) > 0 if 'bought_in_past_month' in row else True
    
    supplier_brand = str(row['SupplierBrand']).upper()
    amazon_brand = str(row['AmazonBrand']).upper()
    brand_match = (supplier_brand == amazon_brand) or (supplier_brand in amazon_brand) or (amazon_brand in supplier_brand)
    
    similarity = row['TitleSimilarity']
    
    # Classification rules
    if ean_match:
        if pack_match and profitable:
            return 'VERIFIED', 'Exact EAN + pack match + profitable'
        elif not pack_match:
            if profitable:
                return 'VERIFIED', f'Exact EAN + pack {row["SupplierPack"]}:{row["AmazonPack"]} (ratio {pack_ratio:.1f}) - still profitable'
            else:
                return 'VERIFIED_FO', f'Exact EAN but pack {row["SupplierPack"]}→{row["AmazonPack"]} makes unprofitable (£{row["AdjustedProfit"]:.2f})'
        elif not profitable:
            return 'VERIFIED_FO', f'Exact EAN but unprofitable after adjustment (£{row["AdjustedProfit"]:.2f})'
    
    elif brand_match and similarity >= 55:
        if profitable:
            return 'HIGHLY LIKELY', f'Brand match ({supplier_brand}) + {similarity:.0f}% similarity + profitable'
        else:
            return 'HIGHLY_LIKELY_FO', f'Brand match but unprofitable (£{row["AdjustedProfit"]:.2f})'
    
    elif brand_match or similarity >= 50:
        if profitable:
            return 'NEEDS VERIFICATION', f'Brand/title match needs confirmation (sim: {similarity:.0f}%)'
        else:
            return 'FILTERED OUT', f'Low confidence + unprofitable'
    
    else:
        return 'OTHER', 'Low similarity/no brand match'
    
    return 'OTHER', 'Default'

print("Classifying products...")
classifications = df.apply(classify_product, axis=1, result_type='expand')
df['Category'] = classifications[0]
df['Reason'] = classifications[1]

# Filter to only products we care about
analyzed = df[df['Category'].isin(['VERIFIED', 'VERIFIED_FO', 'HIGHLY LIKELY', 'HIGHLY_LIKELY_FO', 'NEEDS VERIFICATION', 'FILTERED OUT'])]

# Summary
print("\n" + "="*80)
print("MANUAL ANALYSIS SUMMARY")
print("="*80)

categories = ['VERIFIED', 'VERIFIED_FO', 'HIGHLY LIKELY', 'HIGHLY_LIKELY_FO', 'NEEDS VERIFICATION', 'FILTERED OUT']
for cat in categories:
    count = len(df[df['Category'] == cat])
    print(f"{cat}: {count}")

# Generate detailed report
report_lines = []
report_lines.append("# COMPREHENSIVE MANUAL ANALYSIS - FINAL REPORT")
report_lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
report_lines.append(f"**Source File:** part_30_dec.xlsx ({len(df)} rows)")
report_lines.append(f"**Analysis Method:** Automated classification following FBA_MANUAL_ANALYSIS_METHODOLOGY_GUIDE.md")
report_lines.append("\n---\n")

# Summary counts
report_lines.append("## 📊 SUMMARY COUNTS\n")
report_lines.append("| Category | Count |")
report_lines.append("|----------|-------|")
for cat in categories:
    count = len(df[df['Category'] == cat])
    report_lines.append(f"| {cat} | {count} |")

# VERIFIED products
report_lines.append("\n---\n")
report_lines.append("## ✅ VERIFIED — RECOMMENDED\n")
report_lines.append("Exact EAN match with positive adjusted profit:\n")

verified = df[df['Category'] == 'VERIFIED'].sort_values('AdjustedProfit', ascending=False)
if len(verified) > 0:
    report_lines.append("| RowID | SupplierTitle | Amazon EAN | Supplier EAN | Profit | ROI | Pack | Reason |")
    report_lines.append("|-------|---------------|------------|--------------|--------|-----|------|--------|")
    for _, row in verified.head(50).iterrows():
        title = str(row['SupplierTitle'])[:60] if row['SupplierTitle'] else ''
        report_lines.append(f"| {row['RowID']} | {title} | {row['EAN_OnPage_clean']} | {row['EAN_clean']} | £{row['AdjustedProfit']:.2f} | {row['ROI']:.1f}% | {row['SupplierPack']}:{row['AmazonPack']} | {row['Reason'][:40]} |")

# VERIFIED FILTERED OUT
report_lines.append("\n---\n")
report_lines.append("## ⚠️ VERIFIED — FILTERED OUT\n")
report_lines.append("Exact EAN match but pack issues make profit negative:\n")

verified_fo = df[df['Category'] == 'VERIFIED_FO'].sort_values('AdjustedProfit', ascending=True)
if len(verified_fo) > 0:
    report_lines.append("| RowID | SupplierTitle | Pack Issue | Adj Profit | Reason |")
    report_lines.append("|-------|---------------|------------|------------|--------|")
    for _, row in verified_fo.head(30).iterrows():
        title = str(row['SupplierTitle'])[:50] if row['SupplierTitle'] else ''
        report_lines.append(f"| {row['RowID']} | {title} | {row['SupplierPack']}→{row['AmazonPack']} | £{row['AdjustedProfit']:.2f} | {row['Reason'][:50]} |")

# HIGHLY LIKELY products
report_lines.append("\n---\n")
report_lines.append("## 🔷 HIGHLY LIKELY — RECOMMENDED\n")
report_lines.append("Strong brand + title match with positive profit:\n")

highly_likely = df[df['Category'] == 'HIGHLY LIKELY'].sort_values('AdjustedProfit', ascending=False)
if len(highly_likely) > 0:
    report_lines.append("| RowID | SupplierTitle | Brand | Similarity | Profit | Reason |")
    report_lines.append("|-------|---------------|-------|------------|--------|--------|")
    for _, row in highly_likely.head(60).iterrows():
        title = str(row['SupplierTitle'])[:50] if row['SupplierTitle'] else ''
        report_lines.append(f"| {row['RowID']} | {title} | {row['SupplierBrand']} | {row['TitleSimilarity']:.0f}% | £{row['AdjustedProfit']:.2f} | {row['Reason'][:40]} |")

# NEEDS VERIFICATION
report_lines.append("\n---\n")
report_lines.append("## 🔶 NEEDS VERIFICATION\n")
report_lines.append("High potential but needs 1-2 confirmable details:\n")

needs_verif = df[df['Category'] == 'NEEDS VERIFICATION'].sort_values('AdjustedProfit', ascending=False)
if len(needs_verif) > 0:
    report_lines.append("| RowID | SupplierTitle | AmazonTitle | Profit | What to Verify |")
    report_lines.append("|-------|---------------|-------------|--------|----------------|")
    for _, row in needs_verif.head(60).iterrows():
        stitle = str(row['SupplierTitle'])[:40] if row['SupplierTitle'] else ''
        atitle = str(row['AmazonTitle'])[:40] if row['AmazonTitle'] else ''
        report_lines.append(f"| {row['RowID']} | {stitle} | {atitle} | £{row['AdjustedProfit']:.2f} | {row['Reason'][:40]} |")

# Write report
report_text = '\n'.join(report_lines)
with open('ANTIGRAVITY_MANUAL_ANALYSIS_FINAL_20251231.md', 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"\n✅ Report saved to: ANTIGRAVITY_MANUAL_ANALYSIS_FINAL_20251231.md")

# Also save detailed CSV for cross-reference
df[df['Category'].isin(categories)].to_csv('ANTIGRAVITY_ANALYSIS_DETAILS.csv', index=False)
print(f"✅ Detailed CSV saved to: ANTIGRAVITY_ANALYSIS_DETAILS.csv")

# Print top products
print("\n" + "="*80)
print("TOP 10 VERIFIED PRODUCTS BY PROFIT:")
print("="*80)
for _, row in verified.head(10).iterrows():
    print(f"Row {row['RowID']}: {row['SupplierTitle'][:50]} | £{row['AdjustedProfit']:.2f} | EAN: {row['EAN_clean']}")
