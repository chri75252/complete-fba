import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')

# Analyze supplier titles for patterns
supplier_titles = df['SupplierTitle'].dropna().tolist()
amazon_titles = df['AmazonTitle'].dropna().tolist()

# Pattern detection counters
explicit_units = {'pcs': 0, 'pk': 0, 'pack': 0, 'piece': 0, 'pieces': 0, 'pce': 0}
trailing_numbers = []
leading_multipliers = []
dimension_patterns = []
capacity_patterns = []
multipack_capacity_patterns = []  # For "3 x 400ml" patterns

for title in supplier_titles:
    t = str(title).upper()
    
    # Explicit units
    for unit in explicit_units:
        if re.search(r'\b' + unit.upper() + r'\b', t):
            explicit_units[unit] += 1
    
    # Trailing numbers (e.g., 'STICKS 200')
    match = re.search(r'\s(\d+)\s*$', t)
    if match:
        trailing_numbers.append((title, match.group(1)))
    
    # Leading multipliers (e.g., '10x Product')
    match = re.search(r'^(\d+)\s*[xX]\s+', t)
    if match:
        leading_multipliers.append((title, match.group(1)))
    
    # Dimension patterns (e.g., '9x9', '20cm')
    if re.search(r'\d+\s*[xX]\s*\d+\s*(CM|MM|IN|INCH|\")', t, re.IGNORECASE):
        dimension_patterns.append(title)
    
    # Capacity patterns (e.g., '500ML', '1L')
    if re.search(r'\d+\s*(ML|L|LTR|G|KG|OZ)\b', t, re.IGNORECASE):
        capacity_patterns.append(title)

# Analyze Amazon titles for multipack capacity patterns (e.g., "3 x 400ml")
for title in amazon_titles:
    t = str(title)
    match = re.search(r'(\d+)\s*[xX]\s*(\d+)\s*(ml|g|l|kg|oz)\b', t, re.IGNORECASE)
    if match:
        multipack_capacity_patterns.append((title[:80], match.group(0)))

output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\opu v1.1\_pattern_analysis.txt'

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('=== EXPLICIT UNIT COUNTS ===\n')
    for k, v in explicit_units.items():
        f.write(f'{k}: {v}\n')
    
    f.write('\n=== TRAILING NUMBERS (first 30) ===\n')
    for item in trailing_numbers[:30]:
        f.write(f'{item}\n')
    f.write(f'Total count: {len(trailing_numbers)}\n')
    
    f.write('\n=== LEADING MULTIPLIERS (first 20) ===\n')
    for item in leading_multipliers[:20]:
        f.write(f'{item}\n')
    f.write(f'Total count: {len(leading_multipliers)}\n')
    
    f.write('\n=== DIMENSION PATTERNS (first 20) ===\n')
    for item in dimension_patterns[:20]:
        f.write(f'{item}\n')
    f.write(f'Total count: {len(dimension_patterns)}\n')
    
    f.write('\n=== CAPACITY PATTERNS (first 30) ===\n')
    for item in capacity_patterns[:30]:
        f.write(f'{item}\n')
    f.write(f'Total count: {len(capacity_patterns)}\n')
    
    f.write('\n=== AMAZON MULTIPACK CAPACITY PATTERNS (N x Capacity) - first 30 ===\n')
    for item in multipack_capacity_patterns[:30]:
        f.write(f'{item}\n')
    f.write(f'Total count: {len(multipack_capacity_patterns)}\n')

print('Pattern analysis saved to:', output_path)
