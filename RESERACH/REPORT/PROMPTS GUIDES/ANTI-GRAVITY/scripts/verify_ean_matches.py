import pandas as pd

# Load source data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

def is_valid_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    s = str(ean).strip()
    return s.isdigit() and len(s) >= 8

# Find all exact EAN matches
matches = []
for idx, row in df.iterrows():
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    if is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2:
        profit = row.get('NetProfit', 0)
        if pd.isna(profit):
            profit = 0
        matches.append({
            'RowID': idx + 1,
            'ASIN': row['ASIN'],
            'EAN': ean1,
            'SupplierTitle': str(row['SupplierTitle'])[:50],
            'AmazonTitle': str(row['AmazonTitle'])[:50],
            'NetProfit': profit,
        })

print(f'Total Exact EAN Matches: {len(matches)}')
print()
for m in matches:
    profit_str = f"{m['NetProfit']:.2f}" if isinstance(m['NetProfit'], float) else str(m['NetProfit'])
    print(f"Row {m['RowID']}: {m['ASIN']} | EAN={m['EAN']} | Profit={profit_str}")
    print(f"  Supplier: {m['SupplierTitle']}")
    print(f"  Amazon: {m['AmazonTitle']}")
    print()
