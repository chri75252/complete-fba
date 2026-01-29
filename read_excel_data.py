import pandas as pd
import json
import sys

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx"

try:
    df = pd.read_excel(file_path)
    # Get column names
    columns = df.columns.tolist()
    # Get first 5 rows as a sample
    sample = df.head(10).to_dict(orient="records")

    result = {"columns": columns, "sample": sample, "total_rows": len(df)}
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"Error: {str(e)}", file=sys.stderr)
    sys.exit(1)
