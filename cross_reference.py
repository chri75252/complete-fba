"""
FINAL CROSS-REFERENCE: Check what was missed by the 3 reports vs my analysis
"""
import pandas as pd
import re

# Load source data
df = pd.read_excel(r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\PART3\PART3.xlsx')
df['RowID'] = df.index + 1

# Clean EANs
df['EAN_clean'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
df['EAN_OnPage_clean'] = df['EAN_OnPage'].astype(str).str.replace('.0', '', regex=False).str.strip()

def is_valid_ean(ean):
    if pd.isna(ean) or str(ean).strip() in ['nan', '', 'None', 'NaN', '0', '-']:
        return False
    s = str(ean).strip()
    return s.isdigit() and len(s) >= 8

# Find all exact EAN matches
ean_matches = []
for idx, row in df.iterrows():
    ean1 = row['EAN_clean']
    ean2 = row['EAN_OnPage_clean']
    if is_valid_ean(ean1) and is_valid_ean(ean2) and ean1 == ean2:
        profit = row.get('NetProfit', 0)
        if pd.isna(profit):
            profit = 0
        ean_matches.append({
            'RowID': idx + 1,
            'ASIN': row['ASIN'],
        })

# Extract ASINs from each report
def extract_asins_from_md(filepath):
    asins = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'\b(B[A-Z0-9]{9})\b'
    matches = re.findall(pattern, content)
    for m in matches:
        asins.add(m)
    return asins

gpt_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gpt PHASEA_MANUAL_REPORT_20251225 (1).md'
gemini_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\gemini PHASEA_MANUAL_REPORT_20251225.md'
codex_path = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\finale\part 4 2.9\codex PHASEA_MANUAL_REPORT_20251225.md'

gpt_asins = extract_asins_from_md(gpt_path)
gemini_asins = extract_asins_from_md(gemini_path)
codex_asins = extract_asins_from_md(codex_path)

print("=" * 80)
print("CROSS-REFERENCE: EXACT EAN MATCHES vs REPORTS")
print("=" * 80)
print(f"\nTotal Exact EAN Matches in PART3.xlsx: {len(ean_matches)}")
print()

# Check each EAN match
print("ASIN               | RowID | In GPT? | In Gemini? | In Codex?")
print("-" * 65)

missed_by_all = []
for m in ean_matches:
    asin = m['ASIN']
    row_id = m['RowID']
    in_gpt = "YES" if asin in gpt_asins else "NO"
    in_gemini = "YES" if asin in gemini_asins else "NO"
    in_codex = "YES" if asin in codex_asins else "NO"
    
    print(f"{asin} | {row_id:5d} | {in_gpt:7s} | {in_gemini:10s} | {in_codex}")
    
    if asin not in gpt_asins and asin not in gemini_asins and asin not in codex_asins:
        missed_by_all.append(m)

print()
print("=" * 80)
print(f"EAN MATCHES MISSED BY ALL 3 REPORTS: {len(missed_by_all)}")
print("=" * 80)
for m in missed_by_all:
    row = df[df['RowID'] == m['RowID']].iloc[0]
    print(f"Row {m['RowID']}: ASIN={m['ASIN']}")
    print(f"  EAN: {row['EAN_clean']}")
    print(f"  Supplier: {row['SupplierTitle']}")
    print(f"  Amazon: {row['AmazonTitle']}")
    print(f"  Profit: {row['NetProfit']:.2f}")
    print()
