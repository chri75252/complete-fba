import pandas as pd
import re

df = pd.read_csv(r'input_data_all_linking.csv')

print(f'Total rows: {len(df)}')
print(f'EAN_OnPage non-null: {df["EAN_OnPage"].notna().sum()}')

# Convert scientific notation back to string
def clean_ean(x):
    if pd.isna(x):
        return ''
    if isinstance(x, float):
        return str(int(x))
    return re.sub(r'\D', '', str(x).strip())

df['EAN_clean'] = df['EAN'].apply(clean_ean)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_ean)

# Simple match (same digits)
df['ean_match'] = (df['EAN_clean'] != '') & (df['EAN_OnPage_clean'] != '') & (df['EAN_clean'] == df['EAN_OnPage_clean'])

print(f'Rows where EAN == EAN_OnPage (simple match): {df["ean_match"].sum()}')

# Now with your criteria
df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)

matching = df[df['ean_match'] & (df['NetProfit'] > 0) & (df['sales'] > 0)]
print(f'Matching EAN + NetProfit>0 + Sales>0: {len(matching)}')

# Unique
unique_eans = matching['EAN_clean'].nunique()
print(f'Unique EANs: {unique_eans}')

unique_asins = matching['ASIN'].nunique()
print(f'Unique ASINs: {unique_asins}')

# Deduplicated
deduped = matching.drop_duplicates(subset=['EAN_clean'])
print(f'After EAN deduplication: {len(deduped)}')

deduped_asin = matching.drop_duplicates(subset=['ASIN'])
print(f'After ASIN deduplication: {len(deduped_asin)}')

# What about the original 821? Let me check what the script counted
print("\n=== Analysis of what the report counted as 821 ===")
# The 821 includes ALL with exact EAN + adjusted profit > 0, NOT requiring sales > 0

# Let's see the breakdown
all_ean_match = df[df['ean_match']]
print(f'Total rows with EAN match: {len(all_ean_match)}')

ean_match_profit = all_ean_match[all_ean_match['NetProfit'] > 0]
print(f'EAN match + NetProfit > 0: {len(ean_match_profit)}')

ean_match_profit_sales = ean_match_profit[ean_match_profit['sales'] > 0]
print(f'EAN match + NetProfit > 0 + Sales > 0: {len(ean_match_profit_sales)}')

ean_match_profit_nosales = ean_match_profit[ean_match_profit['sales'] == 0]
print(f'EAN match + NetProfit > 0 + Sales = 0: {len(ean_match_profit_nosales)}')
