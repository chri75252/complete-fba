import pandas as pd
import json
import os

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 4 jan\part 4 jan.xlsx"

try:
    df = pd.read_excel(file_path, nrows=50)
    # Convert to json records to avoid truncation issues with printing large DFs
    with open('calibration_data.json', 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, default=str, indent=2)
    print("Data written to calibration_data.json")
except Exception as e:
    print(f"Error: {e}")
