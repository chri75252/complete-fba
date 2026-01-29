
import pandas as pd
import json

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"

try:
    df = pd.read_excel(file_path, nrows=2)
    print("ALL_COLUMNS_START")
    print(json.dumps(df.columns.tolist()))
    print("ALL_COLUMNS_END")
except Exception as e:
    print("ERROR:", e)
