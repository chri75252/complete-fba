"""
Generate production-equivalent preview of Approach 2 tier classification
applied to the two reference CSVs. Output format matches the standard
analysis CSV (21 columns) plus appended columns showing the old tier side.

Applies on top of raw A2:
  - deterministic Amazon-listing-swap gate
    (EAN exact + title_sim<0.25 + shared_tokens<2 -> demote to TIER_3)
  - financial/category post-layer parity with current classify_row
"""
from __future__ import annotations
import csv, json
from pathlib import Path
from collections import Counter

REPO = Path(__file__).resolve().parents[2]
A2_DIR = REPO / "FINAL STALE/agent analyses/initial_probabilistic_implementation_package/initial_probabilistic_regenerated_outputs"
OUT_DIR = REPO / "temp/tier_preview_approach2"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_COLS = [
    "SupplierTitle","AmazonTitle","EAN","EAN_OnPage","ASIN",
    "SupplierPrice_incVAT","SellingPrice_incVAT","NetProfit","ROI",
    "bought_in_past_month","amazon_sales_badge","sales_value",
    "tier","confidence_score","flags","reasons","ean_exact_match",
    "SupplierURL","AmazonURL","fba_seller_count","Category",
]
EXTRA_COLS = [
    "tier_old","confidence_score_old","flags_old","reasons_old",
    "ean_exact_match_old","posterior_match_probability",
    "title_similarity","shared_tokens",
]

CATEGORY_KEYWORDS = {
    "electronics": ["trimmer","charger","battery","headphone","speaker","phone","tablet","laptop"],
    "food": ["chocolate","biscuit","cereal","snack","sweet","candy"],
    "health": ["cream","soap","shampoo","wash","lotion","gel","wipe"],
    "cleaning": ["bleach","detergent","cloth","mop","brush"],
    "toys": ["toy","game","puzzle","doll","figure"],
}

def to_float(v, default=0.0):
    try: return float(v) if v not in (None, "", "None") else default
    except (ValueError, TypeError): return default

def to_int(v, default=0):
    try: return int(v) if v not in (None,"","None") else default
    except (ValueError, TypeError): return default

def apply_listing_swap_gate(row, new_tier, new_flags, new_reasons):
    if str(row.get("new_ean_exact_match","")).lower() not in ("true","1"):
        return new_tier, new_flags, new_reasons
    t_sim = to_float(row.get("title_similarity",0))
    shared = to_int(row.get("shared_tokens",0))
    if t_sim < 0.25 and shared < 2:
        new_tier = "TIER_3_NEEDS_REVIEW"
        new_flags = list(new_flags) + ["EAN_MATCH_TITLE_MISMATCH"]
        new_reasons = list(new_reasons) + [
            "EAN matches but titles share <2 meaningful tokens and sim<0.25 - "
            "possible Amazon listing swap"
        ]
    return new_tier, new_flags, new_reasons

def apply_post_layer(row, new_tier, new_flags, new_reasons):
    roi = to_float(row.get("ROI",0))
    net = to_float(row.get("NetProfit",0))
    sup = to_float(row.get("SupplierPrice_incVAT",0))
    sell = to_float(row.get("SellingPrice_incVAT",0))
    if roi > 1000:
        new_flags.append("EXTREME_ROI")
        new_reasons.append(f"Suspiciously high ROI: {roi:.0f}%")
    if sell > 0 and sup > 0 and (sell/sup) > 20:
        new_flags.append("EXTREME_PRICE_RATIO")
        new_reasons.append(f"Price ratio {sell/sup:.1f}x - likely mismatch")
    if net <= 0:
        new_flags.append("UNPROFITABLE")

    sl = (row.get("SupplierTitle","") or "").lower()
    al = (row.get("AmazonTitle","") or "").lower()
    s_cats, a_cats = set(), set()
    for cat,kws in CATEGORY_KEYWORDS.items():
        if any(kw in sl for kw in kws): s_cats.add(cat)
        if any(kw in al for kw in kws): a_cats.add(cat)
    if s_cats and a_cats and not (s_cats & a_cats):
        new_flags.append("CATEGORY_MISMATCH")
        new_reasons.append(f"Category mismatch: supplier={s_cats} vs amazon={a_cats}")

    if str(row.get("new_ean_exact_match","")).lower() in ("true","1") and \
       "EAN_MATCH_TITLE_MISMATCH" not in new_flags:
        if net > 0 and "CATEGORY_MISMATCH" not in new_flags:
            new_tier = "TIER_1_VERIFIED"
        else:
            new_tier = "TIER_2_LIKELY"
    elif "CATEGORY_MISMATCH" in new_flags and new_tier == "TIER_2_LIKELY":
        new_tier = "TIER_3_NEEDS_REVIEW"
    return new_tier, new_flags, new_reasons

