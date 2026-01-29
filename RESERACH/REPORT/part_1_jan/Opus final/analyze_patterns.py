import pandas as pd
import re
import sys

# Redirect output to file
outfile = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\Opus final\pattern_output.txt'
sys.stdout = open(outfile, 'w', encoding='utf-8')

# Load the data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')

print("=" * 60)
print("DIMENSION PATTERNS IN SUPPLIER TITLES")
print("=" * 60)

dim_patterns = {
    'cm': [], 'mm': [], 'ml': [], 'ltr': [], 'g_gram': [], 'kg': [], 'oz': [], 'inch': []
}

for idx, title in enumerate(df['SupplierTitle'].dropna().tolist()[:500]):
    title_str = str(title).upper()
    if re.search(r'\d+\s*CM', title_str): dim_patterns['cm'].append((idx, title))
    if re.search(r'\d+\s*MM(?!X)', title_str): dim_patterns['mm'].append((idx, title))
    if re.search(r'\d+\s*ML', title_str): dim_patterns['ml'].append((idx, title))
    if re.search(r'\d+\s*LTR', title_str): dim_patterns['ltr'].append((idx, title))
    if re.search(r'\d+\s*G(?:\s|$)', title_str): dim_patterns['g_gram'].append((idx, title))
    if re.search(r'\d+\s*KG', title_str): dim_patterns['kg'].append((idx, title))
    if re.search(r'\d+\s*OZ', title_str): dim_patterns['oz'].append((idx, title))
    if re.search(r'\d+\s*(?:INCH|IN["\']?)', title_str): dim_patterns['inch'].append((idx, title))

for pattern, items in dim_patterns.items():
    print(f"\n{pattern.upper()}: {len(items)} occurrences")
    for idx, title in items[:5]:
        print(f"  Row {idx}: {title[:90]}")

print("\n" + "=" * 60)
print("CAPACITY MULTIPACK PATTERNS IN AMAZON TITLES (N x NNml)")
print("=" * 60)

cap_patterns = []
for idx, title in enumerate(df['AmazonTitle'].dropna().tolist()[:500]):
    title_str = str(title)
    match = re.search(r'(\d+)\s*[Xx]\s*\d+\s*(ml|g|l|cl|oz)', title_str, re.IGNORECASE)
    if match:
        cap_patterns.append((idx, title[:90], match.group()))

print(f"\nFound {len(cap_patterns)} capacity multipack patterns:")
for idx, title, pattern in cap_patterns[:15]:
    print(f"  Row {idx}: Pattern='{pattern}' in: {title}")

print("\n" + "=" * 60)
print("BRAND POSITION ANALYSIS")
print("=" * 60)

# Common supplier brands based on the titles
known_brands = ['CHEF AID', 'DLUX', 'TALA', 'MINKY', 'BETTINA', 'PRIMA', 'PYREX', 'DEKTON', 
                'ROLSON', 'APAC', 'OPAL', 'FAIRY', 'AIRWICK', 'PALOMA', 'EUROWRAP', 'APOLLO',
                'LYNWOOD', 'ABBEY', 'STARWASH', 'PROKLEEN', 'BRIGHT', 'GLEAMAX', 'STATUS',
                'PANASONIC', 'DUNLOP', 'BLACKSPUR', 'SOUDAL', 'PPS', 'BBQ', 'GIFTMAKER']

brand_at_start = 0
brand_middle = 0
brand_at_end = 0

for idx, title in enumerate(df['SupplierTitle'].dropna().tolist()[:300]):
    title_upper = str(title).upper()
    for brand in known_brands:
        if brand in title_upper:
            # Check position
            pos = title_upper.find(brand)
            title_len = len(title_upper)
            if pos == 0 or pos <= 5:
                brand_at_start += 1
            elif pos > title_len - len(brand) - 5:
                brand_at_end += 1
            else:
                brand_middle += 1
            break

print(f"\nBrand at START: {brand_at_start}")
print(f"Brand in MIDDLE: {brand_middle}")
print(f"Brand at END: {brand_at_end}")

print("\n" + "=" * 60)
print("SALES COLUMN ANALYSIS")
print("=" * 60)

sales_col = 'bought_in_past_month'
print(f"\nSales column: {sales_col}")
print(f"Data type: {df[sales_col].dtype}")
print(f"Sample values: {df[sales_col].head(10).tolist()}")
print(f"Contains text that needs parsing: {df[sales_col].dtype == 'object'}")
