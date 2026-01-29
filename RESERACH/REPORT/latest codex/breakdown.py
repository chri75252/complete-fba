import pandas as pd
import re

df = pd.read_csv(r'input_data_all_linking.csv')

def clean_to_digits(x):
    if pd.isna(x):
        return ''
    if isinstance(x, float):
        return str(int(x))
    s = str(x).strip()
    if 'e+' in s.lower() or 'e-' in s.lower():
        return ''
    return re.sub(r'\D', '', s)

df['EAN_clean'] = df['EAN'].apply(clean_to_digits)
df['EAN_OnPage_clean'] = df['EAN_OnPage'].apply(clean_to_digits)

# RAW match
df['ean_match'] = (df['EAN_clean'] != '') & (df['EAN_OnPage_clean'] != '') & (df['EAN_clean'] == df['EAN_OnPage_clean'])

df['NetProfit'] = pd.to_numeric(df['NetProfit'], errors='coerce').fillna(0)
df['sales'] = pd.to_numeric(df['bought_in_past_month'], errors='coerce').fillna(0)

print("=== BREAKDOWN OF EAN MATCHES ===")
print(f"Total EAN matches: {df['ean_match'].sum()}")

ean_matched = df[df['ean_match']]
print(f"\nWith NetProfit > 0: {len(ean_matched[ean_matched['NetProfit'] > 0])}")
print(f"With NetProfit <= 0: {len(ean_matched[ean_matched['NetProfit'] <= 0])}")

print(f"\nWith Sales > 0: {len(ean_matched[ean_matched['sales'] > 0])}")
print(f"With Sales = 0: {len(ean_matched[ean_matched['sales'] == 0])}")

print(f"\nWith BOTH NetProfit > 0 AND Sales > 0: {len(ean_matched[(ean_matched['NetProfit'] > 0) & (ean_matched['sales'] > 0)])}")

# This is the key - the 821 came from NetProfit > 0 only
# The 34 comes from NetProfit > 0 AND Sales > 0

print("\n=== THE ISSUE ===")
print(f"Old report (821): EAN match + NetProfit > 0 = {len(ean_matched[ean_matched['NetProfit'] > 0])}")
print(f"New report (34):  EAN match + NetProfit > 0 + Sales > 0 = {len(ean_matched[(ean_matched['NetProfit'] > 0) & (ean_matched['sales'] > 0)])}")

# Wait - 821 doesn't match 913 either. Let me check the adjusted profit
df['SupplierPrice_incVAT'] = pd.to_numeric(df['SupplierPrice_incVAT'], errors='coerce').fillna(0)

# Simple adjusted profit (assuming RSU=1 for now)
print(f"\nEAN match + Adjusted (raw NetProfit) > 0: {len(ean_matched[ean_matched['NetProfit'] > 0])}")
