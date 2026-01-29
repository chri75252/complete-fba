import pandas as pd
import numpy as np
import re
from difflib import SequenceMatcher

# Load PART3.xlsx
df = pd.read_excel('PART3.xlsx')

# Clean EAN columns
df['_sup_ean'] = df['EAN'].astype(str).str.strip().str.replace('.0', '', regex=False)
df['_amz_ean'] = df['EAN_OnPage'].astype(str).str.strip().str.replace('.0', '', regex=False)

# Identify exact EAN matches
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

exact_ean_df = df[ean_match_mask].copy()
print("="*80)
print("EXACT EAN MATCHES FROM PART3.xlsx")
print("="*80)
print(f"Total exact EAN matches: {len(exact_ean_df)}")
print()

# Function to extract pack quantities
def extract_pack_qty(title):
    if pd.isna(title):
        return 1
    title = str(title).lower()
    
    # Patterns to extract pack quantities
    patterns = [
        r'pack of (\d+)',
        r'(\d+)\s*pack\b',
        r'(\d+)\s*pcs\b',
        r'(\d+)\s*pieces\b',
        r'set of (\d+)',
        r'(\d+)\s*x\s+\w',  # "3 x ", "4 x "
        r'x\s*(\d+)\b',     # "x3", "x 3"
        r'(\d+)\s*bags\b',
        r'(\d+)\s*bottles\b',
        r'(\d+)\s*containers\b',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            qty = int(match.group(1))
            if 1 < qty <= 200:  # Reasonable pack size
                return qty
    return 1

# Function to check if titles indicate a pack mismatch
def check_pack_mismatch(sup_title, amz_title):
    sup_qty = extract_pack_qty(sup_title)
    amz_qty = extract_pack_qty(amz_title)
    
    if sup_qty != amz_qty and (sup_qty > 1 or amz_qty > 1):
        return f"MISMATCH ({sup_qty} vs {amz_qty})"
    return "OK"

# Function for title similarity
def title_similarity(s1, s2):
    if pd.isna(s1) or pd.isna(s2):
        return 0
    return SequenceMatcher(None, str(s1).lower(), str(s2).lower()).ratio()

# Analyze each exact EAN match
print("DETAILED ANALYSIS OF EXACT EAN MATCHES:")
print("-"*80)

confirmed_exact_ean = []
excluded_exact_ean = []

for idx, row in exact_ean_df.iterrows():
    asin = row['ASIN']
    sup_title = row['SupplierTitle']
    amz_title = row['AmazonTitle']
    ean = row['EAN']
    profit = row['NetProfit']
    sales = row['bought_in_past_month']
    
    pack_status = check_pack_mismatch(sup_title, amz_title)
    sim = title_similarity(sup_title, amz_title)
    
    sup_qty = extract_pack_qty(sup_title)
    amz_qty = extract_pack_qty(amz_title)
    
    if pack_status == "OK":
        confirmed_exact_ean.append({
            'ASIN': asin,
            'EAN': ean,
            'SupplierTitle': sup_title,
            'AmazonTitle': amz_title,
            'NetProfit': profit,
            'Sales': sales,
            'TitleSimilarity': sim,
            'PackVerdict': 'CONFIRMED (Exact EAN, Pack OK)',
            'SupQty': sup_qty,
            'AmzQty': amz_qty
        })
        status = "CONFIRMED"
    else:
        excluded_exact_ean.append({
            'ASIN': asin,
            'EAN': ean,
            'SupplierTitle': sup_title,
            'AmazonTitle': amz_title,
            'NetProfit': profit,
            'Sales': sales,
            'TitleSimilarity': sim,
            'PackVerdict': f'EXCLUDED ({pack_status})',
            'SupQty': sup_qty,
            'AmzQty': amz_qty
        })
        status = f"EXCLUDED - {pack_status}"
    
    print(f"{asin} | EAN: {ean}")
    print(f"  Supplier: {sup_title[:60]}...")
    print(f"  Amazon: {amz_title[:60]}...")
    print(f"  Similarity: {sim:.2f} | Pack: {pack_status} | Profit: £{profit:.2f} | Sales: {sales}")
    print(f"  STATUS: {status}")
    print()

print("="*80)
print(f"CONFIRMED EXACT EAN MATCHES: {len(confirmed_exact_ean)}")
print(f"EXCLUDED EXACT EAN MATCHES (pack issues): {len(excluded_exact_ean)}")
print("="*80)

# Now analyze non-EAN matches with very high confidence
print()
print("="*80)
print("ANALYZING NON-EAN MATCHES FOR HIGH-CONFIDENCE CONFIRMATION")
print("="*80)

# Get rows without exact EAN match
non_ean_df = df[~ean_match_mask].copy()

# Calculate title similarity
non_ean_df['sim'] = non_ean_df.apply(lambda r: title_similarity(r['SupplierTitle'], r['AmazonTitle']), axis=1)
non_ean_df['sup_qty'] = non_ean_df['SupplierTitle'].apply(extract_pack_qty)
non_ean_df['amz_qty'] = non_ean_df['AmazonTitle'].apply(extract_pack_qty)
non_ean_df['pack_ok'] = non_ean_df.apply(lambda r: r['sup_qty'] == r['amz_qty'] or (r['sup_qty'] == 1 and r['amz_qty'] == 1), axis=1)

# Function to extract key tokens for matching
def extract_key_tokens(title):
    if pd.isna(title):
        return set()
    title = str(title).lower()
    # Remove common words
    stopwords = {'the', 'a', 'an', 'and', 'or', 'for', 'with', 'in', 'on', 'at', 'to', 'of', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare', 'ought', 'used', 'pack'}
    # Extract words
    words = re.findall(r'\b[a-z]{3,}\b', title)
    return set([w for w in words if w not in stopwords])

non_ean_df['sup_tokens'] = non_ean_df['SupplierTitle'].apply(extract_key_tokens)
non_ean_df['amz_tokens'] = non_ean_df['AmazonTitle'].apply(extract_key_tokens)
non_ean_df['token_overlap'] = non_ean_df.apply(lambda r: len(r['sup_tokens'] & r['amz_tokens']), axis=1)
non_ean_df['token_jaccard'] = non_ean_df.apply(
    lambda r: len(r['sup_tokens'] & r['amz_tokens']) / len(r['sup_tokens'] | r['amz_tokens']) 
    if len(r['sup_tokens'] | r['amz_tokens']) > 0 else 0, 
    axis=1
)

# Brand extraction
def extract_brand(title):
    if pd.isna(title):
        return None
    title = str(title).upper()
    # Common brands in the data
    brands = ['MASON CASH', 'PYREX', 'TIDYZ', 'AMTECH', 'ROLSON', 'DEKTON', 'BLUE CANYON', 'FAIRY', 
              'EVERBUILD', 'KILNER', 'DETTOL', 'MARIGOLD', 'PRICE', 'KENSINGTON', 'SCHOTT ZWIESEL',
              'BAKER', 'SALT', 'HARRIS', 'FALCON', 'ELLIOTT', 'PRIMA', 'QUEST', 'BACOFOIL', 'SOUDAL',
              'STATUS', 'EXTRASTAR', 'GIFTMAKER', 'DRAPER', 'BRIGHT', 'HOMELY', 'KINGFISHER', 'ROUNDUP']
    for brand in brands:
        if brand in title:
            return brand
    return None

non_ean_df['sup_brand'] = non_ean_df['SupplierTitle'].apply(extract_brand)
non_ean_df['amz_brand'] = non_ean_df['AmazonTitle'].apply(extract_brand)
non_ean_df['brand_match'] = non_ean_df.apply(
    lambda r: r['sup_brand'] == r['amz_brand'] and r['sup_brand'] is not None, 
    axis=1
)

# CONFIRMED criteria for non-EAN:
# 1. Title similarity >= 0.65 AND pack_ok AND (brand_match OR token_overlap >= 4)
# OR
# 2. Title similarity >= 0.50 AND pack_ok AND brand_match AND token_overlap >= 3

confirmed_non_ean = []

for idx, row in non_ean_df.iterrows():
    sim = row['sim']
    pack_ok = row['pack_ok']
    brand_match = row['brand_match']
    token_overlap = row['token_overlap']
    token_jaccard = row['token_jaccard']
    profit = row['NetProfit']
    sales = row['bought_in_past_month']
    
    confirmed = False
    reason = ""
    
    # Criteria 1: High similarity + pack OK + (brand or token overlap)
    if sim >= 0.65 and pack_ok and (brand_match or token_overlap >= 4):
        confirmed = True
        reason = f"High similarity ({sim:.2f}) + pack OK + {'brand match' if brand_match else f'token overlap ({token_overlap})'}"
    
    # Criteria 2: Medium similarity + pack OK + brand match + token overlap
    elif sim >= 0.50 and pack_ok and brand_match and token_overlap >= 3:
        confirmed = True
        reason = f"Medium similarity ({sim:.2f}) + pack OK + brand match + token overlap ({token_overlap})"
    
    # Criteria 3: High token Jaccard + pack OK
    elif token_jaccard >= 0.40 and pack_ok and token_overlap >= 4:
        confirmed = True
        reason = f"High token Jaccard ({token_jaccard:.2f}) + pack OK + token overlap ({token_overlap})"
    
    if confirmed:
        confirmed_non_ean.append({
            'ASIN': row['ASIN'],
            'EAN': row['EAN'],
            'SupplierTitle': row['SupplierTitle'],
            'AmazonTitle': row['AmazonTitle'],
            'NetProfit': profit,
            'Sales': sales,
            'TitleSimilarity': sim,
            'TokenOverlap': token_overlap,
            'TokenJaccard': token_jaccard,
            'BrandMatch': brand_match,
            'PackVerdict': 'CONFIRMED (Title Analysis)',
            'Reason': reason
        })

print(f"CONFIRMED NON-EAN MATCHES (via title analysis): {len(confirmed_non_ean)}")
print()

# Sort by sales
confirmed_non_ean_df = pd.DataFrame(confirmed_non_ean).sort_values('Sales', ascending=False)
print("TOP 30 CONFIRMED NON-EAN MATCHES:")
print("-"*80)
for idx, row in confirmed_non_ean_df.head(30).iterrows():
    print(f"{row['ASIN']} | Sim: {row['TitleSimilarity']:.2f} | Tokens: {row['TokenOverlap']} | Profit: £{row['NetProfit']:.2f} | Sales: {row['Sales']}")
    print(f"  Supplier: {str(row['SupplierTitle'])[:70]}")
    print(f"  Amazon: {str(row['AmazonTitle'])[:70]}")
    print(f"  Reason: {row['Reason']}")
    print()

# Total confirmed
total_confirmed = len(confirmed_exact_ean) + len(confirmed_non_ean)
print("="*80)
print(f"TOTAL CONFIRMED MATCHES FROM PART3: {total_confirmed}")
print(f"  - Exact EAN (pack OK): {len(confirmed_exact_ean)}")
print(f"  - Non-EAN (title analysis): {len(confirmed_non_ean)}")
print("="*80)

# Save results
confirmed_exact_ean_df = pd.DataFrame(confirmed_exact_ean)
excluded_exact_ean_df = pd.DataFrame(excluded_exact_ean)

confirmed_exact_ean_df.to_csv('confirmed_exact_ean.csv', index=False)
confirmed_non_ean_df.to_csv('confirmed_non_ean.csv', index=False)
excluded_exact_ean_df.to_csv('excluded_exact_ean.csv', index=False)

print("\nResults saved to:")
print("  - confirmed_exact_ean.csv")
print("  - confirmed_non_ean.csv")
print("  - excluded_exact_ean.csv")
