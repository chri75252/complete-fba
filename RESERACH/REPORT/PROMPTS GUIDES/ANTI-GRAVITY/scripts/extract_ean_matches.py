import pandas as pd
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')
df['RowID'] = df.index + 1
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

def is_valid_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    return str(ean).strip().isdigit() and len(str(ean).strip()) >= 8

# Get all EAN matches
for idx, row in df.iterrows():
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    if is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2:
        profit = row.get('NetProfit', 0)
        if pd.isna(profit): profit = 0
        sup_price = row.get('SupplierPrice_incVAT', row.get('SupplierPrice', 0))
        sell_price = row.get('SellingPrice_incVAT', row.get('SellingPrice', 0))
        if pd.isna(sup_price): sup_price = 0
        if pd.isna(sell_price): sell_price = 0
        roi = row.get('ROI', 0)
        if pd.isna(roi): roi = 0
        sales = row.get('sales_numeric', 0)
        if pd.isna(sales): sales = 0
        
        row_id = row['RowID']
        asin = row['ASIN']
        sup_title = row['SupplierTitle']
        amz_title = row['AmazonTitle']
        
        print(f"ROW {row_id} | ASIN: {asin} | EAN: {ean1}")
        print(f"  SUPPLIER: {sup_title}")
        print(f"  AMAZON: {amz_title}")
        print(f"  Price: GBP{sup_price:.2f} -> GBP{sell_price:.2f} | Profit: GBP{profit:.2f} | ROI: {roi:.1f}% | Sales: {int(sales)}")
        print()
