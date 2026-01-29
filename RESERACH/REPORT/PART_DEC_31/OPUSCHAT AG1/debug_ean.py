"""
Debug: Compare EAN matches between old and new datasets
Find missing EAN matches
"""
import pandas as pd
import re

# Load both datasets
df_old = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx')
df_new = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

print("="*80)
print("DATASET COMPARISON")
print("="*80)
print(f"OLD dataset (part_30_dec.xlsx): {len(df_old)} rows")
print(f"NEW dataset (PART_DEC_31.xlsx): {len(df_new)} rows")
print()

# Clean EANs
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip().replace('.0', '')
    return re.sub(r'\D', '', s)

df_old['EAN_clean'] = df_old['EAN'].apply(clean_ean)
df_old['EAN_OnPage_clean'] = df_old['EAN_OnPage'].apply(clean_ean)
df_new['EAN_clean'] = df_new['EAN'].apply(clean_ean)
df_new['EAN_OnPage_clean'] = df_new['EAN_OnPage'].apply(clean_ean)

# Find basic matches (EAN = EAN_OnPage, both non-empty)
def is_basic_match(row):
    ean = row['EAN_clean']
    ean_amz = row['EAN_OnPage_clean']
    if not ean or not ean_amz:
        return False
    if ean == 'nan' or ean_amz == 'nan':
        return False
    return ean == ean_amz

df_old['is_match'] = df_old.apply(is_basic_match, axis=1)
df_new['is_match'] = df_new.apply(is_basic_match, axis=1)

old_matches = df_old[df_old['is_match']]
new_matches = df_new[df_new['is_match']]

print(f"OLD EAN matches (basic): {len(old_matches)}")
print(f"NEW EAN matches (basic): {len(new_matches)}")
print()

# Get the EANs that match
old_matching_eans = set(old_matches['EAN_clean'].tolist())
new_matching_eans = set(new_matches['EAN_clean'].tolist())

# Find EANs in old but NOT in new
missing_eans = old_matching_eans - new_matching_eans
new_eans = new_matching_eans - old_matching_eans
common_eans = old_matching_eans & new_matching_eans

print(f"Common EANs in both: {len(common_eans)}")
print(f"EANs in OLD but missing from NEW matches: {len(missing_eans)}")
print(f"NEW EANs not in OLD: {len(new_eans)}")
print()

if missing_eans:
    print("="*80)
    print("MISSING EANS (in OLD matches but NOT in NEW matches):")
    print("="*80)
    for ean in list(missing_eans)[:20]:
        old_row = df_old[df_old['EAN_clean'] == ean].iloc[0]
        title = str(old_row.get('SupplierTitle', ''))[:50]
        profit = old_row.get('NetProfit', 0)
        
        # Check if this EAN exists in new dataset at all
        new_rows_with_ean = df_new[df_new['EAN_clean'] == ean]
        if len(new_rows_with_ean) > 0:
            new_row = new_rows_with_ean.iloc[0]
            new_amz_ean = new_row['EAN_OnPage_clean']
            status = f"EAN exists but AMZ_EAN={new_amz_ean}"
        else:
            status = "EAN NOT IN NEW DATASET"
        
        print(f"EAN: {ean} | Profit: {profit:.2f} | {title}")
        print(f"   Status: {status}")
        print()

if new_eans:
    print()
    print("="*80)
    print("NEW EANS (in NEW matches but NOT in OLD):")
    print("="*80)
    for ean in list(new_eans)[:10]:
        new_row = df_new[df_new['EAN_clean'] == ean].iloc[0]
        title = str(new_row.get('SupplierTitle', ''))[:50]
        profit = new_row.get('NetProfit', 0)
        print(f"EAN: {ean} | Profit: {profit:.2f} | {title}")

# Also check: are some EANs in new dataset but with different AMZ_EAN?
print()
print("="*80)
print("CHECKING: OLD matching EANs that exist in NEW but don't match:")
print("="*80)
for ean in list(old_matching_eans)[:50]:
    new_rows = df_new[df_new['EAN_clean'] == ean]
    if len(new_rows) > 0:
        new_row = new_rows.iloc[0]
        new_amz = new_row['EAN_OnPage_clean']
        if ean != new_amz:
            old_row = df_old[df_old['EAN_clean'] == ean].iloc[0]
            old_amz = old_row['EAN_OnPage_clean']
            title = str(old_row.get('SupplierTitle', ''))[:45]
            print(f"EAN: {ean}")
            print(f"  OLD AMZ_EAN: {old_amz} (MATCHED)")
            print(f"  NEW AMZ_EAN: {new_amz} (NO MATCH)")
            print(f"  Title: {title}")
            print()
