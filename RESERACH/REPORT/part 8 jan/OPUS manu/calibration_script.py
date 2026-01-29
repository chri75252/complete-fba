import pandas as pd
import re
import json

# Load data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx', nrows=50)

print("=" * 60)
print("AGENTIC FBA CALIBRATION ANALYSIS - PART 8 JAN")
print("=" * 60)

# ================ TASK 1: PACK QUANTITY PATTERNS ================
print("\n" + "=" * 60)
print("TASK 1: PACK QUANTITY PATTERNS")
print("=" * 60)

unit_patterns_found = set()
trailing_nums = []
dimension_examples = []
capacity_examples = []
leading_multipliers = []

for i, row in df.iterrows():
    sup = str(row['SupplierTitle']).upper()
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    
    # 1. Explicit units (pcs, pk, pack, pieces, pc)
    expl = re.findall(r'(\d+)\s*(PCS|PCE|PK|PACK|PIECES|PC)\b', sup, re.I)
    if expl:
        for num, unit in expl:
            unit_patterns_found.add(unit.upper())
        
    # 2. Trailing numbers
    trail = re.search(r'\b(\d+)\s*$', sup)
    if trail:
        trailing_nums.append((i, trail.group(1), sup))
        
    # 3. Leading multipliers (10x Product)
    lead = re.search(r'^(\d+)\s*[xX]\s+', sup)
    if lead:
        leading_multipliers.append((i, lead.group(1), sup))
        
    # 4. Dimensions
    dims = re.findall(r'(\d+\.?\d*)\s*(CM|MM|INCH|")', sup, re.I)
    if dims:
        dimension_examples.append((i, dims, sup))
        
    # 5. Capacity
    caps = re.findall(r'(\d+\.?\d*)\s*(ML|LTR|L|G|KG|OZ)\b', sup, re.I)
    if caps:
        capacity_examples.append((i, caps, sup))

print(f"\n1. EXPLICIT UNIT KEYWORDS FOUND: {unit_patterns_found if unit_patterns_found else 'None'}")

print(f"\n2. TRAILING NUMBERS ({len(trailing_nums)} found):")
for r, num, title in trailing_nums[:10]:
    print(f"   Row {r}: '{num}' in '{title}'")
    
print(f"\n3. LEADING MULTIPLIERS ({len(leading_multipliers)} found):")
for r, num, title in leading_multipliers[:10]:
    print(f"   Row {r}: '{num}x' in '{title}'")

print(f"\n4. DIMENSION EXAMPLES ({len(dimension_examples)} found):")
for r, d, title in dimension_examples[:10]:
    print(f"   Row {r}: {d} in '{title}'")

print(f"\n5. CAPACITY EXAMPLES ({len(capacity_examples)} found):")
for r, c, title in capacity_examples[:10]:
    print(f"   Row {r}: {c} in '{title}'")

# ================ TASK 1B: CAPACITY MULTIPACK PATTERNS ================
print("\n" + "=" * 60)
print("TASK 1B: CAPACITY MULTIPACK PATTERNS")
print("=" * 60)

capacity_multipacks = []
for i, row in df.iterrows():
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    sup = str(row['SupplierTitle']).upper()
    
    # Pattern: N x [capacity]ml/g/l
    cap_multi = re.search(r'(\d+)\s*[xX]\s*(\d+)\s*(ML|G|L|KG|OZ)\b', amz + " " + sup)
    if cap_multi:
        capacity_multipacks.append((i, cap_multi.group(0), sup, amz[:80]))

print(f"\nCapacity Multipack Patterns Found ({len(capacity_multipacks)}):")
for r, pattern, sup, amz in capacity_multipacks[:10]:
    print(f"   Row {r}: Pattern='{pattern}'")
    print(f"      SUP: {sup}")
    print(f"      AMZ: {amz}")

# ================ TASK 1C: NON-PACK Nx SPEC PATTERNS ================
print("\n" + "=" * 60)
print("TASK 1C: NON-PACK 'Nx' SPEC/FEATURE PATTERNS")
print("=" * 60)

