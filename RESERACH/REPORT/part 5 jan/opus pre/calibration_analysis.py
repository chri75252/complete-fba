"""
FBA Pre-flight Calibration Analysis
Analyzes supplier naming conventions and data patterns
"""
import pandas as pd
import re
from collections import Counter

# Read first 50 rows
file_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 5 jan\part 5 jan.xlsx'
df = pd.read_excel(file_path, nrows=50)

print("=" * 80)
print("FBA PRE-FLIGHT CALIBRATION ANALYSIS")
print("=" * 80)
print(f"\nFile: part 5 jan.xlsx")
print(f"Rows analyzed: {len(df)}")
print(f"Columns: {', '.join(df.columns.tolist())}\n")

# ====================================================================================
# TASK 1: DETECT PACK QUANTITY PATTERNS
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 1: PACK QUANTITY PATTERN DETECTION")
print("=" * 80)

explicit_units_found = set()
trailing_number_examples = []
leading_multiplier_examples = []
dimension_patterns = set()
capacity_multipack_examples = []
spec_multiplier_examples = []

# Patterns to detect
explicit_unit_pattern = re.compile(r'\b(\d+)\s*(pcs?|pce|pieces?|pk|pack|unit|count|set)\b', re.IGNORECASE)
trailing_number_pattern = re.compile(r'[A-Z]+\s+(\d+)$')
leading_multiplier_pattern = re.compile(r'^(\d+)\s*x\s+', re.IGNORECASE)
dimension_pattern = re.compile(r'(\d+)\s*(cm|mm|ml|ltr?|kg|g|oz|inch|ft|m\b)', re.IGNORECASE)
capacity_multipack_pattern = re.compile(r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|kg|oz)', re.IGNORECASE)
spec_multiplier_pattern = re.compile(r'(\d+)x?\s*(magnification|zoom|microscope|scope|times|power)', re.IGNORECASE)

print("\nAnalyzing SupplierTitle vs AmazonTitle for pack patterns...\n")

for idx, row in df.iterrows():
    supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ''
    amazon_title = str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else ''
    
    # Explicit units
    explicit_matches = explicit_unit_pattern.findall(supplier_title)
    if explicit_matches:
        for qty, unit in explicit_matches:
            explicit_units_found.add(unit.lower())
            if len(explicit_units_found) <= 5:  # Show first few examples
                print(f"Row {idx}: Explicit unit found - '{qty} {unit}' in: {supplier_title[:80]}")
    
    # Trailing numbers
    trailing_match = trailing_number_pattern.search(supplier_title)
    if trailing_match and len(trailing_number_examples) < 5:
        trailing_number_examples.append((idx, supplier_title, trailing_match.group(1)))
    
    # Leading multipliers
    leading_match = leading_multiplier_pattern.search(supplier_title)
    if leading_match and len(leading_multiplier_examples) < 5:
        leading_multiplier_examples.append((idx, supplier_title, leading_match.group(1)))
    
    # Dimensions
    dim_matches = dimension_pattern.findall(supplier_title + ' ' + amazon_title)
    for qty, unit in dim_matches:
        dimension_patterns.add(unit.lower())
    
    # Capacity multipacks (in Amazon titles)
    cap_matches = capacity_multipack_pattern.findall(amazon_title)
    if cap_matches and len(capacity_multipack_examples) < 8:
        capacity_multipack_examples.append((idx, amazon_title, cap_matches[0]))
    
    # Spec/feature multipliers
    spec_matches = spec_multiplier_pattern.findall(amazon_title)
    if spec_matches and len(spec_multiplier_examples) < 5:
        spec_multiplier_examples.append((idx, amazon_title, spec_matches[0]))

print(f"\n✓ Explicit units found: {sorted(explicit_units_found)}")

if trailing_number_examples:
    print(f"\n✓ Trailing number patterns found ({len(trailing_number_examples)} examples):")
    for idx, title, num in trailing_number_examples:
        print(f"  Row {idx}: Ends with '{num}' - {title[:80]}")
else:
    print("\n✗ No trailing number patterns detected")

if leading_multiplier_examples:
    print(f"\n✓ Leading multiplier patterns found ({len(leading_multiplier_examples)} examples):")
    for idx, title, num in leading_multiplier_examples:
        print(f"  Row {idx}: Starts with '{num}x' - {title[:80]}")
else:
    print("\n✗ No leading multiplier patterns detected")

print(f"\n✓ Dimension/measurement units found: {sorted(dimension_patterns)}")

