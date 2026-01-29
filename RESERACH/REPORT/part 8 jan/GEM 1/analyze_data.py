import pandas as pd

file_path = "temp_part8.xlsx"
try:
    df = pd.read_excel(file_path, nrows=50)
    
    print("=== DATA INSPECTION ===")
    print(f"Sales Column: bought_in_past_month")
    print("-" * 30)
    
    print("SAMPLE ROWS (SupplierTitle | AmazonTitle | Sales):")
    for i, row in df.head(30).iterrows():
        st = str(row['SupplierTitle'])
        at = str(row['AmazonTitle'])
        sales = str(row['bought_in_past_month'])
        print(f"ROW {i}: SUP='{st}' | AMZ='{at}' | SALES='{sales}'")

except Exception as e:
    print(e)
