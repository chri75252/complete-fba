import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=50)
    print("COLUMNS:")
    print(df.columns.tolist())
    print("-" * 20)
    
    # Identify likely columns based on common names if possible, otherwise print all valid ones
    supplier_title_col = next((c for c in df.columns if "Supplier Title" in c or "Product Name" in c), None) # Guessing
    amazon_title_col = next((c for c in df.columns if "Amazon Title" in c or "Title" in c), None)
    brand_col = next((c for c in df.columns if "Brand" in c), None)
    sales_col = next((c for c in df.columns if "Sales" in c or "bought" in c), None)
    
    cols_to_print = [c for c in [supplier_title_col, amazon_title_col, brand_col, sales_col] if c]
    
    if not cols_to_print:
        print("Could not guess columns. Printing first 5 rows of all columns:")
        print(df.head(5).to_markdown())
    else:
        print(f"Detected Columns: Supplier='{supplier_title_col}', Amazon='{amazon_title_col}', Brand='{brand_col}', Sales='{sales_col}'")
        print(df[cols_to_print].head(50).to_markdown())

except Exception as e:
    print(f"Error reading file: {e}")
