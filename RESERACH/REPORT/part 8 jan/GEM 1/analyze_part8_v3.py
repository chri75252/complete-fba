import pandas as pd
import os

file_path = "temp_part8.xlsx"

try:
    print("Reading file...")
    df = pd.read_excel(file_path, nrows=20)
    print("COLUMNS_START")
    for col in df.columns:
        print(f"COL: {col}")
    print("COLUMNS_END")
    
    print("ROWS_START")
    # Print distinct rows of relevant columns to avoid huge output
    # I'll just print the whole row dictionary for the first 10
    for idx, row in df.head(20).iterrows():
        print(f"ROW {idx}: {row.to_dict()}")
    print("ROWS_END")

except Exception as e:
    print(f"Error: {e}")
