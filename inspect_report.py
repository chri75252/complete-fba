import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=50)
    print("COLUMNS:")
    print(df.columns.tolist())
    print("-" * 20)
    print("FIRST 50 ROWS (subset of columns):")
    # printing all leads to trunction, so I'll try to guess relevant ones or just print to json
    print(df.head(50).to_json(orient='records', indent=2))
except Exception as e:
    print(f"Error reading file: {e}")
