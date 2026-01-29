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

def gtin_checksum_ok(digits):
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = 0
    for i, d in enumerate(body_rev, start=1):
        total += d * (3 if i % 2 == 1 else 1)
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits):
    if not isinstance(digits, str) or not digits.isdigit():
        return digits if isinstance(digits, str) else ''
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

df['EAN_clean'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_to_digits)
df['EAN_normalized'] = df['EAN_clean'].apply(normalize_ean)
df['EAN_OnPage_normalized'] = df['EAN_OnPage_clean'].apply(normalize_ean)

# RAW match
df['raw_match'] = (df['EAN_clean'] != '') & (df['EAN_OnPage_clean'] != '') & (df['EAN_clean'] == df['EAN_OnPage_clean'])

# Normalized match
df['norm_match'] = (df['EAN_normalized'] != '') & (df['EAN_OnPage_normalized'] != '') & (df['EAN_normalized'] == df['EAN_OnPage_normalized'])

print(f"RAW EAN matches: {df['raw_match'].sum()}")
print(f"NORMALIZED EAN matches: {df['norm_match'].sum()}")

# Find rows that match ONLY after normalization (not raw)
df['only_norm_match'] = df['norm_match'] & ~df['raw_match']
print(f"Matches ONLY after normalization: {df['only_norm_match'].sum()}")

# Show examples of these
only_norm = df[df['only_norm_match']]
if len(only_norm) > 0:
    print("\nExamples of matches created by normalization:")
    for _, row in only_norm.head(10).iterrows():
        print(f"  Raw Supplier:  {row['EAN_clean']}")
        print(f"  Raw Amazon:    {row['EAN_OnPage_clean']}")
        print(f"  Norm Supplier: {row['EAN_normalized']}")
        print(f"  Norm Amazon:   {row['EAN_OnPage_normalized']}")
        print(f"  Supplier Title: {str(row['SupplierTitle'])[:50]}")
        print()
