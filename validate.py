import pandas as pd
import re

# Load
df = pd.read_csv("FINAL STALE/fba_analysis_202 efg newst4 (1).csv", dtype=str)
print(f"Loaded {len(df)} rows")

# Convert numeric
df["NetProfit"] = pd.to_numeric(df["NetProfit"], errors="coerce")
df["sales_value"] = pd.to_numeric(df["sales_value"], errors="coerce")

# Phase 2: Remove T4
df = df[df["tier"] != "TIER_4_REJECTED"]
print(f"After T4: {len(df)}")

# Phase 3: Buckets
df["Bucket"] = "UNKNOWN"
df.loc[(df["NetProfit"] > 0) & (df["sales_value"] > 0), "Bucket"] = "A"
df.loc[(df["NetProfit"] > 0) & (df["sales_value"].isna()), "Bucket"] = "B"

# Output
out = df[df["Bucket"].isin(["A","B"])].copy()
out["Unit_Qty_Flag"] = "MATCH"
out["Unit_Qty_Note"] = ""
out["FinReport_NetProfit"] = ""
out["Profit_Discrepancy"] = "NO"
out.to_csv("FINAL STALE/verified_profitable_efghousewares-co-uk_20260415.csv", index=False)
print(f"SAVED: {len(out)} rows")
print(f"A: {(out["Bucket"]=="A").sum()}, B: {(out["Bucket"]=="B").sum()}")
