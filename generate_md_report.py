
import pandas as pd
import os
from datetime import datetime

# --- CONFIG ---
CSV_PATH = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\FLASH\deep_analysis_20251228.csv'
OUTPUT_REPORT = r'C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\partdec2812\FLASH\PHASEA_MANUAL_REPORT_20251228.md'

df = pd.read_csv(CSV_PATH)

# Clean EAN for display
def clean_ean_display(val):
    if pd.isna(val) or str(val).lower() == 'nan':
        return "-"
    return str(val).split('.')[0].strip()

df['EAN_display'] = df['EAN'].apply(clean_ean_display)
df['EAN_OnPage_display'] = df['EAN_OnPage'].apply(clean_ean_display)

# Helper for table alignment
def format_table(data, columns):
    if not data:
        return "| No items found |"
    
    col_widths = {col: len(col) for col in columns}
    for row in data:
        for col in columns:
            val = str(row.get(col, ""))
            col_widths[col] = max(col_widths[col], len(val))
            
    header = "| " + " | ".join([f"{col:<{col_widths[col]}}" for col in columns]) + " |"
    separator = "|-" + "-|-".join(["-" * col_widths[col] for col in columns]) + "-|"
    
    formatted_rows = [header, separator]
    for row in data:
        formatted_row = "| " + " | ".join([f"{str(row.get(col, '')):<{col_widths[col]}}" for col in columns]) + " |"
        formatted_rows.append(formatted_row)
        
    return "\n".join(formatted_rows)

# Define columns as per PHASEA schema
TABLE_COLUMNS = [
    "Verdict", "Confidence", "SupplierTitle", "AmazonTitle", "Supplier EAN", "Amazon EAN",
    "ASIN", "SupplierPrice", "SellingPrice", "NetProfit", "ROI", "Sales",
    "Pack Verdict", "Adjusted Profit", "Key Match Evidence", "Filter Reason"
]

def process_row(row):
    d = {
        "Verdict": "",
        "Confidence": int(row['MLS']),
        "SupplierTitle": row['SupplierTitle'][:80],
        "AmazonTitle": row['AmazonTitle'][:80],
        "Supplier EAN": row['EAN_display'],
        "Amazon EAN": row['EAN_OnPage_display'],
        "ASIN": row['ASIN'],
        "SupplierPrice": f"£{row['SupplierPrice_incVAT']:.2f}",
        "SellingPrice": f"£{row['SellingPrice_incVAT']:.2f}",
        "NetProfit": f"£{row['NetProfit']:.2f}",
        "ROI": f"{row['ROI']:.1f}%",
        "Sales": int(row['sales']),
        "Pack Verdict": row['Pack_Verdict'],
        "Adjusted Profit": f"£{row['Adjusted_Profit']:.2f}",
        "Key Match Evidence": "",
        "Filter Reason": "",
        "MLS": row['MLS'],
        "Sales_Val": row['sales']
    }
    
    if row['is_exact_ean_strict']:
        d["Key Match Evidence"] = "Strict Exact EAN Match"
    else:
        sup_t = str(row['SupplierTitle']).lower()
        amz_t = str(row['AmazonTitle']).lower()
        shared = []
        words = re.findall(r'\b\w{4,}\b', sup_t)
        for w in words:
            if w in amz_t: shared.append(w)
        d["Key Match Evidence"] = ", ".join(list(set(shared))[:4])
        
    return d

buckets = {
    "VERIFIED (Recommended)": [],
    "HIGH LIKELIHOOD (Recommended)": [],
    "NEEDS VERIFICATION": [],
    "FILTERED OUT (Audit)": [],
    "OTHER": 0
}

import re

for _, row in df.iterrows():
    p = process_row(row)
    
    is_verified = row['is_exact_ean_strict']
    # Sellable + Profitable check
    is_profitable = (row['NetProfit'] > 0 and row['Adjusted_Profit'] > 0)
    is_sellable = (row['sales'] > 0)
    
    mls = row['MLS']
    
    if is_verified:
        if is_profitable and is_sellable:
            p["Verdict"] = "VERIFIED"
            buckets["VERIFIED (Recommended)"].append(p)
        else:
            p["Verdict"] = "EXCLUDED"
            if not is_sellable: p["Filter Reason"] = "No Sales"
            elif not is_profitable: p["Filter Reason"] = "Non-profitable"
            buckets["FILTERED OUT (Audit)"].append(p)
    elif mls >= 75:
        if is_profitable and is_sellable:
            p["Verdict"] = "HIGH LIKELIHOOD"
            buckets["HIGH LIKELIHOOD (Recommended)"].append(p)
        else:
            p["Verdict"] = "NEEDS VERIFICATION"
            p["Filter Reason"] = "Uncertainty / Low ROI"
            buckets["NEEDS VERIFICATION"].append(p)
    elif mls >= 35:
        p["Verdict"] = "NEEDS VERIFICATION"
        buckets["NEEDS VERIFICATION"].append(p)
    else:
        buckets["OTHER"] += 1

