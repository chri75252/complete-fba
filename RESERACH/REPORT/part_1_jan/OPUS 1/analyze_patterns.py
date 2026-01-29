import pandas as pd
import re

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx', nrows=50)

print("=" * 80)
print("SUPPLIER TITLE vs AMAZON TITLE ANALYSIS (First 50 rows)")
print("=" * 80)
print()

for idx, row in df.iterrows():
    print(f"Row {idx}:")
    print(f"  EAN: {row['EAN']}")
    print(f"  SupplierTitle: {row['SupplierTitle']}")
    print(f"  AmazonTitle: {row['AmazonTitle']}")
    print(f"  bought_in_past_month: {row['bought_in_past_month']}")
    print()

print("=" * 80)
print("PATTERN DETECTION ANALYSIS")
print("=" * 80)

# Pattern detection for pack quantities
explicit_units = []
trailing_numbers = []
leading_multipliers = []
dimension_formats = []
brand_positions = []

unit_pattern = re.compile(r'\b(\d+)\s*(pcs?|pce|pk|pack|unit|set|piece|pieces)\b', re.IGNORECASE)
trailing_number_pattern = re.compile(r'\s(\d{2,})$')  # Numbers >= 2 digits at end
leading_multiplier_pattern = re.compile(r'^(\d+)\s*x\s+', re.IGNORECASE)
dimension_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(cm|mm|ml|ltr|l|kg|g|oz|inch|")\b', re.IGNORECASE)

for idx, row in df.iterrows():
    supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
    amazon_title = str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else ""
    
    # Check for explicit units
    for title in [supplier_title, amazon_title]:
        matches = unit_pattern.findall(title)
        if matches:
            explicit_units.append((idx, title, matches))
    
    # Check for trailing numbers in supplier title
    match = trailing_number_pattern.search(supplier_title)
    if match:
        trailing_numbers.append((idx, supplier_title, match.group(1)))
    
    # Check for leading multipliers
    for title in [supplier_title, amazon_title]:
        match = leading_multiplier_pattern.search(title)
        if match:
            leading_multipliers.append((idx, title, match.group(1)))
    
    # Check for dimension formats
    for title in [supplier_title, amazon_title]:
        matches = dimension_pattern.findall(title)
        if matches:
            dimension_formats.append((idx, title, matches))

print()
print("=== EXPLICIT UNIT PATTERNS FOUND ===")
for item in explicit_units:
    print(f"  Row {item[0]}: '{item[1]}' -> {item[2]}")

print()
print("=== TRAILING NUMBER PATTERNS FOUND ===")
for item in trailing_numbers:
    print(f"  Row {item[0]}: '{item[1]}' -> ends with '{item[2]}'")

print()
print("=== LEADING MULTIPLIER PATTERNS FOUND ===")
for item in leading_multipliers:
    print(f"  Row {item[0]}: '{item[1]}' -> starts with '{item[2]}x'")

print()
print("=== DIMENSION FORMATS FOUND ===")
for item in dimension_formats:
    print(f"  Row {item[0]}: '{item[1]}' -> {item[2]}")

# Analyze brand position
print()
print("=== BRAND POSITION ANALYSIS ===")
# Check first word of supplier titles
first_words = []
for idx, row in df.iterrows():
    supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ""
    if supplier_title:
        first_word = supplier_title.split()[0] if supplier_title.split() else ""
        first_words.append((idx, first_word, supplier_title))

print("First words of SupplierTitle:")
unique_first_words = {}
for idx, word, title in first_words:
    if word.upper() not in unique_first_words:
        unique_first_words[word.upper()] = []
    unique_first_words[word.upper()].append((idx, title))

for word, items in sorted(unique_first_words.items(), key=lambda x: -len(x[1])):
    print(f"  '{word}': {len(items)} occurrences")

# Check bought_in_past_month column format
print()
print("=== SALES COLUMN ANALYSIS ===")
print("bought_in_past_month values (unique):")
sales_values = df['bought_in_past_month'].unique()
for val in sales_values[:20]:
    print(f"  {repr(val)}")

# Check if there are other sales columns
sales_columns = [col for col in df.columns if 'sale' in col.lower() or 'sold' in col.lower()]
print(f"\nOther potential sales columns: {sales_columns}")
