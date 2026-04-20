import pandas as pd

df = pd.read_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\temp\fba_analysis_202 efg newst4 (1).csv")

print(f"Total Rows: {len(df)}")
if 'tier' in df.columns:
    print(f"\nTier Breakdown:\n{df['tier'].value_counts(dropna=False)}")
if 'flags' in df.columns:
    print(f"\nFlags Breakdown:\n{df['flags'].value_counts().head(5)}")
if 'NetProfit' in df.columns:
    print(f"\nProfitable (NetProfit > 0): {(df['NetProfit'] > 0).sum()}")
    print(f"Unprofitable (NetProfit <= 0): {(df['NetProfit'] <= 0).sum()}")
if 'sales_value' in df.columns:
    print(f"\nItems with Sales Data: {df['sales_value'].notna().sum()}")
    print(f"Items with Sales > 0: {(df['sales_value'] > 0).sum()}")
