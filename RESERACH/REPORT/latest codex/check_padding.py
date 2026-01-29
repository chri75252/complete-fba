import pandas as pd
import re

df = pd.read_csv(r'input_data_all_linking.csv')

# Check specific EANs the user mentioned
eans_to_check = [
    '026102251102',  # CARAFE
    '026102105061',  # ASPEN BOWL
    '011179826872',  # HAPPY 13TH
    '076171101556',  # LITTLE TREES
    '051131659889',  # COMMAND POSTER
    '011179633784',  # HONEYCOMB GARLAND
]

print("=== CHECKING FOR LEFT-PADDED EANs ===\n")

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

for ean in eans_to_check:
    ean_no_leading_zero = ean.lstrip('0')
    
    # Check if this EAN exists in CSV (with or without leading zero)
    matches_with_zero = df[df['EAN_clean'] == ean]
    matches_without_zero = df[df['EAN_clean'] == ean_no_leading_zero]
    
    print(f"EAN: {ean}")
    print(f"  With leading zero ({ean}): {len(matches_with_zero)} rows")
    print(f"  Without leading zero ({ean_no_leading_zero}): {len(matches_without_zero)} rows")
    
    if len(matches_without_zero) > 0:
        row = matches_without_zero.iloc[0]
        print(f"  CSV EAN value: {row['EAN_clean']}")
        print(f"  CSV EAN_OnPage: {row['EAN_OnPage_clean']}")
        print(f"  Title: {str(row['SupplierTitle'])[:60]}")
    elif len(matches_with_zero) > 0:
        row = matches_with_zero.iloc[0]
        print(f"  CSV EAN value: {row['EAN_clean']}")
        print(f"  CSV EAN_OnPage: {row['EAN_OnPage_clean']}")
        print(f"  Title: {str(row['SupplierTitle'])[:60]}")
    print()

# Now check ALL EANs that start with 0 in the report but not in CSV
print("\n=== ALL EANs WHERE NORMALIZATION ADDED LEADING ZERO ===\n")

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

df['EAN_normalized'] = df['EAN_clean'].apply(normalize_ean)
df['EAN_OnPage_normalized'] = df['EAN_OnPage_clean'].apply(normalize_ean)

# Find rows where normalization added leading zeros
df['ean_was_padded'] = (df['EAN_clean'] != '') & (df['EAN_normalized'] != df['EAN_clean'])
df['amz_was_padded'] = (df['EAN_OnPage_clean'] != '') & (df['EAN_OnPage_normalized'] != df['EAN_OnPage_clean'])

print(f"Supplier EANs that got padded: {df['ean_was_padded'].sum()}")
print(f"Amazon EANs that got padded: {df['amz_was_padded'].sum()}")

# Check if any padded EANs created matches
df['norm_match'] = (df['EAN_normalized'] != '') & (df['EAN_OnPage_normalized'] != '') & (df['EAN_normalized'] == df['EAN_OnPage_normalized'])
padded_matches = df[df['norm_match'] & (df['ean_was_padded'] | df['amz_was_padded'])]
print(f"VERIFIED matches where padding was involved: {len(padded_matches)}")

if len(padded_matches) > 0:
    print("\nExamples of PADDED matches:")
    for _, row in padded_matches.head(10).iterrows():
        print(f"  Raw Supplier:  {row['EAN_clean']} -> Normalized: {row['EAN_normalized']}")
        print(f"  Raw Amazon:    {row['EAN_OnPage_clean']} -> Normalized: {row['EAN_OnPage_normalized']}")
        print(f"  Title: {str(row['SupplierTitle'])[:60]}")
        print()
