"""
Extended Preflight Calibration Analysis Script for part_2_jan.xlsx
"""
import pandas as pd
import re
from collections import Counter

# Load the data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx')

supplier_titles = df['SupplierTitle'].dropna().astype(str).tolist()
amazon_titles = df['AmazonTitle'].dropna().astype(str).tolist()

print("=" * 80)
print("EXTENDED PATTERN ANALYSIS")
print("=" * 80)

# 1. Trailing numbers
print("\n=== TRAILING NUMBER ANALYSIS ===")
trailing_nums = []
for i, title in enumerate(supplier_titles):
    match = re.search(r'\s(\d{1,4})$', title)
    if match:
        trailing_nums.append((i, title, match.group(1)))

print(f"Total titles with trailing numbers: {len(trailing_nums)}")
print("\nSamples:")
for idx, title, num in trailing_nums[:25]:
    print(f"  Row {idx}: '{title}' -> trailing '{num}'")

# 2. PIECES/PCS/PCE patterns
print("\n\n=== PIECES/PCS/PCE PATTERNS ===")
pieces_pattern = r'\b(\d+)\s*(pieces?|pcs?|pce)\b'
pieces_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(pieces_pattern, title, re.IGNORECASE)
    if m:
        pieces_matches.append((i, title, m.group()))

print(f"Total with PIECES/PCS/PCE: {len(pieces_matches)}")
for idx, title, pattern in pieces_matches[:20]:
    print(f"  Row {idx}: '{pattern}' in '{title}'")

# 3. PACK/PK patterns
print("\n\n=== PACK/PK PATTERNS ===")
pack_pattern = r'\b(\d+)\s*(pack|pk)\b|\b(pack|pk)\s*(\d+)\b'
pack_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(pack_pattern, title, re.IGNORECASE)
    if m:
        pack_matches.append((i, title, m.group()))

print(f"Total with PACK/PK: {len(pack_matches)}")
for idx, title, pattern in pack_matches[:20]:
    print(f"  Row {idx}: '{pattern}' in '{title}'")

# 4. Multiplier patterns (NxProduct)
print("\n\n=== MULTIPLIER PATTERNS (N x ...) ===")
multi_pattern = r'\b(\d+)\s*x\s*(\d+)?(m|ml|g|l|cm|mm|pk|pack)?'
multi_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(multi_pattern, title, re.IGNORECASE)
    if m:
        multi_matches.append((i, title, m.group()))

print(f"Total with multiplier patterns: {len(multi_matches)}")
for idx, title, pattern in multi_matches[:15]:
    print(f"  Row {idx}: '{pattern}' in '{title}'")

# 5. Capacity patterns in Amazon titles
print("\n\n=== AMAZON CAPACITY PATTERNS ===")
cap_pattern = r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|cl|kg|oz)'
cap_matches = []
for i, title in enumerate(amazon_titles):
    m = re.search(cap_pattern, title, re.IGNORECASE)
    if m:
        cap_matches.append((i, title[:100], m.group()))

print(f"Total capacity multipacks found: {len(cap_matches)}")
for idx, title, pattern in cap_matches[:15]:
    print(f"  Row {idx}: '{pattern}' in '{title}...'")

# 6. Extract all unique brands from supplier titles (first word analysis)
print("\n\n=== FIRST WORD FREQUENCY (potential brands) ===")
first_words = Counter()
for title in supplier_titles:
    words = title.split()
    if words:
        first_words[words[0].upper()] += 1

print("Top 30 first words (likely brands):")
for word, count in first_words.most_common(30):
    print(f"  {word}: {count} occurrences")

# 7. Pattern: Word followed by number (PRODUCT 100, PRODUCT 50, etc.)
print("\n\n=== WORD + TRAILING NUMBER PATTERNS ===")
word_num_pattern = r'([A-Z]+)\s+(\d{2,4})$'
word_num_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(word_num_pattern, title, re.IGNORECASE)
    if m:
        word_num_matches.append((i, title, m.group(1), m.group(2)))

print(f"Total matches: {len(word_num_matches)}")
for idx, title, word, num in word_num_matches[:20]:
    print(f"  Row {idx}: '{word} {num}' in '{title}'")

# 8. Check for "CASES" pattern (special for cupcake etc)
print("\n\n=== CASES PATTERN ===")
cases_pattern = r'(\d+)\s*cases?'
cases_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(cases_pattern, title, re.IGNORECASE)
    if m:
        cases_matches.append((i, title, m.group()))

print(f"Total with CASES: {len(cases_matches)}")
for idx, title, pattern in cases_matches[:15]:
    print(f"  Row {idx}: '{pattern}' in '{title}'")

# 9. SCOURER pattern (number + product type)
print("\n\n=== NUMBER BEFORE PRODUCT TYPE ===")
num_product_pattern = r'\b(\d+)\s+(scourer|sponge|napkin|plate|pegs?|bag|brush|hook|bell|screw|ball)\w*'
np_matches = []
for i, title in enumerate(supplier_titles):
    m = re.search(num_product_pattern, title, re.IGNORECASE)
    if m:
        np_matches.append((i, title, m.group()))

print(f"Total matches: {len(np_matches)}")
for idx, title, pattern in np_matches[:15]:
    print(f"  Row {idx}: '{pattern}' in '{title}'")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
