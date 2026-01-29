import pandas as pd

file_path = "temp_part8.xlsx"
try:
    df = pd.read_excel(file_path, nrows=1)
    print("ALL_COLUMNS_LIST:")
    for c in df.columns:
        print(f"COLUMN: {c}")
except Exception as e:
    print(e)
