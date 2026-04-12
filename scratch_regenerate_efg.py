"""
EFG Housewares Product List Regenerator — Surgical FBA Analysis
================================================================
Source: fba_financial_report_ALL_linking_map_20260108_005639.csv (21,305 rows)
Skills invoked: @systematic-debugging, @data-quality-frameworks, @pricing-strategy,
                @inventory-demand-planning, @supply-chain-risk-auditor
"""
import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime

# === CONFIG ===
REPO = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
REPORT = os.path.join(REPO, r"OUTPUTS\FBA_ANALYSIS\financial_reports\efghousewares-co-uk\fba_financial_report_ALL_linking_map_20260108_005639.csv")
OUTPUT_DIR = os.path.join(REPO, r"OUTPUTS\PRODUCTS_LISTS")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Amazon cache for match-quality verification
AMAZON_CACHE_DIR = os.path.join(REPO, r"OUTPUTS\FBA_ANALYSIS\amazon_cache")
LINKING_MAP_DIR = os.path.join(REPO, r"OUTPUTS\FBA_ANALYSIS\linking_maps\efghousewares-co-uk")

# === LOAD DATA ===
print("=" * 80)
print("PHASE 1: DATA LOAD & DECONTAMINATION")
print("=" * 80)
df = pd.read_csv(REPORT)
print(f"[LOAD] Raw rows: {len(df)}")

