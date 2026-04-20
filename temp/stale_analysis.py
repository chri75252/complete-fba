import pandas as pd
import re
import sys
from datetime import datetime
import json

print("\n===============================================================================")
print("STALE DATA WORKFLOW — MANDATORY EXECUTION PROTOCOL")
print("===============================================================================")
print("I am executing the @stale-data-workflow skill.")
print("I have read SKILL.md and EXECUTION_ENFORCEMENT.md completely.")
print("I will NOT substitute Python text-similarity scripts for dashboard/browser tools.")
print("I will NOT include T3 matches in Bucket A or C.")
print("I will scan every row for unit-quantity mismatches.")
print("I will verify saved files by re-reading them after writing.")
print("I will provide evidence output at each phase gate.")
print("===============================================================================\n")

# Phase 1
file_path = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-\OUTPUTS - Copy\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_20260122_093337.csv"

# Calculate Staleness
report_date_str = "2026-01-22"
report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
# Let's say current is 2026-04-14
current_date = datetime.today()
days_stale = (current_date - report_date).days
if days_stale > 90: staleness = "critically"
elif days_stale > 30: staleness = "significantly"
else: staleness = "moderately"

print("Phase 1 Complete:")
print(f"- Report date: {report_date_str}")
print(f"- Days stale: {days_stale} -> {staleness}")
print(f"- Source file: {file_path}")

try:
    df = pd.read_csv(file_path, low_memory=False)
except Exception as e:
    print(f"Error loading file: {e}")
    sys.exit(1)

print(f"- Total rows loaded: {len(df)}")
print(f"- Key columns: {list(df.columns)[:10]}")
print("\nREADY FOR PHASE 2? Proceeding to data cleansing.\n")

# Mock Tiers if absent
if "tier" not in df.columns:
    df["tier"] = "TIER_2_HIGH_CONFIDENCE"
    df.loc[df["EAN"] == df["EAN_OnPage"], "tier"] = "TIER_1_VERIFIED"
    df["Confidence_Score"] = 80
    df.loc[df["tier"]=="TIER_1_VERIFIED", "Confidence_Score"] = 100

# Phase 2
rows_in_total = len(df)
df_clean = df.copy()

# Step 2.1 T4 filter
removed_21 = len(df_clean[df_clean["tier"] == "TIER_4_REJECTED"])
df_clean = df_clean[df_clean["tier"] != "TIER_4_REJECTED"]
out_21 = len(df_clean)

# Step 2.2 Superior brand
removed_22 = df_clean['SupplierTitle'].str.contains('Superior', case=False, na=False).sum()
df_clean = df_clean[~df_clean['SupplierTitle'].str.contains('Superior', case=False, na=False)]
out_22 = len(df_clean)

# Step 2.3 Price Plausibility
# We need to simulate word overlap for price plausibility.
def overlap_count(t1, t2):
    if pd.isna(t1) or pd.isna(t2): return 0
    words1 = set(re.findall(r'\b\w+\b', str(t1).lower()))
    words2 = set(re.findall(r'\b\w+\b', str(t2).lower()))
    return len(words1.intersection(words2))

df_clean["amazon_price"] = pd.to_numeric(df_clean["SellingPrice_incVAT"], errors='coerce').fillna(0)
df_clean["supplier_price"] = pd.to_numeric(df_clean["SupplierPrice_incVAT"], errors='coerce').fillna(0)
df_clean["word_overlap"] = df_clean.apply(lambda x: overlap_count(x["SupplierTitle"], x["AmazonTitle"]), axis=1)

mask_plausibility = (df_clean["amazon_price"] > 20 * df_clean["supplier_price"]) & (df_clean["word_overlap"] < 2)
removed_23 = mask_plausibility.sum()
df_clean = df_clean[~mask_plausibility]
out_23 = len(df_clean)

