import pandas as pd
import re

df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')

# Analyze brand patterns
supplier_titles = df['SupplierTitle'].dropna().tolist()

# Known brand patterns in titles
brand_keywords = ['EUROWRAP', 'DLUX', 'MINKY', 'STARWASH', 'STATUS', 'CHEF AID', 'PROKLEEN', 'TALA', 
                  'PRIMA', 'PANASONIC', 'AIRWICK', 'FAIRY', 'DUNLOP', 'DEKTON', 'BETTINA',
                  'ABBEY', 'LYNWOOD', 'SECURPAK', 'APAC', 'PALOMA', 'MASON', 'GIFTMAKER', 'KOOPMAN']

brand_start = 0
brand_end = 0
brand_middle = 0

for title in supplier_titles[:500]:  # Sample 500
    t = str(title).upper()
    for brand in brand_keywords:
        if brand.upper() in t:
            pos = t.find(brand.upper())
            if pos == 0:
                brand_start += 1
            elif pos > len(t) // 2:
                brand_end += 1
            else:
                brand_middle += 1
            break

output_lines = []
output_lines.append('Brand position analysis (sample 500):')
output_lines.append(f'  Start: {brand_start}')
output_lines.append(f'  Middle: {brand_middle}')
output_lines.append(f'  End: {brand_end}')

# Analyze potential traps
output_lines.append('\n--- POTENTIAL TRAPS ---')

# Model number traps (numbers that look like capacities/quantities but aren't)
model_traps = []
for i, title in enumerate(supplier_titles[:100]):
    t = str(title).upper()
    # Numbers after brand names that might be model numbers
    if re.search(r'[A-Z]+\s+\d{3,}(?!\s*(ML|G|KG|L|PCS|PACK|PC))', t):
        match = re.search(r'([A-Z]+\s+\d{3,})', t)
        if match:
            model_traps.append((i, title, match.group(1)))

output_lines.append('\nModel number traps (first 10):')
for trap in model_traps[:10]:
    output_lines.append(f'  Row {trap[0]}: {trap[1]} -> {trap[2]}')

# Dimension traps (NxN patterns)
dim_traps = []
for i, title in enumerate(supplier_titles[:200]):
    t = str(title).upper()
    # Look for NxN that could be confused as multipliers
    if re.search(r'\d+\s*X\s*\d+\s*(CM|MM|IN|INCH|\")', t):
        match = re.search(r'(\d+\s*X\s*\d+\s*(CM|MM|IN|INCH|\"))', t)
        if match:
            dim_traps.append((i, title, match.group(1)))

output_lines.append('\nDimension traps (first 10):')
for trap in dim_traps[:10]:
    output_lines.append(f'  Row {trap[0]}: {trap[1]} -> {trap[2]}')

# Quantity-inside traps (patterns like "STICKS 200" where 200 is quantity in pack, not 200 packs)
qty_inside_traps = []
for i, title in enumerate(supplier_titles[:200]):
    t = str(title).upper()
    # Look for keywords followed by large numbers
    if re.search(r'(STICKS?|CARDS?|PICKS?|PEGS?|NAPKINS?|CASES?|CLIPS?|PINS?|SCREWS?)\s+(\d{2,})', t):
        match = re.search(r'(STICKS?|CARDS?|PICKS?|PEGS?|NAPKINS?|CASES?|CLIPS?|PINS?|SCREWS?)\s+(\d{2,})', t)
        if match:
            qty_inside_traps.append((i, title, match.group(0)))

output_lines.append('\nQuantity-inside traps (first 15):')
for trap in qty_inside_traps[:15]:
    output_lines.append(f'  Row {trap[0]}: {trap[1]} -> {trap[2]}')

# Write to file
output_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\opu v1.1\_brand_trap_analysis.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print('Analysis saved to:', output_path)