# Coerce numerics
for col in ["bought_in_past_month", "NetProfit", "ROI", "SellingPrice_incVAT",
            "SupplierPrice_exVAT", "SupplierPrice_incVAT", "ReferralFee", "FBAFee",
            "fba_seller_count", "fbm_seller_count", "total_offer_count",
            "ProfitMargin", "Breakeven"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

sales_col = "bought_in_past_month"

# === STEP 1: HARD EXCLUSION — "Superior" brand ===
superior_mask = (
    df["SupplierTitle"].str.contains("Superior", case=False, na=False) |
    df["AmazonTitle"].str.contains("Superior", case=False, na=False)
)
df_clean = df[~superior_mask].copy()
print(f"[DECONTAM] Removed {superior_mask.sum()} 'Superior' branded rows")
print(f"[DECONTAM] Remaining: {len(df_clean)}")

# === STEP 2: MATCH-TYPE CLASSIFICATION ===
# The report lacks explicit match_type/tier columns.
# We infer match quality from EAN_OnPage presence and EAN-to-ASIN consistency.
print()
print("=" * 80)
print("PHASE 2: MATCH-TYPE CLASSIFICATION & VERIFICATION")
print("=" * 80)

def classify_match(row):
    """
    Classify match type based on available signals:
    - T1 (EAN Match): EAN_OnPage is present AND non-null -> confirmed barcode match
    - T2 (Likely Match): EAN_OnPage missing but ASIN maps to a single EAN -> probable title match
    - T3 (Weak Match): EAN_OnPage missing AND ASIN maps to many products -> unreliable
    """
    if pd.notna(row["EAN_OnPage"]):
        return "T1_EAN_MATCH"
    else:
        return "T2_T3_TITLE_MATCH"  # Will be split further below

df_clean["match_type_raw"] = df_clean.apply(classify_match, axis=1)

# Further split T2 vs T3 by checking ASIN collision density
# If an ASIN is mapped to 10+ different supplier products, it's almost certainly wrong
asin_counts = df_clean.groupby("ASIN").size().reset_index(name="asin_product_count")
df_clean = df_clean.merge(asin_counts, on="ASIN", how="left")

def refine_match_type(row):
    if row["match_type_raw"] == "T1_EAN_MATCH":
        return "T1"
    elif row["asin_product_count"] <= 3:
        return "T2"
    else:
        return "T3"

df_clean["match_type"] = df_clean.apply(refine_match_type, axis=1)

t1_count = (df_clean["match_type"] == "T1").sum()
t2_count = (df_clean["match_type"] == "T2").sum()
t3_count = (df_clean["match_type"] == "T3").sum()
print(f"[MATCH] T1 (EAN confirmed): {t1_count}")
print(f"[MATCH] T2 (Likely title match, low collision): {t2_count}")
print(f"[MATCH] T3 (Weak match, high ASIN collision): {t3_count}")

# === STEP 3: T2/T3 MATCH VERIFICATION — Critical Scrutiny ===
# For T2/T3 matches, check if the Amazon title is plausibly the same product
# as the supplier title. Use simple heuristic: word overlap ratio.
print()
print("=" * 80)
print("PHASE 3: T2/T3 MATCH VERIFICATION (Critical Scrutiny)")
print("=" * 80)

def title_similarity(sup_title, amz_title):
    """Simple word-overlap similarity score."""
    if pd.isna(sup_title) or pd.isna(amz_title):
        return 0.0
    sup_words = set(str(sup_title).lower().split())
    amz_words = set(str(amz_title).lower().split())
    # Remove common noise words
    noise = {"the", "a", "an", "of", "for", "and", "with", "in", "to", "set", "-", "&", "x", "pack"}
    sup_words -= noise
    amz_words -= noise
    if not sup_words or not amz_words:
        return 0.0
    overlap = sup_words & amz_words
    return len(overlap) / max(len(sup_words), len(amz_words))

df_clean["title_similarity"] = df_clean.apply(
    lambda r: title_similarity(r["SupplierTitle"], r["AmazonTitle"]), axis=1
)

# Category compatibility check: extract category from SupplierURL
def extract_category(url):
    if pd.isna(url):
        return "unknown"
    parts = [p for p in str(url).split("/") if p and "." not in p and "http" not in p and len(p) > 2]
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").title()
    return "unknown"

df_clean["supplier_category"] = df_clean["SupplierURL"].apply(extract_category)

# Mark T2/T3 verification status
def verify_t2_t3(row):
    if row["match_type"] == "T1":
        return "VERIFIED"
    
    sim = row["title_similarity"]
    asin_collision = row["asin_product_count"]
    
    # Obvious false positive: completely different product types
    if sim < 0.05 and asin_collision > 5:
        return "REJECTED_FALSE_POSITIVE"
    
    # High-collision ASIN with no title overlap = almost certainly wrong
    if asin_collision > 10 and sim < 0.15:
        return "REJECTED_HIGH_COLLISION"
    
    # Moderate match — needs validation
    if sim < 0.15:
        return "VALIDATION_REQUIRED"
    
    # Reasonable overlap
    if sim >= 0.3:
        return "LIKELY_VALID"
    
    return "VALIDATION_REQUIRED"

df_clean["verification_status"] = df_clean.apply(verify_t2_t3, axis=1)

verified_counts = df_clean["verification_status"].value_counts()
print("[VERIFICATION STATUS]")
for status, count in verified_counts.items():
    print(f"  {status}: {count}")

# Remove confirmed false positives
rejected_mask = df_clean["verification_status"].isin(["REJECTED_FALSE_POSITIVE", "REJECTED_HIGH_COLLISION"])
rejected_count = rejected_mask.sum()
df_verified = df_clean[~rejected_mask].copy()
print(f"\n[PURGE] Rejected {rejected_count} false-positive T2/T3 matches")
print(f"[PURGE] Remaining verified/candidate rows: {len(df_verified)}")

# === STEP 4: BUCKET SEGMENTATION ===
print()
print("=" * 80)
print("PHASE 4: BUCKET SEGMENTATION")
print("=" * 80)

# Bucket A — Proven demand: Sales > 0 AND NetProfit > 0
bucket_a = df_verified[
    (df_verified[sales_col] > 0) & (df_verified["NetProfit"] > 0)
].copy()
bucket_a["bucket"] = "A"
bucket_a["inclusion_reason"] = "Proven demand with positive profit"

# Bucket B — Positive-profit / zero-sales opportunity
bucket_b_candidates = df_verified[
    (df_verified["NetProfit"] > 0) &
    ((df_verified[sales_col] == 0) | df_verified[sales_col].isna())
].copy()

# Apply critical analysis for Bucket B
def assess_bucket_b(row):
    """
    Assess whether a zero-sales, positive-profit product deserves inclusion.
    Returns (include: bool, reason: str, confidence: str)
    """
    profit = row["NetProfit"]
    roi = row["ROI"] if pd.notna(row["ROI"]) else 0
    price = row["SellingPrice_incVAT"] if pd.notna(row["SellingPrice_incVAT"]) else 0
    match = row["match_type"]
    verify = row["verification_status"]
    category = row["supplier_category"]
    sim = row["title_similarity"]
    
    reasons = []
    score = 0
    
    # Strong profit signal
    if profit > 5:
        score += 2
        reasons.append("Strong absolute profit (>5 GBP)")
    elif profit > 2:
        score += 1
        reasons.append("Moderate profit (>2 GBP)")
    
    # Strong ROI
    if roi > 100:
        score += 2
        reasons.append(f"High ROI ({roi:.0f}%)")
    elif roi > 50:
        score += 1
        reasons.append(f"Moderate ROI ({roi:.0f}%)")
    
    # Price point viability (sweet spot for FBA: 8-30 GBP)
    if 8 <= price <= 30:
        score += 1
        reasons.append("Price in FBA sweet spot")
    elif price > 30:
        score += 0.5
        reasons.append("Higher price point, possible demand")
    
    # Match quality bonus/penalty
    if match == "T1":
        score += 2
        reasons.append("EAN-confirmed match")
    elif match == "T2" and verify == "LIKELY_VALID":
        score += 1
        reasons.append("Likely valid T2 match")
    elif verify == "VALIDATION_REQUIRED":
        score -= 1
        reasons.append("Match needs validation")
    
    # Category demand heuristic
    household_cats = ["kitchen", "bathroom", "cleaning", "storage", "home", "household",
                      "garden", "laundry", "cookware", "tableware", "plastics"]
    cat_lower = category.lower()
    if any(c in cat_lower for c in household_cats):
        score += 1
        reasons.append("High-demand household category")
    
    # Inclusion threshold
    if score >= 3:
        confidence = "HIGH" if score >= 5 else "MEDIUM"
        return True, "; ".join(reasons), confidence
    else:
        return False, "; ".join(reasons) if reasons else "Insufficient signals", "LOW"

bucket_b_assessments = bucket_b_candidates.apply(assess_bucket_b, axis=1, result_type="expand")
bucket_b_candidates["b_include"] = bucket_b_assessments[0]
bucket_b_candidates["inclusion_reason"] = bucket_b_assessments[1]
bucket_b_candidates["confidence"] = bucket_b_assessments[2]

bucket_b = bucket_b_candidates[bucket_b_candidates["b_include"] == True].copy()
bucket_b["bucket"] = "B"
bucket_b_rejected = len(bucket_b_candidates) - len(bucket_b)

print(f"Bucket A (Proven demand): {len(bucket_a)}")
print(f"Bucket B candidates assessed: {len(bucket_b_candidates)}")
print(f"Bucket B included: {len(bucket_b)}")
print(f"Bucket B rejected (insufficient signals): {bucket_b_rejected}")

# Bucket C — Near-profit / high-sales opportunity
bucket_c_candidates = df_verified[
    (df_verified[sales_col] > 0) &
    (df_verified["NetProfit"] <= 0) &
    (df_verified["NetProfit"] > -3)  # Within 3 GBP of breakeven
].copy()

def assess_bucket_c(row):
    """
    Assess whether a near-profit, high-sales product has a credible path to profitability.
    """
    profit = row["NetProfit"]
    sales = row[sales_col] if pd.notna(row[sales_col]) else 0
    price = row["SellingPrice_incVAT"] if pd.notna(row["SellingPrice_incVAT"]) else 0
    match = row["match_type"]
    verify = row["verification_status"]
    
    reasons = []
    score = 0
    
    # How close to breakeven?
    if profit > -0.50:
        score += 3
        reasons.append(f"Very close to breakeven ({profit:.2f} GBP gap)")
    elif profit > -1.00:
        score += 2
        reasons.append(f"Close to breakeven ({profit:.2f} GBP gap)")
    elif profit > -2.00:
        score += 1
        reasons.append(f"Near breakeven ({profit:.2f} GBP gap)")
    
    # High sales velocity
    if sales >= 200:
        score += 3
        reasons.append(f"Very high demand ({sales:.0f} sold/month)")
    elif sales >= 100:
        score += 2
        reasons.append(f"High demand ({sales:.0f} sold/month)")
    elif sales >= 50:
        score += 1
        reasons.append(f"Moderate demand ({sales:.0f} sold/month)")
    
    # Credible margin improvement paths
    if price >= 10 and abs(profit) < 1.5:
        score += 1
        reasons.append("Small price increase could flip to profit")
    
    # Match quality
    if match == "T1":
        score += 1
        reasons.append("EAN-confirmed match")
    elif verify == "VALIDATION_REQUIRED":
        score -= 1
        reasons.append("Match needs validation")
    
    if score >= 3:
        confidence = "HIGH" if score >= 5 else "MEDIUM"
        return True, "; ".join(reasons), confidence
    else:
        return False, "; ".join(reasons) if reasons else "Insufficient signals", "LOW"

bucket_c_assessments = bucket_c_candidates.apply(assess_bucket_c, axis=1, result_type="expand")
bucket_c_candidates["c_include"] = bucket_c_assessments[0]
bucket_c_candidates["inclusion_reason"] = bucket_c_assessments[1]
bucket_c_candidates["confidence"] = bucket_c_assessments[2]

bucket_c = bucket_c_candidates[bucket_c_candidates["c_include"] == True].copy()
bucket_c["bucket"] = "C"
bucket_c_rejected = len(bucket_c_candidates) - len(bucket_c)

print(f"Bucket C candidates assessed: {len(bucket_c_candidates)}")
print(f"Bucket C included: {len(bucket_c)}")
print(f"Bucket C rejected: {bucket_c_rejected}")

# === STEP 5: ADD MISSING COLUMNS & ENRICH ===
print()
print("=" * 80)
print("PHASE 5: ENRICH & OUTPUT")
print("=" * 80)

# Standardize columns for Bucket A
if "inclusion_reason" not in bucket_a.columns:
    bucket_a["inclusion_reason"] = "Proven demand with positive profit"
if "confidence" not in bucket_a.columns:
    bucket_a["confidence"] = bucket_a.apply(
        lambda r: "HIGH" if r["match_type"] == "T1" else ("MEDIUM" if r["verification_status"] == "LIKELY_VALID" else "LOW"),
        axis=1
    )

# Combine all buckets
output_columns = [
    "SupplierTitle", "AmazonTitle", "match_type", "EAN", "EAN_OnPage", "ASIN",
    sales_col, "NetProfit", "ROI", "SellingPrice_incVAT", "SupplierPrice_exVAT",
    "bucket", "inclusion_reason", "confidence", "verification_status",
    "title_similarity", "asin_product_count", "supplier_category",
    "SupplierURL", "AmazonURL", "ProfitMargin", "Breakeven",
    "fba_seller_count", "fbm_seller_count", "total_offer_count"
]

# Add validation_required column
for bdf in [bucket_a, bucket_b, bucket_c]:
    bdf["validation_required"] = bdf.apply(
        lambda r: "YES" if r["verification_status"] == "VALIDATION_REQUIRED" else "NO",
        axis=1
    )
    # Priority scoring
    bdf["priority_score"] = 0
    if "NetProfit" in bdf.columns:
        bdf.loc[bdf["NetProfit"] > 5, "priority_score"] += 2
        bdf.loc[bdf["NetProfit"] > 2, "priority_score"] += 1
    if sales_col in bdf.columns:
        bdf.loc[bdf[sales_col] > 100, "priority_score"] += 2
        bdf.loc[bdf[sales_col] > 50, "priority_score"] += 1
    bdf.loc[bdf["match_type"] == "T1", "priority_score"] += 2
    bdf.loc[bdf["confidence"] == "HIGH", "priority_score"] += 1
    bdf["priority"] = bdf["priority_score"].apply(
        lambda x: "HIGH" if x >= 5 else ("MEDIUM" if x >= 3 else "LOW")
    )

output_columns += ["validation_required", "priority"]

# Ensure all columns exist
for bdf in [bucket_a, bucket_b, bucket_c]:
    for col in output_columns:
        if col not in bdf.columns:
            bdf[col] = ""

master = pd.concat([bucket_a[output_columns], bucket_b[output_columns], bucket_c[output_columns]], ignore_index=True)

# Sort: Bucket A first, then by priority and profit
bucket_order = {"A": 0, "B": 1, "C": 2}
priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
master["_bucket_sort"] = master["bucket"].map(bucket_order)
master["_priority_sort"] = master["priority"].map(priority_order)
master = master.sort_values(["_bucket_sort", "_priority_sort", "NetProfit"], ascending=[True, True, False])
master = master.drop(columns=["_bucket_sort", "_priority_sort"])

# === SAVE FILES ===
ts = datetime.now().strftime("%Y%m%d_%H%M%S")

master_path = os.path.join(OUTPUT_DIR, f"efg_master_product_list_{ts}.csv")
bucket_a_path = os.path.join(OUTPUT_DIR, f"efg_bucket_A_proven_{ts}.csv")
bucket_bc_path = os.path.join(OUTPUT_DIR, f"efg_bucket_BC_opportunities_{ts}.csv")
summary_path = os.path.join(OUTPUT_DIR, f"efg_analysis_summary_{ts}.md")

master.to_csv(master_path, index=False, encoding="utf-8-sig")
bucket_a[output_columns].to_csv(bucket_a_path, index=False, encoding="utf-8-sig")
pd.concat([bucket_b[output_columns], bucket_c[output_columns]]).to_csv(bucket_bc_path, index=False, encoding="utf-8-sig")

print(f"[SAVED] Master: {master_path}")
print(f"[SAVED] Bucket A: {bucket_a_path}")
print(f"[SAVED] Bucket BC: {bucket_bc_path}")

# === SUMMARY ===
print()
print("=" * 80)
print("FINAL SUMMARY")
print("=" * 80)

summary_lines = []
summary_lines.append(f"# EFG Housewares Product List Analysis Summary")
summary_lines.append(f"Generated: {datetime.now().isoformat()}")
summary_lines.append(f"Source: fba_financial_report_ALL_linking_map_20260108_005639.csv")
summary_lines.append(f"")
summary_lines.append(f"## Counts")
summary_lines.append(f"- Raw rows: 21,305")
summary_lines.append(f"- Superior brand excluded: {superior_mask.sum()}")
summary_lines.append(f"- False-positive T2/T3 rejected: {rejected_count}")
summary_lines.append(f"- **Bucket A (Proven demand)**: {len(bucket_a)}")
summary_lines.append(f"- **Bucket B (Profit + zero-sales opportunity)**: {len(bucket_b)}")
summary_lines.append(f"- **Bucket C (Near-profit + high-sales)**: {len(bucket_c)}")
summary_lines.append(f"- **Total in master list**: {len(master)}")
summary_lines.append(f"")
summary_lines.append(f"## Match Type Breakdown (Master List)")

for bkt in ["A", "B", "C"]:
    bkt_df = master[master["bucket"] == bkt]
    t1 = (bkt_df["match_type"] == "T1").sum()
    t2 = (bkt_df["match_type"] == "T2").sum()
    t3 = (bkt_df["match_type"] == "T3").sum()
    val_req = (bkt_df["validation_required"] == "YES").sum()
    summary_lines.append(f"- Bucket {bkt}: T1={t1}, T2={t2}, T3={t3}, Validation Required={val_req}")

summary_lines.append(f"")
summary_lines.append(f"## T2/T3 Verification Results")
summary_lines.append(f"- Total T2/T3 assessed: {t2_count + t3_count}")
summary_lines.append(f"- Rejected as false positive: {rejected_count}")
summary_lines.append(f"- Included (likely valid or validation required): {(master['match_type'].isin(['T2', 'T3'])).sum()}")
summary_lines.append(f"")
summary_lines.append(f"## Bucket B Rejection Rate")
summary_lines.append(f"- Candidates assessed: {len(bucket_b_candidates)}")
summary_lines.append(f"- Included: {len(bucket_b)} ({100*len(bucket_b)/max(1,len(bucket_b_candidates)):.1f}%)")
summary_lines.append(f"- Rejected (insufficient signals): {bucket_b_rejected}")
summary_lines.append(f"")
summary_lines.append(f"## Top Priority Opportunities")
summary_lines.append(f"")
summary_lines.append(f"### Bucket A — Top 10 by NetProfit")
top_a = bucket_a.nlargest(10, "NetProfit")
for _, r in top_a.iterrows():
    summary_lines.append(f"- [{r['match_type']}] **{str(r['SupplierTitle'])[:60]}** | Profit: {r['NetProfit']:.2f} | Sales: {r[sales_col]:.0f} | ROI: {r['ROI']:.0f}%")

summary_lines.append(f"")
summary_lines.append(f"### Bucket B — Top 10 by NetProfit (zero-sales opportunities)")
top_b = bucket_b.nlargest(10, "NetProfit")
for _, r in top_b.iterrows():
    sales_str = f"{r[sales_col]:.0f}" if pd.notna(r[sales_col]) else "N/A"
    summary_lines.append(f"- [{r['match_type']}] **{str(r['SupplierTitle'])[:60]}** | Profit: {r['NetProfit']:.2f} | Sales: {sales_str} | Reason: {r['inclusion_reason'][:80]}")

summary_lines.append(f"")
summary_lines.append(f"### Bucket C — Top 10 Near-Profit High-Sales")
top_c = bucket_c.nlargest(10, sales_col)
for _, r in top_c.iterrows():
    summary_lines.append(f"- [{r['match_type']}] **{str(r['SupplierTitle'])[:60]}** | Profit: {r['NetProfit']:.2f} | Sales: {r[sales_col]:.0f} | Reason: {r['inclusion_reason'][:80]}")

summary_lines.append(f"")
summary_lines.append(f"## Key Assumptions & Risks")
summary_lines.append(f"- Data is from Jan 8, 2026 snapshot — sales figures may be stale")
summary_lines.append(f"- T2/T3 matches verified via title-similarity heuristic; manual spot-checks recommended")
summary_lines.append(f"- Bucket B products labeled 'VALIDATION_REQUIRED' need Keepa/Google Trends confirmation")
summary_lines.append(f"- Bucket C products may become profitable with small price adjustments or fee changes")
summary_lines.append(f"- No Keepa/Google Trends data integrated programmatically in this pass — flagged for manual review")

summary_text = "\n".join(summary_lines)
Path(summary_path).write_text(summary_text, encoding="utf-8")
print(summary_text)
print(f"\n[SAVED] Summary: {summary_path}")

# Print final counts
print(f"\n{'='*80}")
print(f"EXECUTION COMPLETE")
print(f"{'='*80}")
print(f"Master list: {len(master)} products")
print(f"  Bucket A: {len(bucket_a)}")
print(f"  Bucket B: {len(bucket_b)}")  
print(f"  Bucket C: {len(bucket_c)}")
print(f"Files saved to: {OUTPUT_DIR}")
