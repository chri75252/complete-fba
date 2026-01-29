import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\part 8 jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=10)
    print("COLUMNS:")
    print(df.columns.tolist())
    print("-" * 20)
    print("FIRST 10 ROWS:")
    print(df.to_markdown())

except Exception as e:
    print(f"Error reading file: {e}")
