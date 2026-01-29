import pandas as pd
import json

# Read all 4 Excel files
files = ['tanle 1 .xlsx', 'tanle 2.xlsx', 'tanle 3.xlsx', 'table 4.xlsx']

all_verified = []
all_likely = []
all_different = []

for f in files:
    df = pd.read_excel(f)
    # Normalize match status column
    status_col = None
    for c in df.columns:
        if 'match' in str(c).lower() and 'status' in str(c).lower():
            status_col = c
            break
    
    if status_col is None:
        for c in df.columns:
            if 'Match Status' in str(c):
                status_col = c
                break
    
    if status_col:
        for idx, row in df.iterrows():
            status = str(row.get(status_col, '')).upper()
            asin = str(row.get('ASIN', '')).strip()
            
            if pd.isna(asin) or asin == 'NAN' or asin == '' or len(asin) < 5:
                continue
            
            # Get supplier title from available columns
            supplier_title = ''
            for col in ['Supplier Title', 'supplier title', 'SupplierTitle']:
                if col in df.columns:
                    supplier_title = str(row.get(col, ''))
                    break
            
            entry = {
                'asin': asin,
                'supplier_title': supplier_title,
                'match_status': status,
                'source_file': f
            }
            
            if 'CONFIRM' in status:
                all_verified.append(entry)
            elif 'LIKELY' in status:
                all_likely.append(entry)
            elif 'DIFFERENT' in status or 'UNABLE' in status:
                all_different.append(entry)

print(f'CONFIRMED MATCHES: {len(all_verified)}')
print(f'LIKELY MATCHES: {len(all_likely)}')  
print(f'DIFFERENT/UNABLE: {len(all_different)}')

# Check for duplicates and conflicts
all_asins = {}
conflicts = []
for e in all_verified + all_likely + all_different:
    asin = e['asin']
    if asin in all_asins:
        if all_asins[asin]['match_status'] != e['match_status']:
            conflicts.append({
                'asin': asin,
                'file1': all_asins[asin]['source_file'],
                'status1': all_asins[asin]['match_status'],
                'file2': e['source_file'],
                'status2': e['match_status']
            })
    else:
        all_asins[asin] = e

print(f'\nUnique ASINs total: {len(all_asins)}')

if conflicts:
    print(f'\n!!! CONFLICTS FOUND ({len(conflicts)}):')
    for c in conflicts:
        print(f"  ASIN {c['asin']}: {c['file1']}={c['status1']} vs {c['file2']}={c['status2']}")
else:
    print('\nNo conflicts found - all duplicates have matching statuses.')

# Save consolidated data
output = {
    'verified': all_verified,
    'likely': all_likely,
    'different': all_different,
    'conflicts': conflicts
}

with open('consolidated_verification_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print('\nSaved to consolidated_verification_data.json')

# Print verified ASINs for reference
print('\n=== CONFIRMED MATCH ASINs ===')
for v in all_verified:
    print(f"  {v['asin']}: {v['supplier_title'][:60]}")
