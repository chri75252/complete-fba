import pandas as pd

files = {
    '050818': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260330_050818.csv',
    '120126': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_120126.csv',
    '141308': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_141308.csv',
    '163421': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_163421.csv',
    '182449': 'fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_20260408_182449.csv'
}

dfs = {}
for name, f in files.items():
    dfs[name] = pd.read_csv(f)
    print(name + ': ' + str(len(dfs[name])) + ' rows')

print()
all_df = pd.concat(dfs.values(), ignore_index=True)
print('Total rows before dedup: ' + str(len(all_df)))

all_df['key'] = all_df['EAN'].astype(str) + '|' + all_df['ASIN'].astype(str)
all_df_deduped = all_df.drop_duplicates(subset=['key'], keep='last')
print('Total rows after dedup: ' + str(len(all_df_deduped)))

output_path = 'fba_financial_report_MERGED_DEDUPED.csv'
all_df_deduped.drop(columns=['key']).to_csv(output_path, index=False)
print('Saved to: ' + output_path)
