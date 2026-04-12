import pandas as pd

df = pd.read_csv(r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS\PRODUCTS_LISTS\efg_master_product_list_20260412_072629.csv")

print("=== SANITY CHECK: Extreme ROI items (>5000%) — likely false matches ===")
suspicious = df[df["ROI"] > 5000]
print(f"Count with ROI>5000%: {len(suspicious)}")
for _, r in suspicious.head(15).iterrows():
    sup = str(r["SupplierTitle"])[:45]
    amz = str(r["AmazonTitle"])[:45]
    print(f"  [{r['match_type']}] {sup} -> {amz} | ROI={r['ROI']:.0f}% sim={r['title_similarity']:.2f} bucket={r['bucket']}")

print()
print("=== ROI DISTRIBUTION ===")
for threshold in [50, 100, 200, 500, 1000, 5000]:
    count = len(df[df["ROI"] <= threshold])
    print(f"  ROI <= {threshold}%: {count}")

print()
print("=== REALISTIC BUCKET A (ROI<=200, Sales>0, Profit>0) ===")
realistic_a = df[(df["bucket"]=="A") & (df["ROI"] <= 200) & (df["ROI"] > 0)]
print(f"Count: {len(realistic_a)}")
for _, r in realistic_a.nlargest(15, "NetProfit").iterrows():
    sup = str(r["SupplierTitle"])[:50]
    sales = r["bought_in_past_month"]
    sales_str = f"{sales:.0f}" if pd.notna(sales) else "N/A"
    print(f"  [{r['match_type']}] {sup} | Profit={r['NetProfit']:.2f} Sales={sales_str} ROI={r['ROI']:.1f}%")

print()
print("=== REALISTIC BUCKET C (ROI > -50%, Sales>50) ===")
realistic_c = df[(df["bucket"]=="C") & (df["bought_in_past_month"] >= 50)]
print(f"Count: {len(realistic_c)}")
for _, r in realistic_c.nlargest(10, "bought_in_past_month").iterrows():
    sup = str(r["SupplierTitle"])[:50]
    print(f"  [{r['match_type']}] {sup} | Profit={r['NetProfit']:.2f} Sales={r['bought_in_past_month']:.0f}")
