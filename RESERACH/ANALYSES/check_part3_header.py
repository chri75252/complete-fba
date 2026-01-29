
import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"

try:
    df = pd.read_excel(file_path, nrows=5)
    print("COLUMNS:", df.columns.tolist())
    print("dtypes:", df.dtypes)
    print(df.head(2).to_markdown())
except Exception as e:
    print("ERROR:", e)
