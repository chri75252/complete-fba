import pandas as pd
import re

df = pd.read_csv('PART_DEC_31.csv', nrows=50, encoding='utf-8-sig')

print('=== ADDITIONAL PATTERN ANALYSIS ===\n')

# Check for shorthand patterns like PC, PK, etc.
shorthand_patterns = []
for i, title in enumerate(df['SupplierTitle'].dropna()):
    title_str = str(title).upper()
    # Look for patterns like 2PC, 6PK, 8PC, etc.
    matches = re.findall(r'(\d+)\s*(PC|PK|PCE|PCS)(?:\s|$)', title_str)
    if matches:
        shorthand_patterns.append((i, title_str, matches))

print('Shorthand unit patterns (XPC, XPK, etc.):')
for idx, title, matches in shorthand_patterns:
    print(f'  Row {idx}: "{title}"')
    print(f'    Found: {matches}')
print(f'\nTotal shorthand patterns: {len(shorthand_patterns)}')

# Check for 'EACH' notation
each_patterns = []
for i, title in enumerate(df['SupplierTitle'].dropna()):
    title_str = str(title).upper()
    if 'EACH' in title_str:
        each_patterns.append((i, title_str))

print(f'\n"EACH" patterns: {len(each_patterns)}')
for idx, title in each_patterns:
    print(f'  Row {idx}: "{title}"')

# Check for cases/box patterns
case_patterns = []
for i, title in enumerate(df['SupplierTitle'].dropna()):
    title_str = str(title).upper()
    if 'CASES' in title_str or 'BOX' in title_str or 'PACK' in title_str:
        case_patterns.append((i, title_str))

print(f'\nCASES/BOX/PACK patterns: {len(case_patterns)}')
for idx, title in case_patterns:
    print(f'  Row {idx}: "{title}"')

# Count dimension format usage (with space vs without)
with_space = 0
without_space = 0
for title in df['SupplierTitle'].dropna():
    title_str = str(title).upper()
    if re.search(r'\d+\s+(CM|MM|ML|G|KG|L|LTR|OZ|INCH)', title_str):
        with_space += 1
    elif re.search(r'\d+(CM|MM|ML|G|KG|L|LTR|OZ|INCH)', title_str):
        without_space += 1

print(f'\n=== DIMENSION FORMAT ===')
print(f'With space (e.g., "50 CM"): {with_space}')
print(f'Without space (e.g., "50CM"): {without_space}')
