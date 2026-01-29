"""
Preflight Calibration Analysis Script for part_2_jan.xlsx
Analyzes supplier naming conventions, pack patterns, and data anomalies.
"""
import pandas as pd
import re
from collections import Counter

# Load the data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_2_jan\part_2_jan.xlsx')

print("=" * 80)
print("PREFLIGHT CALIBRATION ANALYSIS - part_2_jan.xlsx")
print("=" * 80)
print(f"\nTotal rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# ============================================================================
# TASK 1: PACK QUANTITY PATTERN DETECTION
# ============================================================================
print("\n" + "=" * 80)
print("TASK 1: PACK QUANTITY PATTERN DETECTION")
print("=" * 80)

supplier_titles = df['SupplierTitle'].dropna().astype(str).tolist()
amazon_titles = df['AmazonTitle'].dropna().astype(str).tolist()

# Pattern counters
explicit_units = Counter()
trailing_numbers = []
leading_multipliers = []
dimension_patterns = []

# Explicit unit patterns
unit_patterns = {
    'pcs': r'\b\d+\s*pcs?\b',
    'pce': r'\b\d+\s*pce\b',
    'pk': r'\b(?:pk|pack)\s*\d+\b|\b\d+\s*(?:pk|pack)\b',
    'pack': r'\bpack\s*(?:of\s*)?\d+\b|\b\d+\s*pack\b',
    'unit': r'\b\d+\s*units?\b',
    'x_multiplier': r'\b\d+\s*x\s+\w',  # "10x Product" or "10 x Product"
}

print("\n--- Supplier Title Samples (first 50) ---")
for i, title in enumerate(supplier_titles[:50]):
    print(f"{i:3d}: {title}")

print("\n--- Amazon Title Samples (first 50) ---")
for i, title in enumerate(amazon_titles[:50]):
    print(f"{i:3d}: {title[:150]}...")  # Truncate long titles

# Check for explicit pack units
print("\n\n--- EXPLICIT UNIT PATTERNS FOUND ---")
for pattern_name, pattern in unit_patterns.items():
    matches = []
    for i, title in enumerate(supplier_titles[:100]):
        if re.search(pattern, title, re.IGNORECASE):
            matches.append((i, title))
    if matches:
        print(f"\n{pattern_name.upper()} pattern ({len(matches)} matches):")
        for idx, title in matches[:5]:
            print(f"  Row {idx}: {title}")

# Check for trailing numbers (potential quantities)
print("\n\n--- TRAILING NUMBER PATTERNS ---")
trailing_pattern = r'(\s\d{1,4})$'  # Number at end
for i, title in enumerate(supplier_titles[:100]):
    match = re.search(trailing_pattern, title)
    if match:
        trailing_numbers.append((i, title, match.group(1).strip()))

print(f"Found {len(trailing_numbers)} titles with trailing numbers:")
for idx, title, num in trailing_numbers[:15]:
    print(f"  Row {idx}: '{title}' -> trailing '{num}'")

# Check for leading multipliers
print("\n\n--- LEADING MULTIPLIER PATTERNS ---")
leading_pattern = r'^(\d+)\s*x\s+'
for i, title in enumerate(supplier_titles[:100]):
    match = re.search(leading_pattern, title, re.IGNORECASE)
    if match:
        leading_multipliers.append((i, title, match.group(1)))

print(f"Found {len(leading_multipliers)} titles with leading multipliers:")
for idx, title, num in leading_multipliers[:10]:
    print(f"  Row {idx}: '{title}'")

# Dimension patterns
print("\n\n--- DIMENSION/MEASUREMENT PATTERNS ---")
dim_patterns = [
    (r'\b\d+\s*cm\b', 'cm'),
    (r'\b\d+\s*mm\b', 'mm'),
    (r'\b\d+\s*ml\b', 'ml'),
    (r'\b\d+\s*ltr?\b', 'ltr'),
    (r'\b\d+\s*kg\b', 'kg'),
    (r'\b\d+\s*g\b', 'g'),
    (r'\b\d+\s*oz\b', 'oz'),
    (r'\b\d+\s*inch\b', 'inch'),
    (r'\b\d+\s*x\s*\d+\s*(?:cm|mm|inch|in)\b', 'LxW dimension'),
]

for pattern, name in dim_patterns:
    matches = []
    for i, title in enumerate(supplier_titles[:100]):
        if re.search(pattern, title, re.IGNORECASE):
            matches.append((i, title))
    if matches:
        print(f"\n{name} pattern ({len(matches)} matches in first 100):")
        for idx, title in matches[:3]:
            print(f"  Row {idx}: {title}")

# ============================================================================
# TASK 1B: CAPACITY MULTIPACK PATTERNS
# ============================================================================
print("\n\n" + "=" * 80)
print("TASK 1B: CAPACITY MULTIPACK PATTERNS IN AMAZON TITLES")
print("=" * 80)

capacity_multipack_pattern = r'(\d+)\s*x\s*\d+\s*(ml|g|l|kg|cl|oz)'
capacity_multipacks = []

for i, title in enumerate(amazon_titles[:100]):
    match = re.search(capacity_multipack_pattern, title, re.IGNORECASE)
    if match:
        capacity_multipacks.append((i, title, match.group()))

print(f"\nFound {len(capacity_multipacks)} capacity multipack patterns (e.g., '3 x 400ml'):")
for idx, title, pattern in capacity_multipacks[:15]:
    print(f"  Row {idx}: Pattern='{pattern}' in '{title[:100]}...'")

# ============================================================================
# TASK 2: SALES SIGNAL DETECTION
# ============================================================================
print("\n\n" + "=" * 80)
print("TASK 2: SALES SIGNAL DETECTION")
print("=" * 80)

sales_columns = ['sales_numeric', 'bought_in_past_month', 'Sales']
for col in sales_columns:
    if col in df.columns:
        print(f"\n'{col}' column found!")
        print(f"  Sample values: {df[col].head(10).tolist()}")
        print(f"  Dtype: {df[col].dtype}")
        # Check for text patterns
        sample = df[col].dropna().head(20)
        has_text = any(isinstance(v, str) for v in sample)
        print(f"  Contains text: {has_text}")

# Check bought_in_past_month specifically
if 'bought_in_past_month' in df.columns:
    print("\n--- bought_in_past_month analysis ---")
    sample_values = df['bought_in_past_month'].dropna().unique()[:20]
    print(f"  Unique sample values: {sample_values}")

# ============================================================================
# TASK 3: BRAND POSITION DETECTION
# ============================================================================
print("\n\n" + "=" * 80)
print("TASK 3: BRAND POSITION DETECTION")
print("=" * 80)

# Common brand names to check
known_brands = [
    'PYREX', 'AMTECH', 'RSW', 'EUROWRAP', 'DLUX', 'ROLSON', 'LYNX', 'DOVE',
    'GREEN ARROW', 'OPAL', 'SIEMENS', 'MOTOROLA', 'BOSCH', 'BRAUN', 'PRIMA',
    'TALA', 'CHEF AID', 'PRESTIGE', 'ADDIS', 'VINERS', 'RAYWARE', 'DENBY',
    'MASON CASH', 'KITCHENCRAFT', 'JUDGE', 'STELLAR', 'PROCOOK', 'DUNELM'
]

brand_positions = {'start': 0, 'middle': 0, 'end': 0, 'not_found': 0}

for title in supplier_titles[:100]:
    title_upper = title.upper()
    words = title_upper.split()
    found = False
    for brand in known_brands:
        if brand in title_upper:
            found = True
            brand_words = brand.split()
            first_word = brand_words[0]
            # Check position
            if title_upper.startswith(brand) or (words and words[0] == first_word):
                brand_positions['start'] += 1
            elif title_upper.endswith(brand) or (words and words[-1] == brand_words[-1]):
                brand_positions['end'] += 1
            else:
                brand_positions['middle'] += 1
            break
    if not found:
        brand_positions['not_found'] += 1

print(f"\nBrand position analysis (first 100 rows):")
print(f"  At START: {brand_positions['start']}")
print(f"  In MIDDLE: {brand_positions['middle']}")
print(f"  At END: {brand_positions['end']}")
print(f"  Brand not found: {brand_positions['not_found']}")

# Sample brand-containing titles
print("\n--- Sample titles with brands ---")
for i, title in enumerate(supplier_titles[:50]):
    for brand in known_brands:
        if brand in title.upper():
            words = title.split()
            pos = "START" if title.upper().startswith(brand) else ("END" if title.upper().endswith(brand) else "MIDDLE")
            print(f"  Row {i}: '{title}' -> Brand '{brand}' at {pos}")
            break

# ============================================================================
# TASK 4: CALIBRATION WARNINGS - POTENTIAL TRAPS
# ============================================================================
print("\n\n" + "=" * 80)
print("TASK 4: CALIBRATION WARNINGS - POTENTIAL TRAPS")
print("=" * 80)

# Dimension trap detection: NxN dimensions
dimension_trap_pattern = r'(\d+)\s*x\s*(\d+)\s*(cm|mm|inch|in|"|\')'
model_number_pattern = r'\b\d{3,4}\b(?!\s*(ml|g|l|kg|cm|mm|pcs?|pack))'
capacity_as_rsu_pattern = r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|cl)'

