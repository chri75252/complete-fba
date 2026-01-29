import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=50)
    print("COLUMNS_FOUND:", df.columns.tolist())
    
    cols_to_print = ['SupplierTitle']
    if 'AmazonTitle' in df.columns:
        cols_to_print.append('AmazonTitle')
    elif 'amazontitle' in df.columns:
        cols_to_print.append('amazontitle')
    
    # Check for sales columns
    sales_cols = [c for c in df.columns if 'bought' in c.lower() or 'sales' in c.lower()]
    cols_to_print.extend(sales_cols)
    
    print("\nSAMPLE DATA (First 50 rows):")
    for index, row in df.iterrows():
        entry = {col: row[col] for col in cols_to_print}
        print(f"ROW {index}: {entry}")

except Exception as e:
    print(f"Error: {e}")
