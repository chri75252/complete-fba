import pandas as pd
import numpy as np

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

# Check for strict EAN matches (both present and equal)
def is_valid_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    return True

df['ean_match'] = df.apply(lambda x: is_valid_ean(x['EAN']) and is_valid_ean(x['EAN_OnPage']) and x['EAN_clean'] == x['EAN_OnPage_clean'], axis=1)

print('=== GROUND TRUTH ANALYSIS ===')
print(f'Total rows: {len(df)}')
ean_match_count = df['ean_match'].sum()
print(f'Strict EAN matches (both valid, equal): {ean_match_count}')
print()

# Get all EAN matches
ean_matches = df[df['ean_match'] == True].copy()
ean_matches['row_id'] = ean_matches.index + 1

# Save to CSV for review
output = []
output.append('ROW_ID,EAN,ASIN,NetProfit,Sales,SupplierTitle,AmazonTitle')
for idx, row in ean_matches.iterrows():
    profit = row.get('NetProfit', 0)
    sales = row.get('sales_numeric', 0) if pd.notna(row.get('sales_numeric', None)) else 0
    output.append(f'{idx+1},{row["EAN_clean"]},{row["ASIN"]},{profit},{sales},"{str(row["SupplierTitle"])[:50]}","{str(row["AmazonTitle"])[:50]}"')

print('=== ALL EAN MATCHED PRODUCTS ===')
for line in output:
    print(line)

print()
print('=== EAN MATCH ASINS ===')
for asin in ean_matches['ASIN'].unique():
    print(f'  {asin}')