print("\n--- POTENTIAL DIMENSION TRAPS ---")
dim_traps = []
for i, title in enumerate(supplier_titles[:100]):
    match = re.search(dimension_trap_pattern, title, re.IGNORECASE)
    if match:
        dim_traps.append((i, title, match.group()))

for idx, title, pattern in dim_traps[:10]:
    print(f"  Row {idx}: '{pattern}' in '{title}' -> Should be RSU=1 (dimensions)")

print("\n--- POTENTIAL MODEL NUMBER TRAPS ---")
model_traps = []
for i, title in enumerate(supplier_titles[:100]):
    # Look for 3-4 digit numbers that might be model numbers
    match = re.search(r'\b([A-Z]+\s*\d{3,4})\b', title, re.IGNORECASE)
    if match:
        model_traps.append((i, title, match.group()))

for idx, title, pattern in model_traps[:10]:
    print(f"  Row {idx}: '{pattern}' in '{title}' -> Might be model number, not quantity")

print("\n--- POTENTIAL TRAILING QUANTITY TRAPS ---")
# These could be quantities OR model numbers OR capacities
qty_traps = []
for i, title in enumerate(supplier_titles[:100]):
    match = re.search(r'\s(\d{2,4})$', title)
    if match:
        num = match.group(1)
        qty_traps.append((i, title, num))

for idx, title, num in qty_traps[:15]:
    print(f"  Row {idx}: Trailing '{num}' in '{title}' -> Quantity OR model number?")

print("\n--- POTENTIAL CAPACITY MULTIPACK TRAPS ---")
cap_traps = []
for i, title in enumerate(amazon_titles[:100]):
    match = re.search(capacity_as_rsu_pattern, title, re.IGNORECASE)
    if match:
        n, cap, unit = match.groups()
        cap_traps.append((i, title, n, cap, unit))

for idx, title, n, cap, unit in cap_traps[:10]:
    print(f"  Row {idx}: '{n} x {cap}{unit}' -> RSU={n} (not {int(n)*int(cap)}), in '{title[:80]}...'")

print("\n\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
