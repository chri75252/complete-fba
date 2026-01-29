import pandas as pd
import re

# Load the data
df = pd.read_csv(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\latest codex\input_data_all_linking.csv')

print(f'Total rows: {len(df)}')

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    s = str(x).strip()
    if 'e+' in s.lower() or 'e' in s.lower():
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

def is_strict_valid_barcode(digits):
    if not isinstance(digits, str) or not digits.isdigit():
        return False
    normalized = normalize_ean(digits)
    if len(normalized) not in (8, 12, 13, 14):
        return False
    if re.search(r'0{6,}$', normalized):
        return False
    return gtin_checksum_ok(normalized)

# Process EANs
df['EAN_digits'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_digits'] = df['EAN_OnPage'].apply(clean_to_digits)
df['EAN_digits_normalized'] = df['EAN_digits'].apply(normalize_ean)
df['EAN_OnPage_digits_normalized'] = df['EAN_OnPage_digits'].apply(normalize_ean)
df['EAN_strict_valid'] = df['EAN_digits'].apply(is_strict_valid_barcode)
df['EAN_OnPage_strict_valid'] = df['EAN_OnPage_digits'].apply(is_strict_valid_barcode)

# Exact EAN match
df['is_exact_ean_strict'] = (
    df['EAN_strict_valid']
    & df['EAN_OnPage_strict_valid']
    & (df['EAN_digits_normalized'] == df['EAN_OnPage_digits_normalized'])
)

# Get sales column
sales_col = 'bought_in_past_month' if 'bought_in_past_month' in df.columns else 'Sales'
df['sales'] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)

# Get profit column
df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)

print(f'\nRows with exact EAN match (both valid, checksums OK): {df["is_exact_ean_strict"].sum()}')
print(f'Rows with NetProfit > 0: {(df["NetProfit"] > 0).sum()}')
print(f'Rows with sales > 0: {(df["sales"] > 0).sum()}')

# The key filter
verified_criteria = df['is_exact_ean_strict'] & (df['NetProfit'] > 0) & (df['sales'] > 0)
verified_with_sales = df[verified_criteria]

print(f'\n=== YOUR CRITERIA ===')
print(f'Exact EAN match + NetProfit > 0 + Sales > 0: {len(verified_with_sales)}')

# Check for duplicates by EAN
unique_eans = verified_with_sales['EAN_digits_normalized'].nunique()
print(f'Unique EANs among those: {unique_eans}')

# Drop duplicates by EAN to get truly unique products
deduped = verified_with_sales.drop_duplicates(subset=['EAN_digits_normalized'])
print(f'After removing EAN duplicates: {len(deduped)}')

# Also check ASIN duplicates
unique_asins = verified_with_sales['ASIN'].nunique()
print(f'Unique ASINs among those: {unique_asins}')

deduped_asin = verified_with_sales.drop_duplicates(subset=['ASIN'])
print(f'After removing ASIN duplicates: {len(deduped_asin)}')

# Show breakdown of the 821 VERIFIED in original report
print(f'\n=== BREAKDOWN OF 821 VERIFIED IN REPORT ===')
verified_all = df[df['is_exact_ean_strict'] & (df['NetProfit'] > 0)]
print(f'Total with exact EAN + NetProfit > 0 (regardless of sales): {len(verified_all)}')

verified_with_sales_gt0 = verified_all[verified_all['sales'] > 0]
verified_with_sales_eq0 = verified_all[verified_all['sales'] == 0]
print(f'  - With sales > 0: {len(verified_with_sales_gt0)}')
print(f'  - With sales = 0: {len(verified_with_sales_eq0)}')
