import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"

print(f"Checking file: {file_path}")
if os.path.exists(file_path):
    print("File exists.")
    try:
        df = pd.read_excel(file_path)
        print("Columns:", df.columns.tolist())
        print("Row count:", len(df))
        print("First 3 rows:")
        print(df.head(3))
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print("File does not exist.")