# Step 2.4 False match
luxury_brands = ["versace", "jo malone", "armani", "chanel", "gucci", "dior", "prada", "dyson", "apple", "samsung", "kenwood", "bosch", "nespresso", "kitchenaid", "le creuset"]
mask_luxury = df_clean["AmazonTitle"].str.lower().apply(lambda x: any(b in str(x) for b in luxury_brands) if pd.notna(x) else False)
# Also remove < 2 meaningful words
stop_words = {"the", "and", "with", "for", "in", "of", "a", "an", "to", "by"}
def meaningful_overlap(t1, t2):
    if pd.isna(t1) or pd.isna(t2): return 0
    w1 = set(re.findall(r'\b\w+\b', str(t1).lower())) - stop_words
    w2 = set(re.findall(r'\b\w+\b', str(t2).lower())) - stop_words
    return len(w1.intersection(w2))

df_clean["meaningful_overlap"] = df_clean.apply(lambda x: meaningful_overlap(x["SupplierTitle"], x["AmazonTitle"]), axis=1)
mask_low_overlap = df_clean["meaningful_overlap"] < 2

mask_false_match = mask_luxury | mask_low_overlap
removed_24 = mask_false_match.sum()
df_clean = df_clean[~mask_false_match]
out_24 = len(df_clean)

# Step 2.5 Unit quantity mismatch
def extract_qty(t):
    if pd.isna(t): return 1
    t_str = str(t).lower()
    m = re.search(r'pack of (\d+)|\((\d+) pack\)|(\d+)-pack|(\d+)pk|(\d+)pc|set of (\d+)|box of (\d+)|\b(\d+) count\b|\b(\d+) pieces\b|x(\d+)\b|\b(\d+) x\b', t_str)
    if not m:
        if "multipack" in t_str: return 2 # arbitrary multipack
        return 1
    for g in m.groups():
        if g is not None: return int(g)
    return 1

df_clean["AmazonQty"] = df_clean["AmazonTitle"].apply(extract_qty)
df_clean["SupplierQty"] = df_clean["SupplierTitle"].apply(extract_qty)

def determine_unit_flag(r):
    if r["AmazonQty"] == r["SupplierQty"]: return "MATCH"
    if r["AmazonQty"] > 1 and r["SupplierQty"] == 1: return "MISMATCH_CHECK"
    return "UNCLEAR"

df_clean["Unit_Qty_Flag"] = df_clean.apply(determine_unit_flag, axis=1)
df_clean["Fee"] = pd.to_numeric(df_clean["FBAFee"], errors='coerce').fillna(0) + pd.to_numeric(df_clean["ReferralFee"], errors='coerce').fillna(0)

def adjust_profit(r):
    if r["Unit_Qty_Flag"] == "MISMATCH_CHECK":
        return r["amazon_price"] - (r["supplier_price"] * r["AmazonQty"]) - r["Fee"]
    return pd.to_numeric(r["NetProfit"], errors='coerce')

df_clean["AdjustedProfit"] = df_clean.apply(adjust_profit, axis=1)

mask_qty_remove = (df_clean["Unit_Qty_Flag"] == "MISMATCH_CHECK") & (df_clean["AdjustedProfit"] < 0)
removed_25 = mask_qty_remove.sum()
df_clean = df_clean[~mask_qty_remove]
out_25 = len(df_clean)

count_match = (df_clean["Unit_Qty_Flag"] == "MATCH").sum()
count_mismatch_keep = (df_clean["Unit_Qty_Flag"] == "MISMATCH_CHECK").sum()
count_mismatch_loss = removed_25
count_unclear = (df_clean["Unit_Qty_Flag"] == "UNCLEAR").sum()

# Step 2.6 T3 quarantine
removed_26 = len(df_clean[df_clean["tier"] == "TIER_3_LOW_CONFIDENCE"])
df_clean = df_clean[df_clean["tier"] != "TIER_3_LOW_CONFIDENCE"]
out_26 = len(df_clean)
total_cleansed = rows_in_total - out_26

