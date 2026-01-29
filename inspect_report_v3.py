import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=50)
    
    print("--- SALES COLUMN CHECK ---")
    print("Column 'bought_in_past_month' sample values:")
    print(df['bought_in_past_month'].head(10).tolist())
    
    print("\n--- TITLE ANALYSIS (First 20) ---")
    for index, row in df.head(20).iterrows():
        st = str(row.get('SupplierTitle', ''))
        at = str(row.get('AmazonTitle', ''))
        print(f"R{index} | S: {st[:60]} | A: {at[:60]}")

except Exception as e:
    print(f"Error: {e}")
