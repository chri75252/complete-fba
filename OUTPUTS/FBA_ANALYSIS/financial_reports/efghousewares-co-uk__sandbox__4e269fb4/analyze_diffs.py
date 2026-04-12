import pandas as pd

files = {
    '050818 (Mar30)': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260330_050818.csv',
    '120126 (12:01)': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_120126.csv',
    '141308 (14:13)': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_141308.csv',
    '163421 (16:34)': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_163421.csv',
    '182449 (18:24)': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_182449.csv'
}

dfs = {}
for name, f in files.items():
    dfs[name] = pd.read_csv(f)
    dfs[name]['key'] = dfs[name]['EAN'].astype(str) + '|' + dfs[name]['ASIN'].astype(str)

print('=== INCREMENTAL ANALYSIS ===')
prev_keys = None
for name, df in dfs.items():
    keys = set(df['key'])
    if prev_keys is None:
        print(name + ': ' + str(len(keys)) + ' rows (baseline)')
    else:
        new_keys = keys - prev_keys
        removed_keys = prev_keys - keys
        print(name + ': ' + str(len(keys)) + ' rows, +' + str(len(new_keys)) + ' new, -' + str(len(removed_keys)) + ' removed')
    prev_keys = keys

print()
print('=== FINANCIAL METRICS COMPARISON (Sample) ===')
# Compare key metrics for rows present in all files
metric_cols = ['SupplierPrice_exVAT', 'SellingPrice_incVAT', 'ReferralFee', 'FBAFee', 'PrepHouseFee', 'NetProfit', 'ROI', 'ProfitMargin']

for name, df in dfs.items():
    if len(df) > 10:  # Skip tiny files
        print(name)
        for col in metric_cols:
            if col in df.columns:
                print('  ' + col + ': mean=' + '{:.2f}'.format(df[col].mean()) + ', min=' + '{:.2f}'.format(df[col].min()) + ', max=' + '{:.2f}'.format(df[col].max()))
        break  # Just show one detailed example
