"""
Find genuinely missed products where titles actually match
"""
import pandas as pd
from difflib import SequenceMatcher

# Load data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')
df['RowID'] = df.index + 1
df['Sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)
df['Profit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)

# Title similarity
def title_similarity(title1, title2):
    if pd.isna(title1) or pd.isna(title2):
        return 0.0
    return SequenceMatcher(None, str(title1).lower(), str(title2).lower()).ratio()

df['title_sim'] = df.apply(lambda x: title_similarity(x['SupplierTitle'], x['AmazonTitle']), axis=1)

# Extract keywords from title
def extract_keywords(title):
    if pd.isna(title):
        return set()
    title = str(title).upper()
    # Remove common words
    stopwords = {'THE', 'A', 'AN', 'AND', 'OR', 'WITH', 'FOR', 'OF', 'IN', 'ON', 'TO'}
    words = set(title.split()) - stopwords
    return words

def keyword_overlap(title1, title2):
    kw1 = extract_keywords(title1)
    kw2 = extract_keywords(title2)
    if not kw1 or not kw2:
        return 0, 0
    overlap = len(kw1 & kw2)
    return overlap, len(kw1)

df['keyword_data'] = df.apply(lambda x: keyword_overlap(x['SupplierTitle'], x['AmazonTitle']), axis=1)
df['keyword_overlap'] = df['keyword_data'].apply(lambda x: x[0])
df['keyword_total'] = df['keyword_data'].apply(lambda x: x[1])
df['keyword_ratio'] = df.apply(lambda x: x['keyword_overlap'] / x['keyword_total'] if x['keyword_total'] > 0 else 0, axis=1)

print("=" * 100)
print("GENUINE MATCHES: HIGH KEYWORD OVERLAP + HIGH TITLE SIM")
print("=" * 100)

# Find products with high keyword overlap (>3 shared words) and high similarity
genuine_matches = df[
    (df['keyword_overlap'] >= 3) &
    (df['title_sim'] >= 0.4) &
    (df['Profit'] > 0.5) &
    (df['Sales'] >= 50)
].sort_values(['keyword_overlap', 'title_sim'], ascending=[False, False])

print(f"Count: {len(genuine_matches)}")
print()
print("TOP GENUINE MATCHES FOR REVIEW:")
print("-" * 100)
for idx, row in genuine_matches.head(40).iterrows():
    sup_title = str(row['SupplierTitle'])[:45]
    amz_title = str(row['AmazonTitle'])[:45]
    print(f"Row {row['RowID']:4d} | KW:{row['keyword_overlap']:2d} | Sim:{row['title_sim']:.0%} | £{row['Profit']:6.2f} | S:{int(row['Sales']):4d}")
    print(f"  SUP: {sup_title}")
    print(f"  AMZ: {amz_title}")
    print()

# Find HIGH-PROFIT products where Amazon title contains key supplier words
print("\n" + "=" * 100)
print("HIGH-PROFIT PRODUCTS WHERE AMZ TITLE CONTAINS SUPPLIER KEYWORDS")
print("=" * 100)

def amz_contains_supplier_words(row):
    sup = str(row['SupplierTitle']).upper() if pd.notna(row['SupplierTitle']) else ''
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ''
    
    # Key product words to check
    sup_words = sup.split()[:5]  # First 5 words
    matches = 0
    for word in sup_words:
        if len(word) > 3 and word in amz:
            matches += 1
    return matches

df['key_word_match'] = df.apply(amz_contains_supplier_words, axis=1)

keyword_matches = df[
    (df['key_word_match'] >= 2) &
    (df['Profit'] > 2) &
    (df['Sales'] >= 100)
].sort_values('Profit', ascending=False)

print(f"Count: {len(keyword_matches)}")
print()
for idx, row in keyword_matches.head(30).iterrows():
    sup_title = str(row['SupplierTitle'])[:50]
    amz_title = str(row['AmazonTitle'])[:50]
    print(f"Row {row['RowID']:4d} | KW:{row['key_word_match']} | £{row['Profit']:6.2f} | S:{int(row['Sales']):4d}")
    print(f"  SUP: {sup_title}")
    print(f"  AMZ: {amz_title}")
    print()

# Summary
print("\n" + "=" * 100)
print("SUMMARY OF POTENTIALLY MISSED PRODUCTS")
print("=" * 100)
print(f"Products with >=3 keyword overlap + >=40% sim: {len(genuine_matches)}")
print(f"Products with >=2 key word matches (high profit): {len(keyword_matches)}")
