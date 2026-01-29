import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

# Clean EANs
def clean_ean(x):
    if pd.isna(x):
        return ''
    s = str(x).strip().replace('.0', '')
    return re.sub(r'\D', '', s)

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# Basic match
def is_basic_match(row):
    ean = row['EAN_clean']
    ean_amz = row['EAN_OnPage_clean']
    if not ean or not ean_amz:
        return False
    if ean == 'nan' or ean_amz == 'nan':
        return False
    return ean == ean_amz

df['is_match'] = df.apply(is_basic_match, axis=1)
matches = df[df['is_match']]

print(f'Basic EAN matches: {len(matches)}')
print()

# Check checksum for each
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

checksum_pass = 0
checksum_fail = 0

for idx, row in matches.iterrows():
    ean = row['EAN_clean']
    title = str(row.get('SupplierTitle', ''))[:45]
    checksum_ok = gtin_checksum_ok(ean)
    length = len(ean)
    status = 'OK' if checksum_ok else 'FAIL'
    if checksum_ok:
        checksum_pass += 1
    else:
        checksum_fail += 1
    print(f'{ean} (len={length}) [{status}] | {title}')

print()
print(f'Checksum PASS: {checksum_pass}')
print(f'Checksum FAIL: {checksum_fail}')