spec_x_patterns = []
spec_keywords = ['MAGNIFICATION', 'ZOOM', 'MICROSCOPE', 'SCOPE', 'TIMES', 'STRONGER', 'BRIGHTER']
for i, row in df.iterrows():
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    sup = str(row['SupplierTitle']).upper()
    
    combined = sup + " " + amz
    # Look for Nx near spec keywords
    for kw in spec_keywords:
        if kw in combined:
            nx = re.search(r'(\d+)[xX]', combined)
            if nx:
                spec_x_patterns.append((i, nx.group(0), kw, sup[:60]))

print(f"\nSpec/Feature 'Nx' Patterns Found ({len(spec_x_patterns)}):")
for r, pattern, kw, title in spec_x_patterns[:10]:
    print(f"   Row {r}: Pattern='{pattern}' near keyword '{kw}' in '{title}'")

# ================ TASK 2: SALES SIGNAL ================
print("\n" + "=" * 60)
print("TASK 2: SALES SIGNAL DETECTION")
print("=" * 60)

# Check available columns
sales_cols = ['bought_in_past_month', 'sales_numeric', 'Sales']
found_sales_col = None
for col in sales_cols:
    if col in df.columns:
        found_sales_col = col
        sample_vals = df[col].head(10).tolist()
        print(f"\nFound column: '{col}'")
        print(f"Sample values: {sample_vals}")
        print(f"Data type: {df[col].dtype}")
        break

# ================ TASK 3: BRAND PATTERNS ================
print("\n" + "=" * 60)
print("TASK 3: BRAND PATTERN DETECTION")
print("=" * 60)

# Known brand list
known_brands = ['MINKY', 'CHEF AID', 'TALA', 'PANASONIC', 'DUNLOP', 'AIRWICK', 'TONKITA', 
                'PROKLEEN', 'DEKTON', 'GRAFIX', 'EUROWRAP', 'STATUS', 'TOM SMITH', 'LYNWOOD',
                'PRIMA', 'SECURPAK', 'STARWASH', 'DLUX', 'RSW']

brand_in_supplier = 0
brand_in_amazon = 0
brand_at_start = 0

for i, row in df.iterrows():
    sup = str(row['SupplierTitle']).upper()
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    
    for brand in known_brands:
        if brand in sup:
            brand_in_supplier += 1
            if sup.startswith(brand):
                brand_at_start += 1
            break
    
    for brand in known_brands:
        if brand in amz:
            brand_in_amazon += 1
            break

print(f"\nBrand presence in Supplier Titles: {brand_in_supplier}/{len(df)} ({100*brand_in_supplier/len(df):.1f}%)")
print(f"Brand presence in Amazon Titles: {brand_in_amazon}/{len(df)} ({100*brand_in_amazon/len(df):.1f}%)")
print(f"Brand at START of Supplier Title: {brand_at_start}/{len(df)} ({100*brand_at_start/len(df):.1f}%)")

# ================ CRITICAL: MISMATCH ANALYSIS ================
print("\n" + "=" * 60)
print("CRITICAL: SUPPLIER vs AMAZON TITLE MISMATCH ANALYSIS")
print("=" * 60)

mismatch_count = 0
match_count = 0
for i, row in df.iterrows():
    sup = str(row['SupplierTitle']).upper()
    amz = str(row['AmazonTitle']).upper() if pd.notna(row['AmazonTitle']) else ""
    
    sup_words = set([w for w in re.findall(r'[A-Z]{4,}', sup)])
    amz_words = set([w for w in re.findall(r'[A-Z]{4,}', amz)])
    
    overlap = sup_words.intersection(amz_words)
    
    if len(overlap) == 0:
        mismatch_count += 1
    else:
        match_count += 1

print(f"\nRows with NO word overlap (likely mismatches): {mismatch_count}/{len(df)} ({100*mismatch_count/len(df):.1f}%)")
print(f"Rows with SOME word overlap (potential matches): {match_count}/{len(df)} ({100*match_count/len(df):.1f}%)")

