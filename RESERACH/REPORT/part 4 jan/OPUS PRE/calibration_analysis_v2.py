import pandas as pd
import re

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\part 4 jan.xlsx')

# Save first 50 rows analysis to file
output_lines = []
output_lines.append("=" * 100)
output_lines.append("CALIBRATION ANALYSIS - FIRST 50 ROWS")
output_lines.append("=" * 100)
output_lines.append("")

for idx, row in df.head(50).iterrows():
    output_lines.append(f"Row {idx}:")
    output_lines.append(f"  SUPPLIER: {row['SupplierTitle']}")
    output_lines.append(f"  AMAZON:   {row['AmazonTitle']}")
    output_lines.append("")

# Pattern Analysis
output_lines.append("")
output_lines.append("=" * 100)
output_lines.append("PATTERN ANALYSIS")
output_lines.append("=" * 100)

# Analyze pack quantity patterns
supplier_titles = df.head(50)['SupplierTitle'].astype(str).tolist()
amazon_titles = df.head(50)['AmazonTitle'].astype(str).tolist()

# Check for explicit unit patterns
explicit_unit_patterns = {
    'pcs': r'\b\d+\s*pcs\b',
    'pce': r'\b\d+\s*pce\b',
    'pk': r'\b\d+\s*pk\b',
    'pack': r'\bpack\s*of\s*\d+\b|\b\d+\s*pack\b',
    'set': r'\bset\s*of\s*\d+\b|\b\d+\s*set\b',
    'pieces': r'\b\d+\s*pieces?\b'
}

output_lines.append("")
output_lines.append("--- EXPLICIT UNIT PATTERNS ---")
for pattern_name, pattern in explicit_unit_patterns.items():
    supplier_matches = []
    amazon_matches = []
    for i, title in enumerate(supplier_titles):
        matches = re.findall(pattern, title, re.IGNORECASE)
        if matches:
            supplier_matches.append((i, matches, title[:100]))
    for i, title in enumerate(amazon_titles):
        matches = re.findall(pattern, title, re.IGNORECASE)
        if matches:
            amazon_matches.append((i, matches, title[:100]))
    
    if supplier_matches or amazon_matches:
        output_lines.append(f"\n  {pattern_name.upper()}:")
        if supplier_matches:
            output_lines.append(f"    Supplier examples: {supplier_matches[:3]}")
        if amazon_matches:
            output_lines.append(f"    Amazon examples: {amazon_matches[:3]}")

# Check for trailing numbers (potential implicit quantities)
output_lines.append("")
output_lines.append("--- TRAILING NUMBER PATTERNS (potential implicit quantities) ---")
trailing_num_pattern = r'\s(\d{2,})\s*$'
for i, title in enumerate(supplier_titles[:50]):
    match = re.search(trailing_num_pattern, title)
    if match:
        output_lines.append(f"  Row {i}: SUPPLIER ends with '{match.group(1)}' -> {title[:80]}")

# Check for leading multipliers (Nx pattern)
output_lines.append("")
output_lines.append("--- LEADING MULTIPLIER PATTERNS (Nx at start) ---")
leading_mult_pattern = r'^(\d+)\s*[xX]\s+'
for i, title in enumerate(supplier_titles[:50]):
    match = re.search(leading_mult_pattern, title)
    if match:
        output_lines.append(f"  Row {i}: SUPPLIER starts with '{match.group(1)}x' -> {title[:80]}")
for i, title in enumerate(amazon_titles[:50]):
    match = re.search(leading_mult_pattern, title)
    if match:
        output_lines.append(f"  Row {i}: AMAZON starts with '{match.group(1)}x' -> {title[:80]}")

# Check for capacity multipack patterns (N x capacity)
output_lines.append("")
output_lines.append("--- CAPACITY MULTIPACK PATTERNS (N x [capacity]ml/g/l) ---")
capacity_pattern = r'(\d+)\s*[xX]\s*(\d+)\s*(ml|g|l|ltr|oz|kg)\b'
for i, title in enumerate(amazon_titles[:50]):
    matches = re.findall(capacity_pattern, title, re.IGNORECASE)
    if matches:
        output_lines.append(f"  Row {i}: AMAZON has capacity pattern {matches} -> {title[:100]}")
