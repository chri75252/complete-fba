
import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx"

df = pd.read_excel(file_path, nrows=1)
cols = df.columns.tolist()
for i in range(0, len(cols), 5):
    print(cols[i:i+5])