# ====================================================================================
# TASK 1B: CAPACITY MULTIPACK PATTERNS
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 1B: CAPACITY MULTIPACK PATTERN DETECTION")
print("=" * 80)

if capacity_multipack_examples:
    print(f"\n✓ Found {len(capacity_multipack_examples)} capacity multipack patterns:")
    for idx, title, match in capacity_multipack_examples:
        qty, capacity, unit = match
        print(f"  Row {idx}: '{qty} x {capacity}{unit}' → RSU should be {qty}, NOT {int(qty)*int(capacity)}")
        print(f"    Amazon: {title[:100]}")
else:
    print("\n✗ No capacity multipack patterns detected")

# ====================================================================================
# TASK 1C: NON-PACK "Nx" SPEC/FEATURE MULTIPLIERS
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 1C: NON-PACK 'Nx' SPEC/FEATURE MULTIPLIERS")
print("=" * 80)

if spec_multiplier_examples:
    print(f"\n✓ Found {len(spec_multiplier_examples)} spec/feature multipliers (SHOULD NOT trigger RSU):")
    for idx, title, match in spec_multiplier_examples:
        num, keyword = match
        print(f"  Row {idx}: '{num}x {keyword}' is a FEATURE, not pack count")
        print(f"    Amazon: {title[:100]}")
else:
    print("\n✗ No spec/feature multipliers detected")

# ====================================================================================
# TASK 2: DETECT SALES SIGNAL
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 2: SALES SIGNAL DETECTION")
print("=" * 80)

sales_columns = ['bought_in_past_month', 'sales_numeric', 'Sales']
detected_sales_column = None
sales_requires_parsing = False

for col in sales_columns:
    if col in df.columns:
        detected_sales_column = col
        sample_vals = df[col].dropna().head(10).tolist()
        print(f"\n✓ Sales column found: '{col}'")
        print(f"  Sample values: {sample_vals}")
        
        # Check if contains text requiring parsing
        if df[col].dtype == 'object':
            text_samples = [str(v) for v in sample_vals if '+' in str(v) or 'bought' in str(v).lower()]
            if text_samples:
                sales_requires_parsing = True
                print(f"  ⚠ Contains text requiring parsing: {text_samples}")
        break

if not detected_sales_column:
    print("\n✗ No standard sales column found")
    detected_sales_column = 'bought_in_past_month'  # Default fallback

# ====================================================================================
# TASK 3: DETECT BRAND PATTERNS
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 3: BRAND PATTERN DETECTION")
print("=" * 80)

# Analyze if brand is consistently at start
potential_brands = []
brand_pattern_analysis = {'start': 0, 'mixed': 0, 'total': 0}

for idx, row in df.head(30).iterrows():
    supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ''
    if not supplier_title:
        continue
    
    brand_pattern_analysis['total'] += 1
    
    # Extract first word (potential brand)
    first_word = supplier_title.split()[0] if supplier_title.split() else ''
    
    # Check if first word is all caps (common brand pattern)
    if first_word.isupper() and len(first_word) >= 2:
        potential_brands.append(first_word)
        brand_pattern_analysis['start'] += 1
    else:
        brand_pattern_analysis['mixed'] += 1

brand_counts = Counter(potential_brands)
most_common_brands = brand_counts.most_common(10)

print(f"\nBrand position analysis:")
print(f"  Brands at start: {brand_pattern_analysis['start']}/{brand_pattern_analysis['total']}")
print(f"  Mixed/other: {brand_pattern_analysis['mixed']}/{brand_pattern_analysis['total']}")

if brand_pattern_analysis['start'] > brand_pattern_analysis['mixed']:
    brand_position = 'start'
    print(f"\n✓ Brand position: START (brands consistently appear at the beginning)")
else:
    brand_position = 'mixed'
    print(f"\n✓ Brand position: MIXED (brands appear in various positions)")

print(f"\nMost common potential brands:")
for brand, count in most_common_brands:
    print(f"  {brand}: {count} occurrences")

# ====================================================================================
# TASK 4: CALIBRATION WARNINGS
# ====================================================================================
print("\n" + "=" * 80)
print("TASK 4: CALIBRATION WARNINGS")
print("=" * 80)

warnings = []

