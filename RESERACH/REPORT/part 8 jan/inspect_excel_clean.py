import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part 8 jan\tes.xlsx"

try:
    df = pd.read_excel(file_path)
    print("COLUMNS_START")
    for col in df.columns:
        print(col)
    print("COLUMNS_END")
    
    print("ROW0_START")
    if not df.empty:
        print(df.iloc[0].to_dict())
    print("ROW0_END")
except Exception as e:
    print(f"Error: {e}")
