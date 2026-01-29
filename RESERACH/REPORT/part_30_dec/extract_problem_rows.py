import pandas as pd

df = pd.read_excel('part_30_dec.xlsx')

# Problem rows with pack/dimension issues
problem_rows = [126, 135, 317, 1971, 2021, 2089, 420, 853, 2066, 1655]

print("="*80)
print("ACTUAL DATA FROM part_30_dec.xlsx - Problem Rows Analysis")
print("="*80)

for row_id in problem_rows:
    if row_id <= len(df):
        r = df.iloc[row_id-1]
        print(f"\n--- Row {row_id} ---")
        sup_title = str(r.get('SupplierTitle', 'N/A'))
        amz_title = str(r.get('AmazonTitle', 'N/A'))
        print(f"SUP: {sup_title[:80]}")
        print(f"AMZ: {amz_title[:80]}")
        print(f"EAN: {r.get('EAN', 'N/A')} | AMZ_EAN: {r.get('EAN_OnPage', 'N/A')}")
        print(f"Profit: {r.get('NetProfit', 'N/A')}")
