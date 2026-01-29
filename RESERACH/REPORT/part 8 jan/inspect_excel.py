import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\tes.xlsx"

try:
    df = pd.read_excel(file_path)
    print(f"Total Rows: {len(df)}")
    print("Columns:", df.columns.tolist())
    print("-" * 30)
    print(df.head(5).to_string())
except Exception as e:
    print(f"Error reading excel: {e}")