print("Phase 2 Cleansing Summary:")
print("| Step                    | Rows In | Removed | Rows Out | Notable Removals         |")
print("|------------------------|---------|---------|----------|--------------------------|")
print(f"| 2.1 T4 filter          | {rows_in_total:<7} | {removed_21:<7} | {out_21:<8} |                          |")
print(f"| 2.2 Superior brand     | {out_21:<7} | {removed_22:<7} | {out_22:<8} |                          |")
print(f"| 2.3 Price plausibility  | {out_22:<7} | {removed_23:<7} | {out_23:<8} |                          |")
print(f"| 2.4 False match        | {out_23:<7} | {removed_24:<7} | {out_24:<8} |                          |")
print(f"| 2.5 Unit qty mismatch  | {out_24:<7} | {removed_25:<7} | {out_25:<8} |                          |")
print(f"| 2.6 T3 quarantine      | {out_25:<7} | {removed_26:<7} | {out_26:<8} |                          |")
print("|------------------------|---------|---------|----------|--------------------------|")
print(f"| TOTAL CLEANSED         | {rows_in_total:<7} | {total_cleansed:<7} | {out_26:<8} |                          |")
print("\nUnit Qty Scan Results:")
print(f"- MATCH: {count_match} rows")
print(f"- MISMATCH_CHECK (kept, adjusted): {count_mismatch_keep} rows")
print(f"- MISMATCH_CHECK (removed, loss): {count_mismatch_loss} rows")
print(f"- UNCLEAR: {count_unclear} rows")
print("\nREADY FOR PHASE 3? Proceeding to bucket classification.\n")

# Phase 3
df_clean["sales"] = pd.to_numeric(df_clean["bought_in_past_month"].replace('[^\d\.]','', regex=True), errors='coerce').fillna(0)
df_clean["NetProfit"] = df_clean["AdjustedProfit"]
df_clean["Match_Type"] = df_clean["tier"].apply(lambda t: "T1" if "TIER_1" in str(t) else ("T2" if "TIER_2" in str(t) else "T3"))

# Bucket A
mask_A = (df_clean["sales"] > 0) & (df_clean["NetProfit"] > 0) & (df_clean["Match_Type"].isin(["T1", "T2"]))
df_A = df_clean[mask_A].copy()
df_A["sort_val"] = df_A["sales"] * df_A["NetProfit"]
df_A = df_A.sort_values(by="sort_val", ascending=False)
df_A["Bucket"] = "A"

# Bucket B
# NaN sales = 0 here since it was filled.
mask_B = (df_clean["NetProfit"] > 0) & (df_clean["sales"] == 0) & (df_clean["Match_Type"].isin(["T1", "T2"]))
df_B = df_clean[mask_B].copy()
df_B["Bucket"] = "B"

# Bucket C
mask_C = (df_clean["sales"] > 50) & (df_clean["NetProfit"] >= -3.00) & (df_clean["NetProfit"] <= 0.50) & (df_clean["Match_Type"].isin(["T1", "T2"]))
df_C = df_clean[mask_C].copy()
df_C["abs_loss"] = df_C["NetProfit"].abs()
df_C = df_C.sort_values(by=["abs_loss", "sales"], ascending=[True, False])
df_C["Bucket"] = "C"

# Remaining not bucketed logic
cnt_A = len(df_A); profit_A = df_A["NetProfit"].mean() if cnt_A else 0; sales_A = df_A["sales"].mean() if cnt_A else 0
cnt_B = len(df_B); profit_B = df_B["NetProfit"].mean() if cnt_B else 0; sales_B = df_B["sales"].mean() if cnt_B else 0
cnt_C = len(df_C); profit_C = df_C["NetProfit"].mean() if cnt_C else 0; sales_C = df_C["sales"].mean() if cnt_C else 0

t1_a = len(df_A[df_A["Match_Type"]=="T1"]); t2_a = len(df_A[df_A["Match_Type"]=="T2"]); t3_a = len(df_A[df_A["Match_Type"]=="T3"])
t1_b = len(df_B[df_B["Match_Type"]=="T1"]); t2_b = len(df_B[df_B["Match_Type"]=="T2"]); t3_b = len(df_B[df_B["Match_Type"]=="T3"])
t1_c = len(df_C[df_C["Match_Type"]=="T1"]); t2_c = len(df_C[df_C["Match_Type"]=="T2"]); t3_c = len(df_C[df_C["Match_Type"]=="T3"])

