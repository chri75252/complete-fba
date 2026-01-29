import pandas as pd
import re

# Ground truth EANs (29 from the table I extracted)
gt_eans = ['5059001500861','5050028016069','5010853235530','5053249248356','5032759031078','5060357990107','5053249248295','5053249228174','5010792542676','5010792542737','5010792749549','5039295201040','26102251102','5025364001970','5019200117338','5026180033572','5060187173633','5030481940088','5013159300353','5036200121479','5012904061204','5013159004428','5060187175750','5010853203508','5012904004188','5055361761119','5012904148738','5022704000013','8711252100531']

# Load OLD and NEW
df_old = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\part_30_dec\part_30_dec.xlsx')
df_new = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART_DEC_31\PART_DEC_31.xlsx')

def clean(x):
    if pd.isna(x): return ''
    return re.sub(r'\D', '', str(x).replace('.0',''))

df_old['e1'] = df_old['EAN'].apply(clean)
df_old['e2'] = df_old['EAN_OnPage'].apply(clean)
df_new['e1'] = df_new['EAN'].apply(clean)
df_new['e2'] = df_new['EAN_OnPage'].apply(clean)

old_matches = df_old[(df_old['e1']==df_old['e2']) & (df_old['e1']!='') & (df_old['e1']!='nan')]
new_matches = df_new[(df_new['e1']==df_new['e2']) & (df_new['e1']!='') & (df_new['e1']!='nan')]

print('OLD EAN matches not in ground truth list (the 4 missing):')
for idx, row in old_matches.iterrows():
    ean = row['e1']
    if ean not in gt_eans:
        title = row['SupplierTitle']
        print(f'  EAN: {ean} | Title: {title[:50]}')

print()
print('NEW EAN matches not in ground truth list:')
for idx, row in new_matches.iterrows():
    ean = row['e1']
    if ean not in gt_eans:
        title = row['SupplierTitle']
        print(f'  EAN: {ean} | Title: {title[:50]}')
