import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

# Clean EANs
df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)

def gtin_checksum_ok(digits):
    if not digits.isdigit():
        return False
    n = len(digits)
    if n not in (8, 12, 13, 14):
        return False
    body = digits[:-1]
    check = int(digits[-1])
    body_rev = list(map(int, body[::-1]))
    total = sum(d * (3 if i % 2 == 1 else 1) for i, d in enumerate(body_rev, start=1))
    calc = (10 - (total % 10)) % 10
    return calc == check

def normalize_ean(digits):
    if not digits.isdigit():
        return digits
    if len(digits) in (8, 12, 13, 14) and gtin_checksum_ok(digits):
        return digits
    for target_len in [12, 13, 14]:
        if len(digits) < target_len:
            padded = digits.zfill(target_len)
            if gtin_checksum_ok(padded):
                return padded
    return digits

def is_strict_valid_barcode(digits):
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

df['EAN_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
df['EAN_strict_valid'] = df['EAN_normalized'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_normalized'].apply(is_strict_valid_barcode)
df['is_exact_ean_strict'] = (
    df['EAN_strict_valid'] & 
    df['EAN_OnPage_strict_valid'] & 
    (df['EAN_normalized'] == df['EAN_OnPage_normalized'])
)

# Count
strict_matches = df[df['is_exact_ean_strict']]
print(f'STRICT EAN matches: {len(strict_matches)}')
print()

# Also check basic matches
def is_basic_match(row):
    ean = row['EAN_digits']
    ean_amz = row['EAN_OnPage_digits']
    if not ean or not ean_amz or ean == 'nan' or ean_amz == 'nan':
        return False
    return ean == ean_amz

df['is_basic_match'] = df.apply(is_basic_match, axis=1)
basic_matches = df[df['is_basic_match']]

print(f'BASIC EAN matches: {len(basic_matches)}')
print()

# Find ones that are basic match but NOT strict match
missing = df[(df['is_basic_match']) & (~df['is_exact_ean_strict'])]
print(f'Missing from strict (basic match but NOT strict): {len(missing)}')
print()

for idx, row in missing.iterrows():
    ean = row['EAN_digits']
    ean_norm = row['EAN_normalized']
    ean_valid = row['EAN_strict_valid']
    amz_ean = row['EAN_OnPage_digits']
    amz_norm = row['EAN_OnPage_normalized']
    amz_valid = row['EAN_OnPage_strict_valid']
    title = str(row.get('SupplierTitle', ''))[:45]
    
    print(f"Title: {title}")
    print(f"  EAN:     {ean} -> normalized: {ean_norm} (valid: {ean_valid})")
    print(f"  AMZ_EAN: {amz_ean} -> normalized: {amz_norm} (valid: {amz_valid})")
    print()
