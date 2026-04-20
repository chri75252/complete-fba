#!/usr/bin/env python3
"""Stale Data Workflow for efghousewares"""
import pandas as pd
import os
import json
import re
from datetime import datetime

print("=== STALE DATA WORKFLOW - EFGHOUSEWARES ===")
print()

# === CONFIGURATION ===
BASE = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
STALE_PATH = os.path.join(BASE, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_MERGED_20260108_010448.csv")
EXCLUSION_PATH = os.path.join(BASE, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk__sandbox__4e269fb4\fba_financial_report_efghousewares-co-uk__sandbox__4e269fb4_RECONCILED_20260410_001500.csv")
OUTPUT_ROOT = os.path.join(BASE, r"OUTPUTS\PRODUCTS_LISTS")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
SUPPLIER = "efghousewares-co-uk"

# 10 excluded categories
EXCLUDED_CATS = [
    "https://www.efghousewares.co.uk/shop-by-department/disposable-bags-&-tableware/disposable-tableware",
    "https://www.efghousewares.co.uk/shop-by-department/pound-lines/diy---tools",
    "https://www.efghousewares.co.uk/shop-by-department/disposable-bags-&-tableware/bin-bag-carrier-bag-paper-bag",
    "https://www.efghousewares.co.uk/shop-by-department/pound-lines/candles-air-fresheners-diffuse",
    "https://www.efghousewares.co.uk/shop-by-department/household-cleaners/air-fresheners",
    "https://www.efghousewares.co.uk/shop-by-department/pound-lines/bathroom---cosmetics---beauty",
    "https://www.efghousewares.co.uk/shop-by-department/diy/amtech-tools",
    "https://www.efghousewares.co.uk/shop-by-department/china/home-baking",
    "https://www.efghousewares.co.uk/shop-by-department/electrical/light-bulbs",
    "https://www.efghousewares.co.uk/shop-by-department/glassware/glass-tableware",
]

LUXURY = ["versace", "jo malone", "armani", "chanel", "gucci", "dior", "prada", "dyson", "apple", "samsung"]

# === PHASE 1 ===
print("PHASE 1: ASSESS STALENESS")
print()

# Staleness
stale_date = "20260108"
stale_dt = datetime.strptime(stale_date, "%Y%m%d")
today = datetime(2026, 4, 19)
days_old = (today - stale_dt).days

status = "CRITICALLY" if days_old > 90 else "SIGNIFICANTLY" if days_old > 30 else "MODERATELY"
print(f"Report date: {stale_date} ({days_old} days old -> {status} stale)")
print(f"Source file: {os.path.basename(STALE_PATH)}")

df_stale = pd.read_csv(STALE_PATH, dtype=str, keep_default_na=False)
total_rows = len(df_stale)
print(f"Total rows: {total_rows}")
print(f"Columns: {list(df_stale.columns)[:10]}")

df_excl = pd.read_csv(EXCLUSION_PATH, dtype=str, keep_default_na=False)
excl_rows = len(df_excl)
print(f"Exclusion rows: {excl_rows}")

# Get exclusion ASINs/URLs
excl_asins = set(df_excl["ASIN"].dropna().astype(str).unique()) if "ASIN" in df_excl.columns else set()
excl_urls = set(df_excl["SupplierURL"].dropna().astype(str).unique()) if "SupplierURL" in df_excl.columns else set()
print(f"Exclusion ASINs: {len(excl_asins)}")
print(f"Exclusion URLs: {len(excl_urls)}")
print()

# === PHASE 2 ===
print("PHASE 2: DATA CLEANSING")

df = df_stale.copy()
rows_in = len(df)

# 2.1 - No TIER column, skip
# 2.2 - Superior brand
before = len(df)
df = df[~df["SupplierTitle"].str.contains("Superior", case=False, na=False)]
removed = before - len(df)
print(f"Step 2.2 (Superior): {removed} removed")

# 2.3 - Price plausibility  
before = len(df)
try:
    sup_price = pd.to_numeric(df["SupplierPrice_incVAT"], errors="coerce").fillna(0)
    amz_price = pd.to_numeric(df["SellingPrice_incVAT"], errors="coerce").fillna(0)
    mask = ~((amz_price > 20 * sup_price))
    df = df[mask]
    removed = before - len(df)
    print(f"Step 2.3 (Price plausibility): {removed} removed")
except Exception as e:
    print(f"Step 2.3 skipped: {e}")

# 2.4 - Luxury false match
before = len(df)
def has_luxury_false(row):
    sup = str(row.get("SupplierTitle", "")).lower()
    amz = str(row.get("AmazonTitle", "")).lower()
    return not any(b in sup for b in LUXURY) and any(b in amz for b in LUXURY)

df = df[~df.apply(has_luxury_false, axis=1)]
removed = before - len(df)
print(f"Step 2.4 (Luxury false match): {removed} removed")

# 2.5 - Unit qty mismatch
def get_qty(title):
    title = str(title).lower()
    for pat in [r"pack\s*of\s*(\d+)", r"\((\d+)\s*pack\)", r"(\d+)-pack", r"(\d+)pk"]:
        m = re.search(pat, title)
        if m:
            return int(m.group(1))
    return 1

def qty_flag(row):
    sq = get_qty(row.get("SupplierTitle", ""))
    aq = get_qty(row.get("AmazonTitle", ""))
    if sq == 1 and aq > 1:
        return "MISMATCH_CHECK"
    return "MATCH"

df["Unit_Qty_Flag"] = df.apply(qty_flag, axis=1)
mismatch = (df["Unit_Qty_Flag"] == "MISMATCH_CHECK").sum()
print(f"Step 2.5 (Unit qty): {mismatch} flagged")

# 2.6 - T3 quarantine (skip - no tier info)
print(f"Step 2.6 (T3 quarantine): skipped")

rows_out = len(df)
print(f"Phase 2: {rows_in} -> {rows_out}")
print()

# === PHASE 3 ===
print("PHASE 3: BUCKET CLASSIFICATION")

# Parse numeric
df["NetProfit_num"] = pd.to_numeric(df["NetProfit"], errors="coerce").fillna(0)
df["Sales_num"] = pd.to_numeric(df.get("bought_in_past_month", pd.Series([0]*len(df))), errors="coerce").fillna(0)
if "bought_in_past_month" in df.columns:
    df["Sales_num"] = pd.to_numeric(df["bought_in_past_month"], errors="coerce").fillna(0)
else:
    df["Sales_num"] = 0

# Bucket A: Sales > 0 AND NetProfit > 0
bucket_a = df[(df["Sales_num"] > 0) & (df["NetProfit_num"] > 0)].copy()
bucket_a["Bucket"] = "A"

# Bucket B: NetProfit > 0, Sales = 0
bucket_b = df[(df["NetProfit_num"] > 0) & (df["Sales_num"] <= 0)].copy()
bucket_b["Bucket"] = "B"

# Bucket C: Sales > 50 AND NetProfit -3 to 0.5
bucket_c = df[(df["Sales_num"] > 50) & (df["NetProfit_num"] >= -3.0) & (df["NetProfit_num"] <= 0.5)].copy()
bucket_c["Bucket"] = "C"

print(f"Bucket A: {len(bucket_a)} (avg profit: {bucket_a['NetProfit_num'].mean():.2f})")
print(f"Bucket B: {len(bucket_b)} (avg profit: {bucket_b['NetProfit_num'].mean():.2f})")
print(f"Bucket C: {len(bucket_c)} (avg profit: {bucket_c['NetProfit_num'].mean():.2f})")
print()

# === PHASE 4 ===
print("PHASE 4: RE-SCRAPE TARGETS")

bucket_ac = pd.concat([bucket_a, bucket_c], ignore_index=True)
if "SupplierURL" in bucket_ac.columns:
    cat_stats = bucket_ac.groupby("SupplierURL").agg({
        "ASIN": "count",
        "NetProfit_num": lambda x: (x * x.abs()).sum()
    }).rename(columns={"ASIN": "count", "NetProfit_num": "value"})
    cat_stats = cat_stats.sort_values("value", ascending=False).head(10)
    print(f"Top categories: {len(cat_stats)}")
    for i, (url, row) in enumerate(cat_stats.iterrows()):
        name = url.split("/")[-1][:30] if url else "unknown"
        print(f"  {i+1}. {name}: {int(row['count'])} prods")
print()

# === PHASE 5 ===
print("PHASE 5: SPOT CHECK (GEMINI available only)")
sample = min(3, len(bucket_a))
print(f"Sample for validation: {sample} products")
for _, r in bucket_a.head(sample).iterrows():
    title = str(r.get("SupplierTitle", ""))[:40]
    asin = str(r.get("ASIN", ""))
    profit = r["NetProfit_num"]
    print(f"  - {title}... | {asin} | £{profit:.2f}")
print()

# === PHASE 6 ===
print("PHASE 6: OUTPUTS")

out_dir = os.path.join(OUTPUT_ROOT, f"{SUPPLIER}_stale_analysis_{TIMESTAMP}")
csv_dir = os.path.join(out_dir, "csvs")
cat_dir = os.path.join(out_dir, "categories")
os.makedirs(csv_dir, exist_ok=True)
os.makedirs(cat_dir, exist_ok=True)

# Save CSVs
df.to_csv(os.path.join(csv_dir, f"{SUPPLIER}_VALIDATED_master_{TIMESTAMP}.csv"), index=False)
bucket_a.to_csv(os.path.join(csv_dir, f"{SUPPLIER}_VALIDATED_bucketA_{TIMESTAMP}.csv"), index=False)
pd.concat([bucket_b, bucket_c]).to_csv(os.path.join(csv_dir, f"{SUPPLIER}_VALIDATED_bucketBC_{TIMESTAMP}.csv"), index=False)

# Save JSONs
cat_targets = []
if len(cat_stats) > 0:
    for url, row in cat_stats.iterrows():
        cat_targets.append({"category_url": url, "product_count": int(row["count"]), "weighted_value": float(row["value"])})

with open(os.path.join(cat_dir, f"{SUPPLIER}_category_sandbox_targets_{TIMESTAMP}.json"), "w") as f:
    json.dump(cat_targets, f, indent=2)

phase_summary = {
    "phase1": {"total_rows": total_rows, "days_old": days_old, "staleness": status},
    "phase2": {"rows_in": rows_in, "rows_out": rows_out},
    "phase3": {"bucket_a": len(bucket_a), "bucket_b": len(bucket_b), "bucket_c": len(bucket_c)},
    "phase4": {"categories": len(cat_stats)},
    "phase5": {"sample": sample},
    "excluded_categories": EXCLUDED_CATS,
}

with open(os.path.join(cat_dir, f"{SUPPLIER}_phase4_summary_{TIMESTAMP}.json"), "w") as f:
    json.dump(phase_summary, f, indent=2)

# FINAL PRODUCT LIST (filter exclusions)
final = pd.concat([bucket_a, bucket_b], ignore_index=True)
final = final[~final["ASIN"].isin(excl_asins)]
final = final[~final["SupplierURL"].isin(excl_urls)]
for cat in EXCLUDED_CATS:
    final = final[final["SupplierURL"] != cat]

print(f"Final products after exclusions: {len(final)}")

# Save product list JSON
products_list = [{
    "supplier_title": str(r.get("SupplierTitle", "")),
    "amazon_title": str(r.get("AmazonTitle", "")),
    "asin": str(r.get("ASIN", "")),
    "ean": str(r.get("EAN", "")),
    "supplier_url": str(r.get("SupplierURL", "")),
    "amazon_url": str(r.get("AmazonURL", "")),
    "net_profit": float(r["NetProfit_num"]),
    "sales": float(r["Sales_num"]),
    "bucket": str(r.get("Bucket", "A")),
} for _, r in final.head(500).iterrows()]

plist = {
    "supplier": SUPPLIER,
    "timestamp": TIMESTAMP,
    "product_count": len(products_list),
    "products": products_list,
}

prod_path = os.path.join(OUTPUT_ROOT, f"product_list_{SUPPLIER}_{TIMESTAMP}.json")
with open(prod_path, "w") as f:
    json.dump(plist, f, indent=2)

print(f"Saved: {os.path.basename(prod_path)}")
print()

# VERIFY
print("VERIFICATION")
verify = pd.read_csv(os.path.join(csv_dir, f"{SUPPLIER}_VALIDATED_master_{TIMESTAMP}.csv"))
print(f"Master CSV: {len(verify)} rows")
print(f"Has Unit_Qty_Flag: {'Unit_Qty_Flag' in verify.columns}")
lux = sum(1 for t in verify["SupplierTitle"] if "superior" in str(t).lower())
print(f"Superior brand remaining: {lux}")
print()

# Report
print("="*50)
print("FINAL REPORT")
print("="*50)
print(f"Phase 1: {total_rows} rows ({days_old} days old)")
print(f"Phase 2: {rows_in} -> {rows_out} after cleansing")
print(f"Phase 3: A={len(bucket_a)}, B={len(bucket_b)}, C={len(bucket_c)}")
print(f"Phase 4: {len(cat_stats)} categories")
print(f"Phase 5: {sample} spot-check samples")
print(f"Phase 6: {len(final)} products in final list")
print()
print("OUTPUT FILES:")
print(f"  {prod_path}")
print(f"  {out_dir}/csvs/")
print(f"  {out_dir}/categories/")
print()
print("EXCLUDED CATEGORIES (10):")
for i, c in enumerate(EXCLUDED_CATS[:3]):
    print(f"  {i+1}. {c}")
print(f"  ... and 7 more")
print()
print("DONE")
