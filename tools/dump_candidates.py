
import pandas as pd

CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_part1.csv"
OUTPUT_TXT = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\candidates_for_review.txt"

df = pd.read_csv(CSV_PATH)

# Filter
candidates = df[
    (df['sales'] > 0) & 
    (df['NetProfit'] > 0)
].copy()

candidates = candidates.sort_values(by='sales', ascending=False)

with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    f.write("=== EXACT EAN MATCHES ===\n")
    exact = candidates[candidates['is_exact_ean'] == True]
    for idx, row in exact.iterrows():
        f.write(f"INDEX: {idx}\n")
        f.write(f"TITLES: {row['SupplierTitle']}  <->  {row['AmazonTitle']}\n")
        f.write(f"EANs: {row['EAN']} <-> {row['EAN_OnPage']}\n")
        f.write(f"PROFIT: Net £{row['NetProfit']} | Adj £{row['Adjusted_Profit']}\n")
        f.write(f"PACK: {row['Pack_Verdict']} (Ratio {row['Qty_Ratio']})\n")
        f.write(f"SALES: {row['sales']}\n")
        f.write("-" * 40 + "\n")

    f.write("\n=== HIGH LIKELIHOOD ===\n")
    high = candidates[(candidates['category'] == 'HIGH_LIKELIHOOD') & (candidates['is_exact_ean'] == False)]
    for idx, row in high.iterrows():
        f.write(f"INDEX: {idx}\n")
        f.write(f"TITLES: {row['SupplierTitle']}  <->  {row['AmazonTitle']}\n")
        f.write(f"PROFIT: Net £{row['NetProfit']} | Adj £{row['Adjusted_Profit']}\n")
        f.write(f"PACK: {row['Pack_Verdict']} (Ratio {row['Qty_Ratio']})\n")
        f.write(f"SALES: {row['sales']}\n")
        f.write("-" * 40 + "\n")

print(f"Dumped {len(candidates)} candidates to {OUTPUT_TXT}")
