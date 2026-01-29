"""
Comprehensive Sweep: Find potentially missed products
"""
import pandas as pd
import re
from difflib import SequenceMatcher

# Load the data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')
df['RowID'] = df.index + 1

# Clean EANs
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# Sales
df['Sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
df['Profit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)

# Known brands for matching
KNOWN_BRANDS = [
    'EUROWRAP', 'DLUX', 'MINKY', 'STARWASH', 'STATUS', 'CHEF AID', 'PROKLEEN', 'TALA',
    'PRIMA', 'PANASONIC', 'AIRWICK', 'FAIRY', 'DUNLOP', 'DEKTON', 'BETTINA', 'ABBEY',
    'LYNWOOD', 'SECURPAK', 'APAC', 'PALOMA', 'MASON', 'GIFTMAKER', 'KOOPMAN', 'PYREX',
    'PUREBREED', 'BEAUFORT', 'KILROCK', 'SOUDAL', 'EVERBUILD', 'ROLSON', 'AMTECH',
    'DRAPER', 'HARRIS', 'EXTRASTAR', 'MARIGOLD', 'DETTOL', 'ROUNDUP', 'TIDYZ',
    'MASON CASH', 'BLUE CANYON', 'PAN AROMA', 'BRIGHT & HOMELY', 'COUNTRY CLUB',
    'AIR WICK', 'GLADE', 'FEBREZE', 'VANISH', 'FINISH', 'SCHOTT ZWIESEL',
    'PRICE & KENSINGTON', 'WHAM', 'BACOFOIL', 'HIGHLAND', 'RENTOKIL', 'SABICHI',
    'APOLLO', 'WENKEN', 'QUEST', 'DAEWOO', 'BLACKSPUR', 'KINGAVON'
]

# Check for ALL EAN matches
def basic_ean_match(row):
    e1 = str(row['EAN_clean']).strip()
    e2 = str(row['EAN_OnPage_clean']).strip()
    if not e1 or not e2 or e1 == 'nan' or e2 == 'nan':
        return False
    return e1 == e2

df['basic_ean_match'] = df.apply(basic_ean_match, axis=1)

# Brand extraction
def extract_brand(title):
    if pd.isna(title):
        return None
    title_upper = str(title).upper()
    for brand in KNOWN_BRANDS:
        if brand.upper() in title_upper:
            return brand
    return None

def brands_match(sup_title, amz_title):
    sup_brand = extract_brand(sup_title)
    amz_brand = extract_brand(amz_title)
    if sup_brand and amz_brand:
        return sup_brand.upper() == amz_brand.upper()
    if sup_brand:
        return sup_brand.upper() in str(amz_title).upper()
    return False

df['Brand_Match'] = df.apply(lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)

# Title similarity
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_sim'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# === ANALYSIS ===

print("=" * 80)
print("COMPREHENSIVE SWEEP: POTENTIALLY MISSED PRODUCTS")
print("=" * 80)

# 1. All EAN matches
ean_matches = df[df['basic_ean_match'] == True]
print(f"\n1. TOTAL EAN MATCHES FOUND: {len(ean_matches)}")
print("-" * 60)
for idx, row in ean_matches.head(50).iterrows():
    sup_title = str(row['SupplierTitle'])[:45]
    print(f"Row {row['RowID']:4d}: {sup_title:45s} | Profit: £{row['Profit']:6.2f} | Sales: {int(row['Sales']):4d}")

# 2. Brand matches NOT in EAN matches with high profit
brand_only = df[(df['Brand_Match'] == True) & (df['basic_ean_match'] == False) & (df['Profit'] > 1)]
brand_only = brand_only.sort_values('Profit', ascending=False)
print(f"\n2. BRAND MATCHES (No EAN) WITH PROFIT > £1: {len(brand_only)}")
print("-" * 60)
for idx, row in brand_only.head(40).iterrows():
    sup_title = str(row['SupplierTitle'])[:40]
    brand = row['Supplier_Brand'] or 'N/A'
    print(f"Row {row['RowID']:4d}: [{brand:12s}] {sup_title:40s} | £{row['Profit']:6.2f} | S:{int(row['Sales']):4d}")

# 3. High title similarity (>0.5) without brand match
high_sim = df[(df['title_sim'] >= 0.5) & (df['Brand_Match'] == False) & (df['basic_ean_match'] == False) & (df['Profit'] > 0.5)]
high_sim = high_sim.sort_values('title_sim', ascending=False)
print(f"\n3. HIGH TITLE SIMILARITY (>50%) WITHOUT BRAND MATCH: {len(high_sim)}")
print("-" * 60)
for idx, row in high_sim.head(20).iterrows():
    sup_title = str(row['SupplierTitle'])[:35]
    amz_title = str(row['AmazonTitle'])[:35]
    print(f"Row {row['RowID']:4d}: {sup_title:35s} vs {amz_title:35s} | Sim: {row['title_sim']:.0%}")

# 4. Very high profit products (>£10) not yet categorized
high_profit = df[(df['Profit'] > 10) & (df['Brand_Match'] == False) & (df['basic_ean_match'] == False)]
high_profit = high_profit.sort_values('Profit', ascending=False)
print(f"\n4. HIGH PROFIT (>£10) NOT BRAND/EAN MATCHED: {len(high_profit)}")
print("-" * 60)
for idx, row in high_profit.head(20).iterrows():
    sup_title = str(row['SupplierTitle'])[:40]
    amz_title = str(row['AmazonTitle'])[:40]
    print(f"Row {row['RowID']:4d}: {sup_title:40s} | £{row['Profit']:6.2f} | S:{int(row['Sales']):4d}")
    print(f"         AMZ: {amz_title}")

# 5. Products with known brands that weren't detected
print(f"\n5. SUMMARY STATISTICS")
print("-" * 60)
print(f"Total rows: {len(df)}")
print(f"EAN matches: {len(df[df['basic_ean_match'] == True])}")
print(f"Brand matches (no EAN): {len(df[(df['Brand_Match'] == True) & (df['basic_ean_match'] == False)])}")
print(f"Title sim > 40%: {len(df[df['title_sim'] >= 0.4])}")
print(f"Title sim > 50%: {len(df[df['title_sim'] >= 0.5])}")
print(f"Products with Profit > 0: {len(df[df['Profit'] > 0])}")
print(f"Products with Profit > £5: {len(df[df['Profit'] > 5])}")
print(f"Products with Profit > £10: {len(df[df['Profit'] > 10])}")

# Save to file
output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\opu v1.1\_missed_products_sweep.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("COMPREHENSIVE SWEEP: POTENTIALLY MISSED PRODUCTS\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"TOTAL EAN MATCHES: {len(ean_matches)}\n")
    f.write(f"BRAND MATCHES (no EAN, profit>£1): {len(brand_only)}\n")
    f.write(f"HIGH TITLE SIM (>50%, no brand): {len(high_sim)}\n")
    f.write(f"HIGH PROFIT (>£10, unmatched): {len(high_profit)}\n")

print(f"\n\nSweep complete. Results also saved to: _missed_products_sweep.txt")