# Check for problematic rows
for idx, row in df.iterrows():
    supplier_title = str(row['SupplierTitle']) if pd.notna(row['SupplierTitle']) else ''
    amazon_title = str(row['AmazonTitle']) if pd.notna(row['AmazonTitle']) else ''
    
    # Look for numbers that could be confused as quantities
    # Pattern: product name with numbers that aren't quantities
    if re.search(r'\d{3,4}(?!ml|cm|mm|g|kg|\s*x)', supplier_title):
        potential_model_numbers = re.findall(r'\b\d{3,4}\b', supplier_title)
        for num in potential_model_numbers:
            if int(num) > 100:  # Likely model number, not quantity
                warnings.append({
                    'row': idx,
                    'type': 'Model number confusion',
                    'detail': f"'{num}' in title may be model number, not quantity",
                    'title': supplier_title[:80]
                })
    
    # Check for severe title mismatches (possibly wrong EAN match)
    if supplier_title and amazon_title:
        supplier_words = set(supplier_title.lower().split())
        amazon_words = set(amazon_title.lower().split())
        common_words = supplier_words.intersection(amazon_words)
        
        if len(common_words) == 0 and idx < 10:  # Only check first 10 rows
            warnings.append({
                'row': idx,
                'type': 'Severe title mismatch',
                'detail': 'No common words between supplier and Amazon titles',
                'title': f"Supplier: {supplier_title[:50]} | Amazon: {amazon_title[:50]}"
            })

print(f"\nFound {len(warnings)} potential calibration warnings:\n")
for i, warning in enumerate(warnings[:15], 1):  # Show max 15 warnings
    print(f"{i}. Row {warning['row']}: {warning['type']}")
    print(f"   {warning['detail']}")
    print(f"   {warning['title']}\n")

# ====================================================================================
# OUTPUT: CONFIGURATION BLOCK
# ====================================================================================
print("\n" + "=" * 80)
print("CONFIGURATION OUTPUT")
print("=" * 80)

print("\n```python")
print("# --- CALIBRATION CONFIGURATION ---")
print("SUPPLIER_NAMING_CONVENTION = {")
print(f"    \"explicit_units\": {sorted(list(explicit_units_found))},  # Detected unit keywords")
print(f"    \"allow_trailing_number_as_qty\": {len(trailing_number_examples) > 0},  # Trailing numbers found: {len(trailing_number_examples)} examples")
print(f"    \"leading_multiplier_check\": {len(leading_multiplier_examples) > 0},  # Leading 'Nx' patterns found: {len(leading_multiplier_examples)} examples")
print(f"    \"dimension_shield_keywords\": {sorted(list(dimension_patterns))},  # Detected measurement units")
print(f"    \"brand_position\": \"{brand_position}\",  # Detected brand position")
print(f"    \"sales_column\": \"{detected_sales_column}\",  # Detected sales column")
print(f"    \"capacity_pattern_as_rsu\": {len(capacity_multipack_examples) > 0},  # 'N x Capacity' patterns found: {len(capacity_multipack_examples)} examples")
print(f"    \"spec_x_shield_keywords\": [\"magnification\", \"zoom\", \"microscope\", \"scope\", \"times\"],  # Spec features, not pack counts")
print(f"    \"table_pipe_sanitization\": True  # Replace '|' with '/' in output tables")
print("}")
print("# ---------------------------------")
print("```")

# ====================================================================================
# SUMMARY
# ====================================================================================
print("\n" + "=" * 80)
print("CALIBRATION SUMMARY")
print("=" * 80)

print(f"""
✓ Explicit pack units detected: {len(explicit_units_found)} types
✓ Trailing number patterns: {len(trailing_number_examples)} examples
✓ Leading multiplier patterns: {len(leading_multiplier_examples)} examples
✓ Capacity multipack patterns: {len(capacity_multipack_examples)} examples (e.g., '3 x 400ml')
✓ Dimension/measurement units: {len(dimension_patterns)} types
✓ Spec/feature multipliers: {len(spec_multiplier_examples)} examples (to shield from RSU)
✓ Sales column: {detected_sales_column}
✓ Brand position: {brand_position.upper()}
✓ Calibration warnings: {len(warnings)} potential issues identified

RECOMMENDATION:
- Use the configuration block above for the main analysis script
- Pay special attention to capacity multipacks (e.g., "3 x 400ml" = 3 units, NOT 1200)
- Shield spec multipliers (e.g., "2x magnification") from triggering RSU calculations
- Review calibration warnings for edge cases that may require manual override
""")

print("\n" + "=" * 80)
print("END OF CALIBRATION ANALYSIS")
print("=" * 80)
