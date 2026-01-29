"""
Pre-flight Calibration Analysis Script
Analyzes the financial report to detect supplier naming conventions and data patterns.
"""
import pandas as pd
import re
from pathlib import Path

# Configuration
INPUT_FILE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\part 3 jan.xlsx"
OUTPUT_DIR = Path(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 3 jan\opus 1")

# Read data
df = pd.read_excel(INPUT_FILE)
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Output file
output_file = OUTPUT_DIR / "calibration_output.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("PRE-FLIGHT CALIBRATION ANALYSIS\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Total rows: {len(df)}\n")
    f.write(f"Columns: {df.columns.tolist()}\n\n")
    
    # === TASK 1: PACK QUANTITY PATTERNS ===
    f.write("="*80 + "\n")
    f.write("TASK 1: PACK QUANTITY PATTERN ANALYSIS\n")
    f.write("="*80 + "\n\n")
    
    # Analyze first 60 rows
    sample_rows = min(60, len(df))
    
    # Pattern categories
    explicit_units = []
    trailing_numbers = []
    leading_multipliers = []
    dimension_patterns = []
    capacity_patterns = []
    spec_x_patterns = []
    
    for idx in range(sample_rows):
        row = df.iloc[idx]
        supplier_title = str(row.get('SupplierTitle', ''))
        amazon_title = str(row.get('AmazonTitle', ''))
        
        f.write(f"\n--- Row {idx} ---\n")
        f.write(f"Supplier: {supplier_title}\n")
        f.write(f"Amazon:   {amazon_title}\n")
        
        # Check for explicit units (pcs, pce, pk, pack, unit, set)
        explicit_match = re.findall(r'\b(\d+)\s*(pcs?|pce|pk|pack|unit|set|piece)\b', supplier_title, re.IGNORECASE)
        if explicit_match:
            explicit_units.append((idx, supplier_title, explicit_match))
            f.write(f"  -> EXPLICIT UNITS: {explicit_match}\n")
        
        # Check for trailing numbers (like "STICKS 200")
        trailing_match = re.search(r'\b([A-Za-z]+)\s+(\d{2,})\s*$', supplier_title)
        if trailing_match:
            trailing_numbers.append((idx, supplier_title, trailing_match.group()))
            f.write(f"  -> TRAILING NUMBER: {trailing_match.group()}\n")
        
        # Check for leading multipliers (like "10x Product")
        leading_match = re.match(r'^(\d+)\s*x\s+', supplier_title, re.IGNORECASE)
        if leading_match:
            leading_multipliers.append((idx, supplier_title, leading_match.group()))
            f.write(f"  -> LEADING MULTIPLIER: {leading_match.group()}\n")
        
        # Check for dimension patterns (like 20cm, 500ml, 9x9in)
        dim_match = re.findall(r'\b(\d+(?:\.\d+)?)\s*(cm|mm|ml|ltr|l|kg|g|oz|inch|in|"|\')\b', supplier_title, re.IGNORECASE)
        if dim_match:
            dimension_patterns.append((idx, supplier_title, dim_match))
            f.write(f"  -> DIMENSIONS: {dim_match}\n")
        
        # Check for dimension-like patterns (like 9x9, 20x30)
        dim_x_match = re.findall(r'\b(\d+)\s*x\s*(\d+)(?:\s*x\s*(\d+))?\s*(cm|mm|in|inch|"|\'|m)\b', supplier_title + ' ' + amazon_title, re.IGNORECASE)
        if dim_x_match:
            f.write(f"  -> DIMENSION 'x' PATTERN: {dim_x_match}\n")
        
        # TASK 1B: Capacity multipack patterns in Amazon title (like "3 x 400ml")
        capacity_match = re.findall(r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|ltr|kg|oz|cl)\b', amazon_title, re.IGNORECASE)
        if capacity_match:
            capacity_patterns.append((idx, amazon_title, capacity_match))
            f.write(f"  -> CAPACITY MULTIPACK: {capacity_match} (RSU = first number)\n")
        
        # TASK 1C: Spec/feature multipliers (like "2x Magnification")
        spec_match = re.findall(r'(\d+)\s*x\s*(magnification|zoom|power|brightness|strength|faster|stronger)', amazon_title, re.IGNORECASE)
        if spec_match:
            spec_x_patterns.append((idx, amazon_title, spec_match))
            f.write(f"  -> SPEC MULTIPLIER (NOT PACK): {spec_match}\n")
    
    # Summary of patterns
    f.write("\n\n" + "="*80 + "\n")
    f.write("PATTERN SUMMARY\n")
    f.write("="*80 + "\n\n")
    
    f.write(f"Explicit units found: {len(explicit_units)} rows\n")
    for item in explicit_units[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    f.write(f"\nTrailing numbers found: {len(trailing_numbers)} rows\n")
    for item in trailing_numbers[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    f.write(f"\nLeading multipliers found: {len(leading_multipliers)} rows\n")
    for item in leading_multipliers[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    f.write(f"\nDimension patterns found: {len(dimension_patterns)} rows\n")
    for item in dimension_patterns[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    f.write(f"\nCapacity multipack patterns found: {len(capacity_patterns)} rows\n")
    for item in capacity_patterns[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    f.write(f"\nSpec/feature multipliers found: {len(spec_x_patterns)} rows\n")
    for item in spec_x_patterns[:10]:
        f.write(f"  Row {item[0]}: {item[2]}\n")
    
    # === TASK 2: SALES SIGNAL ===
    f.write("\n\n" + "="*80 + "\n")
    f.write("TASK 2: SALES SIGNAL DETECTION\n")
    f.write("="*80 + "\n\n")
    
    # Check for sales-related columns
    sales_cols = [col for col in df.columns if 'sale' in col.lower() or 'bought' in col.lower()]
    f.write(f"Sales-related columns: {sales_cols}\n\n")
    
    for col in sales_cols:
        f.write(f"Column '{col}':\n")
        f.write(f"  Data type: {df[col].dtype}\n")
        f.write(f"  Sample values: {df[col].head(10).tolist()}\n")
        f.write(f"  Non-null count: {df[col].notna().sum()}\n")
        f.write(f"  Min: {df[col].min() if pd.api.types.is_numeric_dtype(df[col]) else 'N/A'}\n")
        f.write(f"  Max: {df[col].max() if pd.api.types.is_numeric_dtype(df[col]) else 'N/A'}\n\n")
    
    # === TASK 3: BRAND PATTERNS ===
    f.write("\n" + "="*80 + "\n")
    f.write("TASK 3: BRAND POSITION ANALYSIS\n")
    f.write("="*80 + "\n\n")
    
    # Common brand indicators - analyze first word patterns
    first_words = []
    for idx in range(min(100, len(df))):
        title = str(df.iloc[idx].get('SupplierTitle', ''))
        words = title.split()
        if words:
            first_words.append(words[0].upper())
    
    from collections import Counter
    word_counts = Counter(first_words)
    
    f.write("Most common first words in SupplierTitle (potential brands):\n")
    for word, count in word_counts.most_common(20):
        f.write(f"  {word}: {count} times\n")
    
    # Check for all-caps words at start (brand indicator)
    brand_at_start = 0
    brand_elsewhere = 0
    for idx in range(min(100, len(df))):
        title = str(df.iloc[idx].get('SupplierTitle', ''))
        words = title.split()
        if words and words[0].isupper() and len(words[0]) > 2:
            brand_at_start += 1
        elif any(w.isupper() and len(w) > 2 for w in words[1:]):
            brand_elsewhere += 1
    
    f.write(f"\nBrand at START (all caps first word): {brand_at_start}/{min(100, len(df))}\n")
    f.write(f"Brand ELSEWHERE (all caps word in middle/end): {brand_elsewhere}/{min(100, len(df))}\n")
    
    # === EXTENDED ANALYSIS ===
    f.write("\n\n" + "="*80 + "\n")
    f.write("EXTENDED PATTERN ANALYSIS (Full Dataset)\n")
    f.write("="*80 + "\n\n")
    
    # Search for specific unit keywords across ALL rows
    unit_keywords = {}
    for idx in range(len(df)):
        title = str(df.iloc[idx].get('SupplierTitle', '')).lower()
        for unit in ['pcs', 'pce', 'pk', 'pack', 'unit', 'set', 'piece', 'each']:
            if unit in title:
                if unit not in unit_keywords:
                    unit_keywords[unit] = 0
                unit_keywords[unit] += 1
    
    f.write("Unit keywords found in ALL SupplierTitles:\n")
    for unit, count in sorted(unit_keywords.items(), key=lambda x: -x[1]):
        f.write(f"  '{unit}': {count} occurrences\n")
    
    # Search for dimension keywords
    dim_keywords = {}
    for idx in range(len(df)):
        title = str(df.iloc[idx].get('SupplierTitle', '')).lower()
        for dim in ['cm', 'mm', 'ml', 'ltr', 'l', 'kg', 'g', 'oz', 'inch', 'in']:
            pattern = r'\b\d+\s*' + re.escape(dim) + r'\b'
            if re.search(pattern, title):
                if dim not in dim_keywords:
                    dim_keywords[dim] = 0
                dim_keywords[dim] += 1
    
    f.write("\nDimension/measurement keywords found:\n")
    for dim, count in sorted(dim_keywords.items(), key=lambda x: -x[1]):
        f.write(f"  '{dim}': {count} occurrences\n")
    
    # === TASK 4: CALIBRATION WARNINGS ===
    f.write("\n\n" + "="*80 + "\n")
    f.write("TASK 4: CALIBRATION WARNINGS (Potential Traps)\n")
    f.write("="*80 + "\n\n")
    
    warnings = []
    
    for idx in range(len(df)):
        row = df.iloc[idx]
        supplier_title = str(row.get('SupplierTitle', ''))
        amazon_title = str(row.get('AmazonTitle', ''))
        combined = supplier_title + ' ' + amazon_title
        
        # Check for dimension traps (9x9, 20x30 that look like quantities)
        dim_trap = re.search(r'\b(\d+)\s*x\s*(\d+)\s*(in|inch|cm|mm|")\b', combined, re.IGNORECASE)
        if dim_trap:
            warnings.append((idx, 'DIMENSION TRAP', f"'{dim_trap.group()}' should be RSU=1 (dimensions), not RSU={int(dim_trap.group(1))*int(dim_trap.group(2))}"))
        
        # Check for model number traps (SOUDAL 750, WD-40 400)
        model_trap = re.search(r'\b([A-Z]+[-\s]?\d{3,4})\b', supplier_title)
        if model_trap and not re.search(r'(ml|g|l|pack|pcs)', supplier_title, re.IGNORECASE):
            # Only warn if no unit indicator nearby
            warnings.append((idx, 'MODEL NUMBER TRAP', f"'{model_trap.group()}' might be model number, not capacity"))
        
        # Check for capacity multipack traps (3 x 400ml should be RSU=3, not 1200)
        cap_trap = re.search(r'(\d+)\s*x\s*(\d+)\s*(ml|g|l|ltr|kg|oz|cl)\b', amazon_title, re.IGNORECASE)
        if cap_trap:
            wrong_rsu = int(cap_trap.group(1)) * int(cap_trap.group(2))
            correct_rsu = int(cap_trap.group(1))
            if wrong_rsu != correct_rsu:
                warnings.append((idx, 'CAPACITY MULTIPACK', f"'{cap_trap.group()}' should be RSU={correct_rsu} (bottles/units), not RSU={wrong_rsu}"))
        
        # Check for quantity-inside traps (STICKS 200, PINS 100)
        qty_inside_trap = re.search(r'\b(STICKS?|PINS?|NAILS?|SCREWS?|PEGS?|CLIPS?|PICKS?)\s+(\d{2,})\b', supplier_title, re.IGNORECASE)
        if qty_inside_trap:
            warnings.append((idx, 'QUANTITY-INSIDE TRAP', f"'{qty_inside_trap.group()}' should be 1 pack of {qty_inside_trap.group(2)}, not {qty_inside_trap.group(2)} packs"))
        
        # Check for nested pack patterns (4 x 50)
        nested_pack = re.search(r'\((\d+)\s*x\s*(\d+)\)', combined)
        if nested_pack:
            total = int(nested_pack.group(1)) * int(nested_pack.group(2))
            warnings.append((idx, 'NESTED PACK', f"'{nested_pack.group()}' means {total} total items in one pack"))
    
    f.write(f"Found {len(warnings)} potential traps:\n\n")
    for idx, trap_type, message in warnings[:50]:  # Limit to first 50
        f.write(f"Row {idx}: [{trap_type}] {message}\n")
    
    # Print file location
    print(f"\nOutput written to: {output_file}")

print("\nAnalysis complete!")
