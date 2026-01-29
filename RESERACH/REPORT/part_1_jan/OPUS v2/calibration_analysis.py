import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx', nrows=50)

print('=' * 80)
print('TASK 1: PACK QUANTITY PATTERN ANALYSIS')
print('=' * 80)

# 1a. Explicit Units Detection
explicit_patterns = ['pcs', 'pce', 'pk', 'pack', 'unit', 'pc ']
print('\n--- 1a. Checking for EXPLICIT UNITS (pcs, pce, pk, pack, unit) ---')
found_explicit = False
for i, title in enumerate(df['SupplierTitle']):
    title_lower = str(title).lower()
    for pattern in explicit_patterns:
        if pattern in title_lower:
            print(f'Row {i}: {title} - FOUND: {pattern}')
            found_explicit = True
if not found_explicit:
    print('No explicit unit patterns found (pcs, pce, pk, pack, unit)')

# 1b. Trailing Numbers 
print('\n--- 1b. Checking for TRAILING NUMBERS (potential pack qty) ---')
trailing_num_pattern = r'(\d+)\s*$'
trailing_found = []
for i, title in enumerate(df['SupplierTitle']):
    match = re.search(trailing_num_pattern, str(title))
    if match:
        num = match.group(1)
        trailing_found.append((i, title, num))
        print(f'Row {i}: "{title}" -> Trailing: {num}')
        
# 1c. Leading Multipliers
print('\n--- 1c. Checking for LEADING MULTIPLIERS (10x, 6 x, etc.) ---')
leading_mult_pattern = r'^(\d+)\s*[xX]\s+'
leading_found = False
for i, title in enumerate(df['SupplierTitle']):
    match = re.search(leading_mult_pattern, str(title))
    if match:
        print(f'Row {i}: {title}')
        leading_found = True
if not leading_found:
    print('No leading multiplier patterns (Nx ...) found')

# 1d. Dimension patterns
print('\n--- 1d. DIMENSION vs QUANTITY ANALYSIS ---')
dimension_patterns = [
    (r'\d+\s*cm', 'cm'),
    (r'\d+\s*mm', 'mm'),
    (r'\d+\s*ml', 'ml'),
    (r'\d+\s*g\b', 'g'),
    (r'\d+\s*kg', 'kg'),
    (r'\d+\s*ltr', 'ltr'),
    (r'\d+\s*l\b', 'L'),
    (r'\d+\s*oz', 'oz'),
    (r'\d+\s*inch', 'inch'),
]

print('Dimension patterns found in SupplierTitle:')
for i, title in enumerate(df['SupplierTitle']):
    title_str = str(title).lower()
    dims_found = []
    for pattern, name in dimension_patterns:
        matches = re.findall(pattern, title_str)
        if matches:
            dims_found.extend([(name, m) for m in matches])
    if dims_found:
        print(f'Row {i}: "{title}" -> {dims_found}')

# 1e. Pieces/PC patterns
print('\n--- 1e. Checking for PIECES/PC patterns ---')
pieces_pattern = r'(\d+)\s*(pieces?|pc|pcs)'
for i, title in enumerate(df['SupplierTitle']):
    match = re.search(pieces_pattern, str(title).lower())
    if match:
        print(f'Row {i}: "{title}" -> {match.group(0)}')

print('\n' + '=' * 80)
print('TASK 2: SALES SIGNAL DETECTION')
print('=' * 80)

print('\nColumns available:', df.columns.tolist())
print('\nLooking for sales-related columns...')

# Check for sales columns
sales_cols = ['sales_numeric', 'bought_in_past_month', 'Sales']
for col in sales_cols:
    if col in df.columns:
        print(f'\nFound column: {col}')
        print(f'  Type: {df[col].dtype}')
        print(f'  Sample values: {df[col].head(5).tolist()}')
        print(f'  Contains text requiring parsing: {df[col].dtype == "object"}')

print('\n' + '=' * 80)
print('TASK 3: BRAND PATTERN DETECTION')
print('=' * 80)

# Extract first word as potential brand
print('\nAnalyzing first word of SupplierTitle as potential brand:')
first_words = []
for title in df['SupplierTitle']:
    first_word = str(title).split()[0] if str(title).split() else ''
    first_words.append(first_word)

# Count occurrences of first words
from collections import Counter
word_counts = Counter(first_words)
print('\nMost common first words (potential brands):')
for word, count in word_counts.most_common(15):
    print(f'  {word}: {count} occurrences')

# Check if brands appear consistently at start
print('\nSample SupplierTitles analyzed for brand position:')
for i in range(min(15, len(df))):
    title = df['SupplierTitle'].iloc[i]
    print(f'Row {i}: {title}')

print('\n' + '=' * 80)
print('TASK 4: CALIBRATION WARNINGS - POTENTIAL TRAPS')
print('=' * 80)

# Identify rows that might trap the logic
print('\nANALYZING POTENTIAL TRAPS...\n')

traps = []

# Check for trailing numbers that are NOT pack quantities
for i, title in enumerate(df['SupplierTitle']):
    title_str = str(title)
    
    # Check for trailing numbers that might be model numbers or sizes
    match = re.search(r'(\d+)\s*$', title_str)
    if match:
        num = match.group(1)
        # Check if it's likely a dimension (preceded by unit keywords)
        if re.search(r'(cm|mm|ml|g|kg|ltr|inch|grade)\s*$', title_str.lower()):
            traps.append((i, title, f"'{num}' appears to be a measurement, not pack qty"))
        elif re.search(r'(size|grade|class|type|style|model)\s*\d+\s*$', title_str.lower()):
            traps.append((i, title, f"'{num}' appears to be a model/size number"))
        elif int(num) in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
            # Single digit might be variant/color/size
            traps.append((i, title, f"'{num}' - single digit could be variant, not pack qty"))

# Check for numbers embedded in what looks like product names
for i, title in enumerate(df['SupplierTitle']):
    title_str = str(title)
    # Numbers that appear mid-string
    if re.search(r'\b\d+\s*(cm|mm|ml|g|kg|ltr|inch)\b', title_str.lower()):
        if (i, title) not in [(t[0], t[1]) for t in traps]:
            # Extract the dimension for analysis
            dims = re.findall(r'\b(\d+)\s*(cm|mm|ml|g|kg|ltr|inch)\b', title_str.lower())
            if dims:
                traps.append((i, title, f"Contains dimensions: {dims} - NOT pack quantities"))

print('POTENTIAL TRAP ROWS:')
for row_num, title, reason in traps[:20]:  # Limit to first 20
    print(f'Row {row_num}: "{title}"')
    print(f'         WARNING: {reason}\n')

print('\n' + '=' * 80)
print('SUMMARY CONFIGURATION')
print('=' * 80)
