#!/usr/bin/env python3
"""
Full investigation of missing profit data - saves to file
"""
import pandas as pd
import numpy as np

# Load data
df = pd.read_excel(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\final ver.xlsx")
df.columns = [c.strip() for c in df.columns]

output = []
output.append("=" * 80)
output.append("INVESTIGATION: Missing Profit Data in final ver.xlsx")
output.append("=" * 80)
output.append("")
output.append(f"ALL COLUMNS: {list(df.columns)}")
output.append("")

# Find rows with missing profit
missing = df[df['Adjusted Profit'].isna()]
output.append(f"ROWS WITH MISSING 'Adjusted Profit': {len(missing)}")
output.append("-" * 80)

for idx, row in missing.iterrows():
    title = str(row['SupplierTitle'])[:60].strip()
    asin = str(row['ASIN']).strip()
    roi = row['ROI']
    net_profit = row['NetProfit']
    verdict = str(row['Verdict']).strip()
    pack_verdict = str(row['Pack Verdict']).strip() if 'Pack Verdict' in df.columns else 'N/A'
    filter_reason = str(row['Filter Reason'])[:50].strip() if 'Filter Reason' in df.columns else 'N/A'
    
    output.append(f"Row {idx+2}: {title}")
    output.append(f"  ASIN: {asin}")
    output.append(f"  ROI: {roi}")
    output.append(f"  NetProfit (raw): {net_profit}")
    output.append(f"  Adjusted Profit: MISSING")
    output.append(f"  Verdict: {verdict}")
    output.append(f"  Pack Verdict: {pack_verdict}")
    output.append(f"  Filter Reason: {filter_reason}")
    output.append("")

output.append("-" * 80)
output.append("ROOT CAUSE ANALYSIS")
output.append("-" * 80)
output.append("")

# Superior products specifically
superior = df[df['SupplierTitle'].str.contains('SUPERIOR', case=False, na=False)]
output.append(f"SUPERIOR BRAND PRODUCTS: {len(superior)} total")
output.append("")

for idx, row in superior.iterrows():
    title = str(row['SupplierTitle'])[:60].strip()
    adj_profit = row['Adjusted Profit']
    net_profit = row['NetProfit']
    verdict = str(row['Verdict']).strip()
    
    status = "OK" if not pd.isna(adj_profit) else "MISSING"
    output.append(f"  {title}")
    output.append(f"    NetProfit: {net_profit} | Adjusted Profit: {adj_profit} ({status})")
    output.append(f"    Verdict: {verdict}")
    output.append("")

output.append("-" * 80)
output.append("CONCLUSION")
output.append("-" * 80)
output.append("")

# Count by reason
audited_out = sum(1 for idx, row in missing.iterrows() if 'AUDITED OUT' in str(row['Verdict']).upper())
no_verdict = sum(1 for idx, row in missing.iterrows() if str(row['Verdict']).strip() == 'nan' or pd.isna(row['Verdict']))
other = len(missing) - audited_out - no_verdict

output.append(f"Missing profit breakdown:")
output.append(f"  - AUDITED OUT (excluded from analysis): {audited_out}")
output.append(f"  - No verdict (incomplete data): {no_verdict}")
output.append(f"  - Other: {other}")
output.append("")
output.append("EXPLANATION:")
output.append("The 'Adjusted Profit' column was NOT calculated for rows where:")
output.append("1. The product was marked as 'AUDITED OUT' (excluded during prior review)")
output.append("2. The row has no verdict (incomplete/missing source data)")
output.append("3. Pack quantity adjustment could not be determined")
output.append("")
output.append("These products have ROI values but the Adjusted Profit was intentionally")
output.append("left blank because the profit figure requires pack/quantity validation.")

# Save to file
with open(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\finale\open2\op\INVESTIGATION_MISSING_PROFIT.txt", 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))

print("Investigation saved to INVESTIGATION_MISSING_PROFIT.txt")
print()
print('\n'.join(output))
