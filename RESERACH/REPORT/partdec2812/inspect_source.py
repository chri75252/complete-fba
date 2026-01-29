import pandas as pd
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\PARTDEC28_1.xlsx"

try:
    df = pd.read_excel(file_path)
    print("Columns:", list(df.columns))
    print("Total rows:", len(df))
    print("First 5 rows:")
    print(df.head().to_string())
except Exception as e:
    print(f"Error: {e}")
