import pandas as pd
import json

# Load the enriched CSV
csv_path = "RESERACH/finale/open/final_ver_sheet1_enriched.csv"
df = pd.read_csv(csv_path)

# Filter: Remove AVOID, must have Amazon URL and Supplier Price
df_valid = df[
    (df["Status"] != "AVOID")
    & (df["Amazon URL"].notna())
    & (df["SupplierPrice"] > 0)
    & (df["NetProfit"] > 0)
].copy()

# Sort by NetProfit descending
df_sorted = df_valid.sort_values(by="NetProfit", ascending=False)

# Select Top 10 for inspection
top_candidates = df_sorted.head(10).to_dict(orient="records")

# Output the plan
print(json.dumps(top_candidates, indent=2))
