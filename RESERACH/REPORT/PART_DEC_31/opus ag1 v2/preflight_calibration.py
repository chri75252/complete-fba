import pandas as pd
import re

# Read first 50 rows
df = pd.read_csv('PART_DEC_31.csv', nrows=50, encoding='utf-8-sig')

with open('calibration_analysis.txt', 'w', encoding='utf-8') as f:
    f.write('=== TASK 1: PACK QUANTITY PATTERNS ===\n\n')
    f.write('--- SupplierTitle vs AmazonTitle ---\n\n')
    
    for i in range(min(50, len(df))):
        sup = str(df['SupplierTitle'].iloc[i]) if pd.notna(df['SupplierTitle'].iloc[i]) else 'N/A'
        amz = str(df['AmazonTitle'].iloc[i]) if pd.notna(df['AmazonTitle'].iloc[i]) else 'N/A'
        f.write(f'Row {i}:\n')
        f.write(f'  SUP: {sup}\n')
        f.write(f'  AMZ: {amz}\n\n')
    
    # Pattern detection
    f.write('\n=== PATTERN DETECTION ===\n\n')
    
    # Check for explicit units
    explicit_units_found = set()
    unit_patterns = ['pcs', 'pce', 'pk', 'pack', 'unit', 'units', 'pieces', 'sheets', 'rolls']
    for title in df['SupplierTitle'].dropna():
        title_lower = str(title).lower()
        for unit in unit_patterns:
            if re.search(rf'\b{unit}\b', title_lower) or re.search(rf'\d+\s*{unit}', title_lower):
                explicit_units_found.add(unit)
    
    f.write(f'Explicit units found: {list(explicit_units_found)}\n\n')
    
    # Check for trailing numbers
    trailing_number_examples = []
    for i, title in enumerate(df['SupplierTitle'].dropna()):
        title_str = str(title).strip()
        # Pattern: ends with a number (not preceded by unit keywords)
        match = re.search(r'\s+(\d+)$', title_str)
        if match:
            num = int(match.group(1))
            if num >= 2 and num <= 1000:  # Reasonable pack quantity range
                trailing_number_examples.append((i, title_str, num))
    
    f.write(f'Trailing number examples (potential pack quantities):\n')
    for idx, title, num in trailing_number_examples[:10]:
        f.write(f'  Row {idx}: "{title}" -> trailing number: {num}\n')
    f.write(f'\nTotal trailing number count: {len(trailing_number_examples)}\n\n')
    
    # Check for leading multipliers
    leading_multiplier_examples = []
    for i, title in enumerate(df['SupplierTitle'].dropna()):
        title_str = str(title).strip()
        # Pattern: starts with NxProduct or N x Product
        match = re.match(r'^(\d+)\s*[xX]\s+', title_str)
        if match:
            leading_multiplier_examples.append((i, title_str, int(match.group(1))))
    
    f.write(f'Leading multiplier examples:\n')
    for idx, title, num in leading_multiplier_examples[:10]:
        f.write(f'  Row {idx}: "{title}" -> leading multiplier: {num}\n')
    f.write(f'\nTotal leading multiplier count: {len(leading_multiplier_examples)}\n\n')
    
    # Check dimension patterns
    dimension_examples = []
    dimension_patterns = [
        r'\d+\s*cm', r'\d+\s*mm', r'\d+\s*ml', r'\d+\s*ltr', r'\d+\s*l\b',
        r'\d+\s*kg', r'\d+\s*g\b', r'\d+\s*oz', r'\d+\s*inch', r'\d+\s*in\b',
        r'\d+\s*x\s*\d+\s*x\s*\d+',  # 3D dimensions like 10x5x2
    ]
    
    for i, title in enumerate(df['SupplierTitle'].dropna()):
        title_str = str(title).strip()
        for pattern in dimension_patterns:
            if re.search(pattern, title_str.lower()):
                dimension_examples.append((i, title_str))
                break
    
    f.write(f'Dimension pattern examples:\n')
    for idx, title in dimension_examples[:10]:
        f.write(f'  Row {idx}: "{title}"\n')
    f.write(f'\nTotal dimension pattern count: {len(dimension_examples)}\n\n')
    
    # TASK 2: Sales column detection
    f.write('\n=== TASK 2: SALES COLUMN DETECTION ===\n\n')
    
    sales_columns = ['bought_in_past_month', 'sales_numeric', 'Sales']
    for col in sales_columns:
        if col in df.columns:
            f.write(f"Column '{col}' exists: YES\n")
            sample = df[col].head(10).tolist()
            f.write(f"  Sample values: {sample}\n")
            f.write(f"  Data type: {df[col].dtype}\n")
            
            # Check for text that needs parsing
            sample_strs = [str(v) for v in sample if pd.notna(v)]
            has_text = any(re.search(r'[a-zA-Z+]', s) for s in sample_strs)
            f.write(f"  Contains text needing parsing: {has_text}\n\n")
        else:
            f.write(f"Column '{col}' exists: NO\n\n")
    
    # TASK 3: Brand pattern detection
    f.write('\n=== TASK 3: BRAND PATTERN DETECTION ===\n\n')
    
    brand_at_start = 0
    brand_examples = []
    for i, title in enumerate(df['SupplierTitle'].dropna()):
        title_str = str(title).strip()
        # Check if first word is all caps (likely a brand)
        first_word = title_str.split()[0] if title_str.split() else ''
        if first_word.isupper() and len(first_word) > 2 and first_word.isalpha():
            brand_at_start += 1
            if len(brand_examples) < 10:
                brand_examples.append((i, title_str, first_word))
    
    f.write(f'Brand at start count: {brand_at_start} out of {len(df["SupplierTitle"].dropna())}\n')
    f.write(f'Brand at start percentage: {brand_at_start / len(df["SupplierTitle"].dropna()) * 100:.1f}%\n\n')
    f.write(f'Examples:\n')
    for idx, title, brand in brand_examples:
        f.write(f'  Row {idx}: Brand="{brand}" | "{title}"\n')
    
    # TASK 4: Potential data traps
    f.write('\n\n=== TASK 4: CALIBRATION WARNINGS - POTENTIAL DATA TRAPS ===\n\n')
    
    traps = []
    for i, title in enumerate(df['SupplierTitle'].dropna()):
        title_str = str(title).strip()
        
        # Model numbers that look like quantities
        if re.search(r'\b[A-Z]+\s*\d{2,4}\b', title_str) and not re.search(r'\d+\s*(pcs|pk|pack)', title_str.lower()):
            traps.append((i, title_str, 'Model number may look like quantity'))
        
        # Mixed dimension and quantity patterns
        if re.search(r'\d+\s*x\s*\d+', title_str.lower()) and re.search(r'\d+\s*(cm|mm|ml)', title_str.lower()):
            traps.append((i, title_str, 'Mixed dimensions - could confuse pack detection'))
    
    for idx, title, warning in traps[:15]:
        f.write(f'Row {idx}: "{title}"\n  WARNING: {warning}\n\n')

print('Analysis complete. Output saved to calibration_analysis.txt')
