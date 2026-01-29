import pandas as pd

# Load the analysis
df = pd.read_csv('ground_truth_analysis.csv', index_col=0)

# Print summary
output = []
output.append('GROUND TRUTH SUMMARY')
output.append('='*60)
counts = df['verdict'].value_counts()
output.append(str(counts))
output.append('')

# Show verified items
verified = df[df['verdict'] == 'VERIFIED']
output.append(f'VERIFIED ({len(verified)} items):')
output.append('-'*60)
for idx, row in verified.iterrows():
    title = str(row['SupplierTitle'])[:50]
    ean = row['EAN']
    profit = row['NetProfit']
    output.append(f'{idx}: {title} | EAN: {ean} | Profit: {profit}')

output.append('')

# Show highly likely items  
hl = df[df['verdict'] == 'HIGHLY_LIKELY']
output.append(f'HIGHLY LIKELY ({len(hl)} items):')
output.append('-'*60)
for idx, row in hl.head(50).iterrows():
    title = str(row['SupplierTitle'])[:50]
    sim = row['title_similarity']
    profit = row['NetProfit']
    output.append(f'{idx}: {title} | Sim: {sim:.2f} | Profit: {profit}')

output.append('')

# Show needs verification items (top 30)
nv = df[df['verdict'] == 'NEEDS_VERIFICATION'].sort_values('NetProfit', ascending=False)
output.append(f'NEEDS VERIFICATION ({len(nv)} items - showing top 30):')
output.append('-'*60)
for idx, row in nv.head(30).iterrows():
    title = str(row['SupplierTitle'])[:50]
    profit = row['NetProfit']
    sim = row['title_similarity']
    output.append(f'{idx}: {title} | Sim: {sim:.2f} | Profit: {profit}')

# Write to file
with open('ground_truth_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print(f"Written to ground_truth_summary.txt")
print(f"\nCategory Counts:")
print(counts)
