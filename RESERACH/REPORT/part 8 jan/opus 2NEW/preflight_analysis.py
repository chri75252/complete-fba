"""Pre-flight calibration analysis for FBA financial report"""
import pandas as pd
import re
import json

# Load first 50 rows
file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"
df = pd.read_excel(file_path, nrows=50)

print("=" * 80)
print("PREFLIGHT CALIBRATION ANALYSIS")
print("=" * 80)

# 1. Column information
print("\n### COLUMNS ###")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

print(f"\nTotal shape: {df.shape}")

# 2. Display key columns for pattern analysis
print("\n" + "=" * 80)
print("### SAMPLE DATA: SupplierTitle vs AmazonTitle (first 50 rows) ###")
print("=" * 80)

for idx, row in df.iterrows():
    supplier_title = str(row.get('SupplierTitle', ''))[:100]
    amazon_title = str(row.get('AmazonTitle', ''))[:100]
    ean = str(row.get('EAN', ''))
    print(f"\n--- Row {idx} ---")
    print(f"  EAN: {ean}")
    print(f"  Supplier: {supplier_title}")
    print(f"  Amazon: {amazon_title}")

# 3. Check for sales columns
print("\n" + "=" * 80)
print("### SALES COLUMN DETECTION ###")
print("=" * 80)

sales_candidates = ['sales_numeric', 'bought_in_past_month', 'Sales', 'sales']
for col in sales_candidates:
    if col in df.columns:
        sample = df[col].head(10).tolist()
        print(f"  Found: '{col}' -> Sample values: {sample}")

# 4. Pattern detection
print("\n" + "=" * 80)
print("### PATTERN DETECTION ###")
print("=" * 80)

# Patterns to detect
explicit_units = []
trailing_numbers = []
leading_multipliers = []
dimension_examples = []
capacity_multipacks = []
spec_x_examples = []
brands_at_start = []

unit_patterns = ['pcs', 'pce', 'pk', 'pack', 'unit', 'piece', 'set']
dimension_keywords = ['cm', 'mm', 'ml', 'ltr', 'kg', 'g', 'oz', 'inch', 'L', 'litre', 'liter']

for idx, row in df.iterrows():
    supplier = str(row.get('SupplierTitle', '')).upper()
    amazon = str(row.get('AmazonTitle', ''))
    
    # Check for explicit units
    for unit in unit_patterns:
        if re.search(rf'\b\d+\s*{unit}\b', supplier, re.IGNORECASE):
            explicit_units.append((idx, supplier))
            break
    
    # Check for trailing numbers
    trailing_match = re.search(r'\s+(\d{2,4})$', supplier.strip())
    if trailing_match:
        trailing_numbers.append((idx, supplier, trailing_match.group(1)))
    
    # Check for leading multipliers (like "10x ...")
    leading_match = re.search(r'^(\d+)\s*x\s+', supplier, re.IGNORECASE)
    if leading_match:
        leading_multipliers.append((idx, supplier, leading_match.group(1)))
    
    # Check for dimensions
    for dim in dimension_keywords:
        if re.search(rf'\d+\s*{dim}\b', supplier, re.IGNORECASE):
            dimension_examples.append((idx, supplier, dim))
            break
    
    # Check for capacity multipacks in Amazon titles (e.g., "3 x 400ml")
    capacity_match = re.search(r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|ltr|litre|oz)', amazon, re.IGNORECASE)
    if capacity_match:
        capacity_multipacks.append((idx, amazon, capacity_match.groups()))
    
    # Check for spec/feature X patterns (e.g., "2x magnification")
    spec_x_match = re.search(r'(\d+)x\s*(magnification|zoom|microscope|power|brighter|faster)', amazon, re.IGNORECASE)
    if spec_x_match:
        spec_x_examples.append((idx, amazon, spec_x_match.groups()))
    
    # Check brand at start (all caps word at start)
    brand_match = re.match(r'^([A-Z]{3,})\s+', supplier)
    if brand_match:
        brands_at_start.append((idx, brand_match.group(1)))

print("\n--- Explicit Units Found ---")
for item in explicit_units[:10]:
    print(f"  Row {item[0]}: {item[1][:80]}")

print("\n--- Trailing Numbers Found ---")
for item in trailing_numbers[:10]:
    print(f"  Row {item[0]}: '{item[1][:80]}' -> Trailing: {item[2]}")

print("\n--- Leading Multipliers (Nx) Found ---")
for item in leading_multipliers[:10]:
    print(f"  Row {item[0]}: '{item[1][:80]}' -> Multiplier: {item[2]}")

print("\n--- Dimension Examples Found ---")
for item in dimension_examples[:10]:
    print(f"  Row {item[0]}: '{item[1][:80]}' -> Dimension type: {item[2]}")

print("\n--- Capacity Multipacks in Amazon Found ---")
for item in capacity_multipacks[:10]:
    print(f"  Row {item[0]}: '{item[1][:80]}' -> Pattern: {item[2]}")

print("\n--- Spec/Feature X Patterns Found ---")
for item in spec_x_examples[:10]:
    print(f"  Row {item[0]}: '{item[1][:80]}' -> Pattern: {item[2]}")

print("\n--- Brands at Start ---")
brand_counts = {}
for item in brands_at_start:
    brand_counts[item[1]] = brand_counts.get(item[1], 0) + 1
