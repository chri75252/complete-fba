import pandas as pd

file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx"
output_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\calibration_output.txt"

try:
    df = pd.read_excel(file_path, nrows=50)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("--- SALES COLUMN CHECK ---\n")
        f.write(f"Column 'bought_in_past_month' sample values: {df['bought_in_past_month'].head(10).tolist()}\n\n")
        
        f.write("--- TITLE ANALYSIS (First 50) ---\n")
        for index, row in df.iterrows():
            st = str(row.get('SupplierTitle', ''))
            at = str(row.get('AmazonTitle', ''))
            f.write(f"R{index} | S: {st} | A: {at}\n")

except Exception as e:
    with open(output_path, 'w') as f:
        f.write(f"Error: {e}")