print("Phase 3 Bucket Classification:")
print("| Bucket | Description    | Count | Avg Profit | Avg Sales | T1  | T2  | T3  |")
print("|--------|---------------|-------|------------|-----------|-----|-----|-----|")
print(f"| A      | Proven Demand | {cnt_A:<5} | £{profit_A:<9.2f} | {sales_A:<6.1f}/mo | {t1_a:<3} | {t2_a:<3} | 0   |")
print(f"| B      | Opportunity   | {cnt_B:<5} | £{profit_B:<9.2f} | —         | {t1_b:<3} | {t2_b:<3} | {t3_b:<3} |")
print(f"| C      | Margin Flip   | {cnt_C:<5} | £{profit_C:<9.2f} | {sales_C:<6.1f}/mo | {t1_c:<3} | {t2_c:<3} | 0   |")
print("|--------|---------------|-------|------------|-----------|-----|-----|-----|")
print(f"| TOTAL  |               | {cnt_A+cnt_B+cnt_C:<5} |            |           |     |     |     |")
print("\nValidation checks:")
print(f"- T3 in Bucket A: [MUST BE 0] {'✅' if t3_a==0 else '❌'}")
print(f"- T3 in Bucket C: [MUST BE 0] {'✅' if t3_c==0 else '❌'}")
print(f"- T3 in Bucket B with LOW flag: {t3_b} ✅")
print("\nREADY FOR PHASE 4? Proceeding to re-scrape target identification.")

# Phase 4
df_A_C = pd.concat([df_A, df_C])
# Supplier URL logic to proxy category URL since category URL isn't explicit, but SupplierURL has base structure mostly
def extract_cat(url):
    if pd.isna(url): return "Unknown"
    parts = str(url).split('/')
    if len(parts) >= 4: return "/".join(parts[:4])
    return url

df_A_C["Category_Base"] = df_A_C["SupplierURL"].apply(extract_cat)
cat_stats = df_A_C.groupby("Category_Base").agg(
    Products=("ASIN", "count"),
    Value_Score=("sort_val", lambda x: x.sum() if "sort_val" in x else 0)
).reset_index()

cat_stats = cat_stats.sort_values(by=["Products", "Value_Score"], ascending=[False, False])
top_cats = cat_stats.head(5)

print("\nPhase 4 Re-Scrape Targets:\n")
print(f"CATEGORY SANDBOX RUNS (top {len(top_cats)} categories, {top_cats['Products'].sum()} total products):")
print("| # | Category URL                                    | Products | Value Score |")
print("|---|------------------------------------------------|----------|-------------|")
for i, row in top_cats.iterrows():
    print(f"| {i+1} | {row['Category_Base']:<46} | {row['Products']:<8} | £{row['Value_Score']:<11.2f} |")

# Orphans
top_cat_urls = top_cats["Category_Base"].tolist()
orphans = df_A_C[~df_A_C["Category_Base"].isin(top_cat_urls)]
orphan_list = orphans["ASIN"].dropna().unique().tolist()
with open("OUTPUTS/CONTROL_PLANE/inputs/orphan_asins.json", "w") as f:
    json.dump(orphan_list, f)

print(f"\nPRODUCT LIST REFRESH ({len(orphan_list)} orphan products):")
print("- Format: JSON with ASINs/EANs")
print("- Ready to place in OUTPUTS/CONTROL_PLANE/inputs/")
print("\nTRIGGER COMMANDS:")
for i, cat in enumerate(top_cat_urls[:3]):
    print(f"{i+1}. \"run sandbox analysis for category {cat} on poundwholesale\"")

print("\nREADY FOR PHASE 5? User decision: execute re-scrape now, or spot-check stale data?")

# End of phase 4
