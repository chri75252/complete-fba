import pandas as pd
import json

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\tes.xlsx"
out_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\cols.json"

try:
    df = pd.read_excel(file_path)
    info = {
        "columns": [c.strip() for c in df.columns],
        "first_row": df.iloc[0].to_dict(),
        "row_count": len(df)
    }
    # Handle weird keys in first_row for json dump (timestamp etc)
    for k, v in info["first_row"].items():
        info["first_row"][k] = str(v)
        
    with open(out_path, "w") as f:
        json.dump(info, f, indent=2)
    print("Done")
except Exception as e:
    with open(out_path, "w") as f:
        f.write(str(e))
