"""
Deep Analysis: High-profit products not matched by brand or EAN
"""
import pandas as pd
import re
from difflib import SequenceMatcher

# Load data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')
df['RowID'] = df.index + 1

# Clean & prep
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)
df['Sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
df['Profit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
df['ROI'] = pd.to_numeric(df['ROI'], errors='coerce').fillna(0)

# Brands
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
    if sup_brand:
        return sup_brand.upper() in str(amz_title).upper()
    return False

def basic_ean_match(row):
    e1 = str(row['EAN_clean']).strip()
    e2 = str(row['EAN_OnPage_clean']).strip()
    if not e1 or not e2 or e1 == 'nan' or e2 == 'nan':
        return False
    return e1 == e2

df['basic_ean_match'] = df.apply(basic_ean_match, axis=1)
df['Brand_Match'] = df.apply(lambda x: brands_match(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['Supplier_Brand'] = df['SupplierTitle'].apply(extract_brand)

def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_sim'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# Find high-profit products NOT already matched
high_profit_unmatched = df[
    (df['Profit'] > 5) & 
    (df['Brand_Match'] == False) & 
    (df['basic_ean_match'] == False) &
    (df['Sales'] >= 50)
].sort_values(['Profit'], ascending=False)

print("=" * 100)
print("HIGH-PROFIT PRODUCTS (>£5) NOT MATCHED BY BRAND OR EAN (with Sales >= 50)")
print("=" * 100)
print(f"Total count: {len(high_profit_unmatched)}")
print()

# Manual review - these need human analysis
print("TOP 50 FOR MANUAL REVIEW:")
print("-" * 100)
for idx, row in high_profit_unmatched.head(50).iterrows():
    sup_title = str(row['SupplierTitle'])[:50]
    amz_title = str(row['AmazonTitle'])[:55]
    ean_match_status = "EAN" if row['basic_ean_match'] else "-"
    brand = row['Supplier_Brand'] or '-'
    print(f"Row {row['RowID']:4d} | £{row['Profit']:7.2f} | S:{int(row['Sales']):4d} | Sim:{row['title_sim']:.0%} | {sup_title}")
    print(f"       AMZ: {amz_title}")
    print()

# Look for potential brand matches we might have missed
print("\n" + "=" * 100)
print("PRODUCTS WHERE SUPPLIER HAS KNOWN BRAND BUT AMZ TITLE DOESN'T MATCH")
print("=" * 100)

has_brand_no_match = df[
    (df['Supplier_Brand'].notna()) & 
    (df['Brand_Match'] == False) & 
    (df['Profit'] > 2) &
    (df['Sales'] >= 100)
].sort_values('Profit', ascending=False)

print(f"Count: {len(has_brand_no_match)}")
print()
for idx, row in has_brand_no_match.head(25).iterrows():
    sup_title = str(row['SupplierTitle'])[:45]
    amz_title = str(row['AmazonTitle'])[:50]
    brand = row['Supplier_Brand']
    print(f"Row {row['RowID']:4d} | Brand: {brand:12s} | £{row['Profit']:6.2f} | {sup_title}")
    print(f"       AMZ: {amz_title}")
    print()
