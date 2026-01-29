import pandas as pd
import re

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx', nrows=50)

print("=" * 100)
print("RAW DATA - FIRST 50 ROWS")
print("=" * 100)

for idx, row in df.iterrows():
    print(f"\n--- Row {idx} ---")
    print(f"EAN: {row['EAN']}")
    print(f"SupplierTitle: {row['SupplierTitle']}")
    print(f"AmazonTitle: {row['AmazonTitle']}")
    print(f"bought_in_past_month: {row['bought_in_past_month']}")
    print(f"SupplierPrice_exVAT: {row['SupplierPrice_exVAT']}")
    print(f"SellingPrice_incVAT: {row['SellingPrice_incVAT']}")
    print(f"NetProfit: {row['NetProfit']}")