# SORTING
# Exact-EAN: Sales desc
buckets["VERIFIED (Recommended)"].sort(key=lambda x: x['Sales_Val'], reverse=True)
# High Likelihood: MLS desc, then Sales
buckets["HIGH LIKELIHOOD (Recommended)"].sort(key=lambda x: (x['MLS'], x['Sales_Val']), reverse=True)
# Needs Verification: MLS desc, then Sales
buckets["NEEDS VERIFICATION"].sort(key=lambda x: (x['MLS'], x['Sales_Val']), reverse=True)

# Reconciliation
total_input = len(df)
sum_buckets = (len(buckets["VERIFIED (Recommended)"]) + 
               len(buckets["HIGH LIKELIHOOD (Recommended)"]) + 
               len(buckets["NEEDS VERIFICATION"]) + 
               len(buckets["FILTERED OUT (Audit)"]) + 
               buckets["OTHER"])

recon_status = "PASS" if sum_buckets == total_input else "FAIL"

# Generate Report
today_str = datetime.now().strftime('%Y-%m-%d')
with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
    f.write(f"# PHASE A MANUAL FBA REPORT - {today_str}\n\n")
    
    f.write("## 0. RECONCILIATION PROOF\n\n")
    f.write("| Bucket | Count |\n")
    f.write("|:--|--:|\n")
    f.write(f"| Total input rows | {total_input} |\n")
    f.write(f"| VERIFIED (Recommended) | {len(buckets['VERIFIED (Recommended)'])} |\n")
    f.write(f"| HIGH LIKELIHOOD (Recommended) | {len(buckets['HIGH LIKELIHOOD (Recommended)'])} |\n")
    f.write(f"| NEEDS VERIFICATION | {len(buckets['NEEDS VERIFICATION'])} |\n")
    f.write(f"| FILTERED OUT (Audit) | {len(buckets['FILTERED OUT (Audit)'])} |\n")
    f.write(f"| OTHER (Low MLS/Sales=0/Loss) | {buckets['OTHER']} |\n")
    f.write(f"| **SUM** | **{sum_buckets}** |\n\n")
    f.write(f"✅ Reconciliation: {recon_status} ({sum_buckets} = {total_input})\n\n")

    f.write("## 1. VERIFIED (Exact EAN) - Recommended\n\n")
    f.write("```text\n")
    f.write(format_table(buckets["VERIFIED (Recommended)"], TABLE_COLUMNS))
    f.write("\n```\n\n")

    f.write("## 2. HIGH LIKELIHOOD (MLS >= 75) - Recommended\n\n")
    f.write("```text\n")
    f.write(format_table(buckets["HIGH LIKELIHOOD (Recommended)"], TABLE_COLUMNS))
    f.write("\n```\n\n")

    f.write("## 3. NEEDS VERIFICATION (Uncertain/Ambiguous)\n\n")
    top_75_nv = buckets["NEEDS VERIFICATION"][:75]
    f.write("```text\n")
    f.write(format_table(top_75_nv, TABLE_COLUMNS))
    f.write("\n```\n")
    if len(buckets["NEEDS VERIFICATION"]) > 75:
        rem = len(buckets["NEEDS VERIFICATION"]) - 75
        f.write(f"\n*Remaining: {rem} rows with MLS variant range.*\n\n")
    else:
        f.write("\n")

    f.write("## 4. VERIFIED (Exact EAN) - FILTERED OUT (Audit)\n\n")
    audit_verified = [r for r in buckets["FILTERED OUT (Audit)"] if r["Verdict"] == "EXCLUDED"]
    f.write("```text\n")
    f.write(format_table(audit_verified, TABLE_COLUMNS))
    f.write("\n```\n\n")

    f.write("## 5. HIGH LIKELIHOOD - FILTERED OUT (Audit)\n\n")
    # Add any non-EAN filtered out here (none in current flow but logic-ready)
    f.write("```text\n")
    f.write(format_table([], TABLE_COLUMNS)) 
    f.write("\n```\n\n")

print(f"Final report generated at {OUTPUT_REPORT}")
