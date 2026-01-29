import pandas as pd
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_1_jan\part_1_jan.xlsx')

print('=== SPECIFIC ROWS FOR CALIBRATION WARNINGS ===\n')

# Row patterns with numbers at end that need verification  
interesting_rows = [1, 10, 17, 18, 20, 21, 27, 36, 47, 55, 57, 58, 59, 81, 99, 111, 114, 171]

for idx in interesting_rows:
    if idx < len(df):
        row = df.iloc[idx]
        print('Row ' + str(idx) + ':')
        print('  SupplierTitle: ' + str(row['SupplierTitle']))
        amz_title = row.get('AmazonTitle')
        if pd.notna(amz_title):
            print('  AmazonTitle: ' + str(amz_title)[:100] + '...')
        print()