for i, title in enumerate(supplier_titles[:50]):
    matches = re.findall(capacity_pattern, title, re.IGNORECASE)
    if matches:
        output_lines.append(f"  Row {i}: SUPPLIER has capacity pattern {matches} -> {title[:100]}")

# Check for dimension patterns
output_lines.append("")
output_lines.append("--- DIMENSION PATTERNS ---")
dimension_patterns = [
    r'\d+\s*[xX]\s*\d+\s*(cm|mm|inch|in)\b',
    r'\d+\s*(cm|mm|inch|in)\s*[xX]\s*\d+',
    r'\d+\s*(cm|mm|m)\b',
    r'\d+\s*(ml|ltr|l)\b',
    r'\d+\s*(kg|g|oz)\b'
]
dimension_examples = []
for i, title in enumerate(supplier_titles[:50]):
    for pat in dimension_patterns:
        matches = re.findall(pat, title, re.IGNORECASE)
        if matches:
            dimension_examples.append(f"  Row {i} SUPPLIER: {title[:80]}... matches: {matches}")
            break
for i, title in enumerate(amazon_titles[:50]):
    for pat in dimension_patterns:
        matches = re.findall(pat, title, re.IGNORECASE)
        if matches:
            dimension_examples.append(f"  Row {i} AMAZON: {title[:80]}... matches: {matches}")
            break

if dimension_examples:
    output_lines.extend(dimension_examples[:20])

# Check for spec/feature multipliers that are NOT pack counts
output_lines.append("")
output_lines.append("--- SPEC/FEATURE MULTIPLIERS (NOT pack counts) ---")
spec_patterns = [
    r'(\d+)[xX]\s*(magnification|zoom|microscope|scope|optical)',
    r'(\d+)[xX]\s*(faster|stronger|brighter|louder)',
    r'(\d+)\s*times\b'
]
for i, title in enumerate(amazon_titles[:50]):
    for pat in spec_patterns:
        matches = re.findall(pat, title, re.IGNORECASE)
        if matches:
            output_lines.append(f"  Row {i} AMAZON: {title[:100]}... spec pattern: {matches}")

# Brand position analysis
output_lines.append("")
output_lines.append("--- BRAND POSITION ANALYSIS ---")
output_lines.append("Checking if brand appears at start of supplier titles...")

# Get unique first words from supplier titles
first_words = {}
for title in supplier_titles[:50]:
    if title and len(title) > 2:
        first_word = title.split()[0] if title.split() else ''
        first_words[first_word] = first_words.get(first_word, 0) + 1

output_lines.append(f"  Most common first words: {sorted(first_words.items(), key=lambda x: -x[1])[:15]}")

# Sales column detection
output_lines.append("")
output_lines.append("--- SALES COLUMN DETECTION ---")
output_lines.append(f"Available columns: {list(df.columns)}")
if 'bought_in_past_month' in df.columns:
    output_lines.append(f"  Found 'bought_in_past_month' column")
    output_lines.append(f"  Sample values: {df['bought_in_past_month'].head(10).tolist()}")
    output_lines.append(f"  Data type: {df['bought_in_past_month'].dtype}")
if 'sales_numeric' in df.columns:
    output_lines.append(f"  Found 'sales_numeric' column")
    output_lines.append(f"  Sample values: {df['sales_numeric'].head(10).tolist()}")
if 'Sales' in df.columns:
    output_lines.append(f"  Found 'Sales' column")
    output_lines.append(f"  Sample values: {df['Sales'].head(10).tolist()}")

# Check for pipe characters in titles
output_lines.append("")
output_lines.append("--- PIPE CHARACTER CHECK (for table sanitization) ---")
pipe_count = 0
for title in amazon_titles[:50]:
    if '|' in str(title):
        pipe_count += 1
        output_lines.append(f"  Found pipe in: {title[:100]}")
output_lines.append(f"  Total titles with pipes: {pipe_count}/50")

# Write to file
output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\OPUS PRE\calibration_output.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"Analysis written to: {output_path}")
print("\nQuick Summary:")
print(f"  Total rows in file: {len(df)}")
print(f"  Columns: {list(df.columns)}")