for brand, count in sorted(brand_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {brand}: {count} occurrences")

# 5. Brand presence analysis
print("\n" + "=" * 80)
print("### BRAND PRESENCE ANALYSIS ###")
print("=" * 80)

supplier_brand_present = len(brands_at_start)
supplier_brand_pct = (supplier_brand_present / len(df)) * 100
print(f"Brands at start of SupplierTitle: {supplier_brand_present}/{len(df)} ({supplier_brand_pct:.1f}%)")

# Check for Amazon brand patterns
amazon_brand_keywords = []
for idx, row in df.iterrows():
    amazon = str(row.get('AmazonTitle', ''))
    # Look for brand patterns: "by [Brand]", "[Brand] -", "from [Brand]"
    if re.search(r'\b(by|from)\s+[A-Z][a-zA-Z]+', amazon):
        amazon_brand_keywords.append(idx)
    elif re.match(r'^[A-Z][a-zA-Z]+\s+-\s+', amazon):
        amazon_brand_keywords.append(idx)

amazon_brand_pct = (len(amazon_brand_keywords) / len(df)) * 100
print(f"Brands detected in AmazonTitle: {len(amazon_brand_keywords)}/{len(df)} ({amazon_brand_pct:.1f}%)")

# Summary stats
print("\n" + "=" * 80)
print("### SUMMARY STATISTICS ###")
print("=" * 80)

print(f"  Explicit unit patterns found: {len(explicit_units)}")
print(f"  Trailing number patterns found: {len(trailing_numbers)}")
print(f"  Leading multiplier patterns found: {len(leading_multipliers)}")
print(f"  Dimension patterns found: {len(dimension_examples)}")
print(f"  Capacity multipack patterns found: {len(capacity_multipacks)}")
print(f"  Spec/Feature X patterns found: {len(spec_x_examples)}")
print(f"  Brands at start found: {len(brands_at_start)}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)

# Write detailed output to file
output_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\opus 2NEW\preflight_output.txt"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("PREFLIGHT CALIBRATION ANALYSIS OUTPUT\n")
    f.write("=" * 80 + "\n\n")
    
    f.write("### COLUMNS ###\n")
    for i, col in enumerate(df.columns):
        f.write(f"  {i}: {col}\n")
    f.write(f"\nTotal shape: {df.shape}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("### SAMPLE DATA: SupplierTitle vs AmazonTitle (first 50 rows) ###\n")
    f.write("=" * 80 + "\n")
    
    for idx, row in df.iterrows():
        supplier_title = str(row.get('SupplierTitle', ''))
        amazon_title = str(row.get('AmazonTitle', ''))
        ean = str(row.get('EAN', ''))
        f.write(f"\n--- Row {idx} ---\n")
        f.write(f"  EAN: {ean}\n")
        f.write(f"  Supplier: {supplier_title}\n")
        f.write(f"  Amazon: {amazon_title}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("### SALES COLUMN DETECTION ###\n")
    f.write("=" * 80 + "\n")
    
    for col in sales_candidates:
        if col in df.columns:
            sample = df[col].head(10).tolist()
            f.write(f"  Found: '{col}' -> Sample values: {sample}\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("### PATTERN DETECTION ###\n")
    f.write("=" * 80 + "\n")
    
    f.write("\n--- Explicit Units Found ---\n")
    for item in explicit_units:
        f.write(f"  Row {item[0]}: {item[1]}\n")
    
    f.write("\n--- Trailing Numbers Found ---\n")
    for item in trailing_numbers:
        f.write(f"  Row {item[0]}: '{item[1]}' -> Trailing: {item[2]}\n")
    
    f.write("\n--- Leading Multipliers (Nx) Found ---\n")
    for item in leading_multipliers:
        f.write(f"  Row {item[0]}: '{item[1]}' -> Multiplier: {item[2]}\n")
    
    f.write("\n--- Dimension Examples Found ---\n")
    for item in dimension_examples:
        f.write(f"  Row {item[0]}: '{item[1]}' -> Dimension type: {item[2]}\n")
    
    f.write("\n--- Capacity Multipacks in Amazon Found ---\n")
    for item in capacity_multipacks:
        f.write(f"  Row {item[0]}: '{item[1]}' -> Pattern: {item[2]}\n")
    
    f.write("\n--- Spec/Feature X Patterns Found ---\n")
    for item in spec_x_examples:
        f.write(f"  Row {item[0]}: '{item[1]}' -> Pattern: {item[2]}\n")
    
    f.write("\n--- Brands at Start ---\n")
    for brand, count in sorted(brand_counts.items(), key=lambda x: -x[1]):
        f.write(f"  {brand}: {count} occurrences\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("### BRAND PRESENCE ANALYSIS ###\n")
    f.write("=" * 80 + "\n")
    f.write(f"Brands at start of SupplierTitle: {supplier_brand_present}/{len(df)} ({supplier_brand_pct:.1f}%)\n")
    f.write(f"Brands detected in AmazonTitle: {len(amazon_brand_keywords)}/{len(df)} ({amazon_brand_pct:.1f}%)\n")
    
    f.write("\n" + "=" * 80 + "\n")
    f.write("### SUMMARY STATISTICS ###\n")
    f.write("=" * 80 + "\n")
    f.write(f"  Explicit unit patterns found: {len(explicit_units)}\n")
    f.write(f"  Trailing number patterns found: {len(trailing_numbers)}\n")
    f.write(f"  Leading multiplier patterns found: {len(leading_multipliers)}\n")
    f.write(f"  Dimension patterns found: {len(dimension_examples)}\n")
    f.write(f"  Capacity multipack patterns found: {len(capacity_multipacks)}\n")
    f.write(f"  Spec/Feature X patterns found: {len(spec_x_examples)}\n")
    f.write(f"  Brands at start found: {len(brands_at_start)}\n")

print(f"\nDetailed output written to: {output_path}")
