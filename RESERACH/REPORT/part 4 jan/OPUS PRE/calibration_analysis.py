import pandas as pd

# Read the Excel file
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\part 4 jan.xlsx')

pd.set_option('display.max_colwidth', 250)
pd.set_option('display.width', None)

print("=== FIRST 50 ROWS: SupplierTitle vs AmazonTitle ===\n")
for idx, row in df.head(50).iterrows():
    print(f"Row {idx}:")
    print(f"  SUPPLIER: {row['SupplierTitle']}")
    print(f"  AMAZON:   {row['AmazonTitle']}")
    print()
