"""
EFG Housewares — Second-Pass Decontamination
=============================================
Problem: Many T1 "EAN matches" have 0% title similarity and absurd ROIs,
meaning the EAN-to-ASIN mapping was wrong in the original scraping (ASIN
collision). This pass adds a price-plausibility and title-similarity gate
even for T1 matches.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import os

REPO = r"C:\Users\chris\Desktop\Amazon-FBA-Agent-System-v32 - latest good - Copy (8) - Copy - Copy - POSTLONGRUNPREKIRO2 beforecompletion-"
OUTPUT_DIR = os.path.join(REPO, r"OUTPUTS\PRODUCTS_LISTS")
master_path = os.path.join(OUTPUT_DIR, "efg_master_product_list_20260412_072629.csv")

df = pd.read_csv(master_path)
original_count = len(df)
print(f"[LOAD] Master list: {original_count} products")

# === DECONTAMINATION PASS 2: Price and Title Plausibility ===

# Rule 1: If selling price is > 50x supplier price AND title similarity < 0.1 -> false match
# Example: Supplier sells a 0.62 GBP badge, matched to a 671 GBP Motorola phone
df["price_ratio"] = df["SellingPrice_incVAT"] / df["SupplierPrice_exVAT"].clip(lower=0.01)
false_price_match = (df["price_ratio"] > 50) & (df["title_similarity"] < 0.10)
print(f"[DECONTAM-2] Extreme price ratio + zero title similarity: {false_price_match.sum()}")

# Rule 2: ROI > 1000% with title_similarity < 0.05 -> almost certainly false match
false_roi_match = (df["ROI"] > 1000) & (df["title_similarity"] < 0.05)
print(f"[DECONTAM-2] Extreme ROI + zero title similarity: {false_roi_match.sum()}")

# Rule 3: ROI > 5000% regardless -> flag as unrealistic (wholesale FBA rarely exceeds 200-300%)
extreme_roi = df["ROI"] > 5000
print(f"[DECONTAM-2] ROI > 5000%% (unrealistic for wholesale): {extreme_roi.sum()}")

# Combined contamination mask
contaminated = false_price_match | false_roi_match
df_clean = df[~contaminated].copy()
removed = original_count - len(df_clean)
print(f"[DECONTAM-2] Total removed: {removed}")
print(f"[DECONTAM-2] Clean master list: {len(df_clean)}")

# === RE-BUCKET COUNTS ===
print()
for bkt in ["A", "B", "C"]:
    bkt_df = df_clean[df_clean["bucket"] == bkt]
    t1 = (bkt_df["match_type"] == "T1").sum()
    t2 = (bkt_df["match_type"] == "T2").sum()
    t3 = (bkt_df["match_type"] == "T3").sum()
    val = (bkt_df["validation_required"] == "YES").sum()
    print(f"Bucket {bkt}: {len(bkt_df)} total (T1={t1}, T2={t2}, T3={t3}, ValReq={val})")

# === SAVE CLEAN FILES ===
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
clean_master = os.path.join(OUTPUT_DIR, f"efg_master_CLEAN_{ts}.csv")
clean_a = os.path.join(OUTPUT_DIR, f"efg_bucket_A_CLEAN_{ts}.csv")
clean_bc = os.path.join(OUTPUT_DIR, f"efg_bucket_BC_CLEAN_{ts}.csv")
clean_summary = os.path.join(OUTPUT_DIR, f"efg_analysis_summary_CLEAN_{ts}.md")

df_clean.to_csv(clean_master, index=False, encoding="utf-8-sig")
df_clean[df_clean["bucket"] == "A"].to_csv(clean_a, index=False, encoding="utf-8-sig")
df_clean[df_clean["bucket"].isin(["B", "C"])].to_csv(clean_bc, index=False, encoding="utf-8-sig")

print(f"\n[SAVED] Clean Master: {clean_master}")
print(f"[SAVED] Clean Bucket A: {clean_a}")
print(f"[SAVED] Clean Bucket BC: {clean_bc}")

# === REALISTIC TOP PRODUCTS ===
print("\n=== TOP 20 BUCKET A (CLEAN) by NetProfit ===")
top_a = df_clean[df_clean["bucket"]=="A"].nlargest(20, "NetProfit")
for _, r in top_a.iterrows():
    sup = str(r["SupplierTitle"])[:55]
    s = r["bought_in_past_month"]
    s_str = f"{s:.0f}" if pd.notna(s) else "N/A"
    print(f"  [{r['match_type']}] {sup} | Profit={r['NetProfit']:.2f} Sales={s_str} ROI={r['ROI']:.1f}%")

print("\n=== TOP 15 BUCKET B (CLEAN) by NetProfit ===")
top_b = df_clean[df_clean["bucket"]=="B"].nlargest(15, "NetProfit")
for _, r in top_b.iterrows():
    sup = str(r["SupplierTitle"])[:55]
    s = r["bought_in_past_month"]
    s_str = f"{s:.0f}" if pd.notna(s) else "N/A"
    conf = r["confidence"] if "confidence" in r else "?"
    print(f"  [{r['match_type']}] {sup} | Profit={r['NetProfit']:.2f} Sales={s_str} ROI={r['ROI']:.1f}% conf={conf}")

print("\n=== TOP 15 BUCKET C (CLEAN) by Sales ===")
top_c = df_clean[df_clean["bucket"]=="C"].nlargest(15, "bought_in_past_month")
for _, r in top_c.iterrows():
    sup = str(r["SupplierTitle"])[:55]
    print(f"  [{r['match_type']}] {sup} | Profit={r['NetProfit']:.2f} Sales={r['bought_in_past_month']:.0f}")

# === GENERATE CLEAN SUMMARY ===
lines = []
lines.append("# EFG Housewares — CLEAN Product List Analysis")
lines.append(f"Generated: {datetime.now().isoformat()}")
lines.append(f"Source: fba_financial_report_ALL_linking_map_20260108_005639.csv (21,305 raw)")
lines.append("")
lines.append("## Decontamination Applied")
lines.append(f"- Pass 1: Superior brand exclusion (50 removed)")
lines.append(f"- Pass 1: False-positive T2/T3 ASIN collisions (275 removed)")
lines.append(f"- Pass 2: Price-ratio + title-similarity gate ({removed} removed)")
lines.append(f"  - Catches EAN matches mapped to wrong ASINs (e.g., badge -> phone)")
lines.append("")
lines.append("## Final Counts")
for bkt in ["A", "B", "C"]:
    bkt_df = df_clean[df_clean["bucket"] == bkt]
    t1 = (bkt_df["match_type"] == "T1").sum()
    t2 = (bkt_df["match_type"] == "T2").sum()
    t3 = (bkt_df["match_type"] == "T3").sum()
    val = (bkt_df["validation_required"] == "YES").sum()
    lines.append(f"- **Bucket {bkt}**: {len(bkt_df)} (T1={t1}, T2={t2}, T3={t3}, Validation={val})")
lines.append(f"- **TOTAL**: {len(df_clean)}")
lines.append("")
lines.append("## Key Risks")
lines.append("- Jan 8 2026 data snapshot — 3+ months stale")
lines.append("- T2/T3 items marked 'VALIDATION_REQUIRED' need Keepa/Google Trends manual check")
lines.append("- Bucket C items profitable only with small price increase or fee reduction")
lines.append("- No programmatic Keepa/Google Trends pass in this execution")

Path(clean_summary).write_text("\n".join(lines), encoding="utf-8")
print(f"\n[SAVED] Clean Summary: {clean_summary}")

print(f"\n{'='*60}")
print(f"FINAL CLEAN COUNTS")
print(f"{'='*60}")
print(f"Bucket A: {len(df_clean[df_clean['bucket']=='A'])}")
print(f"Bucket B: {len(df_clean[df_clean['bucket']=='B'])}")
print(f"Bucket C: {len(df_clean[df_clean['bucket']=='C'])}")
print(f"TOTAL: {len(df_clean)}")
