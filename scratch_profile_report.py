import pandas as pd

df = pd.read_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005639.csv")

print("=== BASIC STATS ===")
print(f"Total rows: {len(df)}")
print(f"Unique EANs: {df['EAN'].nunique()}")
print(f"Unique ASINs: {df['ASIN'].nunique()}")
print()

# Sales distribution
sales_col = "bought_in_past_month"
df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
df["NetProfit"] = pd.to_numeric(df["NetProfit"], errors="coerce")
df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")
df["SellingPrice_incVAT"] = pd.to_numeric(df["SellingPrice_incVAT"], errors="coerce")

print("=== SALES DISTRIBUTION ===")
has_sales = df[sales_col] > 0
print(f"With sales > 0: {has_sales.sum()}")
print(f"Sales = 0: {(df[sales_col] == 0).sum()}")
print(f"Sales NaN/missing: {df[sales_col].isna().sum()}")
print()

print("=== PROFIT DISTRIBUTION ===")
print(f"NetProfit > 0: {(df['NetProfit'] > 0).sum()}")
print(f"NetProfit <= 0: {(df['NetProfit'] <= 0).sum()}")
print(f"NetProfit NaN: {df['NetProfit'].isna().sum()}")
print()

# Superior brand count
superior_mask = df["SupplierTitle"].str.contains("Superior", case=False, na=False) | df["AmazonTitle"].str.contains("Superior", case=False, na=False)
print("=== SUPERIOR BRAND ===")
print(f"Rows containing Superior: {superior_mask.sum()}")
print()

# Bucket preview
bucket_a = df[(df[sales_col] > 0) & (df["NetProfit"] > 0) & (~superior_mask)]
bucket_b = df[(df["NetProfit"] > 0) & ((df[sales_col] == 0) | df[sales_col].isna()) & (~superior_mask)]
near_profit = df[(df[sales_col] > 0) & (df["NetProfit"] <= 0) & (df["NetProfit"] > -2) & (~superior_mask)]
print("=== BUCKET PREVIEW (pre-match-quality) ===")
print(f"Bucket A candidates (Sales>0, Profit>0, no Superior): {len(bucket_a)}")
print(f"Bucket B candidates (Profit>0, Sales=0/NaN, no Superior): {len(bucket_b)}")
print(f"Bucket C candidates (Sales>0, Profit near 0, no Superior): {len(near_profit)}")
print()

# Check for match type / tier columns
match_cols = [c for c in df.columns if "match" in c.lower() or "tier" in c.lower() or "confidence" in c.lower() or "type" in c.lower()]
print(f"=== MATCH/TIER COLUMNS ===")
print(f"Found: {match_cols if match_cols else 'NONE - must infer from EAN_OnPage'}")
print()

# EAN matching quality
ean_on_page_present = df["EAN_OnPage"].notna().sum()
print(f"=== EAN MATCHING QUALITY ===")
print(f"EAN_OnPage present: {ean_on_page_present}")
print(f"EAN_OnPage missing (likely title-match): {df['EAN_OnPage'].isna().sum()}")
print()

# Price range
print("=== PRICE RANGES ===")
print(f"SupplierPrice range: {df['SupplierPrice_exVAT'].min():.2f} - {df['SupplierPrice_exVAT'].max():.2f}")
print(f"SellingPrice range: {df['SellingPrice_incVAT'].min():.2f} - {df['SellingPrice_incVAT'].max():.2f}")
print()

# Sample Bucket A top products
if len(bucket_a) > 0:
    print("=== TOP 15 BUCKET A (by NetProfit) ===")
    top_a = bucket_a.nlargest(15, "NetProfit")[["SupplierTitle", "AmazonTitle", "NetProfit", sales_col, "ROI", "ASIN", "EAN_OnPage"]]
    for i, row in top_a.iterrows():
        ean_status = "EAN_MATCH" if pd.notna(row["EAN_OnPage"]) else "TITLE_MATCH"
        print(f"  [{ean_status}] Profit={row['NetProfit']:.2f} Sales={row[sales_col]:.0f} ROI={row['ROI']:.1f}% | {row['SupplierTitle'][:50]} -> {row['AmazonTitle'][:60]}")