# ================ TASK 4: CALIBRATION WARNINGS ================
print("\n" + "=" * 60)
print("TASK 4: CALIBRATION WARNINGS")
print("=" * 60)

warnings = []

# Warning 1: High mismatch rate
if mismatch_count / len(df) > 0.5:
    warnings.append(f"CRITICAL: {100*mismatch_count/len(df):.1f}% of rows have NO word overlap between SupplierTitle and AmazonTitle. This dataset has severe EAN-to-ASIN mapping issues. Most Amazon titles appear to be wrong products!")

# Warning 2: Trailing numbers that might be model numbers
for r, num, title in trailing_nums:
    # Check if the trailing number is part of a model number pattern
    if re.search(r'[A-Z]+\s*' + num + r'\s*$', title):
        warnings.append(f"Row {r}: Trailing '{num}' might be part of model number in '{title}'")
    elif int(num) in [1, 2, 3, 4, 5, 6]:
        warnings.append(f"Row {r}: Trailing '{num}' might be variant number, not quantity, in '{title}'")

# Warning 3: Dimension values that could be confused with quantity
for r, dims, title in dimension_examples:
    for val, unit in dims:
        if float(val) <= 20 and unit.upper() in ['CM', 'M']:
            warnings.append(f"Row {r}: Small dimension '{val}{unit}' could be confused with quantity in '{title}'")

print("\nWARNINGS:")
for w in warnings[:15]:
    print(f"  - {w}")

# ================ FINAL CONFIGURATION OUTPUT ================
print("\n" + "=" * 60)
print("FINAL CALIBRATION CONFIGURATION")
print("=" * 60)

config = f'''
# --- CALIBRATION CONFIGURATION (part 8 jan.xlsx) ---
SUPPLIER_NAMING_CONVENTION = {{
    "explicit_units": {list(unit_patterns_found) if unit_patterns_found else ["pcs", "pk", "pack", "pieces", "pc"]},
    "allow_trailing_number_as_qty": False,  # DANGEROUS - trailing numbers are often variant codes (e.g., "GIRL 3")
    "leading_multiplier_check": {len(leading_multipliers) > 0},
    "dimension_shield_keywords": ["cm", "mm", "ml", "ltr", "kg", "g", "oz", "inch", "m"],
    "brand_position": "start",  # Brands like MINKY, CHEF AID, TALA appear at start
    "brand_in_supplier_usually_present": {brand_in_supplier/len(df) > 0.3},
    "brand_in_amazon_usually_present": {brand_in_amazon/len(df) > 0.3},
    "brand_format_patterns": ["ALL_CAPS_AT_START"],
    "brand_sparse_supplier_mode": True,  # Amazon titles rarely have matching brand
    "strong_similarity_threshold": 0.20,  # LOW due to high mismatch rate
    "strong_shared_tokens_threshold": 2,  # LOW due to high mismatch rate
    "very_strong_similarity_threshold": 0.30,
    "very_strong_shared_tokens_threshold": 3,
    "gate_mode": "C_brand_sparse",  # Use sparse mode due to title mismatches
    "sales_column": "{found_sales_col}",
    "capacity_pattern_as_rsu": True,  # "3 x 400ml" means RSU=3
    "spec_x_shield_keywords": ["magnification", "zoom", "microscope", "scope", "times"],
    "table_pipe_sanitization": True,
    
    # CRITICAL WARNING FLAGS
    "high_mismatch_rate": True,  # {mismatch_count}/{len(df)} rows have no title overlap
    "mismatch_percentage": {100*mismatch_count/len(df):.1f},
    "require_strict_ean_validation": True,  # EAN validity is the only reliable link
}}
# ---------------------------------
'''

print(config)

# Save to file
output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\OPUS manu\CALIBRATION_CONFIG.py'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(config)
print(f"\nConfiguration saved to: {output_path}")
