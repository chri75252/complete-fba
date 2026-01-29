import pandas as pd
df = pd.read_csv("deep_analysis_20251225.csv")
print("Total rows:", len(df))
print(df['Final_Verdict'].value_counts())
print("\nTop 3 Verified:")
print(df[df['Final_Verdict'] == "VERIFIED (Exact EAN)"].head(3)[['SupplierTitle', 'NetProfit']])
