import pandas as pd
import re

df = pd.read_csv(r'input_data_all_linking.csv')

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    if isinstance(x, float):
        return str(int(x))
    s = str(x).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_clean'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_to_digits)

# STRICT match - NO padding, raw digits must be identical
df['strict_raw_match'] = (df['EAN_clean'] != '') & (df['EAN_OnPage_clean'] != '') & (df['EAN_clean'] == df['EAN_OnPage_clean'])

print(f"Strict RAW EAN matches (no padding): {df['strict_raw_match'].sum()}")

# Show examples where normalization might create false matches
df['len_ean'] = df['EAN_clean'].apply(len)
df['len_amz'] = df['EAN_OnPage_clean'].apply(len)
df['len_diff'] = abs(df['len_ean'] - df['len_amz'])

# Find rows where EANs have different lengths
diff_len = df[(df['EAN_clean'] != '') & (df['EAN_OnPage_clean'] != '') & (df['EAN_clean'] != df['EAN_OnPage_clean']) & (df['len_diff'] <= 2) & (df['len_diff'] > 0)]
print(f"Rows with EANs of different lengths (1-2 digit diff): {len(diff_len)}")

# Check if padding would make them match
def would_match_after_padding(row):
    ean = row['EAN_clean']
    amz = row['EAN_OnPage_clean']
    if len(ean) < len(amz):
        return ean.zfill(len(amz)) == amz
    else:
        return amz.zfill(len(ean)) == ean

diff_len['would_match'] = diff_len.apply(would_match_after_padding, axis=1)
false_matches = diff_len[diff_len['would_match']]
print(f"FALSE MATCHES created by left-padding: {len(false_matches)}")

# Show examples
if len(false_matches) > 0:
    print("\nExamples of FALSE MATCHES from padding:")
    for _, row in false_matches.head(10).iterrows():
        print(f"  Supplier EAN: {row['EAN_clean']} ({len(row['EAN_clean'])} digits)")
        print(f"  Amazon EAN:   {row['EAN_OnPage_clean']} ({len(row['EAN_OnPage_clean'])} digits)")
        print(f"  Supplier Title: {str(row['SupplierTitle'])[:50]}")
        print(f"  Amazon Title: {str(row['AmazonTitle'])[:50]}")
        print()
