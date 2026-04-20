"""
Run Approach 2 on angelwholesale (a third supplier, not previously tested) to
verify it generalizes to different naming conventions. Joins the A2 output
with the dashboard-export CSV so we get both old and new tier side-by-side.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "FINAL STALE/agent analyses/initial_probabilistic_implementation_package"))
from probabilistic_matcher_prototype import ProbabilisticPairMatcher, Thresholds  # noqa

OUT_DIR = REPO / "temp/tier_preview_approach2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ANGEL_EXPORT = REPO / "temp/fba-angel_2026-04-17.csv"

REF_COLS = [
    "SupplierTitle","AmazonTitle","EAN","EAN_OnPage","ASIN",
    "SupplierPrice_incVAT","SellingPrice_incVAT","NetProfit","ROI",
    "bought_in_past_month","amazon_sales_badge","sales_value",
    "tier","confidence_score","flags","reasons","ean_exact_match",
    "SupplierURL","AmazonURL","fba_seller_count","Category",
]
EXTRA = [
    "tier_old","confidence_score_old","flags_old","reasons_old",
    "ean_exact_match_old","posterior_match_probability",
    "title_similarity","shared_tokens",
]

CATEGORY_KEYWORDS = {
    "electronics":["trimmer","charger","battery","headphone","speaker","phone","tablet","laptop"],
    "food":["chocolate","biscuit","cereal","snack","sweet","candy"],
    "health":["cream","soap","shampoo","wash","lotion","gel","wipe"],
    "cleaning":["bleach","detergent","cloth","mop","brush"],
    "toys":["toy","game","puzzle","doll","figure"],
}

def tof(v,d=0.0):
    try: return float(v) if v not in (None,"","None") else d
    except: return d
def toi(v,d=0):
    try: return int(v) if v not in (None,"","None") else d
    except: return d

def listing_swap(r, t, flags, reasons):
    if not r.get("_ean_exact", False): return t, flags, reasons
    if r.get("_title_sim",0.0) < 0.25 and r.get("_shared_tokens",0) < 2:
        return "TIER_3_NEEDS_REVIEW", flags+["EAN_MATCH_TITLE_MISMATCH"], \
               reasons+["EAN matches but titles share <2 meaningful tokens and sim<0.25"]
    return t, flags, reasons

def post_layer(r, t, flags, reasons):
    roi=tof(r.get("ROI")); net=tof(r.get("NetProfit"))
    sup=tof(r.get("SupplierPrice_incVAT")); sell=tof(r.get("SellingPrice_incVAT"))
    if roi>1000: flags.append("EXTREME_ROI"); reasons.append(f"High ROI: {roi:.0f}%")
    if sell>0 and sup>0 and sell/sup>20:
        flags.append("EXTREME_PRICE_RATIO"); reasons.append(f"Price ratio {sell/sup:.1f}x")
    if net<=0: flags.append("UNPROFITABLE")
    sl=(r.get("SupplierTitle","")or"").lower(); al=(r.get("AmazonTitle","")or"").lower()
    sc,ac=set(),set()
    for c,kws in CATEGORY_KEYWORDS.items():
        if any(k in sl for k in kws): sc.add(c)
        if any(k in al for k in kws): ac.add(c)
    if sc and ac and not(sc&ac):
        flags.append("CATEGORY_MISMATCH")
        reasons.append(f"Category mismatch supplier={sc} amazon={ac}")
    if r.get("_ean_exact",False) and "EAN_MATCH_TITLE_MISMATCH" not in flags:
        t = "TIER_1_VERIFIED" if net>0 and "CATEGORY_MISMATCH" not in flags else "TIER_2_LIKELY"
    elif "CATEGORY_MISMATCH" in flags and t=="TIER_2_LIKELY":
        t="TIER_3_NEEDS_REVIEW"
    return t,flags,reasons

def main():
    rows = list(csv.DictReader(open(ANGEL_EXPORT,"r",encoding="utf-8-sig")))
    print(f"loaded {len(rows)} angel rows", flush=True)

    matcher = ProbabilisticPairMatcher(Thresholds(tier2_prob=0.95, tier3_prob=0.10))
    matcher.fit(rows)
    predictions = matcher.predict_rows(rows)
    print(f"predicted; sample={predictions[0]['tier']}", flush=True)

    out_path = OUT_DIR / "angelwholesale__tier_preview.csv"
    old_counts = Counter(); new_counts = Counter(); transitions = Counter()
    with open(out_path,"w",encoding="utf-8",newline="") as f:
        w = csv.DictWriter(f, fieldnames=REF_COLS+EXTRA, extrasaction="ignore")
        w.writeheader()
        for r,pred in zip(rows, predictions):
            old_tier = r.get("tier","UNKNOWN")
            new_tier = pred["tier"]
            flags = list(pred["flags"])
            reasons = list(pred["reasons"])
            r["_ean_exact"] = bool(pred["ean_exact_match"])
            r["_title_sim"] = tof(pred["title_similarity"])
            r["_shared_tokens"] = toi(pred["shared_tokens"])
            new_tier, flags, reasons = listing_swap(r, new_tier, flags, reasons)
            new_tier, flags, reasons = post_layer(r, new_tier, flags, reasons)

            out = {c: r.get(c,"") for c in REF_COLS}
            out["tier"] = new_tier
            out["confidence_score"] = pred["confidence_score"]
            out["flags"] = str(flags)
            out["reasons"] = str(reasons)
            out["ean_exact_match"] = pred["ean_exact_match"]
            out["tier_old"] = old_tier
            out["confidence_score_old"] = r.get("confidence_score","")
            out["flags_old"] = r.get("flags","")
            out["reasons_old"] = r.get("reasons","")
            out["ean_exact_match_old"] = r.get("ean_exact_match","")
            out["posterior_match_probability"] = pred["posterior_match_probability"]
            out["title_similarity"] = pred["title_similarity"]
            out["shared_tokens"] = pred["shared_tokens"]
            w.writerow(out)
            old_counts[old_tier]+=1; new_counts[new_tier]+=1
            transitions[(old_tier,new_tier)]+=1

    summary = {
        "supplier":"angelwholesale-co-uk",
        "total_rows": sum(old_counts.values()),
        "old_tier_counts": dict(old_counts),
        "new_tier_counts": dict(new_counts),
        "transitions": {f"{a} -> {b}":c for (a,b),c in sorted(transitions.items(), key=lambda x:-x[1])[:15]},
        "output_csv": str(out_path),
    }
    (OUT_DIR/"angelwholesale__summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))

if __name__=="__main__":
    main()