def parse_list(val):
    if not val: return []
    s = str(val).strip()
    if s.startswith("[") and s.endswith("]"):
        try:
            import ast
            return list(ast.literal_eval(s))
        except Exception:
            pass
    return [s]

def build(source_csv: Path, label: str):
    rows_in = list(csv.DictReader(open(source_csv, "r", encoding="utf-8-sig")))
    out_path = OUT_DIR / f"{label}__tier_preview.csv"
    out_cols = REFERENCE_COLS + EXTRA_COLS
    old_counts, new_counts, transition = Counter(), Counter(), Counter()

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_cols, extrasaction="ignore")
        w.writeheader()
        for r in rows_in:
            old_tier = r.get("tier","UNKNOWN")
            new_tier = r.get("new_tier","UNKNOWN")
            new_flags = parse_list(r.get("new_flags"))
            new_reasons = parse_list(r.get("new_reasons"))
            new_tier, new_flags, new_reasons = apply_listing_swap_gate(r, new_tier, new_flags, new_reasons)
            new_tier, new_flags, new_reasons = apply_post_layer(r, new_tier, new_flags, new_reasons)

            out = {c: r.get(c,"") for c in REFERENCE_COLS}
            # Replace the 'tier' slot with the NEW tier and its metadata.
            out["tier"] = new_tier
            out["confidence_score"] = r.get("new_confidence_score","")
            out["flags"] = str(new_flags)
            out["reasons"] = str(new_reasons)
            out["ean_exact_match"] = r.get("new_ean_exact_match","")
            # Append old side + diagnostics.
            out["tier_old"] = old_tier
            out["confidence_score_old"] = r.get("confidence_score","")
            out["flags_old"] = r.get("flags","")
            out["reasons_old"] = r.get("reasons","")
            out["ean_exact_match_old"] = r.get("ean_exact_match","")
            out["posterior_match_probability"] = r.get("posterior_match_probability","")
            out["title_similarity"] = r.get("title_similarity","")
            out["shared_tokens"] = r.get("shared_tokens","")
            w.writerow(out)

            old_counts[old_tier] += 1
            new_counts[new_tier] += 1
            transition[(old_tier, new_tier)] += 1

    summary = {
        "label": label,
        "source_file": str(source_csv.name),
        "total_rows": sum(old_counts.values()),
        "old_tier_counts": dict(old_counts),
        "new_tier_counts": dict(new_counts),
        "transitions": {f"{k[0]} -> {k[1]}": v for k,v in sorted(transition.items(), key=lambda x: -x[1])[:20]},
        "output_csv": str(out_path),
    }
    (OUT_DIR / f"{label}__summary.json").write_text(json.dumps(summary, indent=2))
    return summary

def main():
    efg_src = A2_DIR / "efg_latest_analysis__probabilistic_regenerated.csv"
    pw_src  = A2_DIR / "pound_latest_analysis__probabilistic_regenerated.csv"
    summaries = [build(efg_src, "efg"), build(pw_src, "poundwholesale")]
    combined = {"suppliers": summaries}
    (OUT_DIR / "combined_summary.json").write_text(json.dumps(combined, indent=2))
    print(json.dumps(combined, indent=2))

if __name__ == "__main__":
    main()
