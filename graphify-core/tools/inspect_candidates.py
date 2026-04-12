
import pandas as pd

CSV_PATH = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\RESERACH\REPORT\deep_analysis_part1.csv"
df = pd.read_csv(CSV_PATH)
candidates = df[(df['sales'] > 0) & (df['NetProfit'] > 0)].sort_values(by='sales', ascending=False)

print("Top 10 Candidates:")
for idx, row in candidates.head(10).iterrows():
    print(f"\nINDEX: {idx}")
    print(f"Cat: {row['category']} | ExactEAN: {row['is_exact_ean']}")
    print(f"Titles: '{row['SupplierTitle']}' vs '{row['AmazonTitle']}'")
    print(f"EANs: {row['EAN']} vs {row['EAN_OnPage']}")
    print(f"Match Score: {row['title_match']:.2f}")
    print(f"Pack: Sup={row['Sup_Qty']} Amz={row['Amz_Qty']} Ratio={row['Qty_Ratio']} Verdict={row['Pack_Verdict']}")
    print(f"Profit: Net={row['NetProfit']} Adj={row['Adjusted_Profit']}")
    print(f"Sales: {row['sales']}")
