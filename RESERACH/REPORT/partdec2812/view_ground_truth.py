import pandas as pd

# Load the analysis
df = pd.read_csv('ground_truth_analysis.csv', index_col=0)

# Print summary
print('GROUND TRUTH SUMMARY')
print('='*60)
counts = df['verdict'].value_counts()
print(counts)
print()

# Show verified items
verified = df[df['verdict'] == 'VERIFIED']
print(f'VERIFIED ({len(verified)} items):')
print('-'*60)
for idx, row in verified.iterrows():
    title = str(row['SupplierTitle'])[:45]
    ean = row['EAN']
    profit = row['NetProfit']
    print(f'{idx}: {title} | EAN: {ean} | Profit: {profit}')

print()

# Show highly likely items  
hl = df[df['verdict'] == 'HIGHLY_LIKELY']
print(f'HIGHLY LIKELY ({len(hl)} items):')
print('-'*60)
for idx, row in hl.head(30).iterrows():
    title = str(row['SupplierTitle'])[:45]
    sim = row['title_similarity']
    print(f'{idx}: {title} | Sim: {sim:.2f}')

print()

# Show needs verification items (top 20)
nv = df[df['verdict'] == 'NEEDS_VERIFICATION'].sort_values('NetProfit', ascending=False)
print(f'NEEDS VERIFICATION ({len(nv)} items - showing top 20):')
print('-'*60)
for idx, row in nv.head(20).iterrows():
    title = str(row['SupplierTitle'])[:45]
    profit = row['NetProfit']
    print(f'{idx}: {title} | Profit: {profit}')

print()

# Show filtered out with exact EAN or brand match
fo = df[df['verdict'] == 'FILTERED_OUT']
print(f'FILTERED OUT ({len(fo)} total):')
